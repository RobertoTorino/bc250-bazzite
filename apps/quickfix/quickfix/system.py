# SPDX-License-Identifier: GPL-3.0-or-later
"""The system part of the quickfixes: what runs as root. The app runs this file through pkexec with the system python3
in isolated mode (-I), one change per call, and it needs only the standard library:

    system.py metrics on [--method M] | off     fix-metrics in the governor's config.toml, then restart a running
                                                governor
    system.py sensors on | off                  options nct6683 force=true in /etc/modprobe.d (SENSORS_CONF)
    system.py mapcount on | off                 vm.max_map_count in /etc/sysctl.d (MAPCOUNT_CONF)
    system.py journal on | off                  the journal kept on the disk, in /var/log/journal
    system.py iommu on | off                    the kernel argument amd_iommu=off, with rpm-ostree kargs
    system.py mitigations on | off              the kernel argument mitigations=off, with rpm-ostree kargs
    system.py vrm on | off                      the bc250_vrm module: built in /var/lib/bc250-quickfix/vrm and loaded
                                                at every boot by a service of its own (VRM_UNIT)

Each change touches only its own file (or, for metrics, the two lines of the governor's [gpu-usage] table, after a
dated backup of config.toml beside it, the same as BC-250 GPU Manager's; for a kernel argument, that argument and a
note in /var/lib/bc250-quickfix that the quickfix added it; for vrm, its folder and its service) and is undone by
its "off". The reading side is in the app
(state.py): it needs no password."""

from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SYSTEM_PYTHON = "/usr/bin/python3"
GOVERNOR_CONFIG = "cyan-skillfish-governor-smu/config.toml"        # in /etc
GOVERNOR_UNIT = "cyan-skillfish-governor-smu.service"
METHODS = ("busy-flag", "process", "kernel")
SENSORS_CONF = "modprobe.d/bc250-quickfix-nct6683.conf"            # in /etc
SENSORS_LINE = "options nct6683 force=true"
MAPCOUNT_CONF = "sysctl.d/90-bc250-quickfix-max-map-count.conf"    # in /etc
MAPCOUNT = 2147483642                                             # what SteamOS and Bazzite set
JOURNAL_DIR = "log/journal"                                       # in /var
JOURNAL_MARK = ".bc250-quickfix"                                   # in it: the quickfix made the folder
KARGS = {"iommu": "amd_iommu=off", "mitigations": "mitigations=off"}  # the kernel arguments the quickfixes add
KARGS_DIR = "lib/bc250-quickfix"                                   # in /var, shared by every deployment: <key>.karg
REBOOT = "Restart the board with systemctl reboot to apply it"
# VRM Sensors: the source of the bc250_vrm module comes with the app (vrm/, unchanged files of VRM_REPO at VRM_TAG;
# tests/test_vrm.py compares them with VRM_SHA256), with a Kbuild and the service's script of our own.
VRM_REPO = "Hexxeh/bc250-vrm-dkms"
VRM_TAG = "v1.1.0"
VRM_COMMIT = "67aea0d9416eec93ec058af3ff519e81af283950"
VRM_SHA256 = {
    "bc250_vrm_core.c": "42f04046ff91ba65157ea8b5542239a9e4ba0fbaedd1bf82ab50dcc638745286",
    "nct6687_smbus.c": "97e173681bbea5fdf7beb4dba70c82519aad46eef915e32d5f078d9d893b6499",
    "nct6687_smbus.h": "ef2c061be372c845a2efee7856c2b4847875fbd0c6de614c08420eeb00a04c17",
    "LICENSE": "edaef632cbb643e4e7a221717a6c441a4c1a7c918e6e4d56debc3d8739b233f6",
}
VRM_SOURCE = Path(__file__).resolve().parent / "vrm"
VRM_MODULE = "bc250_vrm"
VRM_DIR = "lib/bc250-quickfix/vrm"                                 # in /var: src/, the script, one build
VRM_SCRIPT = "bc250-quickfix-vrm.sh"
VRM_UNIT = "bc250-quickfix-vrm.service"                            # in /etc/systemd/system


def karg_mark(var: Path, key: str) -> Path:
    """The note that the quickfix added its kernel argument: it turns off only what it turned on."""
    return var / KARGS_DIR / f"{key}.karg"


def next_kargs() -> list[str] | None:
    """The kernel arguments of the deployment that boots next (rpm-ostree kargs, which needs no root); None when
    rpm-ostree cannot tell."""
    try:
        done = subprocess.run(["rpm-ostree", "kargs"], capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout.split() if done.returncode == 0 else None


def command(args: list[str], own: Path = Path(__file__)) -> list[str]:
    """This file as root, through polkit's password dialog."""
    python = SYSTEM_PYTHON if Path(SYSTEM_PYTHON).is_file() else sys.executable
    return ["pkexec", python, "-I", str(own.resolve()), *args]


def answer(code: int, out: str) -> str:
    """What went wrong ("" when nothing did); pkexec exits with 126 or 127 when the password dialog is canceled."""
    if code == 0:
        return ""
    if code in (126, 127):
        return "Not authorized: the password dialog was canceled or refused."
    return out.strip() or f"It failed (exit code {code})."


def run(argv: list[str]) -> int:
    print("$ " + " ".join(argv), flush=True)
    try:
        return subprocess.run(argv, check=False).returncode
    except OSError as exc:
        print(f"{argv[0]}: {exc}")
        return 127


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.chmod(tmp, 0o644)
    tmp.replace(path)
    print(f"Wrote {path}")


# ----------------------------------------------------------------------------------------------- GPU metrics
def set_metrics(text: str, on: bool, method: str | None) -> str:
    """config.toml's text with fix-metrics (and the method, when given) set in its [gpu-usage] table; every other
    line, comments included, stays as it is. A table or key that is missing is added."""
    lines = text.splitlines()
    want = {"fix-metrics": "true" if on else "false"}
    if method is not None:
        want["method"] = f'"{method}"'
    start = next((i for i, line in enumerate(lines) if line.strip() == "[gpu-usage]"), None)
    if start is None:
        lines += ["", "[gpu-usage]"] + [f"{key} = {value}" for key, value in want.items()]
        return "\n".join(lines) + "\n"
    end = next((i for i in range(start + 1, len(lines)) if lines[i].lstrip().startswith("[")), len(lines))
    for i in range(start + 1, end):
        found = re.match(r"^(\s*)([A-Za-z0-9_-]+)(\s*=\s*)(\"[^\"]*\"|[^#\s]+)(.*)$", lines[i])
        if found and found[2] in want:
            lines[i] = f"{found[1]}{found[2]}{found[3]}{want.pop(found[2])}{found[5]}"
    lines[start + 1:start + 1] = [f"{key} = {value}" for key, value in want.items()]
    return "\n".join(lines) + "\n"


def metrics(etc: Path, on: bool, method: str | None) -> int:
    config = etc / GOVERNOR_CONFIG
    if not config.is_file():
        print(f"{config} does not exist. The GPU governor is not installed.")
        return 1
    backup = config.with_name(f"{config.name}.bak-{datetime.datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(config, backup)
    print(f"Backup: {backup}")
    write(config, set_metrics(config.read_text(encoding="utf-8"), on, method))
    return run(["systemctl", "try-restart", GOVERNOR_UNIT])     # a governor that is stopped stays stopped


# --------------------------------------------------------------------------------------------- the others
def sensors(etc: Path, on: bool) -> int:
    conf = etc / SENSORS_CONF
    if on:
        write(conf, f"# Written by BC-250 Quickfix (Sensors Module): the board's SuperIO chip, for its sensors.\n"
                    f"{SENSORS_LINE}\n")
        return run(["modprobe", "nct6683", "force=true"])
    conf.unlink(missing_ok=True)
    print(f"Removed {conf}. The module stays loaded until the next boot.")
    return 0


def mapcount(etc: Path, on: bool) -> int:
    conf = etc / MAPCOUNT_CONF
    if on:
        write(conf, f"# Written by BC-250 Quickfix (Game Memory Map): the memory areas a game may map.\n"
                    f"vm.max_map_count = {MAPCOUNT}\n")
        return run(["sysctl", "-w", f"vm.max_map_count={MAPCOUNT}"])
    conf.unlink(missing_ok=True)
    print(f"Removed {conf}")
    return run(["sysctl", "--system"])           # the value the other files set, else the kernel's own


def journal(var: Path, on: bool) -> int:
    folder = var / JOURNAL_DIR
    if on:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / JOURNAL_MARK).write_text("Made by BC-250 Quickfix (Persistent Journal).\n", encoding="utf-8")
        code = run(["systemd-tmpfiles", "--create", "--prefix", str(folder)])
        return code or run(["journalctl", "--flush"])
    if not (folder / JOURNAL_MARK).is_file():
        print(f"BC-250 Quickfix did not make {folder}, so it stays.")
        return 1
    run(["journalctl", "--relinquish-var"])
    shutil.rmtree(folder)
    print(f"Removed {folder}. journald keeps the journal in memory again, until the next boot.")
    return 0


def kargs(var: Path, key: str, on: bool) -> int:
    """Adds or removes the quickfix's kernel argument with rpm-ostree kargs: a new deployment, active after a reboot.
    Turn on only adds what is not there yet; turn off only removes what the quickfix added (its note)."""
    arg, mark = KARGS[key], karg_mark(var, key)
    current = next_kargs()
    if current is None:
        print("rpm-ostree could not read the kernel arguments. Is this an rpm-ostree system?")
        return 1
    if on:
        if arg in current:
            print(f"{arg} is on the kernel command line of the next boot already. There is nothing to do.")
            return 1
        mark.parent.mkdir(parents=True, exist_ok=True)
        mark.write_text(f"{arg}\n", encoding="utf-8")           # first: a failure below removes it again
        code = run(["rpm-ostree", "kargs", f"--append={arg}"])
        if code:
            mark.unlink(missing_ok=True)
            return code
        print(f"Added {arg}. {REBOOT}.")
        return 0
    if not mark.is_file():
        print(f"BC-250 Quickfix did not add {arg}, so it stays.")
        return 1
    code = run(["rpm-ostree", "kargs", f"--delete-if-present={arg}"]) if arg in current else 0
    if code:
        return code
    mark.unlink()
    print(f"Removed {arg}. {REBOOT}.")
    return 0


def vrm_unit(folder: Path) -> str:
    script = folder / VRM_SCRIPT
    return ("# Written by BC-250 Quickfix (VRM Sensors): the module that reads the board's voltage regulator.\n"
            "[Unit]\n"
            "Description=BC-250 Quickfix (VRM Sensors): build and load the bc250_vrm module\n"
            f"ConditionPathExists={script}\n\n"
            "[Service]\n"
            "Type=oneshot\n"
            "RemainAfterExit=yes\n"
            f"ExecStart=/usr/bin/bash {script} {folder}\n"
            f"ExecStop=-/usr/sbin/rmmod {VRM_MODULE}\n\n"
            "[Install]\n"
            "WantedBy=multi-user.target\n")


def vrm(etc: Path, var: Path, on: bool, source: Path = VRM_SOURCE) -> int:
    """On: the module's source and the service's script go to /var/lib/bc250-quickfix/vrm (root's own copy: the
    service never runs anything from the home folder), and the service is turned on and started, which builds the
    module for the running kernel and loads it. Off: the service is stopped (it unloads the module) and removed with
    the folder."""
    folder, unit = var / VRM_DIR, etc / "systemd" / "system" / VRM_UNIT
    if on:
        missing = [name for name in (*VRM_SHA256, "Kbuild", VRM_SCRIPT) if not (source / name).is_file()]
        if missing:
            print(f"The module's source is not complete in {source}: {', '.join(missing)} missing.")
            return 1
        (folder / "src").mkdir(parents=True, exist_ok=True)
        for name in (*VRM_SHA256, "Kbuild"):
            shutil.copyfile(source / name, folder / "src" / name)
        shutil.copyfile(source / VRM_SCRIPT, folder / VRM_SCRIPT)
        os.chmod(folder / VRM_SCRIPT, 0o755)
        print(f"Copied the module's source to {folder}")
        write(unit, vrm_unit(folder))
        code = run(["systemctl", "daemon-reload"]) or run(["systemctl", "enable", VRM_UNIT])
        if code:
            return code
        code = run(["systemctl", "restart", VRM_UNIT])
        if code:
            run(["journalctl", "-u", VRM_UNIT, "-b", "-n", "40", "--no-pager", "-o", "cat"])
            print("The module was not built or not loaded. The service stays on. Turn off removes it.")
        return code
    if unit.is_file():
        run(["systemctl", "disable", "--now", VRM_UNIT])
        unit.unlink()
        print(f"Removed {unit}")
        run(["systemctl", "daemon-reload"])
    if folder.is_dir():
        shutil.rmtree(folder)
        print(f"Removed {folder}")
    return 0


def main(argv: list[str] | None = None, etc: Path = Path("/etc"), var: Path = Path("/var")) -> int:
    parser = argparse.ArgumentParser(prog="system.py", description="BC-250 Quickfix, the part that runs as root")
    parser.add_argument("change", choices=("metrics", "sensors", "mapcount", "journal", "vrm", *KARGS))
    parser.add_argument("state", choices=("on", "off"))
    parser.add_argument("--method", choices=METHODS)
    args = parser.parse_args(argv)
    on = args.state == "on"
    if args.change == "metrics":
        return metrics(etc, on, args.method if on else None)
    if args.change == "sensors":
        return sensors(etc, on)
    if args.change == "mapcount":
        return mapcount(etc, on)
    if args.change in KARGS:
        return kargs(var, args.change, on)
    if args.change == "vrm":
        return vrm(etc, var, on)
    return journal(var, on)


if __name__ == "__main__":
    sys.exit(main())
