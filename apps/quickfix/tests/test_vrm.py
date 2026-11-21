# SPDX-License-Identifier: GPL-3.0-or-later
"""VRM Sensors: the module's source is upstream's, unchanged; system.py puts root's copy and the service in place and
removes both; the window offers what applies; and the service's script builds the module for the running kernel."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess

import pytest

from quickfix import runner, state, system, windows

from test_state import put

KERNEL = os.uname().release


def test_the_source_is_upstreams_unchanged():
    for name, digest in system.VRM_SHA256.items():
        assert hashlib.sha256((system.VRM_SOURCE / name).read_bytes()).hexdigest() == digest, name
    version = f'MODULE_VERSION("{system.VRM_TAG[1:]}")'
    assert version in (system.VRM_SOURCE / "bc250_vrm_core.c").read_text()
    kbuild = (system.VRM_SOURCE / "Kbuild").read_text()
    assert "bc250_vrm-y := bc250_vrm_core.o nct6687_smbus.o" in kbuild and "LLVM=1" not in kbuild.split("\n", 3)[3]
    assert os.access(system.VRM_SOURCE / system.VRM_SCRIPT, os.X_OK)


def test_on_and_off(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(system, "run", lambda argv: calls.append(argv) or 0)
    etc, var = tmp_path / "etc", tmp_path / "var"
    assert system.main(["vrm", "on"], etc=etc, var=var) == 0
    folder, unit = var / system.VRM_DIR, etc / "systemd/system" / system.VRM_UNIT
    assert sorted(p.name for p in (folder / "src").iterdir()) == sorted([*system.VRM_SHA256, "Kbuild"])
    assert os.access(folder / system.VRM_SCRIPT, os.X_OK)
    text = unit.read_text()
    assert f"ExecStart=/usr/bin/bash {folder / system.VRM_SCRIPT} {folder}\n" in text
    assert "ExecStop=-/usr/sbin/rmmod bc250_vrm\n" in text and "WantedBy=multi-user.target" in text
    assert calls == [["systemctl", "daemon-reload"], ["systemctl", "enable", system.VRM_UNIT],
                     ["systemctl", "restart", system.VRM_UNIT]]
    calls.clear()
    assert system.main(["vrm", "off"], etc=etc, var=var) == 0
    assert not unit.exists() and not folder.exists()
    assert calls == [["systemctl", "disable", "--now", system.VRM_UNIT], ["systemctl", "daemon-reload"]]
    calls.clear()
    assert system.main(["vrm", "off"], etc=etc, var=var) == 0 and calls == []        # nothing of ours: nothing to do


def test_a_failed_start_shows_the_services_log(tmp_path, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(system, "run", lambda argv: calls.append(argv) or (1 if "restart" in argv else 0))
    assert system.main(["vrm", "on"], etc=tmp_path / "etc", var=tmp_path / "var") == 1
    assert calls[-1][:3] == ["journalctl", "-u", system.VRM_UNIT]
    assert "Turn off removes it" in capsys.readouterr().out


def test_incomplete_source_changes_nothing(tmp_path, capsys):
    assert system.vrm(tmp_path / "etc", tmp_path / "var", True, source=tmp_path / "none") == 1
    assert not (tmp_path / "etc").exists() and not (tmp_path / "var").exists()
    assert "not complete" in capsys.readouterr().out


def test_state(tmp_path):
    assert state.vrm(tmp_path, KERNEL) == state.Vrm(False, False, False, (), False)
    put(tmp_path, f"lib/modules/{KERNEL}/build/Makefile")
    put(tmp_path, f"etc/systemd/system/{system.VRM_UNIT}")
    put(tmp_path, f"var/{system.VRM_DIR}/{KERNEL}/bc250_vrm.ko")
    put(tmp_path, f"var/{system.VRM_DIR}/src/Kbuild")
    v = state.vrm(tmp_path, KERNEL)
    assert (v.ours, v.loaded, v.hwmon, v.built, v.can_build, v.on) == (True, False, False, (KERNEL,), True, True)
    (tmp_path / "sys/module/bc250_vrm").mkdir(parents=True)
    put(tmp_path, "sys/class/hwmon/hwmon3/name", "k10temp\n")
    assert state.vrm(tmp_path, KERNEL).loaded and not state.vrm(tmp_path, KERNEL).hwmon
    put(tmp_path, "sys/class/hwmon/hwmon4/name", "bc250_vrm\n")
    assert state.vrm(tmp_path, KERNEL).hwmon


def test_window(qapp, tmp_path):
    root, calls = tmp_path / "root", []

    def run_root(argv):
        calls.append(argv[4:])
        return runner.Result(0, "")
    window = windows.VrmWindow(run_root=run_root, root=root)
    assert not window.on_button.isEnabled() and not window.off_button.isEnabled()      # no kernel build files
    assert "cannot be built" in window.note.text() and window.state.label.text() == "Off"
    put(root, f"lib/modules/{KERNEL}/build/Makefile")
    window.refresh()
    assert window.on_button.isEnabled() and window.note.text() == ""
    window.on_button.click()
    assert calls == [["vrm", "on"]]
    put(root, f"etc/systemd/system/{system.VRM_UNIT}")
    window.refresh()
    assert window.on_button.isEnabled() and window.off_button.isEnabled()              # on, not loaded: try again
    assert f"journalctl -b -u {system.VRM_UNIT}" in window.note.text() and window.state.kind == "warn"
    assert "Turn on tries again" in window.note.text()
    (root / "sys/module/bc250_vrm").mkdir(parents=True)
    window.refresh()
    assert "did not answer" in window.note.text()
    put(root, "sys/class/hwmon/hwmon4/name", "bc250_vrm\n")
    window.refresh()
    assert window.note.text() == "" and window.state.kind == "ok"
    assert not window.on_button.isEnabled()                                            # loaded: not once more
    assert [window.boxes[c].value.text() for c in ("Module", "At boot", "Sensors")] == ["Loaded", "Yes", "bc250_vrm"]
    window.off_button.click()
    assert calls[-1] == ["vrm", "off"]
    (root / "etc/systemd/system" / system.VRM_UNIT).unlink()
    window.refresh()
    assert not window.off_button.isEnabled() and "something else" in window.note.text()


@pytest.mark.skipif(not os.path.isfile(f"/lib/modules/{KERNEL}/build/Makefile") or not shutil.which("gcc")
                    or not shutil.which("make"), reason="needs the running kernel's build files, gcc and make")
def test_the_script_builds_for_the_running_kernel_and_keeps_one_build(tmp_path):
    folder = tmp_path / "vrm"
    (folder / "src").mkdir(parents=True)
    for name in (*system.VRM_SHA256, "Kbuild"):
        shutil.copyfile(system.VRM_SOURCE / name, folder / "src" / name)
    put(folder, "6.0.0-old/bc250_vrm.ko")
    fake = put(tmp_path, "bin/insmod", '#!/bin/sh\necho "$1" > "$(dirname "$0")/loaded"\n')
    os.chmod(fake, 0o755)
    for name, body in (("selinuxenabled", "exit 0"), ("chcon", 'echo "$@" >> "$(dirname "$0")/labeled"')):
        os.chmod(put(tmp_path, f"bin/{name}", f"#!/bin/sh\n{body}\n"), 0o755)
    env = {**os.environ, "PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}"}
    script = [str(system.VRM_SOURCE / system.VRM_SCRIPT), str(folder)]
    done = subprocess.run(script, env=env, capture_output=True, text=True, timeout=300, check=False)
    if os.path.isdir("/sys/module/bc250_vrm"):
        assert done.returncode == 0 and "loaded already" in done.stdout
        return
    assert done.returncode == 0, done.stdout + done.stderr
    module = folder / KERNEL / "bc250_vrm.ko"
    assert module.is_file() and (tmp_path / "bin/loaded").read_text().strip() == str(module)
    assert sorted(p.name for p in folder.iterdir()) == sorted([KERNEL, "src"])       # the old build and build.* gone
    stamp = module.stat().st_mtime_ns
    assert subprocess.run(script, env=env, capture_output=True, timeout=60, check=False).returncode == 0
    assert module.stat().st_mtime_ns == stamp                                         # built once per kernel
    labeled = (tmp_path / "bin/labeled").read_text().splitlines()                     # SELinux: before every load
    assert labeled == [f"-t modules_object_t {module}"] * 2
