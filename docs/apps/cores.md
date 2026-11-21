<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 CPU Tools](../assets/cores/bc250-cores-bisect.webp){ .app-logo }

# BC-250 CPU Tools

!!! warning "Changes the board"
    The app sends the SoC's SMU one mailbox message over PCI configuration space with setpci, which sets the
    core presence mask to 0xFF in the SMU's own memory; the governor's service is stopped around the message, as
    it shares the mailbox, and started again. The mask takes effect on the next warm reboot, survives warm
    reboots, and a full power off reverts it to the stock 6 cores. The 8 cores stay across power offs only
    through the root service that CPU Tools installs, bc250-cores-unlock.service, which sends the message
    again after a cold boot and warm-reboots once, with a guard against reboot loops. Nothing is written to the
    BIOS, the firmware, the CMOS or the kernel's arguments. Uninstall in CPU Tools disables the service and
    removes its files; the cores stay on until the next full power off, and the board is then stock. CPU Tools
    reboots the board between its rounds, by itself with the unattended option, after a question otherwise.

BC-250 CPU Tools tells **bad CPU cores** apart from an **unstable core unlock** on the AMD BC-250 (Cyan Skillfish).
Use it *before* you trust or keep the 8C/16T core unlock.

The BC-250 ships with 6 of its 8 Zen 2 cores enabled. Its core presence mask is `0x77`. Core 3 of each CCX
(core complex) is fused off, the same in both. That symmetry smells like product segmentation, not harvesting.

The SMU (System Management Unit) is the chip's own controller. It has a quirk, queue-3 message `0x98`, that writes
`0xFF` to any SMN address. SMN is the chip's internal register bus. One of those addresses is the core presence mask
at SMN `0x5A870`, which the host can't write. That write enables all 8 cores on the next warm restart.

**The catch:** that primitive is all-or-nothing. Unlike a GPU CU unlock there is no per-core mask, so you can't
leave one bad core disabled. If *either* extra core is bad, you can't use the core unlock on your board. You want
to know that before you keep it and let a flaky core corrupt data.

`bc250-cores-bisect.sh` does its own unlock, so it needs no other tool. It tests in a way that separates the
possible causes. It is a sibling project of [bc250-cu-bisect](compute.md), which does the same for the GPU CUs.

> **Warning:** this talks to the SMU and runs heavy CPU load. A bad core can freeze the system or
> corrupt data. Save your work first. Use at your own risk.

## How it works

You can't enable the cores one at a time. So the isolation happens **after** the core unlock. The script pins the
load with `taskset` to exactly the threads under test.

| Item           | When            | Pinned to                       | Separates                                             |
|----------------|-----------------|---------------------------------|-------------------------------------------------------|
| `control`      | before unlock   | all stock cores (6C/12T)        | board / power / heat / load tool problems             |
| `post-control` | after unlock    | one stock core (2 threads)      | "the core unlock destabilizes the SoC" from bad cores |
| `coreN`        | after unlock    | one new core on its own         | which new core (if any) is bad                        |
| `combined`     | after unlock    | both new cores together         | cores that pass alone but fail together               |

```
          core0   core1   core2   core4   core5   core6   core3   core7
           ██      ██      ██      ██      ██      ██      ..      ..

██ stock, always enabled (6C/12T)    .. fused off, enabled by the unlock, tested one by one
```

The order isn't a typo. The map groups the stock cores first and the unlocked ones last, where their verdict cells
live.

Why cores 3 and 7 specifically? The mask `0x77` is binary `0111 0111`, one nibble per 4-core CCX. In *each* CCX
it's core 3 that is fused off. CCX0 keeps cores 0,1,2 and CCX1 keeps 4,5,6. The core unlock adds core 3 (CCX0) and
core 7, which is the "core 3" of CCX1. The same position is disabled in both CCXs. That symmetry is what smells like
product segmentation rather than harvesting of defective silicon.

The script shows this map live. It puts `>>` on the core under test. Once a core has a verdict, the map shows one
of these marks:

- `ok` for GOOD
- `xx` for FAILS EVERY TIME
- `??` for RANDOM

The script finds failures in four ways:

- **Machine-check events** in the kernel log (`journalctl -k`). They are the classic symptom of marginal cores.
- **Wrong results, not only crashes.** `stress-ng --verify` recomputes and checks every stressor result.
- **Full crashes**, crash-safe. Before every attempt the script saves what it's doing. After a freeze, restart and
  run it again. It then records the crash and shows the MCE (machine-check event) lines of the previous boot.
- **Optional burn-in extras.** These are `mprime`'s torture test (`--load mprime|both`) and hardware error counters
  from `rasdaemon` (`--rasdaemon`). See [Longer burn-in](#longer-burn-in-mprime--rasdaemon).

The test plan has the same philosophy as the CU bisect:

- **Control first.** The script only offers the core unlock after the stock cores pass every control round. With a
  failing control, the results say nothing about the new cores.
- **Rounds.** Every item runs 3 times by default. The rounds are interleaved, so heat and time don't favor one.
- **One attempt per boot** (default). Warm restarts keep the core unlock, so isolation costs nothing.
- **State machine across boots.** The steps are control → unlock → verify the cores actually came up → bisect →
  verdict. The script detects a cold boot mid-run, because the mask is back to `0x77`, and handles it.
- **Mask gate.** The script refuses boards whose stock mask isn't `0x77`. A different mask strongly suggests
  genuinely defective silicon that was purposefully skipped.

## The verdict and the decision

- **`control` fails** → board, power, heat or load tool. Fix that first.
- **`post-control` fails** → the core unlock destabilizes even the stock cores on your board. Cold boot to revert,
  and don't keep it.
- **A core FAILS EVERY TIME** → likely genuinely bad silicon. The core unlock is all-or-nothing, so **don't use it
  at all.** A cold boot (full power off) reverts everything.
- **RANDOM failures** → points to power or heat, not silicon. Improve cooling and retest.
- **Everything GOOD, alone and combined** → the core unlock looks safe. Keep it, as described below.

## Requirements

- AMD BC-250, Linux with bash 4+. Tested against Bazzite (Fedora Atomic).
- `setpci` (pciutils). SMN/SMU access goes through the PCI config space of `0000:00:00.0`.
- `stress-ng` and `taskset` (util-linux).
- sudo rights. The script uses sudo for `setpci`, the kernel log and the governor's service.
- Optional: `mprime` (Prime95) for the torture test and `rasdaemon` (`ras-mc-ctl`) for hardware
  error counters. You only need them if you ask for them.

## Before you start

1. Start from a **cold boot** (full power off). That guarantees the stock `0x77` state.
2. Close background workloads. The load must land only on the pinned cores.
3. The script stops `cyan-skillfish-governor-smu` for the few milliseconds of the SMU write, because the governor
   shares the mailbox. It starts the governor again afterward.

## Usage

Run it as your normal user:

```bash
chmod +x bc250-cores-bisect.sh
./bc250-cores-bisect.sh                 # 3 rounds, 600 s verified load per attempt
./bc250-cores-bisect.sh -t 1800 -r 5    # longer load, more rounds (recommended before trusting it)
./bc250-cores-bisect.sh --same-boot     # no reboots between bisect attempts (faster, less isolation)
./bc250-cores-bisect.sh --auto          # no prompts, auto-reboot, continues after every login
./bc250-cores-bisect.sh --load both     # stress-ng *and* the mprime torture test per attempt
./bc250-cores-bisect.sh --rasdaemon     # also count hardware errors via ras-mc-ctl
./bc250-cores-bisect.sh --status        # results so far, report + logs in ~/Desktop/bc250-cores-bisect/
./bc250-cores-bisect.sh --reset         # delete the results and start over
./bc250-cores-bisect.sh --help
```

The smallest `-t` is 60.

A run goes through these steps:

1. You run the script.
2. It runs the control rounds, one per boot.
3. It offers the core unlock.
4. You do a warm restart.
5. It detects the new cores.
6. It runs the bisect rounds, one per warm restart.
7. It shows the final summary, the report and the decision.

At the end of a run, and on every `--status`, the script copies everything to `~/Desktop/bc250-cores-bisect/`.
That makes it easy to share.

| File                                         | Contents                                                     |
|----------------------------------------------|--------------------------------------------------------------|
| `bc250-cores-bisect-results-<date>.txt`      | The report: core map, verdicts, decision, every attempt.     |
| `runs.tsv`                                   | The raw results table, one line per attempt.                 |
| `config`                                     | The run's settings and detected cores.                       |
| `logs/<date>-r<round>-<item>.log`            | stress-ng output of each attempt, with verification failures.|
| `logs/<date>-r<round>-<item>-mprime.log`     | mprime torture output, when mprime is part of the load.      |
| `ras-mc-ctl-errors.txt`                      | rasdaemon's error table, with `--rasdaemon`.                 |
| `auto.log`                                   | Everything the script printed in `--auto` runs.              |

The working copies live in `~/.local/share/bc250-cores-bisect/`. `--reset` deletes those, not the Desktop folder.

Pick `-t`/`-r` before you start and keep them. You *can* change them mid-run. The script then keeps the results so
far and asks you to confirm. But the evidence is then mixed. The report lists the load of every attempt. A control
that finished with fewer rounds keeps them. For a uniform result, use `--reset` and start over.

For `--auto`, install the autostart unit, so the script resumes after every login. See
`bc250-cores-bisect-auto.service.example`.

### Running truly unattended (`--auto` checklist)

`--auto` makes the *script* hands-off, but the *system* must get back to your session on its own:

1. **Autologin.** After each restart someone must log in, or the run stalls at the login screen. Turn it on in
   your desktop. On Bazzite/KDE it is System Settings → Colors & Themes → Login Screen (SDDM) → Behavior →
   auto-login. On GNOME, it is Users → auto-login.
2. **Passwordless sudo** for your user. The script needs `setpci` and `journalctl -k` without a prompt. When it
   runs from the unit, there is no terminal to type a password into.

   ```bash
   echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/bc250-bisect
   sudo chmod 440 /etc/sudoers.d/bc250-bisect
   sudo visudo -cf /etc/sudoers.d/bc250-bisect   # must print "parsed OK"
   sudo -k && sudo -n true && echo OK    # must print OK without asking
   ```
   Revert after testing with `sudo rm /etc/sudoers.d/bc250-bisect`.
   If you edit the file by hand, use `sudo visudo -f /etc/sudoers.d/bc250-bisect`. It refuses to save a broken line.
   A broken line makes every `sudo` command print a warning, or stops sudo working at all.
3. **The autostart unit installed.** Without it nothing starts the script again after login. You would have to
   start it by hand at every boot.
4. **No credential popups at login (KDE Wallet / ksshaskpass).** With autologin the KDE Wallet can't unlock by
   itself. So an "SSH credentials" or wallet dialog can appear at session start. It blocks the chain until you
   answer it. There are two ways around it. Give the wallet a blank password. Open it in `kwalletmanager5` first,
   then choose Change Password → empty. Or turn the wallet subsystem off. Plasma 6 has no checkbox for it anymore,
   so use this command:

   ```bash
   kwriteconfig6 --file kwalletrc --group Wallet --key Enabled false   # kwriteconfig5 on Plasma 5
   ```
   Turn it on again afterward with `... --key Enabled true`. Also uncheck "Use KWallet for the Secret
   Service interface" in System Settings → KDE Wallet. Then apps don't route secrets to the disabled wallet.

Check on it while it runs:

```bash
systemctl --user status bc250-cores-bisect-auto.service   # ran / running / failed this boot
tail -f ~/.local/share/bc250-cores-bisect/auto.log        # live output of the current attempt
./bc250-cores-bisect.sh --status                          # progress and results so far
```

When all attempts are done, the script stops restarting on its own. In `--auto` mode it also disables the autostart
unit by itself. It removes the live-output entry too, which is described below. So nothing starts at the next
login. If you ran without `--auto`, disable the unit by hand with
`systemctl --user disable --now bc250-cores-bisect-auto.service`.

Want the live output on the board's screen instead of a shell? Add a desktop autostart entry that opens a terminal
following the log at every login. This is a KDE example. See the comments in
`bc250-cores-bisect-auto.service.example`.

```bash
cat > ~/.config/autostart/bc250-cores-bisect-watch.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=BC-250 bisect live output
Exec=konsole --title "bc250-cores-bisect" -e tail -n 40 -f .local/share/bc250-cores-bisect/auto.log
EOF
```

### How long does it take?

A full run is `5 × rounds` attempts. The items are control, then post-control, core3, core7 and combined. Each
attempt runs the load for `--time` seconds. Add one warm restart for the core unlock.

In the default one-attempt-per-boot mode, add a restart and login of about 1–2 min per attempt. With `--same-boot`
there are only 2–3 restarts in total, plus a 30 s cooldown between attempts. Indications:

| Invocation                           | Attempts | Pure load | Wall clock (approx.)   |
|--------------------------------------|----------|-----------|------------------------|
| default (`-t 600 -r 3`)              | 15       | 2 h 30 m  | ~3 h (15 reboots)      |
| `--same-boot` (`-t 600 -r 3`)        | 15       | 2 h 30 m  | ~2 h 45 m (3 reboots)  |
| `-t 1800 -r 5` (recommended)         | 25       | 12 h 30 m | ~13 h (25 reboots)     |
| `-t 1800 -r 5 --same-boot`           | 25       | 12 h 30 m | ~12 h 45 m (3 reboots) |

The longer runs are for unattended use. Combine them with `--auto` and the autostart unit, and let the run finish
overnight. You don't have to do it in one sitting either. The state survives restarts. So run the script again at
any time, and it continues where it left off. `--status` shows the progress.

### Longer burn-in (`mprime` / `rasdaemon`)

`stress-ng --verify` is the default load and is enough for most boards. For a harder, longer burn-in before you
trust the core unlock, you can add two optional tools:

```bash
./bc250-cores-bisect.sh --load mprime              # mprime torture test instead of stress-ng
./bc250-cores-bisect.sh --load both                # stress-ng first, then mprime
./bc250-cores-bisect.sh --mprime-bin ~/mprime/mprime
./bc250-cores-bisect.sh --rasdaemon                # count hardware errors around every attempt
./bc250-cores-bisect.sh -t 1800 -r 5 --load both --rasdaemon --auto --same-boot
```

- **`--load stress-ng|mprime|both`** (default `stress-ng`). `mprime` runs Prime95's torture test with
  `StressTester=1` and no PrimeNet. It is pinned to exactly the same CPUs as stress-ng. It runs from a private
  working directory under `~/.local/share/bc250-cores-bisect/mprime/<item>/`. The workload is AVX/FMA-heavy,
  in-cache FFT. It catches a different class of marginal silicon than stress-ng's mixed stressors. A torture
  error gives the attempt the outcome **`MPRIME-FAIL`**.
- With **`--load both`** the two tools run **one after the other**, never at the same time. So they don't fight
  over the same threads. Each attempt then takes **2 × `--time`**. Budget double the wall clock from the table
  above.
- **`--mprime-bin PATH`** points at a mprime binary in another place than the ones named under
  [Installing mprime](#installing-mprime).
- **`--rasdaemon`** reads `ras-mc-ctl --errors` before and after every attempt and records the difference. Any
  new hardware error makes the attempt **`RAS-ERROR`**. It needs a running `rasdaemon` service. If `ras-mc-ctl`
  is missing, the script stops and says so. If the service is not running or `ras-mc-ctl` fails, the script
  warns you and carries on without the count. The script exports the full error table as `ras-mc-ctl-errors.txt`.
- The script records both extras per attempt. `runs.tsv` gained a **load tool** and a **rasdaemon errors** column.
  The report lists the load of every attempt, so a mixed run stays readable. The script still reads older result
  files from before this feature correctly.

Like `-t`/`-r`, pick these before you start. The script stores the settings in `config` and reuses them after every
restart. They also go into the command line of the `--auto` service.

#### Installing mprime

[Quickfix](quickfix.md#quickfix) installs mprime with its **Prime95** pill. To install it by hand, download it from
[mersenne.org](https://www.mersenne.org/download/), because no package installs it. Then unpack it into a folder.
These commands do that for version 30.19 build 20, for 64-bit Linux:

```bash
mkdir -p ~/mprime && cd ~/mprime
curl -O https://download.mersenne.ca/gimps/v30/30.19/p95v3019b20.linux64.tar.gz
echo "4ce2377e03deb4cf189523136e26401ba08f67857a128e420dd030d00cdca601  p95v3019b20.linux64.tar.gz" | sha256sum -c
tar -xzf p95v3019b20.linux64.tar.gz
```

The third line compares the download with the SHA-256 that mersenne.org's download page lists, and prints
`p95v3019b20.linux64.tar.gz: OK`. You need nothing more. BC-250 CPU Tools and Nexus Deps look for `mprime` in these
places, in this order:

1. `$PATH`
2. `~/mprime/mprime`
3. `~/.local/bin/mprime`
4. `/opt/mprime/mprime`
5. `/usr/local/bin/mprime`

To try it by hand, `./mprime -t` in that folder starts the torture test on all cores right away, without the
questions about PrimeNet. It runs until Ctrl+C stops it, and writes its settings and `results.txt` into the
folder. The core bisect does not use these. It runs mprime from a working folder of its own, with its own settings.

## Making it persistent

Only after a clean verdict:

```bash
sudo ./bc250-cores-unlock.sh --install
```

The core unlock is volatile. It survives warm restarts, and a full power off reverts it. A fresh write only takes
effect on the *next* restart.

So `--install` copies the script to `/usr/local/sbin`, owned by root, and enables a root service. The service
checks the mask early at every boot. After a cold boot it applies the core unlock again and does **one** warm
restart. A guard file prevents restart loops if the core unlock ever stops taking effect.

`--uninstall` removes the service and the copy. The stock 6C/12T returns after the next full power off. `--status`
shows the mask, the threads, and the state of the service and the guard.

> **Note.** A custom BIOS is another route to a lasting core unlock. It is not part of the suite, which stays
> software-only and reversible on the stock P5.00 BIOS.

## The window

![The window of BC-250 CPU Tools](../assets/cores/bc-cores-bisect-gui.webp)

`cores_bisect` is an optional PyQt6 window for both scripts, on one page. Its top half sets up a run of
`bc250-cores-bisect.sh` and starts it. Its bottom half keeps a tested unlock with `bc250-cores-unlock.sh`. The
window doesn't run the core bisect itself. **Start** hands off to a terminal that runs the exact command line you
would type by hand, and the window closes. You can also type everything it does by hand.

**Starting a run.** The pills under the title:

* **Help** says what the window does. Then it shows the script's own `--help` as a page. The page covers what the
  script does, the control, post-control and core items, and every option in a table.
* **Start** shows a summary of the options and, after Yes, starts the run in a terminal.
* **Show status** runs `--status` in a terminal. You see the results so far and the report. It starts nothing.
* **Reset** runs `--reset` after a question. That deletes every saved result and log in
  `~/.local/share/bc250-cores-bisect`. The script asks once more in the terminal.

Under them, on one line, are three fields:

* **Load per attempt** (`-t`)
* **Rounds per item** (`-r`)
* **Load tool** (`--load`), with the choices stress-ng, mprime and both

Hover a choice of **Load tool** to see what it does, and see [Longer burn-in](#longer-burn-in-mprime--rasdaemon).
Beside the fields is a rough estimate of the whole run, which follows the options. Its tooltip says how the app
works it out.

The switches are pills that say **On** or **Off**. A click turns one over:

* **Rasdaemon** (`--rasdaemon`) and **Same boot** (`--same-boot`).
* **Unattended** (`--auto`) turns on **Auto resume** with it. Auto resume writes and enables
  `~/.config/systemd/user/bc250-cores-bisect-auto.service`, which starts the run again after every restart and
  login. These are the same steps as the [`--auto` checklist](#running-truly-unattended---auto-checklist). The
  script disables the service again once every item is done. Auto resume can only be on with Unattended.

**Keeping the core unlock.** The window reads the results that `bc250-cores-bisect.sh` left in
`~/.local/share/bc250-cores-bisect`. It only enables **Install** once they accept the core unlock. The row for it:

* **Accepted** or **Not accepted** is the verdict on the bisect results. The verdict is Accepted only when all of
  this is true:
    * the bisect phase is finished
    * no attempt is still in progress
    * control and post-control are clean
    * every new core and the combined item passed **every** round

    The tooltip says why, for example a failing core or random failures. It also shows notes, which don't block.
    One note says that the control ran fewer rounds. Another says that the load changed during the run.
* **Install** enables the root service of `bc250-cores-unlock.sh --install`, which keeps the 8 cores at every
  boot. The pill is off until the results accept the core unlock.
* **Uninstall** removes the service. The cores stay on until the next full power off. Then the board is back to
  the stock 6C/12T.
* **Refresh** shows the threads and the state of the service and the guard. It runs `--status` and needs no root.
  It shows the mask too when sudo needs no password.
* **Root status** shows the same status as root, so it always shows the core presence mask. It asks for the sudo
  password when sudo needs one.
* **Re-check** reads the bisect results again, for example after more rounds finished. It writes the verdict and
  its reasons in the log.

Uninstall, Refresh, Root status and Re-check don't depend on the verdict. Install, Uninstall and Root status run
`bc250-cores-unlock.sh` through `sudo`. The password prompt is masked. The app passes the password to `sudo -S`
only and never stores it. The app only asks for the password when sudo needs one.

Under the row are the 8 physical cores in the order of the script's map. The 6 stock cores come first, then the 2
that the core unlock adds. Each of those 2 has one of these marks:

* `ok` passed every round
* `xx` fails every time
* `??` random
* `..` not tested yet

The **i** beside them explains the marks.

**Show logs** opens what `bc250-cores-unlock.sh` prints, and **Hide logs** closes it again. When an action fails, a
red **!** with **Check logs** appears beside the button. It goes away when you open the log.

Hover a field, its label or a pill to see what it does. The window remembers its size and position between runs.

**Installing it: `install.sh`.** Run it from a clone or the extracted release tarball. It installs these parts:

* a root-owned copy of the tools in `/opt/bc250-cores-bisect-v<version>`, with `/opt/bc250-cores-bisect`
  pointing at it
* a private PyQt6 venv in `~/.local/share/bc250-cores-bisect-app/venv`
* the launcher `~/.local/bin/bc250-cores-bisect-gui`
* an app menu entry and a Desktop icon

It also removes the separate unlock window of earlier versions. Run it as your own user. Only the copy to `/opt`
asks for the sudo password.

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app menu entry only, no Desktop icon
bc250-cores-bisect-gui               # or launch it from the app menu
./install.sh --uninstall             # remove the app; keeps results, settings and logs (and the unlock itself)
./install.sh --uninstall --purge     # also remove results, settings, logs and the autostart unit
```

Your bisect results stay in `~/.local/share/bc250-cores-bisect`. The installer never touches that folder unless
you pass `--purge`.

Per-user alternative, no `/opt` and nothing root-owned:

```bash
bash packaging/bazzite/install-bisect-gui.sh     # venv + launcher + menu entry "BC-250 CPU Tools"
bash packaging/bazzite/uninstall-bisect-gui.sh   # removes all of that again (keeps your results and the unlock)
```

**From a venv (development):**

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m cores_bisect   # --script PATH and --unlock-script PATH to use other scripts
```

You need a terminal emulator to see and run the core bisect. The window tries `$TERMINAL` first, then these:

* konsole
* gnome-terminal
* ptyxis
* xfce4-terminal
* foot
* alacritty
* kitty
* x-terminal-emulator
* xterm

The window shows an error if it finds none.

## Known side effect

After the core unlock, `pp_dpm_sclk` and the `hwmon` file `freq1_input` report nonsense GPU clocks of tens of MHz.
This is cosmetic. The SMU's own clock getters stay correct, and this script ignores GPU clocks.
Diagnostics that read those files will flag it, for example tests 19/40 of [Board Test](check.md). That is
expected while the core unlock is active. The GPU governor's `fix-freq` option puts the real clock back
(see [GPU Manager](gpu.md)).

## Credits

[rw-r-r-0644/bc250-core-unlock](https://github.com/rw-r-r-0644/bc250-core-unlock) (MIT) discovered and documented
the SMU quirk. The quirk is queue-3 message `0x98`, which writes `0xFF` at SMN `0x5A870`. This project
is an independent implementation built around those hardware facts. It adds the control/bisect/verdict
method, crash-safe multi-boot state, and reversible persistence.

## License

GNU GPLv3, see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/cores/LICENSE).
