# SPDX-License-Identifier: GPL-3.0-or-later
"""What the quickfixes read, as your own user: the files, the kernel's own reports and rpm-ostree's kernel arguments.
Every reader takes its roots (/etc, /proc, /sys, /var, the home folder) so the tests give it a folder of their
own."""

from __future__ import annotations

import os
import shutil
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from . import system

ROOT = Path("/")


# ------------------------------------------------------------------------------------------------- Test Extras
@dataclass(frozen=True)
class Tool:
    command: str                # what the tests look for on PATH
    package: str                # what the installer installs
    used_by: str                # the tests that use it


@dataclass(frozen=True)
class Group:
    option: str                 # install-requirements.sh's option for it
    name: str
    what: str                   # how it is installed, in a few words
    tools: tuple[Tool, ...]


# The groups of Board Test's development/tools/install-requirements.sh, in its order (tests/test_extras.py reads the
# script and keeps the two the same).
GROUPS: tuple[Group, ...] = (
    Group("--rpms", "RPM packages", "Layered with rpm-ostree: active after a reboot.", (
        Tool("stress-ng", "stress-ng", "41 (CPU load), 42 (CPU score), 49 (memory bandwidth)"),
        Tool("sensors", "lm_sensors", "22 (temperatures and fans)"),
        Tool("vkmark", "vkmark", "41 (GPU load, when memtest_vulkan and vkpeak are missing)"),
        Tool("nvme", "nvme-cli", "10 (SMART health)"),
        Tool("fio", "fio", "43 (random 4K read)"),
    )),
    Group("--bins", "Binaries", "The latest releases from their GitHub projects, into ~/.local/bin.", (
        Tool("memtest_vulkan", "memtest_vulkan", "41 (GPU load and a VRAM error check)"),
        Tool("vkpeak", "vkpeak", "42 (GPU score), 41 (GPU load, when memtest_vulkan is missing)"),
    )),
    Group("--speedtest", "Speed test", "Ookla's CLI, into ~/.local/bin; running it accepts Ookla's license and "
          "privacy terms.", (
        Tool("speedtest", "Ookla speedtest", "44 (Internet Speed; speedtest-cli works too)"),
    )),
    Group("--dev", "Development extras", "Layered with rpm-ostree: active after a reboot.", (
        Tool("sqlite3", "sqlite", "no test: the app's history database, during development"),
    )),
)
# Already on Bazzite: what the tests use besides.
BUILT_IN = (Tool("glmark2", "glmark2", "41 (GPU load, last resort)"),
            Tool("vulkaninfo", "vulkan-tools", "20, 21 (Vulkan, compute units)"),
            Tool("smartctl", "smartmontools", "10 (SMART health)"))
INSTALLER = "development/tools/install-requirements.sh"             # in Board Test's folder
BOARD_TEST = Path("/opt/bc250-board-test")
BREW_BIN = Path("/home/linuxbrew/.linuxbrew/bin")                  # Homebrew on Bazzite


def find_tool(command: str, home: Path | None = None, path: str | None = None) -> str:
    """Where the tests would find *command*: PATH, then ~/.local/bin and Homebrew (test-board.sh's find_tool);
    "" when it is not there."""
    found = shutil.which(command, path=path if path is not None else os.environ.get("PATH", ""))
    if found:
        return found
    home = home or Path.home()
    for folder in (home / ".local" / "bin", BREW_BIN):
        candidate = folder / command
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return ""


def installer(board_test: Path = BOARD_TEST, checkout: Path | None = None) -> Path | None:
    """Board Test's install-requirements.sh: the installed one, else the checkout's (apps/check beside this app)."""
    checkout = checkout or Path(__file__).resolve().parents[2] / "check"
    for folder in (board_test, checkout):
        script = folder / INSTALLER
        if script.is_file():
            return script
    return None


# --------------------------------------------------------------------------------------------- MangoHud Config
MANGOHUD_CONF = ".config/MangoHud/MangoHud.conf"                # in the home folder
LOG_FOLDER = "mangohud-logs"                                    # in the home folder
LOG_INTERVAL = 500


def mangohud_conf(home: Path | None = None) -> Path:
    return (home or Path.home()) / MANGOHUD_CONF


def conf_values(text: str) -> dict[str, str]:
    """MangoHud's key=value lines (a bare key is "1"); comments and blank lines left out; the last one counts."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip() if _ else "1"
    return values


def with_logging(text: str, folder: Path) -> str:
    """*text* with MangoHud's log turned on: output_folder, autostart_log and log_interval set (a line that sets one
    is replaced where it is, the others are added at the end); every other line stays."""
    want = {"output_folder": str(folder), "autostart_log": "1", "log_interval": str(LOG_INTERVAL)}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        key = line.split("#", 1)[0].partition("=")[0].strip()
        if key in want:
            lines[i] = f"{key}={want.pop(key)}"
    if want:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("# FPS log, read by BC-250 Board Test (written by BC-250 Quickfix)")
        lines += [f"{key}={value}" for key, value in want.items()]
    return "\n".join(lines) + "\n"


def logging_on(values: dict[str, str]) -> bool:
    return bool(values.get("output_folder")) and values.get("autostart_log", "0") not in ("", "0")


def log_files(folder: Path) -> list[Path]:
    try:
        return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix == ".csv")
    except OSError:
        return []


# --------------------------------------------------------------------------------------------- Fix GPU Metrics
@dataclass(frozen=True)
class Metrics:
    installed: bool             # the governor's config.toml is there
    fix: bool                   # fix-metrics = true in it
    method: str                 # its [gpu-usage] method; "" when it sets none
    mounted: bool               # a patched gpu_metrics is mounted over the sysfs file
    problem: str = ""           # the config could not be read


def metrics(root: Path = ROOT) -> Metrics:
    config = root / "etc" / system.GOVERNOR_CONFIG
    mounted = mounted_gpu_metrics(root)
    if not config.is_file():
        return Metrics(False, False, "", mounted)
    try:
        usage = tomllib.loads(config.read_text(encoding="utf-8")).get("gpu-usage", {})
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return Metrics(True, False, "", mounted, f"{config} could not be read: {exc}")
    usage = usage if isinstance(usage, dict) else {}
    method = usage.get("method", "")
    return Metrics(True, usage.get("fix-metrics") is True, method if isinstance(method, str) else "", mounted)


def mounted_gpu_metrics(root: Path = ROOT) -> bool:
    try:
        text = (root / "proc" / "self" / "mountinfo").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(line.split()[4].endswith("/gpu_metrics") for line in text.splitlines() if len(line.split()) > 4)


# ---------------------------------------------------------------------------------------------- Sensors Module
# The board's SuperIO chip, a Nuvoton NCT6686D: the kernel's nct6683 driver serves it when forced, the nct6687 driver
# (which some images ship) by itself. Either gives a hwmon named after the chip (nct6683, nct6686, nct6687).
DRIVERS = ("nct6683", "nct6687")


@dataclass(frozen=True)
class Sensors:
    driver: str                 # the SuperIO driver that is loaded: nct6683 or nct6687; "" when none is
    ours: bool                  # our modprobe.d file is there
    elsewhere: str              # another modprobe.d file that forces nct6683: its name
    hwmon: str                  # the chip's hwmon, as it names itself; "" when there is none

    @property
    def on(self) -> bool:
        """The sensors are there now, or nct6683 is forced from the next boot."""
        return bool(self.driver) or self.ours or bool(self.elsewhere)


def sensors(root: Path = ROOT) -> Sensors:
    driver = next((d for d in DRIVERS if (root / "sys" / "module" / d).is_dir()), "")
    ours = system.made(root / "etc" / system.SENSORS_CONF)
    elsewhere = ""
    folder = root / "etc" / "modprobe.d"
    if folder.is_dir():
        for conf in sorted(folder.glob("*.conf")):
            if conf.name in (Path(system.SENSORS_CONF).name, system.earlier(Path(system.SENSORS_CONF)).name):
                continue
            try:
                text = conf.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(line.split()[:2] == ["options", "nct6683"] and "force=true" in line
                   for line in text.splitlines() if not line.lstrip().startswith("#")):
                elsewhere = conf.name
                break
    hwmon = ""
    for name in sorted((root / "sys" / "class" / "hwmon").glob("*/name")):
        try:
            text = name.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text.startswith("nct668"):
            hwmon = text
            break
    return Sensors(driver, ours, elsewhere, hwmon)


# --------------------------------------------------------------------------------------------- Game Memory Map
@dataclass(frozen=True)
class MapCount:
    value: int                  # vm.max_map_count now; 0 when it cannot be read
    ours: bool                  # our sysctl.d file is there


def mapcount(root: Path = ROOT) -> MapCount:
    try:
        value = int((root / "proc" / "sys" / "vm" / "max_map_count").read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        value = 0
    return MapCount(value, system.made(root / "etc" / system.MAPCOUNT_CONF))


# ------------------------------------------------------------------------------------------ Persistent Journal
@dataclass(frozen=True)
class Journal:
    persistent: bool            # /var/log/journal is there: journald keeps the journal on the disk
    ours: bool                  # the quickfix made it


def journal(root: Path = ROOT) -> Journal:
    folder = root / "var" / system.JOURNAL_DIR
    return Journal(folder.is_dir(), system.made(folder / system.JOURNAL_MARK))


# ------------------------------------------------------------------------------- IOMMU Off, CPU Mitigations Off
@dataclass(frozen=True)
class Karg:
    arg: str                    # the kernel argument: amd_iommu=off, mitigations=off
    now: bool                   # on the running kernel's command line (/proc/cmdline)
    next: bool | None           # on the next boot's (rpm-ostree kargs); None when rpm-ostree cannot tell
    ours: bool                  # the quickfix added it (its note in /var/lib/bc250-quickfix)
    iommu_groups: int | None    # the IOMMU groups now (0: the IOMMU is off); None without /sys/kernel/iommu_groups

    @property
    def pending(self) -> bool:
        """The next boot differs from the running one: a reboot applies it."""
        return self.next is not None and self.next != self.now


def karg(key: str, root: Path = ROOT, next_kargs: Callable[[], list[str] | None] = system.next_kargs) -> Karg:
    arg = system.KARGS[key]
    try:
        now = arg in (root / "proc" / "cmdline").read_text(encoding="utf-8", errors="replace").split()
    except OSError:
        now = False
    following = next_kargs()
    groups_dir = root / "sys" / "kernel" / "iommu_groups"
    try:
        groups: int | None = sum(1 for p in groups_dir.iterdir() if p.is_dir())
    except OSError:
        groups = None
    return Karg(arg, now, None if following is None else arg in following,
                system.made(system.karg_mark(root / "var", key)), groups)
