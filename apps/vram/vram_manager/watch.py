# SPDX-License-Identifier: GPL-3.0-or-later
"""The sessions: what each program asked of the memory while it ran, and how it ended (owner, 26-11-2026).

The watcher runs in the desktop session as a user service (service.py) while the suite's memory guard is on:

    python -m vram_manager.watch

Every SAMPLE_S seconds it reads the board's figures: the RAM in use (MemTotal minus MemAvailable), the RAM the GPU
borrows (amdgpu's mem_info_gtt_used), the swap in use and the memory pressure ("full avg10" in
/proc/pressure/memory, the share of time every task waited for memory). It also reads each program of the session:
the units under the user manager's app.slice, with their memory and swap (memory.current, memory.swap.current).

A program is a session when it took MIN_MIB or more at its peak, or when it was killed. A session keeps the board's
peaks while it ran. When the program's unit is gone, the watcher writes the session to SESSIONS, newest last, and
keeps the last KEEP. How it ended:

    Closed                          the unit went without a kill
    Guard: swap full                systemd-oomd ended it: swap was over the guard's limit
    Guard: memory pressure          systemd-oomd ended it: memory pressure was over the guard's limit
    Killed: swap full               the kernel's OOM killer ended it, with the swap full at the peak
    Killed: GPU memory              the same, with the GPU borrowing half the RAM or more at the peak
    Killed: RAM full                the same, otherwise
    Running when the session ended  the watcher was stopped (log out, shut down) while it ran
    Board restarted while it ran    found open at the next boot: the board froze or lost power

systemd-oomd and the kernel say who they ended in the journal: oomd's "Marked … for killing due to memory used … and
swap used …" and "Memory pressure for … is …", the kernel's "oom-kill:… task_memcg=…". A program's own oom_kill count
(memory.events) also tells a kernel kill.

Standard library and the app's own modules only, so the service starts without Qt."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import APP_ID, swap, system

SAMPLE_S = 2
MIN_MIB = 1024                  # a program is a session when it took this much at its peak (memory and swap)
KEEP = 50                       # the sessions kept in SESSIONS
SWAP_FULL = 0.95                # a kill with the swap this full at the peak: "swap full"
GPU_SHARE = 0.5                 # a kill with the GPU borrowing this share of the RAM at the peak: "GPU memory"
PROPOSE_AFTER = 3               # the sessions a proposal needs
LOOK_BACK = 10                  # the sessions a proposal looks at, newest first
SPARE_MIB = 2048                # the RAM the Smooth profile's GTT limit leaves the system

CLOSED = "Closed"
GUARD_SWAP = "Guard: swap full"
GUARD_PRESSURE = "Guard: memory pressure"
KILLED_SWAP = "Killed: swap full"
KILLED_GPU = "Killed: GPU memory"
KILLED_RAM = "Killed: RAM full"
SESSION_ENDED = "Running when the session ended"
RESTARTED = "Board restarted while it ran"
SHORT_OF_SWAP = (GUARD_SWAP, KILLED_SWAP)


def data_dir() -> Path:
    from bc250_core.platform import data_home
    return data_home() / APP_ID


def sessions_path() -> Path:
    return data_dir() / "sessions.jsonl"


def open_path() -> Path:
    return data_dir() / "sessions-open.json"


@dataclass
class Session:
    unit: str                       # the unit under app.slice
    program: str                    # its name for people
    start: float                    # epoch seconds
    boot_id: str
    own_mib: int = 0                # the program's own peak, memory and swap
    ram_mib: int = 0                # the board's peaks while it ran
    gtt_mib: int = 0
    swap_mib: int = 0
    swap_total_mib: int = 0
    ram_total_mib: int = 0
    pressure: float = 0.0
    oom_kills: int = 0              # memory.events oom_kill, last seen
    end: float = 0.0
    ended: str = ""


@dataclass
class Board:
    ram_mib: int = 0
    ram_total_mib: int = 0
    gtt_mib: int = 0
    swap_mib: int = 0
    swap_total_mib: int = 0
    pressure: float = 0.0


# --- Reading ---------------------------------------------------------------------------------------------------

def read_board(sys_root: Path = Path("/sys"), proc_root: Path = Path("/proc")) -> Board:
    info = system._meminfo(proc_root)
    usage = system.read_usage(sys_root, proc_root)
    pressure = 0.0
    try:
        for line in (proc_root / "pressure/memory").read_text().splitlines():
            if line.startswith("full "):
                pressure = float(dict(w.split("=", 1) for w in line.split()[1:]).get("avg10", 0))
    except (OSError, ValueError):
        pass
    total = info.get("MemTotal", 0)
    return Board(ram_mib=(total - info.get("MemAvailable", total)) // 1024, ram_total_mib=total // 1024,
                 gtt_mib=usage.gtt_used_mib or 0,
                 swap_mib=(info.get("SwapTotal", 0) - info.get("SwapFree", 0)) // 1024,
                 swap_total_mib=info.get("SwapTotal", 0) // 1024, pressure=pressure)


def app_slice(proc_root: Path = Path("/proc"), cgroup_root: Path = Path("/sys/fs/cgroup")) -> Path | None:
    """The user manager's app.slice, from the watcher's own cgroup (it runs under the same user manager)."""
    try:
        line = (proc_root / "self/cgroup").read_text().splitlines()[0]
    except (OSError, IndexError):
        return None
    path = line.split("::", 1)[-1]
    match = re.match(r"(.*/user@[^/]+\.service)/", path + "/")
    return cgroup_root / match.group(1).lstrip("/") / "app.slice" if match else None


def _bytes(path: Path) -> int:
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return 0


def read_programs(folder: Path | None) -> dict[str, tuple[int, int]]:
    """Each unit under app.slice: (its memory and swap in MiB, its oom_kill count)."""
    out: dict[str, tuple[int, int]] = {}
    if folder is None:
        return out
    try:
        units = [p for p in folder.iterdir() if p.is_dir()]
    except OSError:
        return out
    for unit in units:
        kills = 0
        try:
            for line in (unit / "memory.events").read_text().splitlines():
                if line.startswith("oom_kill "):
                    kills = int(line.split()[1])
        except (OSError, ValueError):
            pass
        mib = (_bytes(unit / "memory.current") + _bytes(unit / "memory.swap.current")) // (1024 * 1024)
        out[unit.name] = (mib, kills)
    return out


# --- Names -----------------------------------------------------------------------------------------------------

DESKTOP_DIRS = (Path.home() / ".local/share/applications", Path.home() / ".local/share/flatpak/exports/share/applications",
                Path("/var/lib/flatpak/exports/share/applications"), Path("/usr/share/applications"))


def desktop_id(unit: str) -> str:
    """The app a unit runs, as the desktop names it: app-org.kde.konsole-423093.scope is org.kde.konsole."""
    name = unit.replace("\\x2d", "-")
    name = re.sub(r"\.(scope|service)$", "", name)
    name = name.split("@", 1)[0]
    name = re.sub(r"^app-", "", name)
    name = re.sub(r"^flatpak-", "", name)
    return re.sub(r"-\d+$", "", name)


def steam_name(number: int, steam_dir: Path | None) -> str:
    """A Steam game's name: a shortcut's by its appid, else the installed game's manifest; "" when neither."""
    if steam_dir is None:
        return ""
    try:
        from bc250_core import steam
        for item in steam.shortcuts(steam_dir):
            if int(steam.field(item, "appid", 0)) & 0xFFFFFFFF == number:
                return str(steam.field(item, "AppName"))
    except Exception:  # noqa: BLE001  (a name is a nicety: the unit's own stays)
        pass
    try:
        text = (steam_dir / "steamapps" / f"appmanifest_{number}.acf").read_text(errors="replace")
        match = re.search(r'"name"\s+"([^"]*)"', text)
        return match.group(1) if match else ""
    except OSError:
        return ""


def program_name(unit: str, steam_dir: Path | None = None, dirs: tuple[Path, ...] = DESKTOP_DIRS) -> str:
    """A unit's name for people: a Steam game's name, the Name of the app's desktop file, else the app's ID."""
    app = desktop_id(unit)
    match = re.fullmatch(r"steam-app(\d+)", app)
    if match:
        return steam_name(int(match.group(1)), steam_dir) or f"Steam game {match.group(1)}"
    for folder in dirs:
        try:
            for line in (folder / f"{app}.desktop").read_text(errors="replace").splitlines():
                if line.startswith("Name="):
                    return line[5:].strip()
        except OSError:
            continue
    return app


# --- How a program ended ---------------------------------------------------------------------------------------

def _journal(args: list[str]) -> str:
    try:
        return subprocess.run(["journalctl", "--no-pager", "-o", "cat", *args], capture_output=True, text=True,
                              timeout=30, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def ending(session: Session, journal: Callable[[list[str]], str] = _journal) -> str:
    """How the session's program ended, from the journal since it started and its own oom_kill count."""
    since = ["-b", "--since", f"@{int(session.start)}"]
    for line in journal([*since, "-u", "systemd-oomd.service"]).splitlines():
        if f"/{session.unit}" in line or line.endswith(session.unit):
            if line.startswith("Marked ") and "swap used" in line:
                return GUARD_SWAP
            if line.startswith("Memory pressure for "):
                return GUARD_PRESSURE
    killed = session.oom_kills > 0 or any(
        "oom-kill:" in line and f"/{session.unit}," in line for line in journal([*since, "-k"]).splitlines())
    if not killed:
        return CLOSED
    if session.swap_total_mib and session.swap_mib >= session.swap_total_mib * SWAP_FULL:
        return KILLED_SWAP
    if session.ram_total_mib and session.gtt_mib >= session.ram_total_mib * GPU_SHARE:
        return KILLED_GPU
    return KILLED_RAM


# --- The record ------------------------------------------------------------------------------------------------

def read_sessions(path: Path | None = None) -> list[Session]:
    """The recorded sessions, oldest first; a line that cannot be read is left out."""
    out = []
    try:
        lines = (path or sessions_path()).read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        try:
            out.append(Session(**json.loads(line)))
        except (ValueError, TypeError):
            continue
    return out


def write_session(session: Session, path: Path | None = None) -> None:
    path = path or sessions_path()
    kept = read_sessions(path)[-(KEEP - 1):] + [session]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(asdict(s)) + "\n" for s in kept), encoding="utf-8")
    tmp.replace(path)


def boot_id(proc_root: Path = Path("/proc")) -> str:
    return system._read(proc_root / "sys/kernel/random/boot_id") or ""


@dataclass
class Watcher:
    """One look every SAMPLE_S seconds (tick()); the open sessions are kept in OPEN, so a restart of the watcher
    goes on with them, and a new boot finds the ones the board left."""
    sys_root: Path = Path("/sys")
    proc_root: Path = Path("/proc")
    folder: Path | None = None
    steam_dir: Path | None = None
    record: Path | None = None
    open_file: Path | None = None
    journal: Callable[[list[str]], str] = _journal
    clock: Callable[[], float] = time.time
    open: dict[str, Session] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.record = self.record or sessions_path()
        self.open_file = self.open_file or open_path()
        self.boot = boot_id(self.proc_root)
        try:
            left = {k: Session(**v) for k, v in json.loads(self.open_file.read_text(encoding="utf-8")).items()}
        except (OSError, ValueError, TypeError):
            left = {}
        for unit, session in left.items():
            if session.boot_id == self.boot:
                self.open[unit] = session
            elif session.own_mib >= MIN_MIB:
                session.ended, session.end = RESTARTED, session.end or session.start
                write_session(session, self.record)
        self.save_open()

    def save_open(self) -> None:
        self.open_file.parent.mkdir(parents=True, exist_ok=True)
        self.open_file.write_text(json.dumps({k: asdict(v) for k, v in self.open.items()}), encoding="utf-8")

    def tick(self) -> None:
        board = read_board(self.sys_root, self.proc_root)
        programs = read_programs(self.folder)
        now = self.clock()
        for unit, (mib, kills) in programs.items():
            session = self.open.get(unit)
            if session is None:
                session = self.open[unit] = Session(unit, program_name(unit, self.steam_dir), now, self.boot)
            session.own_mib = max(session.own_mib, mib)
            session.oom_kills = kills
            session.ram_mib = max(session.ram_mib, board.ram_mib)
            session.gtt_mib = max(session.gtt_mib, board.gtt_mib)
            session.swap_mib = max(session.swap_mib, board.swap_mib)
            session.pressure = max(session.pressure, board.pressure)
            session.swap_total_mib, session.ram_total_mib = board.swap_total_mib, board.ram_total_mib
            session.end = now
        for unit in [u for u in self.open if u not in programs]:
            session = self.open.pop(unit)
            session.end = now
            session.ended = ending(session, self.journal)
            if session.own_mib >= MIN_MIB or session.ended != CLOSED:
                write_session(session, self.record)
        self.save_open()

    def stop(self) -> None:
        """The watcher stops (log out, shut down): the open sessions are written as still running then."""
        for session in self.open.values():
            if session.own_mib >= MIN_MIB:
                session.ended = SESSION_ENDED
                write_session(session, self.record)
        self.open.clear()
        self.save_open()


# --- The proposal ----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Proposal:
    text: str
    zram_size: str = ""             # a zram size to write, "" for none
    pages: int | None = None        # a GTT limit to write, None for none


def gtt_pages(ram_mib: int) -> int:
    """The Smooth profile's GTT limit: the RAM less SPARE_MIB, in 4 KiB pages."""
    return max(ram_mib - SPARE_MIB, 1024) * 256


def bigger_zram(setup: swap.Setup) -> str:
    """The next zram size up from the layout written; "" when there is none (twice the RAM, or zswap)."""
    sizes = [size for _label, size, _factor in swap.ZRAM_SIZES]
    if setup.layout == swap.BAZZITE:
        return "ram"                                # Bazzite's own is half the RAM
    if setup.layout == swap.ZRAM and setup.zram_size in sizes[:-1]:
        return sizes[sizes.index(setup.zram_size) + 1]
    return ""


def propose(sessions: list[Session], setup: swap.Setup, ram_mib: int, next_pages: int | None) -> Proposal:
    """What the recorded sessions ask for: a larger zram when swap ran out, a GTT limit below the RAM when the GPU's
    borrowing filled it. Nothing before PROPOSE_AFTER sessions."""
    if len(sessions) < PROPOSE_AFTER:
        return Proposal(f"A proposal needs {PROPOSE_AFTER} sessions. {len(sessions)} recorded so far.")
    recent = sessions[-LOOK_BACK:]
    short_swap = any(s.ended in SHORT_OF_SWAP or (s.ended == RESTARTED and s.swap_total_mib
                                                   and s.swap_mib >= s.swap_total_mib * SWAP_FULL) for s in recent)
    short_gpu = any(s.ended == KILLED_GPU for s in recent)
    zram = bigger_zram(setup) if short_swap else ""
    pages = gtt_pages(ram_mib) if short_gpu and ram_mib else None
    if pages is not None and next_pages is not None and next_pages <= pages:
        pages = None                                # the next boot's limit leaves the room already
    parts = []
    if zram:
        label = next(lbl for lbl, size, _f in swap.ZRAM_SIZES if size == zram)
        parts.append(f"zram {label[0].lower() + label[1:]}")
    if pages is not None:
        parts.append(f"GTT limit {system.mib_text(pages // 256)}")
    count = len(recent)
    if parts:
        return Proposal(f"Proposal from {count} sessions: {' and '.join(parts)}.", zram, pages)
    if short_swap:
        return Proposal(f"Swap ran out in the last {count} sessions, and zram is at its largest. Try zswap with a swap "
                        "file.")
    return Proposal(f"No change: none of the last {count} sessions ran out of memory.")


# --- The service -----------------------------------------------------------------------------------------------

def main() -> int:
    from bc250_core import steam
    watcher = Watcher(folder=app_slice(), steam_dir=steam.find_steam())
    running = True

    def stop(_signum, _frame) -> None:
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while running:
        try:
            watcher.tick()
        except OSError as error:                # a look that fails: the next one tries again
            print(f"watch: {error}", file=sys.stderr)
        time.sleep(SAMPLE_S)
    watcher.stop()
    return 0


if __name__ == "__main__":
    os.nice(5)                                  # a look every two seconds never competes with a game
    sys.exit(main())
