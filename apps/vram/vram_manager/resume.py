# SPDX-License-Identifier: GPL-3.0-or-later
"""The window back after a restart (owner, 26-11-2026, as Core Unlock): while a written change waits for a restart,
an autostart entry opens the window again after the next login, with the next step. The window removes the entry
once the restart is done, and install.sh --uninstall removes it with the app. restart() restarts the board as Core
Unlock's does: no password dialog, sudo -n as the fallback."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

ENTRY_NAME = "bc250-memory-manager-resume.desktop"


def entry_path() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")) / "autostart" / ENTRY_NAME


def armed() -> bool:
    return entry_path().is_file()


def arm() -> None:
    """This Python with this package: the window that armed the entry opens again, installed or from a checkout. The
    entry's Path= is the app's folder, so -m finds the package."""
    from . import ROOT
    path = entry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("[Desktop Entry]\nType=Application\nName=BC-250 Memory Manager, the next learning step\n"
                    f"Exec={shlex.join([sys.executable, '-m', 'vram_manager'])}\nPath={ROOT}\n"
                    "X-GNOME-Autostart-enabled=true\n")


def disarm() -> None:
    entry_path().unlink(missing_ok=True)


def restart() -> bool:
    """Restarts the board. False when neither systemctl nor sudo -n may."""
    for argv in (["systemctl", "reboot", "--no-ask-password"], ["sudo", "-n", "systemctl", "reboot"]):
        try:
            if subprocess.run(argv, capture_output=True).returncode == 0:
                return True
        except OSError:
            continue
    return False
