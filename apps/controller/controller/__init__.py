# SPDX-License-Identifier: GPL-3.0-or-later
"""Sony's DualSense and DualSense Edge controllers on Bazzite: their battery and firmware, the firmware update that
Sony offers only for Windows, and the Edge's profiles. The kernel's hid-playstation drives the controller; the app
talks to it through its hidraw node, with the standard library only."""

APP_NAME = "BC-250 Controller"
APP_ID = "bc250-controller"
__version__ = "2.10.0"

from pathlib import Path

from bc250_core import AppInfo

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / f"{APP_ID}.webp"

# Settings in ~/.config/bc250-controller/bc250-controller.ini
INFO = AppInfo(app_id=APP_ID, name=APP_NAME, version=__version__, logo=LOGO_PATH, tag_prefix="bc250-controller-v",
               settings_ini=True)

__all__ = ["APP_ID", "APP_NAME", "INFO", "LOGO_PATH", "ROOT", "__version__"]
