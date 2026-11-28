# SPDX-License-Identifier: GPL-3.0-or-later
"""Installing shadPS4's newest nightly (emulator.py; owner, 28-11-2026) from a zip made here instead of the download,
GitHub's answer the conftest's (offline_newest): checked against its SHA-256 first, "current" switched, other versions kept beside it, and nothing changed when a step fails; the builds
the version manager offers, the stable releases and the pre-release (core's builds; owner, 20-11-2026)."""

from __future__ import annotations

import hashlib
import io
import urllib.error
import zipfile
from pathlib import Path

import pytest

from bc250_core import builds
from shadps4_manager import emulator


def _zip(member: str = emulator.MEMBER, data: bytes = b"#!/bin/sh\necho shadPS4\n") -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as packed:
        packed.writestr(member, data)
    return out.getvalue()


def _fetch(payload: bytes, calls: list | None = None):
    def fetch(url: str, dest: Path, progress=None) -> None:
        if calls is not None:
            calls.append(url)
        dest.write_bytes(payload)
    return fetch


@pytest.fixture
def pinned(monkeypatch):
    """The zip the tests use, pinned as the release."""
    payload = _zip()
    monkeypatch.setattr(emulator, "SHA256", hashlib.sha256(payload).hexdigest())
    return payload


def test_the_pin_points_at_the_release():
    assert emulator.URL == ("https://github.com/shadps4-emu/shadPS4/releases/download/"
                            "Pre-release-shadPS4-2026-11-28-86aad15dbcdb58756effc507d4142f5996e5f348/"
                            "shadps4-linux-sdl-2026-11-28-86aad15.zip")
    assert len(emulator.SHA256) == 64 and emulator._pick({}, {"name": emulator.ASSET}) == emulator.VERSION
    assert emulator.tested().kind == builds.PRERELEASE


def test_install_and_remove(tmp_path, pinned):
    home = tmp_path / "emulator"
    assert emulator.installed_version(home) == ""
    calls = []
    assert emulator.install(home, _fetch(pinned, calls)) == f"shadPS4 {emulator.VERSION}, the newest nightly, is installed."
    assert calls == [emulator.URL]
    image = emulator.appimage(home)
    assert image.read_bytes().startswith(b"#!/bin/sh") and image.stat().st_mode & 0o777 == 0o755
    assert (home / "current").is_symlink() and emulator.installed_version(home) == emulator.VERSION
    assert sorted(p.name for p in home.iterdir()) == [emulator.VERSION, "current"]  # no download left behind
    emulator.remove(home)
    assert not home.exists() and emulator.installed_version(home) == ""


def test_an_older_version_stays_beside_it(tmp_path, pinned):
    home = tmp_path / "emulator"
    (home / "0.18.0").mkdir(parents=True)
    (home / "0.18.0" / emulator.MEMBER).write_text("old")
    (home / "current").symlink_to("0.18.0")
    assert emulator.installed_version(home) == "0.18.0"
    emulator.install(home, _fetch(pinned))
    assert emulator.installed_version(home) == emulator.VERSION
    assert (home / "0.18.0" / emulator.MEMBER).read_text() == "old"              # one click away
    builds.use(home, "0.18.0", emulator.MEMBER)
    calls = []
    assert emulator.install(home, _fetch(pinned, calls)) == f"shadPS4 {emulator.VERSION}, the newest nightly, is in use."
    assert calls == [] and emulator.installed_version(home) == emulator.VERSION  # back without a download


def test_the_builds_on_github(tmp_path):
    """The version manager's list: the Linux SDL zip of each release and of the pre-release, with GitHub's SHA-256;
    one is unpacked as the pinned release is."""
    nightly = _zip(data=b"#!/bin/sh\necho nightly\n")

    def release(tag: str, name: str, asset: str, prerelease: bool = False) -> dict:
        return {"tag_name": tag, "name": name, "published_at": "2026-11-19T10:00:00Z", "prerelease": prerelease,
                "assets": [{"name": "shadps4-win64-sdl-x.zip", "digest": "sha256:" + "00" * 32},
                           {"name": asset, "digest": "sha256:" + hashlib.sha256(nightly).hexdigest(), "size": 33000000,
                            "browser_download_url": f"https://github.com/shadps4-emu/shadPS4/releases/download/{tag}/"
                                                    f"{asset}"}]}

    def fetch(url: str):
        assert url == "https://api.github.com/repos/shadps4-emu/shadPS4/releases?per_page=30"
        return [release("Pre-release-shadPS4-2026-11-19-443b954bea3e", "Pre-release-shadPS4-2026-11-19-443b954",
                        "shadps4-linux-sdl-2026-11-19-443b954.zip", prerelease=True),
                release("v.0.20.0", "shadps4 v0.20.0 - codename Dead Or Stephen 5 - The Comeback",
                        "shadps4-linux-sdl-0.20.0.zip")]
    found = emulator.available(fetch)
    assert [(b.version, b.kind) for b in found] == [("2026-11-19-443b954", builds.PRERELEASE),
                                                    ("0.20.0", builds.RELEASE)]
    assert found[1].name.endswith("The Comeback")
    home = tmp_path / "emulator"
    emulator.install_build(home, found[0], _fetch(nightly))
    assert (home / "2026-11-19-443b954" / emulator.MEMBER).read_bytes() == b"#!/bin/sh\necho nightly\n"
    assert emulator.installed_version(home) == ""                                # not in use until Use
    assert emulator.tested().version == emulator.VERSION 


@pytest.mark.parametrize("payload, message", [
    (b"something else", "SHA-256 differs"),
])
def test_a_different_file_is_refused(tmp_path, pinned, payload, message):
    home = tmp_path / "emulator"
    with pytest.raises(emulator.EmulatorError, match=message):
        emulator.install(home, _fetch(payload))
    assert emulator.installed_version(home) == "" and not list(home.iterdir())


def test_a_zip_without_the_appimage_or_damaged(tmp_path, monkeypatch):
    home = tmp_path / "emulator"
    for payload, message in ((_zip("other.AppImage"), "has no Shadps4-sdl.AppImage"), (b"PK\x03\x04broken", "damaged")):
        monkeypatch.setattr(emulator, "SHA256", hashlib.sha256(payload).hexdigest())
        with pytest.raises(emulator.EmulatorError, match=message):
            emulator.install(home, _fetch(payload))
        assert not list(home.iterdir())


def test_download_errors_say_what_happened(tmp_path):
    def http(url, dest, progress=None):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    def offline(url, dest, progress=None):
        raise urllib.error.URLError("Name or service not known")
    with pytest.raises(emulator.EmulatorError, match="GitHub answered 404"):
        emulator.install(tmp_path, http)
    with pytest.raises(emulator.EmulatorError, match="download failed: Name or service not known"):
        emulator.install(tmp_path, offline)


def _nightlies(*versions: str):
    """GitHub's release list for shadPS4, newest first: the nightly (a pre-release) and stable releases."""
    def fetch(url: str):
        assert url == "https://api.github.com/repos/shadps4-emu/shadPS4/releases?per_page=30"
        return [{"tag_name": f"Pre-release-shadPS4-{v}" if v[0] == "2" else f"v.{v}", "name": v,
                 "html_url": f"https://github.com/shadps4-emu/shadPS4/releases/tag/{v}", "prerelease": v[0] == "2",
                 "published_at": "2026-11-29T10:00:00Z",
                 "assets": [{"name": f"shadps4-linux-sdl-{v}.zip", "digest": "sha256:" + "ab" * 32, "size": 33000000,
                             "browser_download_url": f"https://github.com/x/{v}.zip"}]} for v in versions]
    return fetch


def test_the_newest_nightly(offline_newest, monkeypatch):
    """Install's build and the window's news: GitHub's nightly, not a stable release beside it."""
    monkeypatch.setattr(emulator, "newest", offline_newest)     # the real one
    found = emulator.newest(_nightlies("2026-11-29-abcdef0", "0.21.0"))
    assert (found.version, found.kind, found.sha256) == ("2026-11-29-abcdef0", builds.PRERELEASE, "ab" * 32)
    news = emulator.newer_release(_nightlies("2026-11-29-abcdef0", "0.21.0"))
    assert (news.version, news.published) == ("2026-11-29-abcdef0", "2026-11-29") and news.url.endswith("abcdef0")
    with pytest.raises(emulator.EmulatorError, match="no shadPS4 nightly"):
        emulator.newest(_nightlies("0.21.0"))

    def offline(url: str):
        raise urllib.error.URLError("no network")
    with pytest.raises(emulator.EmulatorError, match="GitHub could not be asked"):
        emulator.newest(offline)
    assert emulator.newer_release(offline) is None                                 # nothing to say then


def test_install_takes_what_github_names(tmp_path):
    """The newest nightly GitHub names is downloaded and put in use; already there, it is put in use alone."""
    payload = _zip(data=b"#!/bin/sh\necho newer nightly\n")
    newer = builds.Build("2026-11-29-abcdef0", "Pre-release", "2026-11-29", builds.PRERELEASE,
                         "https://github.com/x/newer.zip", "shadps4-linux-sdl-2026-11-29-abcdef0.zip",
                         hashlib.sha256(payload).hexdigest(), len(payload))
    home, calls = tmp_path / "emulator", []
    assert emulator.install(home, _fetch(payload, calls), find=lambda: newer) == ("shadPS4 2026-11-29-abcdef0, the "
                                                                                  "newest nightly, is installed.")
    assert calls == ["https://github.com/x/newer.zip"] and emulator.installed_version(home) == "2026-11-29-abcdef0"
    assert emulator.install(home, _fetch(payload, calls), find=lambda: newer).endswith("is in use.")
    assert len(calls) == 1
