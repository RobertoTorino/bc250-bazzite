<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Board Test](../assets/check/bc250-board-test.webp){ .app-logo }

# BC-250 Board Test

BC-250 Board Test checks an **AMD BC-250** board running **Bazzite** (Fedora Atomic / rpm-ostree). It has
read-only diagnostics, a stress test and benchmarks. The board has the Cyan Skillfish APU, `gfx1013`, PCI
`1002:13fe`.

The tests install nothing and change no setting. There are two exceptions, and you start both yourself:

* The stress test puts the board under load on purpose.
* The write part of the disk speed test writes one temporary file and removes it.

---

## Download and install

BC-250 Board Test is part of the [BC250 Bazzite Suite](https://github.com/RobertoTorino/bc250-bazzite). It is
always installed with the suite. Install the suite's **portal** (see [Install](../install.md)), and this app comes
along.

You can also install it on its own. Its release is on the suite's
[Releases](https://github.com/RobertoTorino/bc250-bazzite/releases) page, as `bc250-check-v<version>.tar.gz` with
a `SHA256SUMS` file. To hear about new releases, click **Watch → Custom → Releases** on the suite page.

The app itself layers nothing with `rpm-ostree`. The test engine goes to `/opt`. The GUI's Python packages go
into the suite's shared venv in your home directory.

**1. Download and verify.** Get both files from the Releases page. Then run this in the download folder:

```shell
sha256sum --check --ignore-missing SHA256SUMS
```

**2. Extract and run the installer** as your own user, not with `sudo`. It asks for your password only to
copy the app to `/opt`.

```shell
tar -xzf bc250-check-v*.tar.gz
cd bc250-check-v*/
./install.sh
```

**3. Start** **BC-250 Board Test** from the app menu or the icon on your Desktop, or run
`bc250-board-test` in a terminal. You can delete the extracted download folder.

What `install.sh` does:

* It copies the app, with the `bc250_core` it was released with, to `/opt/bc250-board-test-v<version>`.
  That folder is owned by root.
* It points `/opt/bc250-board-test` at that folder and removes older versions.
* It uses the suite's shared venv `~/.local/share/bc250-bazzite-suite/venv` with PyQt6, and makes it on first
  use. The wheels bundle Qt, so nothing else is needed. The first download is ~100 MB.
* The venv is removed with the last suite app that uses it.
* It adds the launcher `~/.local/bin/bc250-board-test`, an app menu entry and a Desktop icon.
  `./install.sh --no-desktop-shortcut` skips the Desktop icon.

**Optional tools.** The app runs without extras. A test whose tool is missing says so. The table lists the tools
the tests use when they are there. The suite's [Quickfix](quickfix.md#quickfix) quickfix shows which ones are
there and installs them.

| Tool | Used by | Group |
|------|---------|-------|
| `stress-ng` | 41 CPU + GPU Stress (CPU load), 42 Performance Benchmark (CPU score), 49 CPU Memory Bandwidth | RPM packages |
| `lm_sensors` (`sensors`) | 22 Hardware Sensors | RPM packages |
| `vkmark` | 41 CPU + GPU Stress, as the GPU load when memtest_vulkan and vkpeak are missing | RPM packages |
| `nvme-cli` (`nvme`) | 10 NVMe Devices (SMART health) | RPM packages |
| `fio` | 43 Disk Speed (random 4K read) | RPM packages |
| `memtest_vulkan` | 41 CPU + GPU Stress, as the GPU load and a VRAM error check | Binaries in `~/.local/bin` |
| `vkpeak` | 42 Performance Benchmark (GPU score), and 41 CPU + GPU Stress as the GPU load when memtest_vulkan is missing | Binaries in `~/.local/bin` |
| Ookla `speedtest` | 44 Internet Speed (`speedtest-cli` works too) | Speed test in `~/.local/bin` |
| `mprime` (Prime95) | No test. [BC-250 CPU Tools](cores.md#longer-burn-in-mprime--rasdaemon) runs its torture test for a longer burn-in | Prime95 in `~/mprime`, with a link in `~/.local/bin` |
| `sqlite` (`sqlite3`) | No test. It looks into the app's history database during development | Development extras |

Tests 10, 20, 21 and 41 also use `glmark2`, `vulkan-tools` (`vulkaninfo`, `vkcube`) and `smartmontools`
(`smartctl`). Those come with Bazzite.

The script `/opt/bc250-board-test/development/tools/install-requirements.sh` installs the tools. Run without
an option, it asks per group. It says what each group is for and what it installs, and it skips what is there
already.

* **RPM packages** are layered with `rpm-ostree`. They become active after a restart (`systemctl reboot`).
* **Binaries** (`vkpeak`, `memtest_vulkan`) are the latest releases from their GitHub projects.
* **The speed test** is Ookla's CLI. Running it accepts Ookla's license and privacy terms.
* **Prime95** is `mprime`, the release that mersenne.org's download page lists. The script compares the download
  with the SHA-256 listed there before it unpacks it. Run the script again when there is a newer release, and it
  installs that one over the old one.
* **Development extras** are only for working on the app.

```bash
/opt/bc250-board-test/development/tools/install-requirements.sh          # asks per group
/opt/bc250-board-test/development/tools/install-requirements.sh --all    # every group except the development extras, no questions
```

`--rpms`, `--bins`, `--speedtest`, `--mprime` and `--dev` install one group.

> **Why `/opt`?** The test engine runs as root through sudo. So a release build checks `test-board.sh` before it
> runs it. The file and every folder above it must be owned by root, and only root may write to them. The file
> must also match the SHA-256 recorded when the release was built. A copy in your home directory fails that
> check on purpose.

**Update:** Update from the portal. Or download, verify and extract the new release and run its `./install.sh`
again. It replaces the old version. Your settings and the history are kept, because they live in your home
directory.

**Uninstall:** Removing the portal removes this app too. To remove only this app:

```shell
/opt/bc250-board-test/install.sh --uninstall           # keeps settings, history and reports
/opt/bc250-board-test/install.sh --uninstall --purge   # removes those too
```

## Reporting problems

Open an [issue](https://github.com/RobertoTorino/bc250-bazzite/issues/new/choose) for the app **check**. Add the
app version (**Settings → About**) and the full report of the run (**Show Logs**). The report contains details
about your system, so read it before you post it. For security problems, see [SECURITY.md](../SECURITY.md).

---

## Using the app

* **Run all tests** runs every test except the benchmark (42), the disk speed test (43) and the internet speed
  test (44). The stress test runs along only when **Include stress test (41) in run** is checked.
* You can also open a category on the left and run one test, or all tests of that category.
* A test button turns **yellow** while it runs. Then it turns **green** (passed), **orange** (warning),
  **red** (failure) or **blue** (information only).
* The output appears in the terminal of the page. Fix suggestions appear in the **Hints** panel next to it.
* The boxes at the top count the latest result of every test and give a **health score**. Click
  **Warnings**, **Failures** or **Info / hints** to see what is behind the number.
* The light **Base System** and **Extended System** boxes, at the end of the row, rate the hardware and its
  setup. Click either one for the breakdown. [System score](#system-score) explains how they are calculated.
* Most checks need administrator rights. When a password is needed, a masked prompt appears. The password
  is never shown, saved or logged.
* **History** lists every run by date, and you can pick a date range. Select a run to see its results and
  measurements.
* Select two runs with Ctrl-click to compare them side by side, for example before and after a CU unlock. You see
  what got better or worse, and by how much.
* The run button shows the progress, and the time left during the stress test.
* Closing the window during a run asks first and stops the tests cleanly.
* A run of a minute or more that finishes while you're in another window gives a desktop notification
  (**Settings → General**).
* The app remembers its window size, the last page, the panel sizes and the stress settings.
* **Show Logs** lists earlier runs, colored like the live output.
* **Settings** has privacy options, a system overview, log cleanup, version information and **Print results**.
* The benchmark (42), the disk speed test (43) and the internet speed test (44) are never part of
  **Run all tests**. Start them from their own buttons, on an idle system.

**Print results** shows a compact "BC-250 Board Test Results" card. It holds the Base and Extended System scores
and the other header boxes, so it is easy to compare with other users. Under the card are three buttons:

* **Save…** saves the card as a PNG where you choose, and opens it. The first suggestion is results.png in
  Downloads.
* **Copy** puts it on the clipboard, to paste in a chat or a forum post.
* **Share** has three kinds of entries. The first sends the card to a phone paired with KDE Connect, with one
  entry per phone in reach. **Email…** opens your mail app with the card attached. **Show in file manager**
  shows it in the file manager.

The file manager's own right-click **Share** has the rest of what KDE offers, such as Imgur, Telegram,
Nextcloud and Bluetooth. **Share** first writes the card to `results-card.png` in
`~/Desktop/bc250-board-test/`. That file is overwritten each time.

**Game details** records a game while you play, like MangoHud's logging:

* Copy its launch line into the game's **Properties → Launch options** in Steam. It works alongside
  `mangohud %command%`.
* Every session becomes a graph. It shows FPS, the game's CPU/GPU share, total load, GPU and CPU clocks and
  temperatures, power, voltage, VRAM and GTT, the fan and the free system memory.
* When the game ends, the page also shows **Checks for the last session**. They are listed below.
* Per game, you can turn recording on or off and set the sample interval.
* A screenshot of the game is taken once during the first recorded session and shown on the page.
* FPS and the frametime checks need MangoHud with logging on. See [A game's FPS](#a-games-fps).
* The page also reads the launch options in Steam. A line that starts the game monitor from a folder or python
  that is gone would stop the game from starting. Such a game is listed with the line to put in its place.
* Copy the launch line from the installed app, not from a checkout. A line from a checkout stops working when
  that folder moves.

**Checks for the last session** cover:

* the real 1%/0.1% lows and the stutter share, from MangoHud's per-frame log
* whether the session was GPU-bound or CPU-bound
* whether the VRAM carve-out, GTT or RAM ran out
* whether the board was power-capped or lost clocks to heat
* any amdgpu errors the kernel logged while the game ran

**In-game overlay:** the app has its own overlay in its own style. Its buttons are **Show overlay** and
**Test overlay** on the Game details page.

* With **Test overlay** you can drag it anywhere on the screen. The position is saved, and the in-game overlay
  appears there.
* The in-game overlay is click-through, so it never steals a click from the game.
* It is a separate window. Games in exclusive fullscreen bypass the compositor (direct scanout), so no external
  window can appear above them.
* Only something drawn inside the game's own frames can. MangoHud works that way, as a Vulkan/OpenGL layer
  injected into the game.
* So for fullscreen games use **Set MangoHud overlay style**. It writes a MangoHud config that the app owns. The
  launch-line wrapper passes it to MangoHud, and it comes close to the look of the app's overlay.
* The app's own overlay does work over games in windowed or borderless-fullscreen mode.

### System score

A stock BC-250 on the latest BIOS, set up as recommended and with every default below met, scores exactly **100**.
That board has:

* BIOS 5.00
* 24 CUs
* 6 cores/12 threads
* a 512 GB NVMe reading 850 MB/s
* a 1 Gbit/s link
* the ACPI fix
* a 6 GB VRAM split
* mitigations off
* the IOMMU disabled
* zswap with a disk swapfile
* a 100% health score

Anything below a default costs points. Upgrades only raise the Extended score, so the Base score never exceeds
100. Upgrades are more CUs or cores, a bigger or faster drive, or a faster link.

| Item | Points | Default (full points) | Above the default (Extended score only) |
|---|---|---|---|
| **Hardware** | **55** | | |
| GPU compute units | 20 | 24 CUs, evenly distributed (see below) | In proportion: 32 CUs = 26.7, 40 CUs = 33.3 |
| CPU cores / threads | 15 | 6 cores / 12 threads (cores 75%, threads 25%) | In proportion: 8C/16T = 20 |
| NVMe read speed (test 43) | 10 | 850 MB/s. The PCIe 2.0 slot tops out at ~1000 MB/s | +25% of the points per doubling |
| NVMe capacity | 5 | 512 GB. 480 GB and up count | +25% of the points per doubling: 1 TB = 6.25, 8 TB = 10 |
| Wired network link | 5 | 1 Gbit/s, the onboard port's maximum | +25% of the points per doubling. A 2.5 GbE USB adapter = 6.7 |
| **Configuration** | **45** | | |
| BIOS | 5 | 5.00. 3.00 = 3 and 1.00 = 1. A modded BIOS counts as current | None |
| ACPI fix (test 26) | 10 | Applied: cpufreq scaling and CPU idle states exist | None |
| VRAM split (test 37) | 10 | 6 GB (`bc250memcfg UMA_SIZE 6144`). Any other split gets 5 | None |
| CPU mitigations (test 24) | 5 | Off (`mitigations=off`) | None |
| IOMMU (test 23) | 5 | Disabled (no IOMMU groups) | None |
| Swap (test 14) | 5 | zswap in front of a disk swapfile. zram + disk or disk only gets 3. zram only or zram + zswap gets 2. No usable swap gets 0 | None |
| Health score | 5 | 100% | None |

* **Base System Score**: an item below its default costs points in proportion. An item above it earns nothing,
  so the maximum is 100. The score is rounded down, so a board on an older BIOS can never reach 100.
* **Extended System Score**: the Base score plus what goes beyond the defaults. On a stock board it is
  equal to the Base score.
* An item that is not measured yet scores 0. The pop-up lists the test to run for it.
* **CU balance**: the CUs sit in 4 shader arrays of 5 WGPs, with 2 CUs per WGP. The array with the fewest CUs
  sets the pace.
* An uneven unlock is scored as the evenly distributed count below it, which is 4 x the smallest array. So
  10/8/6/8 = 32 CUs counts as 24. The pop-up warns that the CUs are not evenly assigned.
* The per-array counts come from test 21, which needs root and `umr`. Without them the total is rounded
  down to a multiple of 8, so to 24, 32 or 40.

## The window in detail

**The left pane** holds the Overview, one page per test category, History, Game details, Help and Settings.
Help is this chapter.

**The boxes at the top** count the latest result of every test over all runs, also after a restart:

* **Tests** is the number of tests available.
* **Finished** counts the tests with a result in the history.
* **Passed**, **Warnings**, **Failures** and **Info / hints** count those results.

The test buttons show that result too, and their tooltip has its date. Behind **Warnings**, **Failures** and
**Info / hints** are the WARNING, ERROR or INFO lines per test, with the hints from the log of that result.
Click a test name to open its page, or **Show in log** to open the run log at that test.

* **Health score:** passed and info tests count 100%, warnings 50% and failures 0%, averaged over the tests
  that ran. Green from 90%, orange from 70%, red below.
* **CPU score** (purple) and **GPU score** (blue) show the last performance benchmark (test 42). 100 is your
  board in its stock configuration. Hover for details.

**The status bar** at the bottom right shows live values, every 2 s:

* **CPU / GPU:** whole-system load. The GPU load comes from the kernel sensor, from the governor's patched
  `gpu_metrics` (fix-metrics on) or from the GPU time of your processes. Hover to see which, and what a sample
  costs.
* **🎮 Game:** while a game runs, its name, and the share of the CPU and GPU it uses. The name comes from Steam,
  or from the game's .exe. With MangoHud logging on, it also shows the FPS.
* **↓ / ↑:** download and upload traffic over the wired and Wi-Fi interfaces, from `/proc/net/dev`.
* **Hz:** the refresh rate of the display the app is on.
* **Live:** switch it off to stop sampling. It also pauses while the window is minimized.

The status bar only reads a few files from `/proc` and `/sys`. A sample takes about 1 ms, and a full process scan
runs every 10 s. It slows down by itself if sampling gets expensive, so it is safe to keep running while you
play.

**Settings** opens a panel over the window. Close it with ✕, Esc or a click outside. It has these pages:

* **Privacy**: what is stored and sent, history and log masking, administrator rights
* **General**: notifications, copying the reports to the Desktop
* **System overview**: BIOS version, CUs, cores, threads, speed test, NVMe size, free space and package count at
  a glance
* **Logs & history**: clean up logs
* **About**: version, build date, repository
* **Print results**

### Running and stopping

* **Run all tests** never includes the benchmark (42), the disk speed test (43) or the internet speed test
  (44).
* **Run all &lt;category&gt; tests** runs every test on that page.
* Only one run happens at a time. The buttons are off while it runs.
* **Stop** stops the current run. The tests first end their CPU and GPU load and remove their temporary files.
  The test that was running goes back to not run.
* A test takes the color of the worst line it logged. An error counts over a warning, a warning over a success,
  and a success over info.
* Its output also streams into the terminal of the test's own category page.
* The **Hints** panel collects suggested fixes (⚠) and background notes (ℹ).

### Administrator password

Most checks read root-only logs and sysfs, so the tests run through `sudo`. When sudo needs a password, a masked
prompt appears. The password goes straight to sudo and is never stored or logged. sudo remembers it for its
usual timeout, so you are not asked for every test.

**Settings › Privacy** can turn sudo off. Then fewer checks run, and you are never asked for a password. It can
also make sudo forget the password right away.

### Logs

Every run is saved as `~/.local/share/bc250-board-test/logs/<YYYYmmdd-HHMMSS>_<scope>.log`. **Show Logs** on a
page lists that page's runs. **Show all logs** lists every run.

**Mask personal data in saved GUI logs** is on by default (**Settings › Privacy**). It replaces personal data
in these files with placeholders. The terminal shows everything. The masked data is:

* the host and user name
* the home folder
* serial numbers
* MAC and IP addresses
* the speed test's ISP and result URL

Below the list of runs, **Files mentioned in this run** lists every log, CSV and config file the selected run
refers to. Examples are the full report, the stress CSV, the GPU load tool log and the governor config. Click
one to read it.

* A warning icon means the file is not on this machine.
* Very large files show their last 2 MiB.
* Root-only files show the `sudo less` command to use instead.
* For a CSV, **Show graph** plots it.

**Clean up logs** is under **Settings › Logs & history**. It removes the run logs older than N days, or all logs.
The default is 30 days. The dialog shows what goes before anything happens. Removing old logs keeps the results in
the history. **Remove ALL** also empties the history. The full reports are owned by root, so removing them asks
for your password. `bench-baseline.json` and the benchmark and speed test history CSVs are always kept.

### History

Every result is stored in a small SQLite database, `~/.local/share/bc250-board-test/history.db`. It holds:

* per run, the date, scope, active CUs and cores/threads
* per run, the kernel version and mitigation state, only when turned on in **Settings › Privacy**
* per test, the status and the number of hints
* the numbers worth comparing, which are benchmark scores, stress clocks, temperatures and power, and disk and
  internet speeds

Some full reports are not in the history yet. They are in `/var/log/bc250-board-test` and the Desktop folder.
The app imports them once, at startup. The database grows by a few KB per run. Only your user can read the
history and the logs.

The app checks the history at every start. When it is damaged or was changed outside the app, the app keeps it
aside as `history.db.damaged-<date>`. Then a new, empty history starts.

On the **History** page, **From** / **to** pick the dates and **All dates** shows everything again.

* **One run selected:** its results per category, its measurements and the files it wrote. **Show logs** opens
  its log and full report. Click a test name to open its page.
* **Two runs selected** (Ctrl-click or Shift-click): side by side, with the older run on the left. You see the
  counts and configuration, the tests whose result changed and every measurement with the difference.
* Green is better, red is worse. Differences under 2% count as the same, as measurement noise.
* Uncheck **Only differences** to see every test.

A typical use is to run everything and the benchmark, then change something, such as a CU unlock, the BIOS, the
kernel or the governor. Then run them again and compare the two runs.

### Integrity of the tests

Before every run the app checks the test files. They must be exactly the ones that came with this version, and
only an administrator can change them. **Why `/opt`?** above explains this. If the check fails, no tests run,
since they would run with administrator rights. A red bar at the top says so. Then reinstall the app.

### Graphs

**Show graph** opens a chart window for the CSV files the tests write:

* **Stress telemetry**, next to the stress settings, shows the latest stress run. It has panels for clocks,
  temperatures, GPU busy, GPU power, GPU memory, fan, GPU voltage and load average, with the peaks on top.
* Pick older runs from the **File** list.
* A clock that drops while the temperature climbs is thermal throttling. A line that simply stops is the moment
  the board froze.
* **Benchmark history**, on the Performance page, shows bar charts per run. They cover the scores against the
  baseline, GPU FP32, CPU multi- and single-thread, VRAM bandwidth and GPU clock.
* Its bars are labeled *#run CUs threads*. Hover for the date, mitigations and kernel.
* **Any CSV** in Show Logs: one panel per numeric column.

Drag a rectangle to zoom in, right-click to zoom out, hover a line for its value. **Save as PNG…** saves all
panels as one image. Graphs need the `PyQt6-Charts` package, which the installer puts in the venv.

### Stress test and benchmark settings

**Stress test (41):**

* **Stress duration** is how long the load runs, 10–3600 s. The default is 120.
* **Sample interval** is the seconds between telemetry samples. The default is 2.
* The test loads all CPU threads with `stress-ng`, or with shell busy-loops.
* It loads the GPU with `memtest_vulkan`, `vkpeak`, `vkmark`, `glmark2` or `vkcube`. `memtest_vulkan` is
  recommended, because it also checks the VRAM for errors.
* This is a deliberate attempt to reproduce lockups under load. The system is sluggish while it runs and may
  freeze. If it does, the last telemetry line is the board's final operating point.
* The app asks before it starts.

**Benchmark (42):**

* **CPU time per phase** is the seconds per `stress-ng` phase. The default is 20. Keep it the same between runs
  you compare.
* The log also shows the theoretical FP32 peak for the detected CU count and clock. A result far below it means
  unlocked CUs are not doing work.
* Close games and other heavy apps first.
* [Performance score](#performance-score-comparing-cu-and-core-unlocks) explains how to save the baseline.

### A game's FPS

The FPS comes from MangoHud's log, which it writes while the game runs. Turn it on once in
`~/.config/MangoHud/MangoHud.conf`:

```ini
output_folder=/home/<you>/mangohud-logs
autostart_log=1
log_interval=500
```

Create the folder, and make sure MangoHud is active for the game. One way is the Steam launch option
`mangohud %command%`. MangoHud writes a log file per game session, so delete old ones now and then. Without
logging, the game's name and its CPU and GPU share are still shown. The suite's
[MangoHud Config](quickfix.md#mangohud-config) quickfix sets the three lines and makes the folder for you.

The **Game details** launch line does not work with the **Flatpak** version of Steam, because the game would not
start. Use the Steam that comes with Bazzite. The **Checks for the last session** always describe the newest
session. Older sessions keep their graphs.

## Output files

All files go to `/var/log/bc250-board-test/`:

| File                                       | Contents                                                                               |
|--------------------------------------------|----------------------------------------------------------------------------------------|
| `bc250-test-results-<YYYYmmdd-HHMMSS>.log` | Full report.                                                                           |
| `bc250-stress-<YYYYmmdd-HHMMSS>.csv`       | Stress telemetry, written only by a stress run.                                        |
| `bc250-gpuload-<YYYYmmdd-HHMMSS>.log`      | Output of the GPU load tool, written only by a stress run.                             |
| `bc250-memtest-<YYYYmmdd-HHMMSS>.log`      | memtest_vulkan's own log, when it was the GPU load tool.                               |
| `bc250-bench-<YYYYmmdd-HHMMSS>.json`       | Benchmark result, written only by the benchmark.                                       |
| `bc250-bench-vkpeak-<YYYYmmdd-HHMMSS>.log` | vkpeak output of the benchmark.                                                        |
| `bc250-bench-history.csv`                  | One line per benchmark run, to compare configurations over time.                       |
| `bc250-disk-<YYYYmmdd-HHMMSS>.csv`         | Write speed and drive temperature per 256 MiB, only when writes are tested.            |
| `bc250-speedtest-<YYYYmmdd-HHMMSS>.json`   | Raw speed test result, only by the internet speed test.                                |
| `bc250-speedtest-history.csv`              | One line per speed test, with interface, server, speeds, idle/loaded latency, jitter and loss. |

At the end of the run they are copied to `~/Desktop/bc250-board-test/` of the desktop user, for easy sharing.
In the GUI this is **Settings > General > Copy the full reports to Desktop**, on by default. On the command line,
`--no-desktop` skips it.
During a stress run the files are flushed to disk after every sample, so they survive a hard lockup.

The GUI also keeps its own captured output of every run as
`~/.local/share/bc250-board-test/logs/<YYYYmmdd-HHMMSS>_<scope>.log`. These are not the files above. They hold
what the script printed during that run.

In-game monitoring writes one CSV per gameplay session to
`~/.local/share/bc250-board-test/game-logs/bc250-game-<game>-<YYYYmmdd-HHMMSS>.csv`. Its columns are
`elapsed_s, fps, game_cpu_pct, game_gpu_pct, cpu_pct, gpu_pct, sclk_mhz, mclk_mhz,
gpu_temp_c, gpu_power_w, vram_used_mib, gtt_used_mib, vddgfx_mv, fan_rpm, cpu_temp_c, cpu_mhz_avg,
mem_avail_mib`. The **Game details** page opens these files as graphs.

Next to each CSV is a small `.json` with what is only measured once per session:

* the VRAM/GTT budget
* the GPU power cap
* the real 1%/0.1% lows and stutter share from MangoHud's per-frame log
* the amdgpu errors the kernel logged while the game ran

The **Game details** page turns both into the pass/warn/fail **Checks for the last session**.

The columns of the stress CSV are `elapsed_s, sclk_mhz, mclk_mhz, gpu_busy_pct, vram_used_mib, gtt_used_mib,
gpu_temp_c, gpu_power_w, vddgfx_mv, cpu_tctl_c, cpu_mhz_avg, fan_rpm, load1`. Open it directly in
LibreOffice Calc to plot clocks, memory and power against temperature.

`gpu_busy_pct` comes from the kernel's `gpu_busy_percent` when it works. Stock kernels have no GPU-load
sensor for Cyan Skillfish, so the read fails. That is also why MangoHud and the Steam overlay show 0% unless
the governor's `fix-metrics` is on. The app then measures the gfx and compute engine time of every GPU
client from `/proc/*/fdinfo`, the same method nvtop uses. The log states which source was used.

The summary reports peak VRAM and GTT use as a percentage of each budget. It warns at 90% VRAM, when allocations
spill into GTT. It warns at 85% GTT, when the GPU is close to running out of memory.

Every line is tagged `SUCCESS`, `INFO`, `WARNING` or `ERROR`, and a `[SUMMARY]` block at the end
reports the overall verdict. In the app these become the button colors, the counters and the hints panel.

---

## Tests

### System

| #  | Test                         | Checks                                                                          |
|----|------------------------------|---------------------------------------------------------------------------------|
| 00 | Platform Identification      | Confirms the board really is a BC-250. Reports the BIOS, stock or modded, the Bazzite image and the kernel. The latest stock BIOS 5.00 is a pass. An older stock BIOS is a warning with an update hint. |
| 01 | Running Services             | Lists every active systemd service.                                             |
| 02 | Failed Units                 | Errors on any unit in a failed state.                                           |
| 03 | System Uptime                | Reports uptime and load average.                                                |
| 11 | Resource Consumption         | Top CPU and memory consumers.                                                   |
| 12 | Boot Time                    | `systemd-analyze` breakdown, warns on units taking over a minute.               |
| 31 | File and Directory Integrity | Lists `/var/log` and verifies that it exists.                                   |

### Network

| #  | Test                   | Checks                                                                    |
|----|------------------------|---------------------------------------------------------------------------|
| 04 | Network Connectivity   | Pings an external host.                                                   |
| 05 | DNS Resolution         | Resolves a known hostname.                                                |
| 06 | Public Internet Access | Fetches a URL over HTTPS.                                                 |
| 07 | Open Ports             | Lists listening TCP/UDP sockets.                                          |
| 08 | NTP Synchronization    | Confirms the clock is synchronized.                                       |
| 30 | SSH Service            | Reports `sshd.service` / `sshd.socket` state. SSH is off by default on Bazzite. |
| 53 | Wi-Fi Adapter          | Every Wi-Fi adapter and whether the kernel has a driver for it. See below. |
| 44 | Internet Speed         | **Opt-in**. Run it from its button on the Network page. See below.       |

**How test 44 measures the connection.** It uses Ookla's `speedtest`, or `speedtest-cli` as a fallback. A run
takes about 30 s.

* **Download and upload** in Mbps, plus the data used. That is roughly 1 GB on a gigabit line.
* **Idle latency and jitter**, and the **latency while downloading/uploading**. Only Ookla's CLI measures loaded
  latency.
* When the loaded latency is more than 100 ms above idle, the line suffers from *bufferbloat*. Games then lag
  whenever something else uses the connection. The fix is SQM (fq_codel/CAKE) in the router.
* **Packet loss** (Ookla only): over 1% is a warning.
* **The local link** is the interface the traffic uses, Ethernet or Wi-Fi, and its link speed.
* A 10/100 Mbit/s Ethernet link is a warning, because it points to a bad or 2-pair cable. A download near the
  link speed means the port is the limit.
* A VPN in the path is noted, because then the VPN is measured, not the line.
* Every run is appended to `bc250-speedtest-history.csv`. **Show graph** compares all runs.
* To install Ookla's CLI, download the Linux x86_64 `.tgz` from <https://www.speedtest.net/apps/cli>. Put the
  `speedtest` binary in `~/.local/bin`. Running it accepts Ookla's license and GDPR terms.

**What test 53 says about Wi-Fi.** The BC-250 has no Wi-Fi of its own. A USB stick or a PCIe card adds it. The
test lists every Wi-Fi adapter it finds, with its USB or PCI ID and its driver. It says one of these for each:

* **connected**, a success. It reports the band, the signal in dBm and the link speed. The network's name stays
  out of the report.
* **works, not connected**. Connect it in the network settings.
* **switched off** by rfkill, in software or by a hardware switch. This is a warning.
* **the driver is there but not loaded**. The running kernel has a module for the stick's ID that is not loaded.
  The test gives the `modprobe` command.
* **firmware missing**. The driver took the adapter but did not get its firmware file at this boot.
* **no driver**. The running kernel has no driver for the stick's ID, so it does not work on Bazzite as it is.
* **storage mode**. The stick shows up as a small disk with the Windows driver. Most sticks switch when that disk
  is ejected. An AIC8800D80 stick, such as the UGREEN AX900, has no driver in Bazzite's kernel. So it does not
  work on Bazzite as it is.

Sticks with a Realtek (rtw88, rtw89) or MediaTek (mt76) chip mostly have a driver in Bazzite's kernel. The test
only reads. It loads no module and switches no stick. When there is no adapter at all, the test reports that
without a warning, because the network cable needs nothing.

### Storage and memory

| #  | Test                             | Checks                                                                                 |
|----|----------------------------------|----------------------------------------------------------------------------------------|
| 09 | Disk Configuration               | Filesystem usage and mount points.                                                     |
| 10 | NVMe Devices                     | Detection. PCIe link speed and width against what the drive and the slot support. DRAM cache, or a host memory buffer on a DRAM-less drive. SMART health, with wear, media errors, spare, temperature, time spent throttling and unsafe shutdowns. |
| 14 | Memory and Swap                  | RAM usage and the full swap topology, with zram, zswap, disk swap, overlaps and swappiness. |
| 37 | Unified Memory and VRAM Pressure | VRAM/GTT usage, OOM-kill history, `vm.max_map_count`, swappiness.                      |
| 49 | CPU Memory Bandwidth             | `stress-ng` STREAM-like bandwidth on 1 thread and all threads. Shows the GDDR6 latency cost the CPU pays for the GPU's console-class bandwidth. |
| 43 | Disk Speed (read, write, SLC cache) | **Opt-in**. Run it from its button on the Storage page. See below.                   |

**How test 43 measures the system disk.** That is the disk that holds `/var/tmp`.

* **Sequential read**: `dd` reads 4 GiB straight from the partition with direct I/O. Nothing is
  written. The result is compared with the PCIe link ceiling from test 10.
* **Random 4K read** at queue depth 1 and 32: `fio --readonly` over the whole partition, 10 s each.
  This part is skipped without a system-wide `fio`, because a Homebrew fio is not run as root. A high QD1
  latency, over ~150 µs, is typical of a DRAM-less drive without a host memory buffer.
* **Sequential write and SLC cache**, only with **Disk speed test (43): also test writes** checked:
    * It writes a temporary file in `/var/tmp` in 256 MiB chunks, with direct I/O and flushed. It deletes the
      file afterward.
    * The file is created with `chattr +C`, so btrfs doesn't compress it. Compression would fake the result.
    * Each chunk's speed and the drive temperature go to `bc250-disk-<timestamp>.csv`. **Show graph**
      plots it.
    * The point where the speed falls below 60% of the starting speed is reported as the SLC cache
      size. If the drive was at its warning temperature at that moment, it is reported as thermal
      throttling instead.
    * Pick a size larger than the expected cache. That is a few GiB on cheap/QLC drives and tens of GiB on
      large TLC drives. The test needs that size plus 5 GiB free.
    * The run stops early if the drive reaches its critical temperature.

**DRAM cache detection (test 10)**:

* No drive reports "has DRAM" directly.
* DRAM-less NVMe drives ask the host for a *Host Memory Buffer*. That is the `HMPRE` field of
  `nvme id-ctrl`. The kernel logs it as `allocated N MiB host memory buffer`.
* The test reads both. If neither is present, the drive has its own DRAM.
* On the BC-250 the HMB comes out of the RAM that is shared with the GPU, usually 32–64 MiB.

### System logs

| #  | Test           | Checks                                                                   |
|----|----------------|--------------------------------------------------------------------------|
| 15 | Boot Logs      | Current-boot kernel errors, with known-benign BC-250 noise filtered out. |
| 16 | System Journal | Journal errors from the last 7 days, same filtering.                     |

Tests 15, 16 and 17 follow the log lines with a hint per kind of line. The hint says what the line means and what
to do about it, with the number of lines it covers. Real faults come first, such as GPU hangs, disk errors and
crashes. Known harmless messages come after them. A service that failed gets the commands to read why and to turn
it off. Lines without a known explanation are grouped per program, with the command to read them.

### GPU and graphics

| #  | Test                  | Checks                                                                     |
|----|-----------------------|----------------------------------------------------------------------------|
| 17 | amdgpu Driver         | Confirms `amdgpu` is bound to the Cyan Skillfish APU.                      |
| 18 | GPU Governor          | Verifies a governor is running. Without one the GPU is pinned at 1500 MHz. |
| 19 | GPU Frequency Scaling | Reads `pp_dpm_sclk` / `pp_dpm_mclk` to confirm the clock actually moves.   |
| 20 | Vulkan / Mesa         | Confirms RADV reports GFX1013 and not the llvmpipe software fallback.      |
| 21 | Compute Unit Count    | Active CUs from the live GPU registers, which needs admin rights and umr. Otherwise, the kernel value. Stock is 24, unlocked is up to 40. Explains why the kernel and RADV keep reporting the probe-time value. |
| 29 | Display Session, DisplayPort and HDMI | Identifies the display manager, session type and compositor, and the connector status. |
| 47 | Vulkan Futureproof Matrix | Vulkan API level and the feature set modern games need. That is ray tracing, mesh shaders, VRS, pipeline libraries and the VRAM carveout against today's 8 GiB recommendation. Hard evidence of which current and upcoming titles can run at all. |
| 50 | Video Decode and Encode (VCN) | `vainfo` codec matrix for H.264/HEVC/VP9/AV1 decode and encode. Matters for streaming, OBS recording and video playback while gaming. |
| 51 | HDMI-CEC | The CEC adapter of the DisplayPort output, which exists only when the DP-to-HDMI converter tunnels CEC. Whether the TV answers a poll, and Bazzite's CEC mode. Together they say whether the board can turn the TV on and off. See [BC-250 CEC Manager](cec.md). |
| 52 | HDMI-CEC Services | Whether the services behind the TV control run. These are Valve's CEC daemon (`cecd`), BC-250 CEC Manager's background and boot services when installed, and Bazzite's dGPU CEC services when enabled. A service that is installed but not running is a warning. One that is not installed is only reported. |

### CPU and firmware

| #  | Test                      | Checks                                                                          |
|----|---------------------------|---------------------------------------------------------------------------------|
| 23 | IOMMU Disabled            | Counts IOMMU groups. IOMMU is broken on the BC-250 and must be off, via the BIOS or the `amd_iommu=off` kernel argument. The [IOMMU Off](quickfix.md#iommu-off) quickfix sets it. |
| 24 | CPU Mitigations           | Passes when `mitigations=off` is set, worth roughly +18 FPS on this board. The [CPU Mitigations Off](quickfix.md#cpu-mitigations-off) quickfix sets it. |
| 25 | CPU Core and Thread Count | Reports cores and threads. Stock is 6C/12T, and 8C/16T after the unlock.        |
| 26 | CPU Power Management      | Checks cpufreq scaling and C-states. Both need the BC-250 ACPI fix.             |
| 46 | CPU Voltage               | CPU/SoC voltage rails from hwmon (amdgpu `vddgfx`/`vddnb`) plus the voltage each core requests. That is the current P-state VID via MSR, one line per core. |

### Stability and thermals

| #  | Test                          | Checks                                                                        |
|----|-------------------------------|-------------------------------------------------------------------------------|
| 22 | Hardware Sensors              | nct6683/nct6687 SuperIO, GPU and CPU temperatures, CPU and GPU rails, fan RPM sanity. |
| 27 | Handheld Daemon               | Confirms `hhd.service` is masked. It causes constant micro-stuttering.        |
| 28 | Suspend Targets               | Which sleep the board offers, whether systemd may use it, and the suspends since boot. |
| 40 | Power Delivery and Throttling | GPU power cap and draw, governor frequency ceiling, throttle messages.        |

### Crash forensics

| #  | Test                                | Checks                                                                                      |
|----|-------------------------------------|---------------------------------------------------------------------------------------------|
| 34 | Previous Boot Shutdown Integrity    | Flags previous boots that ended with no shutdown sequence, the signature of a hard lockup.  |
| 35 | GPU Hang and Reset History          | Ring timeouts, GPU resets, VM faults and soft recoveries across retained boots.             |
| 36 | Kernel Panic, Lockup and Crash Dump | Oopses, soft/hard lockups, call traces, `coredumpctl` records and NMI watchdog state.       |

### Gaming

| #  | Test                           | Checks                                                                                  |
|----|--------------------------------|-----------------------------------------------------------------------------------------|
| 38 | Steam and Gaming Stack         | Steam, gamescope, gamemode, MangoHud, umu. Library paths and free space.                |
| 39 | Audio Stack                    | PipeWire/WirePlumber state, default sink and ALSA cards.                                |
| 48 | Real-Game Frametime (MangoHud logs) | Reads the most recent MangoHud logs from real play sessions for average FPS, 1% and 0.1% lows and stutter share. That is evidence from actual games, which synthetic benchmarks cannot give. |
| 41 | CPU + GPU Stress and Telemetry | **Opt-in.** Loads the board and records clocks, temperature, power and fans throughout. Includes a sustained-performance verdict that compares the first minute with the last. |

### Performance

| #  | Test                                    | Checks                                                                                              |
|----|-----------------------------------------|-----------------------------------------------------------------------------------------------------|
| 42 | Performance Benchmark (CPU / GPU score) | **Opt-in**. Run it from its button. CPU single/multi-thread and GPU FP32 compute, scored against a stock board. Adds a comparison ladder against known systems, which are the Steam Deck, Series S, Steam Machine, PS5 and desktop GPUs. |
| 60 | VKCube (Vulkan on the screen)           | Draws the Vulkan tools' spinning cube (`vkcube`) in a window for five seconds, as the desktop user in the running session. A pass when it is still drawing after that time. An error when it ended by itself, with its output. Skipped without a graphical session, such as a run over SSH, or without `vkcube`. |

See [Performance score](#performance-score-comparing-cu-and-core-unlocks) below.

### Updates

| #  | Test                   | Checks                                                                           |
|----|------------------------|----------------------------------------------------------------------------------|
| 13 | Security Configuration | firewalld zones and SELinux enforcement mode.                                    |
| 32 | OSTree Deployment      | Lists deployments and warns when a newer one is staged and waiting for a reboot. |
| 33 | Update and Patch       | Checks for available rpm-ostree updates and lists Flatpak remotes.               |
| 45 | Installed Packages     | Counts installed software per source. The sources are image RPMs, layered/overridden packages, Flatpak apps, Homebrew, AppImages and Distrobox containers. Names and versions only. |

---

## Performance score: comparing CU and core unlocks

Test 42 runs fixed workloads and scores them against a **baseline**. The baseline is your own board in its stock
configuration, which counts as 100. Stock is 6 cores / 12 threads, 24 CUs and governor max 1850 MHz. A score of
132 means 32% faster than stock.

| Score     | Workload                                                              | Changes with                                |
|-----------|-----------------------------------------------------------------------|---------------------------------------------|
| CPU score | `stress-ng --cpu-method matrixprod`, all threads, bogo ops/s          | Core/thread unlock, mitigations, CPU clock  |
| (CPU 1T)  | Same on one thread, reported in the log and history                   | Mitigations, CPU clock                      |
| GPU score | `vkpeak` FP32 GFLOPS, the best of fp32-scalar / fp32-vec4             | CU unlock, GPU clock / governor maximum     |

FP32 throughput scales with CUs × clock, so it shows exactly what a CU unlock adds. The benchmark also
samples the GPU clock and prints the theoretical peak, which is CUs × 128 × MHz. A result far below it means
unlocked CUs are not doing work, or the clock dropped. vkpeak's `copy-d2d` VRAM bandwidth is recorded
too. It is memory-bound, so it does not change with CUs.

1. Put the board in its stock configuration. Undo any CU unlock and restart, so it has 24 CUs. Close games, check
   **Save as baseline (stock board only)** and run test 42 once. This writes
   `/var/log/bc250-board-test/bench-baseline.json`, the 100 mark for the whole system.
2. Apply an unlock and run test 42 again, without **Save as baseline (stock board only)**. The CPU and GPU score
   boxes at the top show the result. **Benchmark history** compares all runs.

The benchmark needs `stress-ng` (`rpm-ostree install stress-ng`) and `vkpeak`. Get `vkpeak` from its
[releases](https://github.com/nihui/vkpeak/releases) and put the binary in `~/.local/bin`. Keep the
CPU phase length the same between runs you compare.

### Example: 24 → 36 CU unlock

This was measured on a BC-250 in October 2026. The board had 6C/12T, governor max 1850 MHz, mitigations off,
kernel 7.2.7-ogc1.1 and Mesa 26.2.2. The 36-CU run scores **149** on the GPU. The ideal is 150 (36 ÷ 24).

|                              | 24 CU (baseline) | 36 CU          | Change              |
|------------------------------|------------------|----------------|---------------------|
| GPU FP32                     | 5689 GFLOPS      | 8504 GFLOPS    | **+49%**            |
| Share of theoretical maximum | 100%             | 100%           | holds 1850 MHz      |
| VRAM copy                    | 187 GB/s         | 185 GB/s       | same                |
| CPU multi / single (ops/s)   | 6646 / 1094      | 6633 / 1086    | same (within noise) |

* All 36 CUs are active, and the GPU keeps its full clock during the benchmark.
* Memory bandwidth does not grow with the CUs. So games limited by memory bandwidth gain less than the FP32
  figure suggests. Those are games at high resolutions or with large textures. Expect roughly +15–35% FPS in real
  games.
* The CPU is unchanged, because a CU unlock adds GPU units only.
* The benchmark is short. Check the unlock with a long stress test, which is test 41 with a duration of 300 s and
  memtest_vulkan. It shows whether the clock holds when the board is hot and how much power it draws. It also
  shows whether the extra CUs cause VRAM errors.

Stress test at 36 CUs, in runs of 300 s and 600 s with memtest_vulkan + stress-ng on 12 threads:

| Metric                 | Result                                                    |
|------------------------|-----------------------------------------------------------|
| GPU clock under load   | 1850 MHz throughout (at 912 mV)                           |
| GPU busy               | ~90%                                                      |
| GPU power              | 121 W average, 132 W peak                                 |
| Temperatures           | GPU 59 °C max, CPU (Tctl) 71 °C max, fan 2603 RPM max     |
| VRAM errors            | none in about 27,000 memtest_vulkan passes in 10 min, ~374 GB/s |
| Kernel faults          | no GPU hangs, panics, throttling or OOM events            |

The 36-CU unlock is stable under sustained load and runs cool. Both runs show one ~12 s pause at
t≈275 s. That is memtest_vulkan itself, switching from its standard 5-minute test to its endless
test. The gpuload log then says "Standard 5-minute test PASSed!". Test 41 reports that pause as INFO. Any
other stall is a WARNING with the system journal around it.

---

## Diagnosing a hard lockup

A freeze with a continuous screeching tone is a total kernel stall. The sound card keeps replaying
the same DMA buffer because nothing is left running to refill it. That rules out an application
crash and points at the kernel or the SoC itself.

Turn on crash capture first, because a freeze this abrupt never reaches the disk. The suite's
[Persistent Journal](quickfix.md#persistent-journal) quickfix makes the journal folder.

```bash
sudo mkdir -p /var/log/journal && sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo sysctl -w kernel.nmi_watchdog=1
```

Then reproduce it under observation. On the **Stability and thermals** page set **Stress duration** to 300 s
and **Sample interval** to 1 s, and run the stress test (41).

The telemetry line prints to the page's terminal every 10 seconds. So if the board dies, the last values on
screen are its final operating point. Note the `sclk` and `vddgfx` at that moment.

Most likely causes, in order:

1. **Governor ceiling too high.** Many boards hard-lock above roughly 1850 MHz. Lower the maximum in
   `/etc/cyan-skillfish-governor-smu/config.toml`, then run
   `sudo systemctl restart cyan-skillfish-governor-smu` and test again.
2. **Power supply sag.** A marginal 12 V rail browns out the SoC and leaves no log evidence. Suspect
   this if the stress run survives cleanly but games still crash.
3. **Unified memory exhaustion.** CPU and GPU share one 16 GB pool. See test 37.
4. **Missing ACPI fix.** No C-states and no cpufreq scaling. See test 26.

## Useful follow-up commands

```bash
journalctl --list-boots                  # which boots are still retained
journalctl -b -1 -n 50                   # last entries before the previous boot ended
sudo cat /sys/fs/pstore/dmesg-*          # firmware-captured panic, if any
coredumpctl list --since "-14 days"      # crashed applications
watch -n1 cat /sys/class/drm/card0/device/pp_dpm_sclk    # live GPU clock
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target   # turn sleep off
```

## Fix: GPU load shows 0% in the Steam overlay / MangoHud

The stock kernel has no GPU-load sensor for Cyan Skillfish. Reading `gpu_busy_percent` fails, and the
`gpu_metrics` table the overlays read carries no valid load value either. Depending on the tool, the
GPU load then shows as **0%** or as an impossible **655%**. That is the raw `0xFFFF` in that table.

`cyan-skillfish-governor-smu` already measures the real load to drive the clock. With `fix-metrics` on, it also
writes that load into a patched copy of `gpu_metrics`. It bind-mounts that copy over the sysfs file. Then the
Steam performance overlay, MangoHud and radeontop show a real GPU %.

The suite's [Fix GPU Metrics](quickfix.md#fix-gpu-metrics) quickfix turns it on and off, with a backup of
the settings file. By hand, turn it on in `/etc/cyan-skillfish-governor-smu/config.toml`:

```toml
[gpu-usage]
fix-metrics = true
method = "busy-flag"   # "busy-flag", "process" or "kernel"
```

```bash
sudo sed -i 's/^fix-metrics *= *false/fix-metrics = true/' /etc/cyan-skillfish-governor-smu/config.toml
sudo systemctl restart cyan-skillfish-governor-smu
mount | grep gpu_metrics                 # the patched copy should be mounted over the sysfs file
```

Then start a game with the Steam overlay at performance level 3 or higher, and check that the GPU % moves.

Notes:

* `fix-metrics` also turns on the load calculation used by the governor's performance mode.
* Test 40 reports `fix-metrics`, the load method and the clock control method. When `fix-metrics` is on, it also
  checks that the patched `gpu_metrics` is really mounted. When it is off, it gives the hint to turn it on.
* `[gpu] set-method` sets how the governor changes the clock:
    * `smu` talks directly to the SMU, the GPU's power-management firmware. It's the default and the usual
      choice on a stock kernel.
    * `kernel` goes through the amdgpu driver, which a stock driver caps at 2000 MHz. Use it only on a patched
      BC-250 kernel.
* `method` sets how the governor measures load:
    * `busy-flag` samples the GPU's busy bit and is the default.
    * `process` sums per-program GPU time from `/proc/*/fdinfo`. It costs more CPU and can stall on Proton
      games with very many open files.
    * `kernel` only works on patched kernels where `gpu_busy_percent` is readable.
* On some kernels the metrics patching misbehaves. If the overlay or governor acts up after you turn it on,
  set `fix-metrics = false` again and restart the governor.
* Kernels with the BC-250 telemetry fixed in-kernel report the load natively, and `fix-metrics` is not needed
  there. One example is MastaG's linux-cachyos-bc250.
* A newly unlocked CU count or a kernel update can make the overlay drop back to 0%. Reinstalling or
  restarting the governor usually restores it.
* The stress test (41) does not depend on this setting. It measures GPU load itself, from
  `/proc/*/fdinfo`.

Sources: the troubleshooting and GPU governor chapters of the unofficial BC-250 community guide, and the
cyan-skillfish-governor-smu README.

## Requirements

The app never installs anything. It only detects what is already on `PATH`. Layer the optional load tools once,
and every later run picks them up:

```bash
rpm-ostree install stress-ng glmark2
systemctl reboot
```

Or use the optional script shipped with the app. It layers the RPM packages.
It downloads `vkpeak`, `memtest_vulkan` and the Ookla `speedtest` CLI into `~/.local/bin`, and `mprime` into `~/mprime`.
Run without an option, it asks for each group separately.

```bash
./development/tools/install-requirements.sh          # interactive
./development/tools/install-requirements.sh --all    # every group but the development extras, no questions
```

Also recommended is zswap in front of a disk swapfile, instead of Bazzite's zram-only swap. Then memory pressure
does not go straight to the OOM killer, which on the BC-250 can present as a hard freeze. The Btrfs-safe commands
are under *Swap file recommendation* in
[Board Test script](../development/board-test.md#swap-file-recommendation). Tests 14 and 37 check and report the
swap layout.

`vulkan-tools`, which provides `vkcube`, is usually present on Bazzite already. Note that **Flatpak
versions are not detected**. The binary has to be on `PATH`, so layering is the right route here.

| Tool                                 | Used by           | Fallback if missing                                                                 |
|--------------------------------------|-------------------|-------------------------------------------------------------------------------------|
| `stress-ng` or `stress`              | Test 41 CPU load  | Shell busy-loops, one per thread. Still saturates the CPU.                          |
| `stress-ng`                          | Test 42 CPU score | No CPU score (warning).                                                             |
| `vkpeak`                             | Test 42 GPU score | No GPU score (warning).                                                             |
| `memtest_vulkan` or `vkpeak`         | Test 41 GPU load  | vkmark, glmark2 or vkcube, which are much lighter. See below.                       |
| `vkmark`, `glmark2` or `vkcube`      | Test 41 GPU load  | CPU-only stress plus a warning.                                                     |
| `lm_sensors`                         | Test 22           | Falls back to reading hwmon sysfs directly.                                         |
| `vulkan-tools`                       | Tests 20, 21      | Those checks are skipped.                                                           |
| `nvme-cli` or `smartmontools`        | Test 10           | DRAM/HMB guessed from the kernel log, and no SMART health.                          |
| `fio`                                | Test 43           | Random 4K read skipped. Sequential read and write use `dd`.                         |
| Ookla `speedtest` or `speedtest-cli` | Test 44           | Test 44 warns and is skipped. `speedtest-cli` has no loaded latency or packet loss. |

* Preference order for GPU load is memtest_vulkan → vkpeak → vkmark → glmark2 → vkcube.
* **memtest_vulkan is recommended.** It's a headless compute load that keeps the GPU fully busy. It also
  checks the VRAM for errors, and any error found is reported as an ERROR.
* memtest_vulkan isn't packaged. Download the Linux build from
  [its releases](https://github.com/GpuZelenograd/memtest_vulkan/releases). Put the `memtest_vulkan` binary in
  `/usr/local/bin` or `~/.local/bin`. The app also finds it there.
* **User-installed tools never run as root.** The app finds tools in `~/.local/bin` and Homebrew itself
  instead of adding those folders to root's PATH. Anything your user can write to is run as your user, not as
  root. That covers those folders, and any tool not owned by root.
* `fio` needs root to read the raw partition, so a fio from Homebrew or `~/.local/bin` is not used. Install it
  with `rpm-ostree install fio` for the random 4K test.
* memtest_vulkan is limited to ¾ of the VRAM and at most half of the available RAM. Left alone it fills
  all free RAM on this APU, and the OOM killer then kills the desktop (kwin_wayland).
* Memory safety during the stress run:
    * The GPU load tool is the OOM killer's first victim (`oom_score_adj` 1000).
    * The test protects itself, so it can always stop the load.
    * The tool is wrapped in `timeout`, so it never outlives the test.
    * A memory guard stops the run when available RAM drops below 5% (min 512 MiB).
* vkmark and glmark2 render one light frame at a time. On the BC-250 vkmark ran ~2000 FPS in every scene and
  left the GPU only ~20% busy at 1000 MHz. So test 41 will warn that the GPU was never meaningfully loaded.
* As a fallback they run in a 2560x1440 window, and vkmark only runs `effect2d` blur and the `desktop` scene
  with 16 large windows.
* The CPU load runs as `SCHED_IDLE` with `chrt -i 0`, or at `nice 19` without `chrt`. Its autogroup is set to
  nice 19. So it only uses cycles nothing else wants and never slows the GPU load tool or the desktop.
* vkcube is a spinning cube. It'll register, but it won't push the GPU hard enough to be a real stability test.

### Install commands

```bash
sudo rpm-ostree install lm_sensors
systemctl reboot
```

```bash
rpm-ostree install vkmark
systemctl reboot
```

```bash
rpm-ostree install nvme-cli fio      # test 10 SMART/DRAM detection, test 43 random reads
systemctl reboot
```

**INFO: glmark2, vkcube, vulkan-tools and smartctl are already available on Bazzite.**

## Advice to set the VRAM size

The split sets a minimum, not a reservation.
The GPU grows past it dynamically.
512 MB is the RAM-efficient choice, because unused VRAM returns to the regular pool when the game exits.
With an 8 GB split that memory is permanently unavailable even when a game uses 2 GB.
But 512 MB has two documented crash mechanisms.

1. Dynamic ceiling. Linux allows dynamic VRAM up to half the remaining RAM. That gives:

   | Split  | Max total VRAM before the display driver crashes |
   |--------|--------------------------------------------------|
   | 512 MB | 8.25 GB                                          |
   | 4 GB   | 10 GB                                            |
   | 6 GB   | 11 GB                                            |
   | 8 GB   | 12 GB                                            |

   This is fixed with ttm.pages_limit, so it does not need a bigger split.
2. Framebuffer pinning. Scatter-gather display is off on Cyan Skillfish. So every framebuffer the compositor
   displays must be pinned inside the real minimum carve. When a game fills that 512 MB, the next flip can't be
   pinned and the session dies:
   ```bash
   amdgpu: ... pin failed
   Failed to pin framebuffer with error -12
   gamescope: drm: fatal flip error, aborting
   ```
   There is no GPU hang and no OOM-kill, so nothing the tests were looking for. ttm.pages_limit does not help,
   because it only raises the dynamic ceiling. The documented fix is a larger minimum split. A split of 6 GB resolved it
   for the reporter, and it never came back.
   That is the value with a documented fix-report behind it for exactly this failure.
   You can use fanoush/bc250_memcfg, which writes to CMOS. It sets the hidden UMA setting from Linux
   on any BIOS:

   ```bash
   git clone https://github.com/fanoush/bc250_memcfg
   cd bc250_memcfg
   make
   sudo ./bc250memcfg UMA_SIZE 6144
   systemctl reboot
      
   # drop the pages limit if set, not needed when applying this
   rpm-ostree kargs --delete-if-present=ttm.pages_limit
      
   # verify after reboot:
   cat /sys/class/drm/card*/device/mem_info_vram_total   # 6442450944 = 6 GB
   free -h                                               # ~9.4 GB system RAM
   ```

## The stock P5.00 BIOS

The suite advises the latest stock BIOS, P5.00. Software covers the rest, and every step below is reversible.

> **Note.** A custom BIOS is another route to some of these settings. It is not part of the suite.

### Disabling the IOMMU

The IOMMU is broken on the BC-250, and leaving it active creates an unstable system.
A boot parameter tells the kernel to never initialize the AMD IOMMU (AMD-Vi).
That is the standard BC-250 community workaround.

The suite's [IOMMU Off](quickfix.md#iommu-off) quickfix adds it for you, and removes it again. By hand, on
Bazzite (ostree-based):

```bash
rpm-ostree kargs --append=amd_iommu=off
systemctl reboot

# verify after reboot (this is exactly what test 23 checks):
find /sys/kernel/iommu_groups -maxdepth 1 -mindepth 1 -type d | wc -l   # should be 0
```

Nuances:

- `amd_iommu=off` stops the kernel's AMD-Vi driver from initializing. Then there are no IOMMU groups, no DMA
  remapping and no interrupt remapping via IOMMU. From Linux's perspective this is functionally
  equivalent to the BIOS toggle, and it resolves the instability.
- It is *not* a hardware-level disable. The firmware still powers and configures the silicon. But
  nothing programs or uses it, so the broken behavior isn't triggered. In practice BC-250
  users on the stock 5.00 BIOS run stable with this karg.
- `iommu=pt` (passthrough) is a softer alternative but not sufficient here. On the BC-250 you
  want it fully off.
- The downside is no VFIO/PCI passthrough for VMs, which is irrelevant on this board anyway.

Test 23 validates either route the same way. It counts IOMMU groups, so it goes green whether
the IOMMU was disabled in the BIOS or via the kernel argument.

### Optional: ACPI fix

[e-tho/bc250-acpi-fix](https://github.com/e-tho/bc250-acpi-fix) is a pure-software fix. It is the maintained fork
of [bc250-collective/bc250-acpi-fix](https://github.com/bc250-collective/bc250-acpi-fix). It has three SSDT
overrides that are loaded from initrd via the kernel's ACPI table upgrade.

* It needs no flashing.
* It is fully reversible. Delete the file and the GRUB line.
* It works on all stock BIOS versions.
* It covers both stock 6-core and unlocked 8-core setups.

To install it on Bazzite:

```bash
sudo cp acpi_override.cpio /boot/
echo 'GRUB_EARLY_INITRD_LINUX_CUSTOM="../../acpi_override.cpio"' | sudo tee -a /etc/default/grub
ujust regenerate-grub   # then reboot
```

Or use the guided installer from
[acpi](https://github.com/RobertoTorino/bc250-bazzite/tree/main/apps/acpi), a suite app that is installed from
the portal. It bundles the tables, checks the board and its BIOS, installs idempotently and has an
uninstaller. The fix is persistent. The blscfg GRUB module applies the early initrd to every
BLS boot entry, so it survives kernel and rpm-ostree image updates.

Verify with `sudo dmesg | grep -iE 'ACPI.*(SSDT|Table Upgrade)'`, or just run test 26 again.
It reports whether the ACPI tables came from the initrd override or the BIOS.

**For the 2 extra cores without flashing:**
[rw-r-r-0644/bc250-core-unlock](https://github.com/rw-r-r-0644/bc250-core-unlock) unlocks
8C/16T at runtime via the SMU. Caveats:

- It survives warm reboots only. Redo it after every cold boot.
- It refuses boards whose core mask isn't the usual `0x77`. A different mask suggests defective cores.
- Stress-test for MCEs before trusting the new cores. Test 25 checks for machine-check events.
- A known side effect is that `pp_dpm_sclk` reports nonsense clocks afterward. Tests 19/40 would
  flag that.

Or use [BC-250 CPU Tools](https://github.com/RobertoTorino/bc250-bazzite/tree/main/apps/cores), a suite app.
It does its own unlock and also makes it **persistent**:

1. **Test first:** `bc250-cores-bisect.sh` runs a control on the stock cores and unlocks. Then it tests each
   new core on its own and both combined over several rounds. Each round is a verified `stress-ng` run with an
   MCE check, and the test is crash-safe across reboots. The unlock is all-or-nothing, so you want this verdict
   before trusting it.
2. **Make it persistent:** after a clean verdict, run `sudo ./bc250-cores-unlock.sh --install`, or use
   **Install** in its GUI, which is gated on the bisect verdict. It turns on a root service that re-applies the
   unlock after every cold boot and warm-reboots once. It survives reboots, cold boots and Bazzite updates.
3. **Undo:** `sudo ./bc250-cores-unlock.sh --uninstall`, then a full power off. Stock 6C/12T returns.

**For the extra CUs without flashing:**
[BC-250 CU Tools](https://github.com/RobertoTorino/bc250-bazzite/tree/main/apps/compute), a suite app, unlocks
CUs at runtime by writing the GPU's WGP mask registers with `umr`. It keeps a validated unlock across reboots:

1. **Test first:** `bc250-cu-bisect.sh` tests every locked WGP (2 CUs) on its own over several rounds and
   tells bad WGPs apart from an unstable unlock, power or heat. Then test the combined mask again on its own.
2. **Make it persistent:** `bc250-cu-unlock.sh --install <masks>`, or **Install** in its BC Unlock GUI,
   saves the mask and reapplies it at every boot through a root systemd service that starts before the
   desktop. It survives reboots, cold boots and Bazzite updates. The GUI only allows **Install** once the
   bisect results show the combined mask passed every round with the same number of WGPs on all 4 rows.
3. **Undo:** `sudo ./bc250-cu-unlock.sh --uninstall` or **Uninstall** in the GUI, then restart. Stock 24 CUs
   return.

Caveats:

- Keep the 4 shader arrays even, for example 4/4/4/4 WGPs = 32 CUs. The GPU splits work across them in
  lockstep, so an uneven mask uses more power without being faster.
- Check the result here. Test 21 shows the live CU count. Test 41 (stress) and test 42 (benchmark) show
  whether it's stable and what it adds. See [Example: 24 → 36 CU unlock](#example-24--36-cu-unlock).
- A WGP that passed can still fail under other conditions, such as heat or a game. After a hang, uninstall and
  restart, then test again.

With these tools every setting has a software-only, reversible way on the stock BIOS, up to and
including 5.00:

| Setting                            | On the stock BIOS                                          |
|------------------------------------|------------------------------------------------------------|
| UMA/VRAM split                     | `bc250_memcfg`, which writes the CMOS value                |
| ACPI fix (C-states + freq scaling) | `bc250-persistent-acpi`, which works on 1.00–5.00 with the same DSDT |
| IOMMU disable                      | `rpm-ostree kargs --append=amd_iommu=off`                  |
| 8C/16T unlock                      | `bc250-cores-unlock.sh --install`                          |
| Extra CUs                          | `bc250-cu-unlock.sh --install`                             |

Minor caveats, not performance losses:

- Cores: after a cold boot the service re-applies the unlock and does **one extra warm reboot**.
  Power-on is slightly slower, and runtime performance is the same.
- A CMOS reset or battery pull reverts the `bc250_memcfg` split. Just run it again.
- Validate cores and CUs with the bisect tools first. Silicon quality is per board, independent of BIOS.

Going beyond stock: [BC-250 GPU OC Bisect](https://github.com/RobertoTorino/bc250-bazzite/tree/main/apps/oc), a
suite app, sweeps the governor's top GPU safe-point the same bisect way, with the clock up and the voltage down.
It finds the safe overclock or undervolt for your specific board, and no BIOS is involved either.

The stock BIOS is also the safe choice. It has zero bricking risk, and no duplicate-ACPI-table conflicts
with the override.

> **Note** from e-tho's README. A custom BIOS may ship its own ACPI fixes, and duplicate tables fail
> to load. On such a BIOS, remove the ACPI override first.

---

## License

Copyright © 2026 RobertoTorino.

BC-250 Board Test is free software: you can redistribute it and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.html), version 3 or (at your option) any
later version. It is distributed in the hope that it will be useful, but **without any warranty**; without
even the implied warranty of merchantability or fitness for a particular purpose.

The release tarball `bc250-check-v<version>.tar.gz` is the complete source of that release. It is Python and
shell, and nothing is compiled. GitHub also attaches the source of the whole suite at that tag.

Third-party components: Qt 6 (LGPL v3), PyQt6 (GPL v3), the Inter font (SIL Open Font License 1.1).
