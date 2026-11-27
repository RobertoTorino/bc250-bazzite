# SPDX-License-Identifier: GPL-3.0-or-later
import json

import pytest
from PyQt6.QtWidgets import QMessageBox

from vram_manager import cmos, guard, learn, main_window, privileged, resume, service, swap, watch
from vram_manager.main_window import MainWindow
from conftest import FakeOstree
from dumps import BOARD_1, FakePort, bank


class Board:
    """Runs the helper's own code on a fake bank, as pkexec would run cmos.py."""

    def __init__(self):
        self.data = bank(BOARD_1)
        self.calls = []

    def __call__(self, args):
        self.calls.append(args)
        bank2 = cmos.Bank(FakePort(self.data))
        try:
            data = cmos.do_read(bank2) if args == ["--read"] else cmos.do_set_uma(bank2, int(args[1]))
        except cmos.CmosError as exc:
            return privileged.Result(False, {}, str(exc))
        return privileged.Result(True, json.loads(json.dumps(data)), "")

    @property
    def uma(self):
        return cmos.Block(bytes(self.data[0x90:0xAC])).uma_mb


@pytest.fixture
def answer(monkeypatch):
    replies = {"value": QMessageBox.StandardButton.Yes, "questions": []}

    def question(_parent, _title, text, *a, **k):
        replies["questions"].append(text)
        return replies["value"]
    monkeypatch.setattr(QMessageBox, "question", question)
    warnings, infos = [], []
    monkeypatch.setattr(QMessageBox, "warning", lambda _p, _t, text: warnings.append(text))
    monkeypatch.setattr(QMessageBox, "information", lambda _p, _t, text: infos.append(text))
    replies["warnings"], replies["infos"] = warnings, infos
    return replies


class Swapper:
    """Runs the swap helper's own code on the temp /etc and /var, as pkexec would run swap.py."""

    def __init__(self, root):
        self.etc, self.var, self.proc = root / "etc", root / "var", root / "proc"
        self.var.mkdir(exist_ok=True)
        self.calls, self.commands = [], []

    def run(self, cmd):
        self.commands.append(cmd)
        if cmd[:3] == ["btrfs", "filesystem", "mkswapfile"]:
            with open(cmd[-1], "wb") as file:
                file.truncate(int(cmd[4][:-1]) * 1024 * 1024)
        return 1 if cmd[0] in ("selinuxenabled", "btrfs") and cmd[1:2] != ["filesystem"] else 0

    def __call__(self, args):
        self.calls.append(args)
        try:
            if args == ["--delete-file"]:
                data = swap.delete_file(self.etc, self.var, self.proc, self.run)
            else:
                options = dict(zip(args[::2], args[1::2]))
                setup = swap.Setup(options["--layout"], options.get("--zram-size", ""), options.get("--compressor", ""),
                                   int(options.get("--file-mib", 0)),
                                   int(options["--swappiness"]) if "--swappiness" in options else None)
                data = swap.apply(setup, self.etc, self.var, self.proc, self.run, btrfs=lambda _p: True)
        except swap.SwapError as exc:
            return privileged.Result(False, {}, str(exc))
        return privileged.Result(True, json.loads(json.dumps(data)), "")


class Guarder:
    """Runs the guard helper's own code on the temp /etc, as pkexec would run guard.py; systemctl --user recorded."""
    def __init__(self, etc):
        self.etc, self.calls, self.systemctl = etc, [], []

    def __call__(self, args):
        self.calls.append(args)
        try:
            data = guard.apply(args[1], self.etc, lambda cmd: 0)
        except guard.GuardError as exc:
            return privileged.Result(False, {}, str(exc))
        return privileged.Result(True, data, "")

    def user(self, cmd):
        self.systemctl.append(cmd)
        return 0, "", ""


def make(qapp, sys_root, proc_root, board, ostree=None, swapper=None, guarder=None):
    swapper = swapper or Swapper(sys_root.parent)
    guarder = guarder or Guarder(swapper.etc)
    return MainWindow(sys_root, proc_root, runner=board, commands=ostree or FakeOstree(), swapper=swapper,
                      etc_root=swapper.etc, var_root=swapper.var, guarder=guarder,
                      config_dir=sys_root.parent / "config", sessions_file=sys_root.parent / "sessions.jsonl",
                      python="/venv/bin/python", app_root=sys_root.parent / "app", user_commands=guarder.user)


def test_shows_the_board(qapp, sys_root, proc_root):
    w = make(qapp, sys_root, proc_root, Board())
    assert w.vram_box.value.text() == "6.0 GiB" and w.gtt_box.value.text() == "9.4 GiB"
    assert w.swap_box.value.text() == "zram"
    assert w.ttm_box.value.text() == "11.5 GiB" and w.ttm_box.caption.text() == "GTT limit"
    assert w.gtt_box.caption.text() == "GTT: all the RAM"
    assert "above the RAM, so the GTT is all the RAM, 9.4 GiB" in w.ttm_box.toolTip()
    assert w.details.text() == "vm.swappiness 10"
    assert w.badge.text() == "6.0 GiB split"
    assert w.combo.currentData() == 6144
    assert not w.apply_button.isEnabled() and not w.undo_button.isEnabled()   # the split it has: nothing to apply
    assert w.ttm_combo.currentData() == 3014656 and not w.ttm_button.isEnabled()
    assert w.ttm_note.isHidden() and w.ttm_reason.isHidden()
    w.combo.setCurrentIndex(main_window.SPLITS.index(4096))
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(None))
    assert w.apply_button.isEnabled() and w.ttm_button.isEnabled()
    assert "framebuffer pin failures" in w.split_info.text_ and "Wiki" in w.ttm_info.text_
    w.close()


def test_apply_reboot_and_undo(qapp, sys_root, proc_root, answer, tmp_path):
    board = Board()
    w = make(qapp, sys_root, proc_root, board)
    w.combo.setCurrentIndex(main_window.SPLITS.index(4096))
    w.apply_split()
    assert board.calls == [["--set-uma", "4096"]] and board.uma == 4096
    assert w.badge.text() == "Reboot to apply"
    assert w.undo_button.isEnabled()
    backups = list((tmp_path / "data/bc250-memory-manager/backups").glob("cmos-*.json"))
    assert len(backups) == 1 and json.loads(backups[0].read_text())["before"]["uma_mb"] == 6144
    w.close()

    # Same boot: still pending.
    w = make(qapp, sys_root, proc_root, board)
    assert w.badge.text() == "Reboot to apply" and w.combo.currentData() == 4096
    assert not w.apply_button.isEnabled()                 # 4 GB is written already
    w.combo.setCurrentIndex(main_window.SPLITS.index(6144))
    assert w.apply_button.isEnabled()                     # back to the booted split: a write, as Undo is
    w.close()

    # After a reboot into the new split.
    (proc_root / "sys/kernel/random/boot_id").write_text("boot-2\n")
    (sys_root / "class/drm/card1/device/mem_info_vram_total").write_text(str(4096 * 1024 * 1024))
    w = make(qapp, sys_root, proc_root, board)
    assert w.badge.text() == "4.0 GiB split"
    assert "4 GB split from the last change is active" in w.split_note.text()
    w.undo()
    assert board.uma == 6144 and w.badge.text() == "Reboot to apply"
    w.close()


def test_reboot_without_the_split(qapp, sys_root, proc_root, answer):
    board = Board()
    w = make(qapp, sys_root, proc_root, board)
    w.combo.setCurrentIndex(main_window.SPLITS.index(8192))
    w.apply_split()
    w.close()
    (proc_root / "sys/kernel/random/boot_id").write_text("boot-2\n")
    w = make(qapp, sys_root, proc_root, board)
    assert "kernel got 6.0 GiB" in w.split_note.text()
    w.close()


def test_cancel_writes_nothing(qapp, sys_root, proc_root, answer):
    answer["value"] = QMessageBox.StandardButton.No
    board = Board()
    w = make(qapp, sys_root, proc_root, board)
    w.combo.setCurrentIndex(0)
    w.apply_split()
    assert board.calls == [] and board.uma == 6144
    w.close()


def test_helper_error_is_shown(qapp, sys_root, proc_root, answer):
    board = Board()
    board.data[0x94] ^= 0xFF                            # a bad checksum: the helper refuses
    w = make(qapp, sys_root, proc_root, board)
    w.combo.setCurrentIndex(main_window.SPLITS.index(4096))
    w.apply_split()
    assert "cannot be trusted" in answer["warnings"][0]
    assert w.badge.text() == "6.0 GiB split"
    w.close()


def test_read_cmos_saves_a_dump(qapp, sys_root, proc_root, tmp_path, monkeypatch):
    shown = []
    monkeypatch.setattr(main_window.TextDialog, "exec", lambda self: shown.append(self.terminal.toPlainText()))
    w = make(qapp, sys_root, proc_root, Board())
    w.read_cmos()
    assert "UMA_SIZE   6144 MB" in shown[0]
    dumps = list((tmp_path / "data/bc250-memory-manager/backups").glob("cmos-dump-*.txt"))
    assert len(dumps) == 1 and "bank 2:" in dumps[0].read_text()
    w.close()


def test_other_board_disables_the_actions(qapp, sys_root, proc_root):
    (sys_root / "class/dmi/id/board_name").write_text("Other Board\n")
    w = make(qapp, sys_root, proc_root, Board())
    assert not w.apply_button.isEnabled() and not w.read_button.isEnabled()
    assert "not a BC-250" in w.block_reason.text()
    w.close()


def test_ttm_apply_reboot_and_default(qapp, sys_root, proc_root, answer):
    ostree = FakeOstree()
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(4194304))
    w.apply_ttm()
    assert ("The GTT stays at 9.4 GiB, all the RAM with this split. A limit above the RAM changes nothing until a "
            "smaller split.") in answer["questions"][0]
    assert ostree.calls[1] == ["rpm-ostree", "kargs", "--replace=ttm.pages_limit=4194304", "--unchanged-exit-77"]
    assert "ttm.pages_limit=4194304" in ostree.arguments and "3014656" not in ostree.arguments
    assert w.badge.text() == "Reboot to apply" and "16.0 GiB GTT limit is in the next boot" in w.ttm_note.text()
    assert "Restart the board to use it" in w.ttm_note.text()
    assert not w.ttm_button.isEnabled()                   # 16 GiB is written: not again
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(3014656))
    assert w.ttm_button.isEnabled()
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(4194304))
    assert w.ttm_box.value.text() == "11.5 GiB" and w.ttm_box.caption.text() == "next boot 16.0 GiB"
    assert answer["infos"] == ["Done. The 16.0 GiB GTT limit is in the next boot's kernel arguments.\n\nRestart the "
                               "board to use it. The app does not restart the board by itself. Use the menu, or run "
                               "systemctl reboot in a terminal."]
    assert w.combo.currentData() == 6144 and not w.apply_button.isEnabled()  # the split is untouched
    w.close()

    # Same boot: still waiting, whatever the settings say.
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    assert w.badge.text() == "Reboot to apply" and w.ttm_combo.currentData() == 4194304
    w.close()

    # After the reboot into the new arguments.
    (proc_root / "sys/kernel/random/boot_id").write_text("boot-2\n")
    (proc_root / "cmdline").write_text("BOOT_IMAGE=x rw ttm.pages_limit=4194304\n")
    (sys_root / "module/ttm/parameters/pages_limit").write_text("4194304\n")
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    assert w.badge.text() == "6.0 GiB split"
    assert w.ttm_note.text() == ("The 16.0 GiB GTT limit from the last change is active. The GPU may borrow up to "
                                 "9.4 GiB of the RAM, all of it.")
    assert w.ttm_box.value.text() == "16.0 GiB" and w.ttm_box.caption.text() == "GTT limit"

    # Back to the kernel's default: the argument is removed.
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(None))
    assert w.ttm_combo.currentData() is None
    w.apply_ttm()
    assert "The GTT then is about 4.7 GiB instead of 9.4 GiB now." in answer["questions"][-1]
    assert ostree.calls[-3] == ["rpm-ostree", "kargs", "--delete=ttm.pages_limit=4194304", "--unchanged-exit-77"]
    assert "ttm.pages_limit" not in ostree.arguments
    assert "kernel default GTT limit (half the RAM) is in the next boot" in w.ttm_note.text()
    assert w.ttm_box.caption.text() == "next boot: default"
    assert w.map.previewing and w.map.preview is None and w.map.preview_ttm is None
    w.close()


def test_ttm_reboot_without_the_limit(qapp, sys_root, proc_root, answer):
    ostree = FakeOstree()
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(None))
    w.apply_ttm()
    w.close()
    (proc_root / "sys/kernel/random/boot_id").write_text("boot-2\n")
    ostree.arguments = "BOOT_IMAGE=x rw ttm.pages_limit=3014656"         # the board started the old deployment
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    assert "but this boot has the 11.5 GiB GTT limit" in w.ttm_note.text()
    assert not w.badge.text() == "Reboot to apply"
    w.close()


def test_ttm_cancel_and_failure(qapp, sys_root, proc_root, answer):
    ostree = FakeOstree()
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    answer["value"] = QMessageBox.StandardButton.No
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(None))
    w.apply_ttm()
    assert len(ostree.calls) == 1 and "3014656" in ostree.arguments
    answer["value"] = QMessageBox.StandardButton.Yes
    ostree.error = "error: Transaction in progress: upgrade"
    w.apply_ttm()
    assert answer["warnings"] == ["rpm-ostree kargs failed: error: Transaction in progress: upgrade"]
    assert "3014656" in ostree.arguments and w.ttm_button.isEnabled()
    w.close()


def test_ttm_without_rpm_ostree(qapp, sys_root, proc_root):
    ostree = FakeOstree()
    ostree.error, ostree.code = "rpm-ostree is not installed.", privileged.NOT_INSTALLED
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    assert not w.ttm_button.isEnabled() and "no rpm-ostree" in w.ttm_reason.text()
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(None))
    assert not w.ttm_button.isEnabled()
    w.combo.setCurrentIndex(main_window.SPLITS.index(4096))
    assert w.apply_button.isEnabled()                                     # the split does not depend on it
    w.close()


def test_ttm_set_outside_the_app(qapp, sys_root, proc_root):
    ostree = FakeOstree("rw ttm.pages_limit=2000000")
    (proc_root / "cmdline").write_text("rw ttm.pages_limit=2000000\n")
    (sys_root / "module/ttm/parameters/pages_limit").write_text("2000000\n")
    w = make(qapp, sys_root, proc_root, Board(), ostree)
    assert w.ttm_combo.currentText() == "7.6 GiB, as set now" and w.ttm_combo.currentData() == 2000000
    assert w.ttm_combo.count() == len(main_window.kargs.PRESETS) + 1 and not w.map.previewing
    w.close()


def test_ttm_says_writing_while_rpm_ostree_runs(qapp, sys_root, proc_root, answer):
    """rpm-ostree takes a minute or two after the password dialog: the window must show it is busy meanwhile."""
    seen = []
    ostree = FakeOstree()
    inner = ostree.__call__

    def slow(cmd):
        if cmd[2].startswith("--replace"):
            w.writing_since -= 83                                       # as if 83 s had passed
            w.tick_writing()                                            # what the timer does every second
            seen.append((w.badge.text(), w.ttm_note.text(), w.ttm_button.isEnabled(), w.apply_button.isEnabled(),
                         w.writing_timer.isActive()))
        return inner(cmd)

    w = make(qapp, sys_root, proc_root, Board(), slow)
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(4194304))
    w.apply_ttm()
    assert seen == [("Writing…", "<b>rpm-ostree is writing the next boot's kernel arguments, 83 s so far. This takes "
                     "a minute or two. The window answers again when rpm-ostree is done.</b>", False, False, True)]
    assert not w.writing_timer.isActive()
    assert w.badge.text() == "Reboot to apply" and not w.ttm_button.isEnabled() and not w.apply_button.isEnabled()
    w.ttm_combo.setCurrentIndex(w.ttm_combo.findData(None))
    assert w.ttm_button.isEnabled()
    w.close()


def test_profiles_write_what_differs(qapp, sys_root, proc_root, answer):
    """The board runs the Games profile (6 GB, 11.5 GiB): Games is off, Defaults writes both; then Games again."""
    board, ostree = Board(), FakeOstree()
    w = make(qapp, sys_root, proc_root, board, ostree)
    assert not w.profile_buttons["games"].isEnabled() and w.profile_buttons["defaults"].isEnabled()
    assert w.profile_buttons["games"].toolTip() == "6 GB  (recommended for games) split, 11.5 GiB GTT limit"
    w.apply_profile("defaults")
    assert answer["questions"][-1].startswith("Write the 512 MB split to CMOS and the kernel default GTT limit "
                                              "(half the RAM) to the next boot's kernel arguments?\n\nBoth take "
                                              "effect after you restart the board.")
    assert answer["questions"][-1].endswith("You will be asked for your password once for each.")
    assert board.calls == [["--set-uma", "512"]] and board.uma == 512
    assert ostree.calls[-3][2] == "--delete=ttm.pages_limit=3014656" and "ttm" not in ostree.arguments
    assert answer["infos"] == ["Done. The app wrote the 512 MB split to CMOS and the kernel default GTT limit (half "
                               "the RAM) to the next boot's kernel arguments.\n\nRestart the board to use it. The app "
                               "does not restart the board by itself. Use the menu, or run systemctl reboot in a "
                               "terminal."]
    assert w.badge.text() == "Reboot to apply" and w.combo.currentData() == 512
    assert w.ttm_combo.currentData() is None
    assert not w.profile_buttons["defaults"].isEnabled() and w.profile_buttons["games"].isEnabled()
    w.apply_profile("games")
    assert board.uma == 6144 and "ttm.pages_limit=3014656" in ostree.arguments
    assert not w.profile_buttons["games"].isEnabled() and w.profile_buttons["defaults"].isEnabled()
    w.close()


def test_profile_asks_once_and_stops_on_no(qapp, sys_root, proc_root, answer):
    board, ostree = Board(), FakeOstree()
    w = make(qapp, sys_root, proc_root, board, ostree)
    answer["value"] = QMessageBox.StandardButton.No
    w.apply_profile("defaults")
    assert len(answer["questions"]) == 1 and board.calls == [] and len(ostree.calls) == 1
    # Without rpm-ostree the profile still writes the split, and says only that.
    missing = FakeOstree()
    missing.error, missing.code = "rpm-ostree is not installed.", privileged.NOT_INSTALLED
    w = make(qapp, sys_root, proc_root, board, missing)
    answer["value"] = QMessageBox.StandardButton.Yes
    assert w.profile_steps("defaults") == ["the 512 MB split to CMOS"]
    w.apply_profile("defaults")
    assert board.uma == 512 and "You will be asked for your password." in answer["questions"][-1]
    w.close()


def test_swap_layout_is_written_once_and_waits_for_a_restart(qapp, sys_root, proc_root, answer):
    swapper = Swapper(sys_root.parent)
    w = make(qapp, sys_root, proc_root, Board(), swapper=swapper)
    assert w.layout_combo.currentData() == swap.BAZZITE and not w.swap_button.isEnabled()   # what the board has
    assert w.swap_options.isHidden() and w.delete_button.isHidden() and w.swap_note.isHidden()
    w.layout_combo.setCurrentIndex(w.layout_combo.findData(swap.ZRAM))
    assert not w.swap_options.isHidden() and w.size_label.text() == "zram size:"
    assert w.size_combo.currentText() == "Half the RAM (4.7 GiB)" and w.swappiness_spin.value() == 180
    assert [w.compressor_combo.itemText(i) for i in range(w.compressor_combo.count())] == [
        "lzo-rle", "lzo", "lz4", "lz4hc", "zstd", "deflate", "842"]           # what the board's zram offers
    assert w.compressor_combo.currentText() == "zstd" and w.swap_button.isEnabled()
    answer["value"] = QMessageBox.StandardButton.No
    w.swap_button.click()
    assert swapper.calls == [] and answer["questions"][-1].splitlines() == [
        'Write the swap layout "zram with your size and compressor" for the next boot?', "",
        "zram gets the size half the RAM (4.7 GiB), with zstd.", "vm.swappiness becomes 180.",
        "It takes effect after you restart the board.", "", "You will be asked for your password."]
    answer["value"] = QMessageBox.StandardButton.Yes
    w.swap_button.click()
    assert swapper.calls == [["--layout", "zram", "--zram-size", "ram / 2", "--compressor", "zstd",
                              "--swappiness", "180"]]
    assert not w.swap_button.isEnabled() and w.layout_combo.currentData() == swap.ZRAM      # not once more
    assert "Restart the board" in w.swap_note.text() and w.badge.text() == "Reboot to apply"
    w.swappiness_spin.setValue(100)
    assert w.swap_button.isEnabled()                                          # a new value can be applied
    w.close()
    # After the restart: zram is what runs, so the layout is active.
    (proc_root / "sys/kernel/random/boot_id").write_text("boot-2\n")
    w = make(qapp, sys_root, proc_root, Board(), swapper=swapper)
    assert w.swap_note.text() == "The swap layout from the last change is active." and w.badge.text() == "6.0 GiB split"
    w.close()


def test_zswap_layout_makes_the_file_and_offers_its_deletion_afterward(qapp, sys_root, proc_root, answer):
    swapper = Swapper(sys_root.parent)
    w = make(qapp, sys_root, proc_root, Board(), swapper=swapper)
    w.layout_combo.setCurrentIndex(w.layout_combo.findData(swap.ZSWAP_FILE))
    assert w.size_label.text() == "Swap file:" and w.size_combo.currentData() == 8192
    assert [w.size_combo.itemText(i) for i in range(w.size_combo.count())] == [
        "4 GiB", "8 GiB", "16 GiB", "As large as the RAM (9.4 GiB)"]
    assert w.swappiness_spin.value() == 60 and w.compressor_combo.currentText() == "zstd"
    w.size_combo.setCurrentIndex(0)
    w.swap_button.click()
    assert "It makes the swap file" in answer["questions"][-1] and "zram is turned off." in answer["questions"][-1]
    assert swap.file_mib(swapper.var) == 4096 and w.layout_combo.currentData() == swap.ZSWAP_FILE
    assert w.size_combo.currentData() == 4096 and not w.swap_button.isEnabled() and w.delete_button.isHidden()
    w.close()
    # The next boot got another swap than asked for: said, not hidden.
    (proc_root / "sys/kernel/random/boot_id").write_text("boot-2\n")
    w = make(qapp, sys_root, proc_root, Board(), swapper=swapper)
    assert "but this boot's swap is zram" in w.swap_note.text()
    # The file in use: its size cannot change, and after another layout it cannot be deleted yet.
    (proc_root / "swaps").write_text(f"Filename Type Size Used Priority\n{swapper.var / swap.SWAP_FILE} file 1 0 -2\n")
    w.size_combo.setCurrentIndex(1)
    assert not w.swap_button.isEnabled() and "in use" in w.swap_reason.text()
    w.layout_combo.setCurrentIndex(w.layout_combo.findData(swap.BAZZITE))
    w.swap_button.click()
    assert "removes the app's own swap files" in answer["questions"][-1]
    assert not w.delete_button.isHidden() and not w.delete_button.isEnabled()
    (proc_root / "swaps").write_text("Filename Type Size Used Priority\n")
    w.refresh()
    assert w.delete_button.isEnabled() and "4.0 GiB" in w.delete_button.toolTip()
    w.delete_button.click()
    assert "Delete the swap file" in answer["questions"][-1] and swapper.calls[-1] == ["--delete-file"]
    assert swap.file_mib(swapper.var) == 0 and w.delete_button.isHidden()
    w.close()


def test_a_swap_layout_that_fails_says_why_and_stays_to_apply(qapp, sys_root, proc_root, answer):
    swapper = Swapper(sys_root.parent)
    swapper.__class__ = type("Refused", (Swapper,), {
        "__call__": lambda self, args: privileged.Result(False, {}, "Not authorized")})
    w = make(qapp, sys_root, proc_root, Board(), swapper=swapper)
    w.layout_combo.setCurrentIndex(w.layout_combo.findData(swap.ZRAM))
    w.swap_button.click()
    assert answer["warnings"] == ["Not authorized"] and w.swap_button.isEnabled() and w.swap_note.isHidden()
    assert w.layout_combo.currentData() == swap.ZRAM
    w.close()


def test_the_guard_takes_effect_at_once(qapp, sys_root, proc_root, answer):
    """The suite's guard (owner, 26-11-2026): the four files and the user manager reloaded; Bazzite's own takes them
    away again. Recording goes on and off on its own. Apply is off for the guard that is written."""
    swapper = Swapper(sys_root.parent)
    guarder = Guarder(swapper.etc)
    w = make(qapp, sys_root, proc_root, Board(), swapper=swapper, guarder=guarder)
    assert w.guard_combo.currentData() == guard.BAZZITE and not w.guard_button.isEnabled()
    w.guard_combo.setCurrentIndex(w.guard_combo.findData(guard.SUITE))
    assert w.guard_button.isEnabled()
    w.apply_guard()
    assert answer["questions"][-1] == (
        "Write the memory guard \"The suite's guard: memory pressure 60% for 10 s, or swap 90% full\"?\n\n"
        "systemd-oomd ends the program that uses the most memory when memory pressure stays above 60% for 10 s.\n"
        "It does the same when the swap is 90% full.\n"
        "It takes effect at once, without a restart.\n\nYou will be asked for your password.")
    assert guarder.calls == [["--guard", "suite"]] and guard.read_guard(swapper.etc) == guard.SUITE
    assert guarder.systemctl == [["systemctl", "--user", "daemon-reload"]]
    assert not w.guard_button.isEnabled() and not w.recording()
    w.guard_combo.setCurrentIndex(w.guard_combo.findData(guard.BAZZITE))
    w.apply_guard()
    assert guard.read_guard(swapper.etc) == guard.BAZZITE
    w.close()


def test_recording_on_and_off(qapp, sys_root, proc_root):
    guarder = Guarder(Swapper(sys_root.parent).etc)
    w = make(qapp, sys_root, proc_root, Board(), guarder=guarder)
    assert w.record_box.value.text() == "Off" and w.record_pill.text() == "Turn on"
    w.record_pill.click()
    unit = service.unit_path(sys_root.parent / "config")
    assert "ExecStart=/venv/bin/python -m vram_manager.watch" in unit.read_text()
    assert f"WorkingDirectory={sys_root.parent / 'app'}" in unit.read_text()
    assert ["systemctl", "--user", "restart", service.UNIT] in guarder.systemctl
    assert w.record_box.value.text() == "On" and w.record_pill.text() == "Turn off"
    w.record_pill.click()
    assert not unit.exists() and ["systemctl", "--user", "disable", "--now", service.UNIT] in guarder.systemctl
    w.close()


def test_the_smooth_profile_writes_all_four(qapp, sys_root, proc_root, answer):
    """The board runs the Games profile with Bazzite's swap and guard: the Smooth profile keeps the split and writes
    the GTT limit of the RAM less 2 GiB, zram the size of the RAM and the suite's guard, after one question."""
    board, ostree = Board(), FakeOstree()
    swapper = Swapper(sys_root.parent)
    w = make(qapp, sys_root, proc_root, board, ostree, swapper)
    pages = watch.gtt_pages(9650)
    assert w.profile_steps(main_window.SMOOTH) == [
        f"the {main_window.ttm_label(pages)} to the next boot's kernel arguments",
        "zram the size of the RAM with vm.swappiness 180 for the next boot", "the suite's memory guard"]
    w.apply_profile(main_window.SMOOTH)
    assert answer["questions"][-1] == (
        "Write the 7.4 GiB GTT limit to the next boot's kernel arguments, zram the size of the RAM with "
        "vm.swappiness 180 for the next boot and the suite's memory guard?\n\nBoth take effect after you restart "
        "the board.\nThe app leaves the restart to you.\nThe guard takes effect at once.\n\nYou will be asked "
        "for your password once for each.")
    assert board.calls == [] and f"ttm.pages_limit={pages}" in ostree.arguments
    assert swap.read_setup(swapper.etc, swapper.var) == main_window.SMOOTH_SWAP
    assert guard.read_guard(swapper.etc) == guard.SUITE
    assert answer["infos"][-1].startswith("Done. The app wrote the 7.4 GiB GTT limit")
    assert w.profile_steps(main_window.SMOOTH) == [] and not w.profile_buttons[main_window.SMOOTH].isEnabled()
    assert w.profile_buttons["games"].isEnabled()         # Games has the 11.5 GiB limit
    w.close()


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, boot):
    (proc_root / "sys/kernel/random/boot_id").write_text(boot + "\n")
    w = make(qapp, sys_root, proc_root, Board(), ostree, swapper)
    w.close()
    guarder = Guarder(swapper.etc)
    return MainWindow(sys_root, proc_root, runner=Board(), commands=ostree, swapper=swapper, etc_root=swapper.etc,
                      var_root=swapper.var, guarder=guarder, config_dir=sys_root.parent / "config",
                      sessions_file=sys_root.parent / "sessions.jsonl", python="/venv/bin/python",
                      app_root=sys_root.parent / "app", user_commands=guarder.user,
                      learn_file=sys_root.parent / "learn.json", restarter=lambda: restarts.append(1) or True,
                      clock=clock)


def play(sys_root, boot, start, *games):
    for n, (program, ended) in enumerate(games):
        watch.write_session(watch.Session(f"app-steam-app{n + 1}-1.scope", program, start + n, boot, 3000, 8000, 2000,
                                          4800 if ended == watch.KILLED_SWAP else 1000, 4823, 9650,
                                          38.0 if ended == watch.KILLED_SWAP else 5.0, 0, start + n + 60, ended,
                                          vram_mib=5000, cpu=60.0), sys_root.parent / "sessions.jsonl")


def states(w):
    return [row.state for row in w.step_rows]


def test_the_learning_steps_from_the_start_point_to_the_learned_profile(qapp, sys_root, proc_root, answer):
    """The board has a 16 GiB GTT limit for the next boot: the start point writes the Games profile's 11.5 GiB and
    recording on, then the restart; round 1 with a full swap points to zram the RAM, written with a restart; round 2
    is better and kept, and nothing more points anywhere."""
    ostree = FakeOstree("BOOT_IMAGE=x rw ttm.pages_limit=4194304")
    swapper, clock, restarts = Swapper(sys_root.parent), Clock(), []
    w = learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, "boot-1")
    assert states(w) == ["now", "later", "later", "later", "later"]
    assert (w.step_pill.text(), w.step_pill.caption.text()) == ("Write", "Games profile")
    assert w.start_over_pill.isHidden() and w.alt_pill.isHidden() and w.record_box.value.text() == "Off"
    w.step_pill.click()
    assert answer["questions"][-1].startswith("Write the start point?\n\nIt writes the 11.5 GiB GTT limit to the "
                                              "next boot's kernel arguments and recording on.")
    assert "ttm.pages_limit=3014656" in ostree.arguments and w.recording()
    assert states(w)[:2] == ["done", "now"] and w.step_pill.text() == "Restart" and resume.armed()
    w.step_pill.click()                                     # the countdown
    assert w.countdown == main_window.RESTART_SECS and w.step_pill.text() == "Restart now"
    assert w.alt_pill.text() == "Cancel"
    w.alt_pill.click()
    assert w.countdown == 0 and w.step_pill.text() == "Restart" and restarts == []
    w.step_pill.click()
    w.step_pill.click()                                     # Restart now
    assert restarts == [1]
    w.close()

    # After the restart: round 1. The window opened by the autostart entry removes it.
    clock.now = 2000.0
    ostree.arguments = "BOOT_IMAGE=x rw ttm.pages_limit=3014656"
    (proc_root / "cmdline").write_text("BOOT_IMAGE=x rw ttm.pages_limit=3014656\n")
    w = learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, "boot-2")
    assert not resume.armed() and states(w)[:3] == ["done", "done", "running"]
    assert "0 of 3 game sessions recorded" in w.step_rows[2].line.text()
    play(sys_root, "boot-2", 2100, ("LUMINES", watch.KILLED_SWAP), ("Hades", watch.CLOSED), ("Tetris", watch.CLOSED))
    w.refresh_sessions(force=True)
    assert states(w) == ["done", "done", "done", "now", "later"]
    assert w.step_rows[3].line.text() == "The swap ran full in LUMINES. Try zram the RAM."
    assert (w.step_pill.text(), w.step_pill.caption.text()) == ("Write", "and restart")
    clock.now = 2500.0
    w.step_pill.click()
    assert answer["questions"][-1].startswith("Try zram the RAM?\n\nThe swap ran full in LUMINES.\nThe board "
                                              "restarts 15 s after the write.")
    assert swap.read_setup(swapper.etc, swapper.var) == swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=10)
    assert w.countdown and w.round_box.value.text() == "2" and resume.armed()
    w.restart_now()
    w.close()

    # Round 2: the same games, none short of memory. Better: Keep on the step, Undo beside it.
    clock.now = 3000.0
    w = learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, "boot-3")
    play(sys_root, "boot-3", 3100, ("LUMINES", watch.CLOSED), ("Hades", watch.CLOSED))
    w.refresh_sessions(force=True)
    assert states(w)[4] == "now"                                # LUMINES, which ran out of memory, played again
    assert w.step_rows[4].line.text() == "Better. Keep the change, or undo it. Not played yet in this round: Tetris."
    play(sys_root, "boot-3", 3200, ("Tetris", watch.CLOSED))
    w.refresh_sessions(force=True)
    assert states(w)[4] == "now" and w.step_rows[4].line.text() == "Better. Keep the change, or undo it."
    assert (w.step_pill.text(), w.alt_pill.text()) == ("Keep", "Undo")
    w.step_pill.click()
    assert w.finished_bar.text() == "Done. Your board already runs these settings. They stay after a restart." and not w.finished_bar.isHidden()
    assert states(w) == ["done"] * 5 and w.round_box.caption.text() == "Rounds"
    assert learn.read_state(sys_root.parent / "learn.json").rounds[1].verdict == learn.KEPT
    w.close()


def test_a_change_that_is_no_better_is_undone(qapp, sys_root, proc_root, answer):
    ostree = FakeOstree()
    swapper, clock, restarts = Swapper(sys_root.parent), Clock(), []
    w = learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, "boot-1")
    assert w.step_pill.text() == "Write"                    # recording is off
    w.step_pill.click()
    assert states(w)[:3] == ["done", "done", "running"] and not resume.armed()   # nothing waited for a restart
    assert w.step_rows[1].line.text() == "Nothing waited for a restart."
    play(sys_root, "boot-1", 1100, ("LUMINES", watch.KILLED_SWAP), ("Hades", watch.CLOSED), ("Tetris", watch.CLOSED))
    w.refresh_sessions(force=True)
    clock.now = 1500.0
    w.step_pill.click()
    w.restart_now()
    w.close()
    clock.now = 3000.0
    w = learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, "boot-2")
    play(sys_root, "boot-2", 3100, ("LUMINES", watch.KILLED_SWAP), ("Hades", watch.CLOSED), ("Tetris", watch.CLOSED))
    w.refresh_sessions(force=True)
    assert w.step_rows[4].line.text() == "No better. Undo the change, or keep it."
    assert (w.step_pill.text(), w.alt_pill.text()) == ("Undo", "Keep")
    w.step_pill.click()
    assert answer["questions"][-1].startswith("Undo zram the RAM?")
    assert swap.read_setup(swapper.etc, swapper.var) == swap.Setup()
    assert states(w)[4] == "now" and w.countdown == main_window.RESTART_SECS
    w.cancel_restart()
    assert w.step_pill.text() == "Restart" and "Restart the board" in w.step_rows[4].line.text()
    w.close()

    # After the restart: zram was tried, so round 1's kernel kill points to the suite's guard, which takes effect at
    # once. Start over deletes the rounds.
    w = learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, "boot-3")
    assert w.finished_bar.isHidden() and states(w)[3:] == ["now", "done"]
    assert w.step_rows[3].line.text() == "The kernel ended LUMINES. Try the suite's memory guard."
    assert w.step_rows[4].line.text() == "The change was undone."
    assert (w.step_pill.text(), w.step_pill.caption.text()) == ("Write", "Takes effect at once")
    w.start_over_pill.click()
    assert learn.read_state(sys_root.parent / "learn.json") is None and states(w)[0] == "now"
    w.close()


def test_a_round_that_asks_for_nothing_ends_on_the_start_point(qapp, sys_root, proc_root, answer):
    """Three games that end as usual: the window is done, with nothing to save, and says the start point stays."""
    ostree = FakeOstree()
    swapper, clock, restarts = Swapper(sys_root.parent), Clock(), []
    w = learner(qapp, sys_root, proc_root, ostree, swapper, clock, restarts, "boot-1")
    w.step_pill.click()
    play(sys_root, "boot-1", 1100, ("LUMINES", watch.CLOSED), ("Hades", watch.CLOSED), ("Tetris", watch.CLOSED))
    w.refresh_sessions(force=True)
    assert states(w) == ["done"] * 5
    assert w.finished_bar.text() == "Done. Your board already runs these settings. They stay after a restart."
    assert w.next_label.text() == "Nothing to save. Keep playing."
    texts = [w.content.itemAt(i).widget().text() for i in range(w.content.count())
             if isinstance(w.content.itemAt(i).widget(), main_window.QLabel)]
    assert "<b>The settings your board runs now</b>" in texts
    assert "No change stayed, so these are the start point's settings." in texts
    w.close()


def test_the_log_tab_lists_the_sessions_with_the_crash_report(qapp, sys_root, proc_root):
    """The owner's board, 27-11-2026: Steam, started from the suite, crashed in the suite's unit. The Log tab shows
    each session, newest first; a crash recorded without its report gets it from the journal."""
    sessions = sys_root.parent / "sessions.jsonl"
    suite = "app-bc250\\x2dbazzite\\x2dsuite@eefe.service"
    for session in (watch.Session("app-code-1.scope", "Visual Studio Code", 1000.0, "b", ram_mib=6716, swap_mib=1482,
                                  pressure=4.79, end=1100.0, ended=watch.CLOSED),
                    watch.Session(suite, "BC250 Bazzite Suite", 1200.0, "b", ram_mib=4247, swap_mib=944, end=1300.0,
                                  ended=watch.CRASHED),
                    watch.Session("app-steam@1.service", "Steam", 1400.0, "b", end=1500.0, ended=watch.CRASHED,
                                  crash="steam, SIGSEGV")):
        watch.write_session(session, sessions)
    asked = []

    def journal(args):
        asked.append(args)
        if "--output-fields=COREDUMP_SIGNAL_NAME" in args:
            return "SIGSEGV\n"
        return "Process 194263 (steam) of user 1000 dumped core.\n" if f"COREDUMP_USER_UNIT={suite}" in args else ""

    w = MainWindow(sys_root, proc_root, runner=Board(), commands=FakeOstree(), swapper=Swapper(sys_root.parent),
                   config_dir=sys_root.parent / "config", sessions_file=sessions, python="/venv/bin/python",
                   app_root=sys_root.parent / "app", journal=journal)
    assert w.tabs.tabText(2) == "Log"
    table = w.log_table
    rows = [[table.item(r, c).text() for c in range(table.columnCount())] for r in range(table.rowCount())]
    assert [r[1] for r in rows] == ["Steam", "BC250 Bazzite Suite", "Visual Studio Code"]
    assert rows[0][4] == "steam, SIGSEGV"
    assert rows[1][2:] == ["Crashed", "RAM 4.1 GiB · swap 944 MiB · waited 0%",
                           "steam, SIGSEGV. BC250 Bazzite Suite started it."]
    assert rows[2][4] == ""
    calls = len(asked)
    w.log_only_wrong.setChecked(True)
    assert table.rowCount() == 2 and len(asked) == calls        # the journal is read once a session
    assert w.log_hint.text().startswith("Each program the recording kept")
    w.close()


def test_the_log_tab_says_when_nothing_is_recorded(qapp, sys_root, proc_root):
    w = make(qapp, sys_root, proc_root, Board())
    assert w.log_table.rowCount() == 0
    assert w.log_hint.text() == "Nothing recorded yet. Recording keeps the programs while it is on."
    w.close()
