# SPDX-License-Identifier: GPL-3.0-or-later
"""The window against the real script on the fake board (conftest.Board): the steps it shows, the buttons it
enables, the commands its buttons run and the switches in the launch options."""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from mesh_shaders import main_window
from mesh_shaders.main_window import MainWindow
from mesh_shaders.switches import SWITCHES, SwitchesDialog
from conftest import BUILT, SCRIPT, SUITE_PATCH, needs_bash

pytestmark = needs_bash

RUN = "/usr/local/bin/bc250-mesh-shaders-run %command%"


@pytest.fixture
def window(qapp, board, monkeypatch):
    for key, value in board.env.items():
        monkeypatch.setenv(key, value)
    w = MainWindow(SCRIPT, check_updates=False)
    yield w
    w.close()


def test_fresh_board(window):
    assert window.pill.text() == "Not built"
    assert window.build_state.text().startswith(f"Not built. Builds DirectMesh v1.4, Mesa 26.2.1, suite patch "
                                                f"{SUITE_PATCH}. It downloads")
    assert window.build_button.isEnabled()
    assert not window.install_button.isEnabled() and not window.remove_button.isEnabled()
    assert not window.test_button.isEnabled()
    assert not window.copy_button.isEnabled() and not window.switches_button.isEnabled()
    assert "kernel 7.2.8-ogc5.1.fc44.x86_64" in window.system.text()


def test_no_build_without_a_bc250(window, board):
    (board.root / "sys/bus/pci/devices/0000:01:00.0/device").write_text("0x73bf\n")
    window.refresh()
    assert window.pill.text() == "No BC-250" and not window.build_button.isEnabled()


def test_installed_and_tested(window, board):
    board.make_build()
    board.install()
    window.refresh()
    assert window.pill.text() == "Test needed"
    assert window.install_state.text().startswith(f"Installed: {BUILT}")
    assert window.test_button.isEnabled() and not window.install_button.isEnabled()
    board.pass_test()
    window.refresh()
    assert window.pill.text() == "Ready"
    assert window.test_state.text().startswith("<span style='color:#2e7d32'><b>Passed</b></span> on this kernel")
    window.copy_launch_options()
    assert QApplication.clipboard().text() == RUN


def test_newer_build_waits_to_be_installed(window, board):
    board.make_build()
    board.install()
    board.make_build(built="2026-10-14 08:00 UTC")
    window.refresh()
    assert "A newer build is waiting" in window.install_state.text()
    assert window.install_button.isEnabled()


def test_build_of_an_older_directmesh(window, board):
    board.make_build(directmesh="v1.3")
    window.refresh()
    assert "This version of the app builds DirectMesh v1.4, Mesa 26.2.1" in window.build_state.text()


def test_build_from_before_the_suite_patch(window, board):
    board.make_build(suite_patch=None)
    window.refresh()
    assert window.build_state.text().startswith("Built: DirectMesh v1.4, Mesa 26.2.1, 2026-10-13 19:42 UTC.")
    assert f"This version of the app builds DirectMesh v1.4, Mesa 26.2.1, suite patch {SUITE_PATCH}.</b>" in \
        window.build_state.text()


def test_switches_go_into_the_launch_options(window, board, monkeypatch):
    board.make_build()
    board.install()
    window.refresh()
    picked = [SWITCHES[0], SWITCHES[5]]
    monkeypatch.setattr(SwitchesDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
    monkeypatch.setattr(SwitchesDialog, "chosen", lambda self: picked)
    window.on_switches()
    expected = f"RADV_BC250_MESH_IDXPASS=0 RADV_DEBUG=nomeshshader {RUN}"
    assert window.launch_options() == expected
    assert "RADV_BC250_MESH_IDXPASS=0 RADV_DEBUG=nomeshshader" in window.use_state.text()
    assert "<b>Switches:</b> No indexed mesh draws, Hide mesh shaders." in window.use_state.text()
    assert window.switches_button.caption.text() == "2 on"
    window.copy_launch_options()
    assert QApplication.clipboard().text() == expected
    assert MainWindow(SCRIPT, check_updates=False).launch_options() == expected     # kept in the settings

    monkeypatch.setattr(SwitchesDialog, "chosen", lambda self: [])
    window.on_switches()
    assert window.launch_options() == RUN and "Switches:" not in window.use_state.text()


def test_switches_dialog(qapp):
    dialog = SwitchesDialog([SWITCHES[2]])
    assert dialog.chosen() == [SWITCHES[2]]
    dialog.boxes[SWITCHES[3]].setChecked(True)
    assert dialog.chosen() == [SWITCHES[2], SWITCHES[3]]
    assert dialog.boxes[SWITCHES[4]].text() == "DirectMesh off (RADV_DIRECTMESH=0)"


def test_commands(window):
    assert window.command("build") == ["bash", str(SCRIPT), "--build"]
    assert window.command("test") == ["bash", str(SCRIPT), "--test"]
    assert window.command("install") == ["pkexec", "/usr/bin/bash", str(SCRIPT), "--install-driver"]
    assert window.command("remove") == ["pkexec", "/usr/bin/bash", str(SCRIPT), "--remove-driver"]


def test_buttons_ask_first(window, monkeypatch):
    ran = []
    monkeypatch.setattr(window, "run", ran.append)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No)
    window.on_build()
    window.on_install()
    window.on_remove()
    assert ran == []
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    window.on_build()
    window.on_install()
    window.on_remove()
    assert ran == ["build", "install", "remove"]


def test_run_shows_the_output_and_refreshes(window, board, qapp, monkeypatch):
    monkeypatch.setitem(main_window.ACTIONS, "test", (["--launch-options"], False, "Testing…"))
    window.run("test")
    assert window.process is not None and not window.build_button.isEnabled()
    assert window.process.waitForFinished(10000)
    qapp.processEvents()
    assert window.running.text() == "Done."
    assert "bc250-mesh-shaders-run %command%" in window.output.toPlainText()
    assert window.process is None and window.build_button.isEnabled()


def test_not_authorised(window):
    window.action = "install"
    window.process = object()
    window._finished(126)
    assert window.running.text().startswith("Not authorized")


def releases(*tags: str) -> list[dict]:
    return [{"tag_name": tag, "html_url": f"https://github.com/x/releases/tag/{tag}",
             "published_at": "2026-10-20T10:00:00Z"} for tag in tags]


def checked(qapp, board, monkeypatch, answer) -> MainWindow:
    """A window that looked for a newer DirectMesh release at start, GitHub answering *answer* (or raising it)."""
    for key, value in board.env.items():
        monkeypatch.setenv(key, value)

    def fetch(url: str):
        if isinstance(answer, Exception):
            raise answer
        return answer
    w = MainWindow(SCRIPT, fetch=fetch)
    for _ in range(500):
        qapp.processEvents()
        if w.release is not None:
            break
        w.update_checker._thread and w.update_checker._thread.wait(10)
    assert w.release is not None
    return w


def test_a_newer_directmesh_is_announced(qapp, board, monkeypatch):
    w = checked(qapp, board, monkeypatch, releases("directmesh-v1.5", "directmesh-v1.4"))
    text = w.build_state.text()
    assert "<b>DirectMesh v1.5 is out</b> (2026-10-20). A newer version of this app brings it" in text
    assert "href='https://github.com/x/releases/tag/directmesh-v1.5'" in text
    w.close()


def test_the_pinned_directmesh_is_the_newest(qapp, board, monkeypatch):
    w = checked(qapp, board, monkeypatch, releases("directmesh-v1.4", "directmesh-v1.3.1"))
    assert "DirectMesh v1.4 is the newest release. <a href='#check'>Check again</a>" in w.build_state.text()
    w.close()


def test_a_failed_check_says_so(qapp, board, monkeypatch):
    import urllib.error
    w = checked(qapp, board, monkeypatch, urllib.error.URLError("Name or service not known"))
    assert "Could not look for a newer DirectMesh release: no connection (Name or service not known)." in \
        w.build_state.text()
    w.close()


def test_no_check_at_start_when_switched_off(window, monkeypatch):
    assert window.release is None and not window.update_checker.running
    assert "<a href='#check'>Look for a newer DirectMesh release</a>" in window.build_state.text()
    window.auto_check.setChecked(False)
    assert window.settings.get(main_window.CHECK_AT_START) is False
    started = []
    monkeypatch.setattr(window, "check_for_updates", lambda: started.append(True))
    window._link("#check")
    assert started == [True]


def test_the_window_is_a_card_with_two_rows_of_even_places_and_the_steps_beside_their_boxes(window, board):
    """The header's two symbols, the board line beside the icon, then the checkbox, the introduction, two rows of
    boxes and pills, and the four steps: a box that only names the step, with where it stands beside it."""
    header = window.header
    title = [header.title_row.itemAt(i).widget() for i in range(header.title_row.count())]
    assert title == [header.title, window.pill, window.info, None, window.refresh_button]   # None: the stretch
    assert "What it changes" in window.info.text_ and header.second_row.itemAt(0).widget() is window.system
    page = [window.page.itemAt(i) for i in range(window.page.count())]
    assert page[1].widget() is window.auto_check and "mesh shaders" in page[2].widget().text()
    first = [page[3].layout().itemAt(i).widget() for i in range(5)]
    second = [page[4].layout().itemAt(i).widget() for i in range(4)]
    assert first == [window.build_box, window.driver_box, window.test_box, window.copy_button, window.switches_button]
    assert second == [window.build_button, window.install_button, window.remove_button, window.test_button]
    assert [pill.caption.text() for pill in second] == ["20 to 40 minutes", "The build", "The driver", "A few minutes"]
    assert [box.value.text() for box in window.step_boxes] == ["1. Build", "2. Install", "3. Test", "4. Use"]
    assert len({widget.minimumWidth() for widget in [*first, *second, *window.step_boxes]}) == 1
    assert [box.value.text() for box in first[:3]] == ["Not built", "None", "\u2014"]
    assert window.switches_button.caption.text() == "None on"
    board.make_build()
    board.install()
    window.refresh()
    assert window.build_box.value.text() == "Built" and window.driver_box.value.text() == "Installed"
    assert window.test_box.value.text() == "Not run" and "Installed:" in window.driver_box.toolTip()
