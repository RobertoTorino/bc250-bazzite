# SPDX-License-Identifier: GPL-3.0-or-later
"""The helpers' windows, offscreen, on folders of their own: what each shows, what its buttons offer (what is on
already cannot be turned on again) and what it asks system.py to do as root."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QMessageBox

from helpers import runner, state, system, windows

from test_state import put


@pytest.fixture
def root(tmp_path):
    return tmp_path / "root"


@pytest.fixture
def asked():
    """The commands the windows run as root; each answers as a successful pkexec would."""
    calls: list[list[str]] = []

    def run_root(argv):
        calls.append(argv[3:])                  # after pkexec, python, -I: system.py and its arguments
        return runner.Result(0, "")
    run_root.calls = calls
    return run_root


def change(asked) -> list[list[str]]:
    return [argv[1:] for argv in asked.calls]


def test_test_extras_lists_and_installs(qapp, tmp_path, monkeypatch):
    script = put(tmp_path, f"opt/{state.INSTALLER}", "#!/bin/sh\n")
    home = tmp_path / "home"
    tool = put(home, ".local/bin/vkpeak", "#!/bin/sh\n")
    os.chmod(tool, 0o755)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(state, "BREW_BIN", tmp_path / "brew")
    launched = []
    window = windows.ExtrasWindow(launch=launched.append, board_test=tmp_path / "opt", home=home)
    assert window.found_box.value.text() == f"1/{sum(len(g.tools) for g in state.GROUPS) + len(state.BUILT_IN)}"
    assert window.rows["vkpeak"].toolTip() == str(tool)
    assert window.buttons["--bins"].isEnabled()                         # memtest_vulkan is still missing
    window.buttons["--speedtest"].click()
    window.all_button.click()
    assert launched == [f"{script} --speedtest", f"{script} --all"]
    monkeypatch.setattr(state, "installer", lambda board_test=None, checkout=None: None)
    missing = windows.ExtrasWindow(launch=launched.append, board_test=tmp_path / "none", home=home)
    assert missing.state.text() == "Board Test not found" and not missing.all_button.isEnabled()


def test_mangohud_config_made_and_logging_set(qapp, tmp_path):
    home = tmp_path / "home"
    window = windows.MangoHudWindow(home=home)
    assert window.file_box.value.text() == "New" and window.log_box.value.text() == "Off"
    assert not window.save_button.isEnabled() and window.log_button.isEnabled()
    window.editor.setPlainText("fps\n")
    window.log_button.click()
    assert window.log_box.value.text() == "On" and window.save_button.isEnabled()
    assert not window.log_button.isEnabled()                            # set already
    window.save_button.click()
    conf = home / state.MANGOHUD_CONF
    assert conf.read_text().startswith("fps\n") and f"output_folder={home / 'mangohud-logs'}" in conf.read_text()
    assert (home / "mangohud-logs").is_dir() and window.file_box.value.text() == "There"
    assert window.state.text() == "Saved" and not window.save_button.isEnabled()


def test_mangohud_deletes_only_old_logs(qapp, tmp_path, monkeypatch):
    home = tmp_path / "home"
    old, new = put(home, "mangohud-logs/old.csv"), put(home, "mangohud-logs/new.csv")
    os.utime(old, (1, 1))
    window = windows.MangoHudWindow(home=home)
    assert window.logs_box.value.text() == "2" and window.clean_button.isEnabled()
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    window.clean_button.click()
    assert not old.exists() and new.exists() and not window.clean_button.isEnabled()


def test_fix_gpu_metrics(qapp, root, asked):
    window = windows.MetricsWindow(root=root, run_root=asked)
    assert window.state.text() == "No governor" and not window.on_button.isEnabled()
    put(root, f"etc/{system.GOVERNOR_CONFIG}", '[gpu-usage]\nfix-metrics = false\nmethod = "process"\n')
    window.refresh()
    assert window.method.currentText() == "process" and window.on_button.isEnabled()
    assert not window.off_button.isEnabled()
    window.method.setCurrentText("busy-flag")
    window.on_button.click()
    assert change(asked) == [["metrics", "on", "--method", "busy-flag"]]
    put(root, f"etc/{system.GOVERNOR_CONFIG}", '[gpu-usage]\nfix-metrics = true\nmethod = "busy-flag"\n')
    window.refresh()
    assert window.state.text() == "On, not mounted" and not window.on_button.isEnabled()     # applied already
    window.method.setCurrentText("kernel")
    assert window.on_button.text() == "Apply" and window.on_button.isEnabled()
    window.off_button.click()
    assert change(asked)[-1] == ["metrics", "off"]


def test_sensors_module_counts_either_driver(qapp, root, asked):
    window = windows.SensorsWindow(root=root, run_root=asked)
    assert window.state.text() == "Off" and window.on_button.isEnabled() and not window.off_button.isEnabled()
    window.on_button.click()
    assert change(asked) == [["sensors", "on"]]
    (root / "sys/module/nct6687").mkdir(parents=True)
    put(root, "sys/class/hwmon/hwmon2/name", "nct6686\n")
    window.refresh()
    assert window.boxes["Driver"].value.text() == "nct6687" and window.boxes["Sensors"].value.text() == "nct6686"
    assert window.state.text() == "On" and not window.on_button.isEnabled() and not window.off_button.isEnabled()
    put(root, f"etc/{system.SENSORS_CONF}", system.SENSORS_LINE)
    window.refresh()
    assert window.off_button.isEnabled()


def test_game_memory_map(qapp, root, asked):
    put(root, "proc/sys/vm/max_map_count", "65530\n")
    window = windows.MapCountWindow(root=root, run_root=asked)
    assert window.state.text() == "Off" and window.on_button.isEnabled()
    window.on_button.click()
    assert change(asked) == [["mapcount", "on"]]
    put(root, "proc/sys/vm/max_map_count", f"{system.MAPCOUNT}\n")
    window.refresh()
    assert window.boxes["Set by"].value.text() == "The system" and not window.on_button.isEnabled()
    assert not window.off_button.isEnabled()                            # the system's: not the helper's to undo


def test_persistent_journal_asks_before_it_removes(qapp, root, asked, monkeypatch):
    window = windows.JournalWindow(root=root, run_root=asked)
    assert window.boxes["Journal"].value.text() == "In memory" and window.on_button.isEnabled()
    put(root, f"var/{system.JOURNAL_DIR}/{system.JOURNAL_MARK}")
    window.refresh()
    assert window.boxes["Made by"].value.text() == "This helper" and window.off_button.isEnabled()
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No)
    window.off_button.click()
    assert change(asked) == []
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    window.off_button.click()
    assert change(asked) == [["journal", "off"]]


class Kargs:
    """rpm-ostree kargs as the windows read it: the next boot's arguments."""

    def __init__(self, *args: str) -> None:
        self.args: list[str] | None = list(args)

    def __call__(self) -> list[str] | None:
        return self.args


def test_iommu_off_from_the_next_boot(qapp, root, asked):
    for i in range(2):
        (root / f"sys/kernel/iommu_groups/{i}").mkdir(parents=True)
    put(root, "proc/cmdline", "rhgb quiet\n")
    kargs = Kargs("rhgb", "quiet")
    window = windows.IommuWindow(root=root, run_root=asked, next_kargs=kargs)
    assert window.boxes["IOMMU"].value.text() == "On" and window.state.text() == "Off"
    assert window.on_button.isEnabled() and not window.off_button.isEnabled()
    window.on_button.click()
    assert change(asked) == [["iommu", "on"]]
    kargs.args.append("amd_iommu=off")
    put(root, f"var/{system.KARGS_DIR}/iommu.karg", "amd_iommu=off\n")
    window.refresh()
    assert window.state.text() == "Reboot to apply" and "systemctl reboot" in window.note.text()
    assert not window.on_button.isEnabled() and window.off_button.isEnabled()
    assert window.boxes["Added by"].value.text() == "This helper"
    window.off_button.click()
    assert change(asked)[-1] == ["iommu", "off"]


def test_iommu_off_in_the_bios_needs_nothing(qapp, root, asked):
    (root / "sys/kernel/iommu_groups").mkdir(parents=True)
    window = windows.IommuWindow(root=root, run_root=asked, next_kargs=Kargs("rhgb"))
    assert window.boxes["IOMMU"].value.text() == "Off" and window.state.text() == "Off already"
    assert not window.on_button.isEnabled() and "BIOS" in window.note.text()


def test_cpu_mitigations_set_by_hand_stay(qapp, root, asked):
    put(root, "proc/cmdline", "rhgb mitigations=off\n")                       # the owner's board
    window = windows.MitigationsWindow(root=root, run_root=asked, next_kargs=Kargs("rhgb", "mitigations=off"))
    assert window.state.text() == "On" and window.boxes["Added by"].value.text() == "The system"
    assert not window.on_button.isEnabled() and not window.off_button.isEnabled()
    none = windows.MitigationsWindow(root=root, run_root=asked, next_kargs=lambda: None)
    assert none.state.text() == "No rpm-ostree" and not none.on_button.isEnabled()


def test_a_canceled_password_says_so(qapp, root, monkeypatch):
    shown = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: shown.append(a[2]))
    window = windows.SensorsWindow(root=root, run_root=lambda argv: runner.Result(126, ""))
    window.on_button.click()
    assert shown and "canceled" in shown[0]


def test_every_window_says_what_it_does(qapp, root, tmp_path):
    for key, make in windows.WINDOWS.items():
        extra = {"next_kargs": Kargs()} if key in system.KARGS else {}
        window = make(root=root, home=tmp_path / "home", **extra)
        assert window.windowTitle() == window.helper.name and window.info.text_
        assert ("Changes the board" in window.info.text_) == window.helper.changes_board, key
        window.close()


def test_the_system_part_runs_from_the_app(tmp_path):
    assert Path(system.__file__).name == "system.py"
    argv = system.command(["journal", "on"])
    assert argv[3] == str(Path(system.__file__).resolve())
