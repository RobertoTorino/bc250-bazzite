# SPDX-License-Identifier: GPL-3.0-or-later

"""BC-250 CPU Tools, one window for the core bisect and the core unlock (owner, 20-11-2026: Cores Bisect and Cores
Unlock are one app, as CU Tools). The bisect part only assembles the command line of bc250-cores-bisect.sh and starts it
in a terminal, exactly as if typed by hand; the unlock part reads the bisect's results and runs bc250-cores-unlock.sh."""

from pathlib import Path

APP_NAME = "BC-250 CPU Tools"
APP_ID = "bc250-cores-bisect-gui"
ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / "bc250-cores-bisect.webp"
WINDOW_ICON_PATH = LOGO_PATH
REPO_URL = "https://github.com/RobertoTorino/bc250-bazzite/tree/main/apps/cores"


def _read_version() -> str:
    try:
        return (ROOT / "VERSION").read_text().strip() or "0.0.0"
    except OSError:
        return "0.0.0"


__version__ = _read_version()


def window_title(part: str) -> str:
    """Title of a secondary window. On Linux/Windows Qt appends " — <display name>" itself."""
    import sys
    return f"{APP_NAME} — {part}" if sys.platform == "darwin" else part
