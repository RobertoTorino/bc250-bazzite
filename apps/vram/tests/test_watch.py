# SPDX-License-Identifier: GPL-3.0-or-later
"""The sessions' watcher with a fake /sys, /proc, app.slice and journal: what makes a session, how it ended (the
journal lines are the ones the owner's board logged on 26-11-2026, and systemd-oomd's own message forms), the board
left during a session, the program names, and the proposal."""

from pathlib import Path

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
    def __init__(self, oomd: str = "", kernel: str = ""):
        self.oomd, self.kernel, self.calls = oomd, kernel, []

    def __call__(self, args):
        self.calls.append(args)
        return self.oomd if "systemd-oomd.service" in args else self.kernel if "-k" in args else ""


def make(tmp_path, sys_root, proc_root, journal=None, clock=lambda: 1000.0):
    folder = tmp_path / "cgroup" / CGROUP.lstrip("/")
    folder.mkdir(parents=True, exist_ok=True)
    return folder, watch.Watcher(sys_root, proc_root, folder, None, tmp_path / "sessions.jsonl",
                                 tmp_path / "open.json", journal or Journal(), clock)


def test_a_program_that_took_a_gib_is_a_session(tmp_path, sys_root, proc_root):
    board(proc_root, swap_free_kb=2000000, pressure=12.5)
    folder, w = make(tmp_path, sys_root, proc_root)
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


def done(ended: str, swap_mib: int = 0) -> Session:
    return Session("u", "p", 0, "b", 2000, 9000, 300, swap_mib, 4824, 9650, 20.0, 0, 1, ended)


def test_the_proposal():
    bazzite, ram = swap.Setup(), 9650
    assert watch.propose([done(watch.CLOSED)] * 2, bazzite, ram, 3014656).text == ("A proposal needs 3 sessions. 2 "
                                                                                   "recorded so far.")
    calm = watch.propose([done(watch.CLOSED)] * 3, bazzite, ram, 3014656)
    assert calm == watch.Proposal("No change: none of the last 3 sessions ran out of memory.")
    short = watch.propose([done(watch.CLOSED)] * 2 + [done(watch.KILLED_SWAP)], bazzite, ram, 3014656)
    assert short == watch.Proposal("Proposal from 3 sessions: zram the RAM.", "ram", None)
    zram = swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=180)
    assert watch.propose([done(watch.RESTARTED, swap_mib=4800)] * 3, zram, ram, 3014656).zram_size == "ram * 1.5"
    largest = swap.Setup(swap.ZRAM, "ram * 2", "zstd", swappiness=180)
    assert "Try zswap" in watch.propose([done(watch.GUARD_SWAP)] * 3, largest, ram, None).text
    gpu = watch.propose([done(watch.KILLED_GPU)] * 3, zram, ram, 3014656)
    assert gpu == watch.Proposal("Proposal from 3 sessions: GTT limit 7.4 GiB.", "", watch.gtt_pages(ram))
    assert watch.propose([done(watch.KILLED_GPU)] * 3, zram, ram, watch.gtt_pages(ram)).pages is None
    assert watch.gtt_pages(9650) == (9650 - 2048) * 256
