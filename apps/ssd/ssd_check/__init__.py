# SPDX-License-Identifier: GPL-3.0-or-later
"""The health, power cycles and power-on hours of the board's SSDs."""

APP_NAME = "BC-250 SSD Check"
APP_ID = "bc250-ssd-check"
__version__ = "3.8.0"

from pathlib import Path

from bc250_core import AppInfo

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / f"{APP_ID}.webp"

# Settings in ~/.config/bc250-ssd-check/bc250-ssd-check.ini
INFO = AppInfo(app_id=APP_ID, name=APP_NAME, version=__version__, logo=LOGO_PATH, tag_prefix="bc250-ssd-v",
               settings_ini=True)

__all__ = ["APP_ID", "APP_NAME", "INFO", "LOGO_PATH", "ROOT", "__version__"]
