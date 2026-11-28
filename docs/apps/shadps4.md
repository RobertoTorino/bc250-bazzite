<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 shadPS4 Manager](../assets/shadps4/bc250-shadps4-manager.webp){ .app-logo }

# BC-250 shadPS4 Manager

BC-250 shadPS4 Manager plays **PS4 games** on the **AMD BC-250** with [shadPS4](https://github.com/shadps4-emu/shadPS4),
an open-source PS4 emulator. The app does these things for you:

- It installs the shadPS4 release it was tried with.
- It finds the games in your game folders.
- It adds them to Steam.

A game then starts straight away like any other, on the desktop or from Steam's **Big Picture Mode**. The app also
unpacks package files (`.pkg`) into a game folder, with **Games Install** (Extract PKG).

shadPS4 decides whether a game runs, and how well. Its
[compatibility list](https://github.com/shadps4-emu/shadps4-game-compatibility/issues) shows what others found.

## What you need

- **Your games**, installed from your own PS4. Each game sits in a folder of its own, with its `eboot.bin` and its
  `sce_sys` folder. A game can also be a package file (`.pkg`), which **Extract PKG** unpacks into that layout. The
  app never downloads games.
- **System modules** for some games. These are libraries of the PS4's firmware (`.sprx` files), from your own
  console. Many games run without them. The app cannot ship them, but it shows which ones are there.
- **Steam**, started at least once.
- About 35 MB for shadPS4 itself. Its saves, settings and shader cache go in `~/.local/share/shadPS4`.
- **FUSE 2** (`libfuse.so.2`), which Bazzite has. shadPS4 comes as an AppImage, which mounts itself with FUSE 2.
  Without it, shadPS4 unpacks itself to a temporary folder on every start, which takes longer.

## Using it

The header has four pills:

- **shadPS4 version**
- **shadPS4 Install**
- **shadPS4 Uninstall**
- **Refresh**, which reads everything again

Beside the title is a row of states. Each shows its name and a dot. The dot is green when all is well,
and red when not. Hold the pointer over a state to read it in full.

- **Installed**: the app's own state, such as **Not installed**
- **shadNet**: the state of shadPS4's online service, see [shadNet](#shadnet)
- **Controller**: **Controller connected**, or **No controller** when none is, checked again every few seconds
- **Steam**: green while Steam runs and is signed in, red when it is not

A game started from Steam reads the controller that is connected when it starts. So switch yours on before you
start a game, or press its PS button to wake it. When Steam starts a game without a controller, the app also says
so in a desktop notification. A game in Steam starts only while Steam is signed in. So start Steam and sign in
before you start a game.

Under the header are links to **shadPS4's release notes** and to this wiki. Below them is a second row of five
pills. Each pill shows what it is for on top, and what it does under it:

- **Games Install**
- **Games Uninstall**
- **Available in Steam**, how many of your games are in Steam
- **shadNet Account**
- **Play time**, the time spent in all your games together, as shadPS4 counts it. The tooltip shows each game's
  time.

Your games and the system modules go into the app's own folder. See [Where your games
go](#where-your-games-go). You never choose or browse to a folder for them.

Below the pills are two columns. The first column has four lines: **shadPS4:**, **Sys modules:**, **Game
folders:** and **shadNet:**. Each line says in short where that part stands, with more in its tooltip. The second
column shows the **Installed version:** of shadPS4.

Then comes a row of six tabs:

- **Your games**
- **Start game**
- **Memory cards**
- **Settings**
- **View logs**
- **Clear logs**

**Start game** and **Clear logs** are buttons.

The four lines say this:

- **shadPS4** says **Not installed.** or **Installed.**, with the button to use under it. The version pill in the
  header shows the version installed. When this version of the app brings another shadPS4, the tooltip and the log
  say so. **Install** then puts it back in use. **Install** downloads shadPS4 from its GitHub release (about 32
  MB). Before it unpacks shadPS4, it checks the download against the checksum this version of the app was tried
  with. **Uninstall** takes shadPS4 out again. shadPS4's own folder stays, with your saves, settings and system
  modules.
- **Sys modules** says **Ok** in green when every module that shadPS4 cannot do without is in its module folder. It
  says **Missing sys modules** in red when one is not. The tooltip shows how many there are, which are missing and
  the folder's path. Many games run without them. Put the modules (`.sprx` files) from your own PS4's firmware in
  `~/Games/PS4/Modules`. The app copies them into shadPS4's module folder by itself, when the window opens and on
  **Refresh**. It copies only what is new or changed.
- The **Game folders** line shows where the app looks for games. These are `~/Games/PS4` and a removable drive's
  `Games/PS4`, each game in a folder of its own. The tooltip shows the paths and how many games were found. The
  **i** beside them says what goes there. The app makes them shadPS4's own game folders too, so shadPS4's window
  lists the games. A game may sit up to five folders deep. A package file (`.pkg`) in one of them waits under **Your
  games** to be unpacked. See [Packages](#packages). For a package anywhere else, **Install** opens [Extract
  PKG](#extract-pkg).
- **shadNet** shows the name of the account shadPS4 signs in with. It says **Off** while no account is set up, and
  **—** while shadPS4 has not run yet. The tooltip shows the server. **Account** sets it up, see [shadNet](#shadnet).

### Versions

The version box in the header is a pill. A click opens the list of the shadPS4 builds installed. A check mark marks
the one in use. Pick another to put it in use. The games in Steam start whichever build is in use. Every build shares
shadPS4's own folder, with its saves, settings and system modules. **Manage versions…** under the list opens the
version manager:

- **Installed** lists every build in the app's folder. The one in use has a check mark. The one this version of the
  app was tried with is marked **Tested**. **Use** puts the chosen build in use. **Delete** removes it, but not the
  one in use. **Add** (**Custom build**) takes an AppImage of your own, which is not checked.
- **Download**: **Refresh** asks GitHub which builds there are. These are its stable releases and the pre-release, a
  nightly named after its date and commit. **Download** fetches the chosen one and checks it against the SHA-256
  GitHub publishes for it. It then puts the build beside the others. **Use** then puts it in use.

Only the build marked **Tested** was tried on the board. To go back to it, pick it in the version pill's list. You can
also press **shadPS4 Install**, which puts it back in use without a download when it is still there.

### Where your games go

The app has folders of its own, which it makes when it opens. You never choose or browse to a folder for them.

- `~/Games/PS4`: put your games there, each in a folder of its own with its `eboot.bin`. They then show on **Your
  games**. On a USB drive or an SD card, make a folder `Games/PS4`. The app looks there too while the drive is
  mounted, under `/run/media` or `/media`, as Bazzite mounts it. The app makes these shadPS4's own game folders as
  well, in its `config.json`. So shadPS4's window lists the games too.
- `~/Games/PS4/Modules`: put the system modules from your own PS4 there, and the app copies them into shadPS4.

Until version 3.1, you could add folders in the app with **Add folder**. The app no longer looks in those folders.
Move those games to `~/Games/PS4`.

### Your games

The table lists every game found. It shows the game's title and **ID** (CUSA…) from the game's own files. It also
shows its version and its **Folder**, the folder's name. The tooltip shows the path. Updates and mods are not listed
as games. See [Game updates and mods](#game-updates-and-mods). A PS4 game draws its picture for a wide screen itself.
So there is no screen setting per game, as in the PS2 and PS3 managers.

**Games Uninstall**, the pill above, deletes the chosen game from the disk. A window first lists what would go, a
row each with its size:

- the game's folder
- its update, patch and mods beside it
- its Steam shortcut, when it is in Steam

Every row is checked. Uncheck what you want to keep, then press **Delete marked**. **Cancel** deletes nothing. The
saves, the play time and the package stay. The app will not delete a game at the top of a drive, or a game in a
folder that holds another game. The line under the tabs then says so. Delete such a game by hand.

#### Game updates and mods

Put a game's update in a folder of its own beside the game. Name it like the game's folder with `-UPDATE` added.
`-patch` works too. shadPS4 finds the update there and uses it when it starts the game. The update's files take the
place of the game's, and the game's own folder stays as it is. Mods go the same way, in a folder ending in `-mods`.

```
shadps4_games/
├── CUSA11624/            the game: eboot.bin, sce_sys, ...
├── CUSA11624-UPDATE/     its update: its own eboot.bin, sce_sys and the files it changes
└── CUSA11624-mods/       mods for it
```

Nothing more is needed, and the table lists the game once. An update found beside its game, with the same ID
(CUSA…), is left out of the table, whatever its folder is called. A game copied from a PS4 that had its update
installed already has the update in it. It does not need a `-UPDATE` folder, and the table lists it with the update's
version.

#### Steam

Check the games you want in Steam and press **Update Steam**. The app adds them to Steam as non-Steam games. Their
pictures are the game's own icon and background. Its icon (`sce_sys/icon0.png`) is the logo on the banner. The app
also takes out the games you unchecked and the games it no longer finds. Steam keeps these files in memory. So Steam
closes for the change and starts again in the background. A game added before the app set the logo gets it the next
time you press **Update Steam**. Until then, **Update Steam** is on for it. The info symbol under the list says in
short what the boxes and **Start game** do. **Steam** in its text opens Steam's library.

In Steam, each game's name starts with its system, for example **[PS4] Lumines**. So it stands apart from the same
title on Steam, or on another system, in Steam's menus. A game added under its title alone is renamed the next time
you press **Update Steam**. Until then, **Update Steam** is on for it. Steam sees the renamed game as a new one. Its
play time stays, but you have to set a controller layout or collection for it in Steam again.

The games are in the library under **Non-Steam**, on the desktop and in Big Picture Mode alike. They start shadPS4
full screen. Steam's menu and **Exit game** work as for any game. So does shadPS4's quit window, see [Quit a
game](#quit-a-game).

Steam's overlay works over a game started from Steam, in Big Picture Mode and on the desktop. Press **Shift+Tab** or
the **PS button** for the game's page, its controller layout and its settings, without leaving the game. In Big
Picture Mode, the PS button opens Steam's menu over the game. Press it again there, and it opens the power menu. That
menu has **Exit game** and the way out of Big Picture Mode. On the desktop, the overlay needs **Enable the Steam
Overlay while in-game** in Steam's settings (In Game).

A handheld image of Bazzite has a Game Mode, which is a Steam session of its own. There, change Steam from Desktop
Mode, because in that session Steam cannot close for the change.

##### Covers

A PS4 game has no cover in the shape Steam's library uses. So the app draws one, with the game's icon and its title
on a dark background. You can enter a SteamGridDB API key under **Steam artwork…**. With it, the app takes a cover
from SteamGridDB for each game instead. The background and the logo on the game's page stay the game's own. [Covers
from SteamGridDB](covers.md) says how to get the key, how a game is looked up and how to use a cover of your own.

**Steam** in the line under the table is a link. It opens Steam's library, and Steam starts when it does not run.
**shadPS4 settings** beside it opens shadPS4's own window (Big Picture) for what the app does not set:

- the controller's buttons
- a game's own settings
- shadPS4's game list

**Exit shadPS4**, the first button under the games, closes shadPS4 from the app. Use it when the line under the tabs
asks you to close shadPS4 first. The button is on only while shadPS4 runs. A click ends shadPS4 at once, with no
question. A game that is running ends without saving.

#### A game in Steam more than once

The app checks whether a game has more than one shortcut in Steam. When one has, the line under the tabs names the
game and says how often it is there. The tooltip of its **In Steam** box says the same. **Update Steam** is then on
for it. It leaves one shortcut of each game, with the latest play time, and takes the others out. Its question says
how many double shortcuts go.

#### Start game

**Start game**, the tab beside Your games, is a button. Choose a game in the table and click it. The game starts
through Steam, as its shortcut in Steam starts it. When Steam does not run, the app starts Steam first and waits until
it is up. That takes a while, and then the game starts. The line under the tabs says **Starting…** until shadPS4 runs.
It also says so when Steam did not start the game. While shadPS4 runs already, no second game is started. The tab you
were on stays open. A game that is not in Steam yet is not started. The line under the tabs then says to check it and
press **Update Steam** first.

#### Quit a game

shadPS4's quit window asks whether to quit. **Cross** or **Enter** quits. **Circle** or **Esc** goes back to the
game. Open the quit window with one of these:

- **Share + Options**, pressed together, on a DualShock 4 or DualSense. On other controllers it is Back + Start, and
  on an XBOX controller View + Menu.
- **Ctrl+Shift+End** on the keyboard. The keypad's End works too, which is the 1 key with Num Lock off. That helps on
  a keyboard without an End key of its own.

The app adds these to shadPS4's `input_config/global.ini` when it starts, and says so in the log. The rest of the
file stays as it is. The controller also works on the desktop, where the keyboard may stay with Big Picture after
Steam started the game.

A game started from Steam reads your controllers itself, such as a DualShock 4 or DualSense with its touchpad and
motion sensors. [How it works](#how-it-works) explains both.

### Packages

A package (`.pkg`) is how the PS4 gets a game bought digitally, or its update. Put it in one of the game folders,
`~/Games/PS4` or a drive's `Games/PS4`. It may sit up to five folders deep. Then press **Refresh**. The package is a
row of its own under the games:

- **PKG** for a game to unpack before it plays
- **PKG update** for an update of a game you have

Hover over the row to see where it goes.

- **Unpack all** unpacks every package that waits, one after the other. The games come first, then the updates.
  **Unpack** unpacks only the chosen one. The line under the tabs says which one of how many, and counts its files. A
  large game takes minutes.
- **A game** goes into a folder named by its ID, `CUSA00001`, beside its package.
- **An update** goes beside its game, wherever that is. Its folder is named like the game's with `-UPDATE`. shadPS4
  lays it over the game when it starts, and the game's folder stays as it was. An update newer than the one there
  replaces it. The new one is unpacked first. The old one goes only when every file of the new one was written. An
  update whose game is still a package waits for it. **Unpack** on it says so, and **Unpack all** unpacks both. An
  update without its game is unpacked as a game of its own. Add-on content is not listed. Use Extract PKG for it.
- When the packages are unpacked, a window lists them, each with its size. A package takes as much room as its game,
  and you do not need it to play. Uncheck what you want to keep, then press **Delete marked**. **Cancel** keeps them
  all. A package that was unpacked whole is no longer listed, kept or not. A package with files that could not be
  written stays listed. Its folder then has `extraction_errors.txt`, which names those files.
- **Games Uninstall** on a package row deletes the package itself, after the same window. Some packages cannot be
  unpacked, such as a download cut short, which says **PKG file size is different**. Such a package stays a row until
  you delete or replace it.

The same extractor works in the [Extract PKG](#extract-pkg) window. That window can also do these things:

- preview a package
- salvage a damaged one
- compare two extractions
- rename a package to its content ID

### Settings

The tab scrolls when it is higher than the window.

The tab holds shadPS4's settings that matter for playing. They are the settings shadPS4's own window offers for every
game. The tooltips say what each does. The app writes each one into shadPS4's own settings file (`config.json`) the
moment you change it. It does that only while shadPS4 does not run, because shadPS4 writes its own settings back when
it ends. shadPS4 reads them when a game starts. A game's own settings in shadPS4 come before them. You make those in
shadPS4's own window.

- **Picture** has these settings:
    - VSync. Mailbox is shadPS4's default, and shows the newest frame at each refresh without tearing. On waits for
      each refresh. Off may tear.
    - AMD's FidelityFX upscaling (FSR), with its sharpening (RCAS)
    - HDR
    - a frame rate counter
- **Sound** has the sound output library (SDL or OpenAL) and the volume (up to 500 %). Beside the volume stands
  **Bazzite's volume for shadPS4**, which is not shadPS4's own. Bazzite's sound settings remember a volume and a mute
  per application, also once it is closed. So a game plays without sound while shadPS4 is muted there. The app says
  so, in red, when shadPS4 is muted or turned down to nothing. **Unmute** beside it turns a muted shadPS4 on again.
  Bazzite keeps it on from then on. To change a volume that is turned down, use the sound applet while a game plays.
  That is the speaker in the panel, under Applications.
- **Controller and mouse** has the controller's motion sensors, and when the mouse pointer hides over the game.
- **In a game** has these settings:
    - the PS4's system language, in which a game that has it shows its text
    - the trophy message
    - the game's splash screen

When shadPS4 knows a value and the app does not, the app shows it as it is. Everything else shadPS4 can set stays
in its own window (**shadPS4 settings**).

### Memory cards

A PS4 game keeps each save as a folder, not on a card file. This tab lists the saves in shadPS4's own folder,
`~/.local/share/shadPS4/home/1000/savedata`, and those of every other user. For each save, it shows:

- the game
- the save's title
- its folder
- its size
- when it was last written

Select a save to see its picture and what the game says is in it.

- **Export…** writes the selected saves to one `.zip`, to keep or to share. In it, each save is a folder under its
  game's code.
- **Import…** puts the saves from such a `.zip` in the first user's save folder. The app asks before it replaces a
  save that is there already.
- **Delete…** deletes the selected saves after it asks. A deleted save is gone. Export it first to keep a copy.

Nothing is imported or deleted while shadPS4 runs. Close shadPS4 first.

### View logs

The tab shows everything the app said and did, with the time:

- shadPS4 installed or removed
- what the app set up in shadPS4
- the system modules copied
- the game folders added and taken out
- the settings changed
- shadNet saved
- every change to Steam
- every error

The app logs each game started from Steam by its folder's name when it starts. The line also says whether a
controller was connected. The same lines are in `~/.local/share/bc250-shadps4-manager/bc250-shadps4-manager.log`.
The file turns over at 1 MB, and the app keeps the three older files. **Clear logs**, the tab beside View logs,
empties the file and the View logs tab. It also removes the three older files. The log holds what the app did. It
never holds your SteamGridDB key, your shadNet password or anything else personal.

Two buttons sit above the log. **BC-250 shadPS4 Manager** shows the app's own log. **shadPS4** shows what shadPS4
printed while the last games ran. The run wrapper writes it to `~/.local/share/bc250-shadps4-manager/emulator.log`. Each
game's part opens with a line that says how the wrapper started shadPS4. It ends with a line that gives shadPS4's exit
code. Every line shows your home folder as `~`. This file also turns over at 1 MB, and the app keeps
the three older files. With **shadPS4** chosen, **Clear logs** empties that log and removes its three older files.

### shadNet

shadNet is shadPS4's online service. It offers online trophies, friends and online play, in the games shadPS4
supports online. shadPS4 signs in by itself when a game starts, once it knows your account. **shadNet Account** opens
a window for it:

- **Server**: the shadNet server. It is `srv.shadps4.net:31313`, shadPS4's own, unless you use another one.
- **shadPS4 user**: which of shadPS4's users signs in. Games play as player 1, the first user.
- **shadNet name** and **Password**: your account. The name has 3 to 16 letters, digits, `-` or `_`. It is
  case-sensitive when you sign in.
- **Email**: needed to create an account.
- **Registration key**: only for a server that asks for one to create an account. The server's owner gives it to
  you.

**Create account** makes a new account on the server, with that name, password and email. **Try sign-in** signs in
once and out again, to check the name and password. **Save** keeps it all in shadPS4's own files. Check **Sign in to
shadNet when a game starts** to use the account, or uncheck it to stop. Close shadPS4 before you save, because it
writes its own settings back when it ends.

Beside the title, **shadNet** has a dot that shows its state. Its tooltip says the state in full:

- **shadNet Online** has a green dot. While a game runs, shadPS4 is signed in. Without a game, it means the server
  answers, so shadPS4 can sign in when a game starts. The app asks the server without signing in.
- **shadNet Offline** has a red dot. The server does not answer, or shadPS4's sign-in was refused or dropped. The
  tooltip says why.
- **shadNet Off** has a red dot. No account is set up, or **Sign in to shadNet when a game starts** is off.

While shadPS4 runs, the app reads shadPS4's log every few seconds to see whether it signed in.

shadPS4 keeps the password as plain text in its `users.json`. shadNet sends it over the network unencrypted. Use a
password you use nowhere else.

## Extract PKG

Extract PKG is a window that unpacks package files into the folder layout shadPS4 loads. A package file (`.pkg`)
holds a game, a patch or add-on content. **Games Install** opens the window, and so does a `.pkg` dropped on the main
window. The layout is a `TITLE_ID` folder, for example `CUSA41215`, with `sce_sys/` and the game's files. When you
extract a game into one of the game folders, it shows up in the list when the window closes. It is then ready for
Steam. Extract PKG needs no shadPS4 installed.

It can only open a package that shadPS4 can use, which is a fake-signed (re-encrypted) PKG. Retail packages that
still carry their original encryption cannot be opened. The window then says **Failed to find PFSC header**. A game
unpacks to roughly its package size, so the output folder needs that much room.

Drop a `.pkg` on the window, or **Browse** to it. The icon and the SFO preview fill in at once, before anything is
extracted.

You can open several packages at once. Choose more than one in **Browse**, drop them together, or open them together
from the file manager. The window loads the first one as above. The rest wait their turn, listed under the PKG line.
The games come first, then their updates and add-on content. **Extract PKG** then unpacks the loaded package and
every waiting one after it, into the same output folder. The log runs on from one package to the next. When you choose
not to replace an update with a package, that package is skipped. **Preview Only**, the rename and the comparisons
work on the loaded package alone, and leave the others waiting.

- **SFO Preview:** shows five keys from `param.sfo`:
    - CATEGORY, which is `gd` for a game, `gp` for a patch and `ac` for add-on content
    - CONTENT_ID
    - TITLE
    - TITLE_ID
    - VERSION

    When the package has no readable `param.sfo`, CONTENT_ID and TITLE_ID come from the package header.
    Right-click the preview to copy a line, only its value, or everything.
- **icon preview (click):** shows the package's `icon0.png`, or the app's logo when there is none. Click it to see
  the package's `pic0.png` (or `pic1.png`) full screen. A click, Esc or the B button closes it. Right-click the icon,
  or the full screen picture, for **save as wallpaper**. It saves the picture as a PNG, named after the content ID,
  to your Pictures folder or wherever you choose. The icon's menu also has **show full screen**.
- **Rename to CONTENT_ID:** renames the package file to its content ID, `UP9000-CUSA00038_00-ASTRONAUT0000002.pkg`.
  A game or patch gets its APP_VER added without the dot (`...-0100.pkg`). Add-on content (CATEGORY `ac`) keeps the
  content ID alone. The window says so when the file already has that name, or when another file has it.
- **Output:** the folder the `TITLE_ID` folder goes into. It is the one you used last, or else the first of
  shadPS4's game folders. The line below it says whether it is a game folder. A game extracted elsewhere does not
  show up in the list. The window refuses to extract into a `TITLE_ID` folder that already has something in it, and
  lists what it found. Each extraction or preview needs a fresh folder, so nothing is mixed with an earlier run.
- **Updates:** an update (CATEGORY `gp`) for a game in the output folder goes into a folder beside the game. That
  folder is `TITLE_ID-UPDATE`, for example `CUSA41215-UPDATE`. shadPS4 lays it over the game when the game starts.
  So the game's own folder stays as it is, and deleting the `-UPDATE` folder takes the update out. When the folder
  holds an update already, the window asks whether to replace it. The new one is extracted beside it first. It takes
  the old one's place only when every file was written, else the old one stays. An update package extracted without
  its game in the output folder goes into `TITLE_ID`, as a game does. A package with the game and its update in one
  also says `gp`.
- **Extract PKG:** writes `sce_sys/` first, then every file of the package. The progress bar counts the files.
  `sce_sys/` holds the package's metadata files:
    - `param.sfo`
    - icons, pictures and trophies
    - the decrypted `license.dat`, `nptitle.dat` and `npbind.dat`

    When it is done, the output folder opens in your file manager. The log at the bottom shows each step and each
    file. The same lines go to the log file, see [What goes where](#what-goes-where).
- **Preview Only:** writes only `sce_sys/` and `filelist.txt`. That file lists every file the package holds, with
  its inode and the path it would get. Use it to see what is inside, or to check a package, without the full
  extraction.
- **Salvage Mode (skip bad metadata):** a package with damaged metadata normally stops the extraction at the first
  bad entry. So you see that something is wrong. With Salvage Mode on, the window skips bad entries and extracts the
  rest. The log then ends with a recovery summary. The folder gets `salvage_report.txt`, with the skipped entries,
  and `extraction_errors.txt`, with every error. Files that failed are missing or incomplete. shadPS4 may still run
  the game when it does not need them.
- **Compare Extractions** opens a menu with two tools:
    - **Compare two extraction folders…** compares, for example, this window's output with another tool's. It shows
      which files only one of them has, and which differ in size. When you answer **Yes** to the hash question, it
      also shows which differ in content (SHA-256, slower). The summary goes to the log. A JSON report
      (`compare_report_<date>.json`) goes into the first folder. When both folders have a `filelist.txt`, the tool
      compares those too.
    - **Delta between two compare reports…** takes a before and an after report. They can be from before and after
      a change in the extractor, for example. It tells per count what went up or down, and which files were fixed or
      are new. The text goes to the log, and to `<after report>_delta.txt` next to the after report.

While an extraction runs, the buttons are grayed out. The window then stays open until the extraction has finished.
The window may find, when it opens, that an earlier one did not end cleanly. That happens when the app stopped while
the window was open. The window then says so, with the last file it was extracting. The empty-folder check refuses a
partial `TITLE_ID` folder from then, so delete it.

```
<game folder>/CUSA00038/
├── sce_sys/            param.sfo, icon0.png, pic0.png, pic1.png, trophy/, license.dat, ...
├── eboot.bin           the game's files, in the package's own folder tree
├── ...
└── filelist.txt        every entry of the package: index, inode, type, name and path
```

Patches and add-on content extract the same way into their own folders. For an update, rename its folder after the
game's, with `-UPDATE` added. See [Game updates and mods](#game-updates-and-mods).

A small add-on package may carry only metadata, such as an unlock key. It has no files besides `sce_sys/`. The window
then says "no extractable outer PFS entries detected" and extracts what there is. Some such packages name no files at
all. Their one data block is then written as `inode_1.bin`.

When a package does not extract, the window says why:

- **"is not a valid PKG file":** the file does not start with the PKG magic, a mark every package starts with. It is
  not a package, or it is cut short at the start.
- **"Failed to find PFSC header":** the package's file system could not be decrypted. The package keeps its retail
  encryption, or it is damaged. Only fake-signed packages can be extracted.
- **"Guardrail: target output folder is not empty":** choose or make an empty folder. The `TITLE_ID` folder under it
  must not exist yet, or must be empty. An update is the exception, see **Updates** above.
- **"PKG file size is different":** the file is shorter than its header says. It is an incomplete download or copy.
- **Preflight failed for file N:** the package's metadata for that file is inconsistent. Turn on Salvage Mode to get
  the other files.

A package is a table of metadata entries, followed by an encrypted PFS file system image. The window takes these
steps:

1. It reads the table.
2. It derives the keys the way the console does for fake-signed packages. It uses the "derived key 3" RSA block in
   `entry_keys` and the image key in `image_key`. From them comes the EKPFS key. With the seed in the image
   header, that gives the AES-XTS data and tweak keys.
3. It decrypts the PFS and finds the compressed PFSC container in it.
4. It reads the container's inodes and directory entries.
5. It inflates each file, block by block.

The window is a port of the C++ tool [pkgxtractor](https://github.com/RobertoTorino/pkgxtractor)
(`src/core/file_format/pkg.cpp`, `crypto.cpp`, `psf.cpp`). Those files come from shadPS4 themselves. So the two
give the same files, and the same messages when a package is bad.

## From a terminal

`bc250-shadps4-run` starts the installed shadPS4 with the options you give it. The Steam shortcuts use it. So they
keep working when a newer version of the app brings a newer shadPS4.

```bash
bc250-shadps4-run -f true -g "/path/to/game/eboot.bin"   # a game, full screen
bc250-shadps4-run -g "/path/to/game/eboot.bin"           # a game, as shadPS4's settings say
bc250-shadps4-run -b                                     # shadPS4's own window
```

The run wrapper stays while shadPS4 runs. It passes a stop from Steam on to shadPS4, and ends with shadPS4's exit
code. What shadPS4 prints goes to `~/.local/share/bc250-shadps4-manager/emulator.log`, not to the terminal. The
View logs tab shows it.

The app itself takes packages. `bc250-shadps4-manager file.pkg` opens the package in Extract PKG. Opening a package
with the app from the file manager does the same. `bc250-shadps4-manager a.pkg b.pkg` opens the first and queues the
rest. When the app is open already, the packages go to the open window.

`bc250-shadps4-pkg-cli` extracts without a window:

```bash
bc250-shadps4-pkg-cli <file.pkg> [output folder] [--salvage] [--preview-only] [--no-subfolder]
```

It prints the package's content ID, title and SFO keys. It extracts into `<output>/<TITLE_ID>/`, and writes
`filelist.txt`. The output folder is the package's folder, unless you give another one. `--no-subfolder` extracts
straight into the output folder. `--preview-only` stops after `sce_sys/` and the list. `--salvage` skips bad entries.
The exit code says how it went:

- 0 when every file was written
- 2 when some failed
- 1 when the package could not be opened

The two comparison tools run from the app folder, `~/.local/share/bc250-shadps4-manager/app`, with the python of the
app's venv:

```bash
python -m shadps4_manager.pkgxtractor.compare <folder A> <folder B> [--hash] [--json-out report.json]
python -m shadps4_manager.pkgxtractor.compare_delta <before.json> <after.json> [--out delta.txt]
```

## New shadPS4 releases

Each version of the app was tried with one shadPS4 release, the one **Install** puts in. When the window opens, the
app asks GitHub for shadPS4's newest stable release. It does not look at the daily development builds. When that
release is newer, the shadPS4 line's tooltip and the log say so, with a link to what is new. The app does not install
it by itself, but the [version manager](#versions) can. Once a newer shadPS4 has been tried, it comes with a newer
version of the app, from the [portal](../portal.md). After you update the app, the tooltip says so, and **Install**
brings the newer shadPS4.

## How it works

The Steam shortcuts start `bc250-shadps4-run`, which starts shadPS4. Two things change when Steam is the one that
starts it. When you start it from a terminal, outside Steam, shadPS4 runs as it is.

### Controllers

When Steam starts a game, it tells the game's controller library (SDL) to ignore the controllers Steam handles
itself. It gives the game Steam's virtual controller in their place (Steam Input). shadPS4 then sees only that
virtual controller:

- It has no motion sensors and no touchpad, so a game that uses them cannot.
- On the desktop, it follows the layout Steam has active. While Steam does not know that the game has the focus,
  that is Steam's desktop layout (mouse and keys). The game then gets no controller input at all.

So the run wrapper undoes it. While a real controller is connected, shadPS4 reads that controller itself. It leaves
Steam's virtual one (USB ID `28DE:11FF`) out. The PS button stays Steam's. Without a real controller, the wrapper
leaves Steam's choice as it is. That is the case on a Steam Deck, whose own controls exist only as Steam's virtual
controller.

### A game renamed, moved or gone

A game renamed or moved after it was put in Steam keeps its mark. The app knows each game in Steam by its code. A
game without a code it knows by its file's size. So on **Refresh**, the app finds the game again under its new name,
checked, and says so under the tabs. **Update Steam** then takes the old shortcut out and puts the game in under its
new name.

A game may be no longer there, because it was deleted or is on a drive that is not in. Its shortcut then does not
start shadPS4. A window says which file is missing and what to do. The window closes by itself, so Steam sees the
game end.

### Steam's overlay on the desktop

The KDE desktop of Bazzite is a Wayland session. shadPS4 opens its window through Wayland when it can. But Steam on
the desktop only sees windows that go through X11. XWayland is the X11 server within the Wayland session. A game
window that Steam cannot see has no overlay. **Shift+Tab** and the **PS button** then do nothing. There is also no
way to the game's page, controller layout or settings while it runs. Steam also cannot tell that the game has the
focus. That is why its desktop layout stays active, as described above.

So when Steam starts a game on the Wayland desktop, the run wrapper has shadPS4 open its window through XWayland
(`SDL_VIDEO_DRIVER=x11`). Steam's overlay then works as in any other game. A handheld's Game Mode runs every game
through X11 already.

## What goes where

| What | Where |
|---|---|
| The app | `~/.local/share/bc250-shadps4-manager/app` |
| Its Python, with PyQt6 and cryptography | `~/.local/share/bc250-shadps4-manager/venv` |
| shadPS4 | `~/.local/share/bc250-shadps4-manager/emulator` |
| Extract PKG's log, and its crash marker and progress while it is open | `~/.local/share/bc250-shadps4-manager/pkgxtractor.log`, `.state`, `.progress` |
| Your games and the system modules you put there | `~/Games/PS4` and `~/Games/PS4/Modules` (the app's own folder), and `Games/PS4` on a removable drive |
| shadPS4's saves, settings, system modules | `~/.local/share/shadPS4` (shadPS4's own folder) |
| shadPS4's settings (the Settings tab) | `~/.local/share/shadPS4/config.json`, shadPS4's own |
| shadPS4's play time per game | `~/.local/share/shadPS4/play_time.txt`, shadPS4's own |
| The app's log | `~/.local/share/bc250-shadps4-manager/bc250-shadps4-manager.log` |
| What shadPS4 printed while a game ran | `~/.local/share/bc250-shadps4-manager/emulator.log` |
| Your shadNet account | `~/.local/share/shadPS4/users.json`, the server in its `config.json` |
| The quit hotkeys | `~/.local/share/shadPS4/input_config/global.ini` |
| The app's settings, with Extract PKG's last used folders | `~/.config/bc250-shadps4-manager` |
| The Steam shortcuts | Steam's `shortcuts.vdf` and `grid` folder, per Steam user |
| The covers found on SteamGridDB | `~/.local/share/bc250-shadps4-manager/covers` |
| Launchers | `~/.local/bin/bc250-shadps4-manager`, `~/.local/bin/bc250-shadps4-run`, `~/.local/bin/bc250-shadps4-pkg-cli` |

## Install and remove

Install the app from the [portal](../portal.md), where it is under Gaming. Removing it takes out the app and the
shadPS4 it installed. shadPS4's own folder, with your saves, stays, and so do your games. The games in Steam then no
longer start. So take them out first. Uncheck them and press **Update Steam**.

Installing the app also removes the standalone Bazzite pkgxtractor. Its package extraction is part of this app now,
as Extract PKG. Its settings stay, so Extract PKG starts in the folders you last used there.

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app menu entry only, no icon on the Desktop
./install.sh --uninstall             # remove the app and the shadPS4 it installed; keeps its settings and log
./install.sh --uninstall --purge     # also remove its settings, covers and logs
```

## Disclaimer

The BC250 Bazzite Suite is an independent community project, not affiliated with or endorsed by AMD, ASRock, the Bazzite /
Universal Blue project, Sony, Microsoft, Valve, or the makers of the emulators and the other programs the apps work
with. BC-250 is AMD's product name and Bazzite the Universal Blue project's. PlayStation, PS4, PS5, PS3, PS2, PSP, PS
Vita, PSN, DualSense and Remote Play are Sony's; XBOX, XBOX 360, XBOX Cloud Gaming, Game Pass and Windows are
Microsoft's; Steam, Steam Deck and Big Picture are Valve's; the names of the emulators (shadPS4, RPCS3, PPSSPP, PCSX2,
Vita3K, Xenia) and of HelixSR and DirectMesh belong to their owners. The suite uses them only to say what its apps work with.

## License

GPL-3.0-or-later. shadPS4 is a separate program under its own license (GPL-2.0), downloaded from its own release.
Extract PKG's PKG/PFS/PSF code is a port of shadPS4's (GPL-2.0-or-later).
