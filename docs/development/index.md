<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# Development

How the repository is laid out, how to set it up and test it, how the wiki's pictures and tours are made, and how
the versions and releases fit together. How every app is built, and how to add one:
[Architecture and consistency](architecture.md). The development apps, from Nexus Dashboard to Nexus Deps:
[Dashboard](dashboard.md). How a release is made and published: [Releases](releases.md) and, step by step,
[Portal](../portal.md#appstoml-and-releases). The repository's settings on GitHub and Dependabot's pull requests:
[GitHub settings](github-settings.md). The tools a machine needs to work on it, on Bazzite or Windows, and how they
stay up to date: [The development machine](https://robertotorino.github.io/nexus/machine/) on the Nexus page.

## Layout

The repository is the suite. Paths in this wiki are written from the root of the repository.

```
portal/                       the portal: app, apps.toml (the pinned app releases), its tests and install.sh
apps/<name>/                  one folder per app, each with its own VERSION, CHANGELOG, LICENSE and .gitignore
core/bc250_core/              the shared Python package the apps bundle at release time (see bc250_core below)
tools/                        release and CI (build_release, stage_app, check_versions, check_manifest, pin_app,
                              tag-release.sh, ci_state, ci_matrix, check-release.sh, ci-local.sh, pre-push.sh,
                              git-setup.sh), new_app, sync_icons (the category icons), check_upstream, the
                              screenshot and tour scripts, mkdocs/ (the wiki's hooks and design panel), tests/
                              and installer-tests/
dev/<name>/                   the development apps, run from the checkout and never released: dev/dash/ is Nexus
                              Dashboard (the door to the others), dev/nrt/ Nexus Release Tool, dev/demo/ Nexus
                              Demo Recorder, dev/itests/ Nexus Installer Tests, dev/sounds/ Nexus Sound Lab,
                              dev/deps/ Nexus Deps
docs/ mkdocs.yml              this wiki (MkDocs Material)
icons/                        the category icons
DESIGN.md design/colors/      every color of the suite and its samples (tools/make_design.py writes them)
install.sh                    the portal's installer for a checkout
test.sh                       runs every test folder (core, tools, dev/, the portal and the apps)
SYSTEM                        the system the suite is made for: bazzite
.github/workflows/            ci.yml (every check), release.yml (a release), docs.yml (the wiki on GitHub Pages),
                              upstream.yml (the weekly upstream check)
```

## Set up and test

```bash
# Linux
python3 -m venv .venv-linux && .venv-linux/bin/python -m pip install -r requirements-dev.txt
# Windows (Git Bash)
py -m venv .venv-windows && .venv-windows/Scripts/python.exe -m pip install -r requirements-dev.txt

./test.sh                                   # every test folder, offscreen; picks this OS's venv
NEXUS_SYSTEM=bazzite ./test.sh              # the portal's and the apps' tests too, on Windows
python3 tools/check_versions.py             # hard-coded versions = VERSION
mkdocs build --strict                       # the wiki
```

The suite is worked on and tested on Bazzite: `./test.sh` runs the portal's and the apps' tests on Linux, and core,
tools and `dev/` on both systems.

### CI on your own machine

GitHub runs `ci.yml` on every push and pull request: the versions and the portal's manifest, the pytest matrix
(core, tools, every `dev/` app, the portal and every app), the native Rust job for PS Remote Play, the shell checks
(`bash -n`, shellcheck, line endings, exec bits, the four files of every folder, workflows only at the root), the
installer tests, the wiki build and the Windows `.exe` of SFTP Tools. A release waits for it: a commit CI did not
pass gets no release.

The matrices are read from the folders in a first job, `plan` (`tools/ci_matrix.py`): the pytest matrix is every
folder with `tests/`. The installers job runs every `tools/installer-tests/*.sh` it finds. So a new app needs no
edit to a workflow: its folder, its installer test and its `install.sh` are in CI at once.

`./test.sh` runs every test folder in one venv that holds everything, on whatever Python your system has. GitHub's
CI runs each job on Python 3.12 with only that job's own requirements, so a test can pass here and still fail there:
a Python 3.13 function, or a package only the full venv has. `tools/ci-local.sh` runs the jobs of `ci.yml` the way
GitHub does, in a container (podman, which Bazzite has, or docker):

```bash
tools/ci-local.sh                            # every job, a minute or two once the image is built
tools/ci-local.sh shell pytest/tools         # some jobs; a matrix job by its value, pytest for all of them
tools/ci-local.sh --list                     # the jobs
```

It reads the jobs from the workflow itself, a matrix from the folders as the plan job does, so a new app needs no
change. The first run builds the image from `tools/ci-local/Containerfile` (Python 3.12 and the packages GitHub's
runner has) and PS Remote Play's FFmpeg; both are kept, with the venvs and the logs, in `~/.cache/bc250-ci-local`.
It works on a copy of the checkout with every change staged, as the commit will have it. Only the Windows job does
not run here. The push commands Nexus Release Tool shows run it first (`tools/ci-local.sh && git push`): no push
when a job fails.

On Windows it runs in podman's machine, a small Fedora in WSL that reaches the checkout under `/mnt/c`. Install
podman once (`winget install RedHat.Podman`, then `podman machine init` and `podman machine start`), and run it
from Git Bash as the machine's own user, not root: the installers refuse root.

```bash
podman machine ssh "su - user -c 'cd /mnt/c/Projects/bc250-bazzite && bash tools/ci-local.sh'"   # your checkout's folder
```

`tools/pre-push.sh` runs CI's quick checks in a few seconds: the versions, `portal/apps.toml` with the portal bump
it needs against what the remote has, the scripts' exec bits and the line endings. The checks read the commit that
is pushed, in a checkout of it of their own (a few seconds more), as CI does: a fix that is in the working tree but
not committed never lets a push through. `tools/git-setup.sh`, once per checkout, makes it git's pre-push hook
(`core.hooksPath`):

```bash
tools/git-setup.sh                      # once per checkout: the hook
BC250_PRE_PUSH=full git push            # also every CI job (tools/ci-local.sh)
```

Nexus Release Tool's **git pull** runs `tools/git-setup.sh` first, so a checkout it pulls in is set up.

When the hook stops a push, CI would fail on the same commit: fix it, commit, and push again. Pushing past it with
`git push --no-verify` sends the failure to GitHub, and the release waits until a new push passes CI.

When the remote has commits this checkout lacks, pushed from the other machine, the hook says so and stops before
the checks: run `git pull --rebase`, then push again.

### Working from both Linux and Windows

The repository is used from both systems, so it is set up to behave the same on each:

- **Line endings:** `.gitattributes` makes every text file LF in the repository and in the working tree on both
  systems, regardless of `core.autocrlf` (Git for Windows sets it to `true`). Scripts, units and `.desktop` files
  reach the board with LF, and moving between systems never shows files as changed. CI rejects CRLF.
- **Executable bit:** Git for Windows runs with `core.fileMode=false` and records new files as not executable. After
  `git add` and before committing, run `tools/fix-modes.sh`: it marks every `.sh` as executable in the index (this
  works the same on both systems). CI fails when a script is missing the bit.
- **Venvs:** a venv only runs on the OS that created it, so keep one per system (`.venv-linux/`, `.venv-windows/`).
  Both are ignored by git.
- **Tests:** some app tests use Linux-only calls (`os.getuid`, file modes) and fail on Windows; Linux and CI are
  the reference. Core's tests run on both and never write to the Windows registry.
- **File names:** Linux is case-sensitive and Windows is not, so a link or path whose case only matches on Windows
  breaks on Linux and on GitHub. Keep links and asset names in exactly the case of the file.

## Colors

[DESIGN.md](https://github.com/RobertoTorino/bc250-bazzite/blob/main/DESIGN.md) lists every color of the suite: the
rules that make its design recognizable, every tint of each hue and why it is there, and where each color is used
(the apps' themes and state colors, the wiki, the development apps, the apps' own colors). Each color shows a sample
from `design/colors/`. Both are written by `tools/make_design.py` from the listing in it: change the listing and run
it, never DESIGN.md itself.

```bash
python3 tools/make_design.py            # write DESIGN.md and its samples
python3 tools/make_design.py --check    # only say what is out of date (tools/tests runs it)
```

The check also compares the wiki's stylesheet, `docs/stylesheets/suite.css`, with its listing: a color added to the
stylesheet goes into the listing too, with what it is for.

## The wiki's pictures and tours

To preview the wiki locally, run `mkdocs serve` from the repository root with the development venv active,
then open <http://127.0.0.1:8000/bc250-bazzite/>. Stop the server with Ctrl+C.

The picture of the portal on the home page (`docs/images/home/portal.webp`) is taken from the portal itself:
`tools/portal_screenshot.py` opens its window offscreen on this checkout's `apps.toml` and icons, in a home folder
of its own, with a fixed demo state (one update, the Sustainable tab open), and saves it. The wiki's workflow runs it
before every build, so the published picture always shows the portal as it is on main. Run it yourself to see the
same picture in `mkdocs serve`:

```bash
python tools/portal_screenshot.py          # from the venv; --out FILE to save it elsewhere
```

The video tours are made the same way, frame by frame from the real windows, offscreen, from a terminal as below
or from [Nexus Dashboard](dashboard.md#video-tours). `tools/record-tour.sh`
records the portal's tour, about two minutes, with music under it that fades out over the last two seconds
(`tools/sounds/the_quiet_engine_remix.ogg`, made with generative AI tools; `--no-music` leaves it out).
`tools/record-tour.sh --wiki` also writes the copy on the [Portal Tour](../portal-tour.md) page,
`docs/videos/portal-tour.mp4` (1280 × 720, about 6 MB) and its poster, and a fingerprint of the portal it was recorded from
(`tools/portal-tour.stamp`: the portal's code and pictures, and the tour's script). The checks fail when
the portal changed since, until the tour is recorded again with `--wiki`;
`python3 tools/portal_tour.py --check` says so from a terminal, and `--stamp` marks the video as current
for a change that does not show in it. A change the wiki describes goes into its [Portal](../portal.md) page in the
same change.
The video itself goes to `~/Videos`, outside the repository, at 1920 × 1080. For YouTube, record it at 4K:
`--size 2160p` renders the same tour at 3840 × 2160 (the window drawn at 240 % instead of 120 %, so the text stays
crisp; about three minutes, around 35 MB) into `~/Videos/bc250-portal-tour-v<portal version>-2160p.mp4`.
YouTube shows a 4K upload far sharper than a 1080p one, since it gives it a better codec and more bits. `--size
1440p` is the step between. The wiki's copy is the same whatever the size.
`tools/record-app-tour.sh` records one app's, about 40 seconds, the same script for every app, with music under it
that fades out over the last two seconds (`tools/sounds/the_quiet_engine.mp3`, made with generative AI tools):

```bash
tools/record-app-tour.sh fan                          # ~/Videos/bc250-fan-tour-v<version>.mp4
tools/record-app-tour.sh compute --package cu_unlock  # compute and cores have two programs
tools/record-app-tour.sh cec cec.mp4 --seconds 30     # another file, another length
tools/record-app-tour.sh fan --no-music               # without sound; --music FILE for another track
tools/record-app-tour.sh fan --size 2160p             # at 4K for YouTube: ...-tour-v<version>-2160p.mp4
```

The app starts from the checkout in a home folder of its own. The tour points at the controls of its header, with
their tooltips as captions, and opens its tabs or pages; it presses no buttons and nothing runs as root. What the
app reads from the board is real, so watch the video before you publish it.

The controller beside the board on the home page changes with every portal release, in the order of
`docs/images/home/controllers/controllers.toml`. To add one, put its picture in that folder (WebP, 1295 × 1600, with
a transparent background, like the others) and add it at the end of the list with its alt text.

## Where things are installed

- **Root-owned `/opt`:** the portal (`/opt/bc250-bazzite-suite`), Bazzite Test (`check`), cores, oc and
  acpi, whose scripts run as root: a normal user cannot change code that sudo runs.
- **Your home folder:** the shared venv `~/.local/share/bc250-bazzite-suite/venv` (PyQt6, used by all suite
  GUIs and removed with the last of them), plus each app's settings, results and launchers.
- **`bc250_core` per app:** each app's release carries the `bc250_core` it was tested with, next to its own code.
  Apps with different release tags never share a core version they were not tested with.

[Portal](../portal.md#install) has the full table.

## Versions and tags

`core/`, `portal/` and every app have a `VERSION` file; it is the single source of the version. Versions that are
also written in a script or package (`VERSION="…"`, `__version__ = "…"`, pyproject `version`) must match it, which
CI checks with `tools/check_versions.py`. Everything started at 0.1.0 with the suite.

Each app is released on its own tag (`bc250-check-v0.1.0`, `bc250-gpu-v0.4.0`, …); the release workflow builds
`<tag>.tar.gz` and `SHA256SUMS`. The portal has `bc250-portal-vX.Y.Z` and pins one release of every app in
`portal/apps.toml`; a change there since the last portal release needs a portal version bump at least as large as the largest app bump.
The release steps are in [Portal](../portal.md#appstoml-and-releases).

How the releases are titled on GitHub, and why its **Latest** release is always the newest portal:
[The releases on GitHub](releases.md#the-releases-on-github).

### Upstream releases an app pins or follows

`tools/check_upstream.py` compares what the apps pin or follow with their upstreams, each described
below. It exits with 0 when every one is in step, 1 when one moved and 2 when one could not be checked. The Upstream workflow (`.github/workflows/upstream.yml`) runs it every Monday and can be started by
hand. What moved goes into the open **Upstream review** issue (a new one when none is open, else its list is
updated with a comment), which notifies everyone who watches the repository. The workflow never closes it: close
it once every item on it is handled on `main`, else next Monday's run opens it again. **Close issues** in [Nexus
Dashboard](dashboard.md#close-issues) does it, or a command with a gh login:

```bash
gh issue list                                                  # the open issues, with their numbers
gh issue close <number> --comment "PPSSPP pinned at 1.20."     # close one, saying how it was handled
```

The run fails only when an upstream could not be checked. A moved pin means a new version of the app is due, with
the new pin tried on the board first. It also moves Nexus Deps' list of the programs the apps use: run
`dev/deps/run.sh --sync-upstreams` from the repository's root, else CI fails
([Nexus Deps](dashboard.md#deps)).

The shadPS4 Manager installs one shadPS4 release, pinned in `apps/shadps4/shadps4_manager/emulator.py`
(`VERSION`, `TAG`, `ASSET`, `SHA256`). The tool checks it: a newer stable release, with the Linux zip and the
SHA-256 GitHub publishes for it that a new pin needs, and the SHA-256 of the pinned zip. A new shadPS4 can change
what the app relies on (its `config.json`, the shadNet protocol), so a new pin also needs a look at what changed.

The PPSSPP, PCSX2 (its stable channel) and RPCS3 Managers and Mesh Shaders each pin one release: `VERSION` or
`LANDMARK` in the app's `emulator.py`, and `DIRECTMESH` in `apps/mesh/bc250-mesh-shaders.sh`. RPCS3's `emulator.py`
also holds the size of the pinned AppImage (`SIZE`), by which the app sees that RPCS3 replaced itself with another
build, so a new pin moves it too.
The same tool reports a newer stable release than the pin (for DirectMesh the newest `directmesh-v<version>` tag; a tag
with more after the version is a development candidate and skipped); the apps check the checksum of what they download
themselves. The governor has no pin in the repository (its version is the one COPR built); the GPU Manager
compares the installed package with filippor's latest release.

The BC-250 Upscaler Manager pins no HelixSR release: it gets the latest of one major version (`SUPPORTED_MAJOR`), or the
fallback HelixSR's developer names. Its `apps/upscaler/upscaler/acquire.py` holds `SUPPORTED_MAJOR`,
`KNOWN_VERSION`, the newest release the app was checked against, and `FALLBACK_VERSION`. The same tool reports a newer
stable release (users get it at once, so what changed in its setup, its zip and `helixsr.ini` needs a look and a try
on the board; then `KNOWN_VERSION` moves), a newer major version (users do not get it until the app is moved to it), a fallback
named in the latest release's notes that is not `FALLBACK_VERSION`, and a fallback release without its zip.

The Vita3K Manager installs one Vita3K build, pinned in `apps/vita3k/vita3k_manager/emulator.py`
(`BUILD`, `SEMVER`, `COMMIT`, `SHA256`, `SIZE`). Vita3K has no stable releases: every change is a build, kept as a
release of `Vita3K/Vita3K-builds` tagged with its number, with `Vita3K-x86_64.AppImage` and the SHA-256 GitHub
publishes for it. Builds come almost daily; the tool reports the newest build when it is past the pin (with how many
builds later), and a pinned AppImage that is gone from GitHub or was replaced. The app itself already tells its users
when a newer build is out, so a report is a reminder, not a fault: move the pin when a build is worth trying. A new pin takes the asset's digest and size from that release, and a look at what the app relies on in
Vita3K's source at the new build:

- the command line (`vita3k/config/src/config.cpp`): `-r <title ID>`, `--frontend sdl`, `--firmware`,
  `--pkg` with `--zrif`, and a `.vpk`, `.zip` or folder as the positional argument;
- the folders (`vita3k/app/src/app_init.cpp`, `init_paths`): settings in `$XDG_CONFIG_HOME/Vita3K/config.yml`, the
  storage in `$XDG_DATA_HOME/Vita3K/Vita3K` unless `pref-path` in config.yml moves it, games in its `ux0/app`;
- the firmware's three parts (`vita3k/app/src/app.cpp`, `get_firmware_state`): `vs0`, `sa0` and `pd0` counted as
  installed when they hold anything;
- the SDL frontend (`vita3k/sdl-frontend`): it runs the game given by `-r` and quits with it, and has no full screen
  of its own. `--fullscreen` is not used: Vita3K writes it into config.yml as `boot-apps-full-screen`;
- the AppImage's self-updater (`bin/10-self-updater.hook` in the AppImage): it overwrites the AppImage with the
  newest continuous build unless `DISABLE_AUTO_UPDATES=1`, which the run wrapper sets. `vita3k --version` on the new
  AppImage confirms the build and commit.

The tests hold the `config.yml` the pinned build writes on its first start (`tests/fixtures/config-4186.yml`); a new
pin replaces it with the new build's, renamed for it.

The Xenia Manager installs one Xenia Canary build, pinned in `apps/xenia/xenia_manager/emulator.py` (`BUILD`,
`COMMIT`, `PUBLISHED`, `SHA256`, `SIZE`). Xenia has no stable releases either: every change is a release of
`xenia-canary/xenia-canary`, tagged with its commit, with `xenia_canary_linux.AppImage` and the SHA-256 GitHub
publishes for it. A tag is no number, so the app and the tool take a release published after `PUBLISHED` as a newer
build; the tool also reports a pinned AppImage that is gone or replaced, as for Vita3K. A new pin takes the asset's digest and size and the release's date, and a look at what the
app relies on in Xenia's source at the new commit: the `--fullscreen` option and the positional path
(`src/xenia/app/xenia_main.cc`), the storage root in `$XDG_DATA_HOME/Xenia` (the same file, and `GetUserFolder` in
`src/xenia/base/filesystem_posix.cc`), the places of the game partition in a disc image
(`src/xenia/vfs/devices/disc_image_device.cc`, which `GAME_PARTITIONS` in the app's `games.py` copies), and GTK on
X11 (`GDK_BACKEND` in `src/xenia/ui/windowed_app_main_posix.cc`).

BC-250 USB Wi-Fi builds its driver from one pinned commit per branch of `shenmintao/aic8800d80` (`main` and
`legacy-mcu1`), `PINS` in `apps/wdriver/usb_wifidriver/builder.py`, fetched from the suite owner's
mirror first and from the upstream when the mirror does not answer. The tool reports a branch with commits after its
pin (how many, the newest and the compare page), and a mirror that is not on GitHub or lacks a pinned commit. A new
pin is built on the board against the running kernel and tried with the stick, on the branch for its chip.

BC-250 Mesh Shaders builds RADV from one Mesa release (`MESA_VER` in `apps/mesh/bc250-mesh-shaders.sh`,
with DirectMesh's patch and the suite's patch for that release in `apps/mesh/mesa/`); BC-250 ACE Queues builds it from
the system's Mesa with one patch (`apps/ace/mesa/gfx1013-ace-queue.patch`). The tool takes Mesa's newest release from
its tags on GitLab (a release candidate is none), reports it when it is newer than `MESA_VER`, and tries the ACE patch
on it (`patch -p1 --dry-run` on the files the patch touches, fetched at that release): a patch that no longer applies
stops ACE Queues building once Bazzite ships that Mesa. A new Mesh Shaders pin needs DirectMesh's patch for the new
release and the suite's patch moved to it.

BC-250 PS Remote Play builds FFmpeg from one release (`FFMPEG_VERSION`, `FFMPEG_SHA256` in
`apps/consoles/native/ffmpeg/build.sh`) and takes libva's headers from one release where the system has
none (`LIBVA_VERSION`, `LIBVA_SHA256`). The tool reads FFmpeg's release tags (`n<version>` on its GitHub mirror) and
libva's latest release, and reports a newer FFmpeg on the pinned branch (its fixes), a newer FFmpeg branch (a bigger
move: the decoder calls of the native core) and a newer libva (its headers only; the libraries stay the system's).

USB HD Cam downloads each camera's firmware from one commit of a GitHub repository (`PINNED` in
`apps/hdcam/usb_hdcam/firmware.py`). The tool downloads the file at that commit, which must still have
the pinned SHA-256, and the same file on the repository's default branch: changed or gone there is reported.

BC-250 Bazzite Test runs whichever speedtest CLI is installed; its development tool installs one release of Ookla's
(`SPEEDTEST_VERSION` in `apps/check/development/tools/install-requirements.sh`). Ookla publishes no API;
the tool reads the version from Ookla's Homebrew formula.

```bash
python3 tools/check_upstream.py            # all of them
python3 tools/check_upstream.py helixsr    # one: shadps4, helixsr, ppsspp, pcsx2, rpcs3, directmesh,
                                                          # vita3k, xenia, wdriver, mesa, ffmpeg, hdcam or speedtest
```

## bc250_core

Code shared by the suite's apps (`core/`). Nothing in it imports an app: each app passes its constants in as an `AppInfo`.

| Module | What it holds | Merged from |
|---|---|---|
| `appinfo` | `AppInfo` (id, name, version, logo, tag prefix, settings names) | new |
| `theme` | The suite's theme (`THEMES`, `theme_name()`, `save_theme_name()`, `apply_theme()`, `surface_style()`, `muted()`), `STATE_COLORS`, bundled Inter font, `header_font()`, `HOVER_STYLESHEET`; self-contained, so an app not on core carries a copy | all six GUIs |
| `text` | `fmt()` (`%1` placeholders), `fill()` (`{name}` placeholders), `plain_tooltip()`, `window_title()` | governor, upscaler |
| `widgets` | `AppHeader` (the window header), `StatusPill`, `MetricBox`, `Pill` (a `MetricBox` that is a button), `same_width()`, `ClickableLogo`, `Terminal`, `TextDialog`, `RoundedToolTip`, `show_tooltip()`, `page_header()`, `hint_label()`, `accent_button()`, `set_button_active()` | governor + helixsr's Wayland tooltip + bazzite-test's manual tooltips |
| `app` | `create_app()` / `run_app()` / `exec_app()`: names, Fusion with the theme, tooltip, icon, SIGTERM | the apps' `__main__` |
| `exit_keys` | `install(app)`: Escape and a controller's B close the app's window, after a key the window takes for itself and through its `closeEvent`; B, read with pygame-ce, is Escape for what has the focus, and only for the app that has had the focus for a moment; `install(app, controller=False)` for Escape alone, the class attribute `exit_keys = False` for a window that keeps every key. Self-contained, so an app not on core carries a copy | new |
| `action_tab` | `ActionTab`: the last tab of a `QTabWidget` as a button (Start game in the game managers): a click acts and the open page stays open | new |
| `settings` | `open_settings(info)` at each app's existing file, geometry helpers, `SettingsStore` (typed defaults) | bazzite-test's `AppSettings` |
| `help` | `HelpView` (the content stays in the app) | upscaler |
| `updates` | `latest_release()` (with a tag prefix for the per-app tags: GitHub's release pages, newest first, are followed until one holds the prefix, since other releases can fill the first page), `UpdateStatus`, `UpdateChecker` (any job, off the GUI thread) | upscaler + governor |
| `platform` | XDG folders, `xdg_open()`, `launch_in_terminal()` (with an exit file the caller can watch); for Windows (the development apps, SFTP Tools' `.exe`), `open_path()` and a PowerShell window; `private()`, a path or a text with the user's folders as `%LOCALAPPDATA%`, `%APPDATA%` and `%USERPROFILE%` (`~` on Linux), never the user's name, which `applog.setup(private=True)` applies to every line of a log; `outside_bundle()` and `start_program()`: a program a PyInstaller-built app starts without the app's own DLL directory and PATH, which it would otherwise inherit | the bisect GUIs' `terminal.py` |
| `steam` | Steam's folders and users, `installed()`, `with_steam_closed()`, `shortcuts.vdf` and the shortcuts' artwork in `grid/`, `shortcut_number()` and `play_url()` (a shortcut's number in Steam's file, and the address that starts it) (standard library only) | consoles |
| `steam_art` | `draw_icon_art()`: a shortcut's four pictures drawn from an app's icon, in the icon's color | consoles |
| `upstream` | `publish()` / `read_all()`: the updates outside the suite an app can install now, for the portal's notice (standard library only; HelixSR carries a copy) | new: helixsr, pcsx2, portal |
| `sensors` | `Sensors.read()`: the board's live values from `/proc` and `/sys` without root (CPU, GPU, the governor's range, VRAM, RAM, temperatures, network, disk, fans), `Reading`, `Fan` | System Overlay; used by USB IPS3.5 too |
| `wifi` | The Wi-Fi adapters and whether the running kernel has a driver and firmware for them, `report()` (standard library only; `python3 -m bc250_core.wifi`) | new: check's test 53, wdriver |

Core is **bundled per app**: `tools/stage_app.py` copies `bc250_core/` next to the package of every app that
imports it, so each release runs on the core it was tested with.

### Tests

```bash
cd core && QT_QPA_PLATFORM=offscreen python -m pytest -q tests
```

`tests/test_parity.py` renders core's widgets next to the copies in `apps/gpu` and `apps/upscaler` and requires
identical pixels; a case is skipped once its app no longer has its own copy.
