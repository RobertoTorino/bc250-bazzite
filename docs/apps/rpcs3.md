<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 RPCS3 Manager](../assets/rpcs3/bc250-rpcs3-manager.webp){ .app-logo }

# BC-250 RPCS3 Manager

BC-250 RPCS3 Manager plays **PS3 games** on the **AMD BC-250** with [RPCS3](https://rpcs3.net), an open-source PS3
emulator. The app does these things for you:

- It installs the RPCS3 build it was tried with.
- It takes the PS3's firmware.
- It finds your games and adds them to Steam.

A game then starts straight away, on the desktop or from Steam's **Big Picture Mode**. On a handheld, that is Game
Mode. A game runs from Steam. [**Start game**](#start-game) starts the chosen one there.

The app sets RPCS3 up for that:

- It turns off RPCS3's welcome dialog and RPCS3's own update check.
- It puts player 1 on your controller.
- It sets each game's screen.

RPCS3 installs the firmware and the packages itself, without opening its window. RPCS3's own window opens only for
[RPCS3's settings](#rpcs3s-settings).

RPCS3 decides whether a game runs, and how well. Its [compatibility list](https://rpcs3.net/compatibility) shows
what others found.

## What you need

- **Your games**, from your own discs or installed from your own packages. The app never downloads games.
- **The PS3's firmware** (`PS3UPDAT.PUP`), the PS3's system software. RPCS3 needs it to start any game. The app
  cannot ship it. Download the firmware from
  [PlayStation's firmware page](https://www.playstation.com/en-us/support/hardware/ps3/system-software/). Then put
  it in `~/Games/PS3/Firmware`. The app gives it to RPCS3.
- **Steam**, started at least once. A game is started from Steam.
- About 80 MB for RPCS3 itself. Its firmware, saves, settings and installed games go in `~/.config/rpcs3`. Its
  shader cache goes in `~/.cache/rpcs3`.
- **fusermount** (FUSE), which Bazzite has. RPCS3 comes as an AppImage, which mounts itself with fusermount.
  Without it, RPCS3 unpacks itself to a temporary folder on every start, which takes longer.

## Using it

The header has four pills:

- **RPCS3 version**
- **RPCS3 Install**
- **RPCS3 Uninstall**
- **Refresh**, which reads everything again

Beside the title is a row of states. Each shows its name and a dot. The dot is green when all is well,
and red when not. Hold the pointer over a state to read it in full.

- **Installed**: the app's own state, such as **Not installed**
- **RPCN**: the state of RPCS3's online service, see [RPCN](#rpcn)
- **Controller**: **Controller connected**, or **No controller** when none is, checked again every few seconds
- **Steam**: green while Steam runs and is signed in, red when it is not

A game started from Steam reads the controller that is connected when it starts. So switch yours on before you
start a game, or press its PS button to wake it. When Steam starts a game without a controller, the app also says
so in a desktop notification. A game in Steam starts only while Steam is signed in. So start Steam and sign in
before you start a game.

A controller can switch off during a game, from its idle timer or its battery. This RPCS3 build does not pick it up
again when it comes back. Quit the game and start it again. See [Controllers](#controllers).

Under the header are links to **RPCS3's release notes** and to this wiki. Below them is a second row of five pills.
Each pill shows what it is for on top, and what it does under it:

- **Games Install**
- **Games Uninstall**
- **Available in Steam**, how many of your games are in Steam
- **RPCN Account**. See [RPCN](#rpcn).
- **Play time**, the time spent in all your games together, as RPCS3 counts it. The tooltip shows each game's time.

Your disc games and the firmware go into the app's own folder. See [Where your games go](#where-your-games-go). You
never choose or browse to a folder for them.

Below the pills are two columns. The first column has five lines: **RPCS3:**, **Firmware:**, **Disc games:**,
**PKG games:** and **RPCN:**. Each line says in short where that part stands, with more in its tooltip. The second
column shows the **Installed version:** of RPCS3.

Then comes a row of six tabs:

- **Your games**
- **Start game**
- **Memory cards**
- **Settings**
- **View logs**
- **Clear logs**

**Start game** and **Clear logs** are buttons.

- **RPCS3**: this line says **Not installed.** or **Installed.**, and names the button to use.
    - The version box in the header shows the version installed.
    - The tooltip says which build is installed, or what Install takes.
    - When this version of the app brings another build, the tooltip and the log say so. **RPCS3 Install** then puts
      that build back in use.
    - **RPCS3 Install** downloads RPCS3 from GitHub, about 80 MB. It is the build this version of the app was tried
      with. The app checks it against its checksum before it installs it.
    - **RPCS3 Uninstall** takes RPCS3 out again. RPCS3's own folder stays, with the firmware, your saves, settings
      and installed games.
- **Firmware**: this line says **Uninstalled.**, or shows the version RPCS3 has and nothing else, such as **4.93**.
    - The folder's path is in the tooltip.
    - The **i** beside it says where the firmware comes from.
    - Put the `PS3UPDAT.PUP` you downloaded in `~/Games/PS3/Firmware`. Once RPCS3 is installed, the app gives it to
      RPCS3 by itself, when the window opens and on **Refresh**.
    - RPCS3 installs it without opening its window. The line under the tabs says when it is done. The Firmware line
      then shows the new version.
    - The app leaves a file alone when RPCS3 has its version already. It also leaves a file alone that RPCS3
      refused, until the file changes.
    - The app does not give RPCS3 a firmware older than the one installed.
    - The file stays in the folder.
- **Disc games**: this line shows where the app looks for disc games. These are `~/Games/PS3` and a removable
  drive's `Games/PS3`.
    - The count is in the tooltip.
    - The **i** beside it says what goes there.
    - Each game goes in a folder of its own. The app also finds games in subfolders, up to five folders deep.
- **PKG games**: this line shows RPCS3's games folder, `dev_hdd0/game/` within RPCS3's own folder, while a game is
  installed in it. While none is, it shows **—**.
    - The whole path and the count are in the tooltip.
    - **Games Install** asks for the folder with your `.pkg` files. RPCS3 then installs them without opening its
      window.
    - First RPCS3 copies the license of a PSN game into RPCS3's own folder. That is a `.rap` or `.edat` file beside
      the packages.
    - Then RPCS3 installs each package, a game's update last. An update needs its game installed first.
    - RPCS3 starts once per file, and a large package takes minutes.
    - The line under the tabs says what came. The line and the table follow.
    - The app takes the files in the folder itself, not those in its subfolders.
    - A game's update is a package too. RPCS3 uses it when it starts the game, and the table lists the game once.

### Versions

The version box in the header is a pill. A click opens the list of the RPCS3 builds you installed. A check mark shows
the one in use. Pick another to put it in use. The games in Steam start whichever build is in use. Every build shares
RPCS3's own folder with the firmware, saves, settings and installed games.

**Manage versions…** under the list opens the version manager. It has two parts:

- **Installed** lists every build in the app's folder.
    - A check mark shows the one in use.
    - The one this version of the app was tried with is marked **Tested**.
    - **Use** puts the chosen build in use.
    - **Delete** removes it. You cannot delete the one in use.
    - **Add** (**Custom build**) takes an AppImage of your own. The app does not check it.
- **Download** gets another build from GitHub.
    - **Refresh** asks GitHub which builds there are. It lists RPCS3's newest build only. GitHub lists RPCS3's
      thousands of builds by name, not by date.
    - **Download** fetches the chosen build. It checks it against the SHA-256 GitHub publishes for it, and puts it
      beside the others.
    - **Use** then puts it in use.

Only the build marked **Tested** was tried on the board. To go back to it, pick it in the version pill's list. Or
press **RPCS3 Install**, which puts it back in use without a download when it is still there.

### Where your games go

The app has folders of its own, which it makes when it opens. You never choose or browse to a folder for them.

- `~/Games/PS3`: put your disc games there, each in a folder of its own. They then show on **Your games**.
- On a USB drive or an SD card, make a folder `Games/PS3` on it. The app looks there too while the drive is mounted.
  Bazzite mounts it under `/run/media` or `/media`.
- `~/Games/PS3/Firmware`: put `PS3UPDAT.PUP` there. The app gives it to RPCS3.

You still install packages from a folder you choose with **Games Install**. These are `.pkg` files, with their
`.rap` or `.edat` licenses. The window to choose it opens in `~/Games/PS3`.

Until version 3.1, you could add folders in the app with **Add folder**. The app no longer looks in those folders.
Move those games to `~/Games/PS3`.

### Your games

The table lists every game the app found. For each game it shows:

- its title and **ID** (BLUS…, NPUB…), from the game's own files
- its version
- its **Folder**, the folder's name. The path is in the tooltip.
- its **Screen setting**

The table has three kinds of games:

- **Disc games** in the game folders, each in a folder of its own, as copied from the disc. That is `PS3_DISC.SFB`
  and the `PS3_GAME` folder. RPCS3 does not start a disc game without its `PS3_DISC.SFB`. The table then shows its
  folder in red.
- **Disc games RPCS3 knows**: those it started before, wherever they are.
- **Installed games**: games installed from a package, in RPCS3's `dev_hdd0/game`.

```
PS3/
└── Demon's Souls/
    ├── PS3_DISC.SFB
    └── PS3_GAME/          PARAM.SFO, ICON0.PNG, USRDIR/EBOOT.BIN, ...
```

**Games Uninstall**, the pill above, deletes the chosen game from the disk.

1. A window first lists what would go, a row each with its size. For a disc game, that is its folder and its update
   in RPCS3's games folder. For a package game, it is the game's folder there. The game's Steam shortcut is in the
   list too, when the game is in Steam.
2. Every row is checked. Uncheck what you want to keep.
3. Press **Delete marked**. **Cancel** deletes nothing.

The saves and the licenses stay. The app will not delete a game at the top of a drive, or one in a folder that
holds another game. The line under the tabs then says so. Delete such a game by hand.

#### Screen setting

**Screen setting** sets how the game fills the screen. You choose it per game:

- **16:9**: the PS3's picture for a wide screen, as RPCS3 draws it by default.
- **4:3**: the picture for a 4:3 screen, with borders on a wide one. Use it for a game made for 4:3.
- **Fill screen**: the picture stretched to fill the window, whatever its shape.

RPCS3 keeps the choice in the game's own settings. That is the file RPCS3's own window writes for a game's custom
configuration. The app changes its two lines and leaves the rest.

The app writes the choice the moment you change it, while RPCS3 does not run. RPCS3 writes its own settings when it
closes, over any change made meanwhile. Steam starts a game full screen. `bc250-rpcs3-run` without `--fullscreen`
starts it in a window. See [From a terminal](#from-a-terminal).

#### Steam

Check the games you want in Steam and press **Update Steam**. The app adds them to Steam as non-Steam games. Their
pictures are the game's own icon and background. Its icon (`ICON0.PNG`) is the logo on the banner. The app takes out
the games you unchecked, and the games it no longer finds. Steam keeps these files in memory. So Steam closes for the
change and starts again in the background.

The info symbol under the list says in short what the boxes and **Start game** do. **Steam** in its text is a link.
It opens Steam's library, and Steam starts when it does not run.

In Steam, each game's name starts with its system, for example **[PS3] Lumines**. So it stands apart in Steam's
menus from the same title on Steam or on another system. A game whose name in Steam differs from its title in the app
is renamed the next time you press **Update Steam**. Until then, **Update Steam** is on for it. Steam sees the renamed
game as a new one. Its play time stays. A controller layout or collection you set for it in Steam has to be set again.

The games are in the library under **Non-Steam**, on the desktop and in Big Picture Mode alike. Each one starts the
game alone in RPCS3, full screen. Steam's menu and **Exit game** work as for any game. On the controller, **Share +
Options** together open RPCS3's own menu with **Exit Game**. See [Controllers](#controllers).

Steam's overlay works over a game started from Steam, in Big Picture Mode and on the desktop. Press **Shift+Tab** or
the **PS button** for the game's page, its controller layout and its settings, without leaving the game. In Big
Picture Mode, the PS button opens Steam's menu over the game. Press it again there to open the power menu, with
**Exit game** and the way out of Big Picture Mode.

A game started from Steam reads your controllers itself. [How it works](#how-it-works) explains both.

A handheld image of Bazzite has a Game Mode that is a Steam session of its own. There, change Steam from Desktop
Mode. In that session, Steam cannot close for the change.

##### Covers

A PS3 game has no cover in the shape Steam's library uses. So the app draws one. It shows the game's icon with its
title, on a dark background.

With a SteamGridDB API key, the app takes a cover from SteamGridDB for each game instead. You enter the key under
**Steam artwork…**. The background and the logo on the game's page stay the game's own.
[Covers from SteamGridDB](covers.md) says how to get the key, how the app looks up a game and how to use a cover of
your own.

#### A game in Steam more than once

The app checks whether a game has more than one shortcut in Steam. When one has, the line under the tabs names the
game and says how often it is there. The tooltip of its **In Steam** box says the same. **Update Steam** is then on
for it. It leaves one shortcut of each game, the one with the latest play time, and takes the others out. Its
question says how many double shortcuts go.

#### Start game

**Start game**, the tab beside Your games, is a button. Choose a game in the table and click it. The game starts
through Steam, as its shortcut in Steam starts it.

- When Steam does not run, the app starts Steam first and waits until it is up. That takes a while. Then it starts
  the game.
- The line under the tabs says **Starting…** until RPCS3 runs. It also says so when Steam did not start the game.
- While RPCS3 runs already, the app starts no second game.
- The tab you were on stays open.

The app does not start a game that is not in Steam yet. The line under the tabs then says to check it and press
**Update Steam** first.

### Settings

The tab scrolls when it is higher than the window.

The tab holds RPCS3's settings that matter for playing. The app writes each one into RPCS3's own settings file
(`config.yml`) the moment you change it, while RPCS3 does not run. RPCS3 reads them when a game starts. A game's own
settings in RPCS3 come first. Those are the Screen setting, and settings made for the game in RPCS3's window. The
tooltips say what each setting does.

- **Picture**:
    - the renderer, Vulkan on the BC-250
    - the resolution scale. 150 % fills a 1080p screen, 300 % a 4K one. A higher scale asks more of the GPU.
    - anisotropic filtering
    - anti-aliasing
    - VSync
    - the frame limit
    - output scaling: bilinear, nearest or AMD's FidelityFX Super Resolution
    - **Fill the screen**, the stretch for every game without a Screen setting of its own
- **Emulation**: the PPU and SPU decoders. The recompilers are the fast ones. The interpreters are exact and slow.
- **Sound**: the sound output library, the volume (up to 200 %) and buffering.
- **Messages in a game**: the trophy message and the shader compilation message.

Beside the volume is **Bazzite's volume for RPCS3**. It is not RPCS3's own volume. Bazzite's sound settings remember
a volume and a mute per application, also once the application is closed. So a game plays without sound while RPCS3
is muted there.

- The app says so in red when RPCS3 is muted or turned down to nothing.
- **Unmute** beside it turns a muted RPCS3 on again. Bazzite keeps it on from then on.
- To change a volume that is turned down, use the sound applet while a game plays. That is the speaker in the panel,
  under Applications.

The app shows a value as it is when RPCS3 knows it and the app does not. Everything else RPCS3 can set stays in
RPCS3's own window (**RPCS3 settings**).

#### RPCS3's settings

**RPCS3 settings** opens RPCS3's own window for what the app does not set:

- its other settings
- its controllers beyond player 1 and 2 (**Pads**)
- its online service (RPCN)

The app sets these by itself, before RPCS3's window first opens:

- RPCS3's welcome dialog off. It would first wait for a check in "I have read the Quickstart guide".
- RPCS3's question before a game's window closes off ("Exit Game?"). A game closed from Steam would stop at it.
- RPCS3's own update check off. See [New RPCS3 builds](#new-rpcs3-builds).
- RPCS3's dark style when the suite's theme is dark. The welcome dialog would have offered it.
- Player 1 on your controller. See [Controllers](#controllers).

What the app set up goes to the log.

**Exit RPCS3**, the first button under the games, closes RPCS3 from the app. Use it when the line under the tabs asks
you to close RPCS3 first. The button is on only while RPCS3 runs. A click ends RPCS3 at once, with no question. A game
that is running ends without saving.

RPCS3's Settings may open with a `config.yml` that another build of RPCS3 wrote. RPCS3 then asks **Remove obsolete
settings?**, because the two builds know different settings. That happened on the board after RPCS3 updated itself
in its own window. With its update check off, it no longer does. Answer **Yes** to let RPCS3 tidy its file for the
build that runs. The app's settings are not in it.

### Memory cards

A PS3 game keeps each save as a folder, not on a card file. This tab lists the saves on RPCS3's hard disk. They are
in `~/.config/rpcs3/dev_hdd0/home/00000001/savedata`, and in the same folder of every other user. For each save the
tab shows:

- the game
- the save's title
- its folder
- its size
- when it was last written

Select a save to see its picture and what the game says is in it.

- **Export…** writes the selected saves to one `.zip`, each as its folder. You can keep it or share it.
- **Import…** puts the saves from a `.zip` there.
    - A `.zip` exported here goes back as it is.
    - A `.zip` with a save's files at the top goes in under the `.zip`'s own name.
    - When a save is there already, the app asks before it replaces it.
- **Delete…** deletes the selected saves after it asks. A deleted save is gone. Export it first to keep a copy.

The app imports and deletes nothing while RPCS3 runs. Close RPCS3 first.

### View logs

This tab shows everything the app said and did, with the time:

- RPCS3 installed or removed
- what the app set up in RPCS3
- the firmware
- the packages, with what each package came to. RPCS3's own log, `~/.cache/rpcs3/RPCS3.log`, says that.
- the folders chosen
- every change to Steam
- every error

The app logs each game started from Steam by its folder's name when it starts. The line also says whether a
controller was connected.

The same lines are in `~/.local/share/bc250-rpcs3-manager/bc250-rpcs3-manager.log`. That file turns over at 1 MB,
and the app keeps the three older files. **Clear logs**, the tab beside View logs, empties the file and the View logs
tab. It also removes the three older files. The log holds what the app did. It does not hold your SteamGridDB key or
anything personal.

Two buttons sit above the log. **BC-250 RPCS3 Manager** shows the app's own log. **RPCS3** shows what RPCS3
printed while the last games ran. The run wrapper writes it to `~/.local/share/bc250-rpcs3-manager/emulator.log`. Each
game's part opens with a line that says how the wrapper started RPCS3. It ends with a line that gives RPCS3's exit
code. Every line shows your home folder as `~`. This file also turns over at 1 MB, and the app keeps
the three older files. With **RPCS3** chosen, **Clear logs** empties that log and removes its three older files.

## RPCN

RPCN is RPCS3's online service. It offers online play, friends and scores, in the games RPCS3 supports online. RPCS3
signs in by itself when a game starts, once it knows your account. **RPCN Account** opens a window for it:

- **Server**: the RPCN server. That is `np.rpcs3.net`, RPCS3's own, unless you use another one.
- **RPCN name** and **Password**: your account.
    - The name has 3 to 16 letters, digits, `-` or `_`.
    - The name is case-sensitive when you sign in.
    - The app does not show a password RPCS3 has already. Leave the field empty to keep it.
- **Email**: needed to create an account, and only then.
- **Token**: the 16 characters the server mails you after it creates the account.

The window has these buttons:

- **Create account** makes a new account on the server with that name, password and email. The server mails the
  token.
- **Try sign-in** signs in once and out again, to check the name, password and token.
- **Resend token** has the server mail the token again. The server does that once every 24 hours.
- Press **Save** to keep it all in RPCS3's own files. Check **Sign in to RPCN when a game starts** to use the
  account, or uncheck it to stop. Close RPCS3 before you save.

The **RPCN** line under the pills names the account that signs in, or says **Off**. Beside the title, **RPCN** has a
dot that shows its state. Its tooltip says the state in full:

- **RPCN Online**, with a green dot
- **RPCN Offline**, with a red dot
- **RPCN Off**, with a red dot

While RPCS3 runs, it shows whether RPCS3 signed in, as its log says. Otherwise, it shows whether the server answers.

The app keeps and sends the password as RPCS3 does, scrambled and never as you typed it. The app sends the email
address to the server once, and does not keep it.

## From a terminal

`bc250-rpcs3-run` starts the installed RPCS3 with the options you give it. The Steam shortcuts use it. So they keep
working when a newer version of the app brings a newer RPCS3.

```bash
bc250-rpcs3-run --no-gui --fullscreen "/path/to/PS3_GAME/USRDIR/EBOOT.BIN"   # a game alone, full screen
bc250-rpcs3-run --no-gui "/path/to/PS3_GAME/USRDIR/EBOOT.BIN"                # a game alone, in a window
bc250-rpcs3-run --installfw "/path/to/PS3UPDAT.PUP"                          # install the firmware
bc250-rpcs3-run --headless --installfw "/path/to/PS3UPDAT.PUP"               # the same without RPCS3's window (the app's way)
bc250-rpcs3-run --installpkg "/path/to/folder"                               # install the .pkg (and .rap) files in a folder
bc250-rpcs3-run --headless --installpkg "/path/to/file.pkg"                  # the same without RPCS3's window (the app's way)
bc250-rpcs3-run                                                              # RPCS3's own window
```

The run wrapper stays while RPCS3 runs. It passes a stop from Steam on to RPCS3, and ends with RPCS3's exit
code. What RPCS3 prints goes to `~/.local/share/bc250-rpcs3-manager/emulator.log`, not to the terminal. The
View logs tab shows it.

## New RPCS3 builds

RPCS3 has no stable releases. It publishes a new build for almost every change. Now and then it marks one with a
version number (0.0.43). Each version of the app was tried with one build, the one **RPCS3 Install** puts in.

When the window opens, the app asks GitHub for RPCS3's newest version number. When that one is newer, the RPCS3
line's tooltip and the log say so, with a link to what is new. The app does not install it by itself. The [version
manager](#versions) can. A newer RPCS3 comes with a newer version of the app, once it has been tried. You get it
from the [portal](../portal.md). After you update the app, the RPCS3 line's tooltip says so, and **RPCS3 Install**
brings it.

RPCS3's own window looks for a newer build when it opens, and offers to update itself. The app turns that check off.
So the build stays the one the app was tried with. RPCS3's **Help** menu can still update it by hand. If you update
it there, the RPCS3 line's tooltip says that RPCS3 updated itself. **RPCS3 Install** then puts the tried build back.
RPCS3's Settings then ask once to remove the settings the other build left. See [RPCS3's
settings](#rpcs3s-settings). A game started from Steam never asks.

## How it works

The Steam shortcuts start `bc250-rpcs3-run`, which starts RPCS3. Two things change because Steam is the one that
starts it.

### Controllers

When Steam starts a game, it tells the game's controller library (SDL) to ignore the controllers Steam handles
itself. It gives the game Steam's virtual controller in their place (Steam Input). With RPCS3's SDL controller
setting, RPCS3 then sees only that virtual controller. That controller has no motion sensors. On the desktop it
follows the layout Steam has active, which may be Steam's desktop layout (mouse and keys).

So the run wrapper undoes it. The run wrapper is `bc250-rpcs3-run`, which the shortcuts start. While a real
controller is connected, RPCS3 reads that controller itself. It leaves Steam's virtual one out (USB ID `28DE:11FF`).
The PS button stays Steam's. Without a real controller, the wrapper leaves Steam's choice as it is. That is the case
on a Steam Deck, whose own controls exist only as Steam's virtual controller.

RPCS3 only reads a controller that its pad settings name. Until they name one, it plays with the keyboard. So the app
writes them:

- Player 1 is on the controller connected. A second one is player 2.
- They go through RPCS3's SDL controller setting, with RPCS3's own button layout for it. So Cross is the bottom face
  button.
- **Share + Options** together, or the Guide button, open RPCS3's own menu in the game, with **Exit Game** in it.

RPCS3 has no button chord that quits a game outright. That menu is its way out on the controller, beside Steam's.

RPCS3 knows a controller by the name SDL gives it, which is not the kernel's. So the app asks SDL for the names
whenever the controllers connected change. It uses Bazzite's SDL3 library, the same one RPCS3 uses. The log says
which player went on which name. Once you save RPCS3's own **Pads** settings in its window, that file is RPCS3's.
The app then leaves it alone. On a system without SDL3, the app writes the kernel's name, which RPCS3 may not match.
The log says so.

A controller can leave during a game and come back. For example, its idle timer or an empty battery switches it off,
and you wake it with its PS button. This RPCS3 build then does not know it until you start the game again. RPCS3
knows a controller it had by its name, its device path and its serial together. A Bluetooth controller that
reconnects gets a new device path from the kernel.

RPCS3 has changed this since. It now matches a reconnected controller by name and serial. A later version of the app
brings a build with that change, once it has been tried on the board. Until then, quit the game and start it again
from Steam with the controller on. To quit, use Steam's menu, or **Share + Options** and **Exit Game**.

### A game renamed, moved or gone

A game keeps its mark when you rename or move it after it was put in Steam. The app knows each game in Steam by its
code. When a game has no code, the app knows it by its file's size.

- On **Refresh**, the app finds the game again under its new name, checked, and says so under the tabs.
- **Update Steam** then takes the old shortcut out and puts the game in under its new name.

A shortcut to a game that is no longer there does not start RPCS3. The game may be deleted, or on a drive that is not
in. A window says which file is missing and what to do. It closes by itself, so Steam sees the game end.

### Steam's overlay on the desktop

The KDE desktop of Bazzite is a Wayland session. RPCS3 opens its windows through Wayland when it can. But Steam on
the desktop only sees windows that go through X11. On the Wayland desktop, those go through XWayland, the X11 server
within the Wayland session. A game window Steam cannot see has no overlay. **Shift+Tab** and the **PS button** do
nothing then.

So when Steam starts a game on the Wayland desktop, the run wrapper has RPCS3 open its windows through XWayland
(`QT_QPA_PLATFORM=xcb`). Steam's overlay then works as in any other game. A handheld's Game Mode runs every game
through X11 already.

## What goes where

| What | Where |
|---|---|
| The app | `~/.local/share/bc250-rpcs3-manager/app` |
| RPCS3 | `~/.local/share/bc250-rpcs3-manager/emulator` |
| RPCS3's firmware, saves, settings, installed games | `~/.config/rpcs3` (RPCS3's own folder) |
| RPCS3's play time per game | `~/.config/rpcs3/GuiConfigs/persistent_settings.dat`, RPCS3's own |
| RPCS3's settings (the Settings tab) | `~/.config/rpcs3/config.yml`, RPCS3's own |
| RPCS3's GUI settings for the welcome dialog, the exit question, the update check and the style | `~/.config/rpcs3/GuiConfigs/CurrentSettings.ini`, RPCS3's own |
| Player 1 and 2 on your controllers | `~/.config/rpcs3/input_configs/global/Default.yml`, RPCS3's own |
| Each game's screen setting | `~/.config/rpcs3/custom_configs/config_<Id>.yml`, RPCS3's own |
| RPCS3's shader cache, and its own log `RPCS3.log`, which the app reads to see what RPCS3 installed | `~/.cache/rpcs3` |
| The volume Bazzite remembers for RPCS3 (read only) | `~/.local/state/wireplumber/stream-properties`, WirePlumber's |
| Your disc games and the firmware file | `~/Games/PS3` and `~/Games/PS3/Firmware` (the app's own folder), and `Games/PS3` on a removable drive |
| The app's settings | `~/.config/bc250-rpcs3-manager` |
| The app's log | `~/.local/share/bc250-rpcs3-manager/bc250-rpcs3-manager.log` |
| What RPCS3 printed while a game ran | `~/.local/share/bc250-rpcs3-manager/emulator.log` |
| The Steam shortcuts | Steam's `shortcuts.vdf` and `grid` folder, per Steam user |
| The covers found on SteamGridDB | `~/.local/share/bc250-rpcs3-manager/covers` |
| Launchers | `~/.local/bin/bc250-rpcs3-manager`, `~/.local/bin/bc250-rpcs3-run` |

RPCS3 can keep its drives elsewhere, in its **Configuration > Virtual File System**. The app reads where they are.

## Install and remove

Install the app from the [portal](../portal.md), where it is under Gaming. Removing the app takes out the app and the
RPCS3 it installed. RPCS3's own folder stays, with the firmware and your saves. Your games stay too. The games in
Steam then no longer start. So uncheck them and press **Update Steam** first, to take them out.

```bash
./install.sh                         # install or update
./install.sh --no-desktop-shortcut   # app menu entry only, no icon on the Desktop
./install.sh --uninstall             # remove the app and the RPCS3 it installed; keeps its settings and log
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

GPL-3.0-or-later. RPCS3 is a separate program under its own license (GPL-2.0), downloaded from its own release.
