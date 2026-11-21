# SPDX-License-Identifier: GPL-3.0-or-later
"""The overlay window on a fake board: the rows, the formatting, temperature colors and the menu settings."""

from __future__ import annotations

from PyQt6.QtCore import Qt

from bc250_core.sensors import Fan, Rail, Reading, Sensors
from bc250_core.theme import ORANGE, RED
from system_overlay import overlay
from conftest import Clock, gpu_metrics, proc_stat, write


def make(board) -> overlay.OverlayWindow:
    return overlay.OverlayWindow(Sensors(board, governor=lambda: (1000, 1850), clock=Clock()))


def test_format_reading():
    rows = overlay.format_reading(Reading(
        cpu_load=12.4, cpu_mhz=3000, cpu_temp=72.1, gpu_load=45.5, gpu_mhz=2000, chip_watts=95.3, gpu_mv=1056,
        gpu_temp=91.0, governor=(1000, 1850), vram=(900_000_000, 6_000_000_000), ram=(4_700_000_000, 9_400_000_000),
        vrm_temp=85.0, cpu_rail=Rail(mv=1050, amps=32.5, temp=47.0), gpu_rail=Rail(mv=950, amps=None, temp=90.0),
        vin_mv=11850, nvme_temp=40.0, net=(2_100_000.0, 80_000.0), disk=(150_000_000.0, 0.0),
        fans=(Fan("Pump Fan", 1169),)), 60.0)
    assert rows == {
        "cpu": ("12 % · 3000 MHz", ""),
        "gpu": ("46 % · 2000 MHz", ""),                             # no current from the VRM: no GPU power
        "chip": ("95 W", ""),                                       # the driver's value is the whole chip's
        "governor": ("1000–1850 MHz", ""),
        "gpu_volt": ("1056 mV", ""),
        "cpu_rail": ("1050 mV · 32.5 A · 34 W", ""),
        "gpu_rail": ("950 mV", ""),                                # no current, so no power either
        "vin": ("11.85 V", ""),
        "vram": ("0.9 / 6.0 GB", ""),
        "ram": ("4.7 / 9.4 GB", ""),
        "refresh": ("60 Hz", ""),
        "fan": ("1169 RPM", ""),
        "cpu_temp": ("72 °C", ""),
        "gpu_temp": ("91 °C", RED),
        "vrm_temp": ("85 °C", ORANGE),
        "cpu_vrm_temp": ("47 °C", ""),
        "gpu_vrm_temp": ("90 °C", RED),
        "nvme_temp": ("40 °C", ""),
        "net": ("↓ 2.1 MB/s · ↑ 80.0 KB/s", ""),
        "disk": ("R 150.0 MB/s · W 0 B/s", ""),
    }
    assert [key for key, _ in overlay.ROWS] == list(rows)          # every row has a value, in order


def test_format_missing_values():
    rows = overlay.format_reading(Reading(cpu_mhz=2800), None)
    assert rows["cpu"] == ("2800 MHz", "")
    assert all(text == overlay.DASH for key, (text, _) in rows.items() if key != "cpu")


def test_warm_is_orange():
    assert overlay._temp(80.0) == ("80 °C", ORANGE)
    assert overlay._temp(79.4)[1] == ""


def test_window_shows_the_board(qapp, board):
    w = make(board)
    texts = {k: label.text() for k, label in w.values.items()}
    assert texts["gpu"] == "46 % · 2000 MHz" and texts["fan"] == "1169 RPM"       # no VRM module: no GPU power
    assert texts["chip"] == "95 W"                                                # the driver's value: the whole chip
    assert texts["governor"] == "1000–1850 MHz" and texts["vram"] == "0.9 / 6.0 GB"
    assert texts["cpu_temp"] == "72 °C" and texts["vrm_temp"] == "58 °C"
    assert texts["cpu"] == "3000 MHz" and texts["net"] == overlay.DASH      # these need a second reading
    write(board / "proc/stat", proc_stat(1000 + 50, 9000 + 150))
    w.refresh()
    assert w.values["cpu"].text() == "25 % · 3000 MHz"
    assert w.values["fan"].toolTip() == "Pump Fan: 1169 RPM"
    w.close()


def test_rail_rows_need_the_vrm_module(qapp, board):
    w = make(board)
    for key in overlay.RAIL_ROWS:
        assert w.values[key].text() == overlay.DASH and "bc250_vrm" in w.values[key].toolTip()
    vrm = board / "sys/class/hwmon/hwmon4"
    write(vrm / "name", "bc250_vrm")
    for name, label, value in (("in1", "CPU Voltage", 1050), ("in2", "GPU Core Voltage", 950),
                               ("curr1", "CPU Current", 32500), ("curr2", "GPU Current", 61200),
                               ("temp1", "CPU VRM Temp", 47000), ("temp2", "GPU VRM Temp", 55000)):
        write(vrm / f"{name}_label", label)
        write(vrm / f"{name}_input", str(value))
    w.refresh()
    assert w.values["cpu_rail"].text() == "1050 mV · 32.5 A · 34 W"
    assert w.values["gpu_rail"].text() == "950 mV · 61.2 A · 58 W"
    assert w.values["gpu"].text().endswith("· 58 W") and w.values["chip"].text() == "95 W"   # the GPU's own power
    assert w.values["cpu_vrm_temp"].text() == "47 °C" and w.values["gpu_vrm_temp"].text() == "55 °C"
    assert w.values["vrm_temp"].text() == "58 °C"                  # the Super I/O's own sensor stays
    assert all(w.values[key].toolTip() == "" for key in overlay.RAIL_ROWS)
    w.close()


def test_gpu_without_the_governors_patch(qapp, board):
    (board / "sys/class/hwmon/hwmon2/device/gpu_metrics").write_bytes(gpu_metrics(0xFFFF))
    w = make(board)
    assert w.values["gpu"].text() == "2000 MHz"
    assert "fix-metrics" in w.values["gpu"].toolTip()
    w.close()


def test_window_flags(qapp, board):
    w = make(board)
    flags = w.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint and flags & Qt.WindowType.WindowStaysOnTopHint
    assert w.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    w.set_on_top(False)
    assert not w.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    w.close()


def test_rows_can_be_hidden(qapp, board):
    w = make(board)
    w.show()
    height = w.height()
    rows = next(a.menu() for a in w.build_menu().actions() if a.text() == "Rows")
    next(a for a in rows.actions() if a.text() == "Disk").toggle()
    assert w.values["disk"].isHidden() and w.captions["disk"].isHidden()
    assert w.height() < height                                     # the window shrinks with it
    w.close()
    again = make(board)
    assert again.hidden_rows() == {"disk"} and again.values["disk"].isHidden()
    again.set_row_visible("disk", True)
    assert again.hidden_rows() == set()
    again.close()


def test_the_last_row_stays(qapp, board):
    w = make(board)
    for key, _ in overlay.ROWS:
        w.set_row_visible(key, False)
    assert len(w.hidden_rows()) == len(overlay.ROWS) - 1
    w.close()


def test_menu_choices_are_remembered(qapp, board):
    w = make(board)
    menu = w.build_menu()
    background = next(a.menu() for a in menu.actions() if a.text() == "Background")
    next(a for a in background.actions() if a.text() == "Very see-through").trigger()
    next(a for a in menu.actions() if a.text() == "Always on top").toggle()
    w.close()
    again = make(board)
    assert again.settings.get("background") == 35 and again.settings.get("on_top") is False
    assert not again.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    again.close()


def test_position_is_remembered(qapp, board):
    w = make(board)
    w.move(123, 45)
    w.close()
    again = make(board)
    assert (again.x(), again.y()) == (123, 45)
    again.close()
