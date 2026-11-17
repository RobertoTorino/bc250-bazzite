# SPDX-License-Identifier: GPL-3.0-or-later
"""system.py, the part that runs as root, on a folder of its own: each change writes only its own file (or, for the
GPU governor, its two lines after a backup), and its off undoes it."""

from __future__ import annotations

import tomllib

import pytest

from quickfix import system

CONFIG = """# us
[timing.intervals]
sample = 250

[gpu-usage]
fix-metrics = false
 fix-freq = false
method = "process" # "busy-flag" , "process" or "kernel"
flush-every = 10

[gpu]
set-method = "smu"  # "smu" or "kernel"
"""


@pytest.fixture
def ran(monkeypatch):
    calls = []
    monkeypatch.setattr(system, "run", lambda argv: calls.append(argv) or 0)
    return calls


def test_fix_metrics_changes_only_its_two_lines():
    text = system.set_metrics(CONFIG, True, "busy-flag")
    assert text.splitlines() == [line.replace("fix-metrics = false", "fix-metrics = true")
                                 .replace('"process" #', '"busy-flag" #') for line in CONFIG.splitlines()]
    usage = tomllib.loads(text)["gpu-usage"]
    assert usage["fix-metrics"] is True and usage["method"] == "busy-flag" and usage["fix-freq"] is False
    off = system.set_metrics(text, False, None)
    assert tomllib.loads(off)["gpu-usage"] == {**usage, "fix-metrics": False}          # the method stays


def test_fix_metrics_adds_what_is_missing():
    assert tomllib.loads(system.set_metrics("[gpu]\nset-method = \"smu\"\n", True, "kernel"))["gpu-usage"] == \
        {"fix-metrics": True, "method": "kernel"}
    text = system.set_metrics("[gpu-usage]\nflush-every = 10\n\n[gpu]\n", True, None)
    assert tomllib.loads(text)["gpu-usage"] == {"fix-metrics": True, "flush-every": 10}


def test_metrics_backs_up_and_restarts_a_running_governor(tmp_path, ran):
    config = tmp_path / system.GOVERNOR_CONFIG
    config.parent.mkdir(parents=True)
    config.write_text(CONFIG)
    assert system.main(["metrics", "on", "--method", "busy-flag"], etc=tmp_path) == 0
    backups = list(config.parent.glob("config.toml.bak-*"))
    assert len(backups) == 1 and backups[0].read_text() == CONFIG
    assert tomllib.loads(config.read_text())["gpu-usage"]["fix-metrics"] is True
    assert ran == [["systemctl", "try-restart", system.GOVERNOR_UNIT]]


def test_metrics_without_the_governor(tmp_path, ran, capsys):
    assert system.main(["metrics", "on"], etc=tmp_path) == 1 and ran == []
    assert "not installed" in capsys.readouterr().out


def test_sensors_on_and_off(tmp_path, ran):
    assert system.main(["sensors", "on"], etc=tmp_path) == 0
    conf = tmp_path / system.SENSORS_CONF
    assert system.SENSORS_LINE in conf.read_text().splitlines() and ran == [["modprobe", "nct6683", "force=true"]]
    assert system.main(["sensors", "off"], etc=tmp_path) == 0
    assert not conf.exists()


def test_mapcount_on_and_off(tmp_path, ran):
    system.main(["mapcount", "on"], etc=tmp_path)
    conf = tmp_path / system.MAPCOUNT_CONF
    assert f"vm.max_map_count = {system.MAPCOUNT}" in conf.read_text()
    system.main(["mapcount", "off"], etc=tmp_path)
    assert not conf.exists()
    assert ran == [["sysctl", "-w", f"vm.max_map_count={system.MAPCOUNT}"], ["sysctl", "--system"]]


def test_journal_on_and_off_only_its_own(tmp_path, ran):
    folder = tmp_path / system.JOURNAL_DIR
    assert system.main(["journal", "on"], var=tmp_path) == 0
    assert (folder / system.JOURNAL_MARK).is_file()
    assert ran == [["systemd-tmpfiles", "--create", "--prefix", str(folder)], ["journalctl", "--flush"]]
    assert system.main(["journal", "off"], var=tmp_path) == 0 and not folder.exists()
    folder.mkdir(parents=True)                                  # the system's own folder
    assert system.main(["journal", "off"], var=tmp_path) == 1 and folder.is_dir()


def test_the_command_and_its_answer(tmp_path):
    argv = system.command(["sensors", "on"], own=tmp_path / "system.py")
    assert argv[0] == "pkexec" and argv[2] == "-I" and argv[-3:] == [str(tmp_path / "system.py"), "sensors", "on"]
    assert system.answer(0, "anything") == ""
    assert "canceled" in system.answer(126, "") and "canceled" in system.answer(127, "")
    assert system.answer(1, "it broke\n") == "it broke"


@pytest.mark.parametrize("key", ["iommu", "mitigations"])
def test_kernel_argument_on_and_off_only_its_own(tmp_path, ran, monkeypatch, capsys, key):
    arg, mark = system.KARGS[key], system.karg_mark(tmp_path, key)
    args = ["rhgb", "quiet"]
    monkeypatch.setattr(system, "next_kargs", lambda: args)
    assert system.main([key, "off"], var=tmp_path) == 1 and ran == []          # not added by the quickfix
    assert system.main([key, "on"], var=tmp_path) == 0
    assert ran == [["rpm-ostree", "kargs", f"--append={arg}"]] and mark.read_text() == f"{arg}\n"
    assert "systemctl reboot" in capsys.readouterr().out
    args.append(arg)
    assert system.main([key, "on"], var=tmp_path) == 1 and len(ran) == 1       # there already
    assert system.main([key, "off"], var=tmp_path) == 0 and not mark.exists()
    assert ran[-1] == ["rpm-ostree", "kargs", f"--delete-if-present={arg}"]


def test_kernel_argument_set_by_hand_stays(tmp_path, ran, monkeypatch):
    monkeypatch.setattr(system, "next_kargs", lambda: ["mitigations=off"])     # the owner's board
    assert system.main(["mitigations", "on"], var=tmp_path) == 1
    assert system.main(["mitigations", "off"], var=tmp_path) == 1 and ran == []


def test_kernel_argument_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(system, "next_kargs", lambda: [])
    monkeypatch.setattr(system, "run", lambda argv: 1)                         # rpm-ostree refused
    assert system.main(["iommu", "on"], var=tmp_path) == 1
    assert not system.karg_mark(tmp_path, "iommu").exists()                    # no note of what is not there
    monkeypatch.setattr(system, "next_kargs", lambda: None)
    assert system.main(["iommu", "on"], var=tmp_path) == 1


def test_next_kargs_reads_rpm_ostree(monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, "rhgb mitigations=off\n"))
    assert system.next_kargs() == ["rhgb", "mitigations=off"]
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, ""))
    assert system.next_kargs() is None

    def missing(*a, **k):
        raise FileNotFoundError("rpm-ostree")
    monkeypatch.setattr(subprocess, "run", missing)
    assert system.next_kargs() is None
