<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# CLAUDE.md (BC250 Bazzite Suite)

The rules of the **BC250 Bazzite Suite** (exactly that name): tools for the AMD BC-250 on Bazzite. The repository is
`github.com/RobertoTorino/bc250-bazzite` (branch `main`). The owner works on it from Bazzite (the BC-250 board is the
development machine); the development tools run on Linux only (owner, 15-11-2026). This file, not a local memory,
carries the standing rules, and the owner may change them when the need is there.

**It is standalone** (owner, 14-11-2026: "identical to bazzite-console", one repository per suite). Everything it
needs is in this repository: its tools, its core and its development apps. Nothing here depends on a checkout of
Nexus (`github.com/RobertoTorino/nexus`) or of another suite, and nothing is taken from one at run, test or release
time. The suite was the folder `bc250-bazzite/` of Nexus until 14-11-2026, with its tags, releases and wiki there;
the tooling began as a copy of Nexus's and is this repository's own now: a change to it is made here.

**Twin of the Bazzite Console Suite** (owner, 15-11-2026: "basically identical, the only difference is that one runs on
a bc250 board and the other runs on a PlayStation 5 board"). This suite and the Bazzite Console Suite
(`github.com/RobertoTorino/bazzite-console`, checked out beside this one) share their release logic (NRT, `tools/`, the
workflows, CI), design features, category icons and the apps' design: these stay equal. A change to any of them is made
in both repositories in the same piece of work, with each one's CHANGELOG and wiki; only what the hardware makes
different differs (names, `TAG_PREFIX`, the board's apps and checks). Standalone still holds: neither reads the other at
run, test or release time. The handover names what changed in each.

## Rules from the owner

- **Never commit, tag or push.** The owner does every git commit, tag and push. Finish work in the working tree and
  say what is ready; don't offer to commit.
- **NRT handles the releases** (owner, 15-11-2026). Nexus Release Tool works out each version from the CHANGELOG
  entries since the last tag (`Breaking.` major, `Added.` minor, `Fixed.` patch), bumps the `VERSION`s, pins the
  portal's `apps.toml` and starts the release; the owner runs it. Claude never bumps a `VERSION`, tags, builds or
  publishes release assets, pins a release in `portal/apps.toml` or writes the release entries in the CHANGELOGs, and
  doesn't offer to. When finished work will need a release, the handover says which app and why. Claude may change
  the release tools and their tests.
- **READMEs and the wiki hold no status, plans, step numbers or decision notes.** No placeholder folders that only
  describe future work. CHANGELOG entries are history and may mention steps.
- **The wiki keeps up with the work** (owner, 28-10-2026): new information, a new way of working or new logic worth
  knowing goes into its chapter of the wiki in the same change as the code, as a CHANGELOG entry does: what it does
  and how to use it, written for the person using it, never status or plans. The handover names the chapters it
  changed.
- **CHANGELOG for every change:** the root CHANGELOG for suite-wide changes, the app's (or core's, the portal's, a
  dev app's) for its own. Format: a `Changelog: DD-MM-YYYY HH:MM:SS` line, a blank line, then plain sentences; newest
  first. The time is Europe/Amsterdam (CET/CEST), whatever the machine's own zone:
  `python3 -c "import datetime, zoneinfo; print(datetime.datetime.now(zoneinfo.ZoneInfo('Europe/Amsterdam')).strftime('%d-%m-%Y %H:%M:%S'))"`.
- **Every entry starts with its kind** (owner, 15-10-2026): `Breaking.` (removed, or no longer working as before:
  major), `Added.` (a new feature: minor) or `Fixed.` (a bug or security fix: patch); 0.x apps too. NRT takes
  the number from them.
- **VERSION is the single source** of each app's version. Copies in code (`__version__`, shell `VERSION=`,
  pyproject, Cargo) must match: `tools/check_versions.py`.
- **Every folder that was a repository once** (each app, `core/`, `portal/`) keeps LICENSE, .gitignore, VERSION and
  CHANGELOG; each `dev/` app keeps LICENSE, .gitignore and CHANGELOG, and has no VERSION (owner, 15-11-2026: a
  development app is never released; its header shows the checkout's commit and its time, as NRT's does). GitHub
  workflows live only in the root `.github/`.
- **An info symbol where space is limited** (owner, 01-11-2026): a window never carries long lines of explanation.
  Where a line of hint text would take the room, a small round "i" (core's `InfoButton`) opens the text on a click,
  with its links; a short line under a control stays a `hint_label`.
- **Open by default.** Everything about the suite may be public: code, plans, issues, test data and recordings from
  the boards. Only personal data stays out (names, addresses, host and user names, serial numbers, MAC and IP
  addresses, keys, account details), as the apps mask it in their logs. When in doubt whether something is personal,
  ask.
- **Ask** before decisions that are the owner's (what an app does, repo layout, anything on the
  board). Do the obvious housekeeping without asking.
- **Warn before board changes.** Apps that change how the board runs (CU/core unlocks, GPU governor, GPU
  overclocking, ACPI override, the patched RADV of ace, the DirectMesh RADV of mesh, the VRAM split of vram, the
  thermal guard of fan, the kernel module of wifi) are marked `changes_board` and the portal asks first. Frame it
  as standard caution: the apps are software-only and reversible, not "risky". Every such app says what it changes
  (owner, 03-11-2026): its `board_change` in `portal/apps.toml`, a few plain sentences on what it touches, what
  stays after a reboot or a power off, what it never touches (the BIOS, the firmware) and how it is undone, written
  from the code, not from the README. The tile's tooltip shows it under "Changes the board", and the app's wiki
  chapter opens with the same text, word for word, in a `!!! warning "Changes the board"` box right after its
  title; `tools/check_manifest.py` compares the two (the word Disclaimer stays the wikis' liability notice).
- **Advice, not reboots.** No app reboots, powers off or logs out the board; when one is needed, the app says so
  (and which command does it). The exception, by design (owner, 15-10-2026): CU Bisect and Cores Bisect, whose
  rounds each need a fresh boot (they ask, or reboot by themselves with `--auto`), and Cores Unlock's boot service,
  which reboots warm once after a cold boot so the cores come up. A second exception (owner, 16-10-2026): the
  thermal guard shuts the board down cleanly at a critical temperature, to protect the hardware; the limits are
  the owner's. A new reboot anywhere else is the owner's decision.
- **The current releases are the baseline.** They were tested extensively on two boards. Moving code must not
  change behavior; a finding in existing code is "a code path to check", not a known failure. Prove "unchanged"
  (diffs, pixel comparisons, the installer tests) rather than assume it.
- **Not limited to the owner's setup.** The owner's board, TV, cable and settings are one case, not the target:
  apps read what the hardware reports and offer every option it supports (a CEC 2.0 TV, another display mode,
  a second adapter), and say so where an option does not apply, rather than leaving out what the owner's setup
  lacks. Recorded data from the owner's board makes good test fixtures; tests also cover other setups.
- **Consistent architecture.** Every app is built the same way, so one that works is the pattern for the next:
  - Layout: `apps/<name>/` holds its Python package(s) directly (`<package>/__main__.py`, no wrapper folder),
    `<name>` a short name and `<package>` the app's name without its BC-250 or Bazzite prefix
    (`apps/ace/ace_queues/`, `apps/datstation/datstation/`; owner, 17-10-2026; a renamed app's old key goes in
    `RENAMED` in the portal's manifest.py),
    `images/`, `tests/`, `install.sh` and the four files; data the package reads (a catalog, tables) sits in
    the package or beside it in the app folder. `tools/tests/test_layout.py` checks the layout.
    An app's icons are copies of its category's icon: `icons/categories.toml` assigns them, `tools/sync_icons.py`
    writes them.
  - Code: shared code comes from `bc250_core` (bundled per app); the installer writes a launcher in
    `~/.local/bin` whose exec line names the app's python, a menu entry and an optional Desktop icon; every app has
    its installer test (`tools/installer-tests/<name>.sh`).
  - Window: the first line is the app's icon at 96 px on the left, spanning the title (with the version) and a
    second line below it (status boxes or the app's main controls). No long lines of text in the window (owner,
    01-11-2026): where space is limited, an info symbol (core's `InfoButton`) opens the explanation; what is
    applied already cannot be applied again (its Apply is off).
  A new app copies the structure of an existing one; any deviation is the owner's decision. The manual's
  [Architecture and consistency](docs/development/architecture.md) describes it all, with the steps for a new app.
- **The Bazzite design** (owner, 25-10-2026: a design per system): this suite keeps the Bazzite design (purple, the
  apps' theme and the wiki's). Never carry another system's design over to it, nor its design to another system.
- **Scope is the suite, not Bazzite.** We answer for the portal and its apps, not for Bazzite itself. A system-wide
  Bazzite package is in scope only where one of our apps uses it (Nexus Deps lists it then); its updates and
  security fixes are Bazzite's. Our own code, and the Python packages in our apps' environments, are ours. One
  exception (owner, 15-10-2026): Nexus Deps shows Bazzite's update state (the running image, an update waiting for
  a reboot, uupd's last run). Since 09-11-2026 (owner) it shows every update of the machine (Bazzite's image,
  Flatpaks, Homebrew, Rust, the development venv), installs them with a card's Update after it asks, and reminds
  hourly; uupd still installs them nightly by itself.
  Its Fix (owner, 07-11-2026) installs what an installed app needs and lacks, after it lists the commands and asks:
  Python packages with pip, a missing tool with Homebrew, else layered with rpm-ostree (active after a restart,
  which it advises and never does).
- **chiaki-ng is named only where licensing needs it:** PS Remote Play's LICENSE, the License sections of its README
  and manual chapter, the suite's license overview (README, docs/index.md) and this file. Everywhere else (code,
  comments, tests, vectors, log messages, the manual, CHANGELOGs) it is "the reference" (the reference
  implementation); user-facing text does not mention it at all.
- **KROU4's PS5CameraDriver is never named** (owner, 23-10-2026), only in this file: not in code, comments, tests,
  the wiki or CHANGELOGs. Where its tried firmware patch matters, it is "another project's firmware
  patch".

## What this is

A **portal** installs and starts the apps listed in its manifest. **check** (BC-250 Board Test) is always
installed and always listed first; every other listed app is an optional tile. The release tags are
`bc250-<app>-v<x.y.z>` and `bc250-portal-v<x.y.z>` (`TAG_PREFIX`, owner 15-11-2026; the releases made in Nexus had
no prefix). The app ids, the launchers and the suite's folder on the board (`~/.local/share/bc250-bazzite-suite/`)
stayed the same through the moves. The wiki is at robertotorino.github.io/bc250-bazzite/. The suite's system is
`bazzite` (`SYSTEM`).

Every app has a `category` in `portal/apps.toml`, the same as its icon's in `icons/categories.toml` (sustainable,
graphics, gaming, utilities): the portal, one fullscreen view for the keyboard, the mouse and a controller (owner,
01-11-2026), shows a category strip with the notice of updates beside it and check as the first tile on Sustainable
(owner, 20-10-2026). There is no Development category (owner, 27-10-2026): the portal lists only released apps.

## Layout

The repository is the suite, and the tools know only this one (`tools/suites.py`):

- `portal/`: the portal (`bc250_portal`), `apps.toml` (one pinned release per app), its tests and `install.sh`.
  It installs as a copy in the home folder (owner, 15-11-2026): the program in
  `~/.local/share/bc250-bazzite-suite/portal`, what it remembers in `.../state`; no `/opt`, no sudo for the portal.
  Installed from a checkout, it installs the apps from that checkout.
- `apps/<name>/`: check, gpu, upscaler, compute, cores, oc, acpi, overlay, turing, webcam, controller, bios, ace, mesh,
  vram, fan, wifi, cec, sftp, consoles, clb, shadps4, rpcs3, ppsspp, pcsx2, vita3k, xenia, datstation, ssd, btpair.
  Each has its own VERSION, CHANGELOG, LICENSE (acpi is MIT; consoles is AGPL-3.0, its protocol code ported from
  chiaki-ng: those files AGPL-3.0-only, its own AGPL-3.0-or-later; clb (BC-250 XB Remote Play, XBOX) is
  GPL-3.0-or-later with protocol code ported from Greenlight and xal-node, MIT, whose notice its README keeps; the
  rest GPL-3.0-or-later), .gitignore.
- `core/bc250_core/` with `core/VERSION`: the shared Python code, **bundled per app** at release time
  (`tools/stage_app.py`), so each app runs on the core it was tested with; the shared venv
  `~/.local/share/bc250-bazzite-suite/venv` holds only PyQt6 and pygame-ce (the portal's controller reader). In a
  checkout an app's `install.sh` and its tests find core at `../../core` from the app folder. Core's `nexus.py`
  is the design of the development apps (the theme `NEXUS`) and their header (`header()`: the checkout's commit and
  its time, `checkout_stamp()`).
- `tools/`: the release and check tools (`build_release.py`, `stage_app.py`, `check_versions.py`,
  `check_manifest.py`, `pin_app.py`, `suite_release.py`, `publish_release.sh`, `tag-release.sh`, `release_commit.py`,
  `ci_state.py`, `ci_matrix.py`, `check-release.sh`: the board checks of a portal release), CI on this machine
  (`ci-local.sh`, `ci_local.py`, `ci-local/`, `ci-qt-libs.sh`), `suites.py`, `sync_icons.py`, `new_app.py`,
  `check_upstream.py`, `fix-modes.sh`, `nrt.sh`, the tours
  (`portal_tour.py`, `app_tour.py`, `tour_frames.py`, `record-tour.sh`, `record-app-tour.sh`, their music in
  `sounds/`), `portal_screenshot.py`, `make_portal_sounds.py`, `apply_design.py`, `make_design.py` (DESIGN.md and its
  samples in `design/colors/`), `mkdocs/` (the wiki's hooks, the
  design panel, the disclaimer and the overrides), `tests/` and `installer-tests/` (installers on Linux with
  fakeroot shims).
- `dev/<name>/`: the development apps, each with `.checkout-only`: they run from the checkout, are never released
  and are in no portal. They keep Nexus's names and Nexus's design (teal, the theme `NEXUS`, never the Bazzite
  purple): Nexus Dashboard (`dev/dash`) opens them all: Nexus Release Tool (`dev/nrt`, the release front end), Nexus
  Installer Tests (`dev/itests`, the installer tests one at a time), Nexus Demo Recorder (`dev/demo`, a portal
  installation recorded with OBS), Nexus Sound Lab (`dev/sounds`), Nexus Deps (`dev/deps`, the suite's packages and
  tools on the machine with Fix; its catalog is `dev/deps/nexus_deps/catalogs/bc250-bazzite.toml`). A portal that
  runs from the checkout, or was installed from one, installs the released apps from that checkout's source: that is
  how a release is tried on a board before its tag. Install every app through the portal, so what is installed stays
  in step.
- `docs/` and `mkdocs.yml`: the wiki; `icons/`: the category icons; `install.sh`: the portal's installer from a
  checkout; `test.sh`: every test folder; `requirements-dev.txt`: the development venv.
- `.github/workflows/ci.yml`: every check on every push and pull request; `release.yml`: a release, started by Nexus
  Release Tool's Start new release on the release commit (or a tag pushed by hand); `docs.yml`: the wiki on GitHub
  Pages; `upstream.yml`: the weekly upstream check. `.github/dependabot.yml`: a weekly pull request for newer
  actions.

## Working tree

- **Line endings:** every text file is LF in git and in the working tree (`.gitattributes`: `* text=auto eol=lf`).
- **Exec bits:** a checkout with `core.fileMode=false` records new files as 100644. Before committing,
  `tools/fix-modes.sh` marks every `.sh` executable in the index; CI fails otherwise.
- **Venv:** one at the repo root, `.venv-linux/`; `./test.sh` takes it. Bazzite's system `python3` has no PyQt6:
  `python3 -m venv .venv-linux && .venv-linux/bin/python -m pip install -r requirements-dev.txt`.
- **Tests keep settings in a temp folder:** the conftest fixtures turn settings into .ini files there.
- Keep path and link case exact: Linux and GitHub are case-sensitive.

## Checks before handing work over

`tools/ci-local.sh` runs every job of ci.yml as GitHub runs it (Python 3.12, each job with only its own
requirements, in a podman container); run it before saying work is ready. `./test.sh` runs every test folder. By
hand, from the repository root:

```bash
python3 tools/check_versions.py
python3 tools/check_manifest.py --base origin/main   # portal/apps.toml rules, the bump since the last portal release
python3 tools/sync_icons.py --check
for t in tools/installer-tests/*.sh; do [ "${t##*/}" = shims.sh ] || bash "$t"; done   # every installer test
mkdocs build --strict                                # the wiki, from the venv
```

Every app (and every `portal/apps.toml` entry) has an installer test, `tools/installer-tests/<name>.sh`, and CI runs
each one; a new app adds both (`tools/tests/test_installer_tests.py` checks it). Nexus Installer Tests lists the
scripts in that folder by itself.

**Missing tooling is installed, not worked around** (owner, 26-10-2026): when a check needs a tool the machine lacks
(shellcheck, fakeroot, podman, Node.js for the design panel's script), get it (`brew install` on Bazzite) and run the
check, rather than reviewing by eye. **Frequently needed tools are installed for good** (owner, 05-11-2026): a tool
the work needs more than once is installed permanently on the development machine (Homebrew, or a distrobox for a
Fedora package Homebrew lacks), not run once in a throwaway container.

## Releases

Nexus Release Tool handles the releases: it works out the versions from the CHANGELOG kinds, and its release tab
starts `release.yml` on the release commit; one release by hand is `tools/tag-release.sh bc250-<app>-v<x.y.z>`, which
tags and pushes only a pushed commit that passed CI, and `release.yml` builds and publishes it on GitHub (owner,
15-11-2026: the same in both twins).
GitHub's Latest release is the newest portal.
`tools/check_upstream.py`, weekly in `.github/workflows/upstream.yml`, says when an upstream an app pins (an
emulator, HelixSR, DirectMesh, the USB Wi-Fi driver, Mesa, FFmpeg) moved past the pin. Moving a pin is code Claude
may prepare (with its CHANGELOG entry); the board test and the app's release are the owner's, and the handover says
so.

## Style

Code reads like the code around it: the same comment density, naming and idiom. Docs are plain, short sentences,
written for the person using the tool. **American English** (owner, 26-10-2026) in everything written: color, gray,
center, canceled, license, catalog, labeled; identifiers, settings keys, file names and recorded data keep the
spelling they have. **Pictures are WebP wherever WebP is accepted** (owner, 26-10-2026): a picture on a page or in an
app's window is a `.webp` copy of its source; a PNG stays only where WebP is not accepted or expected (a favicon, the
`-128.png` menu and Desktop icons, the source drawings in `icons/`).

The manual (`docs/`, built with MkDocs) is called **the wiki** in user-facing text: the header link and the Home
page's footer say Wiki. The repository's own GitHub wiki stays unused.
