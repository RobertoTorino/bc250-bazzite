<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 CU Tools](../assets/compute/bc250-cu-bisect.webp){ .app-logo }

# BC-250 CU Tools

!!! warning "Changes the board"
    The app writes the GPU's shader array and WGP mask registers with umr, as root, while the driver runs: that
    is the CU unlock. The registers are volatile: any reboot puts the stock 24 CUs back, and nothing is burned
    into the chip. The unlock stays across reboots and power offs only through the root service that CU Tools
    installs, bc250-cu-unlock.service with the masks in /etc/bc250-cu-bisect, which writes the registers again
    early at every boot. Nothing is written to the BIOS, the firmware, the CMOS or the kernel's arguments.
    Uninstall in CU Tools disables the service and removes its files; the unlock lasts until the next reboot,
    and the board is then stock. CU Tools reboots the board between its rounds, by itself with the unattended
    option, after a question otherwise.

BC-250 CU Tools tells **bad CUs** apart from an **unstable CU unlock** on the AMD BC-250 (Cyan Skillfish, gfx1013).
A CU is a compute unit of the GPU. CUs come in pairs, and a pair is a WGP.

Every BC-250 die differs. AMD fuses off WGPs that failed validation. But a crash after a CU unlock doesn't have to
mean a bad WGP. A runtime unlock writes GPU registers while the driver is running. The kernel and RADV keep their
24-CU view. Extra CUs draw more power at the same voltage. Crashes that move from one CU pair to another usually
point to the CU unlock, power or heat, not to bad silicon.

`bc250-cu-bisect.sh` does its own unlock, so no other tool is involved. It tests in a way that separates these
causes.

> **Warning:** this writes GPU registers. A bad WGP or the CU unlock itself can freeze the system. Save your
> work first. Use at your own risk.

## Unlocking extra CUs, step by step

New here? This is the whole process, start to finish. If you only read one section, read this one.

**What you're doing.** Your board ships with **24 CUs** active. Up to 16 more are switched off. AMD fused some of
them off because they are defective. Others are fine. These scripts find out which are good, and then switch on
the good ones at every boot.

**The only three outcomes.** The GPU has 4 identical rows, called shader arrays. It feeds all 4 in lockstep, so a
row with fewer active CUs holds the other three back. Only three settings do anything useful, and the tools here
will not let you install anything else.

| Setting                | Mask                  | What you get                      |
|------------------------|-----------------------|-----------------------------------|
| **24 CUs** (default)   | `0x07,0x07,0x07,0x07` | What the board does out of the box |
| **32 CUs**             | `0x0f,0x0f,0x0f,0x0f` | +1 good WGP on each of the 4 rows |
| **40 CUs** (max)       | `0x1f,0x1f,0x1f,0x1f` | +2 good WGPs on each of the 4 rows |

The tools **reject** anything in between. One example is 5 extra CUs on one row and none on another. It would
boot and run, but no faster than 24 CUs. It would also use more power and make more heat. So you're aiming for
32, and trying for 40.

---

**Step 1 — Install the prerequisites and read the warning.**
See [Requirements](#requirements) and [Before you start](#before-you-start). You need `umr`, and ideally
`memtest_vulkan`. Close your games and save your work. This *will* freeze the machine at some point, by design.

**Step 2 — Find out which switched-off CUs are good (`bc250-cu-bisect.sh`).**

```bash
chmod +x bc250-cu-bisect.sh
./bc250-cu-bisect.sh
```

It tests **one** switched-off WGP (2 CUs) at a time, under real GPU load. Then it asks you to restart and run it
again for the next one. There are 8 switched-off WGPs and 3 test rounds each, so about **27 boots** in total.
Expect this to take a day or two of on-and-off work. With `--auto`, it restarts by itself without asking, see
[Running truly unattended](#running-truly-unattended---auto-checklist). Each WGP ends up with one of the three
verdicts in [Results](#results):

- GOOD
- FAILS EVERY TIME, which is bad silicon, so leave it off
- RANDOM

**Step 3 — Read the suggestion at the end.**
When every WGP has a verdict, the script prints the best **even** mask your board supports. For example:

```
- WGPs that passed every round: SE0.SH0.WGP3 SE0.SH1.WGP3 SE1.SH0.WGP3 SE1.SH1.WGP3
  Combined: 0x0f,0x0f,0x0f,0x0f (32 CUs, WGPs per row: 4 4 4 4).
```

If one row had a bad WGP, the script trims the others down to match. So what it suggests is always 24, 32 or 40,
never a lopsided number like 38.

**Step 4 — Retest that exact combination (this step is not optional).**
WGPs that each pass alone can still fail *together*. More active CUs draw more power at the same voltage. So run
the suggested command, which tests the full combined mask in one go:

```bash
./bc250-cu-bisect.sh --reset && ./bc250-cu-bisect.sh --baseline 0x0f,0x0f,0x0f,0x0f --control-only --rounds 1
```

Replace the mask with the one *your* run suggested. This is a single boot, not another 27.

**Step 5 — Make it permanent (`bc250-cu-unlock.sh`).**
A CU unlock is only ever register writes. Nothing is burned into the chip, so it's gone after a restart. This
second script applies it again at every boot. It does that as a system service that runs before your desktop
starts:

```bash
chmod +x bc250-cu-unlock.sh
sudo ./bc250-cu-unlock.sh --install 0x0f,0x0f,0x0f,0x0f
```

That's it. From now on the board comes up with 32 or 40 CUs on every boot. That includes cold boots and boots
after system updates. The script refuses to install a mask that isn't one of the three even settings.

**Step 6 — Verify it's actually live.**

```bash
sudo ./bc250-cu-unlock.sh --status     # "Live masks now:" is read straight off the GPU
```

Trust that line over any CU count that other GPU tools show. Most of them cache the number the driver saw at
boot, as [the note further down](#keeping-the-unlock-after-a-reboot) explains.

**Step 7 — Want to go back?**

```bash
sudo ./bc250-cu-unlock.sh --uninstall  # stock 24 CUs again from the next boot
```

Do this if the system starts misbehaving later. A WGP that passed the tests can still turn out unstable under a
different game or in a hotter room.

> **Prefer clicking to typing?** [The window](#the-window) does exactly the same thing. Its top half starts
> steps 2–4, and its bottom half handles steps 5–7. It shows **Accepted** only once your results justify the mask.
> Until then, **Install** is grayed out.

## How it works

The script writes the three registers of a runtime CU unlock with [umr](https://gitlab.freedesktop.org/tomstdenis/umr):

| Register                         | Per shader array | Meaning                                    |
|----------------------------------|------------------|--------------------------------------------|
| `CC_GC_SHADER_ARRAY_CONFIG`      | yes              | Bits 16-20 mark WGPs inactive, cleared to 0 |
| `SPI_PG_ENABLE_STATIC_WGP_MASK`  | yes              | WGPs that get work, 5 bits of 2 CUs each   |
| `RLC_PG_ALWAYS_ON_WGP_MASK`      | no               | Union of the four SPI masks                |

The BC-250 has 4 shader arrays of 5 WGPs each, which is 40 CUs. The arrays are SE0.SH0, SE0.SH1, SE1.SH0 and
SE1.SH1. Stock is 24 CUs.

```
             WGP0   WGP1   WGP2   WGP3   WGP4      mask (bit4..bit0)
             bit0   bit1   bit2   bit3   bit4
SE0.SH0       ██     ██     ██     ..     ..      0x07
SE0.SH1       ██     ██     ██     ..     ..      0x07
SE1.SH0       ██     ██     ██     ..     ..      0x07
SE1.SH1       ██     ██     ██     ..     ..      0x07

██ baseline, always unlocked (the stock 24 CUs)   .. locked WGP, 2 CUs, not yet tested
```

Each row is a 5-bit `SPI_PG_ENABLE_STATIC_WGP_MASK` value. WGP0 is bit 0 and WGP4 is bit 4. A set bit means that
WGP is unlocked (2 CUs). Read the stock row above from right to left, WGP4 first, to get `00111`, which is `0x07`.
In it, WGP0-2 are unlocked and WGP3-4 are locked. A row with all 5 WGPs unlocked is `11111`, which is `0x1f`.

The 4 rows are always written together as `SE0.SH0,SE0.SH1,SE1.SH0,SE1.SH1`. So the stock baseline above is
`0x07,0x07,0x07,0x07` (24 CUs). A fully unlocked board would be `0x1f,0x1f,0x1f,0x1f` (40 CUs). This is exactly
the format that `--baseline` takes, and that `--status` and the window print back.

That's the default layout. 3 of the 5 WGPs per shader array ship unlocked, which is 24 CUs. The other 2 per array
are fused off at the factory. Those 8 WGPs (16 CUs) are what this script tests one by one. The script shows this
same map live while it runs. `>>` marks the WGP under test. Once a WGP has a verdict, it shows `ok` for GOOD, `xx`
for FAILS EVERY TIME or `??` for RANDOM. See [Results](#results).

> **Only 24, 32 or 40 CUs exist.** The GPU front-end splits work across the 4 shader arrays in lockstep. The
> slowest row caps them all. Unlocking WGPs on only one or two rows doesn't speed anything up, because the other
> rows still bottleneck at their old CU count. The extra CUs just sit idle, hot and powered. So the only
> configurations worth having unlock the *same* number of WGPs on every row.
>
> | WGPs per row | Mask                  | Total CUs            |
> |--------------|-----------------------|----------------------|
> | 3            | `0x07,0x07,0x07,0x07` | **24** (stock/default) |
> | 4            | `0x0f,0x0f,0x0f,0x0f` | **32**               |
> | 5            | `0x1f,0x1f,0x1f,0x1f` | **40** (max)         |
>
> The per-row mask doesn't have to be exactly `0x0f` or `0x1f`. If WGP3 is bad on a row but WGP4 is good, `0x17`
> is also 4 WGPs. What matters is that all 4 rows unlock the *same count*.
>
> `bc250-cu-unlock.sh` and the window **refuse** anything else. They reject an uneven mask like
> `0x1f,0x1f,0x07,0x07` (5/5/3/3) with an error and don't install it.

The test plan:

- **Control.** The same register writes with your baseline masks, so no extra CUs. If the control fails, the
  unlock method, power or heat is at fault. The WGP verdicts then can't blame your CUs.
- **One step per locked WGP.** The baseline plus that single WGP (2 CUs). The script tests every locked WGP on
  its own.
- **Rounds.** Every item runs several times, 3 by default. The rounds are interleaved, so heat and time don't
  favor one item.
- **One attempt per boot.** This is the default. Every attempt starts from the clean driver state.
- **Idle writes.** The script only writes the masks while the GPU is idle, then reads them back. During the load
  it reads them again every 10 s to catch masks that drift.
- **Correctness, not only crashes.** `memtest_vulkan` reports wrong results. The script uses vkpeak, vkmark or
  glmark2 when it's missing, but those only show crashes.
- **Crash-safe.** Before every phase the script saves what it's doing. After a freeze, cold boot and run it
  again. It then records the crash and its phase, either writing the masks or under load. It also records the
  GPU faults in the kernel log of the previous boot.

## Requirements

- AMD BC-250, Linux with bash 4+. Tested against Bazzite (Fedora Atomic).
- `umr`, owned by root, in `/usr/bin`, `/usr/sbin` or `/usr/local/bin`.
  On Bazzite, run `sudo rpm-ostree install umr`, then restart. "Already requested" means it's waiting for that
  restart.
- A GPU load tool, preferably [memtest_vulkan](https://github.com/GpuZelenograd/memtest_vulkan/releases)
  in `~/.local/bin`. vkpeak, vkmark and glmark2 work too.
- sudo rights, only for umr and the kernel log.

## Before you start

1. Every boot must start at the stock state. Turn off anything that applies a CU unlock at boot, and don't run
   other CU tools during the test. The script refuses to start when a CU unlock is already active.
2. Cap the GPU governor at 1500 MHz, for example in `/etc/cyan-skillfish-governor-smu/config.toml`. Then power
   and heat don't hide the result. The script warns when the ceiling is higher.
3. Close games and video players.

## Usage

Run it as your normal user:

```bash
chmod +x bc250-cu-bisect.sh
./bc250-cu-bisect.sh                 # baseline = the stock masks of this boot, 3 rounds, 180 s load
./bc250-cu-bisect.sh -t 300 -r 5     # longer load, more rounds
./bc250-cu-bisect.sh --baseline 0x07,0x07,0x07,0x07   # start from masks you trust
./bc250-cu-bisect.sh --baseline 0x0f,0x0f,0x0f,0x0f --control-only --rounds 1   # re-validate a combined mask, control only
./bc250-cu-bisect.sh --status        # results so far, report on the Desktop
./bc250-cu-bisect.sh --same-boot     # no reboots: restore the baseline live between attempts
./bc250-cu-bisect.sh --auto          # no prompts, auto-reboot after each attempt (see below)
./bc250-cu-bisect.sh --reset         # delete the results and start over
./bc250-cu-bisect.sh --help
```

After each attempt it offers to power off or restart. Powering off is best, because it gives a cold boot. Power
on and run it again until all attempts are done. With 3 rounds and 8 locked WGPs that's 27 boots. `--same-boot`
is faster, but every attempt then inherits the state of the previous one.

### How long a full run takes

Total attempts = rounds × (1 + locked WGPs). The 1 is the control. Each attempt takes about 15 s to settle, then
the load time, then a few seconds of overhead. The load time is `--time`, 180 s by default. That is roughly
`load time + 20 s` of active GPU time per attempt. On top of that:

| Test type                                   | Per-attempt overhead                         | Example: 3 rounds, 8 locked WGPs (27 attempts), default 180 s load |
|----------------------------------------------|-----------------------------------------------|---------------------------------------------------------------------|
| Default, a restart or power off between attempts | a full boot, and your own clicks          | 27 × ~200 s plus 27 boots, typically 2 to 3 hours with the restarts |
| `--same-boot`                                 | 30 s cooldown, no restart                     | 27 × ~230 s ≈ 1 h 45 min hands-off                                   |
| `--auto` with the systemd unit, see below     | a full boot, but no manual steps              | same wall-clock as the default mode, but unattended                 |
| `--control-only`                              | only the control item is tested               | `rounds` attempts instead of `rounds × (1 + WGPs)`, for example 3 instead of 27 |

More rounds (`-r`) or a longer load (`-t`) scale the total time linearly. Each extra locked WGP adds one more
item, which is `rounds` more attempts.

### Running truly unattended (`--auto` checklist)

Clicking through 27 restarts by hand is slow. `--auto` keeps one attempt per boot, so nothing is lost in
correctness. It removes the manual steps:

- It doesn't ask anything. It takes an unfinished attempt for a crash, and it goes on past warnings.
- It restarts on its own when more attempts are left, and doesn't ask.

Combine it with the included systemd user unit. The script then also starts again after every login. That turns
the whole bisect run into a loop you only have to start once:

```bash
mkdir -p ~/.config/systemd/user
cp bc250-cu-bisect-auto.service.example ~/.config/systemd/user/bc250-cu-bisect-auto.service
# edit ExecStart in that file to the real path of bc250-cu-bisect.sh
systemctl --user enable --now bc250-cu-bisect-auto.service
systemctl --user status bc250-cu-bisect-auto.service 
```

`--auto` makes the *script* hands-off, but the *system* must get back to your session on its own:

* **Autologin.** After each restart someone must log in, or the run stalls at the login screen. Turn autologin
  on in your desktop. On Bazzite with KDE, go to System Settings → Colors & Themes → Login Screen (SDDM) →
  Behavior → auto-login. On GNOME, go to Users → auto-login.
* **sudo without a password.** The script still needs sudo for `umr` and the kernel log. There's no terminal to
  type a password into. Add a drop-in file for sudo:

```bash
echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/bc250-cu-bisect
sudo chmod 440 /etc/sudoers.d/bc250-cu-bisect
sudo visudo -cf /etc/sudoers.d/bc250-cu-bisect   # must print "parsed OK"
sudo -k && sudo -n true && echo OK    # must print OK without asking
```
Revert after testing with `sudo rm /etc/sudoers.d/bc250-cu-bisect`.
If you edit the file by hand, use `sudo visudo -f /etc/sudoers.d/bc250-cu-bisect`. It refuses to save a broken
line. A broken line makes every `sudo` command print a warning, or stops sudo working at all.

The script first tries `systemctl reboot` with `--no-ask-password`. With that option it fails where it would
otherwise open a password dialog that nobody is there to answer. Then it falls back to `sudo -n systemctl reboot`.
If both fail, the script stops, so it doesn't hang, and tells you to restart by hand. Most desktops let the
logged-in user restart and power off directly. If yours doesn't, add passwordless sudo for `systemctl reboot`
and `poweroff` too.

For a truly unattended run, for example overnight, make sure of this as well:

* **The autostart unit installed.** Without it nothing starts the script again after login. You'd have to start
  it by hand at every boot.
* **No credential popups at login (KDE Wallet / ksshaskpass).** With autologin the KDE Wallet can't unlock by
  itself. So an "SSH credentials" or wallet dialog can appear at session start. It blocks the chain until you
  answer it. Either give the wallet a blank password, or turn the wallet subsystem off. For a blank password,
  open the wallet in `kwalletmanager5` first, then choose Change Password and leave it empty. Plasma 6 has no
  checkbox for the wallet subsystem anymore, so turn it off with this command:

```bash
kwriteconfig6 --file kwalletrc --group Wallet --key Enabled false   # kwriteconfig5 on Plasma 5
```

Turn it on again afterward with `... --key Enabled true`. Also uncheck "Use KWallet for the Secret Service
interface" in System Settings → KDE Wallet. Then apps don't send secrets to the wallet that is off.

Check on it while it runs:

```bash
systemctl --user status bc250-cu-bisect-auto.service   # ran / running / failed this boot
tail -f ~/.local/share/bc250-cu-bisect/auto.log         # live output of the current attempt
./bc250-cu-bisect.sh --status                           # progress and results so far
```

When all attempts are done, the script stops restarting on its own. In `--auto` mode it also turns
`bc250-cu-bisect-auto.service` off by itself. It removes the optional live-output autostart entry below too. So
nothing starts at the next login.

Starting a new `--auto` run turns the unit on again if it's still installed but was left off. If the unit isn't
installed at all, the script warns. The run then can't continue past a restart. If you ran without `--auto`,
turn the unit off by hand with `systemctl --user disable --now bc250-cu-bisect-auto.service`.

A real freeze still needs a power cycle by hand, the same as without `--auto`. The script resumes from there as
usual.

Want the live output on screen and not in a log file? Add a desktop autostart entry that opens a terminal
following it at every login. This is a KDE example. The comments in `bc250-cu-bisect-auto.service.example` say
more:

```bash
cat > ~/.config/autostart/bc250-cu-bisect-watch.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=BC-250 bisect live output
Exec=konsole --title "bc250-cu-bisect" -e tail -n 40 -f .local/share/bc250-cu-bisect/auto.log
EOF
```

## Results

While it runs, and in the summary and the report, the same CU map shows where it's at:

```
             WGP0   WGP1   WGP2   WGP3   WGP4
SE0.SH0       ██     ██     ██     ok     ..
SE0.SH1       ██     ██     ██     xx     ..
SE1.SH0       ██     ██     ██     ..     ??
SE1.SH1       ██     ██     ██     >>     ..

██ baseline  >> testing now  ok passed every round  xx fails every time  ?? random  .. not tested yet
```

Outcomes per attempt:

| Outcome       | Meaning                                                                |
|---------------|------------------------------------------------------------------------|
| `PASS`        | Load ran the full time, no errors, no kernel faults, masks held        |
| `ERRORS`      | memtest_vulkan reported wrong results                                  |
| `FAULT`       | GPU fault in the kernel log, such as a ring timeout, GPU reset or page fault |
| `LOAD-FAIL`   | The load tool stopped early                                            |
| `CRASH-LOAD`  | The system went down under load                                       |
| `CRASH-APPLY` | The system went down while writing the masks on an idle GPU           |
| `DRIFT`       | The masks changed after they were written                              |
| `MISMATCH`    | The masks didn't read back as written                                  |
| `ABORTED`     | Stopped by hand, so the attempt runs again                             |

Verdict per WGP:

- **GOOD.** It passed every round.
- **FAILS EVERY TIME.** Likely a bad WGP, so leave it locked. It says "(memory errors)" when memtest_vulkan
  found errors.
- **RANDOM.** It failed in some rounds only. A bad WGP normally fails every time, so this points to the unlock
  method, power or heat.

`CRASH-APPLY`, `DRIFT` and `MISMATCH` point to the CU unlock itself. When the control fails, the WGP verdicts are
not reliable.

> **Note: `GPU load only reached X%` even on a healthy PASS.** On the BC-250 the
> `gpu_busy_percent` sensor the script reads can stay near 0% while the GPU is under load.
>
> Look at the clock (`max sclk MHz`). It should still boost under load, and drop on a failing WGP. If it does,
> the SMU's real DPM/boost logic is reacting correctly. The load was real, and only the busy percentage is
> unreliable on this hardware. Don't treat a low or 0% busy reading by itself as a sign that the test didn't
> stress the GPU.

When everything is done and the control passed, the script suggests a combined mask of the good WGPs. WGPs that
pass one by one can still fail together, because they draw more power at the same voltage. So test the
combination:

```bash
./bc250-cu-bisect.sh --reset && ./bc250-cu-bisect.sh --baseline <masks> --control-only --rounds 1
```

With `--control-only`, the script doesn't bisect the WGPs that are still locked in `<masks>` again. One example
is a WGP you already know is bad and left out on purpose. Only the `control` item runs, so this is a single-boot
check and not another full bisect run.

The suggested mask is always even already, at 24, 32 or 40 CUs. If one row has a bad WGP, the script trims the
other rows down to match. You can't install an uneven mask, and it wouldn't be faster anyway. Once the
combination also passes, make it survive a restart with
[bc250-cu-unlock.sh](#keeping-the-unlock-after-a-reboot).

Files, in `~/.local/share/bc250-cu-bisect/`:

- `umr-runs.tsv`: one line per attempt, with the columns listed below
- `umr-config`: baseline, rounds and load time
- `logs/`: the load tool's output per attempt

The columns of `umr-runs.tsv`:

- time
- boot
- round
- item
- masks
- outcome
- memtest errors
- kernel faults
- drift
- max temperature
- max clock
- max GPU busy
- note

The script writes a readable report to the Desktop when all attempts are done, and with `--status`.

## Keeping the unlock after a reboot

A runtime unlock resets to stock at every boot. It only ever writes registers, and nothing is fused. So by
default you're back to 24 CUs the next time you start the system.

`bc250-cu-unlock.sh` is a separate, standalone script. At every boot it applies a mask again that you've already
validated. It does that as a root systemd service that starts before the display manager. It does not retest
anything, and it's not a diagnostic. Only use it once a mask has passed the bisect run above:

```bash
chmod +x bc250-cu-unlock.sh
sudo ./bc250-cu-unlock.sh --install 0x0f,0x0f,0x0f,0x0f   # save, apply now, enable at every boot
./bc250-cu-unlock.sh --status                             # installed masks, service state, live masks
sudo ./bc250-cu-unlock.sh --uninstall                     # disable it; stock 24 CUs from the next boot
```

`--status` shows the live masks only when you run it with sudo, or when sudo needs no password.

**Only 24, 32 and 40 CUs can be installed.** `--install` checks the mask before it touches a single register.
So does a bare apply. They refuse anything that isn't 3, 4 or 5 WGPs on *every* one of the 4 shader-array rows:

```
$ sudo ./bc250-cu-unlock.sh --install 0x1f,0x1f,0x07,0x07
ERROR: uneven mask 0x1f,0x1f,0x07,0x07 - 5/5/3/3 WGPs on SE0.SH0/SE0.SH1/SE1.SH0/SE1.SH1.
  The GPU drives all 4 shader arrays in lockstep, so an uneven unlock runs no faster than its
  smallest row while burning the extra power. Unlock the SAME number of WGPs on every row.
  Allowed: 3 per row = 24 CUs (stock), 4 per row = 32 CUs, 5 per row = 40 CUs (max).
  Example 32 CUs: 0x0f,0x0f,0x0f,0x0f     Example 40 CUs: 0x1f,0x1f,0x1f,0x1f
```

**Once `--install` has run, the CU unlock is persistent.** The systemd service applies the saved mask again on
every single boot from then on. You don't need to do anything more, and you don't need to run the script again.
It survives restarts, power-offs, cold boots, and kernel and OS updates alike. Only `--uninstall` turns that off
again, or deleting the service and its config by hand.

Only install a mask that:

- passed with the control, so no crashes with just the baseline masks
- came back GOOD for every WGP in it, on its own, in `bc250-cu-bisect.sh`
- was then also tested as the combined mask itself, because WGPs that pass alone can still fail together
- unlocks the same number of WGPs on all 4 shader arrays, for 24, 32 or 40 CUs, which the script enforces

> **Worked example: why an uneven mask gets rejected.** Say your bisect run found one bad WGP, `SE1.SH0.WGP4`,
> and everything else good. The "everything that passed" combination would be `0x1f,0x1f,0x0f,0x1f`. That is 38
> CUs, with `5/5/4/5` WGPs per row. Both the script and the window refuse it.
>
> This isn't a bug. The GPU front-end splits work across the 4 shader arrays in lockstep. So the row with the
> fewest active WGPs caps the actual performance. The spare WGP on the other 3 rows just sits unused. `38` CUs
> (`5/5/4/5`) performs the same as `32` CUs (`4/4/4/4`). You get no real-world gain in speed, just extra power
> and heat.
>
> With one WGP permanently bad, the best option is `4/4/4/4`. Drop the spare good WGP on the 3 healthy rows to
> match the row with the bad one. `bc250-cu-bisect.sh` does this trim for you and suggests the even mask
> directly.
> ```
> ./bc250-cu-bisect.sh --reset && ./bc250-cu-bisect.sh --baseline 0x0f,0x0f,0x0f,0x0f --control-only --rounds 1
> ```
> That retest passes evenly on all 4 rows, so the window shows **Accepted**. You get 32 real, usable CUs over
> the stock 24.

Config and the systemd unit:

- `/etc/bc250-cu-bisect/masks`: the installed masks, one line
- `/etc/systemd/system/bc250-cu-unlock.service`: the service, with `Before=display-manager.service`

With `Before=display-manager.service`, the service applies the CU unlock before anything starts using the GPU.

A real hang is still a real hang. A WGP you thought was GOOD can turn out unstable under different conditions
later. Then boot, run `sudo ./bc250-cu-unlock.sh --uninstall`, and restart to go back to stock.

> **If the CU unlock doesn't survive a restart: `--install` now fails loudly instead of lying.**
>
> `systemctl enable` can fail while the CU unlock is still applied for the *current* boot only. Causes include
> SELinux and a read-only `/etc/systemd/system` on some images. Earlier versions printed "Installed and enabled"
> regardless. You'd only find out after the next restart that it never persisted.
>
> `--install` now checks the actual result. It exits with an error and doesn't claim success. The error names
> `systemctl status bc250-cu-unlock.service` and `journalctl -u bc250-cu-unlock.service` to check. If you're on
> an older copy of the script, update it and run `--install` again to see the real reason for the failure.
>
> **How to be 100% certain of the live CU count.** More than one thing can report a CU count, and they are
> not all equally trustworthy:
>
> - `sudo ./bc250-cu-unlock.sh --status` → **"Live masks now"** reads the actual GPU registers right now. This
>   is the ground truth for the current boot.
> - Test #21 of [Board Test](check.md) reads the exact same registers, read-only. It agrees with the line above by
>   construction.
> - `--status` → **"Configured masks"** is just what's saved in `/etc/bc250-cu-bisect/masks`. This is what you
>   *asked* to install, not proof that it's active. If `--install` failed without saying so, as described above,
>   this can show 32 CUs while the live registers are back to 24.
> - Third-party GPU info and monitoring apps, such as `rocm-smi` and Vulkan/OpenCL CU counts. These typically
>   read the CU count that the `amdgpu` driver cached once, when it probed the GPU at boot or driver load. They
>   don't read the registers again. Say you unlock registers at runtime, or a persistence service runs after
>   the driver already probed. Then these can keep showing a stale number until the driver probes again, which
>   takes another restart. That goes in either direction.
>
> When in doubt, trust `--status`'s "Live masks now" or test #21 over anything else. They are the only ones that
> read the hardware directly, at the moment you ask.

### The window
![bc-cu-bisect-gui.webp](../assets/compute/bc-cu-bisect-gui.webp)

`cu_bisect` is an optional PyQt6 window for both scripts, on one page. Its top half sets up a run of
`bc250-cu-bisect.sh` and starts it. Its bottom half installs a tested CU unlock with `bc250-cu-unlock.sh`. The
window doesn't do the bisecting itself. **Start** hands off to a terminal that runs the exact command line you'd
have typed by hand, and the window closes.

**Starting a run.** The pills under the title:

* **Help** says what the window does, then shows the script's own `--help` as a page. The page says what the
  script does, explains the control and WGP steps, and lists every option in a table.
* **Start** shows a summary of the options and, after Yes, starts the run in a terminal.
* **Show status** runs `--status` in a terminal. You see the results so far and the report. It starts nothing.
* **Reset** runs `--reset` after a question. It deletes every saved result and log in
  `~/.local/share/bc250-cu-bisect`. The script asks once more in the terminal.

Under them, on one line, are **Load per attempt** (`-t`), **Rounds per item** (`-r`) and **Baseline**. Baseline
is a preset:

* **Auto-detect** uses this boot's own clean masks. This safe default doesn't pass `--baseline`.
* **Stock, 24 CUs** is `0x07,0x07,0x07,0x07`.
* **Unlocked, 40 CUs** is `0x1f,0x1f,0x1f,0x1f`.
* **Custom...** takes any other 4-mask value, checked as you type.

Hover a choice in the list to see its masks.

The switches are pills that say **On** or **Off**. A click turns one over:

* **Control only** (`--control-only`), **Same boot** (`--same-boot`) and **No watch** (`--no-watch`).
* **Unattended** (`--auto`) turns on **Auto resume** with it. Auto resume writes
  `~/.config/systemd/user/bc250-cu-bisect-auto.service` and turns it on. That service starts the run again after
  every restart and login. These are the same steps as the "Running truly unattended" checklist above. Auto
  resume can only be on with Unattended.

**Installing the CU unlock.** The window doesn't take your word for it. It reads the results that
`bc250-cu-bisect.sh` recorded. **Install** only turns on once they show all of this:

* the combined mask was retested as its own baseline, with no locked WGPs left in that run
* every round of that retest passed
* the 4 rows are even

The row for it:

* **Accepted** or **Not accepted** is the verdict on the bisect results. Its tooltip says why, for example "still
  has 2 WGP(s) under individual test" or "did not pass every round".
* **Install** applies the accepted mask now and keeps it on every boot. It uses the same systemd service as
  `bc250-cu-unlock.sh --install`. The pill is off until the results accept a mask.
* **Uninstall** turns the service off. The board is back to the stock 24 CUs from the next restart.
* **Refresh** shows the installed masks and the service's state (`--status`). It shows the live masks too when
  sudo needs no password.
* **Re-check** reads the bisect results again, for example after another retest. It writes the verdict and its
  reasons in the log.

**Uninstall** and **Refresh** don't depend on the verdict, so you can always turn the service off. Install and
Uninstall run `bc250-cu-unlock.sh` through `sudo`. The window asks for your password in a masked prompt. It
passes the password to `sudo -S` only and never stores it.

Under the row are the four shader-array rows, SE0.SH0 to SE1.SH1, with their five WGPs each. A WGP that is on is
green. The rows show the accepted mask, or the one you preview. **Preview a mask** shows any 4-row mask on the
rows without writing anything. It says how many CUs the mask gives and whether you can install it. You can
install only 24, 32 or 40 CUs, with the same number of WGPs on every row. The **i** beside it explains how to
write a mask.

**Show logs** opens what `bc250-cu-unlock.sh` prints, and **Hide logs** closes it again. When Install or Uninstall
fails, a red **!** with **Check logs** appears beside the button. It goes away when you open the log.

Hover a field, its label or a pill to see what it does. The window remembers its size and position between runs.

Run it straight from a clone, on any distribution:

```bash
cd bc250-bazzite/apps/compute
python3 -m venv _python && _python/bin/pip install -r requirements.txt && _python/bin/python -m cu_bisect
```

On Bazzite, `install.sh` installs it for your user. You get:

- a private venv under `~/.local`
- a launcher
- an app-menu entry
- an icon
- a Desktop icon

It layers nothing with `rpm-ostree` and puts nothing outside your home directory. It also removes the separate
unlock window of earlier versions. Run it as your own user, not with sudo:

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app-menu entry only, no Desktop icon
bc250-bisect-gui                     # or launch it from the app menu
./install.sh --uninstall             # removes the app again (not any results, settings or the unlock itself)
./install.sh --uninstall --purge     # also removes the results, settings, logs and autostart entries
```

`install.sh` runs `packaging/bazzite/install-bisect-gui.sh`, which also works on its own.

You need a terminal emulator to see the bisect run and to start it. The window tries `$TERMINAL` first, then these:

- konsole
- gnome-terminal
- ptyxis
- xfce4-terminal
- foot
- alacritty
- kitty
- x-terminal-emulator
- xterm

The window shows an error if it finds none.

## Releases

Releases have the tag `bc250-compute-v<x.y.z>` in the suite repository. You find them on its
[releases](https://github.com/RobertoTorino/bc250-bazzite/releases) page as `bc250-compute-v<x.y.z>.tar.gz`, with
a `SHA256SUMS` file. The tarball holds the whole set of tools:

- `bc250-cu-bisect.sh`
- `bc250-cu-unlock.sh`
- the window
- `packaging/`
- images and docs

If you just want to run the scripts or the window, download and extract it on the board. You don't need to clone
the repository. The portal installs it for you too.

## Related

[bc250-cores-bisect](cores.md) is the sibling project. It uses the same strategy for the 2 fused-off CPU cores.
That is a control, a per-core bisect run, a verdict, then a reversible persistent 8C/16T unlock.

[Board Test](check.md) holds the diagnostics for the BC-250 on Bazzite. Its test number 21 reads the live CU
masks from the same registers, read-only.

## License

GNU GPLv3, see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/compute/LICENSE). This
keeps the project free and open source, with any forks or redistributions of it. Anyone can use, study and
change it. A closed-source or proprietary fork isn't allowed. Derivatives must stay under the same license and
keep their source available too.
