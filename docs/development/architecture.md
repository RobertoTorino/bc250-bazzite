<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-sitemap-outline:</span>

# Architecture and consistency

Once you know one app of the suite, you can find your way in all of them. Every app is built the same way. Each
app has the same parts:

- the same folders and files
- the same start-up
- the same window header
- the same installer
- the same tests

A new app starts as a copy of that structure. This chapter describes the structure. It also lists the checks that
keep it in place.

## Principles

- **One layout.** Every app folder looks the same. Nothing is wrapped in an extra folder.
- **One way to do a thing.** Shared code lives in `bc250_core`. An app adds only what is its own.
- **Our tools, not Bazzite.** The suite answers for the portal and its apps. A Bazzite system package is in scope
  only where one of our apps uses it. Its updates are Bazzite's.
- **Not limited to one setup.** Apps read what the hardware reports and offer every option it supports. The
  owner's board and TV are test data, not the target.
- **Released code is the baseline.** Moving code must not change what an app does. Prove it with the tests, the
  installer tests and screenshots.
- **Checked by CI.** Each rule below names the check that enforces it. A mistake then fails a test instead of
  waiting for a review.

## The app folder

The repository is the suite, with `core/` and its tools in `tools/`. This chapter writes paths from the root of the
repository. The folder name is the app's key. The suite uses that same name in these places:

- `portal/apps.toml`
- the release tag (`bc250-<name>-v<x.y.z>`)
- the installer test
- the wiki chapter

```
apps/<name>/
├── <package>/                 the Python package, directly in the app folder
│   ├── __init__.py            APP_NAME, APP_ID, __version__, ROOT, LOGO_PATH, INFO
│   ├── __main__.py            start-up: python -m <package>
│   ├── main_window.py         the window
│   └── ...                    the app's own modules, and data it reads (a catalog, tables)
├── images/                    <app-id>.webp (512 px) and <app-id>-128.png for the menu entry
├── native/                    only an app with a native core (consoles): a Rust crate, see below
├── tests/                     conftest.py and test_*.py
├── install.sh                 install, update and uninstall for your own user
├── requirements.txt           runtime Python packages (PyQt6, ...)
├── requirements-dev.txt       -r requirements.txt plus pytest
├── VERSION                    the version: the single source
├── CHANGELOG                  the history, newest first
├── LICENSE                    GPL-3.0-or-later (acpi: MIT; consoles: AGPL-3.0-or-later)
├── .gitignore
└── README.md                  title, one paragraph, link to the manual, license
```

- The **package** sits directly in `apps/<name>/`. It never sits in a wrapper folder such as
  `apps/<name>/<name>/<package>`.
- `<name>` is a short name for the app.
- The package name is the app's name without its BC-250 or Bazzite prefix, written as a Python identifier. Two
  examples are `apps/ace/ace_queues/` for BC-250 ACE Queues and `apps/datstation/datstation/` for Bazzite
  DatStation. The two names may be the same word, as in DatStation.
- The short name may also differ from the app's name. BC-250 Board Test lives in `apps/check/board_test/`, so that
  no folder is called test.
- **Data** the package reads ships inside the package, such as DatStation's `data/questions.json`. It may also sit
  next to the package in the app folder, such as acpi's `tables/`. It never sits one folder up from where the
  installer copies the app.
- An app with a shell script as its engine keeps that script in the app folder too
  (`apps/cores/bc250-cores-bisect.sh`).
- **No placeholder folders** for future work. Plans and status stay out of the app and the wiki.
- **A native core** is a Rust crate in `native/`, with PyO3 for Python. Only BC-250 PS Remote Play has one so far.
  It works like this:
    - Its protocol code builds and tests without Python (`cargo test`).
    - Maturin builds the Python module from `native/pyproject.toml` as a wheel for Python 3.10 and newer.
    - Its version equals the app's VERSION. `tools/check_versions.py` reads `Cargo.toml` and `pyproject.toml`.
    - Cargo's build output, `native/target/`, is never installed or staged.
    - CI's `native` job runs the Rust tests, clippy and the module's Python tests.
    - PS Remote Play's video decoder is the cargo feature `decoder`. It links FFmpeg statically, built by
      `native/ffmpeg/build.sh` from pinned sources.
    - The release workflow builds the wheel with the decoder into `native/wheel/`. That wheel ships in the tarball.
      `tools/build_release.py` refuses the release without it.
    - `install.sh` installs that wheel, so users need no compiler.

`tools/tests/test_layout.py` checks that the packages and `images/` sit at the app root, with no wrapper folder.
CI's `shell` job checks the rest:

- `VERSION`, `CHANGELOG`, `LICENSE` and `.gitignore` in every folder
- LF line endings
- executable `.sh` files

## The package

`__init__.py` holds the app's constants. It holds nothing that needs Qt:

```python
APP_NAME = "BC-250 Example"
APP_ID = "bc250-example"
__version__ = "0.1.0"                     # equal to VERSION; tools/check_versions.py checks it

from pathlib import Path

from bc250_core import AppInfo

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / f"{APP_ID}.webp"
INFO = AppInfo(app_id=APP_ID, name=APP_NAME, version=__version__, logo=LOGO_PATH, tag_prefix="bc250-example-v",
               settings_ini=True)
```

`__main__.py` starts every app the same way, in three steps:

1. `create_app()` sets the names, style, fonts and icon.
2. `instance.already_running()` brings an open window to the front instead of opening a second one.
3. `exec_app()` runs the event loop and handles SIGTERM.

```python
def main() -> int:
    app = create_app(INFO, sys.argv[1:])
    if instance.already_running(INFO.app_id):
        return 0
    window = MainWindow()
    window.show()
    server = instance.serve(INFO.app_id, window)  # noqa: F841 (kept alive while the app runs)
    return exec_app(app)
```

Some apps open what they are given on the command line, such as a file from the menu entry's `%f`, or a host and
port. Such an app hands those arguments to the open window instead of losing them:

- `instance.already_running(INFO.app_id, args)` sends them along.
- `instance.serve(INFO.app_id, window, on_args=...)` gives them to the running window.
- The window opens them as it would at start-up. The shadPS4 Manager, for example, opens the package in Extract
  PKG.

`--version` prints the app's version and the core it runs on.

## The window

Every window starts with the same header. The app's icon sits on the left at 96 px and spans two rows. The first row
has the name with the version, then the app's states. The second row has the status boxes and the action pills.

A row holds five boxes and pills at most.
The rest goes on a row under it, which `header.add_row()` gives.
No action pill stands alone in the first row.

```
┌────────┐  BC-250 Example  v0.1.0   ● Ready
│  icon  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 96 px  │  │  6.0 GiB │ │   on     │ │  1.0.0.0 │ │    —     │
└────────┘  └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

Apps on core build it with `AppHeader`:

```python
from bc250_core.widgets import AppHeader, MetricBox, StatusText

header = AppHeader(LOGO_PATH, APP_NAME, __version__)
self.badge = StatusText()
header.add_state(self.badge)               # beside the title
for box in (self.vram_box, self.gtt_box):
    header.add_second(box)                 # the second row, left to right
header.add_second(self.apply_pill)         # the action pills after the boxes
more = header.add_row()                    # a row under it, when the second holds five already
layout.addLayout(header)
```

### The card

A card is a small window with a few boxes and pills. `CardWindow` in core's `card.py` is its template:

```
┌────────┐  BC-250 Example  v0.1.0   ● Ready  (i)                          (↻)
│  icon  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ 96 px  │  │  box   │ │  box   │ │  pill  │ │  pill  │ │  pill  │
└────────┘  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
   the page: what the card holds
```

- **The title row** holds the name with the version, the state and the info symbol. The refresh symbol sits at its
  right end.
- **The info symbol** says what the app does. In other windows it holds a text the window has no room for.
- **The rows** hold five boxes and pills at most. They are all as wide as the widest.
- **The width** is exactly a full row, so the fifth place ends at the right border. A place is 120 px at least.
- **The height** is what the page holds.
- **Hover texts:** a box or pill takes its tooltip when its value is set.

```python
from bc250_core.card import CardWindow

class Window(CardWindow):
    def __init__(self):
        super().__init__(LOGO_PATH, APP_NAME, __version__, "What the app does.")
        self.set_rows([self.one_box, self.two_box, self.on_pill, self.off_pill])   # a second list is a second row
        self.page.addWidget(self.note)

    def refresh(self):                      # the refresh symbol calls it
        ...
```

A card that needs another layout or width is an exception, and the owner's decision.
Quickfix's Tools window is one. Its pills stand on the left with the text beside them.

Apps that are not on core yet build the same layout in their own code, with the same sizes:

- a 96 px icon
- a 24 px bold title, with the version in gray at 14 px
- 6 px between the rows

Below the header, the rest of the window uses core's widgets:

- `MetricBox` shows figures.
- `StatusPill` and `StatusText` show states: `ok`, `warn`, `bad`, `info` and `neutral`, in the theme's colors.
- `hint_label()` gives a short line under a control.
- `InfoButton` holds an explanation that would take up too much room. It is a small round "i" at the end of the
  control's row. A click opens the text below it, with its links. The text stays until you click elsewhere.
- `ActionPill` is an action. It shows the action in large type and what it works on under it, as the status boxes
  look. An action is never a small button.
- `accent_button()` is the page's main action.

A window carries no long lines of text. What needs more than a line goes behind the info symbol. The wiki chapter
has the rest. An action that is applied already is not offered again. Its button is off until you pick another
value. Secondary windows get their title from `window_title()`.

Every app has the suite's theme. The theme is gunmetal (the default), silver or warm. You make one choice for all
the apps, in the portal. The portal keeps it in `~/.config/bc250-bazzite-suite/theme`. `create_app()` applies it.
An app not on core calls `apply_theme()` from its copy of `theme.py`. The theme gives their colors to these parts:

- the window
- the buttons
- the tabs
- the fields

A status box, pill or banner is the theme's surface, with its state or color as a thick left edge
(`MetricBox.set_colour()`, `surface_style()`). It is never a filled box with white text. That way it reads in a
light and a dark theme alike. Text takes the theme's colors (`THEME.text`, `muted()`), not white or a fixed gray.

Some borders show only at certain times:

- under the mouse
- with the keyboard or controller focus
- on what is chosen, such as a tab or a page in a list

Each of those borders is silver. It is the theme's outline, `OUTLINE` in `theme.py`, or `outline()` in the widgets.
The outline is light silver on gunmetal and warm. It is a darker silver on the light silver theme. A `style.py` keeps
its own color for fills and edges that are always there. It uses `OUTLINE` for those borders too.

Escape and a controller's B close every app's window. The controller also works the app. `__main__.py` calls
`exit_keys.install(app)` right after it makes the application. That is core's `exit_keys`. An app not on core
carries a copy, as it does of `theme.py`. The controller works like this:

- The d-pad and the left stick move the focus to the nearest control in that direction (`ExitKeys.nearest()`). They
  move through a list's rows and an open menu first.
- A sends Space to what has the focus. It sends Enter to an open menu, and to a list row without a box.
- LB and RB change the tab of the `QTabWidget` around the focus. They pass over an `ActionTab`.
- The touchpad moves a uinput mouse of the app's own. That mouse is `VirtualMouse`, as in the portal's
  `pointer.py`. It moves at the speed of the portal's **Touchpad** setting (`portal_touch_speed()`).

A key that the window or one of its widgets takes for itself comes first. So an app's own Escape, such as back from
a page, keeps working. The window closes through its `closeEvent`, which still asks what it asks. In some apps the
controller belongs to something else. Such an app installs it with `controller=False`. A window that must keep every
key, such as a stream, sets the class attribute `exit_keys = False`.

An app may have its own color, taken from its icon. The color is set in a `style.py` beside its window. The shadPS4
Manager's is the pattern. These parts take the color, over the theme:

- the main buttons
- the table headers
- the selection
- the links

White text on the color reads at 4.5:1 or more. Links on a dark window use a lighter shade of it. The color stays
easy on the eye. Without a `style.py`, the app takes the theme's accent.

### Icons

Every app in a category has the same icon. Each category's icon is kept once, in `icons/<category>/`, at 1024, 512,
256 and 128 px. `icons/categories.toml` gives each app its category. It also names the icon's copies:

- `images/<app-id>.webp` (512 px) in the app
- `images/<app-id>-128.png` in the app
- the app's tile in `portal/images/apps/<name>.webp` (256 px)

The copies stay in the repository. So the installers, the portal and the wiki find them where they always did.

The icons are WebP, a fraction of the size of PNG. The apps show WebP through Qt, and the wiki shows it too. Only
the 128 px icon is PNG, because a desktop or Steam may not read WebP. These use the PNG:

- the menu entry
- the Desktop icon
- a Steam shortcut
- a notification

In code, `LOGO_PATH` is the WebP icon. `steam.shortcut_icon()` gives the PNG beside it.

To give a category a new icon, drop the new images in `icons/<category>/` and run `python3 tools/sync_icons.py`.
An image named `<category>-<size>` (any extension) replaces that size only. An image by any other name replaces
all four. The tool then does these steps:

1. It scales each image to its size.
2. It saves it as WebP under the category's names. The 128 px one is saved as PNG.
3. It removes the dropped file.
4. It writes the copies.

Images must be square. An image elsewhere works too:

```bash
python3 tools/sync_icons.py --category sustainable --from ~/Pictures/leaf.png              # all four sizes
python3 tools/sync_icons.py --category sustainable --from ~/Pictures/leaf-small.png --size 128
```

[Nexus Dashboard for BC-250](dashboard.md#convert-icons) does the same from a window.
Run `python3 tools/sync_icons.py --check` to list what is not converted or copied yet. `tools/tests/test_icons.py` fails
when a copy is out of date, or when an app icon has no category.

In the wiki, every page starts with an icon above its heading:

- An app's chapter shows the app's icon (`![Name](../assets/<app>/<app-id>.webp){ .app-logo }`).
- Every other page shows a symbol from Material Design Icons (`<span class="page-icon">:material-<name>:</span>`).
- The Home page starts with its pictures.

`tools/tests/test_mkdocs_hooks.py` fails on a page without one.

## Shared code: bc250_core

`core/bc250_core` holds what more than one app needs:

- the theme
- the widgets
- start-up
- settings
- help
- update checks
- platform helpers

Nothing in it imports an app. Each app passes its constants in as `AppInfo`. The module table is in
[Development](index.md#bc250_core).

Core is **bundled per app**. So each release runs on the core it was tested with. `tools/stage_app.py` copies
`bc250_core/` next to the package of every app that imports it. From a checkout, the installer bundles the
checkout's core the same way. The shared venv holds only PyQt6 and pygame-ce. Pygame-ce is the portal's controller
reader.

Before you write a helper in an app, look in core. If two apps need the same code, move it into core and give it a
test. Apps that are not on core yet keep a copy of core's `instance.py`, `theme.py` and `exit_keys.py`.
`tools/tests/test_instance_copies.py` keeps those copies equal to core's.

## Steam shortcuts and their artwork

Some apps add something to Steam's library for Game Mode. They do it through core's `steam` module. The module
writes the shortcut in `shortcuts.vdf`. It writes its four pictures in `grid/`:

- portrait
- wide
- banner
- the logo Steam lays over the banner

Where the pictures come from depends on what the app has:

| App | What the Steam card shows |
|---|---|
| BC-250 PS Remote Play | Drawn from the app's icon (`steam_art`), with the console's name and model |
| PCSX2 Manager | Drawn from the app's icon (`steam_art`), with the game's title, because a PS2 disc has no pictures |
| Bazzite DatStation | Drawn from the app's icon (`steam_art`), with the app's name |
| shadPS4 Manager | The game's own pictures (`icon0.png`, `pic1.png`), with its icon as the logo |
| RPCS3 Manager | The game's own pictures (`ICON0.PNG`, `PIC1.PNG`), with its icon as the logo |
| Xenia Manager | Drawn from the app's icon (`steam_art`), with the game's title |
| PPSSPP Manager | The game's own pictures (`ICON0.PNG`, `PIC1.PNG`), with its icon as the logo |
| Vita3K Manager | The game's own pictures (`icon0.png`, `pic0.png`), with its icon as the logo |

The emulator managers start a game through Steam too. The tab beside **Your games** is **Start game**. It is core's
`ActionTab`, a tab that acts on a click. It leaves the open page open. It looks up the chosen game's shortcut in
Steam's file (`steam.shortcut_number()`). Then it opens `steam.play_url()` for it.

`steam_art.draw_icon_art()` is for an app with no pictures of its own. It draws the pictures like this:

- The background is near black in the icon's own color, with a glow of it.
- The portrait and the wide picture show the icon with a title and a line under it.
- The banner shows the title centered.
- The icon file itself is the logo.

A new icon changes the cards by itself. The emulator managers keep the games' own pictures. They draw only what a
game lacks.

## Inside an app, and code style

### The technical layout of an app

Each module of a package has one job. So the logic can be tested without a window, and the window stays small:

| Module | What it holds |
|---|---|
| `__init__.py` | The app's constants, such as `APP_NAME`, `APP_ID`, `__version__`, paths and `INFO`. No Qt. |
| `__main__.py` | Start-up only: arguments, `create_app()`, single instance, the window, `exec_app()`. |
| `main_window.py` | The window: layout, signals, and turning results into text and states. Little logic of its own. |
| Logic modules | Reading the board, parsing, deciding and building command lines, as in `system.py`, `cmos.py`, `cec.py`, `options.py`, `gate.py` and `dependencies.py`. They hold no Qt, so they are tested on their own. |
| `runner.py`, `privileged.py` | The one place that runs commands. Steps that need root go through pkexec or sudo here. The result comes back as a small object with the exit code and output. A running `QProcess` reports back with signals instead. It never raises an exception the window has to guess about. |

- **The outside world comes in as parameters.** A window or function takes its folders and command runner as
  arguments. The real ones are the defaults: `MainWindow(sys_root=Path("/sys"), runner=privileged.run)`. Tests pass
  a fake `/sys` and a fake runner. Nothing in a test touches the board.
- **Nothing blocks the window.** Network checks and long jobs run off the GUI thread (core's `UpdateChecker`) or
  as a `QProcess`. They report back with a signal.
- **State lives in the XDG folders.** Settings go in `~/.config/`, through `AppInfo` and core's settings helpers.
  Results and data go in `~/.local/share/`. Each goes in a folder named after the app.
  `install.sh --uninstall --purge` removes exactly those.
- **Scripts that do the board work** stand on their own. They are the bisect and unlock scripts and
  `test-board.sh`. The window builds their command line and shows their output. You can run the script by hand
  with the same result.

### Code style

- **Read like the code around it.** Use the same comment density, naming and idiom as the file you change.
- **Python:** 3.10 or newer. Bazzite ships 3.13 or newer. Use these:
    - `from __future__ import annotations`
    - type hints on functions
    - `dataclass` for results
    - `pathlib` for paths
    - f-strings
    - lines up to about 120 characters
- **Every file** starts with its SPDX line (`# SPDX-License-Identifier: GPL-3.0-or-later`). A module or script
  then starts with a docstring or comment that says what it is for.
- **Comments say why,** not what the next line does. A comment gives the reason for a choice, a board quirk, or a
  finding on the owner's board with its date.
- **Imports go one way.** Core imports no app. Logic modules import no Qt. An app imports core, never another app.
- **Text in the window** is plain, short sentences in English, for the person using the app. The apps are not
  translated. They use no `self.tr()`, and Qt's own dialog buttons stay English too. Errors say what happened and
  what to do next.
- **Shell** scripts follow these rules:
    - `#!/usr/bin/env bash`
    - `set -euo pipefail`
    - `info`/`die` helpers
    - the usage text in the header comment, shown by `--help`
    - quoted variables
    - no shellcheck warnings
- **Files** use LF line endings. Scripts are executable. `tools/fix-modes.sh` sets the bit in the index.

## The installer

`install.sh` sits in the app folder. It runs as your own user and refuses to run with sudo. It uses sudo or pkexec
only for the steps that need root. Every installer takes these options, and `--help` shows them. An app may add its
own.

```
./install.sh                         install or update
./install.sh --no-desktop-shortcut   app menu entry only, no icon on the Desktop
./install.sh --uninstall             remove the app; keeps its settings and results
./install.sh --uninstall --purge     also remove its settings and results
```

It installs:

- **The app** under `~/.local/share/<app-id>/`. An app that runs scripts as root goes under
  `/opt/<app-id>-v<version>` instead, owned by root, with a link `/opt/<app-id>`. So a normal user cannot change
  code that sudo runs.
- **Python:** PyQt6 in the suite's shared venv `~/.local/share/bc250-bazzite-suite/venv`. An app with its own
  packages has its own venv. The shared venv goes when the last app that uses it is removed. pip runs with
  `--upgrade`. So installing again brings every package to the newest version the requirements allow. That
  includes a security fix within that range.
- **A launcher** `~/.local/bin/<app-id>` that changes into the app folder and runs
  `exec "<venv>/bin/python" -m <package>`. Some apps take file or folder paths on their command line, such as the
  shadPS4 Manager. Such a launcher stays in the folder it is started from, so a relative path means what it says.
  It runs `exec "<venv>/bin/python" -c '$RUN_MODULE' "<app folder>" <package> "$@"`. That line puts the app folder
  first on `sys.path` instead (see its `install.sh`). The app's `__main__.py` makes the path absolute before it uses
  the path or hands it on. Keep the `exec "<venv>/bin/python"` start of that line. Nexus Deps reads it to find the
  app's Python environment.
- **A menu entry and a Desktop icon.** Both point at the launcher by its full path.

The installer checks that its files are there before it changes anything. It works the same from a checkout and
from an extracted release. It needs no network except for pip.

## Tests

- **`apps/<name>/tests/`:** pytest, offscreen. `conftest.py` does three things:
    - It puts core from the checkout on the path.
    - It provides a `qapp` fixture.
    - It points QSettings and the XDG folders at a temp folder, so tests never touch your settings.
- **Fakes stand in for the board.** Fake `/sys`, `/proc` and command runners take its place. Data recorded on a
  real board makes good fixtures. Tests also cover other setups.
- **Every app has `tests/`** and a `requirements-dev.txt`, which is its `requirements.txt` plus pytest. CI reads
  its pytest matrix from the folders with `tests/` (`tools/ci_matrix.py`). So the app is in it at once.
- **The installer test** is `tools/installer-tests/<name>.sh`. It installs from the checkout and from a staged
  release, with and without the Desktop icon. Then it uninstalls. It runs without root or network. `shims.sh` turns
  sudo into fakeroot and pip into a stub. CI runs the installer tests side by side, each in a log group of its
  own. [Nexus Installer Tests](dashboard.md#installer-tests) lists the scripts in that folder by itself.
- **`./test.sh`** runs every test folder in the repository. These are core, tools, `dev/`, the portal and the
  apps.

`tools/tests/test_installer_tests.py` fails when an app or a portal entry has no installer test. It also fails when
CI does not run one.

## Versions, changelogs and releases

- `VERSION` is the single source of an app's version. Copies (`__version__`, shell `VERSION=`, pyproject) must
  match it. `tools/check_versions.py` checks them.
- Every change gets a `CHANGELOG` entry in the folder it changes. That is the app, core or the portal. Suite-wide
  changes go in the root `CHANGELOG`. An entry has three parts:
    - a `Changelog: DD-MM-YYYY HH:MM:SS` line in Europe/Amsterdam time
    - a blank line
    - plain sentences

  The newest entry comes first.
- Versions follow semantic versioning. In an app's, core's or the portal's `CHANGELOG`, each entry starts with its
  kind of change. A release takes the highest kind since its last tag:

  | The entry starts with | What changed                                                     | Release | Example         |
  |-----------------------|------------------------------------------------------------------|---------|-----------------|
  | `Breaking.`           | something removed, or no longer working as before (settings, options, files) | major | 1.2.3 → 2.0.0 |
  | `Added.`              | a new feature, everything that worked still works                | minor   | 1.2.3 → 1.3.0   |
  | `Fixed.`              | a bug or security fix                                            | patch   | 1.2.3 → 1.2.4   |

  An app at 0.x follows the same table. A new feature takes 0.1.4 to 0.2.0, and a breaking change takes it to
  1.0.0. The portal moves at least as far as the largest app release it pins. It moves a minor step when an app is
  added or removed. Nexus Release Tool offers that version first.
- Each app is released on its own tag, `bc250-<name>-v<x.y.z>`. The portal pins one release of each app in
  `portal/apps.toml`. The steps are in [Portal](../portal.md#appstoml-and-releases).

## Adding a new app

`tools/new_app.py` writes a new app from this chapter. It also lists the app wherever the suite lists its apps. So
the template cannot drift from the checks. It then runs the checks on the new app:

```bash
python3 tools/new_app.py fan2 "BC-250 Fan Two" --category sustainable --summary "What it does."
python3 tools/new_app.py --help     # --id, --package: the app id and the package, when the defaults are not yours
```

It writes these files:

- `apps/<name>/`, with the package with `__main__.py` and a window on the card, `images/`, `tests/`,
  `install.sh`, the requirements, `VERSION` 0.1.0, `CHANGELOG`, `LICENSE`, `.gitignore` and `README.md`
- the installer test `tools/installer-tests/<name>.sh`
- the chapter `docs/apps/<name>.md`

It adds the app to these places:

- `portal/apps.toml`
- `icons/categories.toml`, with the icon copies
- `mkdocs.yml`
- the apps overview and categories tables
- the home page, as a line at the end of its last card, to work into the cards' text
- the suite README
- the bug report's App dropdown
- the root `requirements-dev.txt`
- Nexus Deps' catalog of the suite

When nothing of the app is there, its `install.sh --uninstall` says the app is not installed and removes nothing.
CI needs no edit, because its pytest matrix, its installer tests and its shellcheck come from the folders.

Some apps do not fit the template. Building one by hand is the owner's decision. These are the steps:

1. Copy the folder of the app closest to yours, and rename the package. Set `APP_NAME`, `APP_ID`, `VERSION`
   (0.1.0) and `__version__`. Clear its `CHANGELOG` and start it with one entry.
2. Add the app to `icons/categories.toml` with its category, and run `python3 tools/sync_icons.py`. It writes the
   icons in `images/` and the portal's tile ([Icons](#icons)).
3. Build the window on the card (`CardWindow`). For a larger window, build it on `AppHeader` and core's widgets.
4. Write `install.sh` from the copied one, with the same options and launcher.
5. Write `tests/` and `requirements-dev.txt`, and `tools/installer-tests/<name>.sh`. CI finds both by itself. It
   takes every folder with `tests/` and every script in `installer-tests/`, and it shellchecks `install.sh`. Add
   the app's `requirements-dev.txt` to the root's, for the development venv.
6. Add the app to `portal/apps.toml`. Give it these keys:
    - name
    - summary
    - `changes_board`
    - `category`, which is its icon's category and the portal's tab for it
    - install
    - uninstall
    - detect
    - launch

    An app that changes the board also gets a `board_change`. In a few plain sentences, it says what the app
    touches, what stays after a reboot or a power off, what it never touches and how it is undone. The tile's
    popup shows it.

    An app made of small quickfixes, as BC-250 Quickfix, lists each one as a `[[apps.<name>.quickfixes]]` table
    instead. Each table has a key, name, summary and launch, and its own `changes_board` and `board_change`. The
    portal shows a tile per quickfix. A new quickfix of BC-250 Quickfix needs three parts, kept the same by its
    tests:

    - a window in its `windows.py`
    - an entry in its `catalog.py`
    - a table in `apps.toml`
7. Add the app to Nexus Deps' catalog of the suite (`dev/deps/nexus_deps/catalogs/bc250-bazzite.toml`). Give it
   these entries:
    - `[app.<name>]` with its launchers
    - its Python packages
    - the external tools it runs, each with the Homebrew formula (`brew`) or Fedora package (`rpm`) that installs it
8. Write its wiki chapter, `docs/apps/<name>.md`, and list it in these places:
    - `mkdocs.yml`
    - a row in the apps overview, `docs/apps/index.md`
    - a link on the home page (`docs/index.md`)
    - an option in the bug report's App dropdown (`.github/ISSUE_TEMPLATE/bug_report.yml`), in the manifest's order

    An app that changes the board opens its chapter with a `!!! warning "Changes the board"` box, right after the
    title. The box holds its `board_change` text word for word. `tools/check_manifest.py` compares the two.
9. Run the checks from [Development](index.md) and every installer test.

The tests in step 9 tell you what you missed:

- an app without an installer test
- a catalog that does not match the requirements files
- a version copy that does not match `VERSION`
- a package in a wrapper folder

After the generator, what is left is the app itself:

- its window and tests
- its chapter
- its CHANGELOG entries
- the catalog, for a package or tool beyond PyQt6
- the portal bump the new entry asks for

## The checks at a glance

| Rule | Checked by |
|---|---|
| Packages and `images/` at the app root, no wrapper folder | `tools/tests/test_layout.py` |
| `install.sh` at the app root, with the standard options, refusing root | `tools/tests/test_layout.py` |
| Every app has `tests/` and `requirements-dev.txt`, and CI runs them | `tools/tests/test_layout.py` |
| `VERSION`, `CHANGELOG`, `LICENSE` and `.gitignore` in every folder, LF line endings and executable scripts | CI's `shell` job |
| Version copies equal `VERSION` | `tools/check_versions.py` |
| Every app and portal entry has an installer test, and CI runs it | `tools/tests/test_installer_tests.py` |
| Copies of `instance.py` equal core's | `tools/tests/test_instance_copies.py` |
| Nexus Deps' catalog matches the requirements files, the portal's apps, and the tools the apps use | `dev/deps/tests/test_dependencies.py` |
| `portal/apps.toml` rules and version bumps | `tools/check_manifest.py` |
| The wiki builds with no broken link | `mkdocs build --strict` |
