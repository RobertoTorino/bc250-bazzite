# SPDX-License-Identifier: GPL-3.0-or-later
import json

import pytest

from vram_manager import privileged, swap

MIB = 1024 * 1024


class Commands:
    """The commands the helper runs: recorded, with mkswapfile and fallocate making a file of the size asked.
    selinux: whether selinuxenabled answers yes; fail: the commands that answer 1."""

    def __init__(self, selinux=False, fail=()):
        self.calls, self.selinux, self.fail = [], selinux, fail

    def __call__(self, cmd):
        self.calls.append(cmd)
        if cmd[0] in self.fail or cmd[:2] in [list(f) for f in self.fail if isinstance(f, tuple)]:
            return 1
        if cmd[:3] == ["btrfs", "filesystem", "mkswapfile"] or cmd[0] == "fallocate":
            size = cmd[4] if cmd[0] == "btrfs" else cmd[2]
            with open(cmd[-1], "wb") as file:
                file.truncate(int(size[:-1]) * MIB)
        if cmd[:3] == ["btrfs", "subvolume", "create"]:
            (type(self).path(cmd[-1])).mkdir(parents=True)
        if cmd[0] == "selinuxenabled":
            return 0 if self.selinux else 1
        return 0

    @staticmethod
    def path(text):
        from pathlib import Path
        return Path(text)

    def names(self):
        return [" ".join(c[:3]) if c[0] in ("btrfs", "semanage", "systemctl") else c[0] for c in self.calls]


@pytest.fixture
def roots(tmp_path):
    etc, var, proc = tmp_path / "etc", tmp_path / "var", tmp_path / "proc"
    var.mkdir()
    proc.mkdir()
    (proc / "swaps").write_text("Filename\tType\tSize\tUsed\tPriority\n/dev/zram0 partition 4940796 0 100\n")
    return etc, var, proc


def test_bazzite_is_no_files_and_reads_back(roots):
    etc, var, proc = roots
    assert swap.read_setup(etc, var) == swap.Setup()
    run = Commands()
    zram = swap.Setup(swap.ZRAM, "ram * 1.5", "lz4", swappiness=150)
    swap.apply(zram, etc, var, proc, run)
    assert (etc / swap.ZRAM_DROPIN).read_text().splitlines()[1:] == [
        "[zram0]", "zram-size = ram * 1.5", "compression-algorithm = lz4"]
    assert "vm.swappiness = 150" in (etc / swap.SYSCTL).read_text()
    assert swap.read_setup(etc, var) == zram and run.calls == []          # files only: nothing is started
    answer = swap.apply(swap.Setup(), etc, var, proc, run)
    assert answer["before"]["layout"] == swap.ZRAM and answer["after"]["layout"] == swap.BAZZITE
    assert not (etc / swap.ZRAM_DROPIN).exists() and not (etc / swap.ZRAM_DROPIN).parent.exists()
    assert not (etc / swap.SYSCTL).exists() and (etc / "sysctl.d").is_dir()  # only our own folder goes
    assert swap.read_setup(etc, var) == swap.Setup()


@pytest.mark.parametrize("btrfs", [True, False])
def test_zswap_makes_the_file_first_and_turns_zram_off(roots, btrfs):
    etc, var, proc = roots
    run = Commands(selinux=True)
    setup = swap.Setup(swap.ZSWAP_FILE, compressor="zstd", file_mib=4096, swappiness=60)
    swap.apply(setup, etc, var, proc, run, btrfs=lambda _p: btrfs)
    made = ["btrfs subvolume create", "btrfs filesystem mkswapfile"] if btrfs else ["fallocate", "mkswap"]
    assert run.names() == [*made, "selinuxenabled", "semanage fcontext -a", "chcon", "systemctl daemon-reload",
                           f"systemctl enable {swap.UNIT}"]
    assert (var / swap.SWAP_FILE).stat().st_size == 4096 * MIB
    assert "zram-size = 0" in (etc / swap.ZRAM_DROPIN).read_text()
    assert f"What={var / swap.SWAP_FILE}" in (etc / "systemd/system" / swap.UNIT).read_text()
    lines = (etc / swap.TMPFILES).read_text().splitlines()[1:]
    assert lines == ["w /sys/module/zswap/parameters/compressor - - - - zstd",
                     "w /sys/module/zswap/parameters/enabled - - - - Y"]
    assert swap.read_setup(etc, var) == setup
    run.calls.clear()
    swap.apply(setup, etc, var, proc, run, btrfs=lambda _p: btrfs)        # the file of that size stays
    assert run.names() == ["systemctl daemon-reload", f"systemctl enable {swap.UNIT}"]
    # Another layout: the unit and zswap's file go, the swap file stays until it is deleted.
    run.calls.clear()
    swap.apply(swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=180), etc, var, proc, run)
    assert run.names() == [f"systemctl disable {swap.UNIT}", "systemctl daemon-reload"]
    assert not (etc / swap.TMPFILES).exists() and not (etc / "systemd/system" / swap.UNIT).exists()
    assert swap.file_mib(var) == 4096 and "zram-size = ram\n" in (etc / swap.ZRAM_DROPIN).read_text()


def test_a_file_that_cannot_be_made_changes_nothing(roots):
    etc, var, proc = roots
    setup = swap.Setup(swap.ZSWAP_FILE, compressor="zstd", file_mib=4096, swappiness=60)
    with pytest.raises(swap.SwapError, match="could not be made"):
        swap.apply(setup, etc, var, proc, Commands(fail=(("btrfs", "filesystem"),)), btrfs=lambda _p: True)
    assert swap.read_setup(etc, var) == swap.Setup() and not etc.exists()
    huge = swap.Setup(swap.ZSWAP_FILE, compressor="zstd", file_mib=10 ** 12, swappiness=60)
    with pytest.raises(swap.SwapError, match="does not fit"):
        swap.apply(huge, etc, var, proc, Commands())
    assert "does not fit" in swap.file_problem(10 ** 12, var, proc) and swap.file_problem(4096, var, proc) == ""


def test_a_file_in_use_keeps_its_size_and_is_not_deleted(roots):
    etc, var, proc = roots
    run = Commands()
    swap.apply(swap.Setup(swap.ZSWAP_FILE, compressor="lz4", file_mib=2048, swappiness=60), etc, var, proc, run,
               btrfs=lambda _p: True)
    with pytest.raises(swap.SwapError, match="uses the swap file"):
        swap.delete_file(etc, var, proc, run)
    (proc / "swaps").write_text(f"Filename Type Size Used Priority\n{var / swap.SWAP_FILE} file 2097148 0 -2\n")
    assert swap.file_in_use(var, proc) and "in use" in swap.file_problem(4096, var, proc)
    assert swap.file_problem(2048, var, proc) == ""
    swap.apply(swap.Setup(), etc, var, proc, run)
    with pytest.raises(swap.SwapError, match="in use until the board restarts"):
        swap.delete_file(etc, var, proc, run)
    (proc / "swaps").write_text("Filename Type Size Used Priority\n")
    assert swap.delete_file(etc, var, proc, Commands(fail=("btrfs",))) == {"ok": True, "deleted_mib": 2048}
    assert not (var / "swap").exists()


def test_check_refuses_what_is_not_offered():
    for bad in (swap.Setup("tmpfs"), swap.Setup(swap.ZRAM, "ram * 9", "zstd", swappiness=60),
                swap.Setup(swap.ZRAM, "ram", "zstd; reboot", swappiness=60),
                swap.Setup(swap.ZRAM, "ram", "zstd", swappiness=201), swap.Setup(swap.ZRAM, "ram", "zstd"),
                swap.Setup(swap.ZSWAP_FILE, compressor="zstd", file_mib=100, swappiness=60)):
        with pytest.raises(swap.SwapError):
            swap.check(bad)


def test_the_helper_runs_isolated_as_root_only(capsys):
    cmd = privileged.command(["--layout", "bazzite"], privileged.SWAP_SCRIPT)
    assert cmd[0] == "pkexec" and cmd[2] == "-I" and cmd[3].endswith("vram_manager/swap.py")
    assert swap.main(["--layout", "bazzite"]) == 1                          # the tests are not root
    assert json.loads(capsys.readouterr().out) == {"ok": False, "error": "The swap layout is written as root."}
    setup = swap.Setup(swap.ZSWAP_FILE, compressor="zstd", file_mib=8192, swappiness=60)
    assert swap.arguments(setup) == ["--layout", "zswap", "--file-mib", "8192", "--compressor", "zstd",
                                     "--swappiness", "60"]
    assert swap.arguments(swap.Setup()) == ["--layout", "bazzite"]
