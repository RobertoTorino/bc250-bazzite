# SPDX-License-Identifier: GPL-3.0-or-later
"""The helpers: one small window each, for one job. The portal shows each as a tile of its own in Utilities, from
the [[apps.helpers.helpers]] tables of its apps.toml, which name the same keys, names and summaries
(tests/test_catalog.py keeps the two the same)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Helper:
    key: str                    # "extras": bc250-helpers extras opens it
    name: str                   # "Test Extras"
    summary: str                # one line, on its tile and in the list
    changes_board: bool = False


HELPERS: tuple[Helper, ...] = (
    Helper("extras", "Test Extras",
           "The optional tools Board Test's tests use: which are there, and their installer."),
    Helper("mangohud", "MangoHud Config",
           "Open or create MangoHud's config, edit and save it; turn on the FPS log Board Test reads."),
    Helper("metrics", "Fix GPU Metrics",
           "Let the GPU governor write the real GPU load into gpu_metrics, for the overlays.", changes_board=True),
    Helper("sensors", "Sensors Module",
           "Load a driver for the board's SuperIO chip at every boot, for its temperatures and fans.",
           changes_board=True),
    Helper("mapcount", "Game Memory Map",
           "Raise vm.max_map_count, the number of memory areas a game may map.", changes_board=True),
    Helper("journal", "Persistent Journal",
           "Keep the system journal on the disk, so the logs of a boot that crashed can be read after it.",
           changes_board=True),
    Helper("iommu", "IOMMU Off",
           "Keep the kernel from using the board's IOMMU, which is broken on the BC-250 (amd_iommu=off).",
           changes_board=True),
    Helper("mitigations", "CPU Mitigations Off",
           "Turn off the kernel's CPU mitigations, which cost speed in games (mitigations=off).", changes_board=True),
)

BY_KEY = {helper.key: helper for helper in HELPERS}
