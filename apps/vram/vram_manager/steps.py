# SPDX-License-Identifier: GPL-3.0-or-later
"""One learning step as a row, as Core Unlock's (owner, 26-11-2026): a mark, "Step N · name" with its state, one line
with what came out of it or what to do now, and on the current step's row its pill. A copy of Core Unlock's StepRow,
on core's theme."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from bc250_core.theme import ACCENT, GREEN, GREY, ORANGE, RED, header_font, muted, surface_style

STEPS = ("Start point", "Restart", "Play and record", "Try one change", "Play and compare")


class StepRow(QFrame):
    MARKS = {"done": "✔", "now": "▶", "running": "▶", "stopped": "✖"}
    WORDS = {"done": "Done", "now": "Do this now", "running": "Running", "stopped": "Stopped", "later": "Later"}

    def __init__(self, index: int):
        super().__init__()
        self.index = index
        self.state = "later"
        self.setObjectName("steprow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(14)
        self.mark = QLabel()
        self.mark.setFixedWidth(30)
        self.mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.mark)
        text = QVBoxLayout()
        text.setSpacing(2)
        top = QHBoxLayout()
        top.setSpacing(10)
        self.title = QLabel()
        self.caption = QLabel()
        top.addWidget(self.title)
        top.addWidget(self.caption)
        top.addStretch(1)
        text.addLayout(top)
        self.line = QLabel()
        self.line.setWordWrap(True)
        text.addWidget(self.line)
        layout.addLayout(text, 1)
        self.slot = QHBoxLayout()                   # the step's pill, on the current step's row only
        layout.addLayout(self.slot)
        self.set_state("later", "")

    def set_state(self, state: str, line: str) -> None:
        self.state = state
        colour = {"done": GREEN, "now": ACCENT, "running": ORANGE, "stopped": RED, "later": GREY}[state]
        later = state == "later"
        current = state in ("now", "running", "stopped")
        self.mark.setText(self.MARKS.get(state, str(self.index + 1)))
        self.mark.setStyleSheet(f"font-size:22px; font-weight:800; color:{muted() if later else colour};")
        self.title.setText(f"Step {self.index + 1} · {STEPS[self.index]}")
        self.title.setStyleSheet(header_font() + "font-size:17px; font-weight:800;"
                                 + (f"color:{muted()};" if later else ""))
        self.caption.setText(self.WORDS[state])
        self.caption.setStyleSheet(f"font-size:13px; font-weight:700; color:{muted() if later else colour};")
        self.line.setText(line)
        self.line.setStyleSheet("font-size:14px;" + ("font-weight:600;" if current else f"color:{muted()};"))
        edge = f"#steprow {{ border:2px solid {ACCENT}; border-left:4px solid {colour}; }}" if current else ""
        self.setStyleSheet(surface_style(colour, "#steprow") + edge + "QLabel { background:transparent; border:none; }")

    def set_pill(self, pill: QWidget | None) -> None:
        """The step's pill on its row, or none."""
        while self.slot.count():
            item = self.slot.takeAt(0)
            if item.widget() is not None:
                item.widget().setParent(None)
        if pill is not None:
            self.slot.addWidget(pill)
            pill.show()                         # a reparented widget stays hidden until shown
