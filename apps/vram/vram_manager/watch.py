# SPDX-License-Identifier: GPL-3.0-or-later
"""The sessions: what each program asked of the memory while it ran, and how it ended (owner, 26-11-2026).

The watcher runs in the desktop session as a user service (service.py) while recording is on (owner, 26-11-2026:
recording on its own, not with the memory guard):

    python -m vram_manager.watch

Every SAMPLE_S seconds it reads the board's figures: the RAM in use (MemTotal minus MemAvailable), the RAM the GPU
borrows (amdgpu's mem_info_gtt_used), the VRAM in use (mem_info_vram_used), the swap in use, the memory pressure
("full avg10" in /proc/pressure/memory, the share of time every task waited for memory) and the CPU load since the
last look (/proc/stat, all cores together). The CPU load is for context only: nothing is decided on it. It also reads each program of the session:
the units under the user manager's app.slice, with their memory and swap (memory.current, memory.swap.current).

A program is a session when it took MIN_MIB or more at its peak, when it was killed, or when it is a game (owner,
26-11-2026: a PS2 game of 1001 MiB was left out). A session keeps the board's
peaks while it ran. When the program's unit is gone, the watcher writes the session to SESSIONS, newest last, and
keeps the last KEEP. How it ended:

    Closed                          the unit went without a kill
    Guard: swap full                systemd-oomd ended it: swap was over the guard's limit
    Guard: memory pressure          systemd-oomd ended it: memory pressure was over the guard's limit
    Killed: swap full               the kernel's OOM killer ended it, with the swap full at the peak
    Killed: GPU memory              the same, with the GPU borrowing half the RAM or more at the peak
    Killed: RAM full                the same, otherwise
    Crashed                         a process of it dumped core (systemd-coredump): not a lack of memory
    Running when the session ended  the watcher was stopped (log out, shut down) while it ran
    Board restarted while it ran    found open at the next boot: the board froze or lost power

systemd-oomd and the kernel say who they ended in the journal: oomd's "Marked … for killing due to memory used … and
swap used …" and "Memory pressure for … is …", the kernel's "oom-kill:… task_memcg=…", systemd-coredump an entry
with COREDUMP_USER_UNIT, the unit (owner's board, 26-11-2026: shadPS4 stopped on a trap and took 36 s to dump). A program's own oom_kill count
(memory.events) also tells a kernel kill.

The Programs window (owner, 26-11-2026) reads two more records. HISTORY holds one point a minute for HISTORY_S, with
the minute's peaks of the board's figures. PROGRAMS holds each program's runs, its own peak and average memory, and
how often a lack of memory ended it, for every program the watcher has seen.

The owner marks programs in that window to close for games (CLOSES). When a game's unit starts (a Steam shortcut or
game, steam-app<number>), the watcher stops each marked program that runs with `systemctl --user stop`: systemd sends
it SIGTERM, on which most programs save and quit. Steam and the games are never stopped. Each stop goes to
CLOSES_LOG, and the program's session ends as "Closed for a game". A game that runs when the watcher starts closes
nothing.

When a game freezes the board for lack of memory, the watcher ends it (owner, 26-11-2026: "end the game, then
notify"): when the memory pressure stays at STALL_PERCENT or more for STALL_S seconds while a game runs, it sends the
game's unit SIGKILL (systemctl --user kill), which frees its memory at once. The session ends as "Ended: memory
stall", a lack of memory, so the learning steps point to a change at once. A notification says so, with a button
that opens the window. The values are starting values to test on the board.

When a game crashes, systemd-coredump logs "Process <pid> (<name>) of user <uid> terminated abnormally" at once,
then writes the crash dump, which took 36 s for shadPS4 on the owner's board (26-11-2026); the game's window stays
frozen meanwhile. The watcher looks for that line while a game runs, finds the game by the process's cgroup, and
notifies at once with the memory figures of that moment (owner, 26-11-2026: "notify on crash").

Standard library and the app's own modules only, so the service starts without Qt."""

from __future__ import annotations

import json
import os
import re
import shlex
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
SPARE_MIB = 2048                # the RAM the Smooth profile's GTT limit leaves the system
POINT_S = 60                    # one point of the history a minute
HISTORY_S = 24 * 3600           # the history kept
STALL_PERCENT = 40.0            # a game is ended when the memory pressure stays at this or more ...
STALL_S = 10                    # ... for this long (starting values, owner 26-11-2026)
CRASH = re.compile(r"Process (\d+) \((.*)\) of user \d+ terminated abnormally")

CLOSED = "Closed"
GUARD_SWAP = "Guard: swap full"
GUARD_PRESSURE = "Guard: memory pressure"
KILLED_SWAP = "Killed: swap full"
KILLED_GPU = "Killed: GPU memory"
KILLED_RAM = "Killed: RAM full"
CRASHED = "Crashed"
STALLED = "Ended: memory stall"
SESSION_ENDED = "Running when the session ended"
RESTARTED = "Board restarted while it ran"
CLOSED_FOR_GAME = "Closed for a game"
SHORT_OF_SWAP = (GUARD_SWAP, KILLED_SWAP)
SHORT = (GUARD_SWAP, GUARD_PRESSURE, KILLED_SWAP, KILLED_GPU, KILLED_RAM, STALLED)  # ended by a lack of memory


def data_dir() -> Path:
    from bc250_core.platform import data_home
    return data_home() / APP_ID


def sessions_path() -> Path:
    return data_dir() / "sessions.jsonl"


def open_path() -> Path:
    return data_dir() / "sessions-open.json"


def history_path() -> Path:
    return data_dir() / "history.jsonl"


def programs_path() -> Path:
    return data_dir() / "programs.json"


def closes_path() -> Path:
    return data_dir() / "close-for-games.json"


def closes_log_path() -> Path:
    return data_dir() / "close-for-games.log"


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
    vram_mib: int = 0               # the board's peak VRAM in use
    cpu: float = 0.0                # the board's peak CPU load, percent of all cores


@dataclass
class Board:
    ram_mib: int = 0
    ram_total_mib: int = 0
    gtt_mib: int = 0
    swap_mib: int = 0
    swap_total_mib: int = 0
    pressure: float = 0.0
    vram_mib: int = 0
    cpu: float = 0.0


@dataclass
class Point:
    """One minute of the history: its start and the minute's peaks."""
    t: float
    ram_mib: int = 0
    gtt_mib: int = 0
    swap_mib: int = 0
    pressure: float = 0.0
    vram_mib: int = 0
    cpu: float = 0.0


@dataclass
class Stats:
    """One program, over every run the watcher saw."""
    program: str
    game: bool = False              # a Steam game, or Steam itself: never closed for a game
    runs: int = 0
    peak_mib: int = 0
    mib_seconds: float = 0.0        # its memory over time, for the average
    seconds: float = 0.0
    killed: int = 0                 # ended by a lack of memory
    last: float = 0.0

    @property
    def average_mib(self) -> int:
        return int(self.mib_seconds / self.seconds) if self.seconds else 0


# --- Reading ---------------------------------------------------------------------------------------------------

def cpu_times(proc_root: Path = Path("/proc")) -> tuple[int, int]:
    """All cores' busy and total time so far (the "cpu" line of /proc/stat, idle and iowait as idle); (0, 0) when
    it cannot be read."""
    try:
        fields = [int(v) for v in (proc_root / "stat").read_text().splitlines()[0].split()[1:]]
    except (OSError, ValueError, IndexError):
        return 0, 0
    total = sum(fields[:8])                     # guest time is counted in user time already
    return total - sum(fields[3:5]), total


def cpu_load(before: tuple[int, int], now: tuple[int, int]) -> float:
    """The CPU load between two cpu_times(), in percent."""
    busy, total = now[0] - before[0], now[1] - before[1]
    return round(100.0 * busy / total, 1) if total > 0 else 0.0


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
                 gtt_mib=usage.gtt_used_mib or 0, vram_mib=usage.vram_used_mib or 0,
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


def is_game(unit: str) -> bool:
    """A Steam game's unit, a shortcut's too (the emulators' games): app-steam-app<number>-<n>.scope."""
    return re.fullmatch(r"steam-app\d+", desktop_id(unit)) is not None


def never_closed(unit: str) -> bool:
    """Steam and its games: closing them for a game would end the game."""
    return is_game(unit) or desktop_id(unit) == "steam"


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


def program_name(unit: str, steam_dir: Path | None = None, dirs: tuple[Path, ...] | None = None) -> str:
    """A unit's name for people: a Steam game's name, the Name of the app's desktop file, else the app's ID."""
    app = desktop_id(unit)
    match = re.fullmatch(r"steam-app(\d+)", app)
    if match:
        return steam_name(int(match.group(1)), steam_dir) or f"Steam game {match.group(1)}"
    for folder in DESKTOP_DIRS if dirs is None else dirs:
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
        return CRASHED if journal([*since, f"COREDUMP_USER_UNIT={session.unit}"]).strip() else CLOSED
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


def read_history(path: Path | None = None, since: float = 0.0) -> list[Point]:
    out = []
    try:
        lines = (path or history_path()).read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        try:
            point = Point(**json.loads(line))
        except (ValueError, TypeError):
            continue
        if point.t >= since:
            out.append(point)
    return out


def write_point(point: Point, path: Path | None = None) -> None:
    """Adds the point and keeps the last HISTORY_S."""
    path = path or history_path()
    kept = read_history(path, point.t - HISTORY_S) + [point]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(asdict(p)) + "\n" for p in kept), encoding="utf-8")
    tmp.replace(path)


def read_stats(path: Path | None = None) -> dict[str, Stats]:
    try:
        data = json.loads((path or programs_path()).read_text(encoding="utf-8"))
        return {name: Stats(**value) for name, value in data.items()}
    except (OSError, ValueError, TypeError, AttributeError):
        return {}


def write_stats(stats: dict[str, Stats], path: Path | None = None) -> None:
    path = path or programs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({name: asdict(s) for name, s in stats.items()}), encoding="utf-8")
    tmp.replace(path)


def read_closes(path: Path | None = None) -> set[str]:
    """The programs marked to close for games, by name."""
    try:
        return {str(name) for name in json.loads((path or closes_path()).read_text(encoding="utf-8"))}
    except (OSError, ValueError, TypeError):
        return set()


def write_closes(names: set[str], path: Path | None = None) -> None:
    path = path or closes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(names)), encoding="utf-8")


def _stop(unit: str) -> int:
    try:
        return subprocess.run(["systemctl", "--user", "--no-block", "stop", unit], capture_output=True,
                              timeout=30, check=False).returncode
    except (OSError, subprocess.SubprocessError):
        return 1


def _kill(unit: str) -> int:
    try:
        return subprocess.run(["systemctl", "--user", "kill", "--signal=SIGKILL", unit], capture_output=True,
                              timeout=30, check=False).returncode
    except (OSError, subprocess.SubprocessError):
        return 1


def _notify(summary: str, body: str, open_app: bool = False) -> None:
    """A desktop notification through notify-send that stays until clicked; with *open_app*, a button that opens the
    window. notify-send waits for the button, so it runs on its own, in a shell that starts the app."""
    from . import APP_NAME, ROOT
    args = ["notify-send", "--app-name", APP_NAME, "--icon", str(ROOT / "images" / f"{APP_ID}-128.png"),
            "--urgency", "critical", "--expire-time", "0", summary, body]
    if open_app:
        args += ["--action", "open=Open Memory Manager"]
        command = (f'[ "$({shlex.join(args)})" = open ] && cd {shlex.quote(str(ROOT))} && '
                   f"exec {shlex.quote(sys.executable)} -m vram_manager")
        args = ["sh", "-c", command]
    try:
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError:
        pass


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
    history: Path | None = None
    programs: Path | None = None
    closes: Path | None = None
    closes_log: Path | None = None
    stopper: Callable[[str], int] = _stop
    killer: Callable[[str], int] | None = None      # _kill, looked up at the start (tests replace it)
    notifier: Callable[..., None] | None = None     # _notify, the same

    def __post_init__(self) -> None:
        self.record = self.record or sessions_path()
        self.open_file = self.open_file or open_path()
        self.history = self.history or history_path()
        self.programs = self.programs or programs_path()
        self.closes = self.closes or closes_path()
        self.closes_log = self.closes_log or closes_log_path()
        self.killer = self.killer or _kill
        self.notifier = self.notifier or _notify
        self.stats = read_stats(self.programs)
        self.point: Point | None = None
        self.first = True                       # the first look: a game that runs already closes nothing
        self.closed: set[str] = set()           # the units stopped for a game
        self.ended: set[str] = set()            # the games ended for a memory stall
        self.crashed: set[str] = set()          # the games whose crash was told already
        self.stall_since: float | None = None   # since when the memory pressure is at STALL_PERCENT or more
        self.crash_seen = self.clock()          # the journal is read for crashes from here on
        self.boot = boot_id(self.proc_root)
        self.cpu = cpu_times(self.proc_root)    # the CPU load is the busy share since the last look
        try:
            left = {k: Session(**v) for k, v in json.loads(self.open_file.read_text(encoding="utf-8")).items()}
        except (OSError, ValueError, TypeError):
            left = {}
        for unit, session in left.items():
            if session.boot_id == self.boot:
                self.open[unit] = session
            elif session.own_mib >= MIN_MIB or is_game(unit):
                session.ended, session.end = RESTARTED, session.end or session.start
                write_session(session, self.record)
        self.save_open()

    def save_open(self) -> None:
        self.open_file.parent.mkdir(parents=True, exist_ok=True)
        self.open_file.write_text(json.dumps({k: asdict(v) for k, v in self.open.items()}), encoding="utf-8")

    def tick(self) -> None:
        board = read_board(self.sys_root, self.proc_root)
        cpu, self.cpu = self.cpu, cpu_times(self.proc_root)
        board.cpu = cpu_load(cpu, self.cpu)
        programs = read_programs(self.folder)
        now = self.clock()
        started_game = ""
        for unit, (mib, kills) in programs.items():
            session = self.open.get(unit)
            if session is None:
                session = self.open[unit] = Session(unit, program_name(unit, self.steam_dir), now, self.boot)
                stats = self.stats.setdefault(session.program, Stats(session.program, never_closed(unit)))
                stats.runs += 1
                if is_game(unit) and not self.first:
                    started_game = session.program
            stats = self.stats.setdefault(session.program, Stats(session.program, never_closed(unit)))
            stats.mib_seconds += mib * max(now - session.end, 0) if session.end else 0
            stats.seconds += max(now - session.end, 0) if session.end else 0
            stats.peak_mib, stats.last = max(stats.peak_mib, mib), now
            session.own_mib = max(session.own_mib, mib)
            session.oom_kills = kills
            session.ram_mib = max(session.ram_mib, board.ram_mib)
            session.gtt_mib = max(session.gtt_mib, board.gtt_mib)
            session.swap_mib = max(session.swap_mib, board.swap_mib)
            session.pressure = max(session.pressure, board.pressure)
            session.vram_mib, session.cpu = max(session.vram_mib, board.vram_mib), max(session.cpu, board.cpu)
            session.swap_total_mib, session.ram_total_mib = board.swap_total_mib, board.ram_total_mib
            session.end = now
        for unit in [u for u in self.open if u not in programs]:
            session = self.open.pop(unit)
            session.end = now
            session.ended = ending(session, self.journal)
            if session.ended == CLOSED and unit in self.closed:
                session.ended = CLOSED_FOR_GAME
            if unit in self.ended:
                session.ended = STALLED
            if session.ended == CRASHED and unit not in self.crashed:
                self.tell_crash(session)            # missed while it ran
            self.closed.discard(unit)
            self.ended.discard(unit)
            self.crashed.discard(unit)
            if session.ended in SHORT and session.program in self.stats:
                self.stats[session.program].killed += 1
            if session.own_mib >= MIN_MIB or session.ended != CLOSED or is_game(unit):
                write_session(session, self.record)
        if started_game:
            self.close_for(started_game)
        games = [u for u in self.open if is_game(u)]
        if games:
            self.watch_crashes(games, now)
        self.watch_stall(games, board, now)
        self.first = False
        self.add_point(board, now)
        self.save_open()

    def close_for(self, game: str) -> None:
        """Stops each running program marked to close for games, and says so in CLOSES_LOG."""
        marked = read_closes(self.closes)
        for unit, session in self.open.items():
            if session.program in marked and not never_closed(unit) and unit not in self.closed:
                code = self.stopper(unit)
                said = "Closed" if code == 0 else f"Could not close (exit code {code})"
                if code == 0:
                    self.closed.add(unit)
                stamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(self.clock()))
                self.closes_log.parent.mkdir(parents=True, exist_ok=True)
                with self.closes_log.open("a", encoding="utf-8") as log:
                    log.write(f"{stamp} {said} {session.program} for {game}.\n")

    def watch_crashes(self, games: list[str], now: float) -> None:
        """A crash of a running game, told at once: systemd-coredump's first line names the process, the game's
        cgroup holds it while the dump is written."""
        text = self.journal(["-b", "--since", f"@{int(self.crash_seen)}", "-t", "systemd-coredump"])
        self.crash_seen = now - SAMPLE_S                  # a line logged during this look is read again next time
        for match in CRASH.finditer(text):
            pid = match.group(1)
            for unit in games:
                if unit not in self.crashed and self.holds(unit, pid):
                    self.tell_crash(self.open[unit])

    def holds(self, unit: str, pid: str) -> bool:
        if self.folder is None:
            return False
        try:
            return any(pid in procs.read_text().split() for procs in (self.folder / unit).rglob("cgroup.procs"))
        except OSError:
            return False

    def tell_crash(self, session: Session) -> None:
        self.crashed.add(session.unit)
        short = session.pressure >= STALL_PERCENT or (
            session.swap_total_mib and session.swap_mib >= session.swap_total_mib * SWAP_FULL)
        figures = (f"The board waited for memory {session.pressure:.0f}% of the time at most, and the swap held "
                   f"{system.mib_text(session.swap_mib)} of {system.mib_text(session.swap_total_mib)}.")
        self.notifier(f"{session.program} crashed",
                      "The crash report takes a moment, then the game closes. " + figures
                      + (" Memory was short, so watch the learning steps." if short else
                         " Memory was not short, so no memory setting points to a change."))

    def watch_stall(self, games: list[str], board: Board, now: float) -> None:
        """The board stalls for memory while a game runs: after STALL_S seconds, the game is ended and told."""
        if not games or board.pressure < STALL_PERCENT:
            self.stall_since = None
            return
        if self.stall_since is None:
            self.stall_since = now
            return
        if now - self.stall_since < STALL_S:
            return
        self.stall_since = None
        for unit in games:
            if unit in self.ended:
                continue
            session = self.open[unit]
            code = self.killer(unit)
            if code != 0:
                continue
            self.ended.add(unit)
            self.notifier(f"{session.program} was ended",
                          f"The board waited for memory {board.pressure:.0f}% of the time for {STALL_S} s, and froze. "
                          "Memory Manager ended the game to free the board. Its learning steps have a change to try.",
                          open_app=True)

    def add_point(self, board: Board, now: float) -> None:
        """The minute's peaks; a finished minute goes to HISTORY, and the statistics with it."""
        if self.point is not None and now - self.point.t >= POINT_S:
            write_point(self.point, self.history)
            write_stats(self.stats, self.programs)
            self.point = None
        if self.point is None:
            self.point = Point(now)
        p = self.point
        p.ram_mib, p.gtt_mib = max(p.ram_mib, board.ram_mib), max(p.gtt_mib, board.gtt_mib)
        p.swap_mib, p.pressure = max(p.swap_mib, board.swap_mib), max(p.pressure, board.pressure)
        p.vram_mib, p.cpu = max(p.vram_mib, board.vram_mib), max(p.cpu, board.cpu)

    def stop(self) -> None:
        """The watcher stops (log out, shut down): the open sessions are written as still running then."""
        for unit, session in self.open.items():
            if session.own_mib >= MIN_MIB or is_game(unit):
                session.ended = SESSION_ENDED
                write_session(session, self.record)
        self.open.clear()
        self.save_open()
        if self.point is not None:
            write_point(self.point, self.history)
        write_stats(self.stats, self.programs)


# --- What the learning steps write (learn.py) ----------------------------------------------------------------

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
