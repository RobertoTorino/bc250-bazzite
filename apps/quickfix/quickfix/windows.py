# SPDX-License-Identifier: GPL-3.0-or-later
"""The quickfixes' windows. Each is the suite's window: the icon at 96 px, the quickfix's name with the version, its
state, the info symbol with what it contains and does, and the refresh symbol at the right end; its status boxes
and pills on the rows under the title, five on a row at most (core's card.py: the card).
The ones that change the board are switches (SwitchWindow): Turn on when it is off, Turn off when the quickfix turned
it on, one password each (pkexec, system.py); what is on already cannot be turned on again. The two kernel
arguments (KargWindow) apply from the next boot, which the window advises."""

from __future__ import annotations

import datetime
import shlex
from collections.abc import Callable
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QComboBox, QGridLayout, QLabel, QMessageBox, QPlainTextEdit

from bc250_core import window_title
from bc250_core.platform import launch_in_terminal, show_in_folder
from bc250_core.theme import GREEN, GREY, ORANGE
from bc250_core.card import CardWindow
from bc250_core.widgets import ActionPill, MetricBox, hint_label, same_width

from . import LOGO_PATH, __version__, runner, state, system
from .catalog import BY_KEY, Quickfix

RootRunner = Callable[[list[str]], runner.Result]
BOARD = ("<br><br><b>Changes the board.</b> It asks for your password once (pkexec). It never touches the BIOS or "
         "the firmware, and Turn off undoes it.")


class QuickfixWindow(CardWindow):
    """One quickfix's window, a card (core's card.py): the header, then the page the quickfix fills (self.page)."""

    def __init__(self, quickfix: Quickfix, info: str, run_root: RootRunner = runner.run_root,
                 root: Path = state.ROOT, home: Path | None = None) -> None:
        super().__init__(LOGO_PATH, quickfix.name, __version__, info + (BOARD if quickfix.changes_board else ""))
        self.quickfix, self.run_root, self.root, self.home = quickfix, run_root, root, home or Path.home()

    def as_root(self, args: list[str], title: str) -> bool:
        """Runs system.py as root; a canceled password or a failure shows a message, and the window reads again."""
        result = self.run_root(system.command(args))
        problem = system.answer(result.code, result.out)
        if problem:
            QMessageBox.warning(self, window_title(title), problem)
        self.refresh()
        return not problem


# ------------------------------------------------------------------------------------------------- Quickfix
TOOLS_INFO = ("<b>Quickfix</b> shows the optional tools BC-250 Board Test's tests use, whether each one is "
               "there, and which tests use it. Board Test runs without them: a test whose tool is missing says so."
               "<br><br>A group's pill (<b>Install</b>) runs Board Test's own installer, "
               "<code>install-requirements.sh</code>, for that group in a terminal: it asks for your password "
               "where it layers packages and skips what is there already. <b>Install all</b> installs every group "
               "but the development extras.<br><br>"
               "<b>Prime95</b> is mprime, which no test uses: BC-250 CPU Tools runs its torture test for a longer "
               "burn-in. The latest release is downloaded from mersenne.org and checked against the SHA-256 listed "
               "there. Nexus Deps shows a newer release when there is one, and its Update installs it.<br><br>"
               "Layered RPM packages are active after a reboot (<code>systemctl reboot</code>). glmark2, "
               "vulkan-tools and smartmontools come with Bazzite.")


class ToolsWindow(QuickfixWindow):
    def __init__(self, launch: Callable[[str], None] = launch_in_terminal, board_test: Path = state.BOARD_TEST,
                 **kwargs) -> None:
        super().__init__(BY_KEY["tools"], TOOLS_INFO, **kwargs)
        self.launch, self.board_test = launch, board_test
        self.resize(900, 560)
        self.found_box = MetricBox("Tools found")
        self.all_button = ActionPill("Install all", "Every missing tool")
        self.all_button.setToolTip("Every group but the development extras, in a terminal (--all)")
        self.all_button.clicked.connect(lambda: self.install("--all"))
        self.set_rows([self.found_box, self.all_button])
        self.grid = QGridLayout()
        self.grid.setColumnStretch(3, 1)
        self.grid.setHorizontalSpacing(10)
        self.page.addLayout(self.grid)
        self.page.addStretch(1)
        self.rows: dict[str, QLabel] = {}
        self.buttons: dict[str, ActionPill] = {}
        row = 0
        for group in state.GROUPS:
            # The group's heading is its Install pill (owner, 17-11-2026): the name, and what a click does under it.
            button = ActionPill(group.name, "Install")
            button.clicked.connect(lambda _=False, o=group.option: self.install(o))
            self.buttons[group.option] = button
            row = self._group(button, group.tools, row)
        self.built_in = ActionPill("With Bazzite", "Included")
        self.built_in.setToolTip("Already on Bazzite: nothing to install.")
        self.built_in.setEnabled(False)
        self._group(self.built_in, state.BUILT_IN, row)
        # The exception among the cards (owner, 21-11-2026): the pills as wide as the widest group's, and the
        # window at its own width, which the tools' text fills.
        same_width([self.found_box, self.all_button, *self.buttons.values(), self.built_in])
        self.resize(900, 560)
        self.refresh()

    def _group(self, pill: ActionPill, tools, row: int) -> int:
        """A group: its pill on the left, its tools beside it (owner, 21-11-2026: the text next to the pill, not
        under it, so the card's width is used). The row after the tools takes the height the pill has left."""
        self.grid.addWidget(pill, row, 0, len(tools) + 1, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        for tool in tools:
            row = self._tool_row(tool, row)
        self.grid.setRowStretch(row, 1)
        self.grid.setRowMinimumHeight(row, 6)
        return row + 1

    def _tool_row(self, tool: state.Tool, row: int) -> int:
        mark = QLabel()
        self.rows[tool.command] = mark
        self.grid.addWidget(mark, row, 1)
        self.grid.addWidget(QLabel(tool.package), row, 2)
        self.grid.addWidget(hint_label(f"Tests {tool.used_by}" if tool.used_by[0].isdigit() else tool.used_by),
                            row, 3)
        return row + 1

    def refresh(self) -> None:
        tools = [t for g in state.GROUPS for t in g.tools] + list(state.BUILT_IN)
        found = 0
        for tool in tools:
            where = state.find_tool(tool.command, self.home)
            found += bool(where)
            self.rows[tool.command].setText(f"<span style='color:{GREEN if where else GREY};'>"
                                            f"{'●' if where else '○'}</span>")
            self.rows[tool.command].setToolTip(where or f"{tool.command} is not on PATH")
        self.found_box.set_value(f"{found}/{len(tools)}", "The tools the tests can find now; a layered package "
                                 "counts after the reboot.")
        self.found_box.set_colour(GREEN if found == len(tools) else ORANGE)
        script = state.installer(self.board_test)
        for button in (*self.buttons.values(), self.all_button):
            button.setEnabled(script is not None)
        for group in state.GROUPS:
            button = self.buttons[group.option]
            complete = all(state.find_tool(t.command, self.home) for t in group.tools)
            button.caption.setText("Installed" if complete else "Install")
            button.setToolTip("Everything in this group is there." if complete else f"{group.what} ({group.option})")
            if complete:
                button.setEnabled(False)
        if script is None:
            self.state.set_status("Board Test not found", "warn",
                                  f"Its installer is not in {self.board_test}: install Board Test from the portal.")
        else:
            self.state.set_status("Ready", "ok")

    def install(self, option: str) -> None:
        script = state.installer(self.board_test)
        if script is None:
            return
        try:
            self.launch(f"{shlex.quote(str(script))} {option}")
        except RuntimeError as exc:
            QMessageBox.warning(self, window_title("Install"), str(exc))


# --------------------------------------------------------------------------------------------- MangoHud Config
MANGOHUD_INFO = ("<b>MangoHud Config</b> opens MangoHud's own settings file, <code>~/.config/MangoHud/"
                 "MangoHud.conf</code>, to edit and save; a file that is not there yet is made on Save.<br><br>"
                 "<b>FPS log</b> sets the three lines BC-250 Board Test needs to show a game's FPS: "
                 "<code>output_folder=~/mangohud-logs</code>, <code>autostart_log=1</code> and "
                 "<code>log_interval=500</code>; Save then makes the folder. MangoHud writes a log file per game "
                 "session while the game runs. Delete logs removes the ones older than 30 days.<br><br>"
                 "MangoHud must be active for the game, for example with the Steam launch option "
                 "<code>mangohud %command%</code>. Without the log, Board Test still shows the game's name and its "
                 "CPU and GPU share.")
OLD_LOG_DAYS = 30


class MangoHudWindow(QuickfixWindow):
    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["mangohud"], MANGOHUD_INFO, **kwargs)
        self.resize(900, 640)
        self.path = state.mangohud_conf(self.home)
        self.folder = self.home / state.LOG_FOLDER
        self.file_box = MetricBox("File")
        self.log_box = MetricBox("FPS log")
        self.logs_box = MetricBox("Log files")
        self.log_button = ActionPill("FPS log", "Set in the text")
        self.log_button.setToolTip("Set the three lines of the FPS log in the text; Save writes them")
        self.log_button.clicked.connect(self.add_logging)
        self.save_button = ActionPill("Save", "Your edits")
        self.save_button.clicked.connect(self.save)
        self.revert_button = ActionPill("Revert", "Revert changes")
        self.revert_button.setToolTip("Read the file again; your edits go")
        self.revert_button.clicked.connect(self.refresh)
        self.folder_button = ActionPill("Log folder", "Click to open")
        self.folder_button.setToolTip(f"Open {self.folder}")
        self.folder_button.clicked.connect(lambda: show_in_folder(self.folder))
        self.clean_button = ActionPill("Delete logs", f"Older than {OLD_LOG_DAYS} days")
        self.clean_button.setToolTip(f"Remove the log files older than {OLD_LOG_DAYS} days")
        self.clean_button.clicked.connect(self.delete_old_logs)
        self.set_rows([self.file_box, self.log_box, self.logs_box, self.revert_button, self.save_button],
                      [self.log_button, self.folder_button, self.clean_button])
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.editor.textChanged.connect(self.show_changed)
        self.page.addWidget(self.editor, 1)
        self.saved = ""
        self.refresh()

    def refresh(self) -> None:
        try:
            self.saved = self.path.read_text(encoding="utf-8")
            exists = True
        except FileNotFoundError:
            self.saved, exists = "", False
        except OSError as exc:
            self.saved, exists = "", False
            self.state.set_status("Not readable", "bad", str(exc))
        self.editor.blockSignals(True)
        self.editor.setPlainText(self.saved)
        self.editor.blockSignals(False)
        self.file_box.set_value("There" if exists else "New", str(self.path) if exists else
                                f"{self.path} is not there yet: Save makes it.")
        self.file_box.set_colour(GREEN if exists else GREY)
        logs = state.log_files(self.folder)
        self.logs_box.set_value(str(len(logs)), f"In {self.folder}")
        self.folder_button.setEnabled(self.folder.is_dir())
        self.clean_button.setEnabled(bool(self.old_logs()))
        self.show_changed()

    def show_changed(self) -> None:
        text = self.editor.toPlainText()
        changed = text != self.saved
        self.save_button.setEnabled(changed)
        self.revert_button.setEnabled(changed)
        values = state.conf_values(text)
        on = state.logging_on(values)
        self.log_box.set_value("On" if on else "Off", f"Logs to {values['output_folder']}" if on else
                               "MangoHud writes no log: FPS log sets it.")
        self.log_box.set_colour(GREEN if on else GREY)
        self.log_button.setEnabled(state.with_logging(text, self.folder) != (text if text.endswith("\n") or not text
                                                                             else text + "\n"))
        self.state.set_status("Edited, not saved" if changed else "Saved", "warn" if changed else "ok")

    def add_logging(self) -> None:
        self.editor.setPlainText(state.with_logging(self.editor.toPlainText(), self.folder))

    def save(self) -> None:
        text = self.editor.toPlainText()
        if text and not text.endswith("\n"):
            text += "\n"
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_name(self.path.name + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(self.path)
            folder = state.conf_values(text).get("output_folder", "")
            if folder:
                Path(folder).expanduser().mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self, window_title("Save"), f"{self.path} could not be written: {exc}")
            return
        self.refresh()

    def old_logs(self) -> list[Path]:
        limit = datetime.datetime.now().timestamp() - OLD_LOG_DAYS * 86400
        return [p for p in state.log_files(self.folder) if p.stat().st_mtime < limit]

    def delete_old_logs(self) -> None:
        old = self.old_logs()
        if not old or QMessageBox.question(
                self, window_title("Delete logs"), f"Delete the {len(old)} log files older than {OLD_LOG_DAYS} "
                f"days in {self.folder}?") != QMessageBox.StandardButton.Yes:
            return
        for path in old:
            path.unlink(missing_ok=True)
        self.refresh()


# -------------------------------------------------------------------------------------------------- the switches
class SwitchWindow(QuickfixWindow):
    """A quickfix that turns one thing on or off: its status boxes, Turn on and Turn off. A subclass reads its state
    in read() and returns what the window shows."""

    CHANGE = ""                         # system.py's change: metrics, sensors, vrm, mapcount, journal, iommu, ...

    def __init__(self, quickfix: Quickfix, info: str, boxes: tuple[str, ...], **kwargs) -> None:
        super().__init__(quickfix, info, **kwargs)
        self.boxes = {caption: MetricBox(caption) for caption in boxes}
        self.on_button = ActionPill("Turn on", "Click to apply")
        self.on_button.clicked.connect(self.turn_on)
        self.off_button = ActionPill("Turn off", "Click to undo")
        self.off_button.clicked.connect(self.turn_off)
        boxes, pills = list(self.boxes.values()), [self.on_button, self.off_button]
        if len(boxes) + len(pills) <= self.ROW_MAX:
            self.set_rows(boxes + pills)
        else:                                   # more than five: the boxes on their row, the pills under them
            self.set_rows(boxes, pills)
        self.note = hint_label("")
        self.page.addWidget(self.note)
        self.page.addStretch(1)

    def show_box(self, caption: str, value: str, tooltip: str, good: bool | None) -> None:
        box = self.boxes[caption]
        box.set_value(value, tooltip)
        box.set_colour(GREY if good is None else GREEN if good else ORANGE)

    def on_args(self) -> list[str]:
        return [self.CHANGE, "on"]

    def turn_on(self) -> None:
        self.as_root(self.on_args(), "Turn on")

    def turn_off(self) -> None:
        self.as_root([self.CHANGE, "off"], "Turn off")


METRICS_INFO = ("<b>Fix GPU Metrics</b> lets the GPU governor (cyan-skillfish-governor-smu) show the real GPU load. "
                "The governor measures the load to drive the clock anyway; with <code>fix-metrics</code> on, it also "
                "writes that load into a patched copy of <code>gpu_metrics</code> and mounts it over the sysfs file, "
                "so the Steam performance overlay, MangoHud and radeontop show a real GPU %.<br><br>"
                "Turn on sets <code>fix-metrics = true</code> and the method in the <code>[gpu-usage]</code> table of "
                "<code>/etc/cyan-skillfish-governor-smu/config.toml</code>, after a dated backup of it beside it "
                "(<code>config.toml.bak-YYYYMMDD-HHMMSS</code>, as BC-250 GPU Manager makes), and restarts a governor "
                "that runs. <b>busy-flag</b> samples the GPU's busy bit (the default), <b>process</b> sums the "
                "programs' GPU time (more CPU), <b>kernel</b> only works on a patched kernel.<br><br>"
                "On some kernels the patching misbehaves: if the overlay or the governor acts up, turn it off again. "
                "A kernel that reports the load itself does not need it.")


class MetricsWindow(SwitchWindow):
    CHANGE = "metrics"

    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["metrics"], METRICS_INFO, ("Governor", "fix-metrics", "Mounted"), **kwargs)
        self.method = QComboBox()
        self.method.addItems(system.METHODS)
        self.method.setToolTip("How the governor measures the load")
        self.method.currentIndexChanged.connect(lambda _i: self.refresh(keep_method=True))
        self.header.second_row.insertWidget(self.header.second_row.indexOf(self.on_button), self.method)
        self.refresh()

    def on_args(self) -> list[str]:
        return ["metrics", "on", "--method", self.method.currentText()]

    def refresh(self, keep_method: bool = False) -> None:
        m = state.metrics(self.root)
        if not keep_method and m.method in system.METHODS:
            self.method.blockSignals(True)
            self.method.setCurrentText(m.method)
            self.method.blockSignals(False)
        self.show_box("Governor", "Installed" if m.installed else "Missing",
                      "Its config.toml is there" if m.installed else
                      "The GPU governor is not installed: BC-250 GPU Manager installs it.", m.installed or None)
        self.show_box("fix-metrics", "On" if m.fix else "Off", f"method = {m.method or 'busy-flag'}", m.fix)
        self.show_box("Mounted", "Yes" if m.mounted else "No", "A patched gpu_metrics is mounted over the sysfs "
                      "file" if m.mounted else "No patched gpu_metrics is mounted", m.mounted)
        same = m.fix and (m.method or "busy-flag") == self.method.currentText()
        self.on_button.setText("Apply" if m.fix else "Turn on")
        self.on_button.setEnabled(m.installed and not m.problem and not same)
        self.off_button.setEnabled(m.installed and not m.problem and m.fix)
        if m.problem:
            self.state.set_status("Not readable", "bad", m.problem)
        elif not m.installed:
            self.state.set_status("No governor", "warn", "Install the GPU governor first (BC-250 GPU Manager).")
        elif m.fix and not m.mounted:
            self.state.set_status("On, not mounted", "warn", "fix-metrics is on, but no patched gpu_metrics is "
                                  "mounted: the governor may not run (BC-250 GPU Manager shows it).")
        else:
            self.state.set_status("On" if m.fix else "Off", "ok" if m.fix else "info")
        self.note.setText("Check it: <code>mount | grep gpu_metrics</code> shows the patched copy.")


SENSORS_INFO = ("<b>Sensors Module</b> makes sure a driver serves the board's SuperIO chip, a Nuvoton NCT6686D, which "
                "gives the board's temperatures and fan speeds (BC-250 Board Test's test 22, lm_sensors' "
                "<code>sensors</code>). Bazzite loads the nct6687 driver for it by itself since image 45.20261117. "
                "Other images may not load it. The kernel's own "
                "nct6683 driver only loads when it is forced.<br><br>Turn on writes "
                f"<code>{system.SENSORS_LINE}</code> to <code>/etc/{system.SENSORS_CONF}</code>, so nct6683 loads at "
                "every boot, and loads it now; it is offered only when no driver serves the chip. Turn off removes "
                "that file; the driver stays loaded until the next boot.")


class SensorsWindow(SwitchWindow):
    CHANGE = "sensors"

    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["sensors"], SENSORS_INFO, ("Driver", "Forced at boot", "Sensors"), **kwargs)
        self.refresh()

    def refresh(self) -> None:
        s = state.sensors(self.root)
        forced = s.ours or bool(s.elsewhere)
        self.show_box("Driver", s.driver or "None", f"The {s.driver} driver is loaded" if s.driver else
                      "Neither nct6683 nor nct6687 is loaded", bool(s.driver))
        self.show_box("Forced at boot", "Yes" if forced else "No", f"Set in /etc/modprobe.d/{s.elsewhere}"
                      if s.elsewhere else f"/etc/{system.SENSORS_CONF}" if s.ours else
                      "nct6683 is not forced" + (f"; {s.driver} needs no forcing" if s.driver else ""),
                      True if forced else None)
        self.show_box("Sensors", s.hwmon or "None", f"The chip reports as hwmon {s.hwmon}" if s.hwmon else
                      "No hwmon of the chip", bool(s.hwmon))
        self.on_button.setEnabled(not s.on)
        self.off_button.setEnabled(s.ours)
        self.state.set_status("On" if s.on else "Off", "ok" if s.on else "info")
        self.note.setText(f"Forced by /etc/modprobe.d/{s.elsewhere}: Turn off does not remove another file."
                          if s.elsewhere and not s.ours else "")


VRM_INFO = ("<b>VRM Sensors</b> builds and loads <code>bc250_vrm</code>, the kernel module that reads the board's "
            "voltage regulator: the voltage, current, power and regulator temperature of the CPU and the GPU supply, "
            "and the 12 V input. BC-250 System Overlay shows them, and BC-250 Board Test's test 22 and lm_sensors' "
            "<code>sensors</code> report them. Bazzite does not include the module.<br><br>"
            f"Turn on copies the module's source (<code>{system.VRM_REPO}</code> {system.VRM_TAG}, which comes with "
            f"the app) to <code>/var/{system.VRM_DIR}</code> and starts <code>{system.VRM_UNIT}</code>, which builds "
            "the module for the running kernel and loads it, now and at every boot. After a kernel update the first "
            "boot builds it again, which takes a few seconds. Turn off unloads the module and removes the service "
            "and the folder.<br><br>"
            "The module reads the regulator through the SuperIO chip. For every reading it writes the regulator's "
            "page register, which selects the CPU or the GPU supply. It writes no voltage, current or limit.")


class VrmWindow(SwitchWindow):
    CHANGE = "vrm"

    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["vrm"], VRM_INFO, ("Module", "At boot", "Sensors"), **kwargs)
        self.refresh()

    def refresh(self) -> None:
        v = state.vrm(self.root)
        self.show_box("Module", "Loaded" if v.loaded else "Not loaded", f"{system.VRM_MODULE} {system.VRM_TAG[1:]}"
                      if v.ours else f"/sys/module/{system.VRM_MODULE}", v.loaded)
        self.show_box("At boot", "Yes" if v.ours else "No", f"/etc/systemd/system/{system.VRM_UNIT}" if v.ours else
                      "The quickfix's service is not there", True if v.ours else None)
        self.show_box("Sensors", system.VRM_MODULE if v.hwmon else "None", "The regulator's sensors are there"
                      if v.hwmon else "No sensors of the regulator", v.hwmon)
        # On, but not loaded: Turn on is there again. It copies the script and the source anew and starts the service,
        # which is what a newer version of the quickfix needs after a load that failed.
        self.on_button.setEnabled(v.can_build and (not v.on or (v.ours and not v.loaded)))
        self.off_button.setEnabled(v.ours)
        self.state.set_status("On" if v.on else "Off", "ok" if v.on and v.loaded else "warn" if v.on else "info")
        if v.ours and not v.loaded:
            note = f"The module is not loaded. Turn on tries again. See why with: journalctl -b -u {system.VRM_UNIT}"
        elif v.loaded and not v.hwmon:
            note = "The module is loaded, but the regulator did not answer: there are no sensors."
        elif v.loaded and not v.ours:
            note = "The module was loaded by something else: Turn off does not unload it."
        elif not v.can_build:
            note = "The running kernel's build files are missing, so the module cannot be built on this image."
        else:
            note = ""
        self.note.setText(note)


MAPCOUNT_INFO = ("<b>Game Memory Map</b> raises <code>vm.max_map_count</code>, the number of memory areas one program "
                 "may map. Some games (and Proton) need many more than the kernel's default and crash without them; "
                 f"SteamOS and Bazzite set {system.MAPCOUNT}.<br><br>Turn on writes it to "
                 f"<code>/etc/{system.MAPCOUNT_CONF}</code> and sets it now. Turn off removes that file and reads the "
                 "system's settings again. BC-250 Board Test's test 37 reports the value.")


class MapCountWindow(SwitchWindow):
    CHANGE = "mapcount"

    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["mapcount"], MAPCOUNT_INFO, ("vm.max_map_count", "Set by"), **kwargs)
        self.refresh()

    def refresh(self) -> None:
        m = state.mapcount(self.root)
        high = m.value >= system.MAPCOUNT
        self.show_box("vm.max_map_count", f"{m.value:,}" if m.value else "—",
                      f"{system.MAPCOUNT:,} or more is what games need", high if m.value else None)
        self.show_box("Set by", "This quickfix" if m.ours else "The system" if high else "—",
                      f"/etc/{system.MAPCOUNT_CONF}" if m.ours else "Another sysctl.d file, or the image's own"
                      if high else "The kernel's default", True if high else None)
        self.on_button.setEnabled(not high)
        self.off_button.setEnabled(m.ours)
        self.state.set_status("On" if high else "Off", "ok" if high else "info")


JOURNAL_INFO = ("<b>Persistent Journal</b> keeps the system journal on the disk, in <code>/var/log/journal</code>. "
                "Without that folder journald keeps it in memory only, and the logs of a boot that crashed or froze "
                "are gone after it: BC-250 Board Test's test 34 cannot read the previous boot's.<br><br>Turn on makes "
                "the folder (<code>systemd-tmpfiles --create</code>) and moves the journal there "
                "(<code>journalctl --flush</code>). Turn off works only on a folder this quickfix made: it moves the "
                "journal back to memory and removes the folder, with the logs in it. journald keeps the folder's size "
                "within its own limits.")


class JournalWindow(SwitchWindow):
    CHANGE = "journal"

    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["journal"], JOURNAL_INFO, ("Journal", "Made by"), **kwargs)
        self.refresh()

    def refresh(self) -> None:
        j = state.journal(self.root)
        self.show_box("Journal", "On disk" if j.persistent else "In memory", "/var/log/journal", j.persistent)
        self.show_box("Made by", "This quickfix" if j.ours else "The system" if j.persistent else "—",
                      "The folder was there already" if j.persistent and not j.ours else "", True if j.persistent
                      else None)
        self.on_button.setEnabled(not j.persistent)
        self.off_button.setEnabled(j.ours)
        self.state.set_status("On" if j.persistent else "Off", "ok" if j.persistent else "info")

    def turn_off(self) -> None:
        if QMessageBox.question(self, window_title("Turn off"), "Remove /var/log/journal, with the logs of every "
                                "earlier boot in it?") == QMessageBox.StandardButton.Yes:
            super().turn_off()


class KargWindow(SwitchWindow):
    """A kernel argument added or removed with rpm-ostree kargs: the running kernel's, the next boot's and who added
    it. A change applies from the next boot; the window says so and never reboots."""

    BOXES = ("Now", "Next boot", "Added by")

    def __init__(self, quickfix: Quickfix, info: str, next_kargs: Callable[[], list[str] | None] = system.next_kargs,
                 **kwargs) -> None:
        self.next_kargs = next_kargs
        super().__init__(quickfix, info, self.BOXES, **kwargs)

    def read(self) -> state.Karg:
        return state.karg(self.CHANGE, self.root, self.next_kargs)

    def applied_otherwise(self, k: state.Karg) -> str:
        """Why Turn on is not needed although the argument is not set ("" when it is needed)."""
        return ""

    def show_more(self, k: state.Karg) -> None:
        """A subclass's own boxes."""

    def refresh(self) -> None:
        k = self.read()
        self.show_more(k)
        self.show_box("Now", "Set" if k.now else "Not set", f"{k.arg} on the running kernel's command line"
                      if k.now else f"{k.arg} is not on /proc/cmdline", k.now or None)
        if k.next is None:
            self.show_box("Next boot", "—", "rpm-ostree could not read the kernel arguments", None)
        else:
            self.show_box("Next boot", "Set" if k.next else "Not set",
                          f"rpm-ostree kargs {'has' if k.next else 'lacks'} {k.arg}", k.next or None)
        self.show_box("Added by", "This quickfix" if k.ours else "The system" if k.now or k.next else "—",
                      f"/var/{system.KARGS_DIR}/{self.CHANGE}.karg" if k.ours else
                      "Set by hand, or by the image: Turn off removes only what this quickfix added"
                      if k.now or k.next else "", True if k.ours or k.now or k.next else None)
        otherwise = self.applied_otherwise(k)
        self.on_button.setEnabled(k.next is False and not otherwise)
        self.off_button.setEnabled(k.next is not None and k.ours)
        if k.next is None:
            self.state.set_status("No rpm-ostree", "warn", "rpm-ostree kargs could not read the kernel arguments.")
        elif k.pending:
            self.state.set_status("Reboot to apply", "warn", f"{system.REBOOT}.")
        elif k.next:
            self.state.set_status("On", "ok")
        elif otherwise:
            self.state.set_status("Off already", "ok", otherwise)
        else:
            self.state.set_status("Off", "info")
        self.note.setText(f"{system.REBOOT}." if k.pending else otherwise)


IOMMU_INFO = ("<b>IOMMU Off</b> keeps the kernel from using the board's AMD IOMMU (AMD-Vi), which is broken on the "
              "BC-250 and makes the system unstable. The modded BIOS can switch it off; without it, the kernel "
              f"argument <code>{system.KARGS['iommu']}</code> does the same from Linux's side.<br><br>Turn on adds "
              "it with <code>rpm-ostree kargs</code>, which makes a new deployment, and notes in "
              f"<code>/var/{system.KARGS_DIR}</code> that the quickfix added it; Turn off removes only an argument the "
              "quickfix added. Either applies from the next boot: restart the board (<code>systemctl reboot</code>). "
              "With the IOMMU off there are no IOMMU groups, which is what BC-250 Board Test's test 23 checks; "
              "passing a PCI device to a virtual machine (VFIO) is then not possible. Turn on is not offered when "
              "the BIOS has the IOMMU off already.")
MITIGATIONS_INFO = ("<b>CPU Mitigations Off</b> turns off the kernel's protections against the CPU's speculative "
                    "execution flaws (Spectre, Meltdown and the like), with the kernel argument "
                    f"<code>{system.KARGS['mitigations']}</code>. They cost speed: roughly 18 FPS in games on this "
                    "board. Without them a program could, in principle, read memory of other programs: keep them on "
                    "where the board runs code you do not trust.<br><br>Turn on adds the argument with "
                    "<code>rpm-ostree kargs</code>, which makes a new deployment, and notes in "
                    f"<code>/var/{system.KARGS_DIR}</code> that the quickfix added it; Turn off removes only an "
                    "argument the quickfix added. Either applies from the next boot: restart the board "
                    "(<code>systemctl reboot</code>). BC-250 Board Test's test 24 reports it.")


class IommuWindow(KargWindow):
    CHANGE = "iommu"
    BOXES = ("IOMMU", "Now", "Next boot", "Added by")

    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["iommu"], IOMMU_INFO, **kwargs)
        self.refresh()

    def applied_otherwise(self, k: state.Karg) -> str:
        return "The BIOS has the IOMMU off: there are no IOMMU groups." if k.iommu_groups == 0 and not k.now else ""

    def show_more(self, k: state.Karg) -> None:
        groups = k.iommu_groups
        self.show_box("IOMMU", "—" if groups is None else "Off" if groups == 0 else "On",
                      "No /sys/kernel/iommu_groups" if groups is None else f"{groups} IOMMU groups",
                      None if groups is None else groups == 0)


class MitigationsWindow(KargWindow):
    CHANGE = "mitigations"

    def __init__(self, **kwargs) -> None:
        super().__init__(BY_KEY["mitigations"], MITIGATIONS_INFO, **kwargs)
        self.refresh()


WINDOWS: dict[str, Callable[..., QuickfixWindow]] = {
    "tools": ToolsWindow, "mangohud": MangoHudWindow, "metrics": MetricsWindow, "sensors": SensorsWindow,
    "vrm": VrmWindow, "mapcount": MapCountWindow, "journal": JournalWindow, "iommu": IommuWindow, "mitigations": MitigationsWindow,
}
