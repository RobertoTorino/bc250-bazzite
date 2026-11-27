# SPDX-License-Identifier: GPL-3.0-or-later
"""The sessions' watcher with a fake /sys, /proc, app.slice and journal: what makes a session, how it ended (the
journal lines are the ones the owner's board logged on 26-11-2026, and systemd-oomd's own message forms), the board
left during a session, the program names, and the proposal."""

from pathlib import Path

import pytest

from vram_manager import swap, watch
from vram_manager.watch import Session

MIB = 1024 * 1024
UNIT = "app-steam-app3880967987-461439.scope"
CGROUP = "/user.slice/user-1000.slice/user@1000.service/app.slice"


def program(folder: Path, unit: str, mib: int, swap_mib: int = 0, kills: int = 0) -> None:
    path = folder / unit
    path.mkdir(parents=True, exist_ok=True)
    (path / "memory.current").write_text(f"{mib * MIB}\n")
    (path / "memory.swap.current").write_text(f"{swap_mib * MIB}\n")
    (path / "memory.events").write_text(f"low 0\nhigh 0\nmax 0\noom 0\noom_kill {kills}\noom_group_kill 0\n")


def board(proc_root: Path, swap_free_kb: int, pressure: float = 0.0) -> None:
    (proc_root / "meminfo").write_text("MemTotal:        9882080 kB\nMemAvailable:     500000 kB\n"
                                       f"SwapTotal:       4939772 kB\nSwapFree:        {swap_free_kb} kB\n")
    (proc_root / "pressure").mkdir(exist_ok=True)
    (proc_root / "pressure/memory").write_text(f"some avg10=50.00 avg60=1.00 avg300=0.06 total=1\n"
                                               f"full avg10={pressure:.2f} avg60=0.00 avg300=0.06 total=1\n")


class Journal:
    def __init__(self, oomd: str = "", kernel: str = "", coredump: str = "", signal: str = "", unit: str = UNIT):
        self.oomd, self.kernel, self.coredump, self.signal, self.calls = oomd, kernel, coredump, signal, []
        self.unit = unit                    # the unit the crash dump names
        self.crash = ""                     # systemd-coredump's first line, at the crash

    def __call__(self, args):
        self.calls.append(args)
        if "systemd-coredump" in args:
            return self.crash
        if any(a.startswith("COREDUMP_USER_UNIT=") for a in args):
            if f"COREDUMP_USER_UNIT={self.unit}" not in args:
                return ""
            return self.signal if "--output-fields=COREDUMP_SIGNAL_NAME" in args else self.coredump
        return self.oomd if "systemd-oomd.service" in args else self.kernel if "-k" in args else ""


@pytest.fixture(autouse=True)
def no_desktop_files(monkeypatch):
    """The names come from the unit alone: the desktop files of the machine that runs the tests stay out."""
    monkeypatch.setattr(watch, "DESKTOP_DIRS", ())


def make(tmp_path, sys_root, proc_root, journal=None, clock=lambda: 1000.0):
    folder = tmp_path / "cgroup" / CGROUP.lstrip("/")
    folder.mkdir(parents=True, exist_ok=True)
    return folder, watch.Watcher(sys_root, proc_root, folder, None, tmp_path / "sessions.jsonl",
                                 tmp_path / "open.json", journal or Journal(), clock)


def test_a_program_that_took_a_gib_is_a_session(tmp_path, sys_root, proc_root):
    board(proc_root, swap_free_kb=2000000, pressure=12.5)
    (proc_root / "stat").write_text("cpu  100 0 100 800 0 0 0 0 0 0\n")
    folder, w = make(tmp_path, sys_root, proc_root)
    (proc_root / "stat").write_text("cpu  250 0 150 900 0 0 0 0 0 0\n")      # 200 of 300 busy since
    program(folder, UNIT, 6000, swap_mib=1500)
    program(folder, "app-org.kde.konsole-423093.scope", 50)      # too small to be a session
    w.tick()
    board(proc_root, swap_free_kb=4000000, pressure=3.0)          # the peaks stay
    w.tick()
    for unit in (UNIT, "app-org.kde.konsole-423093.scope"):
        for f in (folder / unit).iterdir():
            f.unlink()
        (folder / unit).rmdir()
    w.tick()
    [s] = watch.read_sessions(tmp_path / "sessions.jsonl")
    assert (s.unit, s.ended, s.own_mib, s.pressure, s.boot_id) == (UNIT, watch.CLOSED, 7500, 12.5, "boot-1")
    assert (s.ram_mib, s.gtt_mib, s.swap_mib, s.swap_total_mib) == (9162, 280, 2870, 4823)
    assert (s.vram_mib, s.cpu) == (924, 66.7)                     # the VRAM in use, the CPU load's peak
    assert s.program == "Steam game 3880967987"                    # no Steam folder in the test


def end(folder: Path, unit: str) -> None:
    for f in (folder / unit).iterdir():
        f.unlink()
    (folder / unit).rmdir()


def test_a_kernel_kill_with_the_swap_full(tmp_path, sys_root, proc_root):
    """The owner's board, 26-11-2026 12:06: shadPS4 killed with the zram full."""
    board(proc_root, swap_free_kb=0)
    kernel = ("oom-kill:constraint=CONSTRAINT_NONE,nodemask=(null),cpuset=/,mems_allowed=0,global_oom,"
              f"task_memcg={CGROUP}/{UNIT},task=shadPS4:Main,pid=461468,uid=1000\n")
    journal = Journal(kernel=kernel)
    folder, w = make(tmp_path, sys_root, proc_root, journal)
    program(folder, UNIT, 7262)
    w.tick()
    end(folder, UNIT)
    w.tick()
    assert watch.read_sessions(tmp_path / "sessions.jsonl")[-1].ended == watch.KILLED_SWAP
    assert ["-b", "--since", "@1000", "-k"] in journal.calls


def test_a_kernel_kill_with_the_gpu_borrowing_the_ram(tmp_path, sys_root, proc_root):
    """The owner's board, 25-11-2026 20:35: the GPU borrowed 7.9 GB, swap left; the oom_kill count tells it."""
    board(proc_root, swap_free_kb=1967624)
    (sys_root / "class/drm/card1/device/mem_info_gtt_used").write_text(f"{7744 * MIB}\n")
    folder, w = make(tmp_path, sys_root, proc_root)
    program(folder, "app-kyty-1.scope", 2000, kills=1)
    w.tick()
    end(folder, "app-kyty-1.scope")
    w.tick()
    assert watch.read_sessions(tmp_path / "sessions.jsonl")[-1].ended == watch.KILLED_GPU


def test_the_guard_ending_a_program(tmp_path, sys_root, proc_root):
    board(proc_root, swap_free_kb=400000)
    path = f"{CGROUP}/{UNIT}"
    for line, ended in ((f"Marked {path} for killing due to memory used (9.1G) / total (9.4G) and swap used (4.5G) "
                         "/ total (4.7G) being more than 90.00%", watch.GUARD_SWAP),
                        (f"Memory pressure for {path} is 71.20% > 60.00% for > 10s with reclaim activity",
                         watch.GUARD_PRESSURE)):
        folder, w = make(tmp_path, sys_root, proc_root, Journal(oomd=line + "\nKilled " + path + "\n"))
        program(folder, UNIT, 3000)
        w.tick()
        end(folder, UNIT)
        w.tick()
        assert watch.read_sessions(tmp_path / "sessions.jsonl")[-1].ended == ended


def test_a_session_open_at_a_new_boot_and_at_the_end(tmp_path, sys_root, proc_root):
    board(proc_root, swap_free_kb=0)
    folder, w = make(tmp_path, sys_root, proc_root)
    program(folder, UNIT, 7000)
    w.tick()
    (proc_root / "sys/kernel/random/boot_id").write_text("boot-2\n")            # the board froze and restarted
    end(folder, UNIT)
    folder, w = make(tmp_path, sys_root, proc_root)
    assert watch.read_sessions(tmp_path / "sessions.jsonl")[-1].ended == watch.RESTARTED
    program(folder, UNIT, 2000)
    w.tick()
    _folder, again = make(tmp_path, sys_root, proc_root)                       # the watcher restarted: goes on
    assert list(again.open) == [UNIT]
    again.stop()
    assert watch.read_sessions(tmp_path / "sessions.jsonl")[-1].ended == watch.SESSION_ENDED
    assert again.open == {}


def test_only_the_last_sessions_are_kept(tmp_path):
    path = tmp_path / "sessions.jsonl"
    for n in range(watch.KEEP + 5):
        watch.write_session(Session(f"u{n}", "p", n, "b"), path)
    sessions = watch.read_sessions(path)
    assert len(sessions) == watch.KEEP and sessions[-1].unit == f"u{watch.KEEP + 4}"
    path.write_text(path.read_text() + "not json\n")
    assert len(watch.read_sessions(path)) == watch.KEEP


def test_names(tmp_path):
    assert watch.desktop_id("app-org.kde.konsole-423093.scope") == "org.kde.konsole"
    assert watch.desktop_id("app-code@d2e78b11f0da4a4ba6a0dfbeedadb34c.service") == "code"
    assert watch.desktop_id("app-flatpak-com.google.Chrome-1803611865.scope") == "com.google.Chrome"
    assert watch.desktop_id("app-bc250\\x2dshadps4\\x2dmanager-12.scope") == "bc250-shadps4-manager"
    apps = tmp_path / "applications"
    apps.mkdir()
    (apps / "code.desktop").write_text("[Desktop Entry]\nName=Visual Studio Code\nExec=code\n")
    assert watch.program_name("app-code-100435.scope", None, (apps,)) == "Visual Studio Code"
    assert watch.program_name("app-org.kde.konsole-1.scope", None, (apps,)) == "org.kde.konsole"
    steam = tmp_path / "Steam"
    (steam / "steamapps").mkdir(parents=True)
    (steam / "steamapps/appmanifest_1091500.acf").write_text('"AppState"\n{\n\t"appid"\t\t"1091500"\n'
                                                              '\t"name"\t\t"Cyberpunk 2077"\n}\n')
    assert watch.program_name("app-steam-app1091500-77.scope", steam, (apps,)) == "Cyberpunk 2077"


def test_the_app_slice_comes_from_the_watchers_own_cgroup(tmp_path):
    (tmp_path / "self").mkdir()
    (tmp_path / "self/cgroup").write_text(f"0::{CGROUP}/bc250-memory-watch.service\n")
    assert watch.app_slice(tmp_path, Path("/sys/fs/cgroup")) == Path("/sys/fs/cgroup" + CGROUP)
    (tmp_path / "self/cgroup").write_text("0::/system.slice/x.service\n")
    assert watch.app_slice(tmp_path) is None


def test_what_the_learning_steps_write():
    assert watch.gtt_pages(9650) == (9650 - 2048) * 256
    assert watch.bigger_zram(swap.Setup()) == "ram"                 # Bazzite's own is half the RAM
    assert watch.bigger_zram(swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=180)) == "ram * 1.5"
    assert watch.bigger_zram(swap.Setup(swap.ZRAM, "ram * 2", "zstd", swappiness=180)) == ""


def test_the_cpu_load(tmp_path):
    """The busy share of all cores between two looks; idle and iowait count as idle."""
    (tmp_path / "stat").write_text("cpu  100 0 100 700 100 0 0 0 0 0\ncpu0 1 1 1 1 1 0 0 0 0 0\n")
    before = watch.cpu_times(tmp_path)
    assert before == (200, 1000)
    (tmp_path / "stat").write_text("cpu  250 0 150 1000 200 0 0 0 0 0\n")
    assert watch.cpu_load(before, watch.cpu_times(tmp_path)) == 33.3
    assert watch.cpu_times(tmp_path / "none") == (0, 0) and watch.cpu_load((0, 0), (0, 0)) == 0.0


class Clock:
    def __init__(self, now: float = 1000.0):
        self.now = now

    def __call__(self) -> float:
        return self.now


def test_the_history_and_the_programs(tmp_path, sys_root, proc_root):
    """One point a minute with the minute's peaks, kept for 24 hours; each program's runs, peak and average."""
    board(proc_root, swap_free_kb=4000000, pressure=5.0)
    clock = Clock()
    folder, w = make(tmp_path, sys_root, proc_root, clock=clock)
    program(folder, "app-code-1.scope", 2000)
    for _ in range(31):                         # one minute and two seconds, a look every two seconds
        w.tick()
        clock.now += 2
    program(folder, "app-code-1.scope", 4000)
    w.tick()
    end(folder, "app-code-1.scope")
    clock.now += 2
    w.tick()
    w.stop()
    points = watch.read_history(watch.history_path())
    assert [p.t for p in points] == [1000.0, 1060.0] and points[0].pressure == 5.0 and points[0].swap_mib == 917
    stats = watch.read_stats(watch.programs_path())["code"]
    assert (stats.runs, stats.peak_mib, stats.game, stats.killed) == (1, 4000, False, 0)
    assert 2000 <= stats.average_mib <= 2100
    old = watch.Point(1000.0 - watch.HISTORY_S - 1)
    path = tmp_path / "h.jsonl"
    watch.write_point(old, path)
    watch.write_point(watch.Point(1000.0), path)
    assert [p.t for p in watch.read_history(path)] == [1000.0]       # a point older than 24 hours goes


def test_marked_programs_close_when_a_game_starts(tmp_path, sys_root, proc_root):
    """Only marked programs, never Steam or a game; a game that runs at the watcher's start closes nothing."""
    board(proc_root, swap_free_kb=4000000)
    stopped = []
    folder, w = make(tmp_path, sys_root, proc_root)
    w.stopper = lambda unit: stopped.append(unit) or 0
    watch.write_closes({"code", "steam", "Steam game 1"}, watch.closes_path())
    for unit in ("app-code-1.scope", "app-org.kde.konsole-2.scope", "app-steam@autostart.service",
                 "app-steam-app1-3.scope"):
        program(folder, unit, 1500)
    w.tick()
    assert stopped == []                                    # the game ran already
    program(folder, "app-steam-app3880967987-461439.scope", 3000)
    w.tick()
    assert stopped == ["app-code-1.scope"]
    log = watch.closes_log_path().read_text()
    assert log.endswith(" Closed code for Steam game 3880967987.\n")
    end(folder, "app-code-1.scope")
    w.tick()
    assert watch.read_sessions(tmp_path / "sessions.jsonl")[-1].ended == watch.CLOSED_FOR_GAME
    assert w.stats["Steam game 1"].game and w.stats["steam"].game and not w.stats["code"].game


def test_a_game_is_a_session_whatever_its_size_and_a_crash_says_so(tmp_path, sys_root, proc_root):
    """The owner's board, 26-11-2026: PS2 Lumines Plus took 1001 MiB and was left out; shadPS4 stopped on a trap,
    dumped core for 36 s, and was written as Closed."""
    folder, w = make(tmp_path, sys_root, proc_root, Journal(coredump="Process 158297 (shadPS4:Main) of user 1000 "
                                                                      "dumped core."))
    small = "app-steam-app2964377542-1.scope"
    program(folder, small, 1001)
    program(folder, UNIT, 6000)
    program(folder, "app-org.kde.konsole-1.scope", 900)          # not a game, too small: no session
    w.tick()
    for unit in (small, UNIT, "app-org.kde.konsole-1.scope"):
        end(folder, unit)
    w.tick()
    sessions = {s.unit: s.ended for s in watch.read_sessions(tmp_path / "sessions.jsonl")}
    assert sessions == {small: watch.CLOSED, UNIT: watch.CRASHED}


class Clock2:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_a_crash_is_told_at_once_with_the_memory_figures(tmp_path, sys_root, proc_root):
    """systemd-coredump names the process the moment it crashes; the game's cgroup holds it during the dump."""
    board(proc_root, swap_free_kb=3000000, pressure=9.0)
    journal = Journal()
    folder, w = make(tmp_path, sys_root, proc_root, journal)
    told = []
    w.notifier = lambda summary, body, open_app=False: told.append((summary, body, open_app))
    program(folder, UNIT, 6000)
    (folder / UNIT / "cgroup.procs").write_text("158297\n")
    w.tick()
    assert told == []
    journal.crash = "Process 158297 (shadPS4:Main) of user 1000 terminated abnormally with signal 5/TRAP, processing..."
    w.tick()
    w.tick()                                                 # told once
    assert len(told) == 1 and told[0][0] == "Steam game 3880967987 crashed" and not told[0][2]
    assert told[0][1].startswith("shadPS4:Main ended on SIGTRAP. The crash report takes a moment, then the game "
                                 "closes.")
    assert "Memory was not short, so no memory setting points to a change." in told[0][1]
    assert w.open[UNIT].crash == "shadPS4:Main, SIGTRAP"
    assert ["-b", "--since", "@998", "-t", "systemd-coredump"] in journal.calls


def test_a_memory_stall_ends_the_game_and_tells_it(tmp_path, sys_root, proc_root):
    """The pressure at STALL_PERCENT or more for STALL_S seconds while a game runs: SIGKILL, then a notification
    with a button that opens the window; the session ends as a memory stall. Other programs stay."""
    clock = Clock2()
    board(proc_root, swap_free_kb=100000, pressure=55.0)
    folder, w = make(tmp_path, sys_root, proc_root, clock=clock)
    told, killed = [], []
    w.notifier = lambda summary, body, open_app=False: told.append((summary, open_app))
    w.killer = lambda unit: killed.append(unit) or 0
    program(folder, UNIT, 7000)
    program(folder, "app-code-1.scope", 1500)
    w.tick()
    clock.now += 6
    w.tick()
    assert killed == []                                      # not long enough yet
    clock.now += 5
    w.tick()
    assert killed == [UNIT] and told == [("Steam game 3880967987 was ended", True)]
    end(folder, UNIT)
    clock.now += 2
    w.tick()
    [s] = watch.read_sessions(tmp_path / "sessions.jsonl")
    assert (s.unit, s.ended) == (UNIT, watch.STALLED) and s.ended in watch.SHORT


def test_no_stall_without_a_game(tmp_path, sys_root, proc_root):
    clock = Clock2()
    board(proc_root, swap_free_kb=100000, pressure=90.0)
    folder, w = make(tmp_path, sys_root, proc_root, clock=clock)
    killed = []
    w.killer = lambda unit: killed.append(unit) or 0
    program(folder, "app-code-1.scope", 1500)
    for _ in range(10):
        w.tick()
        clock.now += 2
    assert killed == []


def test_a_crash_names_the_process_and_where_it_ran(tmp_path, sys_root, proc_root):
    """The owner's board, 27-11-2026: Steam, started from the suite, crashed in the suite's unit. The notification
    said "BC250 Bazzite Suite crashed ... then the game closes"; it names the process and the program it ran under."""
    suite = "app-bc250\\x2dbazzite\\x2dsuite@eefe894827b648518dec67d3a5ca20b4.service"
    journal = Journal(coredump="Process 194263 (steam) of user 1000 dumped core.\n\nModule …", signal="SIGSEGV\n",
                      unit=suite)
    folder, w = make(tmp_path, sys_root, proc_root, journal)
    told = []
    w.notifier = lambda summary, body, open_app=False: told.append((summary, body))
    program(folder, suite, 3579)
    w.tick()
    end(folder, suite)
    w.tick()
    session = watch.read_sessions(tmp_path / "sessions.jsonl")[-1]
    assert (session.ended, session.crash) == (watch.CRASHED, "steam, SIGSEGV")
    assert told[0][0] == "steam crashed"
    assert told[0][1].startswith(f"steam ended on SIGSEGV. It ran under {session.program}, which started it. The "
                                 "board waited")
    assert "game" not in told[0][1]


def test_a_crash_report_without_an_entry_is_empty():
    session = watch.Session(UNIT, "LUMINES", 1000.0, "boot")
    assert watch.crash_report(session, Journal(unit="app-other.scope")) == ""
    assert watch.crash_report(session, Journal(coredump="Process 1 (shadPS4:Main) of user 1000 dumped core.")) == \
        "shadPS4:Main"
