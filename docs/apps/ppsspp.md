<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 PPSSPP Manager](../assets/ppsspp/bc250-ppsspp-manager.webp){ .app-logo }

# BC-250 PPSSPP Manager

BC-250 PPSSPP Manager lets you play **PSP games** on the **AMD BC-250**. It uses [PPSSPP](https://www.ppsspp.org), an
open-source PSP emulator. The app installs the PPSSPP release it was tested with. It finds your games and adds them
to Steam. They then start from **Game Mode** like any other game.

Whether a game runs, and how well, is up to PPSSPP. Its [compatibility list](https://report.ppsspp.org) shows what
others found. The PSP is light work for the BC-250. Most games run at full speed.

## What you need

- **Your games**, dumped from your own discs. These are ISO, CSO or CHD images. Homebrew and games bought digitally
  come as a folder with the file `EBOOT.PBP`. The app never downloads games.
- **Steam**, started at least once, for Game Mode.
- About 50 MB for PPSSPP itself. PPSSPP keeps its saves, settings and memory stick games in `~/.config/ppsspp`.
  This folder is the PSP's memory stick.
- **fusermount** (FUSE), which Bazzite has. PPSSPP comes as an AppImage, which mounts itself with fusermount.
  Without it, the AppImage unpacks itself to a temporary folder on every start. That takes longer.

You need no firmware. PPSSPP plays the PSP's system software itself.

## Using it

The header has four pills:

- **PPSSPP version**, which opens the list of builds
- **PPSSPP Install**
- **PPSSPP Uninstall**
- **Refresh**, which reads everything again

Beside the title is a row of states. Each shows its name and a dot. The dot is green when all is well,
and red when not. Hold the pointer over a state to read it in full.

- **Installed**: the app's own state, such as **Not installed**
- **Controller**: **Controller connected**, or **No controller** when none is, checked again every few seconds
- **Steam**: green while Steam runs and is signed in, red when it is not

When the window opens without a controller, a desktop notification says so too. It asks you to switch the
controller on or press its PS button.

A game started from Steam reads the controller that is connected when it starts. So switch your controller on
first. A game in Steam starts only while Steam is signed in. So start Steam and sign in before you start a game.

Under the header are the links to **PPSSPP's release notes** and to this wiki. A second row of four pills follows.
Each pill shows what it is for on top and what it does under it:

- **Games Rename**
- **Games Uninstall**
- **Available in Steam**, which counts your games in Steam
- **Play time**, the time spent in all your games together, as PPSSPP counts it

The tooltip of **Play time** shows each game's time.

Below the pills are two columns. The first column has two short lines, **PPSSPP:** and **Game folder:**. Their
tooltips say more. The second column shows the **Installed version:** of PPSSPP.

Then comes a row of six tabs:

- **Your games**
- **Start game**
- **Memory cards**
- **Settings**
- **View logs**
- **Clear logs**

**Start game** and **Clear logs** are buttons.

The two state lines say this:

- **PPSSPP** says **Not installed.** or **Installed.**, with the button to use after it, on one line. The tooltip
  says which release is installed, or what Install takes. It also says when a newer PPSSPP is out.
- **Game folder** shows where the app looks for games. These are `~/Games/PSP` and a removable drive's `Games/PSP`.
  See [Where your games go](#where-your-games-go). You never choose or browse to a folder. The **i** beside the
  folders says what goes there. The tooltip says how many games are on PPSSPP's memory stick. A game may sit up to
  five folders deep.

The pills do this:

- **Install** downloads PPSSPP from its GitHub release, about 48 MB. Before it installs PPSSPP, it checks the file
  against the checksum this version of the app was tested with. When another release is in use, the tooltip and the
  log say so. **Install** then puts the tested release back in use.
- **Uninstall** removes PPSSPP again. PPSSPP's own folder, with your saves and settings, stays.
- **Games Rename** renames the ISO and CSO images after their `PARAM.SFO`. See [Renaming the
  files](#renaming-the-files).

### Versions

The version box in the header is a pill. A click opens the list of the PPSSPP builds you installed. A check mark
shows the one in use. Pick another build to put it in use. The games in Steam start whichever build is in use.
Every build shares PPSSPP's own folder with your saves and settings. **Manage versions…** under the list opens the
version manager. It has two parts:

- **Installed** lists every build in the app's folder. The one in use has a check mark. The one this version of the
  app was tested with is marked **Tested**. **Use** puts the chosen build in use. **Delete** removes it, but not the
  one in use. **Add** (**Custom build**) takes an AppImage of your own. The app does not check that file.
- **Download** lists the builds on GitHub. **Refresh** asks GitHub which releases have a Linux AppImage.
  **Download** fetches the chosen build and checks it against the SHA-256 that GitHub publishes for it. The build
  then sits beside the others. **Use** puts it in use.

Only the build marked **Tested** was tried on the board. To go back to it, pick it in the version pill's list. You
can also press **PPSSPP Install**. When the build is still there, Install puts it back in use without a download.

### Where your games go

The app has a folder of its own, `~/Games/PSP`. It makes the folder when it opens. You never choose or browse to a
folder. Put your disc images and your `EBOOT.PBP` folders there, or in folders inside it. They then show in the
table.

On a USB drive or an SD card, make a folder `Games/PSP`. The app looks there too while the drive is mounted. Bazzite
mounts a drive under `/run/media` or `/media`.

Version 1.0 and older had an **Add folder…** button. The app no longer looks in folders you added that way. Move
those games to `~/Games/PSP`.

### Your games

The table lists every game found. For each game it shows the title and the ID, such as ULUS… or UCES…. Both come
from the `PARAM.SFO` inside the image. The table also shows the game's kind and its file. There are two kinds of
games:

- **Disc images** in the game folders. The app reads an ISO or CSO for its title, ID and pictures. A **CHD** is
  listed under its file name. The app does not look into this MAME archive format. So Steam gets no pictures from a
  CHD, but PPSSPP plays it the same.
- **Memory stick games**, which are folders with the file `EBOOT.PBP`. They sit in the game folders and on
  PPSSPP's own memory stick (`~/.config/ppsspp/PSP/GAME`). PPSSPP keeps homebrew and installed games there. A
  game's update there is not a game to start. Its `PARAM.SFO` says category PG. PPSSPP lays the update over the disc
  game by itself.

**Games Uninstall**, the pill above, deletes the chosen game from the disk. A window first lists what would go, a
row each with its size. That is the disc image, or a memory stick game's own folder. It is also the game's Steam
shortcut when the game is in Steam. Every row is checked. Uncheck what you want to keep, then press **Delete
marked**. **Cancel** deletes nothing. The saves on the memory stick stay.

The app will not delete some games. One is a game at the top of a drive. Another is a game in a folder that holds
another game. The line under the tabs says so. Delete such a game by hand.

**PPSSPP settings**, under the games, opens PPSSPP's own window. It has PPSSPP's other settings, its controller
settings and its game list. A game runs from Steam. [**Start game**](#start-game) starts the chosen game there.

**Exit PPSSPP**, the first button under the games, closes PPSSPP from the app. Use it when the line under the tabs asks
you to close PPSSPP first. The button is on only while PPSSPP runs. A click ends PPSSPP at once, with no question. A
game that is running ends without saving.

#### Steam

Check the games you want in Steam and press **Update Steam**. The app adds them to Steam as non-Steam games. Each
game gets its own pictures from inside the image:

- the game's icon and background as its pictures
- its icon (`ICON0.PNG`) as the logo on the banner

The app takes out the games you unchecked and the games it no longer finds. Steam keeps these files in memory. So
Steam closes for the change and starts again in the background.

The info symbol under the list says in short what the boxes and **Start game** do. **Steam** in its text is a link.
It opens Steam's library, and Steam starts when it does not run.

In Steam each game's name starts with its system, for example **[PSP] Lumines**. So it stands apart in Steam's
menus from the same title on Steam or on another system. A game added under its title alone is renamed the next
time you press **Update Steam**. Until then, **Update Steam** is on for it. Steam sees the renamed game as a new
one. Its play time stays. A controller layout or collection you set for it in Steam has to be set again.

The games are in the library under **Non-Steam**. They are there on the desktop, in Big Picture Mode and in Game
Mode alike. They start the game full screen in PPSSPP. PPSSPP's pause menu then has an **Exit** entry. Steam's menu
and **Exit game** work as for any game.

Steam's overlay works over a game started from Steam, in Game Mode and on the desktop. Press **Shift+Tab** or the
**PS button**. You then see the game's page, its controller layout and its settings, without leaving the game.

A game started from Steam reads your controllers itself. [How it works](#how-it-works) explains both.

Change Steam from Desktop Mode. In Game Mode, Steam is the session itself and cannot close for the change.

##### Covers

A PSP game has no cover in the shape Steam's library uses. So the app draws one, with the game's icon and its title
on a dark background. You can enter a SteamGridDB API key under **Steam artwork…**. With the key, the app takes a
cover from SteamGridDB for each game instead. The background and the logo on the game's page stay the game's own.
[Covers from SteamGridDB](covers.md) explains these things:

- how to get the key
- how the app looks up a game
- how to use a cover of your own

#### A game in Steam more than once

The app checks whether a game has more than one shortcut in Steam. When one has, the line under the tabs names the
game and says how often it is there. The tooltip of its **In Steam** box says the same. **Update Steam** is then on
for it. It leaves one shortcut of each game, with the latest play time, and takes the others out. Its question says
how many double shortcuts go.

#### Start game

The tab beside Your games, **Start game**, is a button. Choose a game in the table and click it. The game starts
through Steam, as its shortcut in Steam starts it.

When Steam does not run, the app starts Steam first and waits until it is up. That takes a while. Then the app
starts the game. The line under the tabs says **Starting…** until PPSSPP runs. It says so when Steam did not start
the game. While PPSSPP already runs, the app starts no second game. The tab you were on stays open.

The app does not start a game that is not in Steam yet. The line under the tabs then says to check it and press
**Update Steam** first.

### Settings

This tab holds PPSSPP's settings that matter for playing. The app writes each one into PPSSPP's own settings file
the moment you change it. Everything else is in PPSSPP's own window, under **PPSSPP settings** below the games. The
tab scrolls when it is higher than the window.

- **Picture** holds these settings:
    - **Renderer**: Vulkan is PPSSPP's own choice on the BC-250. Pick OpenGL when a game shows faults.
    - **Internal resolution**: Automatic follows the screen. 3x fills a 1080p screen sharply, 6x a 4K one. A
      higher one asks more of the GPU.
    - **Stretch to the screen**
    - **Integer scaling**
    - **Texture filtering**: Nearest keeps pixel art sharp.
    - **Anisotropic filtering**
    - **VSync**
- **Game** holds **Frame skipping** and **Cheats**. Frame skipping leaves frames out to keep a slow game at full
  speed. Cheats turns on the cheats in PPSSPP's cheats folder.
- **Sound** holds the **Volume**.
- **Controller** holds two settings:
    - **Stick dead zone**: how far a stick moves before the game sees it. This helps with a stick that drifts.
    - **Stick sensitivity**: how far the PSP's stick goes for the stick's travel. PPSSPP's 1.10 reaches the edge
      a little sooner.
- **On screen** holds **Show FPS** and **Show speed**. They show in a corner of the picture.

Each setting shows what PPSSPP's settings file holds. While the file does not name a setting, you see PPSSPP's own
default. A value set in PPSSPP that the app does not offer is shown as it is. The app writes nothing while PPSSPP
runs. PPSSPP writes its settings back when it closes, over any change.

### Memory cards

A PSP game keeps each save as a folder on the memory stick, not on a card file. This tab lists the saves on
PPSSPP's memory stick (`~/.config/ppsspp/PSP/SAVEDATA`). For each save it shows these things:

- the game
- the save's title
- its folder
- its size
- when it was last written

Select a save to see its picture and what the game says is in it.

- **Export…** writes the selected saves to one `.zip`, each as its folder. You can keep the file or share it.
- **Import…** puts the saves from a `.zip` on the memory stick. A `.zip` exported here goes back as it is. A `.zip`
  with a save's files at the top goes in under the `.zip`'s own name. The app asks before it replaces a save that
  is there already.
- **Delete…** deletes the selected saves after the app asks. A deleted save is gone. Export it first to keep a copy.

The app imports and deletes nothing while PPSSPP runs. Close PPSSPP first.

### View logs

This tab shows everything the app said and did, with the time. The log holds these things:

- PPSSPP installed or removed
- what the app set up in PPSSPP
- files renamed
- every change to Steam
- every error

The same lines are in `~/.local/share/bc250-ppsspp-manager/bc250-ppsspp-manager.log`. The file turns over at 1 MB.
The app keeps the three older files. **Clear logs**, the tab beside View logs, empties the file and the View logs
tab. It also removes the three older files. The log holds what the app did. It holds neither your SteamGridDB key
nor anything personal.

Two buttons sit above the log. **BC-250 PPSSPP Manager** shows the app's own log. **PPSSPP** shows what PPSSPP
printed while the last games ran. The run wrapper writes it to `~/.local/share/bc250-ppsspp-manager/emulator.log`.
Every line starts with its time and a level: INFO, WARNING or ERROR. Every line shows your home folder as `~`. This file also turns over at 1 MB, and the app keeps
the three older files. With **PPSSPP** chosen, **Clear logs** empties that log and removes its three older files.

Each game's part opens with these lines, written before the game starts:

- how the wrapper started PPSSPP
- the PPSSPP build
- the board by its name, with its BIOS
- the processor, its threads and the kernel
- the game and where it is
- each controller, or a warning that none is connected
- the session, such as Wayland on KDE
- each connected display with its name and preferred mode
- the desktop's mode, such as 1920x1080 at 120 Hz
- the memory and swap left

It ends with these lines:

- the exit code and the signal that ended it, as an error for a crash
- how long the game ran
- the memory and swap left
- the system log's out-of-memory kills, GPU hangs, resets and faults, and core dumps while the game ran

A line PPSSPP prints is an ERROR when it starts with error or tells of a crash. It is a WARNING when it starts with
warning or tells of something that failed. A game can be killed together with the wrapper that logs it. The next
start then says so first, with what the system log has from that start on.

## Renaming the files

A dumped disc often gets a meaningless file name. **Games Rename** fixes that. It opens a window with the ISO and CSO
images the app found. For each image it shows the name it would get from its own `PARAM.SFO`. Pick one of eight
naming templates, such as `ULJM05437 - Ever17.iso` or `Ever17 [ULJM05437].iso`. Then press **Rename all**.

The window shows the selected game's pictures. A click cycles ICON0, PIC0 and PIC1. For a title in another language
you can type a **translation**. The new file name then uses it as the title. **Translate** opens the title in Google
Translate. The app never takes over a name that another file already has. It removes characters that are illegal in
file names.

The app never renames a memory stick game, because its file must stay `EBOOT.PBP`. It does not read a CHD. With no
ISO or CSO image found, **Games Rename** is off. A renamed game that is in Steam needs **Update Steam** afterward,
because its shortcut names the file.

This window was once the standalone app **Bazzite UMD File Renamer**. BC-250 PPSSPP Manager now holds it. Installing PPSSPP
Manager removes the standalone app and adopts its saved naming template. Your images stay where they are.

## From a terminal

`bc250-ppsspp-run` starts the installed PPSSPP with the options you give it. The Steam shortcuts use it. So they keep
working when a newer version of the app brings a newer PPSSPP.

```bash
bc250-ppsspp-run --fullscreen --pause-menu-exit "/path/to/game.iso"   # a game full screen (Steam)
bc250-ppsspp-run "/path/to/game.iso"                                  # a game, as PPSSPP is set up
bc250-ppsspp-run                                                      # PPSSPP's own window
```

The run wrapper stays while PPSSPP runs. It passes a stop from Steam on to PPSSPP, and ends with PPSSPP's exit
code. What PPSSPP prints goes to `~/.local/share/bc250-ppsspp-manager/emulator.log`, not to the terminal. The
View logs tab shows it.

## New PPSSPP releases

Each version of the app was tested with one PPSSPP release, the one **Install** puts in. When the window opens, the
app asks GitHub for PPSSPP's newest release. When that release is newer, the PPSSPP line's tooltip and the log say
so. They link to what is new. The app does not install it by itself, but the [version manager](#versions) can.

A newer PPSSPP comes with a newer version of the app, once it has been tried. You get it from the
[portal](../portal.md). After you update the app, the tooltip and the log say so, and **Install** brings it.

The app turns off PPSSPP's own notice of a new release, as described below. On Linux PPSSPP does not update itself.

## How it works

The Steam shortcuts start `bc250-ppsspp-run`, which starts PPSSPP. Two things change when Steam is the one that
starts it. Started from outside Steam, PPSSPP runs as it is. That is the case with **PPSSPP settings** or with
`bc250-ppsspp-run` in a terminal.

Once PPSSPP is installed, the app turns off PPSSPP's notice of a newer release. It does so each time the window
opens, while PPSSPP does not run. The setting is in `PSP/SYSTEM/ppsspp.ini` on PPSSPP's memory stick. A newer PPSSPP
comes with the app instead. Everything else in the file stays as PPSSPP wrote it. What changed goes to the log.

### Controllers

When Steam starts a game, it tells the game's controller library (SDL) to ignore the controllers Steam handles
itself. In their place it gives the game Steam's virtual controller (Steam Input). PPSSPP then sees only that
virtual controller. On the desktop it follows the layout Steam has active. That may be Steam's desktop layout, with
mouse and keys.

So the run wrapper undoes this. While a real controller is connected, PPSSPP reads that controller itself. It
leaves Steam's virtual one (USB ID `28DE:11FF`) out. The PS button stays Steam's.

Without a real controller, the wrapper leaves Steam's choice as it is. An example is a Steam Deck, whose own
controls exist only as Steam's virtual controller. You map the controls in PPSSPP's own window. Open **PPSSPP
settings**, then **Settings > Controls**.

### A game renamed, moved or gone

A game you rename or move after it went into Steam keeps its mark. The app knows each game in Steam by its code.
Without a code, it uses the file's size. So on **Refresh** it finds the game again under its new name, checked. The
line under the tabs says so. **Update Steam** then takes the old shortcut out and puts the game in under its new
name.

A shortcut can point to a game that is no longer there. The game may be deleted, or on a drive that is not in. Then
the shortcut does not start PPSSPP. Instead, a window says which file is missing and what to do. The window closes
by itself, so Steam sees the game end.

### Steam's overlay on the desktop

The KDE desktop of Bazzite is a Wayland session. PPSSPP, an SDL program, may open its window through Wayland. But
Steam on the desktop only sees windows that go through X11. XWayland is the X11 server within the Wayland session.
A game window Steam cannot see has no overlay. **Shift+Tab** and the **PS button** then do nothing.

So when Steam starts a game on the Wayland desktop, the run wrapper has PPSSPP open its window through XWayland
(`SDL_VIDEODRIVER=x11`). Steam's overlay then works as in any other game. Game Mode runs every game through X11
already.

## What goes where

| What | Where |
|---|---|
| The app | `~/.local/share/bc250-ppsspp-manager/app` |
| PPSSPP | `~/.local/share/bc250-ppsspp-manager/emulator` |
| PPSSPP's saves, settings, memory stick games | `~/.config/ppsspp` (the PSP's memory stick) |
| Your games | `~/Games/PSP` (the app's own folder), and `Games/PSP` on a removable drive |
| The app's settings | `~/.config/bc250-ppsspp-manager` |
| The app's log | `~/.local/share/bc250-ppsspp-manager/bc250-ppsspp-manager.log` |
| What PPSSPP printed while a game ran | `~/.local/share/bc250-ppsspp-manager/emulator.log` |
| The Steam shortcuts | Steam's `shortcuts.vdf` and `grid` folder, per Steam user |
| The pictures found on SteamGridDB | `~/.local/share/bc250-ppsspp-manager/covers` |
| Launchers | `~/.local/bin/bc250-ppsspp-manager`, `~/.local/bin/bc250-ppsspp-run` |

PPSSPP can keep its memory stick elsewhere, with its `--root` option and its settings. The app reads the standard
place.

## Install and remove

Install the app from the [portal](../portal.md), where it is under Gaming. Removing it takes out the app and the
PPSSPP it installed. PPSSPP's own folder stays, with your saves, settings and memory stick games. Your games stay
too. The games in Steam then no longer start. So take them out first. Uncheck them and press **Update Steam**.

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app menu entry only, no icon on the Desktop
./install.sh --uninstall             # remove the app and the PPSSPP it installed; keeps its settings and log
./install.sh --uninstall --purge     # also remove its settings, covers and log
```

## Disclaimer

The BC250 Bazzite Suite is an independent community project, not affiliated with or endorsed by AMD, ASRock, the Bazzite /
Universal Blue project, Sony, Microsoft, Valve, or the makers of the emulators and the other programs the apps work
with. BC-250 is AMD's product name and Bazzite the Universal Blue project's. PlayStation, PS4, PS5, PS3, PS2, PSP, PS
Vita, PSN, DualSense and Remote Play are Sony's; XBOX, XBOX 360, XBOX Cloud Gaming, Game Pass and Windows are
Microsoft's; Steam, Steam Deck and Big Picture are Valve's; the names of the emulators (shadPS4, RPCS3, PPSSPP, PCSX2,
Vita3K, Xenia) and of HelixSR and DirectMesh belong to their owners. The suite uses them only to say what its apps work with.

## License

GPL-3.0-or-later. PPSSPP is a separate program under its own license (GPL-2.0-or-later). The app downloads it from
its own release.
