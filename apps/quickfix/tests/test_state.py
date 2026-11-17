# SPDX-License-Identifier: GPL-3.0-or-later
"""What the quickfixes read, from folders that stand in for /etc, /proc, /sys and /var: the BC-250 with the nct6687
driver (the owner's board) and with the forced nct6683, Bazzite's own max_map_count and journal, and a system that
has neither."""

from __future__ import annotations

import os
from pathlib import Path

from quickfix import state, system


def put(root: Path, path: str, text: str = "") -> Path:
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)
    return file


def test_mangohud_logging_lines():
    text = "fps\n# a comment\noutput_folder=/old  # where\nposition=top-left\n"
    values = state.conf_values(text)
    assert values == {"fps": "1", "output_folder": "/old", "position": "top-left"}
    assert not state.logging_on(values)
    new = state.with_logging(text, Path("/home/u/mangohud-logs"))
    assert new.splitlines()[:4] == ["fps", "# a comment", "output_folder=/home/u/mangohud-logs", "position=top-left"]
    assert new.splitlines()[-2:] == ["autostart_log=1", f"log_interval={state.LOG_INTERVAL}"]
    assert state.logging_on(state.conf_values(new))
    assert state.with_logging(new, Path("/home/u/mangohud-logs")) == new                # set already: unchanged
    assert state.with_logging("", Path("/l")).splitlines()[1:] == ["output_folder=/l", "autostart_log=1",
                                                                   "log_interval=500"]


def test_log_files(tmp_path):
    for name in ("Game_2026-11-15.csv", "Game_2026-11-15_summary.csv", "notes.txt"):
        put(tmp_path, name)
    assert [p.name for p in state.log_files(tmp_path)] == ["Game_2026-11-15.csv", "Game_2026-11-15_summary.csv"]
    assert state.log_files(tmp_path / "none") == []


def test_metrics(tmp_path):
    assert state.metrics(tmp_path) == state.Metrics(False, False, "", False)
    put(tmp_path, f"etc/{system.GOVERNOR_CONFIG}", '[gpu-usage]\nfix-metrics = true\nmethod = "busy-flag"\n')
    put(tmp_path, "proc/self/mountinfo", "36 25 0:31 / /sys/devices/pci0000:00/0000:00:08.1/0000:01:00.0/"
        "gpu_metrics rw,relatime shared:1 - tmpfs tmpfs rw\n")
    assert state.metrics(tmp_path) == state.Metrics(True, True, "busy-flag", True)
    put(tmp_path, f"etc/{system.GOVERNOR_CONFIG}", "[gpu-usage\n")
    assert state.metrics(tmp_path).problem


def test_sensors_with_either_driver(tmp_path):
    assert not state.sensors(tmp_path).on
    (tmp_path / "sys/module/nct6687").mkdir(parents=True)                 # the owner's board
    put(tmp_path, "sys/class/hwmon/hwmon3/name", "nct6686\n")
    put(tmp_path, "sys/class/hwmon/hwmon1/name", "amdgpu\n")
    s = state.sensors(tmp_path)
    assert (s.driver, s.hwmon, s.ours, s.on) == ("nct6687", "nct6686", False, True)
    other = tmp_path / "other"
    put(other, "etc/modprobe.d/sensors.conf", "# mine\noptions nct6683 force=true\n")
    assert state.sensors(other).elsewhere == "sensors.conf" and state.sensors(other).on
    put(other, f"etc/{system.SENSORS_CONF}", system.SENSORS_LINE)
    assert state.sensors(other).ours


def test_mapcount_and_journal(tmp_path):
    assert state.mapcount(tmp_path) == state.MapCount(0, False)
    put(tmp_path, "proc/sys/vm/max_map_count", "2147483642\n")
    assert state.mapcount(tmp_path).value == system.MAPCOUNT
    assert state.journal(tmp_path) == state.Journal(False, False)
    (tmp_path / "var/log/journal").mkdir(parents=True)
    assert state.journal(tmp_path) == state.Journal(True, False)
    put(tmp_path, f"var/{system.JOURNAL_DIR}/{system.JOURNAL_MARK}")
    assert state.journal(tmp_path) == state.Journal(True, True)


def test_kernel_arguments(tmp_path):
    put(tmp_path, "proc/cmdline", "BOOT_IMAGE=/vmlinuz rhgb quiet mitigations=off zswap.enabled=0\n")  # the owner's
    for i in range(3):
        (tmp_path / f"sys/kernel/iommu_groups/{i}").mkdir(parents=True)
    k = state.karg("mitigations", tmp_path, lambda: ["rhgb", "mitigations=off"])
    assert (k.now, k.next, k.ours, k.pending) == (True, True, False, False)
    k = state.karg("iommu", tmp_path, lambda: ["rhgb", "amd_iommu=off"])
    assert (k.arg, k.now, k.next, k.pending, k.iommu_groups) == ("amd_iommu=off", False, True, True, 3)
    put(tmp_path, f"var/{system.KARGS_DIR}/iommu.karg", "amd_iommu=off\n")
    assert state.karg("iommu", tmp_path, lambda: None) == state.Karg("amd_iommu=off", False, None, True, 3)
    assert state.karg("iommu", tmp_path / "none", lambda: []).iommu_groups is None    # no /sys


def test_find_tool_where_the_tests_look(tmp_path, monkeypatch):
    monkeypatch.setattr(state, "BREW_BIN", tmp_path / "brew")
    tool = put(tmp_path, "home/.local/bin/vkpeak", "#!/bin/sh\n")
    assert state.find_tool("vkpeak", tmp_path / "home", path="") == ""                 # not executable
    os.chmod(tool, 0o755)
    assert state.find_tool("vkpeak", tmp_path / "home", path="") == str(tool)
    put(tmp_path, "bin/fio", "#!/bin/sh\n")
    os.chmod(tmp_path / "bin/fio", 0o755)
    assert state.find_tool("fio", tmp_path / "home", path=str(tmp_path / "bin")) == str(tmp_path / "bin/fio")


def test_board_tests_installer(tmp_path):
    assert state.installer(tmp_path / "opt", tmp_path / "none") is None
    script = put(tmp_path, f"opt/{state.INSTALLER}")
    assert state.installer(tmp_path / "opt", tmp_path / "none") == script
    assert state.installer(tmp_path / "none").name == "install-requirements.sh"          # the checkout's
