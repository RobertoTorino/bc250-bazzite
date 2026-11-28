# SPDX-License-Identifier: GPL-3.0-or-later
"""The GTT limit on the kernel command line: ttm.pages_limit in the next boot's kernel arguments, read and changed
with rpm-ostree.

rpm-ostree keeps the kernel arguments per deployment. `rpm-ostree kargs --deploy-index=0` prints those of the
first deployment, the one the next boot starts, and needs no root. A change (`--append-if-missing`, `--replace`
or `--delete`) makes a new deployment with the argument and takes effect at the next boot. The delete names the
whole argument, key and value: `--delete-if-present=ttm.pages_limit` with the key alone matched nothing on the
owner's board (01-11-2026), rpm-ostree reported no change in a second, and the app took that for done. So a change
is checked afterwards: the next boot's arguments are read again and must hold what was asked. rpm-ostree's
daemon asks polkit for it (org.projectatomic.rpmostree1.bootconfig), so the desktop's password dialog appears by
itself, without pkexec. The limit is in 4 KiB pages: amdgpu sizes the GTT from it and caps it at the RAM, and
without the argument the kernel takes half the RAM.

The PS5 emulator profile (owner, 27-11-2026) also puts three GPU driver options in the next boot's arguments,
DRIVER. A file in /etc/modprobe.d does not work on Bazzite: the GPU driver loads from the early boot image, before
/etc is there. The other profiles remove exactly these three words again, and leave the same options with other
values alone. The limit and the options go in one rpm-ostree call, so one deployment and one password.

Nothing here needs the standard library's subprocess: the window runs the commands through privileged.run_command,
which keeps the window responsive, and the tests run a fake."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

KEY = "ttm.pages_limit"
PAGES_PER_MIB = 256                     # 4 KiB pages
UNCHANGED = 77                          # rpm-ostree kargs --unchanged-exit-77: nothing to change
NOT_INSTALLED = -2                      # privileged.run_command: the command is not on this system

# The limits the app offers: (label, pages); None is the kernel's default, the argument removed.
PRESETS: tuple[tuple[str, int | None], ...] = (
    ("Kernel default: half the RAM", None),
    ("11.5 GiB, the suite's value (Board Test, test 37)", 3014656),
    ("16 GiB: all the RAM, whatever the split", 4194304),
)

# The PS5 emulator profile's GPU driver options (ACTION-LIST row 6, owner 27-11-2026): not tested on a board yet
DRIVER: tuple[str, ...] = ("amdgpu.sched_policy=2", "amdgpu.vm_update_mode=0", "amdgpu.cwsr_enable=0")

Run = Callable[[list[str]], tuple[int, str, str]]   # (exit code, stdout, stderr)


def pages_in(arguments: str | None) -> int | None:
    """The ttm.pages_limit of a kernel argument line (/proc/cmdline, rpm-ostree kargs); the last one counts, as
    for the kernel. None when it is absent or not a number."""
    found = None
    for word in (arguments or "").split():
        if word.startswith(KEY + "="):
            try:
                found = int(word[len(KEY) + 1:])
            except ValueError:
                found = None
    return found


def driver_in(arguments: str | None) -> tuple[str, ...]:
    """The words of an argument line whose key is one of DRIVER's, as they are written: "amdgpu.cwsr_enable=1"."""
    keys = {word.split("=", 1)[0] for word in DRIVER}
    return tuple(word for word in (arguments or "").split() if word.split("=", 1)[0] in keys)


def has_driver(present: tuple[str, ...]) -> bool:
    """Whether the arguments hold all of DRIVER's words."""
    return set(DRIVER) <= set(present)


def mib(pages: int | None) -> int | None:
    return pages // PAGES_PER_MIB if pages is not None else None


@dataclass(frozen=True)
class NextBoot:
    pages: int | None = None            # ttm.pages_limit in the next boot's kernel arguments; None: not set
    driver: tuple[str, ...] = ()        # the words of DRIVER's keys in them, as written (driver_in)
    error: str = ""                     # why they could not be read: no rpm-ostree, its daemon failed


def _failure(code: int, out: str, err: str) -> str:
    if code == NOT_INSTALLED:
        return "This system has no rpm-ostree. It is not Bazzite, or not an image-based one."
    text = (err.strip() or out.strip()).splitlines()
    last = text[-1] if text else f"exit code {code}"
    if "not authorized" in last.lower() or "notauthorized" in last.lower():
        return "Not authorized: the password dialog was canceled or refused."
    return f"rpm-ostree kargs failed: {last[-300:]}"


def read_next_boot(run: Run) -> NextBoot:
    code, out, err = run(["rpm-ostree", "kargs", "--deploy-index=0"])
    if code != 0:
        return NextBoot(error=_failure(code, out, err))
    return NextBoot(pages_in(out), driver_in(out))


def _limit_change(pages: int | None, present: int | None) -> list[str]:
    if pages == present:
        return []
    if pages is None:
        return [f"--delete={KEY}={present}"]
    if present is not None:
        return [f"--replace={KEY}={pages}"]
    return [f"--append-if-missing={KEY}={pages}"]


def driver_change(driver: bool | None, present: tuple[str, ...]) -> list[str]:
    """DRIVER's words in (True) or out (False) of the arguments; None leaves them. Out removes only DRIVER's own
    words; in replaces a key written with another value."""
    if driver is None:
        return []
    if not driver:
        return [f"--delete={word}" for word in DRIVER if word in present]
    written = {word.split("=", 1)[0]: word for word in present}
    changes = []
    for word in DRIVER:
        key = word.split("=", 1)[0]
        if key not in written:
            changes.append(f"--append-if-missing={word}")
        elif written[key] != word:
            changes.append(f"--replace={word}")
    return changes


def command(pages: int | None, present: int | None, driver: bool | None = None,
            driver_present: tuple[str, ...] = ()) -> list[str]:
    """The rpm-ostree call that puts *pages* in the next boot's arguments (removes the argument for None);
    *present* is the value the next boot has now, None when it has none (--replace and --delete name it,
    --append-if-missing needs it absent). *driver* puts DRIVER's words in or out in the same call (None: leaves
    them); *driver_present* is what the next boot has of them now."""
    return ["rpm-ostree", "kargs", *_limit_change(pages, present), *driver_change(driver, driver_present),
            "--unchanged-exit-77"]


def apply(run: Run, pages: int | None, present: int | None, driver: bool | None = None,
          driver_present: tuple[str, ...] = ()) -> str:
    """Changes the next boot's arguments to *pages*, and DRIVER's words in or out with *driver*, in one call, and
    checks that they hold it; "" when done (or nothing to change), else why not."""
    if not _limit_change(pages, present) and not driver_change(driver, driver_present):
        return ""
    code, out, err = run(command(pages, present, driver, driver_present))
    if code not in (0, UNCHANGED):
        return _failure(code, out, err)
    after = read_next_boot(run)
    if after.error:
        return after.error
    wrong = []
    if after.pages != pages:
        wrong.append(f"{KEY}={after.pages}" if after.pages is not None else f"no {KEY}")
    if driver is not None and driver_change(driver, after.driver):
        wrong.append(" ".join(after.driver) or "none of the GPU driver options")
    if wrong:
        return (f"rpm-ostree reported {'no change' if code == UNCHANGED else 'success'}, but the next boot's kernel "
                f"arguments still have {' and '.join(wrong)}. Nothing is changed. Try again, or run this in a "
                f"terminal: {' '.join(command(pages, after.pages, driver, after.driver))}")
    return ""
