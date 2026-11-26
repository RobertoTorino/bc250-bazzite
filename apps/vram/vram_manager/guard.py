# SPDX-License-Identifier: GPL-3.0-or-later
"""The memory guard: what systemd-oomd ends before the board freezes, and the root helper that writes it.

Two guards (owner, 26-11-2026, after kernel OOM kills on 25-11 with KytyPS5 and 26-11 with shadPS4):

    bazzite   Bazzite's own: memory pressure 80% for 20 s, swap not watched. None of the app's files.
    suite     The suite's guard: memory pressure 60% for 10 s, or swap 90% full

Bazzite's own comes from the image: /usr/lib/systemd/oomd.conf.d/10-oomd-defaults.conf (20 s) and the slice.d
drop-ins of the system and the user manager (kill at 80%). No unit there has ManagedOOMSwap, so swap is not watched,
and a board whose swap is full stalls until the kernel's own OOM killer acts. The suite's values are starting values
to test on the board.

The suite's guard is four files of the app's own, so the image's files stay as they are and removing ours brings
Bazzite's guard back:

    /etc/systemd/oomd.conf.d/90-bc250-memory-manager.conf           the limits and the duration
    /etc/systemd/system/-.slice.d/90-bc250-memory-manager.conf      swap watched for the whole board
    /etc/systemd/system/user@.service.d/90-bc250-memory-manager.conf  memory pressure watched for the session
    /etc/systemd/user/slice.d/90-bc250-memory-manager.conf          the session's slices (apps, games) at the limit

The guard takes effect at once: the helper reloads systemd and restarts systemd-oomd, and the app reloads the user
manager, which hands its slices' settings to systemd-oomd again.

Run as root (through pkexec) with the system Python, standard library only:

    python3 -I guard.py --guard suite
    python3 -I guard.py --guard bazzite

Each prints one JSON object."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

BAZZITE, SUITE = "bazzite", "suite"
PRESSURE_PERCENT = 60                           # the suite's guard: memory pressure limit
DURATION_S = 10                                 # for this long
SWAP_PERCENT = 90                               # or swap this full
GUARDS = {
    SUITE: f"The suite's guard: memory pressure {PRESSURE_PERCENT}% for {DURATION_S} s, or swap {SWAP_PERCENT}% full",
    BAZZITE: "Bazzite's own: memory pressure 80% for 20 s, swap not watched",
}
HEADER = "# Written by BC-250 Memory Manager (memory guard). Pick Bazzite's own guard in the app to remove it.\n"
OOMD = "systemd/oomd.conf.d/90-bc250-memory-manager.conf"                  # these four under /etc
ROOT_SLICE = "systemd/system/-.slice.d/90-bc250-memory-manager.conf"
SESSION = "systemd/system/user@.service.d/90-bc250-memory-manager.conf"
USER_SLICES = "systemd/user/slice.d/90-bc250-memory-manager.conf"
FILES = (OOMD, ROOT_SLICE, SESSION, USER_SLICES)

Run = Callable[[list[str]], int]


class GuardError(Exception):
    """A guard that cannot be written, with the reason for the user."""


def texts() -> dict[str, str]:
    """The suite's guard: each file's text."""
    limit = f"ManagedOOMMemoryPressureLimit={PRESSURE_PERCENT}%\n"
    return {
        OOMD: HEADER + f"[OOM]\nSwapUsedLimit={SWAP_PERCENT}%\nDefaultMemoryPressureLimit={PRESSURE_PERCENT}%\n"
                       f"DefaultMemoryPressureDurationSec={DURATION_S}s\n",
        ROOT_SLICE: HEADER + "[Slice]\nManagedOOMSwap=kill\n",
        SESSION: HEADER + "[Service]\nManagedOOMMemoryPressure=kill\n" + limit,
        USER_SLICES: HEADER + "[Slice]\nManagedOOMMemoryPressure=kill\n" + limit,
    }


def read_guard(etc: Path = Path("/etc")) -> str:
    """The guard the app's files hold: the suite's when all four are there as written, else Bazzite's own. Needs no
    root."""
    wanted = texts()
    for name, text in wanted.items():
        try:
            if (etc / name).read_text() != text:
                return BAZZITE
        except OSError:
            return BAZZITE
    return SUITE


# --- The helper ------------------------------------------------------------------------------------------------

def _run(cmd: list[str]) -> int:
    """Runs a command with its output on stderr, where it does not disturb the JSON answer; 127 when it is not
    installed."""
    try:
        return subprocess.run(cmd, stdout=sys.stderr, check=False).returncode
    except OSError:
        return 127


def _remove(path: Path) -> None:
    path.unlink(missing_ok=True)
    try:
        path.parent.rmdir()                     # our drop-in's folder, when nothing else is in it
    except OSError:
        pass


def apply(guard: str, etc: Path = Path("/etc"), run: Run = _run) -> dict:
    """Writes the guard's files, or removes them for Bazzite's own, and restarts systemd-oomd with them."""
    if guard not in GUARDS:
        raise GuardError(f"Unknown guard {guard!r}.")
    before = read_guard(etc)
    if guard == SUITE:
        for name, text in texts().items():
            path = etc / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            os.chmod(path, 0o644)
    else:
        for name in FILES:
            _remove(etc / name)
    run(["systemctl", "daemon-reload"])
    if run(["systemctl", "restart", "systemd-oomd.service"]) != 0:
        raise GuardError("The files are written, but systemd-oomd did not restart. It reads them at the next boot.")
    return {"ok": True, "before": before, "after": read_guard(etc)}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="guard.py", description="BC-250 memory guard (root helper)")
    parser.add_argument("--guard", choices=tuple(GUARDS), required=True)
    args = parser.parse_args(argv)
    try:
        if os.geteuid() != 0:
            raise GuardError("The memory guard is written as root.")
        result = apply(args.guard)
    except GuardError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    except OSError as exc:
        print(json.dumps({"ok": False, "error": f"{exc.strerror or exc}: {exc.filename or ''}".rstrip(": ")}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
