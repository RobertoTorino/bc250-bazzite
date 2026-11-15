# SPDX-License-Identifier: GPL-3.0-or-later
"""create_app(): an app with .ini settings keeps Qt's default settings format; open_settings() makes its .ini file."""

from __future__ import annotations

from PyQt6.QtCore import QSettings

from bc250_core import app as app_module
from bc250_core import appinfo
from bc250_core.appinfo import AppInfo


def test_an_ini_app_leaves_the_default_format_alone(qapp):
    before = QSettings.defaultFormat()
    try:
        QSettings.setDefaultFormat(QSettings.Format.NativeFormat)
        app_module.create_app(AppInfo(app_id="x-test", name="X", version="0.1.0", settings_org="x-suite",
                                      settings_ini=True))
        assert QSettings.defaultFormat() == QSettings.Format.NativeFormat
    finally:
        QSettings.setDefaultFormat(before)
        appinfo.set_current(None)
