<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Vita3K Manager](../assets/vita3k/bc250-vita3k-manager.webp){ .app-logo }

# Vita3K Manager

Vita3K Manager lets you play **PS Vita games** on the **AMD BC-250**. It uses [Vita3K](https://vita3k.org), an
open-source PS Vita emulator. The app installs the Vita3K build it was tried with. It installs the PS Vita's
firmware and your games through Vita3K. It adds the games to Steam. They then start from **Game Mode** like any
other game.

Whether a game runs, and how well, is up to Vita3K. Its [compatibility list](https://vita3k.org/compatibility.html)
shows what others found.

## What you need

- **Your games**, dumped from your own PS Vita. A game comes as a `.vpk` or `.zip`, as a `.pkg` with its zRIF
  license key, or as a dumped game folder. The app never downloads games.
- **The PS Vita's firmware**, the PS Vita's system software. Vita3K needs it and its font package to start most
  games. The app cannot ship them. Each is a file named `PSP2UPDAT.PUP`:
    - the firmware, which you download [here](https://www.playstation.com/en-us/support/hardware/psvita/system-software/)
      (official page)
    - the font package, which you download
      [here](http://dus01.psp2.update.playstation.net/update/psp2/image/2019_0924/sd_8b5f60b56c3da8365b973dba570c53a5/PSP2UPDAT.PUP?dest=us)
      (Sony's file)
    - optionally the preinstalled apps, which you download
      [here](http://dus01.psp2.update.playstation.net/update/psp2/image/2022_0209/pre_efd1ef6c1cc2fe92e72e9e783e421237/PSP2UPDAT.PUP?dest=us)
      (Sony's file)

    Then put the files in `~/Games/Vita/Firmware`. The app gives them to Vita3K by itself, as
    [Using it](#using-it) explains.
- **Steam**, started at least once, for Game Mode.
- About 86 MB for Vita3K itself. Its settings go in `~/.config/Vita3K`. The PS Vita's storage holds the firmware,
  the installed games and the saves. It is in `~/.local/share/Vita3K/Vita3K`.
- **fusermount** (FUSE), which Bazzite has. Vita3K comes as an AppImage, which mounts itself with fusermount.
  Without it, the AppImage unpacks itself to a temporary folder on every start. That takes longer.

## Using it

The header has four pills:

- **Vita3K version**, which opens the list of builds
- **Vita3K Install**
- **Vita3K Uninstall**
- **Refresh**, which reads everything again

Beside the title is a row of states. Each shows its name and a dot. The dot is green when all is well,
and red when not. Hold the pointer over a state to read it in full.

- **Installed**: the app's own state, such as **Not installed**
- **Controller**: **Controller connected**, or **No controller** when none is, checked again every few seconds
- **Steam**: green while Steam runs and is signed in, red when it is not

A game started from Steam reads the controller that is connected when it starts. So switch your controller on
first. A game in Steam starts only while Steam is signed in. So start Steam and sign in before you start a game.

Under the header are the links to **Vita3K's release notes** and to this wiki. A second row of four pills follows.
Each pill shows what it is for on top and what it does under it:

- **Games Install**
- **Games Uninstall**
- **Available in Steam**, which counts your games in Steam
- **Play time**, the time spent in all your games together, as Vita3K counts it

The tooltip of **Play time** shows each game's time.

Below the pills are two columns. The first column has three short lines, **Vita3K:**, **Firmware:** and **Game
folder:**. Their tooltips say more. The second column shows the **Installed version:** of Vita3K.

Then comes a row of six tabs:

- **Your games**
- **Start game**
- **Memory cards**
- **Settings**
- **View logs**
- **Clear logs**

**Start game** and **Clear logs** are buttons.

The three state lines say this:

- **Vita3K** says **Not installed. Install it with the Install button.** or **Installed. Uninstall with the
  Uninstall button.** The tooltip says which build is installed, or what Install takes. It also says when a newer
  build is out.
- **Firmware** says **Installed.** once Vita3K has the system software and the font package. It says **Partly
  installed.** with one of the two, and **Not installed.** with neither. The tooltip names each part. The parts are
  the system software, the font package and the preinstalled apps (optional). The **i** beside the line says where
  the files go. It links to where you download each file.
- **Game folder** shows the app's own folder, `~/Games/Vita`, and a removable drive's `Games/Vita`. The **i** beside
  the folders says what goes there. The tooltip says how many games Vita3K has installed.

Put the `PSP2UPDAT.PUP` files you downloaded in `~/Games/Vita/Firmware`. Sony names all three files the same. So you
may put each one in a folder of its own there.

Once Vita3K is installed, the app gives the files to Vita3K by itself. It does so when the window opens and on
**Refresh**. It gives the largest file first, then the others one after the other. The line under the tabs then
says which part each file was.

The app gives each file once, as it is. That holds also for a file Vita3K could not use. A file you replace is given
again. The files stay in the folder.

The pills do this:

- **Install** downloads Vita3K from GitHub, about 86 MB. Before it installs Vita3K, it checks the file against the
  checksum this version of the app was tried with. When another build is in use, the tooltip and the log say so.
  **Install** then puts the tried build back in use.
- **Uninstall** removes Vita3K again. Vita3K's own folders stay, with the firmware, your games, saves and settings.
- **Games Install** installs one of your games. Its window opens in the game folder. It offers two ways:
    - **From a file**: the app hands a `.vpk` or `.zip` to Vita3K. Vita3K installs it and then starts it in its own
      window. A `.pkg` asks for the game's zRIF license key. Vita3K then installs it without a window.
    - **From a dumped folder**: Vita3K installs the folder's game and starts it in its own window.

    The list shows the game once it is installed.

### Versions

The version box in the header is a pill. A click opens the list of the Vita3K builds you installed. A check mark
shows the one in use. Pick another build to put it in use. The games in Steam start whichever build is in use.
Every build shares Vita3K's own folder, with the firmware, games, saves and settings. **Manage versions…** under the
list opens the version manager. It has two parts:

- **Installed** lists every build in the app's folder. The one in use has a check mark. The one this version of the
  app was tried with is marked **Tested**. **Use** puts the chosen build in use. **Delete** removes it, but not the
  one in use. **Add** (**Custom build**) takes an AppImage of your own. The app does not check that file.
- **Download** lists the newest builds on GitHub. **Refresh** asks GitHub which builds there are. **Download**
  fetches the chosen build and checks it against the SHA-256 that GitHub publishes for it. The build then sits
  beside the others. **Use** puts it in use.

Only the build marked **Tested** was tried on the board. To go back to it, pick it in the version pill's list. You
can also press **Vita3K Install**. When the build is still there, Install puts it back in use without a download.

### Your games

The table lists every game Vita3K has installed. For each game it shows these things:

- the title and the ID, such as PCSB… or PCSE…, from the game's own files
- its version
- its folder in Vita3K's storage (`ux0/app`)

**Games Uninstall**, the pill above, deletes the chosen game from the disk. A window first lists what would go, a
row each with its size:

- the game in Vita3K's storage
- its update and extra content, when they are there
- its Steam shortcut, when the game is in Steam

Every row is checked. Uncheck what you want to keep, then press **Delete marked**. **Cancel** deletes nothing. The
saves stay.

The app deletes only a game in Vita3K's storage. For any other game, the line under the tabs says so. Delete such a
game by hand.

**Vita3K settings**, under the games, opens Vita3K's own window. It has Vita3K's other settings, its controls and
its game list. A game runs from Steam. [**Start game**](#start-game) starts the chosen game there.

#### Game updates and extra content

You install an update or extra content (DLC) as a game. Press **Games Install** and choose its `.pkg` with its zRIF
key. Vita3K puts an update in `ux0/patch` and extra content in `ux0/addcont`. It uses them when it starts the game.
The table lists the game once.

#### Steam

Check the games you want in Steam and press **Update Steam**. The app adds them to Steam as non-Steam games. Each
game gets its own pictures:

- the game's icon and its LiveArea picture as its pictures
- its icon (`icon0.png`) as the logo on the banner

The app takes out the games you unchecked and the games no longer installed. Steam keeps these files in memory. So
Steam closes for the change and starts again in the background.

The info symbol under the list says in short what the boxes and **Start game** do. **Steam** in its text is a link.
It opens Steam's library, and Steam starts when it does not run.

In Steam each game's name starts with its system, for example **[PS Vita] Gravity Rush**. So it stands apart in
Steam's menus from the same title on Steam or on another system.

The games are in the library under **Non-Steam**. They are there on the desktop, in Big Picture Mode and in Game
Mode alike. They start the game alone in Vita3K, full screen. Vita3K quits when the game ends. Steam's menu and
**Exit game** work as for any game.

Steam's overlay works over a game started from Steam, in Game Mode and on the desktop. Press **Shift+Tab** or the
**PS button**. You then see the game's page, its controller layout and its settings, without leaving the game.

A game started from Steam reads your controllers itself. [How it works](#how-it-works) explains both.

Change Steam from Desktop Mode. In Game Mode, Steam is the session itself and cannot close for the change.

##### Covers

A PS Vita game has no cover in the shape Steam's library uses. So the app draws one, with the game's icon and its
title on a dark background. You can enter a SteamGridDB API key under **Steam artwork…**. With the key, the app takes
a cover from SteamGridDB for each game instead. The background and the logo on the game's page stay the game's own.
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
starts the game. The line under the tabs says **Starting…** until Vita3K runs. It says so when Steam did not start
the game. While Vita3K already runs, the app starts no second game. The tab you were on stays open.

The app does not start a game that is not in Steam yet. The line under the tabs then says to check it and press
**Update Steam** first.

### Settings

This tab holds Vita3K's settings that matter for playing. The app writes each one into Vita3K's own settings file
(`config.yml`) the moment you change it. A game's own settings in Vita3K come before these. Everything else is in
Vita3K's own window, under **Vita3K settings** below the games. The tab scrolls when it is higher than the window.

- **Picture** holds these settings:
    - **Renderer**: Vulkan on the BC-250. OpenGL helps only a game that fails with Vulkan.
    - **Resolution**: a multiple of the PS Vita's 960 × 544. 2x fills a 1080p screen sharply. A higher one asks more
      of the GPU.
    - **Screen filter**: Bilinear is smooth, and Nearest keeps sharp pixels. Bicubic is sharper, and FXAA smooths
      edges. FidelityFX Super Resolution works with Vulkan only.
    - **Anisotropic filtering**
    - **Fill the screen**: the picture stretches to the whole screen. Off, the picture keeps the PS Vita's shape,
      with borders.
    - **VSync**
- **Speed** holds these settings:
    - **High accuracy**: Vita3K draws more exactly, for a game that shows errors. It is slower.
    - **Compile shaders in the background**: the game goes on while Vita3K compiles, with less stutter.
    - **FPS hack**: it may double a 30 FPS game to 60. But it makes some games run twice as fast.
    - **Performance overlay**: the frames per second over the game.
    - **Shader compilation message**
- **Sound** holds these settings:
    - **Volume**
    - **Sound output**: SDL is Vita3K's own choice. Pick Cubeb when the sound crackles.
    - **NGS sound**: the PS Vita's sound engine. Off, many games are silent. Turn it off for a game that hangs on it.
- **System** holds two settings:
    - **Confirm button**: Cross as on a PS Vita sold outside Japan, or Circle as in Japan.
    - **Language** of the PS Vita. A game that has that language shows it.

Each setting shows what Vita3K's settings file holds. While the file does not name a setting, you see Vita3K's own
default. A value set in Vita3K that the app does not offer is shown as it is. The app writes nothing while Vita3K
runs. Vita3K writes its settings back when it closes, over any change.

### Memory cards

A PS Vita game keeps its save as a folder, not on a card file. This tab lists the saves on Vita3K's storage. They
are in `ux0/user/00/savedata` and in every other user's save folder. For each save it shows these things:

- the game
- its folder, named after the game's code
- its size
- when it was last written

Three buttons act on the selected saves:

- **Export…** writes the selected saves to one `.zip`, each as its folder. You can keep the file or share it.
- **Import…** puts the saves from such a `.zip` in the first user's save folder. The app asks before it replaces a
  save that is there already.
- **Delete…** deletes the selected saves after the app asks. A deleted save is gone. Export it first to keep a copy.

The app imports and deletes nothing while Vita3K runs. Close Vita3K first. Vita3K's own window (**Vita3K settings**)
takes in and writes the encrypted saves of a real PS Vita. This tab does not.

### View logs

This tab shows everything the app said and did, with the time. The log holds these things:

- Vita3K installed or removed
- what the app set up in Vita3K
- the firmware files given to Vita3K
- the games installed or deleted
- every change to Steam
- every error

The same lines are in `~/.local/share/bc250-vita3k-manager/bc250-vita3k-manager.log`. The file turns over at 1 MB.
The app keeps the three older files. **Clear logs**, the tab beside View logs, empties the file and the View logs
tab. It also removes the three older files. The log holds what the app did. It holds neither your SteamGridDB key
nor anything personal.

## From a terminal

`bc250-vita3k-run` starts the installed Vita3K with the options you give it. The Steam shortcuts use it. So they
keep working when a newer version of the app brings a newer Vita3K.

```bash
bc250-vita3k-run --frontend sdl -r PCSB00245                   # a game alone, by its ID; Vita3K quits with it
bc250-vita3k-run --firmware "/path/to/PSP2UPDAT.PUP"           # install a part of the firmware
bc250-vita3k-run --pkg "/path/to/game.pkg" --zrif KO5i...      # install a game from its package and license
bc250-vita3k-run "/path/to/game.vpk"                           # install a game and start it
bc250-vita3k-run                                               # Vita3K's own window
```

## New Vita3K builds

Vita3K has no stable releases. It publishes a new build for almost every change. The builds are numbered over its
whole history, such as 4377. Each version of the app was tried with one build, the one **Install** puts in.

When the window opens, the app asks GitHub for Vita3K's newest build. When that build is newer, the Vita3K line's
tooltip and the log say so. They link to what is new. The app does not install it by itself, but the [version
manager](#versions) can.

A newer Vita3K comes with a newer version of the app, once it has been tried. You get it from the
[portal](../portal.md). After you update the app, the tooltip and the log say so, and **Install** brings it.

Vita3K's own window (**Vita3K settings**) would look for a newer build when it opens. The app turns that check off
in Vita3K's settings, together with Vita3K's welcome window. [How it works](#how-it-works) says more. The AppImage Vita3K comes in can update
itself. The app starts Vita3K with that turned off. Should Vita3K have updated itself all the same, the Vita3K
line's tooltip says so. **Install** then puts the tried build back.

## How it works

The Steam shortcuts start `bc250-vita3k-run`. It starts Vita3K with its plain game window, the game alone. Vita3K
quits with the game, so Steam sees the game end. Two things change when Steam is the one that starts it. Started
from outside Steam, Vita3K runs as it is. That is the case with **Vita3K settings** or with `bc250-vita3k-run` in a
terminal.

Once Vita3K is installed, the app sets two lines of Vita3K's settings. They are in `config.yml` in its settings
folder. The app does so each time the window opens, while Vita3K does not run. The two lines are these:

- the welcome window off, which would wait for a click before a game
- Vita3K's own update check off, which would offer a build the app was not tried with

Everything else in the file stays as Vita3K wrote it. What changed goes to the log.

### Controllers

When Steam starts a game, it tells the game's controller library (SDL) to ignore the controllers Steam handles
itself. In their place it gives the game Steam's virtual controller (Steam Input). Vita3K then sees only that
virtual controller. It has no motion sensors or touchpad. On the desktop it follows the layout Steam has active.
That may be Steam's desktop layout, with mouse and keys.

So the run wrapper, `bc250-vita3k-run`, undoes it. While a real controller is connected, Vita3K
reads that controller itself. It leaves Steam's virtual one (USB ID `28DE:11FF`) out. The PS button stays Steam's.

Without a real controller, the wrapper leaves Steam's choice as it is. That is the case on a Steam Deck, whose own
controls exist only as Steam's virtual controller. You set the buttons in Vita3K's own window. Open **Vita3K
settings**, then **Controls**.

### Steam's overlay on the desktop

The KDE desktop of Bazzite is a Wayland session. Vita3K opens its windows through Wayland when it can. But Steam on
the desktop only sees windows that go through X11. These go through XWayland, the X11 server within the Wayland
session. A game window Steam cannot see has no overlay. **Shift+Tab** and the **PS button** then do nothing.

So when Steam starts a game on the Wayland desktop, the run wrapper has Vita3K open its windows through XWayland.
It sets `SDL_VIDEO_DRIVER=x11`, and `QT_QPA_PLATFORM=xcb` for Vita3K's own window. Steam's overlay then works as in
any other game. Game Mode runs every game through X11 already.

## What goes where

| What | Where |
|---|---|
| The app | `~/.local/share/bc250-vita3k-manager/app` |
| Vita3K | `~/.local/share/bc250-vita3k-manager/emulator` |
| The firmware files you put there, and your games to install | `~/Games/Vita/Firmware` and `~/Games/Vita` (the app's own folder) |
| Vita3K's settings | `~/.config/Vita3K` (Vita3K's own folder) |
| The PS Vita's storage, with the firmware, installed games and saves | `~/.local/share/Vita3K/Vita3K` (Vita3K's own folder) |
| Vita3K's shader cache and log | `~/.cache/AppImage-Cache/Vita3K` |
| The app's settings | `~/.config/bc250-vita3k-manager` |
| The app's log | `~/.local/share/bc250-vita3k-manager/bc250-vita3k-manager.log` |
| The Steam shortcuts | Steam's `shortcuts.vdf` and `grid` folder, per Steam user |
| The covers found on SteamGridDB | `~/.local/share/bc250-vita3k-manager/covers` |
| Launchers | `~/.local/bin/bc250-vita3k-manager`, `~/.local/bin/bc250-vita3k-run` |

Vita3K can keep its storage elsewhere. You set that in its **Settings**, as the storage folder. The app reads where
the storage is.

## Install and remove

Install the app from the [portal](../portal.md), where it is under Gaming. Removing the app also removes the Vita3K
it installed. Vita3K's own folders stay, with the firmware, your games and your saves. The games in Steam then no
longer start. So take them out first. Uncheck them and press **Update Steam**.

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app menu entry only, no icon on the Desktop
./install.sh --uninstall             # remove the app and the Vita3K it installed; keeps its settings and log
./install.sh --uninstall --purge     # also remove its settings, covers and log
```

## Disclaimer

The BC250 Bazzite Suite is an independent community project, not affiliated with or endorsed by AMD, ASRock, the Bazzite /
Universal Blue project, Sony, Microsoft, Valve, or the makers of the emulators and the other programs the apps work
with. BC-250 is AMD's product name and Bazzite the Universal Blue project's. PlayStation, PS4, PS5, PS3, PS2, PSP, PS
Vita, PSN, DualSense and Remote Play are Sony's; XBOX, XBOX 360, XBOX Cloud Gaming, Game Pass and Windows are
Microsoft's; Steam, Steam Deck and Big Picture are Valve's; the names of the emulators (shadPS4, RPCS3, PPSSPP, PCSX2,
Vita3K, Xenia) and of Decky Loader, HelixSR and DirectMesh belong to their owners. The suite uses them only to say what its apps work with.

## License

GPL-3.0-or-later. Vita3K is a separate program under its own license (GPL-2.0). The app downloads it from its own
release.
