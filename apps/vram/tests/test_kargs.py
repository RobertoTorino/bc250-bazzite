# SPDX-License-Identifier: GPL-3.0-or-later
from vram_manager import kargs, privileged
from conftest import FakeOstree


def test_pages_in():
    assert kargs.pages_in("rw ttm.pages_limit=3014656 zswap.enabled=0") == 3014656
    assert kargs.pages_in("ttm.pages_limit=1 ttm.pages_limit=2") == 2         # the last one counts
    assert kargs.pages_in("rw ttm.pages_limit=many") is None
    assert kargs.pages_in("rw ttm.page_pool_size=3014656") is None and kargs.pages_in(None) is None
    assert kargs.mib(3014656) == 11776 and kargs.mib(None) is None


def test_command():
    assert kargs.command(None, 3014656) == ["rpm-ostree", "kargs", "--delete=ttm.pages_limit=3014656",
                                            "--unchanged-exit-77"]
    assert kargs.command(4194304, 3014656)[2] == "--replace=ttm.pages_limit=4194304"
    assert kargs.command(4194304, None)[2] == "--append-if-missing=ttm.pages_limit=4194304"
    assert [pages for _, pages in kargs.PRESETS] == [None, 3014656, 4194304]


def test_read_next_boot():
    assert kargs.read_next_boot(FakeOstree()) == kargs.NextBoot(3014656)
    assert kargs.read_next_boot(FakeOstree("rw quiet")) == kargs.NextBoot(None)
    missing = FakeOstree()
    missing.error, missing.code = "rpm-ostree is not installed.", privileged.NOT_INSTALLED
    assert kargs.read_next_boot(missing).error.startswith("This system has no rpm-ostree")
    down = FakeOstree()
    down.error = "error: Could not connect: No such file or directory"
    assert kargs.read_next_boot(down).error == ("rpm-ostree kargs failed: error: Could not connect: No such file or "
                                                "directory")


def test_apply():
    ostree = FakeOstree("rw quiet")
    assert kargs.apply(ostree, 3014656, None) == "" and ostree.arguments == "rw quiet ttm.pages_limit=3014656"
    assert kargs.apply(ostree, 3014656, 3014656) == "" and len(ostree.calls) == 2   # nothing to do: no call
    assert kargs.apply(ostree, 4194304, 3014656) == "" and "ttm.pages_limit=4194304" in ostree.arguments
    assert kargs.apply(ostree, None, 4194304) == "" and ostree.arguments == "rw quiet"
    refused = FakeOstree()
    refused.error = "error: ... GDBus.Error:org.freedesktop.PolicyKit1.Error.NotAuthorized: not authorized"
    assert kargs.apply(refused, None, 3014656) == "Not authorized: the password dialog was canceled or refused."


def test_apply_checks_the_next_boot_afterwards():
    """The owner's board, 01-11-2026: a key-only --delete-if-present matched nothing, rpm-ostree said "unchanged"
    and the app took it for done. Now the next boot's arguments are read back and must hold what was asked."""
    ostree = FakeOstree()
    code, _, _ = ostree(["rpm-ostree", "kargs", "--delete-if-present=ttm.pages_limit", "--unchanged-exit-77"])
    assert code == 77 and "ttm.pages_limit=3014656" in ostree.arguments     # rpm-ostree's own matching

    class Stubborn(FakeOstree):
        def __call__(self, cmd):
            if cmd[2].startswith("--delete"):
                self.calls.append(cmd)
                return 77, "", ""                                             # says unchanged, changes nothing
            return super().__call__(cmd)
    stubborn = Stubborn()
    error = kargs.apply(stubborn, None, 3014656)
    assert error.startswith("rpm-ostree reported no change, but the next boot's kernel arguments still have "
                            "ttm.pages_limit=3014656. Nothing is changed. Try again, or run this in a terminal: "
                            "rpm-ostree kargs --delete=ttm.pages_limit=3014656")


def test_the_ps5_emulators_driver_options_go_in_and_out_in_one_call():
    """In: each missing word appended, a key with another value replaced. Out: only the profile's own words."""
    assert kargs.driver_in("rw amdgpu.sched_policy=2 amdgpu.cwsr_enable=1 amdgpu.ppfeaturemask=1") == (
        "amdgpu.sched_policy=2", "amdgpu.cwsr_enable=1")
    assert kargs.has_driver(kargs.DRIVER) and not kargs.has_driver(("amdgpu.sched_policy=2",))
    assert kargs.command(3670016, 3014656, True, ("amdgpu.cwsr_enable=1",)) == [
        "rpm-ostree", "kargs", "--replace=ttm.pages_limit=3670016", "--append-if-missing=amdgpu.sched_policy=2",
        "--append-if-missing=amdgpu.vm_update_mode=0", "--replace=amdgpu.cwsr_enable=0", "--unchanged-exit-77"]
    assert kargs.command(3014656, 3014656, False, ("amdgpu.sched_policy=2", "amdgpu.cwsr_enable=1")) == [
        "rpm-ostree", "kargs", "--delete=amdgpu.sched_policy=2", "--unchanged-exit-77"]    # cwsr_enable=1 is not ours
    ostree = FakeOstree("rw ttm.pages_limit=3014656 amdgpu.cwsr_enable=1")
    assert kargs.apply(ostree, 3670016, 3014656, True, ("amdgpu.cwsr_enable=1",)) == ""
    assert len([c for c in ostree.calls if c[2] != "--deploy-index=0"]) == 1                  # one deployment
    after = kargs.read_next_boot(ostree)
    assert after.pages == 3670016 and kargs.has_driver(after.driver) and "amdgpu.cwsr_enable=1" not in after.driver
    assert kargs.apply(ostree, 3014656, 3670016, False, after.driver) == ""
    assert kargs.read_next_boot(ostree).driver == () and kargs.apply(ostree, 3014656, 3014656, False, ()) == ""
