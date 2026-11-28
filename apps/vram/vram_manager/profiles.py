# SPDX-License-Identifier: GPL-3.0-or-later
"""The profiles, and the profile a game wants (owner, 28-11-2026: "the Memory Manager profile should be auto
activated based on the game/manager", as a service).

A profile is a split, a GTT limit and, for the Smooth profile, a swap layout and the suite's memory guard. values()
gives a profile's values for this board, and lacks() says in words what the board does not have of it yet. The window
writes a profile with them (main_window.py), and the watcher asks them when a game starts (watch.py).

Which profile a game wants (owner, 28-11-2026: per manager, with a per-game override):

    a game picked in the Programs window      the profile picked for that game
    a game of an emulator manager             the profile picked for that manager in the window
    any other Steam game                      the profile picked for Steam games
    nothing picked                            no profile: the game runs with what the board has

An emulator manager's game is a Steam shortcut that starts the manager's run script, bc250-<key>-run in
~/.local/bin. The manager's name is the second tag its shortcuts carry, such as "PCSX2 Manager". The choices are in
CHOICES beside the watcher's records, and every choice starts empty.

The split, the GTT limit and the swap layout take effect at the next boot, and the guard asks for the password. So
the watcher never writes a profile. When a game wants one the board lacks, it says so in a notification once a
boot, with a button that opens the window on that profile's question (owner, 28-11-2026: "notify, offer restart")."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import guard, kargs, swap, system, watch

RECOMMENDED_MB = 6144                   # board-test's recommendation (test 37): fixes framebuffer pin failures
FIRMWARE_MB = 512                       # the split the firmware starts with after a CMOS clear
SUITE_PAGES = 3014656                   # the suite's GTT limit, 11.5 GiB (Board Test, test 37)
PS5_PAGES = 3670016                     # the PS5 emulator profile's GTT limit, 14 GiB (owner's board, 27-11-2026)
PS5 = "ps5"

SMOOTH = "smooth"
SMOOTH_PAGES = object()                 # PROFILES: the Smooth profile's limit, the RAM less watch.SPARE_MIB
SMOOTH_SWAP = swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=swap.SWAPPINESS[swap.ZRAM])

# The profiles (owner, 01-11-2026): both values at once, each written only where it differs. The Smooth profile
# (owner, 26-11-2026) also writes the swap layout and the suite's memory guard. The PS5 emulator profile (owner,
# 27-11-2026, ACTION-LIST row 6) also puts the GPU driver options kargs.DRIVER in, which the others take out again.
# On the owner's board, ASTRO BOT in KytyPS5-Native ran 20 minutes with its split and limit, and three kernel kills
# came with the 6 GB split; the driver options are not tested on a board yet.
PROFILES = {
    "defaults": ("Default profile", FIRMWARE_MB, None),
    "games": ("Games profile", RECOMMENDED_MB, SUITE_PAGES),
    SMOOTH: ("Smooth profile", RECOMMENDED_MB, SMOOTH_PAGES),
    PS5: ("PS5 emulator profile", FIRMWARE_MB, PS5_PAGES),
}
DRIVER_TEXT = "the PS5 emulator's GPU driver options"
SCREEN_NOTE = "Before a big PS5 game, set the screen to 1920x1080."  # 3840x2160 hung the GPU (owner's board, 27-11)
NONE_LABEL = "No profile"               # a choice left empty: the game runs with what the board has
CHOICES = "profiles.json"
RUN_SCRIPT = re.compile(r"(?:^|/)bc250-([a-z0-9]+)-run\"?$")
STEAM = "steam"                         # the choice for Steam's own games, beside the managers'


def split_label(mb: int) -> str:
    text = f"{mb // 1024} GB" if mb >= 1024 else f"{mb} MB"
    return text + ("  (recommended for games)" if mb == RECOMMENDED_MB else "")


def ttm_label(pages: int | None) -> str:
    """A GTT limit in words: its size, or the kernel's default."""
    return f"{system.mib_text(kargs.mib(pages))} GTT limit" if pages else "kernel default GTT limit (half the RAM)"


def zram_compressors(sys_root: Path = Path("/sys")) -> list[str]:
    """What the board's zram device offers; the usual three when no device is there to ask."""
    for path in sorted((sys_root / "block").glob("zram*/comp_algorithm")):
        try:
            names = path.read_text().replace("[", "").replace("]", "").split()
        except OSError:
            continue
        if names:
            return names
    return list(swap.ZRAM_COMPRESSORS)


def driver(key: str) -> bool:
    """Whether a profile wants kargs.DRIVER in the next boot's arguments (the PS5 emulator profile) or out."""
    return key == PS5


def values(key: str, memory: system.Memory, compressors: list[str]) -> tuple[str, int, int | None,
                                                                              swap.Setup | None, str | None]:
    """A profile's name, split and limit, and the swap layout and guard it also writes (None: left as they are).
    The Smooth profile's limit is the RAM the split leaves, less watch.SPARE_MIB."""
    name, mb, pages = PROFILES[key]
    if pages is not SMOOTH_PAGES:
        return name, mb, pages, None, None
    ram = (memory.vram_mib + memory.ram_mib - mb) if memory.vram_mib and memory.ram_mib else (memory.ram_mib or 0)
    setup = SMOOTH_SWAP if SMOOTH_SWAP.compressor in compressors else swap.Setup(
        swap.ZRAM, SMOOTH_SWAP.zram_size, compressors[0], swappiness=SMOOTH_SWAP.swappiness)
    return name, mb, watch.gtt_pages(ram) if ram else None, setup, guard.SUITE


@dataclass
class Board:
    """What the board will have at the next boot, as far as a profile goes."""
    memory: system.Memory
    written_mb: int | None              # the split in CMOS: the one waiting for a restart, else this boot's
    next_boot: kargs.NextBoot
    swap_setup: swap.Setup
    guard: str
    block_problem: str = ""             # why CMOS must not be touched (cmos.board_problem)
    compressors: list[str] = field(default_factory=lambda: list(swap.ZRAM_COMPRESSORS))


def lacks(key: str, board: Board) -> list[str]:
    """What a profile would write, in words: the split (when CMOS can be written and it differs), the limit and the
    GPU driver options in one step (when rpm-ostree works and they differ), and for the Smooth profile the swap layout and the guard where they differ.
    Empty when the board has the profile, or nothing can be written."""
    _name, mb, pages, setup, wanted = values(key, board.memory, board.compressors)
    steps = []
    if not board.block_problem and mb != board.written_mb:
        steps.append(f"the {split_label(mb)} split to CMOS")
    if not board.next_boot.error:
        limit = pages != board.next_boot.pages
        options = bool(kargs.driver_change(driver(key), board.next_boot.driver))
        if limit and options and driver(key):
            steps.append(f"the {ttm_label(pages)} and {DRIVER_TEXT} to the next boot's kernel arguments")
        elif limit and options:
            steps.append(f"the {ttm_label(pages)} to the next boot's kernel arguments, without {DRIVER_TEXT}")
        elif limit:
            steps.append(f"the {ttm_label(pages)} to the next boot's kernel arguments")
        elif options and driver(key):
            steps.append(f"{DRIVER_TEXT} to the next boot's kernel arguments")
        elif options:
            steps.append(f"the next boot's kernel arguments without {DRIVER_TEXT}")
    if setup is not None and setup != board.swap_setup:
        steps.append(f"zram the size of the RAM with vm.swappiness {setup.swappiness} for the next boot")
    if wanted is not None and wanted != board.guard:
        steps.append("the suite's memory guard")
    return steps


# --- The profile a game wants -----------------------------------------------------------------------------------

@dataclass
class Choices:
    managers: dict[str, str] = field(default_factory=dict)     # a manager's key, or STEAM -> a profile's key
    games: dict[str, str] = field(default_factory=dict)        # a game's name, as the watcher names it -> the same


def read_choices(path: Path) -> Choices:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Choices({str(k): str(v) for k, v in data.get("managers", {}).items() if v in PROFILES},
                       {str(k): str(v) for k, v in data.get("games", {}).items() if v in PROFILES})
    except (OSError, ValueError, AttributeError):
        return Choices()


def write_choices(choices: Choices, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(choices), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def set_choice(path: Path, table: str, name: str, profile: str) -> None:
    """One choice written at once: a profile's key, or "" for none."""
    choices = read_choices(path)
    chosen = getattr(choices, table)
    if profile in PROFILES:
        chosen[name] = profile
    else:
        chosen.pop(name, None)
    write_choices(choices, path)


def manager_of(exe: str) -> str:
    """The manager whose run script a shortcut starts: "pcsx2" for "/home/u/.local/bin/bc250-pcsx2-run"."""
    match = RUN_SCRIPT.search(exe.strip())
    return match.group(1) if match else ""


def _shortcuts(steam_dir: Path | None) -> list[dict]:
    if steam_dir is None:
        return []
    try:
        from bc250_core import steam
        return list(steam.shortcuts(steam_dir))
    except Exception:  # noqa: BLE001  (no Steam, or a file Steam is writing: no shortcuts this time)
        return []


def _field(item: dict, name: str, default: object = "") -> object:
    from bc250_core import steam
    return steam.field(item, name, default)


def _desktop_name(key: str, apps_dir: Path) -> str:
    """A manager's name from its menu entry, bc250-<key>-manager.desktop or bc250-<key>.desktop; "" without one."""
    for name in (f"bc250-{key}-manager.desktop", f"bc250-{key}.desktop"):
        try:
            for line in (apps_dir / name).read_text(errors="replace").splitlines():
                if line.startswith("Name="):
                    return line[5:].strip()
        except OSError:
            continue
    return ""


def managers(steam_dir: Path | None, bin_dir: Path, apps_dir: Path | None = None) -> dict[str, str]:
    """The emulator managers to pick a profile for, by key with their names: each run script in *bin_dir*, and each
    manager a Steam shortcut starts. The name is the manager's menu entry's, else its shortcuts' second tag, else the
    key."""
    found = {match.group(1): "" for path in sorted(bin_dir.glob("bc250-*-run"))
             if (match := RUN_SCRIPT.search(path.name))}
    tags: dict[str, str] = {}
    for item in _shortcuts(steam_dir):
        key = manager_of(str(_field(item, "Exe")))
        tag = _field(item, "tags", {})
        if key:
            found.setdefault(key, "")
            if isinstance(tag, dict) and tag.get("1"):
                tags.setdefault(key, str(tag["1"]))
    if apps_dir is None:
        from bc250_core.platform import data_home
        apps_dir = data_home() / "applications"
    return {key: _desktop_name(key, apps_dir) or tags.get(key) or key for key in found}


def wanted(program: str, number: int | None, steam_dir: Path | None, choices: Choices) -> str:
    """The profile's key a game wants: its own choice, else its manager's, else Steam games'; "" for none. *number*
    is the game's Steam appid (a shortcut's too), *program* its name as the watcher names it."""
    if program in choices.games:
        return choices.games[program]
    if number is None:
        return ""
    for item in _shortcuts(steam_dir):
        if int(_field(item, "appid", 0)) & 0xFFFFFFFF == number:
            key = manager_of(str(_field(item, "Exe")))
            return choices.managers.get(key, "") if key else ""     # a shortcut of none of the managers: none
    return choices.managers.get(STEAM, "")


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        return done.returncode, done.stdout, done.stderr
    except FileNotFoundError:
        return kargs.NOT_INSTALLED, "", f"{cmd[0]} is not installed."
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, "", str(exc)


def read_board(pending_mb: int, sys_root: Path = Path("/sys"), proc_root: Path = Path("/proc"),
               etc: Path = Path("/etc"), var: Path = Path("/var"), run=_run) -> Board:
    """The board as the watcher reads it, without a password: the split waiting in CMOS (*pending_mb*, from the
    window's settings; 0 for none) else this boot's, and the next boot's limit, swap layout and guard."""
    from . import cmos
    memory = system.read_memory(sys_root, proc_root)
    return Board(memory, pending_mb or memory.vram_mib, kargs.read_next_boot(run), swap.read_setup(etc, var),
                 guard.read_guard(etc), cmos.board_problem(sys_root), zram_compressors(sys_root))
