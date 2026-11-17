# SPDX-License-Identifier: GPL-3.0-or-later
"""The quickfixes: one small window each, for one job. The portal shows each as a tile of its own in Utilities, from
the [[apps.quickfix.quickfixes]] tables of its apps.toml, which name the same keys, names and summaries
(tests/test_catalog.py keeps the two the same)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Quickfix:
    key: str                    # "extras": bc250-quickfix extras opens it
    name: str                   # "Test Extras"
    summary: str                # one line, on its tile and in the list
    changes_board: bool = False


QUICKFIXES: tuple[Quickfix, ...] = (
    Quickfix("extras", "Test Extras",
           "The optional tools Board Test's tests use: which are there, and their installer."),
    Quickfix("mangohud", "MangoHud Config",
           "Open or create MangoHud's config, edit and save it; turn on the FPS log Board Test reads."),
    Quickfix("metrics", "Fix GPU Metrics",
           "Let the GPU governor write the real GPU load into gpu_metrics, for the overlays.", changes_board=True),
    Quickfix("sensors", "Sensors Module",
           "Load a driver for the board's SuperIO chip at every boot, for its temperatures and fans.",
           changes_board=True),
    Quickfix("mapcount", "Game Memory Map",
           "Raise vm.max_map_count, the number of memory areas a game may map.", changes_board=True),
    Quickfix("journal", "Persistent Journal",
           "Keep the system journal on the disk, so the logs of a boot that crashed can be read after it.",
           changes_board=True),
    Quickfix("iommu", "IOMMU Off",
           "Keep the kernel from using the board's IOMMU, which is broken on the BC-250 (amd_iommu=off).",
           changes_board=True),
    Quickfix("mitigations", "CPU Mitigations Off",
           "Turn off the kernel's CPU mitigations, which cost speed in games (mitigations=off).", changes_board=True),
)

BY_KEY = {quickfix.key: quickfix for quickfix in QUICKFIXES}
