<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![PCSX2 Manager](../assets/pcsx2/bc250-pcsx2-manager.webp){ .app-logo }

# PCSX2 Manager

PCSX2 Manager plays **PS2 games** on the **AMD BC-250** with [PCSX2](https://pcsx2.net), an open-source PS2 emulator.
The app does these things for you:

- It installs the PCSX2 release it was tried with, and sets it up.
- It takes your PS2 BIOS.
- It finds your games and adds them to Steam.

A game then starts straight away, on the desktop or from Steam's **Big Picture Mode**. On a handheld, that is Game
Mode. You do everything about PCSX2 in the app:

- its [settings](#settings)
- the [memory cards](#memory-cards)
- each game's [screen](#screen)

You never need PCSX2's own window for any of it. A game runs from Steam. [**Start game**](#start-game) starts the
chosen one there.

PCSX2 decides whether a game runs, and how well. Its [compatibility list](https://pcsx2.net/compat) shows what others
found.

## What you need

- **Your games**, dumped from your own discs. They can be ISO images, or compressed CHD, CSO, ZSO or GZ files. The
  app never downloads games.
- **The PS2's BIOS**, dumped from your own console. [PCSX2's BIOS page](https://pcsx2.net/docs/setup/bios) says how,
  with the biosdrain homebrew. The app cannot ship the BIOS. Put the dump, a `.bin` file, in `~/Games/PS2/BIOS`.
  PCSX2 needs the BIOS to start any game.
- **Steam**, started at least once. A game is started from Steam.
- About 60 MB for PCSX2 itself. Its BIOS, memory cards, saves and settings go in `~/.config/PCSX2`.
- **fusermount** (FUSE), which Bazzite has. PCSX2 comes as an AppImage, which mounts itself with fusermount. Without
  it, PCSX2 unpacks itself to a temporary folder on every start, which takes longer.

## Using it

The header has four pills:

- **PCSX2 version**
- **PCSX2 Install**
- **PCSX2 Uninstall**
- **Refresh**, which reads everything again

Beside the title is a row of states. Each shows its name and a dot. The dot is green when all is well,
and red when not. Hold the pointer over a state to read it in full.

- **Installed**: the app's own state, such as **Not installed**
- **Controller**: **Controller connected**, or **No controller** when none is, checked again every few seconds
- **Steam**: green while Steam runs and is signed in, red when it is not

A game started from Steam reads the controller that is connected when it starts. So switch yours on before you
start a game, or press its PS button to wake it. When Steam starts a game without a controller, the app also says
so in a desktop notification. A game in Steam starts only while Steam is signed in. So start Steam and sign in
before you start a game.

Under the header are links to **PCSX2's release notes** and to this wiki. Below them is a second row of four pills.
Each pill shows what it is for on top, and what it does under it:

- **Games Uninstall**
- **Available in Steam**, how many of your games are in Steam
- **BIOS Uninstall**
- **Play time**, the time spent in all your games together, as PCSX2 counts it. The tooltip shows each game's time.

Your games and your BIOS dump go into the app's own folder. See [Where your games go](#where-your-games-go). You
never choose or browse to a folder.

Below the pills are two columns. The first column has three lines: **PCSX2:**, **BIOS:** and **Game folder:**. Each
line says in short where that part stands, with more in its tooltip. The second column shows the **Installed
version:** of PCSX2.

Then comes a row of six tabs:

- **Your games**
- **Start game**
- **Memory cards**
- **Settings**
- **View logs**
- **Clear logs**

**Start game** and **Clear logs** are buttons.

- **PCSX2**: this line says **Not installed.** or **Installed.**
    - The tooltip says which release is installed, or what Install takes.
    - When this version of the app brings another release, the tooltip and the log say so. **PCSX2 Install** then
      puts that release back in use.
    - **PCSX2 Install** downloads PCSX2 from its GitHub release, about 57 MB. It is the stable release this version of
      the app was tried with. The app checks it against its checksum before it installs it.
    - The app then sets PCSX2 up. See [PCSX2's settings](#pcsx2s-settings).
    - **PCSX2 Uninstall** takes PCSX2 out again. PCSX2's own folder stays, with the BIOS, your memory cards and
      settings.
- **BIOS**: this line shows the name of the BIOS dump PCSX2 uses, and nothing else. Without a dump, it says **Not
  installed.**
    - The **i** beside it says what PCSX2 needs the BIOS for, and where it goes.
    - Put your dump in `~/Games/PS2/BIOS`. Put the files with the same name beside it, such as `.NVM` and `.MEC`.
      Only the `.bin` is needed.
    - The app copies the dump into PCSX2's `bios` folder by itself, when the window opens and on **Refresh**. PCSX2
      then uses it.
    - **BIOS Uninstall** takes a dump out of PCSX2's folder and out of `~/Games/PS2/BIOS` again, with those files.
      PCSX2 then uses another dump in the folder, when there is one.
    - PCSX2's folder is in the tooltip.
- **Game folder**: this line shows where the app looks for games. These are `~/Games/PS2` and a removable drive's
  `Games/PS2`.
    - The **i** beside them says what goes there.
    - The app also finds games in subfolders, up to five folders deep. So a folder per game is fine.

### Versions

The version box in the header is a pill. A click opens the list of the PCSX2 builds you installed. A check mark shows
the one in use. Pick another to put it in use. The games in Steam start whichever build is in use. Every build shares
PCSX2's own folder with the BIOS, memory cards and settings.

**Manage versions…** under the list opens the version manager. It has two parts:

- **Installed** lists every build in the app's folder.
    - A check mark shows the one in use.
    - The one this version of the app was tried with is marked **Tested**.
    - **Use** puts the chosen build in use.
    - **Delete** removes it. You cannot delete the one in use.
    - **Add** (**Custom build**) takes an AppImage of your own. The app does not check it.
- **Download** gets other builds from GitHub.
    - **Refresh** asks GitHub which builds there are. These are the newest nightlies and the newest stable release.
    - Each build gets its own copy of PCSX2's catalog.
    - **Download** fetches the chosen build. It checks it against the SHA-256 GitHub publishes for it, and puts it
      beside the others.
    - **Use** then puts it in use.

Only the build marked **Tested** was tried on the board. To go back to it, pick it in the version pill's list. Or
press **PCSX2 Install**, which puts it back in use without a download when it is still there.

### Where your games go

The app has folders of its own, which it makes when it opens. You never choose or browse to a folder.

- `~/Games/PS2`: put your disc images there, or in folders in it. They then show on **Your games**.
- On a USB drive or an SD card, make a folder `Games/PS2` on it. The app looks there too while the drive is mounted.
  Bazzite mounts it under `/run/media` or `/media`.
- `~/Games/PS2/BIOS`: put your console's BIOS dump there. The app copies it into PCSX2.

```
~/Games/PS2/
├── BIOS/                     the BIOS dump you put here: SCPH-70012.bin, SCPH-70012.nvm, ...
├── SLUS_215.53.Lumines.iso   a game you put here
└── Puzzle/Tetris.chd         a game in a folder of its own
```

Until version 3.1, you could add folders in the app with **Add folder**. The app no longer looks in those folders.
Move those games to `~/Games/PS2`.

### Your games

The table lists every game the app found:

- The app reads an **ISO** for its `SYSTEM.CNF`. That file names the program the console boots. That name is the
  game's **ID** (SLUS-12345), shown beside the title.
- A **CHD, CSO, ZSO or GZ** holds the same disc, compressed. The **Type** column shows which. The app does not look
  into those formats, so the row has no ID. PCSX2 plays them the same.
- **File name** is the image's name. Its folder is in the tooltip.

A PS2 disc carries no title of its own. The app takes the title from PCSX2's own catalog of PS2 games, by the serial.
A game PCSX2 does not know gets its file's name, without a serial in it. So `SLUS_215.53.Lumines Plus.iso` is
**Lumines Plus**.

**PCSX2 settings**, left of it, opens PCSX2's own window. Use it for what the Settings tab does not set: PCSX2's other
settings, the controllers and its game list.

**Exit PCSX2**, the first button under the games, closes PCSX2 from the app. Use it when the line under the tabs asks
you to close PCSX2 first. The button is on only while PCSX2 runs. A click ends PCSX2 at once, with no question. A game
that is running ends without saving.

**Games Uninstall**, the pill above, deletes the chosen game from the disk.

1. A window first lists what would go, a row each with its size. These are the disc image, and its Steam shortcut
   when the game is in Steam.
2. Every row is checked. Uncheck what you want to keep.
3. Press **Delete marked**. **Cancel** deletes nothing.

The memory cards stay. The app will not delete some games, such as one at the top of a drive, or one in a folder that
holds another game. The line under the tabs then says so. Delete such a game by hand.

#### Screen

A PS2 game shows a 4:3 picture, with borders on a wide screen. **Screen setting** sets how a game fills the screen.
You set it per game:

- **Original**: the PS2's picture as it is.
- **Widescreen**: PCSX2's widescreen patch for the game, which draws a wider view without stretching. The app offers
  it only for a game PCSX2 has a patch for.
- **Fill screen**: the picture stretched to fill the screen. Round things look wider.

PCSX2 keeps the choice in the game's own settings. A compressed image has no choice here. The app does not look into
it, so it does not know the game's settings file.

#### Steam

Check the games you want in Steam and press **Update Steam**. The app adds them to Steam as non-Steam games. It takes
out the games you unchecked, and the games it no longer finds. Steam keeps these files in memory. So Steam closes for
the change and starts again in the background.

A PS2 disc gives no pictures of its own. So the app draws the pictures on the tiles from its icon, with the game's
title, on a background in the icon's color. The icon is the logo on the banner.

In Steam, each game's name starts with its system, for example **[PS2] Lumines Plus**. So it stands apart in Steam's
menus from the same title on Steam or on another system. A game whose name in Steam differs from its title in the app
is renamed the next time you press **Update Steam**. Until then, **Update Steam** is on for it. Steam sees the renamed
game as a new one. Its play time stays. A controller layout or collection you set for it in Steam has to be set again.

The games are in the library under **Non-Steam**, on the desktop and in Big Picture Mode alike. Each one starts the
game alone in PCSX2, full screen, with the mouse pointer hidden. PCSX2 exits when the game does. Steam's menu and
**Exit game** work as for any game. So does **Select + Start** on the controller. See [Settings](#settings).

Steam's overlay works over a game started from Steam, in Big Picture Mode and on the desktop. Press **Shift+Tab** or
the **PS button** for the game's page, its controller layout and its settings, without leaving the game. In Big
Picture Mode, the PS button opens Steam's menu over the game. Press it again there to open the power menu, with
**Exit game** and the way out of Big Picture Mode.

Steam's overlay also takes **screenshots**. Press **F12** on a keyboard. On a controller in Big Picture Mode, press
the Steam button with the right shoulder button. The screenshots go into Steam's screenshot library. From there,
Steam shows, uploads or shares them. PCSX2's own screenshot key (**F8**) saves into PCSX2's `snaps` folder instead.

A game started from Steam reads your controllers itself. [How it works](#how-it-works) explains both.

On a handheld image of Bazzite, Game Mode is a Steam session of its own. In that session, Steam cannot close for the
change. So change Steam from Desktop Mode.

##### Covers

The app can take the pictures for each game from SteamGridDB, a website of game artwork, instead of drawing them. For
that, enter a SteamGridDB API key under **Steam artwork…**. The app then takes these pictures:

- the cover
- the wide picture
- the banner
- the logo

A picture SteamGridDB does not have stays drawn. The app looks up a game by its title as the list shows it.
See [Covers from SteamGridDB](covers.md) for the key, how a game is looked up and how to use a picture of your own.

#### A game in Steam more than once

The app checks whether a game has more than one shortcut in Steam. When one has, the line under the tabs names the
game and says how often it is there. The tooltip of its **In Steam** box says the same. **Update Steam** is then on
for it. It leaves one shortcut of each game, with the latest play time, and takes the others out. Its question says
how many double shortcuts go.

#### Start game

**Start game** is the tab beside Your games, and it is a button. Choose a game in the table and click it. The game
starts through Steam, as its shortcut in Steam starts it.

- When Steam does not run, the app starts Steam first and waits until it is up. This takes a while. Then it starts
  the game.
- The line under the tabs says **Starting…** until PCSX2 runs. It also says so when Steam did not start the game.
- While PCSX2 runs already, the app starts no second game.
- The tab you were on stays open.
- The app does not start a game that is not in Steam yet. The line under the tabs then says to check it and press
  **Update Steam** first.

### Settings

The tab holds PCSX2's settings that matter for playing. It has two columns, and scrolls when it is higher than the
window. The app writes a setting into PCSX2's own settings file the moment you change it. A game's own settings in
PCSX2 come before these. You set how a game fills the screen per game, in the **Your games** tab.

- **Picture**
    - **Renderer**: Automatic picks Vulkan on the BC-250. Software draws on the CPU, exact but slow.
    - **Internal resolution**: Native is the PS2's. 3x fills a 1080p screen sharply, and 6x a 4K one. A higher one
      asks more of the GPU.
    - **Texture filtering**
    - **Anisotropic filtering**
    - **FXAA**
    - **Integer scaling**
    - **VSync**
    - **Blending accuracy**: how exactly PCSX2 copies the PS2's blending of transparent layers. Basic suits most
      games. A higher level fixes glitches in some, at a cost to the GPU.
    - **Video (FMV) shape**: a game's videos follow the game's screen setting, or take the shape 4:3 or 16:9.
      With 4:3, Fill screen does not stretch them.
- **Emulation**
    - **Fast boot** skips the PS2's start-up screen.
    - **Cheats** turns on PCSX2's `.pnach` cheat files for a game.
    - **No-interlacing patches** give a progressive picture instead of an interlaced one. It is sharper and does not
      shimmer. This works for the games PCSX2 has a patch for.
    - **Save state when quitting** makes a save state when a game ends. Next time, you load it from PCSX2's pause
      menu, with **Esc**.
- **Sound**
    - **Volume** is PCSX2's volume.
    - **Bazzite's volume for PCSX2** stands beside it, and is not PCSX2's. Bazzite's sound settings remember a volume
      and a mute per application, also once it is closed. So a game plays without sound while PCSX2 is muted there.
    - The app says so in red when PCSX2 is muted or turned down to nothing.
    - **Unmute** beside it turns a muted PCSX2 on again. Bazzite keeps it on from then on.
    - To change a volume that is turned down, use the sound applet while a game plays. The applet is the speaker in
      the panel, under Applications.
- **Controllers**
    - **Vibration**
    - **Stick dead zone**: how far a stick moves before the game sees it. This helps with a stick that drifts.
    - **Stick range**: how the stick's travel maps onto the PS2's. PCSX2's 1.33 reaches the edge sooner. **As the
      stick** is 1:1, and **Wider** is 1.66.
    - **Player 2 on the second controller**: a second controller connected is player 2, with the same buttons as
      player 1.
    - **Quit a game with Select + Start**: press Select and Start together on the first controller. This ends the game
      and closes PCSX2 without a question, as Steam's **Exit game** does. Other controllers call Select Share, Create
      or View, and Start Options or Menu. The switch is on from the start. Turn it off for a game that uses the two
      buttons together itself. You then leave a game through Steam's menu. Or press **Esc** on a keyboard to open
      PCSX2's own menu.
- **On screen** is what PCSX2 writes over the picture.
    - **Show FPS**
    - **Show speed**, the game's speed in percent
    - **Show resolution**
    - **Show CPU and GPU use**
    - **Show frame times**, a graph of how long each frame took
    - **Show inputs**, the controller's buttons as they are pressed
    - **Text size** of it all

Each setting shows what PCSX2's settings file holds. A value set in PCSX2 that the app does not offer is shown as it
is. Nothing is written while PCSX2 runs. PCSX2 writes its settings back when it closes, over any change.

### Memory cards

The **Memory cards** tab shows the memory cards in PCSX2's memory card folder. That is `~/.config/PCSX2/memcards`, or
the folder set in PCSX2. The tab also shows the saves on the card you choose:

- each save's title
- its folder on the card
- its size
- when it was saved

The card in each of PCSX2's slots is marked **(slot 1)** or **(slot 2)**. **Slot** puts the chosen card in a slot, or
takes it out of one. A game saves to the card in slot 1, and some games use slot 2 too. A card is in one slot at most.
So a card you put in a slot takes the place of the card there. Select a save to see its 3D icon as a still picture,
as the PS2's browser shows it.

- **Import…** puts save files on the card. It takes these kinds:
    - MAX Drive (`.max`)
    - EMS (`.psu`)
    - SharkPort (`.sps`)
    - X-Port (`.xps`)
    - Code Breaker (`.cbs`)
    - PSV (`.psv`, from a PS3)

    A save that is already on the card stays as it is. Delete it first to replace it. When the card has too little
    space for all of them, the app puts none on it.
- **Export…** saves the selected saves as `.psu` or `.max` files, to keep or to share. For one save, it asks for a
  file name. Several saves go into a folder you choose. Each file is named after the save's folder, its title and a
  checksum.
- **Copy to…** copies the selected saves onto another card.
- **Delete…** deletes the selected saves.
- **New card…** makes a new, empty card.
    - A name ending in `.ps2` is PCSX2's own kind.
    - A `.mc2` card has no error-correcting code (ECC), as a MemCard PRO2 reads.
    - The PS2's own card is 8 MB. PCSX2 also takes 16, 32 and 64 MB, which not every game works with.
    - **Slot** then puts the new card in a slot.
- **Format…** empties the card. Every save on it goes.
- **Check** checks the card's file system, and every page against its ECC. It says what it found.

Before every change, the app copies the card beside it as `<card>.<date and time>.bak`, for example
`Mcd001.ps2.20261016-093000.bak`. It keeps the newest 10 per card. PCSX2 does not list these as cards. To go back to
one, close PCSX2. Then rename the card and give the backup the card's name.

The app makes a change on a copy of the card. The copy takes the card's place when the change is finished. So a
change that fails leaves the card as it was.

Nothing is written while PCSX2 runs. PCSX2 keeps the card in memory and would write its own copy over the change. The
tab says so. Import, copy, delete, format and the slot wait until PCSX2 is closed. Export and check only read the card.

The tab reads PS2 cards. PCSX2 can also keep a card as a folder. It can also play PS1 games with PS1 cards (`.mcd`,
`.mcr`). The tab lists those cards and says it cannot read them. A PS2 can copy a PS1 save onto a PS2 card. The tab
lists such a save with its title.

### View logs

The tab shows everything the app said and did, with the time:

- PCSX2 installed or removed
- what the app wrote in PCSX2's settings
- the BIOS and the folders chosen
- each setting changed
- each change to a memory card
- every change to Steam
- every error

The games are logged too. Each game started from Steam is logged by its file's name when it starts. The line says
whether a controller was connected. The next time the window looks, the app sums up PCSX2's own log of its last run
in one line. That line says which game, how long it was played, until when, and with which controller. PCSX2 writes
its log over at every start. So when you play two games before the window looks, the app sums up only the last run.

The same lines are in `~/.local/share/bc250-pcsx2-manager/bc250-pcsx2-manager.log`. The file turns over at 1 MB, and
the app keeps the three older files. **Clear logs**, the tab beside View logs, empties the file and the View logs tab.
It also removes the three older files. The log holds what the app did. It does not hold your SteamGridDB key or
anything personal.

## From a terminal

`bc250-pcsx2-run` starts the installed PCSX2 with the options you give it. The Steam shortcuts use it. So they keep
working when a newer version of the app brings a newer PCSX2.

```bash
bc250-pcsx2-run -nogui -fullscreen -- "/path/to/game.iso"   # a game alone, full screen (the Steam shortcuts)
bc250-pcsx2-run -nogui -- "/path/to/game.iso"               # a game alone, in a window
bc250-pcsx2-run                                             # PCSX2's own window
```

## New PCSX2 releases

PCSX2 publishes a nightly build for almost every change. Now and then, it publishes a stable release (2.8.2). Each
version of the app was tried with one stable release, the one **PCSX2 Install** puts in.

When the window opens, the app asks GitHub for PCSX2's newest stable release. When that one is newer, the PCSX2
line's tooltip and the log say so, with a link to what is new. The app does not install it by itself, but the
[version manager](#versions) can. A newer PCSX2 comes with a newer version of the app, once it has been tried. You
get it from the [portal](../portal.md). After you update the app, the tooltip says so, and **PCSX2 Install** brings
it.

The app turns PCSX2's own update check off. PCSX2 may still be updated in its own window. The PCSX2 line's tooltip
then says that PCSX2 updated itself. **PCSX2 Install** puts the tried release back.

## How it works

The Steam shortcuts start `bc250-pcsx2-run`, which starts PCSX2. Two things change because Steam is the one that
starts it.

### Controllers

When Steam starts a game, it tells the game's controller library (SDL) to ignore the controllers Steam handles
itself. In their place, it gives the game Steam's virtual controller (Steam Input). PCSX2 then sees only that virtual
controller. It has no motion sensors. On the desktop, it follows the layout Steam has active. That may be Steam's
desktop layout, with mouse and keys.

So the run wrapper undoes it. While a real controller is connected, PCSX2 reads that controller itself. It leaves
Steam's virtual one (USB ID `28DE:11FF`) out. The PS button stays Steam's. Without a real controller, the wrapper
leaves Steam's choice as it is. That is the case on a Steam Deck, whose own controls exist only as Steam's virtual
controller.

PCSX2 itself maps the keyboard to player 1, and no controller. The app maps player 1 to the first controller
connected, whatever its kind. It maps the buttons by their places. The bottom face button is Cross, the right one is
Circle, and so on. This works over USB and Bluetooth alike. With two controllers connected, the first is the one SDL
counts first. **Player 2 on the second controller** in the Settings tab gives the second one the same buttons. A
mapping you make in PCSX2's own window stays. The app leaves player 1 alone once a controller is mapped to it.

### PCSX2's settings

The app sets PCSX2 up so that a game started from Steam goes straight into the game. While PCSX2 is installed and
not running, the app keeps these settings in PCSX2's own settings file (`~/.config/PCSX2/inis/PCSX2.ini`):

- PCSX2's setup wizard is marked done, so it does not open at the first start.
- PCSX2 does not look for updates itself. An update would replace the release the app installed.
- The mouse pointer is hidden over a full-screen game.
- PCSX2 uses the BIOS chosen in the app.
- Player 1 is mapped to the first controller. See [Controllers](#controllers).
- Select + Start together on that controller end the game and close PCSX2. The switch in the [Settings](#settings)
  tab turns it off.

Everything else in the file stays as it is. The [Settings](#settings) tab writes into the same file, one setting at a
time. When PCSX2 has no settings file yet, the app starts from PCSX2's own defaults. These are what PCSX2 writes at its
first start, with its keyboard keys and hotkeys. **Esc** opens PCSX2's pause menu. **F6** changes the picture's
shape. While PCSX2 runs, nothing is written, since PCSX2 writes its settings back when it closes.

### A game renamed, moved or gone

A game you rename or move after it was put in Steam keeps its mark. The app knows each game in Steam by its code. For
a game without a code, it uses the file's size. So on **Refresh**, the app finds the game again under its new name,
checked. The line under the tabs says so. **Update Steam** then takes the old shortcut out and puts the game in under
its new name.

A game may no longer be there, because you deleted it or its drive is not in. Its shortcut then does not start PCSX2.
A window says which file is missing and what to do. The window closes by itself, so Steam sees the game end.

### Steam's overlay on the desktop

The KDE desktop of Bazzite is a Wayland session. PCSX2 is a Qt program, and opens its windows through Wayland when it
can. But Steam on the desktop only sees windows that go through X11. These are XWayland windows, from the X11 server
within the Wayland session. A game window Steam cannot see has no overlay. Then **Shift+Tab** and the **PS button**
do nothing.

So when Steam starts a game on the Wayland desktop, the run wrapper has PCSX2 open its windows through XWayland
(`QT_QPA_PLATFORM=xcb`). Steam's overlay then works as in any other game. A handheld's Game Mode runs every game
through X11 already.

## What goes where

| What | Where |
|---|---|
| The app | `~/.local/share/bc250-pcsx2-manager/app` |
| PCSX2 | `~/.local/share/bc250-pcsx2-manager/emulator` |
| PCSX2's BIOS, memory cards, saves, settings | `~/.config/PCSX2` (PCSX2's own folder) |
| Each game's screen | `~/.config/PCSX2/gamesettings/<serial>_<CRC>.ini`, PCSX2's own settings per game |
| PCSX2's catalog (titles, patches) | Beside PCSX2, in `~/.local/share/bc250-pcsx2-manager/emulator` |
| The memory cards' backups | Beside each card, in PCSX2's memory card folder |
| Your games and your BIOS dump | `~/Games/PS2` and `~/Games/PS2/BIOS` (the app's own folder), and `Games/PS2` on a removable drive |
| The app's settings | `~/.config/bc250-pcsx2-manager` |
| The app's log | `~/.local/share/bc250-pcsx2-manager/bc250-pcsx2-manager.log` |
| The Steam shortcuts | Steam's `shortcuts.vdf` and `grid` folder, per Steam user |
| The pictures found on SteamGridDB | `~/.local/share/bc250-pcsx2-manager/covers` |
| Launchers | `~/.local/bin/bc250-pcsx2-manager`, `~/.local/bin/bc250-pcsx2-run` |

## Install and remove

Install the app from the [portal](../portal.md), where it is under Gaming. Removing the app also takes out the PCSX2
it installed. Your games stay. So does PCSX2's own folder, with the BIOS, your memory cards and
saves. The games in Steam then no longer start. So take them out first. Uncheck them and press **Update Steam**.

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app menu entry only, no icon on the Desktop
./install.sh --uninstall             # remove the app and the PCSX2 it installed; keeps its settings and log
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

GPL-3.0-or-later. PCSX2 is a separate program under its own license (GPL-3.0), downloaded from its own release.
The memory card code is from [mymc++](https://github.com/Adubbz/mymcplusplus) (GPL-3.0-or-later) by Adubbz, based on
mymc+ by Florian Märkl and mymc by Ross Ridge.
