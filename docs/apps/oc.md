<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 GPU OC Bisect](../assets/oc/bc250-gpu-oc-bisect.webp){ .app-logo }

# BC-250 GPU OC Bisect

!!! warning "Changes the board"
    The app only changes the GPU governor's settings file, /etc/cyan-skillfish-governor-smu/config.toml: for
    each attempt it puts a test clock and voltage in it and restarts the governor, which applies them, and puts
    your own file back after the attempt, on a temperature abort and when it exits. It never writes a register
    itself. Install writes the found safe point into the file, with a copy of the file from before it beside it,
    and restarts the governor; the file stays across reboots and power offs. A crash during an attempt can leave
    the test settings in the file until the script runs again and restores it first. Nothing is written to the
    BIOS, the firmware, the CMOS or the kernel's arguments. Uninstall copies the file from before the install
    back and restarts the governor.

Finds your **AMD BC-250's** (Cyan Skillfish, gfx1013) safe **GPU overclock and undervolt**, one step at a time.

No formula gives you the right GPU clock and voltage. The stable ceiling depends on these:

- your specific die, the silicon lottery
- your cooling
- your PSU rail

Two boards from the same batch can differ by 100 MHz or more. So the only honest answer is to test it. You raise the
clock or lower the voltage one step at a time. You put a heavy GPU load on it that checks its own results. Then you
see where your board stops being stable.

`bc250-gpu-oc-bisect.sh` does exactly that, in the same way its sibling projects bisect
[CUs](compute.md) and
[CPU cores](cores.md).

An **overclock** (OC) gives you more performance at the same voltage. An **undervolt** (UV) gives you the same
performance with less heat and power. The script finds how far your board can safely go in either direction. It can
then make the result permanent with `--install`.

!!! warning "Warning"
    This restarts the GPU governor with raised clocks or lowered voltages. An unstable step can freeze
    the system. That is the point of the test, but save your work first. The script enforces hard rails that you
    cannot override:

    - 2500 MHz ceiling
    - 1100 mV ceiling
    - 700 mV floor
    - 97 °C abort

    The community record of hard-locks above ~1850-2000 MHz is one reason for them. One bricked-board report from
    overvolting is the other. Use at your own risk.

## Quick start

```shell
chmod +x bc250-gpu-oc-bisect.sh
./bc250-gpu-oc-bisect.sh            # run the full sweep; repeat after any freeze until it says done
./bc250-gpu-oc-bisect.sh --status   # see the results and the recommendation
./bc250-gpu-oc-bisect.sh --install  # make the recommended point permanent (backup kept)
```

That is all most people need. The rest of this chapter explains what happens under the hood and which options you
have.

### Or use the GUI

The GUI is a PyQt6 launcher with the same look as the sibling projects' GUIs. In the GUI, you pick these:

- the load time
- the rounds
- an overclock sweep, an undervolt sweep or both
- the ladder limits and steps, capped at the hard rails

Then you click **Start GPU OC Bisect**. The window closes. The real sweep continues in a terminal, exactly as if you
typed it by hand. The window also has the buttons **Show status (--status)**, **Install result**, **Uninstall** and
**Reset**. **Reset** asks you to confirm first.

```shell
pip install -r requirements.txt
python -m oc_bisect
```

You can also install or update the desktop app from this repository or from an extracted release tarball. It adds a
launcher, an app-menu entry and an optional Desktop shortcut.

```shell
chmod +x install.sh
./install.sh
```

## How it works

On Bazzite, **cyan-skillfish-governor-smu** sets the BC-250 GPU's clock and voltage. This GPU governor is a service
that follows a frequency and voltage curve. The `[[safe-points]]` in `/etc/cyan-skillfish-governor-smu/config.toml`
define that curve. The stock top point is 2000 MHz @ 1000 mV. The script sweeps that top point in these steps:

| Step        | What changes                                                                    |
|-------------|---------------------------------------------------------------------------------|
| **control** | Nothing. The governor restarts with your own top safe-point. A failing control means power, heat or the load tool is at fault. Then you cannot trust any step verdict. |
| **oc:FREQ** | The top frequency goes up one step at a time, at a fixed voltage. A step is +50 MHz by default, up to `--max-freq`. The voltage is your config's top voltage by default. |
| **uv:VOLT** | The top voltage goes down one step at a time, at your stock top frequency. A step is -25 mV by default, down to `--min-volt`. |

For every attempt the script does this:

1. snapshots your own governor config
2. swaps in a temporary config whose top safe-point is the step under test
3. restarts the governor and runs a **verified** GPU load
4. watches the temperature, the clock and the GPU busy percentage the whole time
5. restores your own config and restarts the governor again

The temporary config keeps your other sections as they are, such as `[gpu]`, `[gpu-usage]` and the timings. The
verified load is [memtest_vulkan](https://github.com/GpuZelenograd/memtest_vulkan). It finds wrong results, not only
crashes. If memtest_vulkan is not installed, the script falls back to vkpeak, vkmark or glmark2. At 97 °C the script
stops the attempt and ends the whole run. You then improve the cooling and run the script again to continue. An
attempt gets the outcome **NO-REACH** if the GPU never gets near the requested clock under full load.

Every step runs 3 rounds by default. The script walks the ladder depth-first. All rounds of a step finish before it
tries the next step. So the sweep never drives past a step that is still failing. The script skips the steps beyond
a step that **fails every time**.

The sweep is **crash-safe**. A marker file records the attempt in flight. After a freeze, do a cold boot and run the
script again. It restores your config first. It records the crash against the right step. Then it resumes where it
left off.

### Verdicts

| Verdict             | Meaning                                                              |
|---------------------|----------------------------------------------------------------------|
| passes every round  | stable at this step                                                  |
| fails every time    | past your die's limit at this voltage, so the ladder stops here      |
| random              | It sometimes passes and sometimes fails. The cause is power, heat or margin noise, not a clean limit. |

The final recommendation is the best step that passed every round. The script also suggests the passing step one
notch back as the **margin pick** for daily use.

## Requirements

- AMD BC-250 running Bazzite, or any distro that uses cyan-skillfish-governor-smu
- `cyan-skillfish-governor-smu` installed, with its config at `/etc/cyan-skillfish-governor-smu/config.toml`
- [memtest_vulkan](https://github.com/GpuZelenograd/memtest_vulkan) in `~/.local/bin`, strongly recommended because
  it verifies results instead of only loading the GPU
- `sudo` for the governor config, `systemctl` and the kernel log

Run the script as your desktop user, not as root.

## Usage

```shell
chmod +x bc250-gpu-oc-bisect.sh
./bc250-gpu-oc-bisect.sh                 # sweep both: OC ladder then UV ladder
./bc250-gpu-oc-bisect.sh --oc            # frequency only
./bc250-gpu-oc-bisect.sh --uv            # voltage only
./bc250-gpu-oc-bisect.sh --status        # results so far + report on the Desktop
```

```text
-t, --time SECS      GPU load per attempt (default 180, minimum 60)
-r, --rounds N       attempts per step (default 3, 2-9)
    --oc             sweep frequency up (default when neither --oc nor --uv is given: both)
    --uv             sweep voltage down
    --max-freq MHZ   highest frequency to try (default 2200, hard ceiling 2500)
    --min-volt MV    lowest voltage to try (default 850, hard floor 700)
    --oc-volt MV     voltage used for the OC ladder (default: your config's top voltage; hard ceiling 1100)
    --freq-step MHZ  OC ladder step (default 50, minimum 25)
    --volt-step MV   UV ladder step (default 25, minimum 5)
    --per-boot       one attempt per boot for strict isolation (default: same boot with a cooldown;
                     the governor restart resets its state)
    --install        write the recommended margin step into the governor config and exit
    --uninstall      restore the governor config from the backup made by --install and exit
    --status         show the results so far and write the report, then exit
    --reset          delete the results and start over
-V, --version        show the version
-h, --help           show this help
```

### Making it stick

When the sweep is complete, `--install` writes the recommended margin point into the real governor config. It asks
you to confirm first. The script keeps a backup of your config at
`/etc/cyan-skillfish-governor-smu/config.toml.pre-oc-bisect`. `--uninstall` restores it and removes the backup. So a
later `--install` backs up the config of that moment.

## State and report

Everything lives in `~/.local/share/bc250-gpu-oc-bisect/`:

- `runs.tsv`, with a line for every attempt
- per-attempt logs in `logs/`
- the snapshot of your governor config

Each line in `runs.tsv` holds the step, MHz, mV, outcome, errors and faults. It also holds the highest temperature,
clock and busy percentage. `--status` writes a readable report to your Desktop. A finished run writes one too.

## Related projects

- [bc250-cu-bisect](compute.md) - CU unlock and bisect
- [bc250-cores-bisect](cores.md) - CPU cores unlock and bisect
- [BC-250 Board Test](check.md) - health-check test suite
- For the **CPU** side, voltage and frequency through the SMU, see
  [bc250_smu_oc](https://github.com/bc250-collective/bc250_smu_oc) from the BC-250 collective. This project sticks to
  the GPU curve on purpose.

## License

GPL-3.0 - see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/oc/LICENSE).
