# SPDX-License-Identifier: GPL-3.0-or-later
"""The BC-250's live system values on a Turzx USB IPS screen (the Turing Smart Screen 3.5" and its family): CPU, GPU,
memory, fan, temperatures, network and disk."""

APP_NAME = "BC-250 Turing Screen"
APP_ID = "bc250-turing-screen"
__version__ = "0.2.0"

from pathlib import Path

from bc250_core import AppInfo

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / f"{APP_ID}.webp"

# Settings in ~/.config/bc250-turing-screen/bc250-turing-screen.ini
INFO = AppInfo(app_id=APP_ID, name=APP_NAME, version=__version__, logo=LOGO_PATH, tag_prefix="bc250-turing-v",
               settings_ini=True)

__all__ = ["APP_ID", "APP_NAME", "INFO", "LOGO_PATH", "ROOT", "__version__"]
