# SPDX-License-Identifier: GPL-3.0-or-later
"""The Programs window (owner, 26-11-2026): the memory over time, and every program the watcher has seen, the
largest first, with the mark that closes it when a game starts, and for a game the profile it wants (owner,
28-11-2026: a game's own choice comes before its manager's, profiles.py).

The graph draws the watcher's history (one point a minute, the minute's peaks) for the range picked: RAM in use, the
RAM the GPU borrows and the swap in use, against the RAM, with a red line where a lack of memory ended a program
(the sessions). The table reads the watcher's statistics; a mark is written to the watcher's list at once, and the
watcher reads it when a game starts. Steam and the games cannot be marked."""

from __future__ import annotations

import time
from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPalette, QPen
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from bc250_core import window_title
from bc250_core.theme import BLUE, ORANGE, RED
from bc250_core.widgets import InfoButton, hint_label

from . import profiles, system, watch

RAM_LINE = "#d8d8d8"
RANGES = (("The last hour", 3600), ("The last 4 hours", 4 * 3600), ("The last 24 hours", 24 * 3600))
SERIES = (("RAM in use", RAM_LINE, "ram_mib"), ("GPU borrows", BLUE, "gtt_mib"), ("Swap in use", ORANGE, "swap_mib"))
CLOSE, KEEP = "Close", "Keep"


class Graph(QWidget):
    """The history as lines, against the RAM; the sessions ended by a lack of memory as red lines."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(230)
        self.points: list[watch.Point] = []
        self.kills: list[watch.Session] = []
        self.ram_mib = 0
        self.start = self.end = 0.0

    def set_data(self, points: list[watch.Point], kills: list[watch.Session], ram_mib: int, start: float,
                 end: float) -> None:
        self.points, self.kills, self.ram_mib, self.start, self.end = points, kills, ram_mib, start, end
        self.update()

    def top_gib(self) -> int:
        """The scale: the RAM or the highest figure, whichever is more, up to the next even GiB."""
        most = max([self.ram_mib] + [max(p.ram_mib, p.gtt_mib, p.swap_mib) for p in self.points]) / 1024
        return max(2, int(most) + 2 - int(most) % 2)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        text = self.palette().color(QPalette.ColorRole.PlaceholderText)
        area = QRectF(56, 10, self.width() - 68, self.height() - 40)
        top, span = self.top_gib(), max(self.end - self.start, 1)

        def x(t: float) -> float:
            return area.left() + (t - self.start) / span * area.width()

        def y(mib: float) -> float:
            return area.bottom() - mib / 1024 / top * area.height()
        step = 2 if top <= 16 else 4
        for gib in range(0, top + 1, step):
            p.setPen(QColor("#555555"))
            p.drawLine(QPointF(area.left(), y(gib * 1024)), QPointF(area.right(), y(gib * 1024)))
            p.setPen(text)
            p.drawText(QRectF(0, y(gib * 1024) - 8, 50, 16), Qt.AlignmentFlag.AlignRight, f"{gib} GiB")
        hours = max(int(span // 3600), 1)
        every = 3600 * (1 if hours <= 4 else 4)
        first = (int(self.start) // every + 1) * every
        for t in range(first, int(self.end) + 1, every):
            p.drawText(QRectF(x(t) - 25, area.bottom() + 6, 50, 16), Qt.AlignmentFlag.AlignCenter,
                       time.strftime("%H:%M", time.localtime(t)))
        if self.ram_mib:
            p.setPen(QPen(QColor(ORANGE), 1, Qt.PenStyle.DashLine))
            p.drawLine(QPointF(area.left(), y(self.ram_mib)), QPointF(area.right(), y(self.ram_mib)))
            p.drawText(QPointF(area.left() + 4, y(self.ram_mib) - 4), f"RAM {system.mib_text(self.ram_mib)}")
        for _label, color, key in SERIES:
            path = QPainterPath()
            for n, point in enumerate(self.points):
                at = QPointF(x(point.t), y(getattr(point, key)))
                path.moveTo(at) if n == 0 else path.lineTo(at)
            p.setPen(QPen(QColor(color), 2))
            p.drawPath(path)
        p.setPen(QPen(QColor(RED), 2))
        for n, session in enumerate(self.kills):
            at = x(session.end)
            p.drawLine(QPointF(at, area.top()), QPointF(at, area.bottom()))
            label = f"{session.ended}: {session.program}"
            width = p.fontMetrics().horizontalAdvance(label)
            left = at + 4 if at + 4 + width <= area.right() else at - 4 - width     # inside the graph
            p.drawText(QPointF(left, area.top() + 30 + 16 * (n % 3)), label)
        if not self.points:
            p.setPen(text)
            p.drawText(area, Qt.AlignmentFlag.AlignCenter, "No history in this range yet.")
        p.end()


class ProgramsDialog(QDialog):
    def __init__(self, parent: QWidget | None, ram_mib: int, history: Path | None = None,
                 programs: Path | None = None, sessions: Path | None = None, closes: Path | None = None,
                 clock=time.time, manual_url: str = "", choices: Path | None = None):
        super().__init__(parent)
        self.setWindowTitle(window_title("Programs"))
        self.resize(900, 720)
        self.ram_mib, self.clock = ram_mib, clock
        self.history_file, self.programs_file = history, programs
        self.sessions_file, self.closes_file = sessions, closes
        self.choices_file = choices or watch.choices_path()
        self.profile_combos: dict[str, QComboBox] = {}

        self.range_combo = QComboBox()
        for label, seconds in RANGES:
            self.range_combo.addItem(label, seconds)
        self.range_combo.setCurrentIndex(1)
        self.range_combo.currentIndexChanged.connect(self.refresh_graph)
        top = QHBoxLayout()
        top.addWidget(QLabel("<b>Memory over time</b>"))
        top.addStretch(1)
        top.addWidget(self.range_combo)
        self.graph = Graph()
        legend = QHBoxLayout()
        for label, color, _key in SERIES:
            legend.addWidget(QLabel(f"<span style='color:{color}'>■</span> {label}"))
        legend.addWidget(QLabel(f"<span style='color:{RED}'>■</span> A program ended by a lack of memory"))
        legend.addStretch(1)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Program", "Runs", "Peak", "Average", "Killed", "Close for games",
                                              "Profile"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(5, 140)
        self.table.setColumnWidth(6, 170)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.itemChanged.connect(self.on_mark)
        bottom = QHBoxLayout()
        bottom.addWidget(hint_label("A checked program gets the stop signal when a game starts. Most programs save "
                                    "and quit on it."), 1)
        bottom.addWidget(InfoButton(
            "<b>Peak</b> and <b>Average</b> are the program's own memory, swap included. <b>Killed</b> counts the "
            "times a lack of memory ended it. When a Steam game or a game of the suite's emulators starts, each "
            "checked program that runs gets systemd's stop signal, SIGTERM. Most programs save and quit on it. Some "
            "do not ask about unsaved files the way their close button does. Steam and the games cannot be checked. "
            "Each close goes to the log. <b>Profile</b> picks the memory profile a game wants. It comes before the "
            "profile picked for its manager in the window. "
            f"<a href='{manual_url}#programs'>Wiki</a>", "About closing for games"))

        lay = QVBoxLayout(self)
        lay.addLayout(top)
        lay.addWidget(self.graph)
        lay.addLayout(legend)
        lay.addWidget(QLabel("<b>Programs, the largest first</b>"))
        lay.addWidget(self.table, 1)
        lay.addLayout(bottom)
        self.refresh_graph()
        self.refresh_table()

    def refresh_graph(self) -> None:
        end = self.clock()
        start = end - self.range_combo.currentData()
        points = watch.read_history(self.history_file, start)
        kills = [s for s in watch.read_sessions(self.sessions_file) if s.ended in watch.SHORT and s.end >= start]
        self.graph.set_data(points, kills, self.ram_mib, start, end)

    def refresh_table(self) -> None:
        stats = sorted(watch.read_stats(self.programs_file).values(), key=lambda s: -s.peak_mib)
        marked = watch.read_closes(self.closes_file)
        chosen = profiles.read_choices(self.choices_file).games
        self.profile_combos = {}
        table = self.table
        table.blockSignals(True)
        table.setRowCount(len(stats))
        for row, s in enumerate(stats):
            cells = (s.program, str(s.runs), system.mib_text(s.peak_mib), system.mib_text(s.average_mib),
                     str(s.killed))
            for column, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row, column, item)
            if s.game:
                mark = QTableWidgetItem("Never")
                mark.setFlags(mark.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
                mark.setToolTip("Closing Steam or a game would end the game")
            else:
                on = s.program in marked
                mark = QTableWidgetItem(CLOSE if on else KEEP)
                mark.setFlags(mark.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                mark.setCheckState(Qt.CheckState.Checked if on else Qt.CheckState.Unchecked)
            mark.setData(Qt.ItemDataRole.UserRole, s.program)
            table.setItem(row, 5, mark)
            if s.game and s.program.lower() != "steam":
                combo = QComboBox()
                combo.addItem("Its manager's", "")
                for key, (name, _mb, _pages) in profiles.PROFILES.items():
                    combo.addItem(name, key)
                combo.setCurrentIndex(max(combo.findData(chosen.get(s.program, "")), 0))
                combo.currentIndexChanged.connect(lambda _i, n=s.program, c=combo: profiles.set_choice(
                    self.choices_file, "games", n, c.currentData()))
                table.setCellWidget(row, 6, combo)
                self.profile_combos[s.program] = combo
            else:
                table.removeCellWidget(row, 6)
                table.setItem(row, 6, QTableWidgetItem("—"))
        table.blockSignals(False)

    def on_mark(self, item: QTableWidgetItem) -> None:
        """A mark checked or unchecked: written to the watcher's list at once."""
        if item.column() != 5 or not item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        marked = watch.read_closes(self.closes_file)
        on = item.checkState() == Qt.CheckState.Checked
        (marked.add if on else marked.discard)(name)
        watch.write_closes(marked, self.closes_file)
        self.table.blockSignals(True)
        item.setText(CLOSE if on else KEEP)
        self.table.blockSignals(False)
