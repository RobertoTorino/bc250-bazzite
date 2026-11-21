# SPDX-License-Identifier: GPL-3.0-or-later
"""The main window: the four steps (build, install, test, use) with their state and buttons, and the output of the
step that runs. Every step runs bc250-mesh-shaders.sh; the ones that change the system go through polkit (pkexec)."""

from __future__ import annotations

import subprocess
from html import escape
from pathlib import Path

from PyQt6.QtCore import QProcess, Qt, QUrl
from PyQt6.QtGui import QCloseEvent, QDesktopServices
from PyQt6.QtWidgets import QApplication, QCheckBox, QDialog, QGridLayout, QHBoxLayout, QLabel, QMessageBox

from bc250_core import SUITE_MANUAL_URL, window_title
from bc250_core import __version__ as CORE_VERSION
from bc250_core.settings import SettingsStore
from bc250_core.updates import Fetch, UpdateChecker
from bc250_core.card import CardWindow
from bc250_core.theme import GREEN, GREY, ORANGE, RED
from bc250_core.widgets import ActionPill, MetricBox, Terminal, hint_label, same_width

from . import APP_NAME, INFO, LOGO_PATH, SCRIPT, __version__
from .status import Status, parse, verdict
from .switches import SWITCHES, Switch, SwitchesDialog, launch_options
from .updates import Release, is_newer, latest_release

MANUAL_URL = f"{SUITE_MANUAL_URL}apps/mesh/"
INTRO = ("Games that need mesh shaders (DirectX 12 Ultimate) get them on the BC-250 through RADV with DirectMesh. "
         "The app builds the driver on this board and installs it beside the system Mesa. The system Mesa is "
         "never changed. Games use the driver only with their launch options, and only after the test passed on the "
         f"running kernel. <a href='{MANUAL_URL}'>Wiki</a>")
ABOUT = ("<b>BC-250 Mesh Shaders</b> builds, installs and tests a second graphics driver that gives games mesh "
         "shaders.<br><br><b>What it changes.</b> The driver goes in <code>/usr/local/lib/bc250-mesh-shaders</code>, "
         "after you give your password. The system Mesa is never changed, and Remove takes the driver out again."
         f"<br><br><a href='{MANUAL_URL}'>BC-250 Mesh Shaders in the wiki</a>")
CHECK_AT_START = "updates/check_on_start"
CHECK_LINK = "#check"
NOT_AUTHORISED = (126, 127)             # pkexec: the password dialog was canceled or refused

# What runs, by action: (arguments, needs root, text while it runs)
ACTIONS = {
    "build": (["--build"], False, "Building the driver (20 to 40 minutes)…"),
    "install": (["--install-driver"], True, "Installing the driver…"),
    "remove": (["--remove-driver"], True, "Removing the driver…"),
    "test": (["--test"], False, "Testing the driver…"),
}


class MeshSettings(SettingsStore):
    DEFAULTS: dict = {CHECK_AT_START: True, **{switch.setting: False for switch in SWITCHES}}


class MainWindow(CardWindow):
    def __init__(self, script: Path = SCRIPT, check_updates: bool | None = None, fetch: Fetch | None = None):
        """*check_updates*: look for a newer DirectMesh release now (None: as the setting says); *fetch*: the
        GitHub request, for tests."""
        super().__init__(LOGO_PATH, APP_NAME, __version__, ABOUT)
        self.resize(self.width(), 640)
        self.script = script
        self.fetch = fetch
        self.release: Release | None = None          # the newest DirectMesh release, once looked up
        self.update_checker = UpdateChecker(self)
        self.update_checker.finished.connect(self._release_checked)
        self.settings = MeshSettings(INFO, self)
        self.status = Status()
        self.action = ""
        self._output = ""
        self.process: QProcess | None = None

        self.pill = self.state                       # the state beside the title
        self.refresh_button.setToolTip("Read the state again")

        # The first row: where the three steps stand, and the two actions for a game. The second: the steps.
        self.build_box, self.driver_box, self.test_box = MetricBox("Build"), MetricBox("Driver"), MetricBox("Test")
        self.copy_button = ActionPill("Copy options", "For Steam",
                                      "Copy the Steam launch options for a game to the clipboard")
        self.copy_button.clicked.connect(self.copy_launch_options)
        self.switches_button = ActionPill("Switches", "None on", "The driver's switches, for comparisons in one game")
        self.switches_button.clicked.connect(self.on_switches)
        self.build_button = ActionPill("Build", "20 to 40 minutes", "Build RADV with DirectMesh in a podman container")
        self.build_button.clicked.connect(self.on_build)
        self.install_button = ActionPill("Install", "The build", "Install the build in /usr/local/lib/bc250-mesh-"
                                         "shaders. You will be asked for your password")
        self.install_button.clicked.connect(self.on_install)
        self.remove_button = ActionPill("Remove", "The driver",
                                        "Remove the driver. Games with the launch options no longer start")
        self.remove_button.clicked.connect(self.on_remove)
        self.test_button = ActionPill("Run test", "A few minutes",
                                      "Run the mesh test with the installed driver (a few minutes)")
        self.test_button.clicked.connect(self.on_test)

        self.system = QLabel()                       # board, kernel and Mesa, beside the icon
        self.system.setWordWrap(True)
        self.header.add_second(self.system, 1)
        self.auto_check = QCheckBox("Look for a newer DirectMesh release at start")
        self.auto_check.setToolTip("One small request to GitHub each time the app starts")
        self.auto_check.setChecked(self.settings.get(CHECK_AT_START))
        self.auto_check.toggled.connect(lambda on: self.settings.set(CHECK_AT_START, on))
        self.page.addWidget(self.auto_check)
        self.page.addWidget(hint_label(INTRO))

        # The rows of boxes and pills, under the introduction and from the window's left edge.
        gap = self.header.second_row.spacing()
        for widgets in ([self.build_box, self.driver_box, self.test_box, self.copy_button, self.switches_button],
                        [self.build_button, self.install_button, self.remove_button, self.test_button]):
            row = QHBoxLayout()
            row.setSpacing(gap)
            for widget in widgets:
                row.addWidget(widget)
            row.addStretch(1)
            self.page.addLayout(row)

        # The four steps: a box each on the left, which only names the step, with where the step stands beside it.
        self.build_state, self.install_state, self.test_state, self.use_state = (self._state_label() for _ in range(4))
        self.build_state.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse
                                                 | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.build_state.linkActivated.connect(self._link)
        steps = QGridLayout()
        steps.setColumnStretch(1, 1)
        steps.setHorizontalSpacing(14)
        self.step_boxes = []
        for number, (name, what, state) in enumerate((("1. Build", "The driver, on this board", self.build_state),
                                                      ("2. Install", "Beside the system Mesa", self.install_state),
                                                      ("3. Test", "On the running kernel", self.test_state),
                                                      ("4. Use", "Per game, in Steam", self.use_state))):
            box = MetricBox(what)
            box.set_value(name)
            self.step_boxes.append(box)
            steps.addWidget(box, number, 0)
            steps.addWidget(state, number, 1)
        self.page.addLayout(steps)
        boxes = [self.build_box, self.driver_box, self.test_box, self.copy_button, self.switches_button,
                 self.build_button, self.install_button, self.remove_button, self.test_button, *self.step_boxes]
        same_width(boxes)
        margins = self.page.contentsMargins()
        self.resize(margins.left() + margins.right() + self.ROW_MAX * boxes[0].minimumWidth()
                    + (self.ROW_MAX - 1) * gap, 760)

        self.running = QLabel()
        self.running.setStyleSheet("font-weight:600;")
        self.output = Terminal()
        self.output.setPlaceholderText("The output of each step appears here.")
        self.page.addWidget(self.running)
        self.page.addWidget(self.output, 1)
        version = QLabel(f"{APP_NAME} {__version__} · core {CORE_VERSION} · the system Mesa is never changed")
        version.setStyleSheet("color:palette(placeholder-text);")
        self.page.addWidget(version, 0, Qt.AlignmentFlag.AlignRight)

        geometry = self.settings.window_state("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        self.refresh()
        if self.settings.get(CHECK_AT_START) if check_updates is None else check_updates:
            self.check_for_updates()

    @staticmethod
    def _state_label() -> QLabel:
        label = QLabel()
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    # --- State ------------------------------------------------------------------------------------------------

    def refresh(self) -> None:
        try:
            done = subprocess.run(["bash", str(self.script), "--status"], capture_output=True, text=True, timeout=30)
            text = done.stdout
        except (OSError, subprocess.SubprocessError) as exc:
            text = ""
            self.output.setPlainText(f"Could not read the state: {exc}")
        self.set_status(parse(text))

    def chosen_switches(self) -> list[Switch]:
        return [switch for switch in SWITCHES if self.settings.get(switch.setting)]

    def launch_options(self) -> str:
        return launch_options(self.status.launch_options, self.chosen_switches())

    def set_status(self, status: Status) -> None:
        self.status = status
        s = status
        pill, kind, tip = verdict(s)
        self.pill.set_status(pill, kind, tip)
        self.system.setText(f"<b>{escape(s.get('Board') or '?')}</b> · kernel {escape(s.get('Kernel') or '?')} · "
                            f"system Mesa {escape(s.system_mesa or '?')}")

        if not s.built:
            build = f"Not built. Builds DirectMesh {escape(s.directmesh or '?')}. It downloads the Mesa source and " \
                    "the build tools, and checks the source against its signature. The build runs in a Fedora " \
                    "container and takes 20 to 40 minutes."
        else:
            build = f"Built: {escape(s.get('Build'))}."
            if s.build_outdated:
                build += f" <b>This version of the app builds DirectMesh {escape(s.directmesh)}.</b> Build again " \
                         "to get it."
        self.build_state.setText(f"{build}<br>{self._release_line()}")
        self.build_box.set_value("Outdated" if s.built and s.build_outdated else "Built" if s.built else "Not built",
                                 build)
        self.build_box.set_colour(GREEN if s.built and not s.build_outdated else ORANGE)

        if not s.installed:
            install = "Not installed." if s.built else "Not installed. Build it first."
        else:
            install = f"Installed: {escape(s.driver)}, in /usr/local/lib/bc250-mesh-shaders."
            if s.install_outdated:
                install += " <b>A newer build is waiting.</b> Install it."
        self.install_state.setText(install)
        self.driver_box.set_value("Update" if s.installed and s.install_outdated else
                                  "Installed" if s.installed else "None", install)
        self.driver_box.set_colour(GREEN if s.installed and not s.install_outdated else ORANGE if s.built else GREY)

        if not s.installed:
            test = "Needs the installed driver."
        elif s.tested:
            test = f"<span style='color:#2e7d32'><b>Passed</b></span> {escape(s.get('Test')[len('passed '):])}."
        elif s.test_failed:
            test = f"<span style='color:#c62828'><b>Failed</b></span> {escape(s.get('Test')[len('failed '):])}."
        else:
            test = f"{escape(s.get('Test')).capitalize()}. Games only use the driver once it has passed on this kernel."
        self.test_state.setText(test)
        self.test_box.set_value("Passed" if s.installed and s.tested else "Failed" if s.installed and s.test_failed
                                else "Not run" if s.installed else "\u2014", test)
        self.test_box.set_colour(GREEN if s.installed and s.tested else RED if s.installed and s.test_failed
                                 else ORANGE if s.installed else GREY)

        use = (f"Per game, in the Steam launch options: <code>{escape(self.launch_options())}</code><br>"
               "Without a passed test on this kernel, the game starts with the system Mesa.")
        chosen = self.chosen_switches()
        if chosen:
            use += f"<br><b>Switches:</b> {escape(', '.join(switch.label for switch in chosen))}."
        self.switches_button.caption.setText(f"{len(chosen)} on" if chosen else "None on")
        self.use_state.setText(use)
        self._fit_states()
        self._update_buttons()

    def _release_line(self) -> str:
        """What the check for a newer DirectMesh release found, with a link to check again or to the release."""
        pinned = self.status.directmesh.split(",")[0]
        again = f"<a href='{CHECK_LINK}'>Check again</a>"
        release = self.release
        if self.update_checker.running:
            return "Looking for a newer DirectMesh release…"
        if release is None:
            return f"<a href='{CHECK_LINK}'>Look for a newer DirectMesh release</a>"
        if release.error:
            return f"Could not look for a newer DirectMesh release: {escape(release.error)}. {again}"
        if is_newer(release, pinned):
            return (f"<b>DirectMesh {escape(release.version)} is out</b> ({escape(release.published)}). A newer version "
                    f"of this app brings it, through the portal. <a href='{escape(release.url)}'>Release notes</a>")
        return f"DirectMesh {escape(release.version)} is the newest release. {again}"

    def _fit_states(self) -> None:
        """Each state text keeps the height its lines need at its width. Qt leaves wrapped text out of a window's
        minimum height, so a short window would otherwise squeeze a second line out of sight."""
        for label in (self.build_state, self.install_state, self.test_state, self.use_state):
            label.setMinimumHeight(label.heightForWidth(max(label.width(), 300)))

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        self._fit_states()                  # a narrower window wraps into more lines

    def _update_buttons(self) -> None:
        s, idle = self.status, self.process is None
        self.refresh_button.setEnabled(idle)
        self.build_button.setEnabled(idle and s.is_bc250)
        self.install_button.setEnabled(idle and s.built and (not s.installed or s.install_outdated))
        self.remove_button.setEnabled(idle and s.installed)
        self.test_button.setEnabled(idle and s.installed)
        self.copy_button.setEnabled(s.installed)
        self.switches_button.setEnabled(s.installed)

    # --- Actions ----------------------------------------------------------------------------------------------

    def _ask(self, title: str, text: str) -> bool:
        answer = QMessageBox.question(self, window_title(title), text)
        return answer == QMessageBox.StandardButton.Yes

    def on_build(self) -> None:
        if self._ask("Build", f"Build RADV with DirectMesh {self.status.directmesh or ''}?\n\n"
                     "It runs as your user in a Fedora container (podman).\n"
                     "It downloads the Mesa source and the build tools, several hundred MB in all.\n"
                     "It takes 20 to 40 minutes.\n"
                     "Nothing on the system changes."):
            self.run("build")

    def on_install(self) -> None:
        if self._ask("Install", "Install RADV with DirectMesh?\n\n"
                     "It goes to /usr/local/lib/bc250-mesh-shaders, beside the system Mesa.\n"
                     "The system Mesa is never changed.\n"
                     "Nothing uses it until the test has passed and you give a game the launch options.\n"
                     "Remove takes it out again.\n"
                     "You will be asked for your password."):
            self.run("install")

    def on_remove(self) -> None:
        if self._ask("Remove", "Remove RADV with DirectMesh?\n\n"
                     f"Also remove \"{self.launch_options()}\" from the launch options of your games.\n"
                     "Without the driver, those games do not start.\n"
                     "You will be asked for your password."):
            self.run("remove")

    def on_test(self) -> None:
        self.run("test")

    def check_for_updates(self) -> None:
        fetch = self.fetch
        if self.update_checker.start(lambda: latest_release(fetch)):
            self.set_status(self.status)

    def _release_checked(self, release: Release) -> None:
        self.release = release
        self.set_status(self.status)

    def _link(self, href: str) -> None:
        if href == CHECK_LINK:
            self.check_for_updates()
        else:
            QDesktopServices.openUrl(QUrl(href))

    def on_switches(self) -> None:
        dialog = SwitchesDialog(self.chosen_switches(), self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        chosen = dialog.chosen()
        for switch in SWITCHES:
            self.settings.set(switch.setting, switch in chosen)
        self.set_status(self.status)

    def copy_launch_options(self) -> None:
        QApplication.clipboard().setText(self.launch_options())
        self.running.setText("Launch options copied. Paste them into a game's Properties → Launch options in Steam.")

    def command(self, action: str) -> list[str]:
        args, root, _ = ACTIONS[action]
        cmd = ["bash", str(self.script), *args]
        return ["pkexec", "/usr/bin/bash", *cmd[1:]] if root else cmd

    def run(self, action: str) -> None:
        if self.process is not None:
            return
        self.action = action
        self._output = ""
        self.output.set_text("")
        self.running.setText(ACTIONS[action][2])
        cmd = self.command(action)
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.readyReadStandardOutput.connect(self._read)
        process.finished.connect(self._finished)
        process.errorOccurred.connect(self._error)
        self.process = process
        self._update_buttons()
        process.start(cmd[0], cmd[1:])

    def _read(self) -> None:
        if self.process is None:
            return
        self._output += bytes(self.process.readAllStandardOutput()).decode("utf-8", "replace")
        self.output.set_text(self._output)

    def _finished(self, code: int, _status=None) -> None:
        root = ACTIONS[self.action][1]
        if code == 0:
            self.running.setText("Done.")
        elif root and code in NOT_AUTHORISED:
            self.running.setText("Not authorized: the password dialog was canceled or refused.")
        else:
            self.running.setText(f"Stopped with exit code {code}. See the output.")
        self.process = None
        self.refresh()

    def _error(self, _error) -> None:
        if self.process is not None and self.process.error() == QProcess.ProcessError.FailedToStart:
            self.running.setText(f"Could not start: {self.process.errorString()}")
            self.process = None
            self._update_buttons()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt override)
        if self.process is not None:
            if not self._ask("Close", "A step is still running. Stop it and close?"):
                event.ignore()
                return
            self.process.terminate()            # the build script then also stops its container
            if not self.process.waitForFinished(15000):
                self.process.kill()
        self.update_checker.stop()
        self.settings.set_window_state("geometry", self.saveGeometry())
        self.settings.sync()
        super().closeEvent(event)
