# SPDX-License-Identifier: GPL-3.0-or-later
"""The Programs window with recorded data: the largest first, the marks written at once, Steam and games never
markable, and the graph drawn for the range picked."""

from PyQt6.QtCore import Qt

from vram_manager import watch
from vram_manager.programs_dialog import ProgramsDialog


def test_the_programs_and_their_marks(qapp, tmp_path):
    stats = {"code": watch.Stats("Visual Studio Code", False, 1, 4700, 3100 * 60.0, 60.0, 0, 1),
             "game": watch.Stats("[PS4] LUMINES REMASTERED", True, 3, 7400, 6000 * 60.0, 60.0, 1, 1),
             "chrome": watch.Stats("Google Chrome", False, 2, 1400, 900 * 60.0, 60.0, 0, 1)}
    watch.write_stats(stats, tmp_path / "programs.json")
    for minute in range(10):
        watch.write_point(watch.Point(100000.0 + minute * 60, 8000, 300, 2000, 3.0), tmp_path / "history.jsonl")
    watch.write_session(watch.Session("u", "[PS4] LUMINES REMASTERED", 100000.0, "b", end=100300.0,
                                      ended=watch.KILLED_SWAP), tmp_path / "sessions.jsonl")
    d = ProgramsDialog(None, 9650, tmp_path / "history.jsonl", tmp_path / "programs.json", tmp_path / "sessions.jsonl",
                       tmp_path / "closes.json", clock=lambda: 100600.0)
    t = d.table
    assert [t.item(r, 0).text() for r in range(3)] == ["[PS4] LUMINES REMASTERED", "Visual Studio Code",
                                                       "Google Chrome"]
    assert [t.item(0, c).text() for c in range(1, 6)] == ["3", "7.2 GiB", "5.9 GiB", "1", "Never"]
    assert not t.item(0, 5).flags() & Qt.ItemFlag.ItemIsUserCheckable
    t.item(1, 5).setCheckState(Qt.CheckState.Checked)
    assert watch.read_closes(tmp_path / "closes.json") == {"Visual Studio Code"} and t.item(1, 5).text() == "Close"
    t.item(1, 5).setCheckState(Qt.CheckState.Unchecked)
    assert watch.read_closes(tmp_path / "closes.json") == set()
    assert len(d.graph.points) == 10 and [s.program for s in d.graph.kills] == ["[PS4] LUMINES REMASTERED"]
    d.range_combo.setCurrentIndex(0)
    assert d.graph.end - d.graph.start == 3600
    assert d.graph.top_gib() == 10
    d.resize(900, 720)
    d.show()
    assert not d.grab().isNull()
    d.close()


def test_a_game_picks_its_own_profile(qapp, tmp_path):
    """A game's row has a Profile choice, written at once; Steam's own row and the programs have none."""
    from vram_manager import profiles
    stats = {"game": watch.Stats("[PS5] ASTRO BOT", True, 1, 9000, 0.0, 0.0, 1, 1),
             "steam": watch.Stats("Steam", True, 1, 3500, 0.0, 0.0, 0, 1),
             "code": watch.Stats("Visual Studio Code", False, 1, 2000, 0.0, 0.0, 0, 1)}
    watch.write_stats(stats, tmp_path / "programs.json")
    d = ProgramsDialog(None, 9650, tmp_path / "history.jsonl", tmp_path / "programs.json", tmp_path / "sessions.jsonl",
                       tmp_path / "closes.json", clock=lambda: 100600.0, choices=tmp_path / "profiles.json")
    assert list(d.profile_combos) == ["[PS5] ASTRO BOT"]
    combo = d.profile_combos["[PS5] ASTRO BOT"]
    assert combo.currentText() == "Its manager's"
    combo.setCurrentIndex(combo.findData("defaults"))
    assert profiles.read_choices(tmp_path / "profiles.json").games == {"[PS5] ASTRO BOT": "defaults"}
    combo.setCurrentIndex(0)
    assert profiles.read_choices(tmp_path / "profiles.json").games == {}
    d.close()
