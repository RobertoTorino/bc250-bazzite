# SPDX-License-Identifier: GPL-3.0-or-later
"""Entry point: python -m vram_manager"""

from __future__ import annotations

import argparse
import sys

from bc250_core import __version__ as CORE_VERSION, instance
from bc250_core.app import create_app, exec_app
from bc250_core import exit_keys

from . import APP_NAME, INFO, __version__


def main() -> int:
    parser = argparse.ArgumentParser(prog="vram_manager", description=f"{APP_NAME} {__version__}")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__} (core {CORE_VERSION})")
    parser.add_argument("--profile", choices=("defaults", "games", "smooth", "ps5"), help="open on this profile's question "
                        "(the watcher's notification, when a game wants a profile the board lacks)")
    args, qt_args = parser.parse_known_args()

    app = create_app(INFO, qt_args)
    exit_keys.install(app)                  # Escape and a controller's B close the window
    if instance.already_running(INFO.app_id):
        return 0
    from .main_window import MainWindow
    window = MainWindow()
    window.show()
    if args.profile:
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: window.offer_profile(args.profile))
    server = instance.serve(INFO.app_id, window)  # noqa: F841 (kept alive while the app runs)
    return exec_app(app)


if __name__ == "__main__":
    sys.exit(main())
