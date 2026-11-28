# SPDX-License-Identifier: GPL-3.0-or-later
"""The profile a game wants: its own choice first, then its manager's, then Steam games'; the managers found from
their run scripts and their shortcuts' tags; and what a profile lacks on a board."""

from __future__ import annotations

from vram_manager import guard, kargs, profiles, swap, system

SHORTCUTS = [
    {"appid": 3880967987, "AppName": "[PS5] ASTRO BOT", "Exe": '"/home/u/.local/bin/bc250-kytyps5-run"',
     "tags": {"0": "PS5", "1": "KytyPS5 Manager"}},
    {"appid": 1111, "AppName": "[PS2] Lumines", "Exe": '"/home/u/.local/bin/bc250-pcsx2-run"',
     "tags": {"0": "PS2", "1": "PCSX2 Manager"}},
    {"appid": 2222, "AppName": "Some program", "Exe": '"/usr/bin/firefox"', "tags": {}},
]


def shortcuts(monkeypatch):
    monkeypatch.setattr(profiles, "_shortcuts", lambda steam_dir: SHORTCUTS if steam_dir else [])
    monkeypatch.setattr(profiles, "_field", lambda item, name, default="": item.get(name, default))


def test_a_game_wants_its_own_choice_then_its_managers_then_steams(monkeypatch, tmp_path):
    shortcuts(monkeypatch)
    steam = tmp_path / "steam"
    choices = profiles.Choices({"kytyps5": "defaults", profiles.STEAM: "games"}, {"[PS2] Lumines": "smooth"})
    assert profiles.wanted("[PS5] ASTRO BOT", 3880967987, steam, choices) == "defaults"
    assert profiles.wanted("[PS2] Lumines", 1111, steam, choices) == "smooth"            # its own choice first
    assert profiles.wanted("Cyberpunk 2077", 1091500, steam, choices) == "games"        # a game of Steam's own
    assert profiles.wanted("Some program", 2222, steam, choices) == ""                  # another shortcut: none
    assert profiles.wanted("[PS2] Other", 1111, steam, profiles.Choices()) == ""        # nothing picked
    assert profiles.wanted("Unknown", None, steam, choices) == ""


def test_the_managers_from_their_run_scripts_and_tags(monkeypatch, tmp_path):
    shortcuts(monkeypatch)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("bc250-kytyps5-run", "bc250-xenia-run", "bc250-vita3k-run", "bc250-board-test"):
        (bin_dir / name).write_text("#!/bin/sh\n")
    apps = tmp_path / "applications"
    apps.mkdir()
    (apps / "bc250-kytyps5.desktop").write_text("[Desktop Entry]\nName=BC-250 KytyPS5 Manager\n")
    (apps / "bc250-xenia-manager.desktop").write_text("[Desktop Entry]\nName=Xenia Manager\n")
    assert profiles.managers(tmp_path / "steam", bin_dir, apps) == {
        "kytyps5": "BC-250 KytyPS5 Manager",            # its menu entry's name before its shortcuts' tag
        "vita3k": "vita3k",                             # neither: the key
        "xenia": "Xenia Manager",
        "pcsx2": "PCSX2 Manager"}                       # no run script, but a shortcut with its tag
    assert profiles.manager_of('"/var/home/u/.local/bin/bc250-shadps4-run"') == "shadps4"
    assert profiles.manager_of("/usr/bin/bc250-shadps4-run-old") == ""


def test_the_choices_are_written_at_once_and_read_back(tmp_path):
    path = tmp_path / "profiles.json"
    profiles.set_choice(path, "managers", "kytyps5", "defaults")
    profiles.set_choice(path, "games", "[PS5] ASTRO BOT", "smooth")
    assert profiles.read_choices(path) == profiles.Choices({"kytyps5": "defaults"}, {"[PS5] ASTRO BOT": "smooth"})
    profiles.set_choice(path, "managers", "kytyps5", "")
    assert profiles.read_choices(path).managers == {}
    path.write_text('{"managers": {"x": "turbo"}, "games": "no"}')
    assert profiles.read_choices(path) == profiles.Choices()                            # nothing usable
    assert profiles.read_choices(tmp_path / "missing.json") == profiles.Choices()


def test_what_a_profile_lacks(sys_root, proc_root, tmp_path):
    memory = system.read_memory(sys_root, proc_root)                                   # the 6 GB split
    games = profiles.Board(memory, 6144, kargs.NextBoot(profiles.SUITE_PAGES), swap.Setup(), guard.BAZZITE)
    assert profiles.lacks("games", games) == []
    assert profiles.lacks("defaults", games) == ["the 512 MB split to CMOS",
                                                  "the kernel default GTT limit (half the RAM) to the next boot's "
                                                  "kernel arguments"]
    pending = profiles.Board(memory, 512, kargs.NextBoot(None), swap.Setup(), guard.BAZZITE)
    assert profiles.lacks("defaults", pending) == []                                   # written, waits for a restart
    locked = profiles.Board(memory, 6144, kargs.NextBoot(error="no rpm-ostree"), swap.Setup(),
                            guard.BAZZITE, block_problem="locked")
    assert profiles.lacks("defaults", locked) == []                                    # nothing can be written


def test_the_ps5_emulator_profile_lacks_its_driver_options_and_the_others_lack_their_removal(sys_root, proc_root):
    memory = system.read_memory(sys_root, proc_root)
    plain = profiles.Board(memory, 512, kargs.NextBoot(profiles.PS5_PAGES), swap.Setup(), guard.BAZZITE)
    assert profiles.lacks(profiles.PS5, plain) == ["the PS5 emulator's GPU driver options to the next boot's kernel "
                                                   "arguments"]
    ps5 = profiles.Board(memory, 512, kargs.NextBoot(profiles.PS5_PAGES, kargs.DRIVER), swap.Setup(), guard.BAZZITE)
    assert profiles.lacks(profiles.PS5, ps5) == []
    assert profiles.lacks("defaults", ps5) == ["the kernel default GTT limit (half the RAM) to the next boot's kernel "
                                               "arguments, without the PS5 emulator's GPU driver options"]
    own = profiles.Board(memory, 512, kargs.NextBoot(None, ("amdgpu.cwsr_enable=1",)), swap.Setup(), guard.BAZZITE)
    assert profiles.lacks("defaults", own) == []                     # an option of another value is not the profile's
