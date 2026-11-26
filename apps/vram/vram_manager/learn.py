# SPDX-License-Identifier: GPL-3.0-or-later
"""The learning steps (owner, 26-11-2026): the app learns the settings that suit the games played, one change a round.

    1. Start point     the Games profile, with Bazzite's swap and guard, and recording on
    2. Restart         the start point takes effect
    3. Play and record round 1: SESSIONS_A_ROUND sessions with the start point
    4. Try one change  one change a measurement points to (propose()), written, then the board restarts
    5. Play and compare the same games again; keep the change or undo it (compare()), then back to step 4

When no measurement points to a change, the settings the board runs are the Learned profile. Recording stays on, so
a game that later runs out of memory points to a change again.

The owner's rules (26-11-2026):

    - A round is better with fewer sessions ended by a lack of memory or a freeze, as a share of its sessions.
      When that is equal, with a peak wait for memory WAIT_MARGIN points lower. Otherwise the setting closer to
      the start point stays: the change is undone.
    - A comparison counts only the games played in both rounds, and names the games still missing.
    - Only a setting a measurement points to changes, and a change is tried once. The CPU load is context only.

What points to what (propose(), in this order):

    zram        a session ended with the swap full, or the board froze with it full: one zram size up
    GTT limit   the kernel ended a program while the GPU borrowed half the RAM or more: the RAM less 2 GiB
    guard       the kernel ended a program, or the board froze, with Bazzite's guard: the suite's guard

The split stays at the start point's: nothing measured yet tells when another split is better (Board Test, test 37:
6 GB prevents the framebuffer pin failures).

The state is one JSON file beside the sessions (LEARN): the rounds, each with the time it began, the boot its setting
was written in (the sessions of that boot ran the old one), the settings it ran with, its change and the verdict; and
the boot a written change waits in for a restart. A round's sessions are the recorded ones that began in it, after
its write boot. Standard library and the app's own modules only."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import guard, kargs, swap, system, watch

SESSIONS_A_ROUND = 3
WAIT_MARGIN = 5.0                       # percentage points of the peak wait for memory that count as a difference
ZRAM, GTT, GUARD = "zram", "gtt", "guard"
ENDED_SHORT = (*watch.SHORT, watch.RESTARTED)       # ended by a lack of memory, or the board froze
KILLED = (watch.KILLED_SWAP, watch.KILLED_GPU, watch.KILLED_RAM)
KEPT, UNDONE = "kept", "undone"
BETTER, WORSE, SAME = "Better", "Worse", "Same"


def learn_path() -> Path:
    return watch.data_dir() / "learn.json"


@dataclass
class Round:
    since: float                        # when its setting was written
    settings: dict                      # what the board runs in it: split, pages, swap (a swap.Setup), guard
    boot: str = ""                      # the boot it was written in, "" when it took effect at once
    change: dict | None = None          # a Change, None for the start point and after an undo
    verdict: str = ""                   # a change's: "", KEPT or UNDONE


@dataclass
class State:
    rounds: list[Round] = field(default_factory=list)
    restart_boot: str = ""              # a written change waits for a restart while this boot runs


@dataclass(frozen=True)
class Change:
    kind: str                           # ZRAM, GTT or GUARD
    value: object                       # ZRAM: a swap.Setup as a dict; GTT: pages; GUARD: its key
    before: object                      # the same, as the board has it
    reason: str                         # what was measured, a sentence
    label: str                          # the change in words, "zram the size of the RAM"


@dataclass
class Verdict:
    ready: bool                         # enough sessions, and a game in both rounds
    kind: str                           # BETTER, WORSE or SAME
    rows: list[tuple[str, str, str, str]]   # measured, round before, this round, BETTER/WORSE/SAME or "Context"
    missing: list[str]                  # the games of the round before not played in this one yet
    sessions: int                       # this round's sessions


def settings(split_mb: int | None, pages: int | None, setup: swap.Setup, guard_key: str) -> dict:
    return {"split": split_mb, "pages": pages, "swap": asdict(setup), "guard": guard_key}


# --- The file --------------------------------------------------------------------------------------------------

def read_state(path: Path | None = None) -> State | None:
    """The learning so far; None before step 1, or when the file cannot be read."""
    try:
        data = json.loads((path or learn_path()).read_text(encoding="utf-8"))
        return State([Round(**r) for r in data["rounds"]], data.get("restart_boot", ""))
    except (OSError, ValueError, TypeError, KeyError):
        return None


def write_state(state: State, path: Path | None = None) -> None:
    path = path or learn_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(asdict(state), indent=1), encoding="utf-8")
    tmp.replace(path)


def clear_state(path: Path | None = None) -> None:
    (path or learn_path()).unlink(missing_ok=True)


# --- The rounds ------------------------------------------------------------------------------------------------

def round_sessions(state: State, sessions: list[watch.Session], index: int) -> list[watch.Session]:
    r = state.rounds[index]
    until = state.rounds[index + 1].since if index + 1 < len(state.rounds) else float("inf")
    return [s for s in sessions if r.since <= s.start < until and not (r.boot and s.boot_id == r.boot)]


def trial(state: State) -> int | None:
    """The round whose change waits for a verdict."""
    last = len(state.rounds) - 1
    return last if last >= 0 and state.rounds[last].change and not state.rounds[last].verdict else None


def baseline(state: State) -> int:
    """The last round with settings that stay: the start point, a kept change, or the settings after an undo."""
    for index in range(len(state.rounds) - 1, -1, -1):
        r = state.rounds[index]
        if r.change is None or r.verdict == KEPT:
            return index
    return 0


def baseline_sessions(state: State, sessions: list[watch.Session]) -> list[watch.Session]:
    """The sessions of every settled round with the baseline's settings: an undo goes on with what they recorded."""
    wanted = state.rounds[baseline(state)].settings
    out = []
    for index, r in enumerate(state.rounds):
        if r.settings == wanted and (r.change is None or r.verdict == KEPT):
            out += round_sessions(state, sessions, index)
    return out


def tried(state: State) -> set[tuple[str, str]]:
    return {(r.change["kind"], json.dumps(r.change["value"], sort_keys=True)) for r in state.rounds if r.change}


def restart_waits(state: State, boot: str) -> bool:
    return bool(state.restart_boot) and state.restart_boot == boot


# --- What the measurements point to ----------------------------------------------------------------------------

def _names(sessions: list[watch.Session]) -> str:
    names = list(dict.fromkeys(s.program for s in sessions))
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + f" and {names[-1]}"


def _swap_full(s: watch.Session) -> bool:
    return s.ended in watch.SHORT_OF_SWAP or (s.ended == watch.RESTARTED and bool(s.swap_total_mib)
                                              and s.swap_mib >= s.swap_total_mib * watch.SWAP_FULL)


def propose(sessions: list[watch.Session], now: dict, ram_mib: int, done: set[tuple[str, str]],
            zram_compressor: str = "zstd", swappiness: int | None = None) -> Change | None:
    """The one change the baseline's sessions point to and that was not tried yet; None when they point to none,
    or before SESSIONS_A_ROUND sessions. *now*: the baseline's settings(). A larger zram keeps the compressor and
    vm.swappiness the board has (*zram_compressor*, *swappiness*: the running ones, for Bazzite's own layout)."""
    if len(sessions) < SESSIONS_A_ROUND:
        return None

    def fresh(kind: str, value: object) -> bool:
        return (kind, json.dumps(value, sort_keys=True)) not in done

    setup = swap.Setup(**now["swap"])
    full = [s for s in sessions if _swap_full(s)]
    bigger = watch.bigger_zram(setup)
    if full and bigger:
        if setup.layout == swap.ZRAM:
            new = swap.Setup(swap.ZRAM, bigger, setup.compressor, swappiness=setup.swappiness)
        else:
            keep = swappiness if swappiness is not None else swap.SWAPPINESS[swap.ZRAM]
            new = swap.Setup(swap.ZRAM, bigger, zram_compressor, swappiness=keep)
        if fresh(ZRAM, asdict(new)):
            label = next(lbl for lbl, size, _f in swap.ZRAM_SIZES if size == bigger)
            return Change(ZRAM, asdict(new), asdict(setup), f"The swap ran full in {_names(full)}.",
                          f"zram {label[0].lower() + label[1:]}")
    gpu = [s for s in sessions if s.ended == watch.KILLED_GPU]
    pages = watch.gtt_pages(ram_mib) if ram_mib else None
    if gpu and pages and now["pages"] and now["pages"] > pages and fresh(GTT, pages):
        return Change(GTT, pages, now["pages"], f"The kernel ended {_names(gpu)} while the GPU filled the RAM.",
                      f"a GTT limit of {system.mib_text(kargs.mib(pages))}")
    killed = [s for s in sessions if s.ended in KILLED]
    froze = [s for s in sessions if s.ended == watch.RESTARTED]
    if (killed or froze) and now["guard"] == guard.BAZZITE and fresh(GUARD, guard.SUITE):
        said = ([f"The kernel ended {_names(killed)}."] if killed else []) + \
               ([f"The board froze while {_names(froze)} ran."] if froze else [])
        return Change(GUARD, guard.SUITE, guard.BAZZITE, " ".join(said), "the suite's memory guard")
    return None


# --- The comparison --------------------------------------------------------------------------------------------

def _share(sessions: list[watch.Session]) -> tuple[int, int]:
    return sum(s.ended in ENDED_SHORT for s in sessions), len(sessions)


def _gib(mib: int) -> str:
    return system.mib_text(mib)


def compare(before: list[watch.Session], after: list[watch.Session]) -> Verdict:
    """The owner's rules on the games played in both rounds."""
    games_before = list(dict.fromkeys(s.program for s in before))
    games_after = {s.program for s in after}
    common = [g for g in games_before if g in games_after]
    missing = [g for g in games_before if g not in games_after]
    a = [s for s in before if s.program in common]
    b = [s for s in after if s.program in common]
    ready = len(after) >= SESSIONS_A_ROUND and bool(common)
    (ka, na), (kb, nb) = _share(a), _share(b)
    wait_a = max((s.pressure for s in a), default=0.0)
    wait_b = max((s.pressure for s in b), default=0.0)
    ends = SAME
    if na and nb and ka * nb != kb * na:
        ends = BETTER if kb * na < ka * nb else WORSE
    waited = SAME
    if wait_b <= wait_a - WAIT_MARGIN:
        waited = BETTER
    elif wait_b >= wait_a + WAIT_MARGIN:
        waited = WORSE
    kind = ends if ends != SAME else waited

    def peak(sessions: list[watch.Session], key: str) -> int:
        return max((getattr(s, key) for s in sessions), default=0)

    def swap_text(sessions: list[watch.Session]) -> str:
        top = max(sessions, key=lambda s: s.swap_mib, default=None)
        return f"{_gib(top.swap_mib)} of {_gib(top.swap_total_mib)}" if top else "—"
    rows = [
        ("Ended for lack of memory", f"{ka} of {na}", f"{kb} of {nb}", ends),
        ("Waited for memory, peak", f"{wait_a:.0f}%", f"{wait_b:.0f}%", waited),
        ("Swap at its peak", swap_text(a), swap_text(b), ""),
        ("GPU borrowing at its peak", _gib(peak(a, "gtt_mib")), _gib(peak(b, "gtt_mib")), ""),
        ("VRAM at its peak", _gib(peak(a, "vram_mib")), _gib(peak(b, "vram_mib")), ""),
        ("CPU at its peak", f"{max((s.cpu for s in a), default=0):.0f}%",
         f"{max((s.cpu for s in b), default=0):.0f}%", "Context"),
    ]
    return Verdict(ready, kind, rows, missing, len(after))


def measured(sessions: list[watch.Session], now: dict, ram_mib: int) -> list[tuple[str, str]]:
    """What step 4 shows under its change: the round's figures, as (measured, value)."""
    k, n = _share(sessions)
    full = sum(_swap_full(s) for s in sessions)
    gtt = max((s.gtt_mib for s in sessions), default=0)
    vram = max((s.vram_mib for s in sessions), default=0)
    split = now.get("split")
    return [
        ("Ended for lack of memory", f"{k} of {n} sessions"),
        ("Swap full", f"{full} of {n} sessions"),
        ("GPU borrowing at its peak", f"{_gib(gtt)} of {_gib(ram_mib)}" if ram_mib else _gib(gtt)),
        ("VRAM at its peak", f"{_gib(vram)} of {_gib(split)}" if split else _gib(vram)),
        ("Waited for memory, peak", f"{max((s.pressure for s in sessions), default=0):.0f}%"),
        ("CPU at its peak", f"{max((s.cpu for s in sessions), default=0):.0f}%"),
    ]
