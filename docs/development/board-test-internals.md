<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-cog-outline:</span>

# BC-250 Board Test - development

This page shows you how to work on the GUI of BC-250 Board Test. The GUI is based on the diagnostic script for
**Bazzite** (Fedora Atomic / rpm-ostree). The script runs on an **AMD BC-250** board. The board has a Cyan Skillfish
APU, `gfx1013`, with the PCI ID `1002:13fe`.

The script is **read-only**. It installs, turns on, turns off and reconfigures nothing. The only exception is the
opt-in `--stress` mode. That mode puts the board under load on purpose.

---

## Getting started

### Requirements

| What         | Version                        | Notes                                                                           |
|--------------|--------------------------------|---------------------------------------------------------------------------------|
| Python       | 3.10 or newer                  | Developed on 3.13. Bazzite ships a recent Python 3 (3.13+). You need no layering. |
| PyQt6        | 6.11 – 6.x (`requirements.txt`) | The pip wheel bundles Qt. That includes the Wayland and X11 platform plugins.   |
| PyQt6-Charts | same minor version as PyQt6    | Qt Charts, for **Show graph**. Optional. The rest of the app works without it. |
| bash, sudo   | —                              | Present on Bazzite. The GUI runs `test-board.sh` through `sudo`.              |

You install nothing with `rpm-ostree` for the GUI itself. A venv in your home directory is enough.

### Develop elsewhere (e.g. macOS)

The real script needs systemd, journald and the BC-250 sysfs nodes. For work on the UI, use the stand-in. It
accepts the same options and prints the same line format:

```bash
_python/bin/python -m board_test --script development/tools/fake-test-board.sh --no-sudo
```

You can also drive the GUI with a real report from the board in place of simulated output. Point `BC250_REPLAY` at
a `/var/log/bc250-board-test/bc250-test-results-*.log` file. The stand-in cuts the selected tests (`--only`) from
that report:

```bash
BC250_REPLAY=debug/bc250-test-results-20260929-093526.log \
  _python/bin/python -m board_test --script development/tools/fake-test-board.sh --no-sudo
```

### Local Bazzite image build (package testing)

With a local image you can test a package or setup against a fully set-up system before you touch a board.
`development/tools/bazzite-image/` builds a custom Bazzite OCI image with Podman:

```bash
cd development/tools/bazzite-image
./build.sh --test        # builds bazzite-custom:<timestamp> and :latest, then a sanity check
```

The `Containerfile` layers the same RPMs as `development/tools/install-requirements.sh --rpms`. To add a locally
built RPM of this project, use the commented `COPY`/`RUN` lines. On a board, rebase onto the local image. You undo
it with `rpm-ostree rollback`.

```bash
sudo rpm-ostree rebase ostree-unverified-image:containers-storage:localhost/bazzite-custom:latest
```

### How it works

* The GUI calls `test-board.sh --gui [--no-desktop] [--only=NN,..] [--stress=S --interval=I]`.
* The GUI adds `--no-desktop` when *Settings › General › Copy the full reports to ~/Desktop/bc250-board-test after
  each run* is off.
* With `--gui` the script words its how-to-run hints for the GUI. It writes "Start test 42 (Performance page)" in
  place of "Re-run with --bench".
* The GUI parses the output per `[TEST NN]` block. The worst tag in a block sets the button color. The order is
  `ERROR` > `WARNING` > `SUCCESS` > `INFO`. The colors are:
    * red for an error
    * orange for a warning
    * green for OK
    * blue for info
* A running test is yellow and labeled `running…`.
* The hints panel collects the `HINT:` lines and the `NOTE:` lines. A `HINT:` line is a fix suggestion, with a ⚠
  icon. A `NOTE:` line is background, with an ℹ icon.
* The script may wrap one hint over more than one `HINT:` or `NOTE:` line. The GUI joins those lines into one hint.
* The stats toolbar counts the latest result of every test over all runs. An SQLite history keeps these results, in
  `~/.local/share/bc250-board-test/history.db`.
* The GUI imports the script's reports into the history at startup.
* During development, you can inspect the history with `sqlite3 ~/.local/share/bc250-board-test/history.db .tables`.
  On Bazzite, layer `sqlite3` once with `development/tools/install-requirements.sh --dev`.
* **Settings › Logs & history › Clean up logs…** removes logs older than N days, or all logs and the history.
* The **health score** is the average over the tests that ran. Each test counts as follows:
    * passed and info at 100%
    * warnings at 50%
    * failures at 0%
* The score is green at ≥ 90% and orange at ≥ 70%. Below 70% it turns red.
* **Settings** is the last item in the navigation. It opens a panel over the window with these sections:
    * *Privacy* explains what the app stores and what reaches the internet. It also has the privacy options.
    * *General* has the notifications and the copy of the reports to the Desktop.
    * *System overview* shows facts about the board as colored boxes. The GUI reads them only when you open the page.
    * The *Logs & history* section holds **Clean up logs…**.
    * *About* shows the version, the build date and the repository.
    * The *Print results* section holds the **Print results** button.
* The options in *Privacy* are:
    * **Keep a test history**
    * **Store the kernel version and CPU mitigation state in the history**, off by default
    * **Mask personal data in saved GUI logs**, on by default
    * **Run the tests with admin privileges (sudo)**
    * **Forget sudo authentication now**
* The boxes in *System overview* are:
    * the BIOS version
    * the unlocked CUs, such as 36/40
    * the CPU cores and threads, such as 6/8 and 12/16
    * the download and upload of the latest speed test
    * the NVMe size and free space
    * the package count from test 45
* The GUI stores its preferences in `~/.config/bc250-board-test/bc250-board-test.ini`.
* Test 41 runs only when you ask for the stress test. Otherwise, the GUI leaves it out and does not count it as run.
* The GUI writes every run to `~/.local/share/bc250-board-test/logs/<YYYYmmdd-HHMMSS>_<scope>.log`.
  **Show Logs** opens them.
* The script still writes its own report to `/var/log/bc250-board-test/`.
