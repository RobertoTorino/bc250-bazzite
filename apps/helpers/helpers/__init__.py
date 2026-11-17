# SPDX-License-Identifier: GPL-3.0-or-later
"""Small helpers for one job each, which come with the suite: Board Test's extras, MangoHud's config, GPU metrics,
the sensors driver, the memory map, the journal, the IOMMU and the CPU mitigations."""

APP_NAME = "BC-250 Helpers"
APP_ID = "bc250-helpers"
__version__ = "0.2.1"

from pathlib import Path

from bc250_core import AppInfo

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / f"{APP_ID}.webp"

# Settings in ~/.config/bc250-helpers/bc250-helpers.ini
INFO = AppInfo(app_id=APP_ID, name=APP_NAME, version=__version__, logo=LOGO_PATH, tag_prefix="bc250-helpers-v",
               settings_ini=True)

__all__ = ["APP_ID", "APP_NAME", "INFO", "LOGO_PATH", "ROOT", "__version__"]
