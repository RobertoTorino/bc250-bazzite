# SPDX-License-Identifier: GPL-3.0-or-later
"""The memory guard's files in a temp /etc: the suite's four drop-ins written and read back, Bazzite's own removing
them, and systemd-oomd restarted with them."""

import pytest

from vram_manager import guard


class Run:
    def __init__(self, fail: str = ""):
        self.calls, self.fail = [], fail

    def __call__(self, cmd):
        self.calls.append(cmd)
        return 1 if self.fail and self.fail in cmd else 0


def test_the_suites_guard_is_written_and_read_back(tmp_path):
    etc, run = tmp_path / "etc", Run()
    assert guard.read_guard(etc) == guard.BAZZITE
    result = guard.apply(guard.SUITE, etc, run)
    assert result == {"ok": True, "before": guard.BAZZITE, "after": guard.SUITE}
    assert (etc / guard.OOMD).read_text() == (guard.HEADER + "[OOM]\nSwapUsedLimit=90%\nDefaultMemoryPressureLimit=60%\n"
                                              "DefaultMemoryPressureDurationSec=10s\n")
    assert (etc / guard.ROOT_SLICE).read_text().endswith("[Slice]\nManagedOOMSwap=kill\n")
    assert (etc / guard.SESSION).read_text().endswith("[Service]\nManagedOOMMemoryPressure=kill\n"
                                                      "ManagedOOMMemoryPressureLimit=60%\n")
    assert (etc / guard.USER_SLICES).read_text().endswith("[Slice]\nManagedOOMMemoryPressure=kill\n"
                                                          "ManagedOOMMemoryPressureLimit=60%\n")
    assert (etc / guard.OOMD).stat().st_mode & 0o777 == 0o644
    assert run.calls == [["systemctl", "daemon-reload"], ["systemctl", "restart", "systemd-oomd.service"]]


def test_bazzites_own_removes_the_files_and_their_folders(tmp_path):
    etc = tmp_path / "etc"
    guard.apply(guard.SUITE, etc, Run())
    (etc / "systemd/oomd.conf.d/10-mine.conf").write_text("[OOM]\n")      # someone else's file stays, and its folder
    assert guard.apply(guard.BAZZITE, etc, Run())["after"] == guard.BAZZITE
    assert not any((etc / name).exists() for name in guard.FILES)
    assert not (etc / "systemd/system/-.slice.d").exists() and (etc / "systemd/oomd.conf.d/10-mine.conf").is_file()


def test_a_changed_file_is_not_the_suites_guard(tmp_path):
    etc = tmp_path / "etc"
    guard.apply(guard.SUITE, etc, Run())
    (etc / guard.SESSION).write_text("[Service]\nManagedOOMMemoryPressure=auto\n")
    assert guard.read_guard(etc) == guard.BAZZITE


def test_oomd_that_does_not_restart_is_an_error(tmp_path):
    with pytest.raises(guard.GuardError, match="did not restart"):
        guard.apply(guard.SUITE, tmp_path / "etc", Run(fail="restart"))
    with pytest.raises(guard.GuardError, match="Unknown guard"):
        guard.apply("other", tmp_path / "etc", Run())


def test_the_helper_refuses_without_root(capsys, monkeypatch):
    monkeypatch.setattr(guard.os, "geteuid", lambda: 1000)
    assert guard.main(["--guard", "suite"]) == 1
    assert '"The memory guard is written as root."' in capsys.readouterr().out
