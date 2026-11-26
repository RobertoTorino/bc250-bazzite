<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-view-dashboard-outline:</span>

# Dashboard

The **Nexus Dashboard for BC-250** (`dev/dash/` in the repository) is the one door to the tools for working on the
suite. Its tiles start the development apps of the checkout, each in a window of its own. Other tiles open the suite's
tools. Below the tiles, Test local apps starts the suite's own apps and its wiki from the checkout.

Like every development app, the dashboard runs from the checkout it lives in. It takes Nexus's design and icon. It
has no releases of its own, so nothing of it is in the portal.

The suite's own scripts stay in `tools/`, and the dashboard runs them there. A tile turns gray where it does not run
on this system. Its tooltip says why.

## Start it

Run these commands from the repository's root, with the checkout's venv (`.venv-linux`).
[Set up and test](index.md#set-up-and-test) says how to make the venv. Installing copies nothing. The menu entry
always starts the app of the checkout you installed it from. After you move the checkout, install it again.

```bash
dev/dash/run.sh                             # open it
dev/dash/install.sh                         # app menu entry and Desktop icon
dev/dash/install.sh --no-desktop-shortcut   # app menu entry only
dev/dash/install.sh --uninstall             # remove them; the checkout stays
dev/dash/install.sh --uninstall --purge     # also remove the settings
```

Run the installer as your own user, not with sudo. Then double-click **Nexus Dashboard for BC-250** on the Desktop to
open the dashboard. Its menu entry opens it too.

When you open the dashboard while it is already open, the open window closes and a new one opens. The app runs from
the checkout, so the new window has the code as it is now. The dashboard ends an open dashboard that does not
answer within 5 seconds.

## The window

The header holds the icon, the name and the checkout's last commit with its time. A development app has no
version. A click on the icon opens the suite's wiki. Below the header are the tiles, then
[Test local apps](#test-local-apps). Under them, a line answers each click. It says which app started and where its
log is, or why a tile is off.

The first tiles are the development apps of the checkout. A click starts the app with its run script. The app opens
in a window of its own, which keeps running when the dashboard closes.

| Tile | What it opens |
|---|---|
| **Nexus Release Tool** | The release front end for a release's versions, CHANGELOG entries, pins and portal bump, and the board checks ([Releases](releases.md)). |
| **Nexus Demo Recorder** | A portal installation recorded with OBS ([below](#demo-recorder)). |
| **Nexus Deps** | The suite's Python packages and tools on this machine, what is missing or outdated, and Fix for it ([below](#deps)). |
| **Nexus Garbage Remover** | The garbage on this machine, with its size, and Delete for it ([below](#garbage-remover)). |
| **Nexus Installer Tests** | The suite's installer tests, one at a time ([below](#installer-tests)). |
| **Nexus Marketing for BC-250** | Writes an article that presents the portal and its apps, as a web page to share ([below](#marketing)). |
| **Nexus Remix Studio** | Mixes a voice with a synthesized background and saves the result ([below](#remix-studio)). |
| **Nexus Sound Lab** | Short sound effects for the suite's windows, made from sliders ([below](#sound-lab)). |
| **Nexus TTS** | Speaks an English text in a natural voice and saves it as a sound file ([below](#nexus-tts)). |

The other tiles work on the suite:

| Tile | What it opens |
|---|---|
| **Portal video tour** | Records the portal's tour ([below](#video-tours)). |
| **Apps video tour** | Records a short tour of each app you check ([below](#video-tours)). |
| **Convert icons** | Makes a category's icons from your images ([below](#convert-icons)). |
| **Close issues** | Closes the open issues on GitHub that you check ([below](#close-issues)). |

## Test local apps

**Test local apps** lets you try a change to the suite's apps before its release. It shows the suite's portal and
every app window of the suite in the checkout, each as an icon. The portal comes first. A click starts that app from
the checkout. The apps start as `python -m <package>` with the checkout's venv and its `core`. That is how `run.sh`
starts a development app.

When the portal is already open, its icon warns you and starts nothing. A second portal never opens. Starting one
only brings the open window to the front, so close the open portal first.

An app that changes how the board runs has an orange **!** on its icon. It asks first, as in the portal. Started
from the checkout, it uses the scripts in the checkout.

Each app writes its output to `~/.cache/nexus-dashboard-bc250/local/<package>.log`. When an app stops with an error, the
end of its log shows below. The apps keep running when you close the dashboard. The round **i** beside the title
says the same.

The last icon is the wiki, **BC250 Bazzite Suite wiki (local)**. It serves the wiki from the checkout with
`mkdocs serve`, which the development venv has. The wiki opens in the browser at
`http://127.0.0.1:8765/bc250-bazzite/`, with its design panel open. It rebuilds on every save. Its log is
`mkdocs-root-local.log` in the same folder as the apps' logs. When the wiki is already running, a click only opens
the page again.

Like the apps, the wiki keeps running when you close the dashboard. The dashboard has no button that stops it.
`pkill -f "mkdocs serve"` stops it. A wiki started before the checkout changed can still show the old setup. That
happens after a pull, or after a change to `mkdocs.yml` or the design panel. Then stop the wiki and click its icon
again.

With **Wiki on the network** checked, the icon serves the wiki on every address of the computer, at port 8785.
Then a handheld, a laptop or the TV can open it too. The addresses for those devices show below once the wiki has
started. The computer's firewall has to let them in.

## Close issues

The **Close issues** dialog shows the open issues on GitHub, such as the weekly Upstream review. Each issue has a
checkbox. **Run** closes the checked ones with `gh issue close`, one after the other. It adds your comment when you
write one. Their output shows below. When one fails, the ones after it stay open. Double-click an issue to open it
on GitHub.

The dialog needs the GitHub CLI with a login (`gh auth login`).

## Video tours

The tours show the real windows of the checkout as it is now. They are recorded offscreen, so nothing shows on the
screen while they record. The videos go to your Videos folder. Music plays under them and fades out over the last
two seconds. For a video without sound, uncheck **Music under the video, faded out over the last two seconds**.

**Size** is 1080p (1920 × 1080) by default, the size the wiki uses. Choose 2160p (4K, 3840 × 2160) for a video for
YouTube. YouTube shows a 4K upload far sharper than a 1080p one. A 4K video is the same tour, drawn at twice the
scale, so the text stays crisp. It takes about four times as long to record. Its name has `-2160p` before `.mp4`. The
1440p size is the step between.

A recording runs in the background, and its output shows in the dialog. **Stop** ends it. **Play** opens the video
in your video player.

- **Portal video tour** records the portal's tour, about four minutes long. The video is
  `bc250-portal-tour-v<portal version>.mp4`. The dialog checks **A voice reads the captions out, with Nexus
  TTS's speech engine** at first. Uncheck it for a tour without the voice. Check **Also write the copy on the wiki's
  Portal Tour page** to also write `docs/videos/portal-tour.mp4` and its poster in the checkout. You review and commit them.
- **Apps video tour** lists every app of the suite. An app with two programs has a row for each program. Check the
  apps (**All**, **None**), set the **Length** (40 seconds by default) and choose **Record**. Each tour takes a few
  seconds. Its video is `bc250-<app>-tour-v<version>.mp4`. Double-click an app to play its video. What an app reads from the
  board is real, so watch a video before you publish it.

The dialogs run `tools/record-tour.sh` and `tools/record-app-tour.sh` with the checkout's development environment.
They need ffmpeg. The same scripts run from a terminal.
[The wiki's pictures and tours](index.md#the-wikis-pictures-and-tours) says how. The music under every tour is in
`tools/sounds/`.

## Convert icons

**Convert icons** makes a category's icons from your images. Every app in a category shares the category's icon.
The icon is kept in `icons/<category>/` at 1024, 512, 256 and 128 px. You give one image for every size, or an image
for a single size. Images must be square.

The images are scaled and saved under the category's names as WebP. The 128 px icon is saved as PNG. Then they are
copied to every app of the category, the portal's tiles and the wiki, as `icons/categories.toml` says.

The dialog shows the current icons of the chosen category. **Convert and copy to the apps** runs
`tools/sync_icons.py`, and its output shows in the dialog. The icons and their copies change in the checkout, for
you to review and commit.

## Demo Recorder

The **Nexus Demo Recorder** (`dev/demo/`) records a demo of a portal installation with OBS. It uses a portal release
extracted in Downloads, which it finds by itself. **Find in Downloads** looks again, and **Choose folder…** takes
another folder. Without a release, it uses the suite in this checkout. Then the checkout's `portal/install.sh`
installs the released apps from the checkout's source. `dev/demo/run.sh` and `dev/demo/install.sh` start and
install the recorder on their own.

Before you record, have these ready:

- **The checkout's venv** with `requirements-dev.txt` installed. It brings the OBS WebSocket client (`obsws-python`)
  and the desktop portal's client (`dbus-fast`).
- **OBS Studio 30 or newer**, running. It has WebSocket 5.3 built in. The recorder sets the folder for the
  recordings through it. On Bazzite, that is the flatpak `com.obsproject.Studio`, or the `obs` command on the PATH.
  **Open OBS** starts it.
- **In OBS, a scene with a screen-capture source** whose preview shows your desktop. On Wayland, the source is
  Screen Capture through PipeWire.
- **OBS's WebSocket server on.** In OBS, choose Tools, WebSocket Server Settings. Check **Enable WebSocket server**
  and set a password. Note the port and the password for step 1.
  The port is 4455 unless you changed it.
- **A portal release**, extracted in Downloads, or the suite in this checkout. **Open the releases page** goes to
  the releases.
- **A clean system for a fresh install.** The portal must not be installed, and neither must the app you want to
  show. The recorder checks both. It keeps **Start recording and install portal** off until they are gone.
- **A terminal emulator** for the installer and its password prompts. Konsole, GNOME Terminal, Ptyxis, Xfce
  Terminal, foot, Alacritty, kitty and xterm work, and so does the one `$TERMINAL` names.
- **A desktop whose portal offers global shortcuts**, for the stop shortcut. KDE Plasma offers them, as on Bazzite.

1. **OBS setup:** OBS needs a scene with a screen-capture source and its WebSocket server turned on. On Wayland, the
   source is Screen Capture through PipeWire. The server is under Tools, WebSocket Server Settings. **Setup
   instructions** has the steps. Enter the port and the password, and choose **Test connection**. The recordings go
   to `~/Videos/demos`.
2. **Portal release and app:** Choose the release and, if you like, an app to show. The demo is a fresh install. So
   the portal and that app must not be installed yet.
3. **Record:** **Start recording and install portal** starts the OBS recording. It also opens the portal's
   installer in a terminal, for its output and its password prompts. The window hides. Once the installer is done,
   the portal opens. Show BC-250 Board Test, then install the chosen app and open it. The global shortcut the window
   named stops the recording and brings the window back. That shortcut is Ctrl+Alt+F12 by default. **Recent
   recordings…** lists the videos and plays one.

## Installer tests

**Nexus Installer Tests** (`dev/itests/`) runs the suite's installer tests, `tools/installer-tests/*.sh`, one at a
time. They run in bash, with fakeroot. Their live output shows on the right, and each test's result shows at the end
of its row. Check the tests and choose **Run selected**, or choose **Run all**. **Stop** ends the test that runs and
skips the rest.

Each test installs an app from the checkout as its installer does on a board. Then it removes the app again. This
happens in a temporary home, so nothing of yours is touched. The tests use fixed temporary folders under `/tmp`. So
the same test never runs twice at once. `dev/itests/run.sh` and `dev/itests/install.sh` start and install the app
on their own.

## Sound Lab

**Nexus Sound Lab** (`dev/sounds/`) makes and tries the short sound effects a window plays. An example is the tick
when the controller moves the focus in the portal.

Choose a **Preset** to start from: Tick, High tick, Blip, Thock, Click, Select, Back, Error or Tick after silence.
Then choose a **Waveform** out of sine, triangle, square, saw and noise. Shape the sound with the sliders:

- the pitch at the start and at the end of a tone, a sweep when they differ
- the length of a tone
- the attack, the rise to full volume
- the decay, how fast the sound dies away per second
- the number of tones, and the interval between them in semitones, where two tones a fifth apart make a blip
- the noise over the tone, and its own decay
- the silence before the sound
- the volume, its peak

The sound is drawn beside the sliders. It plays each time you let go of a slider, and with **Play**. It also plays
when the focus moves between the buttons of **Try it**, the way a window plays it while you navigate. Move the focus
with Tab, the arrow keys or a controller's d-pad. The controller's A plays it again. Once a slider has left the preset, the box says
Custom.

**Save as WAV…** writes the sound as 16-bit mono at 44.1 kHz. It is meant for the portal's sounds folder,
`portal/bc250_portal/sounds/`. The portal plays a sound there by its file name. The app remembers the last sound,
the preset and the save folder.

**Keep the audio link awake**, on by default, plays a silent loop while the window is open. Without it, a short
sound can stay silent on a TV. PipeWire pauses the output when nothing plays. An HDMI TV mutes a moment after the
stream stops. It needs time to unmute when the stream starts again. So a 50 ms tick is over before you hear it.

The preset Tick after silence shows the same from the other side. With the link asleep, only its tick comes through.
A window that plays such sounds needs the same loop while it is open. `dev/sounds/run.sh` and
`dev/sounds/install.sh` start and install the app on their own. The dashboard's tile does the same.

## Nexus TTS

**Nexus TTS** speaks an English text in a natural voice and saves the speech as a sound file. Use it for a video's
voice-over or a spoken note. The voices run on the machine itself, and nothing of your text leaves it. The app is in
`dev/text/`.

Type or paste the text, choose a **Voice** and a **Speed**, and click **Speak**. Ctrl+Enter does the same. The first
sentence plays while the app makes the next ones. An empty line in the text gives a longer pause. **Stop** ends the
speech, and so does Esc.

- **Voice** lists the 15 English female voices of the Kokoro model. Each one shows whether it is American or
  British. The list opens on Heart. The model's male voices and its voices in other languages are not offered.
- **Speed** goes from 0.50 to 2.00. At 1.00 the voice speaks at its own pace. The app opens on 0.85.
- **Save as…** writes the speech as an Ogg Vorbis, MP3, FLAC or WAV file, at 24 kHz mono. The file's suffix sets the
  format. You do not have to click **Speak** first. A text you just heard is saved as you heard it.

The text must be English. The app does not speak a text with letters of another script, such as Cyrillic or
Chinese. It says so in the status line. It cannot tell another language in Latin letters from English. It reads
such a text with English sounds.

The app remembers the text, the voice, the speed, the save folder and the format.

### The speech engine

The speech engine is the program that makes the speech. It is not in the repository, so the app downloads it once.
The first time, the window shows **Set up the speech engine** in place of the text. Click it, and the window shows
each step. The download is about 350 MB, and it goes to `~/.local/share/nexus-text-to-speech/`. After that, the
window opens on the text.

The setup needs one of these:

- [uv](https://docs.astral.sh/uv/), which brings the right Python by itself. Install it with `brew install uv`.
- A Python from 3.10 to 3.13 on the PATH

The engine has its own Python because onnxruntime, one of its packages, has no build for the Python of the
checkout's venv. The app checks each model file against its SHA-256 before it keeps the file. When a step fails, the
window says so. Click **Set up the speech engine** again to retry.

The app uses the half-precision model, `kokoro-v1.0.fp16.onnx`, a file of 164 MB. On a BC-250 it makes speech about
three times faster than the voice speaks it. It is as fast as the full model, at half the download. The engine
starts with the window and stays, so the model loads once. When the engine stops by itself, the window says so.
**Speak** starts it again. The engine's own messages are in the app's log. The dashboard names that log when it
starts the app.

`dev/text/run.sh` starts the app without the dashboard, and `dev/text/install.sh` gives it a menu entry.
`dev/text/install.sh --uninstall --purge` removes the speech engine and the settings.

## Remix Studio

**Nexus Remix Studio** mixes a voice with a synthesized background and saves the result as a sound file. Use it to
put a soft pad under a voice-over. Everything is made on the machine itself. The app is in `dev/studio/`.

The window has three parts, from top to bottom.

### Voice

- **Open a sound file…** takes a WAV, Ogg Vorbis, FLAC or MP3 file as the voice.
- **From a text…** opens a small window. Type an English text, choose a voice and a speed, and click **Make the
  voice**. [Nexus TTS](#nexus-tts) speaks it, so its speech engine must be set up first.
- **Remove** takes the voice out. The mix is then the background alone.
- **Remove silence** cuts the silence at the start and the end of the voice. A pause inside the voice stays.
- **Save a copy…** writes the voice alone, as it is now, as an Ogg Vorbis, MP3, FLAC or WAV file.

The voice is drawn below the buttons.

**Silence below** sets what counts as silence, from -60 dB to -20 dB. The app opens with -40 dB. A higher level cuts
further into a soft start or end. Choose -20 dB to cut a slow fade-in up to the first loud sound. The status line
says how much was removed.

**Remove silence** changes only the voice in the window. The sound file stays as it is. Open the file again to get
the whole voice back. To trim a sound file, open it, click **Remove silence** and then **Save a copy…**. The copy
gets a name of its own, because the app never writes over the voice's file.

### Background

The background is a sustained sound, a pad or a drone, that the app makes itself.

- **Preset** is a sound to start from. There are six: Warm pad, Soft strings, Drone, Glass, Choir and Dark. The box
  says Custom once you change a control.
- **Key**, **Octave** and **Chord** set the notes that sound together.
- **Tone** goes from dark and soft to bright.
- **Movement** sets how much the sound drifts and swells over time. With the slider at 0, the sound stands still.
- **Space** is the reverb, from a dry sound to a large hall.

**Try background** plays 12 seconds of it alone.

### Mix

- **Voice volume** and **Background volume** set how loud each track is. The app opens with the background at 40 %,
  so the voice stays clear.
- **Lead-in** is how long the background plays before the voice starts, and **Tail** how long it goes on after.
- **Fade** is the background's fade in at the start and its fade out at the end.
- **Length** is how long the mix lasts. Without a voice you set it freely, from 5 to 600 seconds. With a voice it
  is the lead-in, the voice and the tail together, and moving it changes the tail.

The pills at the top work on the mix. **Play** makes the mix and plays it. Ctrl+Enter does the same. **Stop** ends
it, and so does Esc. The mix is drawn below the sliders, with its length. A minute of mix takes about five seconds
to make.

**Save as…** writes the mix as an Ogg Vorbis, MP3, FLAC or WAV file, at 48 kHz stereo. The file's suffix sets the
format. You do not have to click **Play** first. A mix you just heard is saved as you heard it. The same settings
always give the same sound.

**Reset** puts the background and the mix back on the values the app starts with. The voice stays.

When both tracks together are too loud for the file, the app turns the whole mix down. It says by how much under
the drawing. Nothing is clipped.

The app remembers the voice file, the silence level, the background, the mix, the save folder and the format.

`dev/studio/run.sh` starts the app without the dashboard, and `dev/studio/install.sh` gives it a menu entry.

## Deps

**Nexus Deps** (`dev/deps/`) shows what the suite's apps need on this machine, and what is missing or outdated. It
lists the Python packages and external tools of the suite's apps installed here. For each one, it shows which apps
and features use it, and whether it is missing or must be updated. **Fix** installs what is needed.

On top, it shows whether a Bazzite update waits for you. It also shows every update the machine has:

- Bazzite's image
- the Flatpaks
- Homebrew
- Rust
- the development venv
- Prime95's mprime, when it is in `~/mprime`

It runs from the checkout, like every development app. Its catalog of the suite is
`dev/deps/nexus_deps/catalogs/bc250-bazzite.toml`.

```bash
dev/deps/run.sh                             # open it
dev/deps/run.sh --fix                       # open it and offer Fix as soon as the check is done
dev/deps/run.sh --remind                    # no window: the hourly check once, from a terminal
dev/deps/run.sh --sync-upstreams            # the list of emulators and firmware in line with the apps' pins again
dev/deps/install.sh                         # app menu entry, Desktop icon and the hourly reminder
dev/deps/install.sh --no-desktop-shortcut   # the same without the Desktop icon
dev/deps/install.sh --uninstall             # remove them and the reminder; --purge also the settings
```

Nexus Deps takes the place of two older tools. Installing it removes an installed Dependency Checker of the suite.
That means its copy, launcher, menu entry, Desktop icon and its weekly timer, `bc250-bazzite-update-reminder.timer`.
It also removes the development machine's hourly `nexus-dev-updates.timer`.

**Bazzite**, the first card, shows the Bazzite image the machine runs, with its version and build date. It shows
whether a newer image is installed and waits for a restart. It also shows when Bazzite's updater last ran.

That updater, `uupd`, runs every night by itself. It updates the image, Flatpaks, Homebrew and distroboxes. A new
image takes effect at the next boot, so an update can wait unnoticed for days. The card then turns to **Restart to
update**. It also warns when the updater failed on its last run, or has not run for over a week. This card only
reads, from `rpm-ostree status` and `systemctl`. It needs no root and no network.

A flattened image is one that does not boot from ostree, such as a PS5 image. There, `rpm-ostree` refuses with "not
booted via libostree". On such an image, the card shows the version from `/etc/os-release` and the running kernel
instead. Nothing waits for a restart there. Dnf updates the packages in place, in the System packages card below.
The updater line stays, since `uupd` still updates the Flatpaks, Homebrew and distroboxes.

**The machine's updates** follow, with a card per source the machine has. Each card shows what is newer, as
installed → new.

| Card | Asked with | Update runs |
|---|---|---|
| Bazzite image | `rpm-ostree upgrade --check` | `rpm-ostree upgrade`. The new image is used after a restart. |
| System packages (dnf), on a flattened image instead of Bazzite image | `dnf -q check-update` | `pkexec dnf upgrade -y` with the packages checked in its question. A new kernel is used after a restart. |
| Flatpak | `flatpak remote-ls --updates` | `flatpak update -y --noninteractive` |
| Homebrew | `brew update`, then `brew outdated` (formulae and casks) | `brew upgrade` |
| Rust | `rustup check` (the toolchains and rustup) | `rustup update` |
| Python venv (.venv-linux) | `pip list --outdated` and a dry run of `requirements-dev.txt` | `pip install --upgrade` of the outdated packages within `requirements-dev.txt` |
| Prime95 (mprime), when it is in `~/mprime` | mersenne.org's download page, against `~/mprime/.release` | Board Test's `install-requirements.sh --mprime` |

**Update** on a card asks first with its command. Then it runs the command in a window with its output. **Fix**
runs every card's command, with the packages' and tools' fixes. A source whose tool is missing has no card. A card
that could not be checked, for example offline, says why.

The venv card lists the packages that `requirements-dev.txt` holds back, such as MkDocs below 2. No Update installs
those. The card also lists the packages missing from the venv. The venv's `python` links to Bazzite's
`/usr/bin/python3`. So a Bazzite image with a newer Python leaves the venv without its packages, and the card says
so.

Bazzite's updater still installs the image, the Flatpaks and Homebrew's packages every night by itself. Update only
does it sooner. **Updates** in the header counts the updates, with the emulators' and the firmware's below.

The **i** beside each card's name says what its Update does. It also says how to handle what goes wrong, such as
going back to the version before, or keeping one package where it is. What needs care is said on the card itself,
in orange:

- a new **major** version, marked on its row, because it can change how a tool behaves
- a Bazzite image that is used after a restart
- a venv left on an older Python

An update that should not be installed by a click has no Update and shows **By hand**. An example is a Bazzite image
of a new Fedora release, such as 44 → 45. It changes the kernel, Mesa and the system's Python at once. So its i gives
the steps instead:

- read its release notes
- run `ujust update` in a terminal
- restart
- open Nexus Deps again for what the new Python left without packages
- how to roll back

**Emulators and firmware** follow. These are the programs and firmware the suite's apps use. Each is on a card with
the latest version and an i that says how to handle it. None of them is installed from here.

| Card | Asked | What an update means |
|---|---|---|
| RPCS3, PCSX2, PPSSPP, Vita3K, Xenia Canary, shadPS4 | GitHub's latest release | Each app installs the build it was tested with (its pin). When **Installed** is behind the pin, open the app and use its Install. When **On GitHub** is newer than the pin, the new build comes with a release of the app, after a test on a board. |
| DualSense firmware (and the Edge's) | Sony's firmware list | A new version since the last look. Connect the controller with a USB cable and update it in BC-250 Controller. |
| PS4 system software | Sony's PS4 update list | A new version since the last look. Update it on the console. |
| PS5 system software, PlayStation Portal | nothing a program can read | **On the device**: the i says where the device shows its updates. |

GitHub is asked with the GitHub CLI's login (`gh auth login`). Without a login, GitHub allows 60 requests an hour.
When those are used up, a card says that its hourly limit is used up, and until when.

An app installed without its emulator so far is no update, and the card says so. Sony's versions are news once. The
first look learns them, and a later one shows what changed.

The list is `dev/deps/nexus_deps/catalogs/upstreams.json`. It says which program each app uses and how its versions
compare. It is written by hand. The pins, repositories, names and launchers in it are read from the apps' code and
the portal's `apps.toml`. After a pin moves, `dev/deps/run.sh --sync-upstreams` brings the list in line. CI fails
until it is. CI also fails for a new emulator app the list does not hold.

**Python packages** are checked where each app runs. Nexus Deps finds every installed app by its launcher. It reads
the package versions in that app's Python environment, the suite's shared one or the app's own. A card shows the
version in each environment, and whether it meets the app's requirement. It also shows the latest version on PyPI.
A package that no installed app uses is shown as **Not needed**.

Each installed version is also looked up in [OSV.dev](https://osv.dev), which collects the GitHub, PyPA and NVD
advisories:

- A green **✓ CVE** means no known vulnerability.
- A red **✗ CVE** lists each vulnerability by its CVE ID, with the release that fixes it. Each ID links to
  [Snyk's vulnerability database](https://security.snyk.io/).
- **CVE ?** means the check could not run, because there is no network or no installed app has the package.

**External tools** are checked for availability on your PATH, in `~/.local/bin` and in Homebrew, where the apps
also look. Each app says whether it needs the tool (required) or uses it when it is there (optional). The links
open the app's chapter in the wiki. Tools that do their work only as root are marked **Needs root.**, and the apps
run them through sudo or pkexec. Where a tool has two forms, one is enough, such as Ookla's `speedtest` or
`speedtest-cli`. PS Remote Play's FFmpeg sits inside its native core. Nexus Deps asks it for its version through the
app's own Python.

### Fix

**Fix** sits beside the check button. It is on when something can be fixed, and its tooltip says what. A click
lists every command it will run and asks first. **No** changes nothing. **Yes** runs the commands one after the
other, in a window that shows their output. It stops at the first that fails. Then the check runs again.

- A Python package that is **Missing**, at a **Wrong version** or that **Needs update** is installed with pip. It
  goes into the environment of the app that needs it, at the version the apps in that environment allow. For a
  known vulnerability, it is at least the release that fixes it. Fix runs one command per environment.
- A missing tool an installed app **needs** is installed with Homebrew when Homebrew has it, with no restart.
  Otherwise, it is layered into the Bazzite image with `rpm-ostree install`, which may ask for your password. A
  layered package is there after a restart. The window says so and gives the command (`systemctl reboot`). Nexus
  Deps never restarts by itself. On a flattened image, the same package is installed with
  `pkexec dnf install -y`, and it is there at once.
- The machine's updates come after the packages and the tools. Fix runs each card's **Update** command, described
  above.
- A dnf step lists each of its packages with a checkbox in the question, all checked. Only the checked ones are
  installed or updated. **All of …** checks them all, or clears them when all were checked. **Yes** is off when
  nothing is left to run. Uncheck the kernel (`kernel`) to keep the one you have.
- Optional tools are left out, because the apps work without them. Some tools are in neither Homebrew nor Fedora,
  such as `ujust`, Steam or a tool an app brings itself. The app's chapter says how to get those.

The catalog says how each tool is installed, with `brew` (the Homebrew formula) and `rpm` (the Fedora package).

### The hourly reminder

The hourly reminder tells you when something needs you, even with the window closed. Every hour, Nexus Deps runs its
check without a window. When the machine was off at that hour, it runs at the next login. When something needs you,
a desktop notification says so. It names any of these:

- a Bazzite update waiting for a restart
- Bazzite's updater failing or not running
- the machine's updates, per source, with how many
- a venv left on an older Python
- the emulators and firmware with news, each piece of news once
- Python packages missing or to update
- tools an installed app needs

**Fix…** opens the window and asks to fix it, with the same question as the button. **Open Nexus Deps** opens the
window. When all is well, the reminder says nothing. It is a systemd user timer, `nexus-deps-reminder.timer`.
`install.sh` adds it, and `--uninstall` removes it. `systemctl --user disable --now nexus-deps-reminder.timer`
switches it off.

### What the statuses mean

Each card has one status, the most urgent that applies. The boxes at the top count them.

| Status | For | Meaning |
|---|---|---|
| **Up to date** | package | Installed where the apps need it, at PyPI's latest version, no known vulnerability. |
| **Update available** | package | PyPI has a newer version. Nothing is wrong. Newer versions come with an app release, after a test. Fix leaves it. |
| **Needs update** | package | An installed app needs a newer version, or a newer release fixes a known vulnerability. Fix updates it. |
| **Vulnerable** | package | An installed version has a known vulnerability that no release fixes yet. |
| **Wrong version** | package | An installed version does not meet an app's requirement. Fix installs one that does. |
| **Missing** | package | Not in the Python environment of an installed app that uses it. Fix installs it. |
| **Missing** | tool | Not found, and an installed app needs it. Fix installs it when the catalog says how. |
| **Not installed** | tool | Not found, but the installed apps only use it when it is there. |
| **Available** | tool | Found. The card shows where, and the version where the check can read one. |
| **Unsupported build** | tool | Found, but in a form the app cannot use, for example a flashrom without the internal programmer. |
| **Not needed** | both | No installed app uses it. |
| **Check failed** | package | The check could not reach PyPI (no network). |

The check sends the names and versions of the Python packages to PyPI and OSV.dev, nothing else.

## Garbage Remover

**Nexus Garbage Remover** (`dev/garbage/`) shows the garbage on this machine and deletes what you check. Garbage is
files nobody needs again, which fill up a disk over time. Our tools' own leftovers are not in it.
`tools/clean_caches.py` removes those before every local CI run.

The table lists each place that holds 1 MB of garbage or more, the largest first. The Trash shows whenever it holds
a file, however small:

| What | Where | Removed with |
|---|---|---|
| **Crash dumps** | `/var/lib/systemd/coredump` | `sudo find /var/lib/systemd/coredump -mindepth 1 -delete` |
| **Steam's crash reports** | `config/htmlcache/BrowserMetrics` in Steam's folder | `find <that folder> -mindepth 1 -delete` |
| **Trash** | `~/.local/share/Trash` | `find ~/.local/share/Trash -mindepth 2 -delete` |
| **Picture previews** | `~/.cache/thumbnails` | `find ~/.cache/thumbnails -mindepth 1 -delete` |
| **pip's download cache** | `~/.cache/pip` | `find ~/.cache/pip -mindepth 1 -delete` |
| **Homebrew's downloads** | `~/.cache/Homebrew` | `brew cleanup --prune=all` |

The size of Homebrew's row leaves out three folders, `api`, `bootsnap` and `tool-selection`. `brew cleanup` keeps
them, because Homebrew needs them to run.

Each row shows its size, and its tooltip says what the files are. Every row is checked at first. Uncheck a row to
keep that place. **Can be removed** shows the total, and **Checked** shows what **Delete** would remove. **Delete**
asks first and lists each place with its size. The crash dumps belong to the system, so for them the app asks for
your password once. The folders themselves stay, and only their content goes. The round symbol at the right of the
title looks again.

Every hour, or at the next login when the machine was off, the app measures the garbage without a window. From
1 GB on, a desktop notification says how much there is, with the largest places. It says so once a day, or sooner
when the garbage grew by another GB. **Open** opens the window. The notification deletes nothing. It is a systemd
user timer, `nexus-garbage-remover-reminder.timer`, that `install.sh` adds and `--uninstall` removes.
`systemctl --user disable --now nexus-garbage-remover-reminder.timer` switches it off.

## Marketing

**Nexus Marketing for BC-250** (`dev/marketing/`) writes an article that presents the portal and every app in it.
The article is a web page to share, in the suite's own design. It covers the portal and its apps only, never the
development apps. It has these parts:

- a hero with the headline and the buttons
- the board's numbers, when `copy.md` has them
- the number of apps, categories and quickfixes
- the portal, with a picture of its Settings page
- each category with a picture of its tab and a card per app
- **And more...**, the small touches of the portal and the apps
- the Portal Tour, the four steps to get it, and the links
- the license and the disclaimer from the suite's README, then the notes on the board's numbers

The board's numbers come from the **Specs** part of `copy.md`. Each line is a number, a space and its label.
A label that ends in `*` or `**` gets a small mark. Its note under **Spec notes** starts with the same mark.
The notes show at the bottom of the page.

The links go to the latest release, the wiki, the Portal Tour and the repository on GitHub. **Watch the tour**
and the video's picture play the video itself. Only the footer's link opens the Portal Tour page. Each app's card
opens its chapter of the wiki. An app that changes the board carries **Changes the board** on its card, in the portal's orange.

The article keeps up with the suite by itself. The apps, their order, their categories and their marks come from
`portal/apps.toml`. The words come from `dev/marketing/nexus_marketing/copy.md`, with a line for each category and
each app. The window lists every app of the portal with its line. **Apps with a line** turns red when an app has
none. The app's tests fail then too. The pencil after the line under the table opens `copy.md` in your
text editor. Write the new line there, then click the round symbol to read it again.

The pictures of the portal are stills of the real portal from this checkout, in `dev/marketing/images/shots/`.
`tools/portal_shots.py` takes them offscreen, the way `tools/portal_tour.py` records the Portal Tour. **Screenshots** shows whether they
are **Current**. It says **Out of date** when the portal changed since. Then the **Screenshots** pill takes them
again. For the hero's background, put a picture named `hero.webp` in the app's `images` folder. Without one, the
article draws a purple placeholder.

The pills:

- **Preview** opens the article in the browser. It is one file with the pictures and fonts inside, so a browser
  in a Flatpak shows it whole.
- **Export** writes the article to a new folder in the folder you choose. The folder holds `index.html` with its
  pictures and fonts. An export never writes over a folder that is there already.
  A git checkout, such as the website's folder, is the exception. There, Export writes the files straight into it,
  over the old ones. It removes nothing. Publish then commits and pushes them.
- **Screenshots** takes the stills of the portal again.
- **Text check** runs `tools/text_check.py` on `copy.md`. Its output shows below the table.
- **Publish** sends the article to the website. Its caption says how many files differ from the website's folder,
  or **Up to date**. The first click asks for the website's folder, the checkout of its repository. The app
  remembers it. Then Publish asks first. It writes the article into the folder and removes the pictures it no
  longer has. It commits only the article's files as "see the changelog" and pushes to GitHub. The website shows
  the new article a minute or two later. Other files in the folder, such as `.nojekyll`, stay as they are.
  **Other folder…** in the question takes another folder. The pill is off while the website is up to date.

The globe beside the round **i** opens the website in the browser. Its address comes from the website's folder. A
`CNAME` file there gives a domain of your own. Without one, the address is GitHub Pages' address of the repository,
such as `https://robertotorino.github.io/bc250-suite/`. The globe is off until Publish knows the folder.
