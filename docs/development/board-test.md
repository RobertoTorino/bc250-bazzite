<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-clipboard-check-outline:</span>

# Board Test: the script

The Board Test script checks an **AMD BC-250** board running **Bazzite** and writes a report. Bazzite is a Fedora
Atomic system that is updated with rpm-ostree. The BC-250 has a Cyan Skillfish APU, `gfx1013`, with PCI ID
`1002:13fe`.

The script is **read-only**. It installs, turns on, turns off and reconfigures nothing. The opt-in `--stress` mode is
the only exception. It puts the board under load on purpose.

---

## Usage

```bash
sudo chmod +x test-board.sh

sudo ./test-board.sh                        # passive diagnostics only (tests 00-40, 45-53, 60)
sudo ./test-board.sh --stress               # ... plus a 120s CPU+GPU stress run (test 41)
sudo ./test-board.sh --stress=300           # 300s stress run
sudo ./test-board.sh --stress=300 --interval=1   # sample telemetry every second
sudo ./test-board.sh --only=04,05,17            # run only tests 04, 05 and 17
sudo ./test-board.sh --only=42 --bench --save-baseline   # benchmark a STOCK board once (baseline = 100)
sudo ./test-board.sh --only=42 --bench          # benchmark after an unlock: CPU and GPU score vs stock
sudo ./test-board.sh --only=10,43 --disk-bench  # NVMe link/DRAM/health + disk read speed (read-only)
sudo ./test-board.sh --only=43 --disk-write=16  # ... also write 16 GiB to find the SLC cache size
sudo ./test-board.sh --only=44 --speedtest      # internet speed, latency under load, packet loss (~1 GB of data)
sudo ./test-board.sh --help                 # show options
```

| Option               | Description                                                                |
|----------------------|----------------------------------------------------------------------------|
| `--stress[=SECONDS]` | Opt-in. Loads the CPU and the GPU and samples telemetry. The default is 120s, the minimum 10s. |
| `--interval=SECONDS` | How often the stress run samples telemetry. The default is 2s, the minimum 1s. |
| `--bench[=SECONDS]`  | Opt-in performance benchmark (test 42). SECONDS is the length of each CPU phase. The default is 20, the minimum 5. |
| `--save-baseline`    | With `--bench`, saves this run as `/var/log/bc250-board-test/bench-baseline.json`. That run is the 100 mark. |
| `--disk-bench`       | Opt-in disk speed test (test 43). It measures sequential read and random 4K read with `fio`. It is read-only. |
| `--disk-write=GiB`   | Also writes GiB (1–256) to a temporary file in `/var/tmp`. The write measures write speed and the SLC cache size. It implies `--disk-bench`. |
| `--speedtest`        | Opt-in internet speed test (test 44) with Ookla `speedtest` or `speedtest-cli`. It uses about 1 GB of data on a fast line. |
| `--only=LIST`        | Runs only the listed tests, for example `--only=04,05,17`. Test 41 also needs `--stress`. Test 42 needs `--bench`, test 43 needs `--disk-bench` and test 44 needs `--speedtest`. |
| `--no-desktop`       | Does not copy the report to the `Desktop` folder of the desktop user. |
| `--gui`              | Words the hints on how to run a test for the GUI instead of for these options. The GUI uses it. |
| `-h`, `--help`       | Shows the usage and exits.                                                 |

[Board Test internals](board-test-internals.md) describes the GUI for developers. [BC-250 Board Test](../apps/check.md)
describes it for users.

### Output

All files go to `/var/log/bc250-board-test/`:

| File                                         | Contents                                                          |
|----------------------------------------------|-------------------------------------------------------------------|
| `bc250-test-results-<YYYYmmdd-HHMMSS>.log`   | The full report                                                   |
| `bc250-stress-<YYYYmmdd-HHMMSS>.csv`         | Stress telemetry, written only with `--stress`                    |
| `bc250-gpuload-<YYYYmmdd-HHMMSS>.log`        | The output of the GPU load tool, written only with `--stress`     |
| `bc250-memtest-<YYYYmmdd-HHMMSS>.log`        | memtest_vulkan's own log, when it was the GPU load tool          |
| `bc250-bench-<YYYYmmdd-HHMMSS>.json`         | The benchmark result, written only with `--bench`                 |
| `bc250-bench-vkpeak-<YYYYmmdd-HHMMSS>.log`   | The vkpeak output of the benchmark                                |
| `bc250-bench-history.csv`                    | One line per benchmark run, to compare configurations over time   |
| `bc250-disk-<YYYYmmdd-HHMMSS>.csv`           | Write speed and drive temperature per 256 MiB, only with `--disk-write` |
| `bc250-speedtest-<YYYYmmdd-HHMMSS>.json`     | The raw speed test result, only with `--speedtest`                |
| `bc250-speedtest-history.csv`                | One line per speed test, with the columns listed below            |

Each line of `bc250-speedtest-history.csv` holds these values:

- The interface
- The server
- The speeds
- The idle and loaded latency
- The jitter
- The packet loss

At the end of the run the script copies the files to `~/Desktop/bc250-board-test/` of the desktop user. This makes
them easy to share. `--no-desktop` skips the copy. In the GUI, the setting is *Settings > General > Copy the full
reports to ~/Desktop/bc250-board-test after each run*. It is on by default. During a stress run the script flushes the
files to disk after every sample. That way they survive a hard lockup.

The GUI also keeps its own captured output of every run as
`~/.local/share/bc250-board-test/logs/<YYYYmmdd-HHMMSS>_<scope>.log`. These are not the files above. They hold only
what the script printed during that run.

The CSV columns are `elapsed_s, sclk_mhz, mclk_mhz, gpu_busy_pct, vram_used_mib, gtt_used_mib,
gpu_temp_c, gpu_power_w, vddgfx_mv, cpu_tctl_c, cpu_mhz_avg, fan_rpm, load1`. You can open the file directly in
LibreOffice Calc. There you can plot clocks, memory and power against temperature.

`gpu_busy_pct` comes from the kernel's `gpu_busy_percent` when it works. Stock kernels have no GPU-load sensor for
Cyan Skillfish, so the read fails. That is also why MangoHud and the Steam overlay show 0%, unless the governor's
`fix-metrics` is on. The script then measures the time each GPU client spends on the graphics and compute engines.
It reads this from `/proc/*/fdinfo`, the same method nvtop uses. The log says which source the script used.

The summary reports the peak VRAM and GTT use as a percentage of each budget. It warns at these levels:

- 90% VRAM, where allocations spill into GTT
- 85% GTT, where the GPU is close to running out of memory

Every line carries a tag: `SUCCESS`, `INFO`, `WARNING` or `ERROR`. A `[SUMMARY]` block at the end reports the verdict
for the whole run.

---

## Tests

### System

| #  | Test                         | Checks                                                                          |
|----|------------------------------|---------------------------------------------------------------------------------|
| 00 | Platform Identification      | Confirms that the board really is a BC-250. Reports the BIOS (stock or modded), the Bazzite image and the kernel. |
| 01 | Running Services             | Lists every active systemd service.                                             |
| 02 | Failed Units                 | Reports an error for any unit in a failed state.                                |
| 03 | System Uptime                | Reports the uptime and the load average.                                        |
| 11 | Resource Consumption         | Lists the programs that use the most CPU and memory.                            |
| 12 | Boot Time                    | Shows the `systemd-analyze` breakdown and warns on units that take over a minute. |
| 31 | File and Directory Integrity | Checks that `/var/log` exists and lists it.                                     |

### Network

| #  | Test                   | Checks                                                                    |
|----|------------------------|---------------------------------------------------------------------------|
| 04 | Network Connectivity   | Pings an external host.                                                   |
| 05 | DNS Resolution         | Resolves a known host name.                                               |
| 06 | Public Internet Access | Fetches a URL over HTTPS.                                                 |
| 07 | Open Ports             | Lists the listening TCP and UDP sockets.                                  |
| 08 | NTP Synchronization    | Confirms that the clock is synchronized.                                  |
| 30 | SSH Service            | Reports the state of `sshd.service` and `sshd.socket`. Bazzite has SSH off by default. |
| 53 | Wi-Fi Adapter          | Shows every Wi-Fi adapter with its driver, firmware, rfkill state and connection. |
| 44 | Internet Speed         | **Opt-in** (`--speedtest`). See below.                                    |

**How test 44 measures the connection**. It uses Ookla's `speedtest`, or `speedtest-cli` as a fallback. A run takes
about 30 s.

* **Download and upload** in Mbps, plus the data used. That is roughly 1 GB on a gigabit line.
* **Idle latency and jitter**, and the **latency while downloading/uploading**. The loaded latency can be more than
  100 ms above idle. Then the line suffers from *bufferbloat*, and games lag whenever something else uses the
  connection. The fix is SQM in the router, with fq_codel or CAKE. Only Ookla's CLI measures loaded latency.
* **Packet loss**, measured by Ookla only. Over 1% is a warning.
* **The local link**. This is the interface the traffic uses, Ethernet or Wi-Fi, and its link speed. A 10/100 Mbit/s
  Ethernet link is a warning, because it points to a bad or 2-pair cable. A download near the link speed means that
  the port is the limit.
* A VPN in the path is noted. With a VPN the test measures the VPN, not the line.
* Every run is appended to `bc250-speedtest-history.csv`. The GUI's **Show graph** compares all runs.
* To install Ookla's CLI, download the Linux x86_64 `.tgz` from <https://www.speedtest.net/apps/cli>. Put the
  `speedtest` binary in `~/.local/bin`. When you run it, you accept Ookla's license and GDPR terms.

Test 53 runs `bc250_core.wifi` with the system `python3 -I -B`. That uses the standard library only and writes no
bytecode as root. The module comes from the `bc250_core` bundled next to the script, or from `core/` in the suite
checkout. It reads these sources:

- `/sys`
- The running kernel's `modules.dep` and `modules.alias`
- This boot's kernel log
- `iw dev <interface> link`

It prints its findings as `LEVEL: text` lines, and the script logs them. A `WARNING` line counts as a warning.

### Storage and memory

| #  | Test                             | Checks                                                                                 |
|----|----------------------------------|----------------------------------------------------------------------------------------|
| 09 | Disk Configuration               | Shows the file system usage and the mount points.                                      |
| 10 | NVMe Devices                     | Detects the drives. Compares the PCIe link speed and width with what the drive and the slot support. Shows the DRAM cache, or the host memory buffer of a DRAM-less drive. Reports the SMART health. That covers wear, media errors, spare, temperature, time spent throttling and unsafe shutdowns. |
| 14 | Memory and Swap                  | Shows the RAM usage and the full swap layout. That covers zram, zswap, disk swap, overlaps and swappiness. |
| 37 | Unified Memory and VRAM Pressure | Shows the VRAM and GTT usage, the OOM-kill history, `vm.max_map_count` and swappiness. |
| 49 | CPU Memory Bandwidth             | Measures the memory bandwidth with a STREAM-like `stress-ng` test, on 1 thread and on all threads. It shows the GDDR6 latency cost the CPU pays for the GPU's console-class bandwidth. |
| 43 | Disk Speed (read, write, SLC cache) | **Opt-in** (`--disk-bench`, `--disk-write=GiB`). See below.                         |

**How test 43 measures the system disk**. The system disk is the disk that holds `/var/tmp`.

* **Sequential read**. `dd` reads 4 GiB straight from the partition with direct I/O. Nothing is written. The result
  is compared with the PCIe link ceiling from test 10.
* **Random 4K read** at queue depth 1 and 32. `fio --readonly` reads over the whole partition, 10 s each. This part
  is skipped without a system-wide `fio`, because a Homebrew fio is not run as root. A QD1 latency over ~150 µs is
  typical of a DRAM-less drive without a host memory buffer.
* **Sequential write and SLC cache**, only with `--disk-write=GiB`:
  * The test writes a temporary file in `/var/tmp` in 256 MiB chunks, with direct I/O and flushed. It deletes the
    file afterward. It creates the file with `chattr +C`, so btrfs doesn't compress it. Compression would fake the
    result.
  * The speed of each chunk and the drive temperature go to `bc250-disk-<timestamp>.csv`. **Show graph** in the GUI
    plots it.
  * The point where the speed falls below 60% of the starting speed is reported as the SLC cache size. The drive may
    be at its warning temperature at that moment. Then the test reports thermal throttling instead.
  * Pick a size larger than the expected cache. That is a few GiB on cheap or QLC drives, and tens of GiB on large
    TLC drives. The test needs that size plus 5 GiB free. The run stops early if the drive reaches its critical
    temperature.

**DRAM cache detection (test 10)**:

* No drive reports "has DRAM" directly.
* DRAM-less NVMe drives ask the host for a *Host Memory Buffer*. That is the `HMPRE` field of `nvme id-ctrl`. The
  kernel logs it as `allocated N MiB host memory buffer`.
* The test reads both. If neither is present, the drive has its own DRAM.
* On the BC-250 the HMB comes out of the RAM that the CPU shares with the GPU. It is usually 32–64 MiB.

### System logs

| #  | Test           | Checks                                                                   |
|----|----------------|--------------------------------------------------------------------------|
| 15 | Boot Logs      | Shows the kernel errors of the current boot. Known harmless BC-250 noise is filtered out. |
| 16 | System Journal | Shows the journal errors of the last 7 days, with the same filter.       |

### GPU and graphics

| #  | Test                  | Checks                                                                     |
|----|-----------------------|----------------------------------------------------------------------------|
| 17 | amdgpu Driver         | Confirms that `amdgpu` is bound to the Cyan Skillfish APU.                 |
| 18 | GPU Governor          | Checks that a governor is running. Without one, the GPU is pinned at 1500 MHz. |
| 19 | GPU Frequency Scaling | Reads `pp_dpm_sclk` and `pp_dpm_mclk` to confirm that the clock really moves. |
| 20 | Vulkan / Mesa         | Confirms that RADV reports GFX1013 and not the llvmpipe software fallback. |
| 21 | Compute Unit Count    | Reads the active CUs from the live GPU registers. That needs admin rights and umr. Otherwise, it shows the kernel value. That is 24 stock and up to 40 unlocked. It explains why the kernel and RADV keep reporting the value from driver probe. |
| 29 | Display Session, DisplayPort and HDMI | Identifies the display manager, the session type and the compositor. Shows the connector status. |
| 47 | Vulkan Futureproof Matrix | Shows the Vulkan API level and the features modern games need. These are ray tracing, mesh shaders, VRS and pipeline libraries. Compares the VRAM carveout with today's recommendation of 8 GiB. |
| 50 | Video Decode and Encode (VCN) | Shows the `vainfo` codec matrix for H.264, HEVC, VP9 and AV1 decode and encode. |
| 51 | HDMI-CEC | Shows the CEC adapter of the DisplayPort output and whether the TV answers a poll. Shows Bazzite's CEC mode. |
| 52 | HDMI-CEC Services | Shows whether `cecd`, `bc250-hdmi-cec-watch` and `bc250-hdmi-cec-boot` run. Also covers Bazzite's dGPU CEC services. |

### CPU and firmware

| #  | Test                      | Checks                                                                          |
|----|---------------------------|---------------------------------------------------------------------------------|
| 23 | IOMMU Disabled            | Counts the IOMMU groups. IOMMU is broken on the BC-250 and must be off. Turn it off in the BIOS or with the `amd_iommu=off` kernel argument. |
| 24 | CPU Mitigations           | Passes when `mitigations=off` is set. That is worth roughly +18 FPS on this board. |
| 25 | CPU Core and Thread Count | Reports the cores and threads. That is 6C/12T stock and 8C/16T after the core unlock. |
| 26 | CPU Power Management      | Checks cpufreq scaling and C-states. Both need the BC-250 ACPI fix.             |
| 46 | CPU Voltage               | Reads the CPU and SoC voltage rails from hwmon, such as amdgpu's `vddgfx` and `vddnb`. Shows the voltage each core requests now, one line per core. That is the P-state VID, read through the MSR. |

### Stability and thermals

| #  | Test                          | Checks                                                                        |
|----|-------------------------------|-------------------------------------------------------------------------------|
| 22 | Hardware Sensors              | Reads the nct6683/nct6687 SuperIO, the GPU and CPU temperatures and the CPU and GPU rails. Checks that the fan RPM makes sense. |
| 27 | Handheld Daemon               | Confirms that `hhd.service` is masked. It causes constant micro-stuttering.   |
| 28 | Suspend Targets               | Shows which sleep the board offers (suspend-to-idle) and whether systemd may use it. Counts the suspends since boot. |
| 40 | Power Delivery and Throttling | Shows the GPU power cap and draw, the governor's frequency ceiling and throttle messages. |

### Crash forensics

| #  | Test                                | Checks                                                                                      |
|----|-------------------------------------|---------------------------------------------------------------------------------------------|
| 34 | Previous Boot Shutdown Integrity    | Flags previous boots that ended with no shutdown sequence. That is the signature of a hard lockup. |
| 35 | GPU Hang and Reset History          | Finds ring timeouts, GPU resets, VM faults and soft recoveries in every retained boot.      |
| 36 | Kernel Panic, Lockup and Crash Dump | Finds oopses, soft and hard lockups, call traces and `coredumpctl` records. Shows the NMI watchdog state. |

### Gaming

| #  | Test                           | Checks                                                                                  |
|----|--------------------------------|-----------------------------------------------------------------------------------------|
| 38 | Steam and Gaming Stack         | Checks Steam, gamescope, gamemode, MangoHud and umu. Shows the library paths and their free space. |
| 39 | Audio Stack                    | Shows the state of PipeWire and WirePlumber, the default sink and the ALSA cards.       |
| 48 | Real-Game Frametime (MangoHud logs) | Reads the latest MangoHud logs from real play sessions. Shows the average FPS, the 1% and 0.1% lows and the share of stutter. |
| 41 | CPU + GPU Stress and Telemetry | **Opt-in.** Loads the board and records clocks, temperature, power and fans all the way through. Gives a verdict on sustained performance, comparing the first minute with the last minute. |

### Performance

| #  | Test                                    | Checks                                                                                              |
|----|-----------------------------------------|-----------------------------------------------------------------------------------------------------|
| 42 | Performance Benchmark (CPU / GPU score) | **Opt-in** (`--bench`). Scores CPU single-thread, CPU multi-thread and GPU FP32 compute against a stock board. Adds a ladder that compares the board with known systems: Steam Deck, Series S, Steam Machine, PS5 and desktop GPUs. |
| 60 | VKCube (Vulkan on the screen)           | Draws the spinning cube of the Vulkan tools (`vkcube`) in a window for five seconds. It runs as the desktop user in the running session. It passes when the cube still draws after that time. It reports an error, with the output, when the cube ended by itself. It is skipped without a graphical session, such as a run over SSH, or without `vkcube`. |

See [Performance score](#performance-score-comparing-cu-and-core-unlocks) below.

### Updates

| #  | Test                   | Checks                                                                           |
|----|------------------------|----------------------------------------------------------------------------------|
| 13 | Security Configuration | Shows the firewalld zones and the SELinux enforcement mode.                      |
| 32 | OSTree Deployment      | Lists the deployments. Warns when a newer one is staged and waits for a restart. |
| 33 | Update and Patch       | Checks for available rpm-ostree updates and lists the Flatpak remotes.           |
| 45 | Installed Packages     | Counts the installed software per source. It shows names and versions only.      |

Test 45 counts these sources:

- Image RPMs
- Layered or overridden packages
- Flatpak apps
- Homebrew
- AppImages
- Distrobox containers

---

## Performance score: comparing CU and core unlocks

Test 42 shows how much faster an unlock makes your board. It runs fixed workloads and scores them against a
**baseline**, which is your own board in its stock configuration. The stock configuration is 6 cores / 12 threads, 24 CUs and
a governor maximum of 1850 MHz. The baseline scores 100. A score of 132 means 32% faster than stock.

| Score     | Workload                                                              | Changes with                                |
|-----------|-----------------------------------------------------------------------|---------------------------------------------|
| CPU score | `stress-ng --cpu-method matrixprod`, all threads, bogo ops/s          | Core/thread unlock, mitigations, CPU clock  |
| (CPU 1T)  | The same on one thread, reported in the log and the history           | Mitigations, CPU clock                      |
| GPU score | `vkpeak` FP32 GFLOPS, the best of fp32-scalar and fp32-vec4           | CU unlock, GPU clock / governor maximum     |

FP32 throughput scales with CUs × clock, so it shows exactly what a CU unlock adds. The benchmark also samples the
GPU clock and prints the theoretical peak. The peak is CUs × 128 × MHz. A result far below it means that the unlocked CUs do
no work, or that the clock dropped. The benchmark also records vkpeak's `copy-d2d` VRAM bandwidth. That number is
bound by memory, so it does not change with the CUs.

1. Put the board in its stock configuration and close your games. Undo any CU unlock and restart, so the board has
   24 CUs. Then run `sudo ./test-board.sh --only=42 --bench --save-baseline`. In the GUI, check *Save as baseline
   (stock board only)* instead. This writes `/var/log/bc250-board-test/bench-baseline.json`. Every copy of the script
   and the GUI share this one baseline. An older version saved the baseline next to the script. The next `--bench`
   run moves that file there.
2. Apply an unlock, then run `sudo ./test-board.sh --only=42 --bench`. Compare the results in
   `/var/log/bc250-board-test/bc250-bench-history.csv` or in the GUI's *Benchmark history*.

The benchmark needs `stress-ng` (`rpm-ostree install stress-ng`) and `vkpeak`. Get vkpeak from its
[releases](https://github.com/nihui/vkpeak/releases) and put the binary in `~/.local/bin`. Keep the CPU phase length
the same between the runs you compare.

### Example: 24 → 36 CU unlock

This run was measured on a BC-250 in October 2026. The board had 6C/12T, a governor maximum of 1850 MHz and
mitigations off. It ran kernel 7.2.7-ogc1.1 and Mesa 26.2.2. The 36-CU run scores **149** on the GPU. The ideal is
150 (36 ÷ 24).

|                              | 24 CU (baseline) | 36 CU          | Change              |
|------------------------------|------------------|----------------|---------------------|
| GPU FP32                     | 5689 GFLOPS      | 8504 GFLOPS    | **+49%**            |
| Share of theoretical maximum | 100%             | 100%           | holds 1850 MHz      |
| VRAM copy                    | 187 GB/s         | 185 GB/s       | same                |
| CPU multi / single (ops/s)   | 6646 / 1094      | 6633 / 1086    | same (within noise) |

* All 36 CUs are active. The GPU keeps its full clock during the benchmark.
* Memory bandwidth does not grow with the CUs. Games that are limited by memory bandwidth gain less than the FP32
  figure suggests. High resolutions and large textures are such cases. Expect roughly +15–35% FPS in real games.
* The CPU is unchanged. A CU unlock adds GPU units only.
* The benchmark is short. Check the unlock with a long stress test: `--only=41 --stress=300` with memtest_vulkan. It
  shows these things:
  * Whether the clock holds when the board is hot
  * How much power the board draws
  * Whether the extra CUs cause VRAM errors

This is the stress test at 36 CUs. It ran for 300 s and 600 s, with memtest_vulkan and stress-ng on 12 threads.

| Metric                 | Result                                                    |
|------------------------|-----------------------------------------------------------|
| GPU clock under load   | 1850 MHz throughout (at 912 mV)                           |
| GPU busy               | ~90%                                                      |
| GPU power              | 121 W average, 132 W peak                                 |
| Temperatures           | GPU 59 °C max, CPU (Tctl) 71 °C max, fan 2603 RPM max     |
| VRAM errors            | none, about 27,000 memtest_vulkan passes in 10 min at ~374 GB/s |
| Kernel faults          | no GPU hangs, panics, throttling or OOM events            |

The 36-CU unlock is stable under sustained load and runs cool. Both runs show one pause of ~12 s at t≈275 s. That
pause is memtest_vulkan itself. It switches from its standard 5-minute test to its endless test. The gpuload log
shows "Standard 5-minute test PASSed!" at that point. Test 41 reports that pause as INFO. Any other stall is a
WARNING, with the system journal around it.

---

## Diagnosing a hard lockup

A freeze with a continuous screeching tone is a total kernel stall. The sound card keeps replaying the same DMA
buffer, because nothing is left running to refill it. That rules out an application crash. It points at the kernel
or at the SoC itself.

First turn on crash capture, because a freeze this abrupt never reaches the disk:

```bash
sudo mkdir -p /var/log/journal && sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo sysctl -w kernel.nmi_watchdog=1
```

Then reproduce the freeze while the script watches:

```bash
sudo ./test-board.sh --stress=300 --interval=1
```

The script prints the telemetry line to the terminal every 10 seconds. If the board dies, the last values on the
screen are its final operating point. Note the `sclk` and `vddgfx` at that moment.

These are the most likely causes, in order:

1. **Governor ceiling too high.** Many boards hard-lock above roughly 1850 MHz. Lower the maximum in
   `/etc/cyan-skillfish-governor-smu/config.toml`. Then run `sudo systemctl restart cyan-skillfish-governor-smu` and
   test again.
2. **Power supply sag.** A marginal 12 V rail browns out the SoC and leaves no evidence in the log. Suspect this when
   the stress run survives cleanly but games still crash.
3. **Unified memory exhaustion.** The CPU and the GPU share one 16 GB pool. See test 37.
4. **Missing ACPI fix.** The board has no C-states and no cpufreq scaling. See test 26.

## Useful follow-up commands

```bash
journalctl --list-boots                  # which boots are still retained
journalctl -b -1 -n 50                   # last entries before the previous boot ended
sudo cat /sys/fs/pstore/dmesg-*          # firmware-captured panic, if any
coredumpctl list --since "-14 days"      # crashed applications
watch -n1 cat /sys/class/drm/card0/device/pp_dpm_sclk    # live GPU clock
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

## Fix: GPU load shows 0% in the Steam overlay / MangoHud

The stock kernel has no GPU-load sensor for Cyan Skillfish. Reading `gpu_busy_percent` fails. The `gpu_metrics`
table that the overlays read carries no valid load value either. Depending on the tool, the GPU load then shows as
**0%** or as an impossible **655%**. The 655% is the raw `0xFFFF` in that table.

`cyan-skillfish-governor-smu` already measures the real load to drive the clock. With `fix-metrics` on, it also
writes that load into a patched copy of `gpu_metrics`. It bind-mounts that copy over the sysfs file. The Steam
performance overlay, MangoHud and radeontop then show a real GPU %.

Turn it on in `/etc/cyan-skillfish-governor-smu/config.toml`:

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

Then start a game with the Steam overlay at performance level 3 or higher. Check that the GPU % moves.

Notes:

* `fix-metrics` also turns on the load calculation that the governor's performance mode uses.
* Test 40 reports `fix-metrics`, the load method and the clock control method. When `fix-metrics` is on, it also
  checks that the patched `gpu_metrics` is really mounted. When it is off, the test gives the hint to turn it on.
* `[gpu] set-method` sets how the governor changes the clock:
  * `smu` talks to the SMU directly. The SMU is the GPU's power-management firmware. `smu` is the default and the
    usual choice on a stock kernel.
  * `kernel` goes through the amdgpu driver, which a stock driver caps at 2000 MHz. Use it only on a patched
    BC-250 kernel.
* `method` sets how the governor measures load:
  * `busy-flag` samples the GPU's busy bit. It is the default.
  * `process` sums the GPU time of each program from `/proc/*/fdinfo`. It costs more CPU. It can stall on Proton
    games with very many open files.
  * `kernel` only works on patched kernels where `gpu_busy_percent` is readable.
* On some kernels the metrics patching misbehaves. If the overlay or the governor acts up after you turn it on, set
  `fix-metrics = false` again and restart the governor.
* Some kernels have the BC-250 telemetry fixed in the kernel, for example MastaG's linux-cachyos-bc250. They report
  the load natively, and `fix-metrics` is not needed there.
* A newly unlocked CU count or a kernel update can make the overlay drop back to 0%. Reinstalling or restarting the
  governor usually restores it.
* The stress test (41) does not depend on this setting. It measures the GPU load itself, from `/proc/*/fdinfo`.

Source: the unofficial BC-250 community guide, with its troubleshooting and GPU governor chapters, and the
cyan-skillfish-governor-smu README.

## Requirements

The script runs as root on Bazzite. It never installs anything. It only detects what is already on `PATH`. Layer the
optional load tools once, and every later run picks them up automatically:

```bash
rpm-ostree install stress-ng glmark2
systemctl reboot
```

Or use the optional script, which installs everything below in one go. It layers the RPM packages `stress-ng`,
`lm_sensors`, `vkmark`, `nvme-cli` and `fio`. It downloads `vkpeak`, `memtest_vulkan` and the Ookla `speedtest` CLI
into `~/.local/bin`. It is interactive and asks for each group separately.

```bash
./development/tools/install-requirements.sh          # interactive
./development/tools/install-requirements.sh --all    # everything, no questions
```

`vulkan-tools`, which provides `vkcube`, is usually on Bazzite already. Note that **Flatpak versions are not
detected**. The binary has to be on `PATH`, so layering is the right route here.

| Tool                                 | Used by           | Fallback if missing                                                                 |
|--------------------------------------|-------------------|-------------------------------------------------------------------------------------|
| `stress-ng` or `stress`              | Test 41 CPU load  | Shell busy-loops, one per thread. They still saturate the CPU.                      |
| `stress-ng`                          | Test 42 CPU score | No CPU score, with a warning                                                        |
| `vkpeak`                             | Test 42 GPU score | No GPU score, with a warning                                                        |
| `memtest_vulkan` or `vkpeak`         | Test 41 GPU load  | vkmark, glmark2 or vkcube, which are much lighter. See below.                       |
| `vkmark`, `glmark2` or `vkcube`      | Test 41 GPU load  | A stress run on the CPU only, plus a warning                                        |
| `lm_sensors`                         | Test 22           | The test reads hwmon sysfs directly.                                                |
| `vulkan-tools`                       | Tests 20, 21      | Those checks are skipped.                                                           |
| `nvme-cli` or `smartmontools`        | Test 10           | DRAM/HMB is guessed from the kernel log. There is no SMART health.                  |
| `fio`                                | Test 43           | Random 4K read is skipped. Sequential read and write use `dd`.                      |
| Ookla `speedtest` or `speedtest-cli` | Test 44           | Test 44 warns and is skipped. `speedtest-cli` has no loaded latency or packet loss. |

* The order of preference for the GPU load is memtest_vulkan → vkpeak → vkmark → glmark2 → vkcube.
* **memtest_vulkan is recommended.** It's a headless compute load that keeps the GPU fully busy. It also checks the
  VRAM for errors, and the test reports any error it finds as an ERROR. It isn't packaged. Download the Linux build
  from [its releases](https://github.com/GpuZelenograd/memtest_vulkan/releases). Put the `memtest_vulkan` binary in
  `/usr/local/bin` or `~/.local/bin`. The script also looks there under sudo.
* **User-installed tools never run as root.** The script finds tools in `~/.local/bin` and Homebrew itself. It does
  not add those folders to root's PATH. Anything your user can write to runs as your user, not as root. That covers
  those folders and any tool that root does not own. `fio` needs root to read the raw partition. So the script does
  not use a fio from Homebrew or `~/.local/bin`. Install it with `rpm-ostree install fio` for the random 4K test.
* memtest_vulkan is limited to ¾ of the VRAM and at most half of the available RAM. Left alone it fills all free RAM
  on this APU. The OOM killer then kills the desktop (kwin_wayland).
* The stress run keeps the memory safe in these ways:
  * The GPU load tool is the OOM killer's first victim (`oom_score_adj` 1000).
  * The script protects itself, so it can always stop the load.
  * The tool is wrapped in `timeout`, so it never outlives the script.
  * A memory guard stops the run when the available RAM drops below 5% (min 512 MiB).
* vkmark and glmark2 render one light frame at a time. On the BC-250 vkmark ran ~2000 FPS in every scene. It left
  the GPU only ~20% busy at 1000 MHz. Test 41 then warns that the GPU was never meaningfully loaded. As a fallback
  they run in a 2560x1440 window. vkmark then runs only the `effect2d` blur and the `desktop` scene with 16 large
  windows.
* The CPU load runs as `SCHED_IDLE` (`chrt -i 0`), or with `nice 19` without `chrt`. Its autogroup is set to nice 19.
  So it only uses cycles that nothing else wants. It never slows the GPU load tool or the desktop.
* vkcube is a spinning cube. It registers as a load, but it doesn't push the GPU hard enough to be a real stability
  test.

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

**INFO: glmark2, vkcube and vulkan-tools are already available on Bazzite.**

## Swap file recommendation

Bazzite ships with **zram as the only swap**. zram is compressed RAM. When it fills there is no overflow to disk, and
the OOM killer runs. On the BC-250, with its unified memory, that can look like a hard freeze of the whole desktop.
Test 14 warns about this layout. Test 37 watches the memory pressure that results.

The recommended layout is **zswap in front of a disk swapfile**, with zram off. It is also the default of the System
score. zswap keeps a compressed cache in RAM like zram does. But when it fills, it writes the oldest pages to the
swapfile instead of ending in the OOM killer. That is much more stable for gaming. zram with a swapfile as a backstop
works too, but scores less. zram alone scores lowest. On Bazzite's Btrfs root a swapfile must be created NOCOW and
uncompressed. The kernel refuses it otherwise.

```bash
sudo mkdir -p /var/swap
sudo btrfs filesystem mkswapfile --size 8g /var/swap/swapfile
sudo swapon /var/swap/swapfile
echo '/var/swap/swapfile none swap defaults 0 0' | sudo tee -a /etc/fstab
# Disable zram (an empty config overrides the default) and enable zswap, then reboot:
sudo touch /etc/systemd/zram-generator.conf
rpm-ostree kargs --append-if-missing=zswap.enabled=1
```

Check the result with `swapon --show`. It shows only the swapfile and no zram. Also check
`cat /sys/module/zswap/parameters/enabled`, which shows `Y`. 8 GiB is a good size for the 16 GB board. Halve it for a
lighter setup. Do not put a swapfile on an SD card or USB stick. Do not run zswap next to zram either. Test 14 warns
about that, because compressing pages twice wastes CPU and memory.

## Advice to set the VRAM size

The split sets a minimum, not a reservation.
The GPU grows past it dynamically.
512 MB is genuinely the RAM-efficient choice, because unused VRAM returns to the regular pool when the game exits.
With an 8 GB split that memory is permanently unavailable even when a game uses 2 GB.
But 512 MB has two documented crash mechanisms.

1. Dynamic ceiling. Linux allows dynamic VRAM up to half the remaining RAM. That gives these limits:

   | Split  | Max total VRAM before the display driver crashes |
   |--------|--------------------------------------------------|
   | 512 MB | 8.25 GB                                          |
   | 4 GB   | 10 GB                                            |
   | 6 GB   | 11 GB                                            |
   | 8 GB   | 12 GB                                            |

   ttm.pages_limit fixes this one. We don't need a bigger split for it.
2. Framebuffer pinning. Scatter-gather display is off on Cyan Skillfish. So every framebuffer the compositor displays
   must be pinned inside the real minimum carve. When a game fills that 512 MB, the next flip can't be pinned. The
   session then dies with these lines:
   ```bash
   amdgpu: ... pin failed
   Failed to pin framebuffer with error -12
   gamescope: drm: fatal flip error, aborting
   ```
   There is no GPU hang and no OOM kill, so nothing the script was looking for. ttm.pages_limit does not help,
   because it only raises the dynamic ceiling. The documented fix is a larger minimum split. 6 GB resolved it for
   the reporter, and the crash never recurred.
   This value of 6 GB has a documented fix report behind it for exactly this failure.
   We can use fanoush/bc250_memcfg, which writes the split to CMOS from Linux, on the stock BIOS.
   The setup menu hides that UMA setting, and bc250_memcfg sets the same CMOS value:

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

## Optional: ACPI fix on the stock BIOS

[e-tho/bc250-acpi-fix](https://github.com/e-tho/bc250-acpi-fix) is a pure-software ACPI fix. It is the maintained
fork of [bc250-collective/bc250-acpi-fix](https://github.com/bc250-collective/bc250-acpi-fix). It loads 3 SSDT
overrides from the initrd through the kernel's ACPI table upgrade. It has these properties:

- It needs no flashing.
- It is fully reversible. Delete the file and the GRUB line.
- It works on all stock BIOS versions.
- It covers both stock 6-core and unlocked 8-core setups.

To install it on Bazzite:

```bash
sudo cp acpi_override.cpio /boot/
echo 'GRUB_EARLY_INITRD_LINUX_CUSTOM="../../acpi_override.cpio"' | sudo tee -a /etc/default/grub
ujust regenerate-grub   # then reboot
```

Or use the guided installer from [acpi](../apps/acpi.md), a suite app. It bundles the tables and checks for a BC-250
and a modded BIOS. It installs idempotently and has an uninstaller. The fix is persistent. The blscfg GRUB module
applies the early initrd to every BLS boot entry. So the fix survives kernel and rpm-ostree image updates.

Check the result with `sudo dmesg | grep -iE 'ACPI.*(SSDT|Table Upgrade)'`. Or just run the test script again. Test 26
reports whether the ACPI tables came from the initrd override or from the BIOS.

**For the 2 extra cores without flashing:**
[rw-r-r-0644/bc250-core-unlock](https://github.com/rw-r-r-0644/bc250-core-unlock) unlocks 8C/16T at runtime through
the SMU. Keep these caveats in mind:

- It survives warm restarts only. Redo it after every cold boot.
- It refuses boards whose core mask isn't the usual `0x77`. A different mask suggests cores that are really defective.
- Stress-test for MCEs before you trust the new cores. Test 25 checks for machine-check events.
- A known side effect is that `pp_dpm_sclk` reports nonsense clocks afterward. Tests 19/40 would flag that.

**For the extra CUs without flashing:**
[BC-250 CU Tools](../apps/compute.md), a suite app, unlocks CUs at runtime. It writes the GPU's WGP mask registers
with `umr`. It keeps a validated unlock across restarts.

1. **Test first:** `bc250-cu-bisect.sh` tests every locked WGP (2 CUs) on its own over several rounds. It tells bad
   WGPs apart from an unstable unlock, power or heat. Then test the combined mask on its own again.
2. **Make it persistent:** `bc250-cu-unlock.sh --install <masks>`, or **Install** in BC-250 CU Tools, saves the mask.
   A root systemd service then applies it again at every boot, before the desktop starts. The unlock survives
   restarts, cold boots and Bazzite updates. CU Tools offers **Install** only after the bisect results show that
   the combined mask passed every round. The mask must also have the same number of WGPs on all 4 rows.
3. **Undo:** run `sudo ./bc250-cu-unlock.sh --uninstall` or click **Uninstall** in CU Tools. Then restart. The board
   is back at stock 24 CUs.

Keep these caveats in mind:

- Keep the 4 shader arrays even, for example 4/4/4/4 WGPs = 32 CUs. The GPU splits work across them in lockstep. An
  uneven mask uses more power without being faster.
- Check the result here. Test 21 shows the live CU count. Test 41 (stress) and test 42 (benchmark) show whether the
  unlock is stable and what it adds. See [Example: 24 → 36 CU unlock](#example-24--36-cu-unlock).
- A WGP that passed can still fail under other conditions, such as heat or a game. After a hang, remove the unlock
  and restart. Then test again.

[BC-250 CPU Tools](../apps/cores.md) keeps a validated core unlock across restarts with its boot service. CU Tools
does the same for the CUs. Both work on the stock BIOS. The suite advises the latest stock P5.00 BIOS and offers no
BIOS flashing.

## Optional: bad CUs or an unstable unlock?

Every BC-250 die differs, because AMD fuses off the WGPs that failed validation. But a crash after a CU unlock
doesn't have to mean a bad WGP. The runtime unlock itself, power or heat can cause it too.
[bc250-cu-bisect](../apps/compute.md) separates these causes. It does its own unlock with umr. It tests a control run
with the same register writes and no extra CUs. It tests every locked WGP on its own over several rounds. It then
tells you for each WGP which of these holds:

- It's good.
- It fails every time, so it is likely bad.
- It fails at random, so the cause is likely the unlock, power or heat.

Once a mask passes, `bc250-cu-unlock.sh` or BC-250 CU Tools keeps it across restarts. See *For the extra CUs without
flashing* above.
