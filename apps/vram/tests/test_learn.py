# SPDX-License-Identifier: GPL-3.0-or-later
"""The learning rules (owner, 26-11-2026): what points to a change, the comparison of two rounds, and the rounds."""
from dataclasses import asdict

from vram_manager import guard, learn, swap, watch
from vram_manager.watch import Session

RAM = 9650
GAMES = learn.settings(6144, 3014656, swap.Setup(), guard.BAZZITE)


def played(program: str, ended: str = watch.CLOSED, start: float = 100.0, boot: str = "boot-2", swap_mib: int = 1000,
           pressure: float = 10.0, cpu: float = 50.0) -> Session:
    return Session("app-steam-app1-1.scope", program, start, boot, 3000, 8000, 2000, swap_mib, 4823, RAM, pressure, 0, start + 60, ended,
                   vram_mib=5000, cpu=cpu)


def test_a_failed_game_points_at_once_otherwise_three_sessions_and_a_reason():
    """Owner, 26-11-2026: a freeze means something needs adjustment, at once."""
    assert learn.propose([played("A")] * 2, GAMES, RAM, set()) is None
    assert learn.propose([played("A")] * 3, GAMES, RAM, set()) is None
    assert learn.propose([played("A", watch.KILLED_SWAP)], GAMES, RAM, set()).kind == learn.ZRAM
    assert learn.propose([played("A", watch.STALLED, swap_mib=4800)], GAMES, RAM, set()).kind == learn.ZRAM
    assert learn.propose([played("A", watch.CRASHED)], GAMES, RAM, set()) is None      # a crash is no lack of memory


def test_a_full_swap_points_to_one_zram_size_up_with_the_running_compressor_and_swappiness():
    change = learn.propose([played("A"), played("B"), played("LUMINES", watch.KILLED_SWAP)], GAMES, RAM, set(),
                           "lzo-rle", 60)
    assert (change.kind, change.label, change.reason) == (learn.ZRAM, "zram the RAM", "The swap ran full in LUMINES.")
    assert change.value == asdict(swap.Setup(swap.ZRAM, "ram", "lzo-rle", swappiness=60))
    assert change.before == asdict(swap.Setup())
    # A freeze with the swap full counts as well; with zram written, its compressor and swappiness stay.
    zram = learn.settings(6144, 3014656, swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=180), guard.BAZZITE)
    froze = learn.propose([played("A", watch.RESTARTED, swap_mib=4800)] * 3, zram, RAM, set())
    assert froze.value == asdict(swap.Setup(swap.ZRAM, "ram * 1.5", "zstd", swappiness=180))
    # Tried once: not again. The freeze then points to the suite's guard.
    again = learn.propose([played("A", watch.RESTARTED, swap_mib=4800)] * 3, zram, RAM,
                          {(learn.ZRAM, '{"compressor": "zstd", "file_mib": 0, "layout": "zram", "swappiness": 180, '
                                        '"zram_size": "ram * 1.5"}')})
    assert (again.kind, again.value, again.reason) == (learn.GUARD, guard.SUITE, "The board froze while A ran.")


def test_a_gpu_kill_points_to_a_lower_gtt_limit_then_the_guard():
    sessions = [played("A"), played("Hades", watch.KILLED_GPU), played("B")]
    change = learn.propose(sessions, GAMES, RAM, set())
    assert (change.kind, change.value, change.before) == (learn.GTT, watch.gtt_pages(RAM), 3014656)
    assert change.label == "a GTT limit of 7.4 GiB"
    # A limit at or below it already, or the kernel's default: the guard instead.
    low = dict(GAMES, pages=watch.gtt_pages(RAM))
    assert learn.propose(sessions, low, RAM, set()).kind == learn.GUARD
    assert learn.propose(sessions, dict(GAMES, pages=None), RAM, set()).reason == "The kernel ended Hades."
    suite = dict(GAMES, pages=None, guard=guard.SUITE)
    assert learn.propose(sessions, suite, RAM, set()) is None


def test_the_comparison_counts_the_games_of_both_rounds():
    before = [played("LUMINES", watch.KILLED_SWAP, pressure=38), played("Hades"), played("C", pressure=20)]
    after = [played("LUMINES", pressure=9), played("Hades", pressure=5)]
    v = learn.compare(before, after)
    assert v.ready and v.missing == ["C"] and v.sessions == 2        # the failed game was played again
    assert not learn.compare([played("A"), played("B"), played("C")], [played("A")]).ready
    v = learn.compare(before, after + [played("New game")])
    assert v.ready and v.kind == learn.BETTER
    assert v.rows[0] == ("Ended for lack of memory", "1 of 2", "0 of 2", learn.BETTER)
    assert v.rows[1] == ("Waited for memory, peak", "38%", "9%", learn.BETTER)
    assert v.rows[-1][3] == "Context"


def test_equal_endings_go_by_the_wait_and_otherwise_the_change_is_no_better():
    before = [played("A", pressure=20)] * 3
    assert learn.compare(before, [played("A", pressure=12)] * 3).kind == learn.BETTER
    assert learn.compare(before, [played("A", pressure=17)] * 3).kind == learn.SAME
    assert learn.compare(before, [played("A", pressure=26)] * 3).kind == learn.WORSE
    worse = [played("A", watch.KILLED_RAM, pressure=1)] + [played("A", pressure=1)] * 2
    assert learn.compare(before, worse).kind == learn.WORSE      # an ending weighs more than the wait


def test_the_rounds_their_sessions_and_the_state_file(tmp_path):
    path = tmp_path / "learn.json"
    assert learn.read_state(path) is None
    st = learn.State([learn.Round(100.0, GAMES, "boot-1")], "boot-1")
    sessions = [played("old", start=50, boot="boot-0"), played("A", start=150, boot="boot-1"),
                played("B", start=200), played("C", start=300), played("D", start=400)]
    assert [s.program for s in learn.round_sessions(st, sessions, 0)] == ["B", "C", "D"]   # not the write boot's
    code = Session("app-code-1.scope", "Visual Studio Code", 250, "boot-2", 1600)
    assert code not in learn.round_sessions(st, sessions + [code], 0)                     # games only
    assert learn.restart_waits(st, "boot-1") and not learn.restart_waits(st, "boot-2")
    zram = learn.settings(6144, 3014656, swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=60), guard.BAZZITE)
    change = learn.Change(learn.ZRAM, asdict(swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=60)),
                          asdict(swap.Setup()), "The swap ran full in B.", "zram the RAM")
    st.rounds.append(learn.Round(350.0, zram, "boot-2", asdict(change)))
    assert learn.trial(st) == 1 and learn.baseline(st) == 0
    assert [s.program for s in learn.baseline_sessions(st, sessions)] == ["B", "C"]
    learn.write_state(st, path)
    assert learn.read_state(path) == st
    st.rounds[1].verdict = learn.UNDONE
    st.rounds.append(learn.Round(500.0, GAMES, "boot-3"))
    sessions.append(played("E", start=600, boot="boot-4"))
    assert learn.trial(st) is None and learn.baseline(st) == 2
    assert [s.program for s in learn.baseline_sessions(st, sessions)] == ["B", "C", "E"]   # round 1 goes on
    assert learn.tried(st) == {(learn.ZRAM, '{"compressor": "zstd", "file_mib": 0, "layout": "zram", '
                                            '"swappiness": 60, "zram_size": "ram"}')}
    learn.clear_state(path)
    assert not path.exists()
