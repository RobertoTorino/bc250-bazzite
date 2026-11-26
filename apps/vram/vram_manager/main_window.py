# SPDX-License-Identifier: GPL-3.0-or-later
"""The main window. The learning steps first (owner, 26-11-2026: a step window as Core Unlock's, the app learns the
settings from the games played, learn.py): the header with the settings they change, recording and the round, five
step rows with the current step's pill on its row, what the current step shows under them, and one row with Start
over, what comes next, Programs and Advanced. A change that needs a restart is written, then the board restarts after
a countdown, and the window opens again after the login (resume.py).

Advanced holds each setting on its own, as before: the memory the system has now (GTT, RAM) with a live map of it,
the VRAM split in CMOS with apply, undo and a read of the CMOS block, the GTT limit (ttm.pages_limit) in the next
boot's kernel arguments, the profiles, the swap layout of the next boot, the memory guard and recording.

A split is written to CMOS, a GTT limit to the next boot's kernel arguments with rpm-ostree, a swap layout to files
of the app's own in /etc (swap.py); all take effect at the next boot. The memory guard (guard.py) takes effect at
once. Recording (watch.py, service.py) goes on and off on its own. The window remembers each change with the boot it was made in, and after a reboot says whether the
kernel got it."""

from __future__ import annotations

import json
import sys
import time
from html import escape
from pathlib import Path
from dataclasses import asdict
from typing import Callable

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFrame, QGroupBox, QHBoxLayout, QHeaderView,
                             QLabel, QMainWindow, QMessageBox, QPushButton, QScrollArea, QSpinBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from bc250_core import SUITE_MANUAL_URL, window_title
from bc250_core import __version__ as CORE_VERSION
from bc250_core.platform import config_home, data_home
from bc250_core.settings import SettingsStore
from bc250_core.theme import ACCENT, BLUE, GREEN, GREY, ORANGE, PURPLE, RED, muted
from bc250_core.widgets import (ActionPill, AppHeader, InfoButton, MetricBox, RefreshButton, StatusText, TextDialog,
                                accent_button, hint_label, same_width)

from . import APP_ID, APP_NAME, INFO, LOGO_PATH, ROOT, __version__
from . import cmos, guard, kargs, learn, privileged, resume, service, swap, system, watch
from .memory_map import MemoryMap, gtt_ceiling
from .steps import STEPS, StepRow

MANUAL_URL = f"{SUITE_MANUAL_URL}apps/vram/"
REFRESH_MS = 2000                       # the memory map's live figures
RECOMMENDED_MB = 6144                   # board-test's recommendation (test 37): fixes framebuffer pin failures
SPLITS = (512, 1024, 2048, 4096, RECOMMENDED_MB, 8192, 10240)
FIRMWARE_MB = 512                       # the split the firmware starts with after a CMOS clear
SUITE_PAGES = 3014656                   # the suite's GTT limit, 11.5 GiB (Board Test, test 37)
PICK = object()                         # apply_ttm(): the limit the combo shows

SMOOTH = "smooth"
SMOOTH_PAGES = object()                 # PROFILES: the Smooth profile's limit, the RAM less watch.SPARE_MIB
SMOOTH_SWAP = swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=swap.SWAPPINESS[swap.ZRAM])
RESTART_SECS = 15                       # the countdown before the window restarts the board, as Core Unlock's

ABOUT = ("The learning steps find the memory settings that suit the games you play.<br><br>1. The start point is the "
         "Games profile, with Bazzite's swap and guard, and recording on.<br>2. The board restarts.<br>3. You play "
         f"as usual. The app records {learn.SESSIONS_A_ROUND} sessions.<br>4. The app proposes one change, from what "
         "it measured. The board restarts.<br>5. You play the same games again. The app compares the two rounds, and "
         "you keep the change or undo it.<br><br>Then step 4 again, until nothing measured asks for a change. "
         f"<a href='{MANUAL_URL}#learning-the-settings'>Wiki</a>")

# The profiles (owner, 01-11-2026): both values at once, each written only where it differs. The Smooth profile
# (owner, 26-11-2026) also writes the swap layout and the suite's memory guard.
PROFILES = {
    "defaults": ("Default profile", FIRMWARE_MB, None),
    "games": ("Games profile", RECOMMENDED_MB, SUITE_PAGES),
    SMOOTH: ("Smooth profile", RECOMMENDED_MB, SMOOTH_PAGES),
}


def tried_text(tried: int, kept: int, undone: int) -> str:
    if tried == 1:
        return f"The change was {'kept' if kept else 'undone'}."
    return f"{tried} changes tried. {kept} kept, {undone} undone."


class ManagerSettings(SettingsStore):
    DEFAULTS = {"pending_mb": 0, "pending_boot_id": "", "previous_mb": 0, "outcome": "",
                # the GTT limit written for the next boot: "" none, "default" (the argument removed) or the pages
                "pending_ttm": "", "pending_ttm_boot_id": "", "ttm_outcome": "",
                # the swap layout written for the next boot: "" none, or its key in swap.LAYOUTS
                "pending_swap": "", "pending_swap_boot_id": "", "swap_outcome": ""}


def backups_dir() -> Path:
    return data_home() / APP_ID / "backups"


def split_label(mb: int) -> str:
    text = f"{mb // 1024} GB" if mb >= 1024 else f"{mb} MB"
    return text + ("  (recommended for games)" if mb == RECOMMENDED_MB else "")


def ttm_label(pages: int | None) -> str:
    """A GTT limit in words: its size, or the kernel's default."""
    return f"{system.mib_text(kargs.mib(pages))} GTT limit" if pages else "kernel default GTT limit (half the RAM)"


def ttm_setting(pages: int | None) -> str:
    return "default" if pages is None else str(pages)


def ttm_pages(setting: str) -> int | None:
    return None if setting == "default" else int(setting)


class MainWindow(QMainWindow):
    def __init__(self, sys_root: Path = Path("/sys"), proc_root: Path = Path("/proc"),
                 runner: Callable[[list[str]], privileged.Result] = privileged.run,
                 commands: kargs.Run = privileged.run_command,
                 swapper: Callable[[list[str]], privileged.Result] = privileged.run_swap,
                 etc_root: Path = Path("/etc"), var_root: Path = Path("/var"),
                 guarder: Callable[[list[str]], privileged.Result] = privileged.run_guard,
                 config_dir: Path | None = None, sessions_file: Path | None = None,
                 python: str = sys.executable, app_root: Path = ROOT,
                 user_commands: kargs.Run = privileged.run_command, learn_file: Path | None = None,
                 restarter: Callable[[], bool] = resume.restart, clock: Callable[[], float] = time.time):
        super().__init__()
        self.resize(900, 900)
        self.sys_root = sys_root
        self.proc_root = proc_root
        self.runner = runner
        self.commands = commands                # runs rpm-ostree for the kernel arguments
        self.swapper = swapper                  # runs swap.py as root for the swap layout
        self.etc_root = etc_root
        self.var_root = var_root
        self.guarder = guarder                  # runs guard.py as root for the memory guard
        self.config_dir = config_dir or config_home()      # the sessions service's unit goes under it
        self.sessions_file = sessions_file or watch.sessions_path()
        self.python, self.app_root = python, app_root    # what the sessions service starts
        self.user_commands = user_commands      # runs systemctl --user for the guard and the sessions service
        self.sessions_seen: float | None = None  # the sessions file's time when last shown
        self.learn_file = learn_file or learn.learn_path()
        self.restarter, self.clock = restarter, clock
        self.state = learn.read_state(self.learn_file)
        self.settings = ManagerSettings(INFO, self)
        self.swap_setup = swap.read_setup(etc_root, var_root)
        self.memory = system.read_memory(sys_root, proc_root)
        self.next_boot = kargs.read_next_boot(commands)
        self.block_problem = ""                 # why CMOS must not be touched on this machine (cmos.board_problem)

        header = AppHeader(LOGO_PATH, APP_NAME, __version__)
        self.badge = StatusText()
        header.add_state(self.badge)
        header.add_action(InfoButton(ABOUT, "About the learning steps"))
        refresh = RefreshButton()
        refresh.clicked.connect(self.refresh)
        header.add_action(refresh)

        # The header (owner, 26-11-2026): the settings the learning changes, recording and the round.
        self.vram_box = MetricBox("VRAM split", PURPLE)
        self.ttm_box = MetricBox("GTT limit", BLUE)
        self.swap_box = MetricBox("Swap", GREY)
        self.record_box = MetricBox("Recording", GREY)
        self.round_box = MetricBox("Round", GREY)
        boxes = [self.vram_box, self.ttm_box, self.swap_box, self.record_box, self.round_box]
        for box in boxes:
            header.add_second(box)
        same_width(boxes)
        # Under Advanced: the GTT and the RAM, beside vm.swappiness.
        self.gtt_box = MetricBox("GTT (RAM the GPU borrows)", BLUE)
        self.ram_box = MetricBox("System RAM", GREY)
        self.details = hint_label("")

        self.finished_bar = QLabel()
        self.finished_bar.setWordWrap(True)
        self.finished_bar.setStyleSheet(f"background:{GREEN}; color:white; font-size:17px; font-weight:800; "
                                        "padding:12px; border-radius:8px;")
        self.finished_bar.hide()
        self.step_rows = [StepRow(i) for i in range(len(STEPS))]
        self.step_pill = ActionPill("Write", "Games profile", colour=ACCENT)
        self.step_pill.clicked.connect(lambda: self.step_action and self.step_action())
        self.step_action: Callable[[], None] | None = None
        self.content = QVBoxLayout()            # what the current step shows under the rows
        self.content.setSpacing(6)

        self.start_over_pill = ActionPill("Start over", "Back to the start point", colour=RED)
        self.start_over_pill.clicked.connect(self.start_over)
        self.next_label = QLabel()
        self.next_label.setWordWrap(True)
        self.next_label.setStyleSheet(f"font-size:13px; font-weight:600; color:{ACCENT};")
        self.hint = hint_label("")
        self.alt_pill = ActionPill("Undo", "Back to the round before")
        self.alt_pill.clicked.connect(lambda: self.alt_action and self.alt_action())
        self.alt_action: Callable[[], None] | None = None
        self.programs_button = ActionPill("Programs", "Memory over time",
                                          "The memory over time, and every program the service has seen")
        self.programs_button.clicked.connect(self.show_programs)
        self.advanced_pill = ActionPill("Advanced", "Show", "Each setting on its own, the memory map and CMOS")
        self.advanced_pill.clicked.connect(self.toggle_advanced)
        self.countdown = 0                      # the seconds before the window restarts the board
        self.note = ""                          # what just happened, over the hint
        self._tick = QTimer(self)
        self._tick.setInterval(1000)
        self._tick.timeout.connect(self.on_tick)

        lay_map_boxes = QHBoxLayout()
        for box in (self.gtt_box, self.ram_box):
            lay_map_boxes.addWidget(box)
        lay_map_boxes.addWidget(self.details, 1)
        mapped = QGroupBox("Memory map")
        self.map = MemoryMap(self.memory)
        lay_map = QVBoxLayout(mapped)
        lay_map.addLayout(lay_map_boxes)
        lay_map.addWidget(self.map)
        lay_map.addWidget(hint_label("Hover over a part to see what it is. When you pick a new split or GTT limit "
                                     "below, the next boot shows under the bar."))
        self.timer = QTimer(self)
        self.timer.setInterval(REFRESH_MS)
        self.timer.timeout.connect(self.refresh_usage)
        self.timer.start()
        split = QGroupBox("VRAM split in CMOS")
        self.combo = QComboBox()
        for mb in SPLITS:
            self.combo.addItem(split_label(mb), mb)
        self.combo.currentIndexChanged.connect(self.on_pick)
        self.apply_button = accent_button("Apply…", "Write this split to CMOS. It takes effect after a restart")
        self.apply_button.clicked.connect(self.apply_split)
        self.undo_button = QPushButton("Undo")
        self.undo_button.setToolTip("Write back the split from before the last change")
        self.undo_button.clicked.connect(self.undo)
        self.read_button = QPushButton("Read CMOS…")
        self.read_button.setToolTip("Show the memory block in CMOS and save a dump of it (read-only)")
        self.read_button.clicked.connect(self.read_cmos)
        self.split_info = InfoButton(
            "The split is the part of the 16 GB the GPU keeps for itself. The rest is system RAM. The GPU can "
            "borrow more from the RAM, which is the GTT. A larger split prevents the framebuffer pin failures that "
            "end a game session (Board Test, test 37). The firmware reads the new split at the next boot. Clearing "
            "CMOS with the jumper or the battery brings back the firmware's default. "
            f"<a href='{MANUAL_URL}'>Wiki</a>", "About the split")
        row = QHBoxLayout()
        row.addWidget(QLabel("New split:"))
        row.addWidget(self.combo, 1)
        for w in (self.apply_button, self.undo_button, self.read_button, self.split_info):
            row.addWidget(w)
        self.split_note = hint_label("")
        self.block_reason = hint_label("")
        lay_split = QVBoxLayout(split)
        lay_split.addLayout(row)
        lay_split.addWidget(self.split_note)
        lay_split.addWidget(self.block_reason)

        limit = QGroupBox("GTT limit on the kernel command line")
        self.ttm_combo = QComboBox()
        for label, pages in kargs.PRESETS:
            self.ttm_combo.addItem(label, pages)
        self.ttm_combo.currentIndexChanged.connect(self.on_pick)
        self.ttm_button = accent_button("Apply…", "Put this limit in the next boot's kernel arguments (rpm-ostree)")
        self.ttm_button.clicked.connect(self.apply_ttm)
        self.ttm_info = InfoButton(
            "The GTT limit is how much RAM the GPU may borrow on top of the split. amdgpu takes it from "
            "ttm.pages_limit on the kernel command line. Without the argument, the limit is half the RAM. The GTT "
            "never grows past the RAM. A small split needs the argument to reach the whole RAM. With a 6 GB split, "
            "11.5 GiB is already the whole RAM. The limit does not fix the framebuffer pin failures. Only a larger "
            "split does. rpm-ostree puts the limit in the next boot's kernel arguments as a new deployment. For the "
            "kernel default, rpm-ostree takes the argument out again. "
            f"<a href='{MANUAL_URL}#the-gtt-limit'>Wiki</a>", "About the GTT limit")
        row_ttm = QHBoxLayout()
        row_ttm.addWidget(QLabel("Next boot:"))
        row_ttm.addWidget(self.ttm_combo, 1)
        row_ttm.addWidget(self.ttm_button)
        row_ttm.addWidget(self.ttm_info)
        self.ttm_note = hint_label("")
        self.ttm_reason = hint_label("")
        lay_limit = QVBoxLayout(limit)
        lay_limit.addLayout(row_ttm)
        lay_limit.addWidget(self.ttm_note)
        lay_limit.addWidget(self.ttm_reason)

        profiles = QGroupBox("Profiles: the split, the GTT limit, the swap and the guard at once")
        self.profile_buttons: dict[str, QPushButton] = {}
        row_profiles = QHBoxLayout()
        for key in PROFILES:
            name, mb, pages, setup, _guard = self.profile_values(key)
            button = QPushButton(f"{name}…")
            button.setToolTip(f"{split_label(mb)} split, {ttm_label(pages)}"
                              + (", zram the size of the RAM, the suite's memory guard" if setup else ""))
            button.clicked.connect(lambda _c, k=key: self.apply_profile(k))
            self.profile_buttons[key] = button
            row_profiles.addWidget(button)
        row_profiles.addStretch(1)
        row_profiles.addWidget(InfoButton(
            f"The <b>Default profile</b> has the firmware's {split_label(FIRMWARE_MB)} split and the kernel's GTT "
            "limit, half the RAM. A board without changes runs like this. The <b>Games profile</b> has the "
            f"{split_label(RECOMMENDED_MB)} split and the 11.5 GiB limit. The split prevents the framebuffer pin "
            "failures (Board Test, test 37). The limit is all the RAM with that split. The suite's boards run this "
            "profile. The <b>Smooth profile</b> has the 6 GB split and a GTT limit of the RAM less 2 GiB. It also "
            "sets zram the size of the RAM and the suite's memory guard. The Default and Games profiles leave the swap "
            "and the guard as they are. A profile writes only what differs from the board. Each part asks for your "
            "password. The split, the limit and the swap take effect after you restart the board. The guard takes "
            f"effect at once. <a href='{MANUAL_URL}#profiles'>Wiki</a>", "About the profiles"))
        lay_profiles = QVBoxLayout(profiles)
        lay_profiles.addLayout(row_profiles)

        layout_box = QGroupBox("Swap layout")
        self.layout_combo = QComboBox()
        for key, label in swap.LAYOUTS.items():
            self.layout_combo.addItem(label, key)
        self.layout_combo.currentIndexChanged.connect(self.on_layout)
        self.swap_button = accent_button("Apply…", "Write this swap layout. It takes effect after a restart")
        self.swap_button.clicked.connect(self.apply_swap)
        self.delete_button = QPushButton("Delete swap file…")
        self.delete_button.clicked.connect(self.delete_swap_file)
        self.swap_info = InfoButton(
            "Swap is where Linux puts pages that do not fit in the RAM. <b>zram</b> keeps them in the RAM, "
            "compressed. That is fast, and it is what Bazzite does. <b>zswap</b> first keeps them compressed in the "
            "RAM. It moves the oldest pages to a swap file on the disk, which holds more than the RAM can. "
            "<b>vm.swappiness</b> is how readily Linux swaps, from 0 to 200. A layout is a few files of the app's "
            "own. Removing them brings Bazzite's own layout back. "
            f"<a href='{MANUAL_URL}#the-swap-layout'>Wiki</a>", "About the swap layout")
        row_swap = QHBoxLayout()
        row_swap.addWidget(QLabel("Next boot:"))
        row_swap.addWidget(self.layout_combo, 1)
        for w in (self.swap_button, self.delete_button, self.swap_info):
            row_swap.addWidget(w)
        self.size_label = QLabel("")
        self.size_combo = QComboBox()
        self.size_combo.currentIndexChanged.connect(self.on_swap_pick)
        self.compressor_combo = QComboBox()
        self.compressor_combo.currentIndexChanged.connect(self.on_swap_pick)
        self.swappiness_spin = QSpinBox()
        self.swappiness_spin.setRange(0, 200)
        self.swappiness_spin.setToolTip("How readily Linux moves pages out of the RAM into swap, 0 to 200")
        self.swappiness_spin.valueChanged.connect(self.on_swap_pick)
        self.swap_options = QWidget()
        row_options = QHBoxLayout(self.swap_options)
        row_options.setContentsMargins(0, 0, 0, 0)
        row_options.addWidget(self.size_label)
        row_options.addWidget(self.size_combo, 1)
        row_options.addWidget(QLabel("Compressor:"))
        row_options.addWidget(self.compressor_combo)
        row_options.addWidget(QLabel("vm.swappiness:"))
        row_options.addWidget(self.swappiness_spin)
        self.swap_note = hint_label("")
        self.swap_reason = hint_label("")
        lay_swap = QVBoxLayout(layout_box)
        lay_swap.addLayout(row_swap)
        lay_swap.addWidget(self.swap_options)
        lay_swap.addWidget(self.swap_note)
        lay_swap.addWidget(self.swap_reason)

        guard_box = QGroupBox("Memory guard: what ends a program before the board freezes")
        self.guard_combo = QComboBox()
        for key, label in guard.GUARDS.items():
            self.guard_combo.addItem(label, key)
        self.guard_combo.currentIndexChanged.connect(self.on_guard_pick)
        self.guard_button = accent_button("Apply…", "Write this guard. It takes effect at once")
        self.guard_button.clicked.connect(lambda: self.apply_guard())
        row_guard = QHBoxLayout()
        row_guard.addWidget(QLabel("Guard:"))
        row_guard.addWidget(self.guard_combo, 1)
        row_guard.addWidget(self.guard_button)
        row_guard.addWidget(InfoButton(
            "When the RAM and the swap run out, the board stalls until the kernel ends a program. That can take "
            "minutes. systemd-oomd ends the program that uses the most memory before that. <b>Bazzite's own</b> guard "
            "acts at 80% memory pressure for 20 s and does not watch the swap. <b>The suite's guard</b> acts at 60% for "
            "10 s, or when the swap is 90% full. It takes effect at once, without a restart. "
            f"<a href='{MANUAL_URL}#the-memory-guard'>Wiki</a>", "About the memory guard"))
        lay_guard = QVBoxLayout(guard_box)
        lay_guard.addLayout(row_guard)

        record_group = QGroupBox("Recording")
        self.record_pill = ActionPill("Turn on", "Recording")
        self.record_pill.clicked.connect(self.toggle_recording)
        row_record = QHBoxLayout()
        row_record.addWidget(hint_label("A user service records the memory while each program of 1 GiB or more "
                                        "runs. The learning steps need it. It needs no password."), 1)
        row_record.addWidget(self.record_pill)
        row_record.addWidget(InfoButton(
            "The service looks every two seconds. It records the RAM, the VRAM and the swap in use, what the GPU "
            "borrows, the wait for memory and the CPU load. The CPU load is for context only. A program that takes "
            "1 GiB or more becomes a session, with how it ended. It runs with your desktop session, whatever the "
            f"memory guard. <a href='{MANUAL_URL}#recording'>Wiki</a>", "About recording"))
        QVBoxLayout(record_group).addLayout(row_record)

        self.advanced = QWidget()
        lay_advanced = QVBoxLayout(self.advanced)
        lay_advanced.setContentsMargins(0, 0, 0, 0)
        for box in (mapped, split, limit, profiles, layout_box, guard_box, record_group):
            lay_advanced.addWidget(box)
        self.advanced.hide()

        bottom = QHBoxLayout()
        bottom.setSpacing(16)
        bottom.addWidget(self.start_over_pill)
        side = QVBoxLayout()
        side.setSpacing(4)
        side.addStretch(1)
        side.addWidget(self.next_label)
        side.addWidget(self.hint)
        side.addStretch(1)
        bottom.addLayout(side, 1)
        right = QHBoxLayout()
        right.setSpacing(8)
        for pill in (self.alt_pill, self.programs_button, self.advanced_pill):
            right.addWidget(pill)
        same_width([self.programs_button, self.advanced_pill])
        bottom.addLayout(right)

        # The page scrolls when the window is lower than it (Advanced is long), as Core Unlock's.
        body = QWidget()
        lay = QVBoxLayout(body)
        lay.setSpacing(10)
        lay.addLayout(header)
        lay.addWidget(self.finished_bar)
        for row in self.step_rows:
            lay.addWidget(row)
        lay.addLayout(self.content)
        lay.addLayout(bottom)
        lay.addWidget(self.advanced)
        lay.addStretch(1)
        version = QLabel(f"{APP_NAME} {__version__} · core {CORE_VERSION} · CMOS, the kernel arguments, the swap "
                         "layout and the guard are written only when you apply")
        version.setStyleSheet("color:palette(placeholder-text);")
        lay.addWidget(version, 0, Qt.AlignmentFlag.AlignRight)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(body)
        self.setCentralWidget(scroll)

        geometry = self.settings.window_state("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        self.check_reboot()
        self.check_ttm_reboot()
        self.check_swap_reboot()
        self.refresh_usage()
        self.refresh()

    # --- State ------------------------------------------------------------------------------------------------

    def check_reboot(self) -> None:
        """After a reboot, a pending split either reached the kernel or did not; remember which and clear it."""
        pending = self.settings.get("pending_mb")
        if not pending or self.settings.get("pending_boot_id") == self.memory.boot_id:
            return
        got = self.memory.vram_mib
        if got == pending:
            self.settings.set("outcome", f"The {split_label(pending)} split from the last change is active.")
        else:
            self.settings.set("outcome", f"The {pending} MB split was written, but the kernel got "
                                         f"{system.mib_text(got)}. Read CMOS to see what the firmware kept.")
        self.settings.set("pending_mb", 0)
        self.settings.set("pending_boot_id", "")

    def check_ttm_reboot(self) -> None:
        """The same for a GTT limit written for the next boot: did this boot's command line get it?"""
        pending = self.settings.get("pending_ttm")
        if not pending or self.settings.get("pending_ttm_boot_id") == self.memory.boot_id:
            return
        wanted, got = ttm_pages(pending), self.memory.ttm_cmdline_pages
        if got == wanted:
            borrow = (f" The GPU may borrow up to {system.mib_text(self.memory.gtt_mib)} of the RAM"
                      + (", all of it." if self.memory.gtt_capped else ".")) if self.memory.gtt_mib else ""
            self.settings.set("ttm_outcome", f"The {ttm_label(wanted)} from the last change is active.{borrow}")
        else:
            self.settings.set("ttm_outcome", f"The {ttm_label(wanted)} was written for the next boot, but this boot "
                                             f"has the {ttm_label(got)}. The board may have started another "
                                             "deployment.")
        self.settings.set("pending_ttm", "")
        self.settings.set("pending_ttm_boot_id", "")

    def check_swap_reboot(self) -> None:
        """The same for a swap layout: does this boot's swap look like it?"""
        pending = self.settings.get("pending_swap")
        if not pending or self.settings.get("pending_swap_boot_id") == self.memory.boot_id:
            return
        m = self.memory
        got = {swap.ZRAM: m.zram and not m.zswap, swap.ZSWAP_FILE: m.zswap and m.disk_swap and not m.zram}
        if got.get(pending, True):
            self.settings.set("swap_outcome", "The swap layout from the last change is active.")
        else:
            self.settings.set("swap_outcome", f"The swap layout was written, but this boot's swap is {m.swap_text}. "
                                              "Apply it again, or see the wiki for the files to check.")
        self.settings.set("pending_swap", "")
        self.settings.set("pending_swap_boot_id", "")

    def on_pick(self) -> None:
        """A split or a GTT limit picked: the memory map's next boot with them, where they differ from this boot's,
        and Apply only for what is not written yet (owner, 01-11-2026: what is applied cannot be applied again)."""
        self.map.set_preview(self.combo.currentData(), kargs.mib(self.ttm_combo.currentData()))
        self.apply_button.setEnabled(not self.block_problem and self.combo.currentData() != self.written_split())
        self.ttm_button.setEnabled(not self.next_boot.error and self.ttm_combo.currentData() != self.next_boot.pages)
        for key, button in self.profile_buttons.items():
            button.setEnabled(bool(self.profile_steps(key)))

    def written_split(self) -> int | None:
        """The split in CMOS: the one waiting for a reboot, else the one this boot got."""
        return self.settings.get("pending_mb") or self.memory.vram_mib

    def profile_values(self, key: str) -> tuple[str, int, int | None, swap.Setup | None, str | None]:
        """A profile's name, split and limit, and the swap layout and guard it also writes (None: left as they
        are). The Smooth profile's limit is the RAM the split leaves, less watch.SPARE_MIB."""
        name, mb, pages = PROFILES[key]
        if pages is not SMOOTH_PAGES:
            return name, mb, pages, None, None
        m = self.memory
        ram = (m.vram_mib + m.ram_mib - mb) if m.vram_mib and m.ram_mib else (m.ram_mib or 0)
        names = self.zram_compressors()
        setup = SMOOTH_SWAP if SMOOTH_SWAP.compressor in names else swap.Setup(
            swap.ZRAM, SMOOTH_SWAP.zram_size, names[0], swappiness=SMOOTH_SWAP.swappiness)
        return name, mb, watch.gtt_pages(ram) if ram else None, setup, guard.SUITE

    def profile_steps(self, key: str) -> list[str]:
        """What a profile would write, in words: the split (when CMOS can be written and it differs), the limit
        (when rpm-ostree works and it differs), and for the Smooth profile the swap layout and the guard where they
        differ. Empty when the board has the profile, or nothing can be written."""
        _name, mb, pages, setup, wanted = self.profile_values(key)
        steps = []
        if not self.block_problem and mb != self.written_split():
            steps.append(f"the {split_label(mb)} split to CMOS")
        if not self.next_boot.error and pages != self.next_boot.pages:
            steps.append(f"the {ttm_label(pages)} to the next boot's kernel arguments")
        if setup is not None and setup != self.swap_setup:
            steps.append(f"zram the size of the RAM with vm.swappiness {setup.swappiness} for the next boot")
        if wanted is not None and wanted != guard.read_guard(self.etc_root):
            steps.append("the suite's memory guard")
        return steps

    def refresh_usage(self) -> None:
        self.map.set_usage(system.read_usage(self.sys_root, self.proc_root))
        self.refresh_sessions()

    def refresh(self) -> None:
        m = self.memory
        self.vram_box.set_value(system.mib_text(m.vram_mib))
        self.gtt_box.set_value(system.mib_text(m.gtt_mib))
        self.ram_box.set_value(system.mib_text(m.ram_mib))
        self.swap_box.set_value(m.swap_text)
        self.ttm_box.set_value(system.mib_text(m.ttm_limit_mib), self.ttm_tip())
        self.ttm_box.caption.setText("GTT limit" if m.ttm_on_cmdline else "GTT limit (default)")
        self.gtt_box.caption.setText("GTT: all the RAM" if m.gtt_capped else "GTT (RAM the GPU borrows)")
        self.details.setText(f"vm.swappiness {m.swappiness}" if m.swappiness is not None else "")
        self.details.setToolTip("How readily Linux moves pages out of the RAM into swap, from 0 to 200. At 0, Linux "
                                "swaps only when the RAM is full. 60 is the kernel's default. At 100 and more, Linux "
                                "prefers swap to the file cache. That is usual with zram, where swap is RAM. Swap "
                                "layout sets it for the next boot.")
        self.details.setVisible(bool(self.details.text()))

        pending = self.settings.get("pending_mb")
        outcome = self.settings.get("outcome")
        swap_pending = self.refresh_swap()
        ttm_pending = self.refresh_ttm() or swap_pending
        if pending:
            self.badge.set_status("Reboot to apply", "warn", f"{split_label(pending)} is in CMOS. The firmware "
                                                               "reads it at the next boot.")
            self.split_note.setText(f"<b>{escape(split_label(pending))}</b> is written to CMOS and takes effect after "
                                    "a reboot.")
        else:
            if ttm_pending:
                self.badge.set_status("Reboot to apply", "warn", ttm_pending)
            else:
                current = f"{system.mib_text(m.vram_mib)} split" if m.vram_mib else "Unknown split"
                kind = "ok" if m.vram_mib == RECOMMENDED_MB else "info" if m.vram_mib else "neutral"
                self.badge.set_status(current, kind)
            self.split_note.setText(escape(outcome))
        self.split_note.setVisible(bool(self.split_note.text()))
        target = pending or m.vram_mib
        if target in SPLITS:
            self.combo.setCurrentIndex(SPLITS.index(target))

        problem = cmos.board_problem(self.sys_root)
        self.block_problem = problem
        self.block_reason.setText(escape(problem))
        self.block_reason.setVisible(bool(problem))
        self.read_button.setEnabled(not problem)
        previous = self.settings.get("previous_mb")
        self.undo_button.setEnabled(not problem and bool(previous) and previous != (pending or m.vram_mib))
        self.undo_button.setToolTip(f"Write back {split_label(previous)}" if previous else "Nothing to undo yet")
        self.refresh_guard()
        self.on_pick()
        self.refresh_sessions(force=True)

    def ttm_tip(self) -> str:
        m = self.memory
        if m.ttm_limit_mib is None:
            return "The kernel's ttm module is not loaded, so there is no limit to read."
        if not m.ttm_on_cmdline:
            return ("This is the kernel's default, half the RAM. ttm.pages_limit is not on the kernel command line. "
                    f"The GPU may borrow up to {system.mib_text(m.gtt_mib)} of the RAM.")
        text = f"ttm.pages_limit={m.ttm_cmdline_pages} on the kernel command line, {system.mib_text(m.ttm_limit_mib)}."
        if m.gtt_capped:
            return text + (f" That is above the RAM, so the GTT is all the RAM, {system.mib_text(m.gtt_mib)}. A "
                           "higher limit cannot give the GPU more.")
        return text + f" The GPU may borrow up to {system.mib_text(m.gtt_mib)} of the RAM."

    def refresh_ttm(self) -> str:
        """The GTT limit box: the next boot's limit in the combo (added when it is none of the presets), the note
        under it, and the reason when rpm-ostree cannot be used. Returns the note when a change waits for a reboot,
        else ""."""
        m, nxt = self.memory, self.next_boot
        waiting = ""
        if nxt.error:
            self.ttm_note.setText(escape(self.settings.get("ttm_outcome")))
            self.ttm_reason.setText(escape(nxt.error))
        else:
            if self.ttm_combo.findData(nxt.pages) < 0:
                self.ttm_combo.addItem(f"{system.mib_text(kargs.mib(nxt.pages))}, as set now", nxt.pages)
            self.ttm_combo.setCurrentIndex(self.ttm_combo.findData(nxt.pages))
            if nxt.pages != m.ttm_cmdline_pages:
                waiting = (f"The {ttm_label(nxt.pages)} is in the next boot's kernel arguments. Restart the board "
                           "to use it. The app does not restart the board by itself.")
                self.ttm_note.setText(f"<b>{escape(waiting)}</b>")
                self.ttm_box.caption.setText(f"next boot {system.mib_text(kargs.mib(nxt.pages))}" if nxt.pages
                                             else "next boot: default")
            else:
                self.ttm_note.setText(escape(self.settings.get("ttm_outcome")))
            self.ttm_reason.setText("")
        self.ttm_note.setVisible(bool(self.ttm_note.text()))
        self.ttm_reason.setVisible(bool(self.ttm_reason.text()))
        return waiting

    # --- The swap layout --------------------------------------------------------------------------------------

    def zram_compressors(self) -> list[str]:
        """What the board's zram device offers; the usual three when no device is there to ask."""
        for path in sorted((self.sys_root / "block").glob("zram*/comp_algorithm")):
            try:
                names = path.read_text().replace("[", "").replace("]", "").split()
            except OSError:
                continue
            if names:
                return names
        return list(swap.ZRAM_COMPRESSORS)

    def fill_swap_options(self) -> None:
        """The second row for the layout picked: its sizes, compressors and swappiness, with the written layout's
        values when it is that one, else the proposal."""
        key, written = self.layout_combo.currentData(), self.swap_setup
        same = written.layout == key
        ram = self.memory.ram_mib or 0
        for widget in (self.size_combo, self.compressor_combo, self.swappiness_spin):
            widget.blockSignals(True)
        self.size_combo.clear()
        self.compressor_combo.clear()
        if key == swap.ZRAM:
            self.size_label.setText("zram size:")
            for label, size, factor in swap.ZRAM_SIZES:
                self.size_combo.addItem(f"{label} ({system.mib_text(int(ram * factor))})" if ram else label, size)
            names, size, first = self.zram_compressors(), written.zram_size if same else "ram / 2", "zstd"
        else:
            self.size_label.setText("Swap file:")
            for gib in swap.FILE_SIZES_GIB:
                self.size_combo.addItem(f"{gib} GiB", gib * 1024)
            if ram and self.size_combo.findData(ram) < 0:
                self.size_combo.addItem(f"As large as the RAM ({system.mib_text(ram)})", ram)
            running = system._selected(system._read(self.sys_root / "module/zswap/parameters/compressor"))
            names = list(dict.fromkeys([*swap.ZSWAP_COMPRESSORS, *([running] if running else [])]))
            size, first = written.file_mib if same and written.file_mib else 8 * 1024, "zstd"
            if self.size_combo.findData(size) < 0:
                self.size_combo.addItem(f"{system.mib_text(size)}, as made", size)
        if same and written.compressor and written.compressor not in names:
            names.append(written.compressor)
        self.compressor_combo.addItems(names)
        self.size_combo.setCurrentIndex(max(self.size_combo.findData(size), 0))
        wanted = written.compressor if same and written.compressor else first
        self.compressor_combo.setCurrentIndex(max(self.compressor_combo.findText(wanted), 0))
        value = written.swappiness if same and written.swappiness is not None else swap.SWAPPINESS.get(key)
        self.swappiness_spin.setValue(value if value is not None else 0)
        for widget in (self.size_combo, self.compressor_combo, self.swappiness_spin):
            widget.blockSignals(False)
        self.swap_options.setVisible(key != swap.BAZZITE)

    def picked_setup(self) -> swap.Setup:
        key = self.layout_combo.currentData()
        if key == swap.BAZZITE:
            return swap.Setup()
        return swap.Setup(key, self.size_combo.currentData() if key == swap.ZRAM else "",
                          self.compressor_combo.currentText(),
                          self.size_combo.currentData() if key == swap.ZSWAP_FILE else 0, self.swappiness_spin.value())

    def on_layout(self) -> None:
        self.fill_swap_options()
        self.on_swap_pick()

    def on_swap_pick(self) -> None:
        """Apply only for a layout that is not written yet and that can be written; else the reason."""
        picked = self.picked_setup()
        problem = ""
        if picked.layout == swap.ZSWAP_FILE:
            problem = swap.file_problem(picked.file_mib, self.var_root, self.proc_root)
        self.swap_button.setEnabled(not problem and picked != self.swap_setup)
        self.swap_reason.setText(escape(problem))
        self.swap_reason.setVisible(bool(problem))

    def refresh_swap(self) -> str:
        """The swap layout box: the written layout in the combos, the note under them, and Delete swap file while
        a file is left that no layout uses. Returns the note when a layout waits for a restart, else ""."""
        self.swap_setup = written = swap.read_setup(self.etc_root, self.var_root)
        self.layout_combo.blockSignals(True)
        self.layout_combo.setCurrentIndex(self.layout_combo.findData(written.layout))
        self.layout_combo.blockSignals(False)
        self.fill_swap_options()
        waiting = ""
        if self.settings.get("pending_swap"):
            waiting = "The swap layout is written. Restart the board to use it."
            self.swap_note.setText(f"<b>{escape(waiting)}</b>")
        else:
            self.swap_note.setText(escape(self.settings.get("swap_outcome"), quote=False))
        self.swap_note.setVisible(bool(self.swap_note.text()))
        left = swap.file_mib(self.var_root) if written.layout != swap.ZSWAP_FILE else 0
        in_use = swap.file_in_use(self.var_root, self.proc_root)
        self.delete_button.setVisible(bool(left))
        self.delete_button.setEnabled(not in_use)
        self.delete_button.setToolTip("The swap file is in use until the board restarts" if in_use else
                                      f"Delete {self.var_root / swap.SWAP_FILE}, {system.mib_text(left)}")
        self.on_swap_pick()
        return waiting

    def apply_swap(self) -> None:
        setup = self.picked_setup()
        if setup.layout == swap.BAZZITE:
            facts = ["It removes the app's own swap files from /etc.", "zram is then as Bazzite sets it."]
        elif setup.layout == swap.ZRAM:
            label = self.size_combo.currentText()
            facts = [f"zram gets the size {label[0].lower() + label[1:]}, with {setup.compressor}.",
                     f"vm.swappiness becomes {setup.swappiness}."]
        else:
            path = self.var_root / swap.SWAP_FILE
            have = swap.file_mib(self.var_root) == setup.file_mib
            facts = [f"It {'keeps' if have else 'makes'} the swap file {path} of {system.mib_text(setup.file_mib)}.",
                     f"zswap is turned on, with {setup.compressor}.", "zram is turned off.",
                     f"vm.swappiness becomes {setup.swappiness}."]
        answer = QMessageBox.question(
            self, window_title("Swap layout"),
            f"Write the swap layout \"{swap.LAYOUTS[setup.layout]}\" for the next boot?\n\n" + "\n".join(facts)
            + "\nIt takes effect after you restart the board.\n\nYou will be asked for your password.")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.write_swap(setup, "Swap layout")

    def write_swap(self, setup: swap.Setup, title: str) -> bool:
        """Writes the layout for the next boot through the helper. True when it is written."""
        result = self.swapper(swap.arguments(setup))
        if not result.ok:
            QMessageBox.warning(self, window_title(title), result.error or "The write failed.")
            self.on_swap_pick()
            return False
        self.settings.set("pending_swap", setup.layout)
        self.settings.set("pending_swap_boot_id", self.memory.boot_id)
        self.settings.set("swap_outcome", "")
        self.refresh()
        return True

    def delete_swap_file(self) -> None:
        path = self.var_root / swap.SWAP_FILE
        answer = QMessageBox.question(
            self, window_title("Delete swap file"),
            f"Delete the swap file {path}?\n\nNo layout uses it anymore.\n"
            f"It frees {system.mib_text(swap.file_mib(self.var_root))} on the disk.\n\n"
            "You will be asked for your password.")
        if answer != QMessageBox.StandardButton.Yes:
            return
        result = self.swapper(["--delete-file"])
        if not result.ok:
            QMessageBox.warning(self, window_title("Delete swap file"), result.error or "The file was not deleted.")
        self.refresh()

    # --- The memory guard and recording ------------------------------------------------------------------------

    def refresh_guard(self) -> None:
        """The guard box: the written guard in the combo."""
        written = guard.read_guard(self.etc_root)
        self.guard_combo.blockSignals(True)
        self.guard_combo.setCurrentIndex(self.guard_combo.findData(written))
        self.guard_combo.blockSignals(False)
        self.on_guard_pick()

    def on_guard_pick(self) -> None:
        self.guard_button.setEnabled(self.guard_combo.currentData() != guard.read_guard(self.etc_root))

    def apply_guard(self, key: str | None = None, ask: bool = True) -> bool:
        """Writes the guard (the combo's, or *key*) and reloads the user manager. True when it is written."""
        key = key or self.guard_combo.currentData()
        if ask:
            if key == guard.SUITE:
                facts = [f"systemd-oomd ends the program that uses the most memory when memory pressure stays above "
                         f"{guard.PRESSURE_PERCENT}% for {guard.DURATION_S} s.",
                         f"It does the same when the swap is {guard.SWAP_PERCENT}% full."]
            else:
                facts = ["It removes the app's own guard files from /etc.", "systemd-oomd then works as Bazzite sets it."]
            answer = QMessageBox.question(
                self, window_title("Memory guard"),
                f"Write the memory guard \"{guard.GUARDS[key]}\"?\n\n" + "\n".join(facts)
                + "\nIt takes effect at once, without a restart.\n\nYou will be asked for your password.")
            if answer != QMessageBox.StandardButton.Yes:
                return False
        result = self.guarder(["--guard", key])
        if not result.ok:
            QMessageBox.warning(self, window_title("Memory guard"), result.error or "The write failed.")
            self.refresh_guard()
            return False
        self.user_commands(["systemctl", "--user", "daemon-reload"])    # the session's slices to systemd-oomd again
        self.refresh_guard()
        self.on_pick()                          # the profiles: the Smooth one may have nothing left to write
        self.render_steps()
        return True

    def recording(self) -> bool:
        return service.installed(self.config_dir)

    def set_recording(self, on: bool) -> bool:
        """Turns the recording service on or off. True when it is as asked."""
        if on:
            error = service.enable(self.user_commands, self.config_dir, self.python, self.app_root)
            if error:
                QMessageBox.warning(self, window_title("Recording"), error)
                return False
        else:
            service.disable(self.user_commands, self.config_dir)
        self.render_steps()
        return True

    def toggle_recording(self) -> None:
        self.set_recording(not self.recording())

    def refresh_sessions(self, force: bool = False) -> None:
        """The steps again when the sessions file changed: a session recorded moves a round on."""
        try:
            changed = self.sessions_file.stat().st_mtime
        except OSError:
            changed = 0.0
        if not force and changed == self.sessions_seen:
            return
        self.sessions_seen = changed
        self.render_steps()

    def show_programs(self) -> None:
        """The Programs window, from the records beside the sessions file."""
        from .programs_dialog import ProgramsDialog
        folder = self.sessions_file.parent
        ProgramsDialog(self, self.memory.ram_mib or 0, folder / watch.history_path().name,
                       folder / watch.programs_path().name, self.sessions_file, folder / watch.closes_path().name,
                       manual_url=MANUAL_URL).exec()

    def toggle_advanced(self) -> None:
        self.advanced.setVisible(self.advanced.isHidden())
        self.advanced_pill.caption.setText("Hide" if self.advanced.isVisible() else "Show")

    # --- The learning steps ------------------------------------------------------------------------------------

    def board_settings(self) -> dict:
        """What the board runs from the next boot on: the split in CMOS, the next boot's GTT limit, the swap layout
        and the guard."""
        pages = None if self.next_boot.error else self.next_boot.pages
        return learn.settings(self.written_split(), pages, self.swap_setup, guard.read_guard(self.etc_root))

    def start_steps(self) -> list[str]:
        """What the start point would write, in words: the Games profile's split and limit, Bazzite's swap and
        guard where they differ, and recording on. Empty when the board has it all."""
        steps = self.profile_steps("games")
        if self.swap_setup != swap.Setup():
            steps.append("Bazzite's own swap layout for the next boot")
        if guard.read_guard(self.etc_root) != guard.BAZZITE:
            steps.append("Bazzite's own memory guard")
        if not self.recording():
            steps.append("recording on")
        return steps

    def running_compressor(self) -> str:
        """The compressor the board's zram uses now (the selected one in comp_algorithm), else zstd."""
        for path in sorted((self.sys_root / "block").glob("zram*/comp_algorithm")):
            name = system._selected(system._read(path))
            if name:
                return name
        return "zstd"

    def proposal(self) -> learn.Change | None:
        st = self.state
        base = learn.baseline(st)
        return learn.propose(learn.baseline_sessions(st, watch.read_sessions(self.sessions_file)),
                             st.rounds[base].settings, self.memory.ram_mib or 0, learn.tried(st),
                             self.running_compressor(), self.memory.swappiness)

    def save_state(self) -> None:
        learn.write_state(self.state, self.learn_file)

    def begin_round(self, change: learn.Change | None, waits: bool) -> None:
        """A new round from now, with the settings just written; a restart waits when *waits*."""
        self.note = ""
        boot = self.memory.boot_id if waits else ""
        rounds = self.state.rounds if self.state else []
        rounds.append(learn.Round(self.clock(), self.board_settings(), boot, asdict(change) if change else None))
        self.state = learn.State(rounds, boot or (self.state.restart_boot if self.state else ""))
        self.save_state()
        if waits:
            resume.arm()

    def write_start(self) -> None:
        """Step 1: the start point, after one question; one password prompt for each part that needs root."""
        steps = self.start_steps()
        if steps:
            listed = steps[0] if len(steps) == 1 else f"{', '.join(steps[:-1])} and {steps[-1]}"
            answer = QMessageBox.question(
                self, window_title("Start point"),
                f"Write the start point?\n\nIt writes {listed}.\nThe split, the GTT limit and the swap take effect "
                "after a restart.\nThe guard and recording take effect at once.\n\nYou will be asked for your "
                "password once for each part.")
            if answer != QMessageBox.StandardButton.Yes:
                return
        _name, mb, pages, _setup, _guard = self.profile_values("games")
        waits = False
        if not self.block_problem and mb != self.written_split():
            if not self.write_split(mb, "Start point", ask=False):
                return
            waits = True
        if not self.next_boot.error and pages != self.next_boot.pages:
            if not self.apply_ttm(pages, ask=False):
                return
            waits = True
        if self.swap_setup != swap.Setup():
            if not self.write_swap(swap.Setup(), "Start point"):
                return
            waits = True
        if guard.read_guard(self.etc_root) != guard.BAZZITE and not self.apply_guard(guard.BAZZITE, ask=False):
            return
        if not self.recording() and not self.set_recording(True):
            return
        waits = waits or self.waiting_for_restart()
        self.begin_round(None, waits)
        self.refresh()

    def waiting_for_restart(self) -> bool:
        """A split, a GTT limit or a swap layout written earlier that the running boot does not have yet."""
        return bool(self.settings.get("pending_mb") or self.settings.get("pending_swap")
                    or (not self.next_boot.error and self.next_boot.pages != self.memory.ttm_cmdline_pages))

    def write_change(self, change: learn.Change, value: object) -> bool:
        """Writes one setting of a change (its value, or its before for an undo). True when it is written."""
        if change.kind == learn.ZRAM:
            return self.write_swap(swap.Setup(**value), "Try one change")
        if change.kind == learn.GTT:
            return self.apply_ttm(value, ask=False)
        return self.apply_guard(value, ask=False)

    def try_change(self) -> None:
        """Step 4: the proposed change, after one question; then the board restarts after the countdown."""
        change = self.proposal()
        if change is None:
            return
        at_once = change.kind == learn.GUARD
        effect = ("It takes effect at once." if at_once else
                  f"The board restarts {RESTART_SECS} s after the write.\nSave your work in other apps first.")
        answer = QMessageBox.question(
            self, window_title("Try one change"),
            f"Try {change.label}?\n\n{change.reason}\n{effect}\n\nYou will be asked for your password.")
        if answer != QMessageBox.StandardButton.Yes or not self.write_change(change, change.value):
            return
        self.begin_round(change, not at_once)
        self.refresh()
        if not at_once:
            self.start_countdown()

    def keep(self) -> None:
        index = learn.trial(self.state)
        if index is None:
            return
        self.state.rounds[index].verdict = learn.KEPT
        self.save_state()
        self.render_steps()

    def undo_change(self) -> None:
        """Step 5: the setting before the change written back; a new round with it, then the restart."""
        index = learn.trial(self.state)
        if index is None:
            return
        change = learn.Change(**self.state.rounds[index].change)
        at_once = change.kind == learn.GUARD
        effect = ("It takes effect at once." if at_once else
                  f"The board restarts {RESTART_SECS} s after the write.\nSave your work in other apps first.")
        answer = QMessageBox.question(
            self, window_title("Undo"),
            f"Undo {change.label}?\n\nThe setting from the round before comes back.\n{effect}\n\n"
            "You will be asked for your password.")
        if answer != QMessageBox.StandardButton.Yes or not self.write_change(change, change.before):
            return
        self.state.rounds[index].verdict = learn.UNDONE
        self.begin_round(None, not at_once)
        self.refresh()
        if not at_once:
            self.start_countdown()

    def start_over(self) -> None:
        answer = QMessageBox.question(
            self, window_title("Start over"),
            "Start the learning over?\n\nThe rounds and their verdicts are deleted.\nThe recorded sessions stay.\n"
            "The board's settings stay as they are until you write the start point.")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.stop_countdown()
        learn.clear_state(self.learn_file)
        self.state = None
        resume.disarm()
        self.note = ""
        self.render_steps()

    def start_countdown(self) -> None:
        self.note = ""
        self.countdown = RESTART_SECS
        self._tick.start()
        self.render_steps()

    def stop_countdown(self) -> None:
        self._tick.stop()
        self.countdown = 0

    def on_tick(self) -> None:
        self.countdown -= 1
        if self.countdown <= 0:
            self.restart_now()
            return
        self.render_steps()

    def restart_now(self) -> None:
        self.stop_countdown()
        if not self.restarter():
            self.note = "The window could not restart the board. Restart it by hand."
        self.render_steps()

    def cancel_restart(self) -> None:
        self.stop_countdown()
        self.note = "The restart is off. Restart the board when you like. The window opens again after the login."
        self.render_steps()

    def settings_text(self, settings: dict, key: str) -> str:
        value = settings.get(key)
        if key == "split":
            return split_label(value).split("  ")[0] if value else "—"
        if key == "pages":
            return system.mib_text(kargs.mib(value)) if value else "Kernel default"
        if key == "swap":
            setup = swap.Setup(**value)
            if setup.layout == swap.ZRAM:
                label = next((lbl for lbl, size, _f in swap.ZRAM_SIZES if size == setup.zram_size), setup.zram_size)
                return f"zram {label[0].lower() + label[1:]}"
            return "zswap with a swap file" if setup.layout == swap.ZSWAP_FILE else "Bazzite's own"
        return "The suite's" if value == guard.SUITE else "Bazzite's"

    def render_steps(self) -> None:
        """The steps from the learning's state, the sessions and the board: each row's state and line, the current
        step's pill, what it shows under the rows, and the bottom row."""
        if not hasattr(self, "advanced"):        # not built yet: a write during the build refreshes
            return
        st, boot = self.state, self.memory.boot_id
        if st is not None and not st.rounds:
            st = self.state = None
        sessions = watch.read_sessions(self.sessions_file)
        if st is not None and not learn.restart_waits(st, boot) and st.restart_boot:
            st.restart_boot = ""                # the restart is done
            self.save_state()
        if st is None or not learn.restart_waits(st, boot):
            resume.disarm()
        lines = ["Write the start point.", "The changes take effect after a restart.",
                 f"Play as usual. The app records {learn.SESSIONS_A_ROUND} game sessions.",
                 "The app proposes one change, from what it measured.",
                 "Play the same games again. Keep the change or undo it."]
        states = ["later"] * len(STEPS)
        pill: tuple[str, str, Callable[[], None]] | None = None
        alt: tuple[str, str, Callable[[], None]] | None = None
        nxt, hint, finished = "", "", ""
        self.clear_content()
        current = 0
        if st is None:
            steps = self.start_steps()
            states[0] = "now"
            if steps:
                lines[0] = "Write the Games profile as the start point. You will be asked for your password."
                pill = ("Write", "Games profile", self.write_start)
            else:
                lines[0] = "Your board has the start point already. Click Start to begin round 1."
                pill = ("Start", "Round 1", self.write_start)
            self.show_start(steps)
            nxt = "Next: restart, in step 2." if steps else "Next: play, in step 3."
        else:
            waits = learn.restart_waits(st, boot)
            trial = learn.trial(st)
            first = learn.round_sessions(st, sessions, 0)
            base = learn.baseline_sessions(st, sessions)
            states[0], lines[0] = "done", "Start point written."
            if len(st.rounds) == 1 and waits:
                current, states[1] = 1, "now"
                lines[1] = "Restart the board. The window opens again after you log in."
                pill = ("Restart", "The board", self.start_countdown)
                nxt = "Next: play, in step 3."
            else:
                states[1] = "done"
                lines[1] = ("The board started with the start point." if st.rounds[0].boot else
                            "Nothing waited for a restart.")
                if trial is None and learn.baseline(st) == 0 and len(base) < learn.SESSIONS_A_ROUND:
                    current, states[2] = 2, "running"
                    lines[2] = (f"Play as usual. {len(base)} of {learn.SESSIONS_A_ROUND} sessions recorded. The window "
                                "can stay closed.")
                    if not self.recording():
                        states[2] = "stopped"
                        lines[2] = "Recording is off. Turn it on to record the sessions."
                        pill = ("Turn on", "Recording", lambda: self.set_recording(True))
                    self.show_sessions("Round 1, recorded so far", base)
                    nxt = "Next: one change, in step 4."
                else:
                    short = sum(s.ended in learn.ENDED_SHORT for s in first)
                    states[2] = "done"
                    lines[2] = f"{len(first)} sessions recorded in round 1. {short} ended for lack of memory."
                    current = self.render_rounds(st, sessions, base, trial, waits, states, lines)
                    pill, alt, nxt, finished = self.round_actions
        if self.countdown:
            pill = ("Restart now", "Don't wait", self.restart_now)
            alt = ("Cancel", "Restart later", self.cancel_restart)
            nxt = f"Restarting in {self.countdown} s."
            hint = "Save your work in other apps first."
        for index, row in enumerate(self.step_rows):
            row.set_state(states[index], lines[index])
            row.set_pill(None)
        self.step_action = pill[2] if pill else None
        if pill:
            self.step_pill.setText(pill[0])
            self.step_pill.caption.setText(pill[1])
            self.step_rows[current].set_pill(self.step_pill)
        self.alt_action = alt[2] if alt else None
        self.alt_pill.setVisible(alt is not None)
        if alt:
            self.alt_pill.setText(alt[0])
            self.alt_pill.caption.setText(alt[1])
        self.finished_bar.setText(finished)
        self.finished_bar.setVisible(bool(finished))
        self.start_over_pill.setVisible(st is not None)
        self.next_label.setText(nxt)
        self.hint.setText(self.note or hint or "Advanced has each setting on its own.")
        rounds = 1 + sum(1 for r in st.rounds if r.change) if st else 0
        self.round_box.set_value(str(rounds) if rounds else "—")
        self.round_box.caption.setText("Rounds" if finished else "Round")
        self.record_box.set_value("On" if self.recording() else "Off")
        self.record_box.set_colour(GREEN if self.recording() else GREY)
        self.record_pill.setText("Turn off" if self.recording() else "Turn on")

    def render_rounds(self, st: learn.State, sessions: list[watch.Session], base: list[watch.Session],
                      trial: int | None, waits: bool, states: list[str], lines: list[str]) -> int:
        """Steps 4 and 5 from round 1 on. Sets self.round_actions (pill, alt, next, finished); returns the current
        step."""
        tried = [r for r in st.rounds if r.change]
        kept = sum(r.verdict == learn.KEPT for r in tried)
        undone = sum(r.verdict == learn.UNDONE for r in tried)
        self.round_actions = (None, None, "", "")
        if trial is not None:
            change = learn.Change(**st.rounds[trial].change)
            number = len(tried) + 1
            if waits:
                states[3] = "now"
                lines[3] = f"{change.label[0].upper() + change.label[1:]} is written. Restart to begin round {number}."
                self.round_actions = (("Restart", "The board", self.start_countdown), None,
                                      "Next: play the same games, in step 5.", "")
                self.show_measured(base, st.rounds[learn.baseline(st)].settings, change)
                return 3
            states[3] = "done"
            lines[3] = f"Round {number}: {change.label}."
            after = learn.round_sessions(st, sessions, trial)
            verdict = learn.compare(base, after)
            missing = f" Not played yet in this round: {', '.join(verdict.missing)}." if verdict.missing else ""
            self.show_compare(number, change, verdict)
            if not verdict.ready:
                states[4] = "running"
                lines[4] = (f"Play the same games again. {verdict.sessions} of {learn.SESSIONS_A_ROUND} sessions "
                            f"recorded.{missing}")
                self.round_actions = (None, None, "Next: keep the change or undo it.", "")
                return 4
            states[4] = "now"
            keep = ("Keep", change.label, self.keep)
            undo = ("Undo", "Back to the round before", self.undo_change)
            if verdict.kind == learn.BETTER:
                lines[4] = f"Better. Keep the change, or undo it.{missing}"
                self.round_actions = (keep, undo, "Next: the next change, in step 4.", "")
            else:
                lines[4] = (f"{'Worse' if verdict.kind == learn.WORSE else 'No better'}. Undo the change, or keep "
                            f"it.{missing}")
                self.round_actions = (undo, keep, "Next: the next change, in step 4.", "")
            return 4
        if tried:
            states[4], lines[4] = "done", tried_text(len(tried), kept, undone)
        if waits:
            states[4] = "now"
            lines[4] = "Undone. Restart the board to bring back the settings from before."
            self.round_actions = (("Restart", "The board", self.start_countdown), None,
                                  "Next: the next change, in step 4.", "")
            return 4
        change = self.proposal()
        settings = st.rounds[learn.baseline(st)].settings
        if change is not None:
            states[3] = "now"
            at_once = change.kind == learn.GUARD
            lines[3] = f"{change.reason} Try {change.label}."
            self.round_actions = (("Write", "Takes effect at once" if at_once else "and restart", self.try_change),
                                  None, "Next: play the same games, in step 5.", "")
            self.show_measured(base, settings, change)
            return 3
        states[3] = "done"
        lines[3] = tried_text(len(tried), kept, undone) if tried else "Nothing measured asked for a change."
        states[4], lines[4] = "done", "Nothing more to change. The measurements ask for nothing."
        self.show_learned(st)
        self.round_actions = (None, None, "Nothing to do.", "Done. Your board runs the Learned profile.")
        return 4

    # --- What the current step shows ---------------------------------------------------------------------------

    def clear_content(self) -> None:
        while self.content.count():
            widget = self.content.takeAt(0).widget()
            if widget is not None:
                widget.hide()                   # at once: deleteLater() leaves it drawn until the event loop
                widget.setParent(None)
                widget.deleteLater()

    def add_text(self, text: str, muted_text: bool = False, size: int = 14) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"font-size:{size}px;" + (f"color:{muted()};" if muted_text else ""))
        self.content.addWidget(label)
        label.show()
        return label

    def add_table(self, headers: list[str], rows: list[tuple], colours: dict | None = None) -> QTableWidget:
        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        for r, cells in enumerate(rows):
            for c, value in enumerate(cells):
                item = QTableWidgetItem(str(value))
                if c:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                colour = (colours or {}).get(value) if c == len(headers) - 1 else None
                if colour:
                    item.setForeground(QColor(colour))
                table.setItem(r, c, item)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()
        for c in range(1, len(headers)):
            header.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setFixedHeight(header.sizeHint().height() + max(len(rows), 1) * table.verticalHeader().defaultSectionSize()
                             + 4)
        self.content.addWidget(table)
        table.show()
        return table

    def show_start(self, steps: list[str]) -> None:
        self.add_text("<b>The Games profile, the start point</b>")
        for line in (f"{split_label(RECOMMENDED_MB).split('  ')[0]} split. It prevents the framebuffer pin failures "
                     "(Board Test, test 37).", f"GTT limit {system.mib_text(kargs.mib(SUITE_PAGES))}.",
                     "Swap and memory guard as Bazzite sets them.",
                     "Recording on. It records memory, swap, CPU and how each game ended."):
            self.add_text(f"• {line}", size=13)
        if steps:
            self.add_text(f"The app writes {', '.join(steps)}.", True, 13)

    def show_sessions(self, title: str, sessions: list[watch.Session]) -> None:
        if not sessions:
            self.add_text("No session yet. A game or program of 1 GiB or more becomes one when it ends.", True, 13)
            return
        self.add_text(f"<b>{escape(title)}</b>")
        self.add_table(["Game", "How it ended", "RAM", "VRAM", "GPU borrows", "Swap", "Waited", "CPU"],
                       [(s.program, s.ended, system.mib_text(s.ram_mib), system.mib_text(s.vram_mib),
                         system.mib_text(s.gtt_mib), system.mib_text(s.swap_mib), f"{s.pressure:.0f}%",
                         f"{s.cpu:.0f}%") for s in sessions[::-1]])
        self.add_text("Waited: the share of time the board waited for memory, at its peak. CPU is for context only.",
                      True, 12)

    def show_measured(self, sessions: list[watch.Session], settings: dict, change: learn.Change) -> None:
        self.add_text("<b>Why this change</b>")
        self.add_table(["Measured", "Value"], learn.measured(sessions, settings, self.memory.ram_mib or 0))
        self.add_text("One change per round, so the comparison shows what it did. The next round plays the same "
                      "games.", True, 13)

    def show_compare(self, number: int, change: learn.Change, verdict: learn.Verdict) -> None:
        self.add_text(f"<b>Before the change against round {number}, the same games</b>")
        self.add_table(["Measured", "Before", f"Round {number}: {change.label}", ""], verdict.rows,
                       {learn.BETTER: GREEN, learn.WORSE: RED, learn.SAME: ORANGE})

    def show_learned(self, st: learn.State) -> None:
        start, now = st.rounds[0].settings, st.rounds[learn.baseline(st)].settings
        why = {learn.ZRAM: "swap", learn.GTT: "pages", learn.GUARD: "guard"}
        reasons = {why[r.change["kind"]]: r.change["reason"] for r in st.rounds
                   if r.change and r.verdict == learn.KEPT}
        names = (("VRAM split", "split"), ("GTT limit", "pages"), ("Swap", "swap"), ("Memory guard", "guard"))
        self.add_text("<b>The Learned profile</b>")
        self.add_table(["Setting", "Start point", "Learned", "Why"],
                       [(name, self.settings_text(start, key), self.settings_text(now, key),
                         reasons.get(key, "Unchanged")) for name, key in names])
        self.add_text("Recording stays on. When a game runs out of memory again, the app proposes a new change.",
                      True, 13)

    # --- Actions ----------------------------------------------------------------------------------------------

    def apply_split(self) -> None:
        self.write_split(self.combo.currentData(), "Apply split")

    def undo(self) -> None:
        self.write_split(self.settings.get("previous_mb"), "Undo")

    def write_split(self, mb: int, title: str, ask: bool = True) -> bool:
        """Writes the split to CMOS, after the question unless *ask* is off (a profile asked already). True when
        it is written."""
        m = self.memory
        left = ""
        if m.vram_mib and m.ram_mib:
            left = f"\nThe system keeps about {system.mib_text(m.vram_mib + m.ram_mib - mb)} of RAM."
        if ask:
            answer = QMessageBox.question(
                self, window_title(title),
                f"Write a VRAM split of {split_label(mb)} to CMOS?\n\n"
                f"This changes how the board starts.\nThe firmware reads the split at the next boot.{left}\n"
                "Only the split changes. The memory timings stay as they are.\nYou can change it back here, or "
                "clear CMOS with the jumper or the battery for the firmware's default.\n\n"
                "You will be asked for your password.")
            if answer != QMessageBox.StandardButton.Yes:
                return False
        result = self.runner(["--set-uma", str(mb)])
        if not result.ok:
            QMessageBox.warning(self, window_title(title), result.error or "The write failed.")
            return False
        self.save_backup(result.data)
        before = result.data["before"]["uma_mb"]
        if before != mb:
            self.settings.set("previous_mb", before)
        self.settings.set("pending_mb", mb if mb != m.vram_mib else 0)
        self.settings.set("pending_boot_id", m.boot_id if mb != m.vram_mib else "")
        self.settings.set("outcome", "" if mb != m.vram_mib else f"CMOS holds the {split_label(mb)} split again.")
        self.refresh()
        return True

    def gtt_effect(self, pages: int | None) -> str:
        """What the GTT would be after a reboot with this limit and the split of this boot, against what it is now:
        the kernel caps it at the RAM, so a limit above the RAM changes nothing visible."""
        m = self.memory
        then = gtt_ceiling(m, None, kargs.mib(pages))
        if then is None or m.gtt_mib is None:
            return ""
        ram = m.ram_mib or 0
        if then == m.gtt_mib:
            if then >= ram * 95 // 100:
                return (f"\nThe GTT stays at {system.mib_text(m.gtt_mib)}, all the RAM with this split. A limit "
                        "above the RAM changes nothing until a smaller split.")
            return f"\nThe GTT stays at {system.mib_text(m.gtt_mib)}."
        return f"\nThe GTT then is about {system.mib_text(then)} instead of {system.mib_text(m.gtt_mib)} now."

    def apply_ttm(self, pages=PICK, ask: bool = True) -> bool:
        """Puts the limit (the combo's, or *pages*) in the next boot's kernel arguments, after the question and
        with the Done message unless *ask* is off (a profile does both). True when it is written."""
        if pages is PICK:
            pages = self.ttm_combo.currentData()
        if ask:
            if pages is None:
                what = "Remove ttm.pages_limit from the kernel arguments of the next boot?\n\nThe kernel then takes "
                what += "its default, half the RAM, as the GTT limit."
            else:
                what = (f"Set ttm.pages_limit to {pages} ({system.mib_text(kargs.mib(pages))}) in the kernel arguments "
                        "of the next boot?\n\nThe GPU may then borrow up to that much of the RAM, but never more "
                        "than the RAM.")
            answer = QMessageBox.question(
                self, window_title("GTT limit"),
                f"{what}{self.gtt_effect(pages)}\n\nrpm-ostree writes a new deployment with the change.\nThis takes "
                "a minute or two, because rpm-ostree puts the layered packages on it again.\nThe change takes effect "
                "after you restart the board. The app leaves the restart to you.\nThe split in CMOS stays as it "
                "is.\n\nYou will be asked for your password.")
            if answer != QMessageBox.StandardButton.Yes:
                return False
        # rpm-ostree works for a minute or two after the password dialog closes: say so where it is seen, with the
        # seconds counting, so the wait does not look like a hang (owner, 01-11-2026).
        self.badge.set_status("Writing…", "info", "rpm-ostree is writing the next boot's kernel arguments")
        self.ttm_note.setVisible(True)
        for widget in (self.ttm_combo, self.ttm_button, self.apply_button, self.undo_button, self.read_button):
            widget.setEnabled(False)
        self.writing_since = time.monotonic()
        self.writing_timer = QTimer(self)
        self.writing_timer.timeout.connect(self.tick_writing)
        self.writing_timer.start(1000)
        self.tick_writing()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            error = kargs.apply(self.commands, pages, self.next_boot.pages)
        finally:
            self.writing_timer.stop()
            QApplication.restoreOverrideCursor()
            self.ttm_combo.setEnabled(True)
        if error:
            QMessageBox.warning(self, window_title("GTT limit"), error)
            pick = self.ttm_combo.currentIndex()
            self.refresh()
            self.ttm_combo.setCurrentIndex(pick)      # the pick stays, so it can be tried again
            return False
        self.next_boot = kargs.read_next_boot(self.commands)
        changed = pages != self.memory.ttm_cmdline_pages
        self.settings.set("pending_ttm", ttm_setting(pages) if changed else "")
        self.settings.set("pending_ttm_boot_id", self.memory.boot_id if changed else "")
        self.settings.set("ttm_outcome", "" if changed else f"The next boot has the {ttm_label(pages)} again.")
        if changed and ask:
            QMessageBox.information(
                self, window_title("GTT limit"),
                f"Done. The {ttm_label(pages)} is in the next boot's kernel arguments.\n\nRestart the board to use "
                "it. The app does not restart the board by itself. Use the menu, or run systemctl reboot in a "
                "terminal.")
        self.refresh()
        return True

    def tick_writing(self) -> None:
        """The note while rpm-ostree works: the seconds so far, so the window is seen to be alive."""
        seconds = int(time.monotonic() - self.writing_since)
        self.ttm_note.setText(f"<b>rpm-ostree is writing the next boot's kernel arguments, {seconds} s so far. This "
                              "takes a minute or two. The window answers again when rpm-ostree is done.</b>")

    def apply_profile(self, key: str) -> None:
        """Writes a profile's split and limit where they differ from the board, after one question; one password
        prompt for each (CMOS through pkexec, the kernel arguments through rpm-ostree)."""
        name, mb, pages, setup, wanted = self.profile_values(key)
        steps = self.profile_steps(key)
        if not steps:
            return
        guard_step = wanted is not None and wanted != guard.read_guard(self.etc_root)
        later = len(steps) - guard_step                 # the steps that wait for a restart
        listed = steps[0] if len(steps) == 1 else f"{', '.join(steps[:-1])} and {steps[-1]}"
        effect = {0: "", 1: "It takes effect after you restart the board.\nThe app leaves the restart to you.\n",
                  2: "Both take effect after you restart the board.\nThe app leaves the restart to you.\n"}.get(
            later, "They take effect after you restart the board.\nThe app leaves the restart to you.\n")
        if guard_step:
            effect += "The guard takes effect at once.\n"
        many = len(steps) > 1
        answer = QMessageBox.question(
            self, window_title(name),
            f"Write {listed}?\n\n{effect}\nYou will be asked for your password" + (" once for each." if many else "."))
        if answer != QMessageBox.StandardButton.Yes:
            return
        if not self.block_problem and mb != self.written_split() and not self.write_split(mb, name, ask=False):
            return
        if not self.next_boot.error and pages != self.next_boot.pages and not self.apply_ttm(pages, ask=False):
            return
        if setup is not None and setup != self.swap_setup and not self.write_swap(setup, name):
            return
        if guard_step and not self.apply_guard(wanted, ask=False):
            return
        done = ("Restart the board to use it. The app does not restart the board by itself. Use the menu, or run "
                "systemctl reboot in a terminal." if later else "It is active now.")
        QMessageBox.information(self, window_title(name), f"Done. The app wrote {listed}.\n\n{done}")

    def save_backup(self, data: dict) -> Path:
        folder = backups_dir()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"cmos-{time.strftime('%Y%m%d-%H%M%S')}.json"
        path.write_text(json.dumps({"before": data["before"], "after": data["after"]}, indent=2) + "\n")
        return path

    def read_cmos(self) -> None:
        result = self.runner(["--read"])
        if not result.ok:
            QMessageBox.warning(self, window_title("Read CMOS"), result.error or "The read failed.")
            return
        text = privileged.report(result.data, self.sys_root)
        folder = backups_dir()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"cmos-dump-{time.strftime('%Y%m%d-%H%M%S')}.txt"
        path.write_text(text)
        dialog = TextDialog("CMOS memory block", f"{text}\nSaved: {path}\n", self)
        dialog.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.timer.stop()
        self.settings.set_window_state("geometry", self.saveGeometry())
        self.settings.sync()
        super().closeEvent(event)
