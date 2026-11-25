# SPDX-License-Identifier: GPL-3.0-or-later
"""Small quickfixes for one job each, which come with the suite: Board Test's optional tools, MangoHud's config, GPU metrics,
the sensors driver, the memory map, the journal, the IOMMU and the CPU mitigations."""

APP_NAME = "BC-250 Quickfix"
APP_ID = "bc250-quickfix"
__version__ = "1.9.3"

from pathlib import Path

from bc250_core import AppInfo

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / f"{APP_ID}.webp"

# Settings in ~/.config/bc250-quickfix/bc250-quickfix.ini
INFO = AppInfo(app_id=APP_ID, name=APP_NAME, version=__version__, logo=LOGO_PATH, tag_prefix="bc250-quickfix-v",
               settings_ini=True)

__all__ = ["APP_ID", "APP_NAME", "INFO", "LOGO_PATH", "ROOT", "__version__"]
