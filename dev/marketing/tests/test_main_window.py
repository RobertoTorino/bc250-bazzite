# SPDX-License-Identifier: GPL-3.0-or-later
"""The window opens offscreen with Nexus's header, a row per portal app, and the pills in their states."""

from __future__ import annotations

import datetime

from nexus_marketing import article
from nexus_marketing.main_window import MainWindow, export_folder


def test_a_row_for_every_app():
    window = MainWindow(stills=lambda: True)
    assert window.table.rowCount() == len(article.apps())
    assert window.apps_box.value.text() == f"{len(article.apps())} of {len(article.apps())}"
    window.close()


def test_current_stills_cannot_be_taken_again():
    window = MainWindow(stills=lambda: True)
    assert not window.shots_pill.isEnabled()
    assert window.shots_box.value.text() == "Current"
    window.close()
    window = MainWindow(stills=lambda: False)
    assert window.shots_pill.isEnabled()
    assert window.shots_box.value.text() == "Out of date"
    window.close()


def test_export_never_takes_a_folder_that_is_there(tmp_path):
    now = datetime.datetime(2026, 11, 25, 21, 30, 5)
    first = export_folder(tmp_path, now)
    assert first.name == "bc250-bazzite-suite-article-2026-11-25-213005"
    first.mkdir()
    assert export_folder(tmp_path, now).name == "bc250-bazzite-suite-article-2026-11-25-213005-2"


def test_export_writes_into_a_git_checkout_itself(tmp_path):
    """A git checkout, as the website's (owner, 26-11-2026): the article goes straight in, no dated folder."""
    (tmp_path / ".git").mkdir()
    assert export_folder(tmp_path) == tmp_path


def test_publish_says_when_the_website_is_behind(tmp_path):
    window = MainWindow(stills=lambda: True)
    assert window.publish_pill.caption.text() == "Choose the folder"
    site = tmp_path / "site"
    (site / ".git").mkdir(parents=True)
    window.settings.setValue("website_folder", str(site))
    window.refresh()
    assert window.publish_pill.caption.text().endswith("changes") and window.publish_pill.isEnabled()
    article.publish(article.build(), site)
    window.refresh()
    assert window.publish_pill.caption.text() == "Up to date"
    assert not window.publish_pill.isEnabled()                  # what is published cannot be published again
    window.close()


def test_website_url_from_the_remote_or_the_cname(tmp_path):
    from nexus_marketing.main_window import website_url
    site = tmp_path / "site"
    (site / ".git").mkdir(parents=True)
    assert website_url(None) is None and website_url(site) is None
    for remote in ("https://github.com/RobertoTorino/bc250-suite.git", "git@github.com:RobertoTorino/bc250-suite.git"):
        (site / ".git" / "config").write_text(f'[remote "origin"]\n\turl = {remote}\n')
        assert website_url(site) == "https://robertotorino.github.io/bc250-suite/"
    (site / "CNAME").write_text("bc250suite.com\n")
    assert website_url(site) == "https://bc250suite.com/"


def test_the_globe_is_on_with_a_website(tmp_path):
    window = MainWindow(stills=lambda: True)
    assert not window.globe_button.isEnabled()
    site = tmp_path / "site"
    (site / ".git").mkdir(parents=True)
    (site / ".git" / "config").write_text('[remote "origin"]\n\turl = https://github.com/RobertoTorino/bc250-suite.git\n')
    window.settings.setValue("website_folder", str(site))
    window.refresh()
    assert window.globe_button.isEnabled() and "robertotorino.github.io/bc250-suite/" in window.globe_button.toolTip()
    window.close()


def test_each_suite_has_its_own_preview_file(monkeypatch, tmp_path):
    """Both suites' twins have the same app ID, so the preview is named after the suite (owner, 25-11-2026)."""
    from nexus_marketing import main_window
    monkeypatch.setattr(main_window, "PREVIEW", tmp_path)
    monkeypatch.setattr(main_window.QDesktopServices, "openUrl", lambda url: True)
    window = MainWindow(stills=lambda: True)
    window.on_preview()
    assert [path.name for path in tmp_path.iterdir()] == [main_window.suite_slug() + ".html"]
    window.close()


def test_the_pencil_opens_copy_md(monkeypatch):
    """The pencil beside the line that names copy.md opens the file in the default editor (owner, 26-11-2026)."""
    from nexus_marketing import main_window
    opened = []
    monkeypatch.setattr(main_window.QDesktopServices, "openUrl", lambda url: opened.append(url.toLocalFile()))
    window = MainWindow(stills=lambda: True)
    window.edit_button.click()
    assert opened == [str(article.COPY)]
    window.close()
