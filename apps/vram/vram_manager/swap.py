# SPDX-License-Identifier: GPL-3.0-or-later
"""The swap layout of the next boot, and the root helper that writes it.

Three layouts (owner, 21-11-2026), each a complete setup:

    bazzite   Bazzite's own: zram as the image sets it. None of the app's files.
    zram      zram with a size and a compressor of your own
    zswap     zswap in front of a swap file on disk, and zram off

A layout is a few files of the app's own, so the image's files stay as they are and removing ours brings Bazzite's
layout back:

    /etc/systemd/zram-generator.conf.d/90-bc250-memory-manager.conf   zram0's size and compressor; size 0: no zram
    /etc/sysctl.d/90-bc250-memory-manager.conf                        vm.swappiness
    /etc/tmpfiles.d/bc250-memory-manager-zswap.conf                   turns zswap on at boot, with its compressor
    /etc/systemd/system/var-swap-swapfile.swap                        the swap file's unit, enabled
    /var/swap/swapfile                                                the swap file, in a folder of its own

Nothing is started or stopped: zram-generator, sysctl, tmpfiles and the swap unit read the files at the next boot.
zswap is turned on through its module parameter, so the kernel arguments (Bazzite has zswap.enabled=0 there) need
no new deployment. On btrfs the folder is a subvolume and the file is made by `btrfs filesystem mkswapfile`, which
turns copy-on-write off for it; elsewhere by fallocate and mkswap. With SELinux the file gets the swapfile_t label:
systemd's swapon may not use a file without it.

Run as root (through pkexec) with the system Python, standard library only:

    python3 -I swap.py --layout bazzite
    python3 -I swap.py --layout zram --zram-size "ram / 2" --compressor zstd --swappiness 180
    python3 -I swap.py --layout zswap --file-mib 8192 --compressor zstd --swappiness 60
    python3 -I swap.py --delete-file        the swap file and its folder, while no layout uses them

Each prints one JSON object."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

MIB = 1024 * 1024
ZRAM_DROPIN = "systemd/zram-generator.conf.d/90-bc250-memory-manager.conf"     # these four under /etc
SYSCTL = "sysctl.d/90-bc250-memory-manager.conf"
TMPFILES = "tmpfiles.d/bc250-memory-manager-zswap.conf"
UNIT = "var-swap-swapfile.swap"                 # systemd names a swap unit after the file's path
SWAP_FILE = "swap/swapfile"                     # under /var
ZSWAP = "/sys/module/zswap/parameters"
HEADER = "# Written by BC-250 Memory Manager (swap layout). Pick Bazzite's own layout in the app to remove it.\n"

BAZZITE, ZRAM, ZSWAP_FILE = "bazzite", "zram", "zswap"
LAYOUTS = {
    BAZZITE: "Bazzite's own: zram as the image sets it",
    ZRAM: "zram with your size and compressor",
    ZSWAP_FILE: "zswap with a swap file on disk, zram off",
}
# zram-generator works the size out from the RAM at every boot, so it follows a new VRAM split by itself.
ZRAM_SIZES: tuple[tuple[str, str, float], ...] = (
    ("Half the RAM", "ram / 2", 0.5),
    ("The RAM", "ram", 1.0),
    ("One and a half times the RAM", "ram * 1.5", 1.5),
    ("Twice the RAM", "ram * 2", 2.0),
)
FILE_SIZES_GIB = (4, 8, 16)                     # the swap file; the window adds "as large as the RAM"
SWAPPINESS = {ZRAM: 180, ZSWAP_FILE: 60}        # proposed: zram's swap is RAM, a swap file's is the disk
ZRAM_COMPRESSORS = ("zstd", "lz4", "lzo-rle")   # offered when no zram device is there to name its own
ZSWAP_COMPRESSORS = ("zstd", "lz4", "lzo")
SPARE_MIB = 1024                                # the disk keeps this much free beside a new swap file

Run = Callable[[list[str]], int]


class SwapError(Exception):
    """A layout that cannot be written, with the reason for the user."""


@dataclass(frozen=True)
class Setup:
    layout: str = BAZZITE
    zram_size: str = ""                 # zram: zram-generator's expression, one of ZRAM_SIZES
    compressor: str = ""                # zram's, or zswap's
    file_mib: int = 0                   # zswap: the swap file's size
    swappiness: int | None = None       # None: Bazzite's value


def _keys(path: Path) -> dict[str, str]:
    """The key = value lines of one of the app's files; empty when it is not there."""
    out = {}
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return out
    for line in lines:
        key, sep, value = line.partition("=")
        if sep and not line.lstrip().startswith("#"):
            out[key.strip()] = value.strip()
    return out


def file_mib(var: Path = Path("/var")) -> int:
    """The swap file's size, 0 when there is none."""
    try:
        return (var / SWAP_FILE).stat().st_size // MIB
    except OSError:
        return 0


def read_setup(etc: Path = Path("/etc"), var: Path = Path("/var")) -> Setup:
    """The layout the app's files hold, which the next boot gets. Needs no root."""
    swappiness = _keys(etc / SYSCTL).get("vm.swappiness", "")
    value = int(swappiness) if swappiness.isdigit() else None
    zram = _keys(etc / ZRAM_DROPIN)
    try:
        zswap = (etc / TMPFILES).read_text()
    except OSError:
        zswap = None
    if zswap is not None or (etc / "systemd/system" / UNIT).is_file():
        compressor = ""
        for line in (zswap or "").splitlines():
            words = line.split()
            if len(words) == 7 and words[1] == f"{ZSWAP}/compressor":
                compressor = words[6]
        return Setup(ZSWAP_FILE, compressor=compressor, file_mib=file_mib(var), swappiness=value)
    if zram:
        return Setup(ZRAM, zram.get("zram-size", ""), zram.get("compression-algorithm", ""), swappiness=value)
    return Setup(swappiness=value)


def file_in_use(var: Path = Path("/var"), proc_root: Path = Path("/proc")) -> bool:
    """Whether the swap file is swap now (/proc/swaps)."""
    try:
        lines = (proc_root / "swaps").read_text().splitlines()[1:]
    except OSError:
        return False
    return any(line.split()[:1] == [str(var / SWAP_FILE)] for line in lines)


def free_mib(var: Path = Path("/var")) -> int | None:
    """The free space where the swap file goes; None when it cannot be read."""
    folder = var / SWAP_FILE
    while not folder.is_dir() and folder != folder.parent:
        folder = folder.parent
    try:
        stat = os.statvfs(folder)
    except OSError:
        return None
    return stat.f_bavail * stat.f_frsize // MIB


def file_problem(wanted_mib: int, var: Path = Path("/var"), proc_root: Path = Path("/proc")) -> str:
    """Why a swap file of this size cannot be made now; "" when it can, or when the file has that size already."""
    have = file_mib(var)
    if have == wanted_mib:
        return ""
    if have and file_in_use(var, proc_root):
        return ("The swap file is in use, so its size cannot change now. Apply another layout, restart the board, "
                "and then apply this one.")
    free = free_mib(var)
    if free is not None and free + have < wanted_mib + SPARE_MIB:
        return (f"A swap file of {wanted_mib} MiB does not fit. The disk has {free + have} MiB for it, and "
                f"{SPARE_MIB} MiB stays free.")
    return ""


def check(setup: Setup) -> None:
    if setup.layout not in LAYOUTS:
        raise SwapError(f"Unknown layout {setup.layout!r}.")
    if setup.layout == BAZZITE:
        return
    if not setup.compressor or not all(c.isalnum() or c == "-" for c in setup.compressor):
        raise SwapError(f"Not a compressor's name: {setup.compressor!r}.")
    if setup.swappiness is None or not 0 <= setup.swappiness <= 200:
        raise SwapError("vm.swappiness goes from 0 to 200.")
    if setup.layout == ZRAM and setup.zram_size not in [size for _label, size, _factor in ZRAM_SIZES]:
        raise SwapError(f"Not one of the zram sizes: {setup.zram_size!r}.")
    if setup.layout == ZSWAP_FILE and setup.file_mib < 1024:
        raise SwapError("The swap file is 1 GiB at least.")


# --- The helper ------------------------------------------------------------------------------------------------

def _run(cmd: list[str]) -> int:
    """Runs a command with its output on stderr, where it does not disturb the JSON answer; 127 when it is not
    installed."""
    try:
        return subprocess.run(cmd, stdout=sys.stderr, check=False).returncode
    except OSError:
        return 127


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.chmod(path, 0o644)


def _remove(path: Path) -> None:
    path.unlink(missing_ok=True)
    if path.parent.name.endswith(".conf.d"):            # our drop-in's folder, when nothing else is in it
        try:
            path.parent.rmdir()
        except OSError:
            pass


def _is_btrfs(folder: Path) -> bool:
    try:
        done = subprocess.run(["stat", "-f", "-c", "%T", str(folder)], capture_output=True, text=True, check=False)
    except OSError:
        return False
    return done.stdout.strip() == "btrfs"


def unit_text(path: Path) -> str:
    return (HEADER + "[Unit]\nDescription=BC-250 Memory Manager: the swap file behind zswap\n\n"
            f"[Swap]\nWhat={path}\n\n[Install]\nWantedBy=swap.target\n")


def tmpfiles_text(compressor: str) -> str:
    return (HEADER + f"w {ZSWAP}/compressor - - - - {compressor}\n"
            f"w {ZSWAP}/enabled - - - - Y\n")


def make_file(mib: int, var: Path, proc_root: Path, run: Run, btrfs: Callable[[Path], bool] = _is_btrfs) -> None:
    """The swap file of *mib* in its folder; one of that size stays as it is."""
    path = var / SWAP_FILE
    problem = file_problem(mib, var, proc_root)
    if problem:
        raise SwapError(problem)
    if file_mib(var) == mib:
        return
    on_btrfs = btrfs(var)
    if not path.parent.exists() and (not on_btrfs or run(["btrfs", "subvolume", "create", str(path.parent)]) != 0):
        path.parent.mkdir(parents=True)
    os.chmod(path.parent, 0o700)
    path.unlink(missing_ok=True)
    if on_btrfs:
        code = run(["btrfs", "filesystem", "mkswapfile", "--size", f"{mib}m", "--uuid", "clear", str(path)])
    else:
        code = run(["fallocate", "-l", f"{mib}M", str(path)])
        if code == 0:
            os.chmod(path, 0o600)
            code = run(["mkswap", str(path)])
    if code != 0 or file_mib(var) != mib:
        path.unlink(missing_ok=True)
        raise SwapError(f"The swap file {path} could not be made (exit code {code}). Nothing else was changed.")
    if run(["selinuxenabled"]) == 0:
        # The rule keeps the label through a relabel of the disk; chcon sets it where semanage is missing.
        run(["semanage", "fcontext", "-a", "-t", "swapfile_t", str(path)])
        run(["chcon", "-t", "swapfile_t", str(path)])


def apply(setup: Setup, etc: Path = Path("/etc"), var: Path = Path("/var"), proc_root: Path = Path("/proc"),
          run: Run = _run, btrfs: Callable[[Path], bool] = _is_btrfs) -> dict:
    """Writes the layout's files and removes the other layouts'. The swap file is made first: when that fails,
    nothing else has changed."""
    check(setup)
    before = read_setup(etc, var)
    unit = etc / "systemd/system" / UNIT
    if setup.layout == ZSWAP_FILE:
        make_file(setup.file_mib, var, proc_root, run, btrfs)
        _write(etc / ZRAM_DROPIN, HEADER + "[zram0]\nzram-size = 0\n")
        _write(etc / TMPFILES, tmpfiles_text(setup.compressor))
        _write(unit, unit_text(var / SWAP_FILE))
        run(["systemctl", "daemon-reload"])
        if run(["systemctl", "enable", UNIT]) != 0:
            raise SwapError(f"systemctl enable {UNIT} failed, so the swap file would not be used at boot.")
    else:
        if unit.is_file():
            run(["systemctl", "disable", UNIT])
            unit.unlink()
            run(["systemctl", "daemon-reload"])
        _remove(etc / TMPFILES)
        if setup.layout == ZRAM:
            _write(etc / ZRAM_DROPIN, HEADER + f"[zram0]\nzram-size = {setup.zram_size}\n"
                                               f"compression-algorithm = {setup.compressor}\n")
        else:
            _remove(etc / ZRAM_DROPIN)
    if setup.layout == BAZZITE:
        _remove(etc / SYSCTL)
    else:
        _write(etc / SYSCTL, HEADER + f"vm.swappiness = {setup.swappiness}\n")
    return {"ok": True, "before": before.__dict__, "after": read_setup(etc, var).__dict__}


def delete_file(etc: Path = Path("/etc"), var: Path = Path("/var"), proc_root: Path = Path("/proc"),
                run: Run = _run) -> dict:
    """Removes the swap file, its SELinux rule and its folder (when nothing else is in it)."""
    path = var / SWAP_FILE
    if read_setup(etc, var).layout == ZSWAP_FILE:
        raise SwapError("The next boot's layout uses the swap file. Apply another layout first.")
    if file_in_use(var, proc_root):
        raise SwapError("The swap file is in use until the board restarts. Restart it and delete the file then.")
    size = file_mib(var)
    path.unlink(missing_ok=True)
    if run(["selinuxenabled"]) == 0:
        run(["semanage", "fcontext", "-d", str(path)])
    if path.parent.is_dir() and not any(path.parent.iterdir()):
        if run(["btrfs", "subvolume", "delete", str(path.parent)]) != 0:
            shutil.rmtree(path.parent, ignore_errors=True)
    return {"ok": True, "deleted_mib": size}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="swap.py", description="BC-250 swap layout (root helper)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--layout", choices=tuple(LAYOUTS))
    group.add_argument("--delete-file", action="store_true")
    parser.add_argument("--zram-size", default="")
    parser.add_argument("--compressor", default="")
    parser.add_argument("--file-mib", type=int, default=0)
    parser.add_argument("--swappiness", type=int)
    args = parser.parse_args(argv)
    try:
        if os.geteuid() != 0:
            raise SwapError("The swap layout is written as root.")
        if args.delete_file:
            result = delete_file()
        else:
            result = apply(Setup(args.layout, args.zram_size, args.compressor, args.file_mib, args.swappiness))
    except SwapError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    except OSError as exc:
        print(json.dumps({"ok": False, "error": f"{exc.strerror or exc}: {exc.filename or ''}".rstrip(": ")}))
        return 1
    print(json.dumps(result))
    return 0


def arguments(setup: Setup) -> list[str]:
    """The helper's command line for a layout."""
    args = ["--layout", setup.layout]
    if setup.layout == ZRAM:
        args += ["--zram-size", setup.zram_size]
    if setup.layout == ZSWAP_FILE:
        args += ["--file-mib", str(setup.file_mib)]
    if setup.layout != BAZZITE:
        args += ["--compressor", setup.compressor, "--swappiness", str(setup.swappiness)]
    return args


if __name__ == "__main__":
    sys.exit(main())
