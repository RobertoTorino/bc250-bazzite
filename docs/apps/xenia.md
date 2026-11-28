<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Xenia Manager](../assets/xenia/bc250-xenia-manager.webp){ .app-logo }

# BC-250 Xenia Manager

BC-250 Xenia Manager lets you play **XBOX 360 games** on the **AMD BC-250**. It uses [Xenia](https://xenia.jp), an XBOX
360 emulator, in its [Xenia Canary](https://github.com/xenia-canary/xenia-canary) builds. The app installs a tested
build. It finds your games and adds them to Steam. They then start from **Game Mode** like any other game.

Xenia's Linux build is experimental. Not every game starts, and a game that runs on Windows may not run here.
Whether a game runs, and how well, is up to Xenia. Its
[compatibility list](https://github.com/xenia-canary/game-compatibility/issues) shows what is known.

## What you need

- **Your games**, from your own discs and console. The app takes these kinds:
    - disc images (`.iso`)
    - discs unpacked to a folder with a `default.xex`
    - Xenia's `.zar` archives
    - Games on Demand and Arcade packages, as the console keeps them

    The app never downloads games.
- **Steam**, started at least once, for Game Mode.
- **FUSE**, which Bazzite has. Xenia comes as an AppImage, which mounts itself with fusermount. Without
  fusermount, the AppImage unpacks itself to a temporary folder on every start.
- No BIOS or firmware. Xenia does not need the console's.

## Using it

The header has four pills:

- **Xenia version**, which opens the list of builds
- **Xenia Install**
- **Xenia Uninstall**
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

Under the header are the links to **Xenia's release notes** and to this wiki. A second row of two pills follows.
Each pill shows what it is for on top and what it does under it:

- **Games Uninstall**
- **Available in Steam**, which counts your games in Steam

Below the pills are two columns. The first column has two short lines, **Xenia:** and **Game folder:**. Their
tooltips say more. The second column shows the **Installed version:** of Xenia.

Then comes a row of six tabs:

- **Your games**
- **Start game**
- **Memory cards**
- **Settings**
- **View logs**
- **Clear logs**

**Start game** and **Clear logs** are buttons.

The two state lines say this:

- **Xenia** says **Not installed. Install it with the Install button.** or **Installed. Uninstall with the
  Uninstall button.** The tooltip says which build is installed, or what Install takes. It also says when a newer
  build is out.
- **Game folder** shows where the app looks for games. These are `~/Games/XBOX360` and a removable drive's
  `Games/XBOX360`. [Where your games go](#where-your-games-go) says more. You never choose or browse to a folder.
  The **i** beside the folders says what goes there. A game may sit up to six folders deep.

The pills do this:

- **Install** downloads Xenia, about 16 MB. Before it installs Xenia, it checks the file against the checksum of the
  build the app was tried with. When another build is in use, the tooltip and the log say so. **Install** then puts
  the tried build back in use.
- **Uninstall** removes Xenia again. Xenia's own folder stays, with its settings, saves and installed content.

### Versions

The version box in the header is a pill. A click opens the list of the Xenia builds you installed. A check mark
shows the one in use. Pick another build to put it in use. The games in Steam start whichever build is in use.
Every build shares Xenia's own folder, with the settings, saves and installed content. **Manage versions…** under
the list opens the version manager. It has two parts:

- **Installed** lists every build in the app's folder. The one in use has a check mark. The one this version of the
  app was tried with is marked **Tested**. **Use** puts the chosen build in use. **Delete** removes it, but not the
  one in use. **Add** (**Custom build**) takes an AppImage of your own. The app does not check that file.
- **Download** lists the newest Canary builds on GitHub. **Refresh** asks GitHub which builds there are.
  **Download** fetches the chosen build and checks it against the SHA-256 that GitHub publishes for it. The build
  then sits beside the others. **Use** puts it in use.

Only the build marked **Tested** was tried on the board. To go back to it, pick it in the version pill's list. You
can also press **Xenia Install**. When the build is still there, Install puts it back in use without a download.

### Where your games go

The app has a folder of its own, `~/Games/XBOX360`. It makes the folder when it opens. You never choose or browse to
a folder. Put your games there, or in folders in it, and they show in the table.

On a USB drive or an SD card, make a folder `Games/XBOX360`. The app looks there too while the drive is mounted.
Bazzite mounts a drive under `/run/media` or `/media`.

Until version 1.0, you could add other folders in the app with **Add folder…**. The app no longer looks in those
folders. Move those games to `~/Games/XBOX360`.

### Your games

The table lists every game found:

- A **disc image** is a game when it is an XBOX 360 disc. The app looks for the disc's mark where Xenia looks for
  it. The table lists the disc under its file's name.
- An **unpacked disc** is its `default.xex`, listed under its folder's name. The other `.xex` files in that folder
  are its parts. Any other `.xex` is listed under its own name.
- A **.zar** archive is listed under its file's name. The app does not look into it.
- A **Games on Demand** or **Arcade** package is listed under the name in its header. Keep it in the folders the
  console made, `<title ID>/00007000/` or `<title ID>/000D0000/`. Saves, downloadable content and title updates are
  not games. The app leaves them out.

The **Title ID** column shows the game's ID, such as 4D5307E6. The app reads it from the `.xex` or the package,
where it can.

**Games Uninstall**, the pill above, deletes the chosen game from the disk. A window first lists what would go, a
row each with its size:

- the game's file or folder
- for a Games on Demand or Arcade title in the console's layout, a row for each part of its title ID folder
- its Steam shortcut, when the game is in Steam

A title ID folder's parts are the game, its title updates and its add-ons. So you can keep the add-ons.

Every row is checked. Uncheck what you want to keep, then press **Delete marked**. **Cancel** deletes nothing.
Xenia's content folder stays, with the saves.

The app will not delete some games. One is a game at the top of a drive. Another is a game in a folder that holds
another game. For such a game, the line under the tabs says so. Delete it by hand.

**Xenia settings**, under the games, opens Xenia's own window. It has Xenia's other settings, its profiles and its
installed content. A game runs from Steam. [**Start game**](#start-game) starts the chosen game there.

**Exit Xenia**, the first button under the games, closes Xenia from the app. Use it when the line under the tabs asks
you to close Xenia first. The button is on only while Xenia runs. A click ends Xenia at once, with no question. A game
that is running ends without saving.

#### Steam

Check the games you want in Steam and press **Update Steam**. The app adds them to Steam as non-Steam games. It
takes out the games you unchecked and the games it no longer finds. Steam keeps these files in memory. So Steam
closes for the change and starts again in the background.

The app draws the pictures on the tiles from its icon. Each picture has the game's title, on a background in the
icon's color. The icon is the logo on the banner.

The info symbol under the list says in short what the boxes and **Start game** do. **Steam** in its text is a link.
It opens Steam's library, and Steam starts when it does not run.

In Steam each game's name starts with its system, for example **[X360] Halo 3**. So it stands apart in Steam's
menus from the same title on Steam or on another system.

The games are in the library under **Non-Steam**. They are there on the desktop, in Big Picture Mode and in Game
Mode alike. They start the game alone in Xenia, full screen.

Steam's overlay works over a game started from Steam, in Game Mode and on the desktop. Press **Shift+Tab** or the
**Steam button**. You then see the game's page, its controller layout and its settings, without leaving the game.

Change Steam from Desktop Mode. In Game Mode, Steam is the session itself and cannot close for the change.

##### Covers

You can enter a SteamGridDB API key under **Steam artwork…**. One key serves the whole suite. With the key, the app
takes all four pictures from SteamGridDB instead of drawing them:

- the cover
- the wide picture
- the banner
- the logo

A picture SteamGridDB does not have stays drawn. [Covers from SteamGridDB](covers.md) explains these things:

- how to get the key
- how the app looks up a game
- how to use pictures of your own

#### A game in Steam more than once

The app checks whether a game has more than one shortcut in Steam. When one has, the line under the tabs names the
game and says how often it is there. The tooltip of its **In Steam** box says the same. **Update Steam** is then on
for it. It leaves one shortcut of each game, with the latest play time, and takes the others out. Its question says
how many double shortcuts go.

#### Start game

The tab beside Your games, **Start game**, is a button. Choose a game in the table and click it. The game starts
through Steam, as its shortcut in Steam starts it.

When Steam does not run, the app starts Steam first and waits until it is up. That takes a while. Then the app
starts the game. The line under the tabs says **Starting…** until Xenia runs. It says so when Steam did not start
the game. While Xenia already runs, the app starts no second game. The tab you were on stays open.

The app does not start a game that is not in Steam yet. The line under the tabs then says to check it and press
**Update Steam** first.

### Settings

The tab scrolls when it is higher than the window.

This tab holds Xenia's settings that matter for playing. The app writes each one into Xenia's own settings file the
moment you change it. That file is `xenia-canary.config.toml` in Xenia's folder. Xenia reads it when it starts. A
game's own settings file in Xenia comes before these. Everything else is in Xenia's own window, under **Xenia
settings** below the games.

- **Picture** holds these settings:
    - **Graphics**: Vulkan is the Linux build's, and Automatic picks it.
    - **Resolution scale**: a multiple of the game's own picture, mostly 1280 × 720. A higher one asks much more of
      the GPU, and breaks some games.
    - **Anti-aliasing**: FXAA smooths jagged edges after the game has drawn.
    - **Scaling and sharpening**: Bilinear, Contrast Adaptive Sharpening or FidelityFX Super Resolution.
    - **Keep the picture's shape**: bars where the screen's shape differs. Off, Xenia stretches the picture.
    - **VSync**
- **Speed** holds two settings:
    - **Frame limit**: with VSync on, **As the game** means 60.
    - **Readback resolve**: for a game that shows wrong or missing effects. Fast reads them a frame late. Full reads
      them exactly and slowly.
- **Sound** holds two settings:
    - **Sound output**: SDL is the Linux build's, and Automatic picks it.
    - **Mute**
- **Console** holds three settings:
    - **Arcade license**: for an XBOX Live Arcade game. Full version unlocks the whole game where its package licenses
      only the trial. All licenses also unlocks its other content.
    - **Achievement messages**
    - **Guide button to the game**: the controller's guide button reaches the game. Off, Steam keeps it.

Each setting shows what Xenia's settings file holds. While there is no file or no line for a setting, you see
Xenia's own default. A value set in Xenia that the app does not offer is shown as it is. The app writes nothing
while Xenia runs.

### Memory cards

An XBOX 360 game keeps each saved game as a folder, not on a card file. This tab lists the saved games in Xenia's
content folder, for every profile. They are in `~/.local/share/Xenia/content/<profile>/<game's code>/00000001`. For
each saved game it shows these things:

- the game
- the save's name
- its folder
- its size
- when it was last written

Three buttons act on the selected saved games:

- **Export…** writes the selected saved games to one `.zip`, each under its game's code. Beside each it puts what
  Xenia notes of it. You can keep the file or share it.
- **Import…** puts the saved games from such a `.zip` under the first profile. Xenia needs a profile for that. Start
  Xenia once with **Xenia settings** and make one. The app asks before it replaces a saved game that is there
  already.
- **Delete…** deletes the selected saved games after the app asks. A deleted one is gone. Export it first to keep a
  copy.

The app imports and deletes nothing while Xenia runs. Close Xenia first.

### View logs

This tab shows everything the app said and did, with the time. The log holds these things:

- Xenia installed or removed
- the games deleted
- every change to Steam
- every error

The same lines are in `~/.local/share/bc250-xenia-manager/bc250-xenia-manager.log`. The file turns over at 1 MB.
The app keeps the three older files. **Clear logs**, the tab beside View logs, empties the file and the View logs
tab. It also removes the three older files. The log holds what the app did. It holds neither your SteamGridDB key
nor anything personal.

Two buttons sit above the log. **BC-250 Xenia Manager** shows the app's own log. **Xenia** shows what Xenia
printed while the last games ran. The run wrapper writes it to `~/.local/share/bc250-xenia-manager/emulator.log`.
Every line starts with its time and a level: INFO, WARNING or ERROR. Every line shows your home folder as `~`. This file also turns over at 1 MB, and the app keeps
the three older files. With **Xenia** chosen, **Clear logs** empties that log and removes its three older files.

Each game's part opens with these lines, written before the game starts:

- how the wrapper started Xenia
- the Xenia build
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

A line Xenia prints is an ERROR when it starts with error or tells of a crash. It is a WARNING when it starts with
warning or tells of something that failed. A game can be killed together with the wrapper that logs it. The next
start then says so first, with what the system log has from that start on.

## From a terminal

`bc250-xenia-run` starts the installed Xenia with the options you give it. The Steam shortcuts use it. So they
keep working when a newer version of the app brings a newer Xenia. Xenia's options take the form `--name=value`.

```bash
bc250-xenia-run --fullscreen=true "/path/to/game.iso"   # a game full screen (Steam)
bc250-xenia-run "/path/to/game.iso"                     # a game in a window
bc250-xenia-run                                         # Xenia's own window
```

The run wrapper stays while Xenia runs. It passes a stop from Steam on to Xenia, and ends with Xenia's exit
code. What Xenia prints goes to `~/.local/share/bc250-xenia-manager/emulator.log`, not to the terminal. The
View logs tab shows it.

## New Xenia builds

Xenia has no stable releases. Xenia Canary publishes a build for almost every change. Each build is named after its
change, such as `54386cb`. Each version of the app was tried with one build, the one **Install** puts in.

When the window opens, the app asks GitHub for the newest build. When that build came out after the app's build,
the Xenia line's tooltip and the log say so. They link to what is new. The app does not install it by itself, but
the [version manager](#versions) can.

A newer build comes with a newer version of the app, once it has been tried. You get it from the
[portal](../portal.md). After you update the app, the tooltip and the log say so, and **Install** brings it.

## How it works

The Steam shortcuts start `bc250-xenia-run`, which starts Xenia. Started from outside Steam, Xenia runs as it is.
That is the case with **Xenia settings** or with `bc250-xenia-run` in a terminal.

### Controllers

When Steam starts a game, it tells the game's controller library (SDL) to ignore the controllers Steam handles
itself. In their place it gives the game Steam's virtual controller (Steam Input). Xenia then sees only that
virtual controller. On the desktop it follows the layout Steam has active. That may be Steam's desktop layout, with
mouse and keys.

So the run wrapper, `bc250-xenia-run`, undoes it. While a real controller is connected, Xenia reads that controller
itself. It leaves Steam's virtual one (USB ID `28DE:11FF`) out.

Without a real controller, the wrapper leaves Steam's choice as it is. That is the case on a Steam Deck, whose own
controls exist only as Steam's virtual controller.

### A game renamed, moved or gone

A game you rename or move after it is in Steam keeps its mark. The app knows each game in Steam by its code. A game
without a code it knows by its file's size. So on **Refresh** the app finds the game again under its new name,
checked. The line under the tabs says so. **Update Steam** then takes the old shortcut out and puts the game in
under its new name.

A shortcut to a game that is no longer there does not start Xenia. The game may be deleted, or on a drive that is
not in. A window then says which file is missing and what to do. It closes by itself, so Steam sees the game end.

### Steam's overlay on the desktop

Xenia's window goes through X11 by itself. On the KDE desktop of Bazzite, that is XWayland. So Steam's overlay sees
the window on the desktop too. The run wrapper has nothing to change for it.

## What goes where

| What | Where |
|---|---|
| The app | `~/.local/share/bc250-xenia-manager/app` |
| Xenia | `~/.local/share/bc250-xenia-manager/emulator` |
| Xenia's settings, saves and installed content | `~/.local/share/Xenia` (Xenia's own folder) |
| Your games | `~/Games/XBOX360` (the app's own folder), and `Games/XBOX360` on a removable drive |
| The app's settings | `~/.config/bc250-xenia-manager` |
| The app's log | `~/.local/share/bc250-xenia-manager/bc250-xenia-manager.log` |
| What Xenia printed while a game ran | `~/.local/share/bc250-xenia-manager/emulator.log` |
| The Steam shortcuts | Steam's `shortcuts.vdf` and `grid` folder, per Steam user |
| The pictures found on SteamGridDB | `~/.local/share/bc250-xenia-manager/covers` |
| Launchers | `~/.local/bin/bc250-xenia-manager`, `~/.local/bin/bc250-xenia-run` |

## Install and remove

Install the app from the [portal](../portal.md), where it is under Gaming. Removing the app also removes the Xenia
it installed. Xenia's own folder stays, with your settings, saves and installed content. Your games stay too. The
games in Steam then no longer start. So take them out first. Uncheck them and press **Update Steam**.

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app menu entry only, no icon on the Desktop
./install.sh --uninstall             # remove the app and the Xenia it installed; keeps its settings and log
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

GPL-3.0-or-later. Xenia is a separate program under its own license (BSD-3-Clause). The app downloads it from
Xenia's own releases.
