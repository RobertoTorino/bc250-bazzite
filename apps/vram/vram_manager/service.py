# SPDX-License-Identifier: GPL-3.0-or-later
"""The user service that records the sessions (watch.py) with the desktop session: bc250-memory-watch.service in
~/.config/systemd/user. The app writes, enables and starts it when recording is turned on, and stops and removes it
when it is turned off (owner, 26-11-2026: recording on its own, not with the memory guard). install.sh restarts it with a new version and removes it with the app, since it starts the app's
own files. As HDMI-CEC's watcher service does."""

from __future__ import annotations

from pathlib import Path

from . import kargs

UNIT = "bc250-memory-watch.service"


def unit_path(config_dir: Path) -> Path:
    return config_dir / "systemd" / "user" / UNIT


def unit_text(python: str, root: Path) -> str:
    return "\n".join([
        "[Unit]",
        "Description=BC-250 Memory Manager: the sessions, what each program asked of the memory",
        "After=graphical-session.target",
        "PartOf=graphical-session.target",
        "",
        "[Service]",
        f"WorkingDirectory={root}",
        f"ExecStart={python} -m vram_manager.watch",
        "Restart=on-failure",
        "RestartSec=30",
        "",
        "[Install]",
        "WantedBy=graphical-session.target",
        "",
    ])


def installed(config_dir: Path) -> bool:
    return unit_path(config_dir).is_file()


def enable(run: kargs.Run, config_dir: Path, python: str, root: Path) -> str:
    """Writes the unit, enables and (re)starts it; the error in words, "" when it runs."""
    path = unit_path(config_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(unit_text(python, root), encoding="utf-8")
    run(["systemctl", "--user", "daemon-reload"])
    run(["systemctl", "--user", "enable", UNIT])
    code, _out, err = run(["systemctl", "--user", "restart", UNIT])
    return "" if code == 0 else f"The sessions service did not start: {err.strip() or f'exit code {code}'}"


def disable(run: kargs.Run, config_dir: Path) -> None:
    path = unit_path(config_dir)
    if not path.is_file():
        return
    run(["systemctl", "--user", "disable", "--now", UNIT])
    path.unlink()
    run(["systemctl", "--user", "daemon-reload"])
