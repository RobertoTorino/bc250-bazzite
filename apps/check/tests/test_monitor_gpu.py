# SPDX-License-Identifier: GPL-3.0-or-later
"""The monitor's GPU load from the governor's gpu_metrics: hundredths of a percent, and the average of a few
snapshots, since one snapshot covers 16 ms and can fall between two frames. The values are the ones a board gave
under a full GPU load on 27-11-2026 (9688, 9844, 10000) and at idle (0, 156)."""

from __future__ import annotations

import struct

import pytest

from board_test import monitor


def metrics(activity: int, revision: int = 2) -> bytes:
    return bytes([0, 0, revision, 0]) + bytes(24) + struct.pack("<H", activity) + bytes(8)


@pytest.fixture
def board(tmp_path):
    proc, sys = tmp_path / "proc", tmp_path / "sys"
    dev = sys / "class/drm/card1/device"
    dev.mkdir(parents=True)
    (dev / "pp_dpm_sclk").write_text("0: 1000Mhz *\n")
    (proc / "self").mkdir(parents=True)
    (proc / "stat").write_text("cpu  1 2 3 4\n")
    (proc / "self/mountinfo").write_text("36 25 0:31 / /sys/devices/pci/gpu_metrics rw - tmpfs tmpfs rw\n")
    return proc, sys, dev


def sampler(board, values):
    """A sampler whose gpu_metrics holds the next of *values* at every snapshot; the waits are recorded."""
    proc, sys, dev = board
    left, waits = list(values), []

    def wait(seconds):
        waits.append(seconds)
        if left:
            (dev / "gpu_metrics").write_bytes(metrics(left.pop(0)))
    (dev / "gpu_metrics").write_bytes(metrics(left.pop(0)))
    return monitor.Sampler(proc, sys, proc, sleep=wait), waits


def test_a_full_load_reads_as_a_full_load(board):
    s, waits = sampler(board, [9688, 9844, 10000, 9844])
    load, source = s._gpu_sensor()
    assert source == "gpu_metrics" and load == pytest.approx(98.44)
    assert waits == [monitor.GPU_SNAPSHOT_GAP_S] * (monitor.GPU_SNAPSHOTS - 1)


def test_one_snapshot_between_two_frames_does_not_make_it_zero(board):
    s, _ = sampler(board, [10000, 0, 9688, 9844])
    assert s._gpu_sensor()[0] == pytest.approx(73.83)


def test_idle(board):
    s, _ = sampler(board, [0, 156, 0, 0])
    assert s._gpu_sensor() == (pytest.approx(0.39), "gpu_metrics")


def test_an_unpatched_value_or_another_layout_falls_back(board):
    s, _ = sampler(board, [0xFFFF])
    assert s._gpu_sensor() == (None, "fdinfo")
    (board[2] / "gpu_metrics").write_bytes(metrics(5000, revision=1))
    assert s._gpu_sensor() == (None, "fdinfo")


def test_the_kernels_own_sensor_comes_first(board):
    s, waits = sampler(board, [5000])
    (board[2] / "gpu_busy_percent").write_text("42\n")
    assert s._gpu_sensor() == (42.0, "sensor") and waits == []


def test_without_the_governors_mount_the_file_is_not_trusted(board):
    s, _ = sampler(board, [5000])
    (board[0] / "self/mountinfo").write_text("36 25 0:31 / /sys rw - sysfs sysfs rw\n")
    assert s._gpu_sensor() == (None, "fdinfo")
