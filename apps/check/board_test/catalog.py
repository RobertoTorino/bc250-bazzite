# SPDX-License-Identifier: GPL-3.0-or-later
"""Test catalog, grouped the same way as the categories in the manual."""

from __future__ import annotations

from dataclasses import dataclass, field

STRESS_TEST_ID = "41"
BENCH_TEST_ID = "42"
DISK_TEST_ID = "43"
SPEEDTEST_TEST_ID = "44"


@dataclass(frozen=True)
class TestDef:
    id: str
    name: str
    checks: str


@dataclass(frozen=True)
class Category:
    key: str
    title: str
    tests: list[TestDef] = field(default_factory=list)

    @property
    def test_ids(self) -> list[str]:
        return [t.id for t in self.tests]


CATEGORIES: list[Category] = [
    Category("system", "System", [
        TestDef("00", "Platform Identification",
                "Confirms the board really is a BC-250 and reports the BIOS, the Bazzite image and the kernel. "
                "It says whether the BIOS is stock or modded. The latest stock 5.00 scores a pass. "
                "An older stock BIOS gets a warning with an update hint."),
        TestDef("01", "Running Services", "Lists every active systemd service."),
        TestDef("02", "Failed Units", "Errors on any unit in a failed state."),
        TestDef("03", "System Uptime", "Reports uptime and load average."),
        TestDef("11", "Resource Consumption", "Top CPU and memory consumers."),
        TestDef("12", "Boot Time", "systemd-analyze breakdown, warns on units taking over a minute."),
        TestDef("31", "File and Directory Integrity", "Lists /var/log and verifies that it exists."),
    ]),
    Category("network", "Network", [
        TestDef("04", "Network Connectivity", "Pings an external host."),
        TestDef("05", "DNS Resolution", "Resolves a known hostname."),
        TestDef("06", "Public Internet Access", "Fetches a URL over HTTPS."),
        TestDef("07", "Open Ports", "Lists listening TCP/UDP sockets."),
        TestDef("08", "NTP Synchronization", "Confirms the clock is synchronized."),
        TestDef("30", "SSH Service", "Reports sshd.service / sshd.socket state. SSH is off by default on Bazzite."),
        TestDef("53", "Wi-Fi Adapter",
                "Every Wi-Fi adapter (USB or PCIe), whether the running kernel has a driver and firmware for it, "
                "rfkill, and the band and signal of its connection. "
                "It only reads. No module is loaded, and no stick is switched."),
        TestDef(SPEEDTEST_TEST_ID, "Internet Speed",
                "Opt-in. Ookla speedtest (or speedtest-cli). Measures download, upload, idle and loaded latency "
                "(bufferbloat) and packet loss. Says whether the network port is the limit. Uses ~1 GB of data "
                "on a fast line."),
    ]),
    Category("storage", "Storage and memory", [
        TestDef("09", "Disk Configuration", "Filesystem usage and mount points."),
        TestDef("10", "NVMe Devices",
                "Detection, and PCIe link speed/width vs. what drive and slot support. DRAM cache or host memory "
                "buffer (DRAM-less). SMART health with wear, errors, temperature and unsafe shutdowns."),
        TestDef("14", "Memory and Swap",
                "RAM usage and the full swap topology, with zram, zswap, disk swap, overlaps and swappiness."),
        TestDef("37", "Unified Memory and VRAM Pressure",
                "VRAM/GTT usage, OOM-kill history, vm.max_map_count, swappiness."),
        TestDef("49", "CPU Memory Bandwidth",
                "stress-ng STREAM-like bandwidth on 1 thread and all threads. Shows the GDDR6 latency cost "
                "the CPU pays for the GPU's console-class bandwidth."),
        TestDef(DISK_TEST_ID, "Disk Speed (read, write, SLC cache)",
                "Opt-in. Sequential and random 4K read of the system disk, read-only. Optionally writes a "
                "temporary file to measure write speed and where the SLC cache runs out."),
    ]),
    Category("logs", "System logs", [
        TestDef("15", "Boot Logs", "Current-boot journal errors, with known-benign BC-250 noise filtered out."),
        TestDef("16", "System Journal", "Journal warnings and errors from the last 7 days, same filtering."),
    ]),
    Category("gpu", "GPU and graphics", [
        TestDef("17", "amdgpu Driver", "Confirms amdgpu is bound to the Cyan Skillfish APU."),
        TestDef("18", "GPU Governor", "Verifies a governor is running. Without one the GPU is pinned at 1500 MHz."),
        TestDef("19", "GPU Frequency Scaling", "Reads pp_dpm_sclk / pp_dpm_mclk to confirm the clock actually moves."),
        TestDef("20", "Vulkan / Mesa", "Confirms RADV reports GFX1013 and not the llvmpipe software fallback."),
        TestDef("21", "Compute Unit Count",
                "Active CUs from the live GPU registers, which needs admin rights and umr. Otherwise, the kernel "
                "value. Stock is 24, unlocked is up to 40."),
        TestDef("47", "Vulkan Futureproof Matrix",
                "Vulkan API level and the feature set modern games need. That is ray tracing, mesh shaders, VRS, "
                "pipeline libraries and the VRAM carveout vs. today's 8 GiB recommendation. Hard evidence of "
                "which current and upcoming titles can run at all."),
        TestDef("50", "Video Decode and Encode (VCN)",
                "vainfo codec matrix: H.264/HEVC/VP9/AV1 decode and encode. Matters for streaming, OBS "
                "recording and video playback while gaming."),
        TestDef("51", "HDMI-CEC",
                "The CEC adapter of the DisplayPort output, whether the TV answers, and Bazzite's CEC mode. "
                "The adapter is there only when the DP-to-HDMI converter tunnels CEC. "
                "Whether the board can turn the TV on and off."),
        TestDef("52", "HDMI-CEC Services",
                "Whether the services behind the TV control run: Valve's CEC daemon (cecd), BC-250 CEC Manager's "
                "background and boot services when installed, and Bazzite's dGPU CEC services when enabled."),
        TestDef("29", "Display Session, DisplayPort and HDMI",
                "Identifies the display manager, session type and compositor, and the connector status."),
    ]),
    Category("cpu", "CPU and firmware", [
        TestDef("23", "IOMMU Disabled",
                "Counts IOMMU groups. IOMMU is broken on the BC-250 and must be off, via BIOS or the amd_iommu=off "
                "kernel argument."),
        TestDef("24", "CPU Mitigations", "Passes when mitigations=off is set. That is worth roughly +18 FPS on this board."),
        TestDef("25", "CPU Core and Thread Count", "Reports cores/threads — 6C/12T stock, 8C/16T after unlocking."),
        TestDef("26", "CPU Power Management", "Checks cpufreq scaling and C-states. Both need the BC-250 ACPI fix."),
        TestDef("46", "CPU Voltage",
                "CPU/SoC voltage rails from hwmon (amdgpu vddgfx/vddnb) plus the voltage each core requests. "
                "That is the current P-state VID via MSR, one line per core."),
    ]),
    Category("stability", "Stability and thermals", [
        TestDef("22", "Hardware Sensors",
                "nct6683/nct6687 SuperIO, GPU and CPU temperatures, CPU and GPU rails, fan RPM sanity."),
        TestDef("27", "Handheld Daemon", "Confirms hhd.service is masked. It causes constant micro-stuttering."),
        TestDef("28", "Suspend Targets",
                "Which sleep the board offers (suspend-to-idle), whether systemd may use it, and the suspends since boot."),
        TestDef("40", "Power Delivery and Throttling",
                "GPU power cap and draw, governor frequency ceiling, throttle messages."),
    ]),
    Category("crash", "Crash forensics", [
        TestDef("34", "Previous Boot Shutdown Integrity",
                "Flags previous boots that ended with no shutdown sequence — the signature of a hard lockup."),
        TestDef("35", "GPU Hang and Reset History",
                "Ring timeouts, GPU resets, VM faults and soft recoveries across retained boots."),
        TestDef("36", "Kernel Panic, Lockup and Crash Dump",
                "Oopses, soft/hard lockups, call traces, coredumpctl records and NMI watchdog state."),
    ]),
    Category("gaming", "Gaming", [
        TestDef("38", "Steam and Gaming Stack", "Steam, gamescope, gamemode, MangoHud and umu. Library paths and free space."),
        TestDef("39", "Audio Stack", "PipeWire/WirePlumber state, default sink and ALSA cards."),
        TestDef("48", "Real-Game Frametime (MangoHud logs)",
                "Reads the most recent MangoHud logs from real play sessions. Gives average FPS, 1% and 0.1% lows "
                "and stutter share. This is evidence from actual games, which synthetic benchmarks cannot give."),
        TestDef(STRESS_TEST_ID, "CPU + GPU Stress and Telemetry",
                "Opt-in. Loads the board and records clocks, temperature, power and fans throughout. "
                "Includes a sustained-performance verdict, first minute vs. last minute."),
    ]),
    Category("performance", "Performance", [
        TestDef(BENCH_TEST_ID, "Performance Benchmark (CPU / GPU score)",
                "Opt-in. CPU single/multi-thread (stress-ng) and GPU FP32 compute (vkpeak). Scored against "
                "a stock BC-250 baseline (= 100) to compare CU and core unlocks. Adds a comparison ladder "
                "against known systems. Those are Steam Deck, Series S, Steam Machine, PS5 and desktop GPUs."),
        TestDef("60", "VKCube (Vulkan on the screen)",
                "Draws the Vulkan tools' spinning cube in a window for five seconds, as the desktop user in the "
                "running session: Vulkan reaches the screen. An error when vkcube ends by itself."),
    ]),
    Category("updates", "Updates", [
        TestDef("13", "Security Configuration", "firewalld zones and SELinux enforcement mode."),
        TestDef("32", "OSTree Deployment",
                "Lists deployments and warns when a newer one is staged and waiting for a reboot."),
        TestDef("33", "Update and Patch", "Checks for available rpm-ostree updates and lists Flatpak remotes."),
        TestDef("45", "Installed Packages",
                "Counts installed software per source. The sources are image RPMs, layered and overridden packages, "
                "Flatpak apps (system and user), Homebrew, AppImages and Distrobox containers. "
                "Names and versions only."),
    ]),
]

TESTS: dict[str, TestDef] = {t.id: t for c in CATEGORIES for t in c.tests}
CATEGORY_OF: dict[str, Category] = {t.id: c for c in CATEGORIES for t in c.tests}
