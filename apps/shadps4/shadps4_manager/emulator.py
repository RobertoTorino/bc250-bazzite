# SPDX-License-Identifier: GPL-3.0-or-later
"""The shadPS4 this app installs: the newest nightly on GitHub (the pre-release, named after its date and commit; an
AppImage in a zip), checked against the SHA-256 GitHub publishes for it (owner, 28-11-2026: the nightly builds).
shadPS4 keeps only one nightly on GitHub and deletes it when the next one comes, so no nightly can be pinned: Install
asks GitHub which one is the newest and puts that in. VERSION and the rest below are the nightly this version of the
app was made with, for the window's texts and Nexus Dependencies. The app says when a newer nightly is out. Another
build, a stable release or the nightly, is downloaded beside it in the version manager (owner, 20-11-2026: as
shadPS4's own launcher has one; core's builds); it was not tried on the board.

Each build goes to ~/.local/share/bc250-shadps4-manager/emulator/<version>/, with "current" pointing to the one in
use. The run wrapper (~/.local/bin/bc250-shadps4-run) starts "current", so the Steam shortcuts keep working when the
version changes."""

from __future__ import annotations

import hashlib
import re
import shutil
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from pathlib import Path

from bc250_core import builds
from bc250_core.builds import Build
from bc250_core.platform import data_home
from bc250_core.updates import Fetch, ReleaseInfo, github_fetch

from . import APP_ID, __version__

VERSION = "2026-11-28-86aad15"          # the nightly this version of the app was made with (its folder name)
TAG = "Pre-release-shadPS4-2026-11-28-86aad15dbcdb58756effc507d4142f5996e5f348"
ASSET = "shadps4-linux-sdl-2026-11-28-86aad15.zip"
SHA256 = "8748e0413a08ddef45bdc30dc6feef7929d7a6d85c5798ceda2356d2ec87a04f"
SIZE_MB = 32                            # the zip, for the question before downloading
NAME = "Pre-release-shadPS4-2026-11-28-86aad15"                 # the release's name on GitHub
PUBLISHED = "2026-11-28"
MEMBER = "Shadps4-sdl.AppImage"         # the only file in the zip
REPO = "shadps4-emu/shadPS4"
URL = f"https://github.com/{REPO}/releases/download/{TAG}/{ASSET}"
RELEASE_PAGE = f"https://github.com/{REPO}/releases/tag/{TAG}"
CHUNK = 1 << 20
TIMEOUT = 30

Progress = Callable[[int, int], None]                   # bytes so far, total (0 when unknown)
Download = Callable[[str, Path, Progress | None], None]


class EmulatorError(Exception):
    pass


def emulator_home() -> Path:
    return data_home() / APP_ID / "emulator"


def appimage(home: Path) -> Path:
    """The AppImage the run wrapper starts."""
    return home / "current" / MEMBER


def installed_version(home: Path) -> str:
    """The installed shadPS4 version ("2026-11-28-86aad15", "0.21.0"), "" when none is."""
    current = home / "current"
    if not (current / MEMBER).is_file():
        return ""
    return current.resolve().name


def download(url: str, dest: Path, progress: Progress | None = None) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": f"{APP_ID}/{__version__}"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response, dest.open("wb") as out:
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        while chunk := response.read(CHUNK):
            out.write(chunk)
            done += len(chunk)
            if progress:
                progress(done, total)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def unpack(archive: Path, member: Path) -> None:
    """The AppImage out of a release's zip (core's builds.install calls it on the checked download)."""
    try:
        with zipfile.ZipFile(archive) as packed:
            if MEMBER not in packed.namelist():
                raise builds.BuildError(f"{archive.name} has no {MEMBER}.")
            with packed.open(MEMBER) as source, member.open("wb") as out:
                shutil.copyfileobj(source, out, CHUNK)
    except zipfile.BadZipFile as error:
        raise builds.BuildError(f"{archive.name} is damaged.") from error


def tested() -> Build:
    """The nightly this version of the app was made with. GitHub deletes it once the next nightly is out."""
    return Build(VERSION, NAME, PUBLISHED, builds.PRERELEASE, URL, ASSET, SHA256, SIZE_MB << 20, RELEASE_PAGE)


def newest(fetch: Fetch | None = None) -> Build:
    """The newest nightly on GitHub, with the SHA-256 GitHub publishes for it (EmulatorError when GitHub cannot be
    asked or has none)."""
    try:
        found = available(fetch)
    except builds.BuildError as error:
        raise EmulatorError(str(error)) from error
    nightly = next((build for build in found if build.kind == builds.PRERELEASE), None)
    if nightly is None:
        raise EmulatorError("GitHub has no shadPS4 nightly for Linux.")
    return nightly


def install(home: Path, fetch: Download = download, progress: Progress | None = None,
            find: Callable[[], Build] | None = None) -> str:
    """Puts the newest nightly in use (*find*: newest): from its folder when it is there, else downloaded, checked
    against GitHub's SHA-256 and unpacked. Other builds stay. Returns what was done. Nothing changes when a step
    fails (EmulatorError)."""
    build = (find or newest)()
    try:
        if (home / build.folder / MEMBER).is_file() and (home / build.folder / builds.INFO).is_file():
            builds.use(home, build.folder, MEMBER)
            return f"shadPS4 {build.version}, the newest nightly, is in use."
        builds.install(home, build, MEMBER, fetch, progress, unpack)
    except builds.BuildError as error:
        raise EmulatorError(str(error)) from error
    return f"shadPS4 {build.version}, the newest nightly, is installed."


_ASSET = re.compile(r"shadps4-linux-sdl-(.+)\.zip")


def _pick(release: dict, asset: dict) -> str | None:
    match = _ASSET.fullmatch(str(asset.get("name", "")))
    return match.group(1) if match else None


def available(fetch: Fetch | None = None) -> list[Build]:
    """The shadPS4 builds that can be downloaded, newest first: the stable releases and the pre-release (a nightly,
    named after its date and commit), each the Linux SDL zip (builds.BuildError when GitHub cannot be asked)."""
    return builds.github_builds(REPO, _pick, fetch or github_fetch(f"{APP_ID}/{__version__}"))


def install_build(home: Path, build: Build, fetch: Download = download, progress: Progress | None = None) -> None:
    """Downloads *build* beside the others, checked against its SHA-256 and unpacked; not in use yet."""
    builds.install(home, build, MEMBER, fetch, progress, unpack, use_it=False)


def remove(home: Path) -> None:
    """Every installed shadPS4 build goes; shadPS4's own folder (saves, system modules, settings) stays."""
    shutil.rmtree(home, ignore_errors=True)


def newer_release(fetch: Fetch | None = None) -> ReleaseInfo | None:
    """shadPS4's newest nightly, which the window compares with the build in use; None when GitHub cannot be asked
    (nothing to say then)."""
    try:
        build = newest(fetch or github_fetch(f"{APP_ID}/{__version__}"))
    except EmulatorError:
        return None
    return ReleaseInfo(build.version, build.name, build.page, build.published, build.asset, build.url, build.size)
