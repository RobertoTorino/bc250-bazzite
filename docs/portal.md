<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC250 Bazzite Suite](assets/portal/bc250-bazzite-suite.webp){ .app-logo }

# Portal

The portal is the BC250 Bazzite Suite's front door. It is one fullscreen view that installs, opens, updates and
removes the suite's apps. It suits a TV and a controller as much as a desk, as Steam's Big Picture does for Steam. It
works with the keyboard, the mouse or a controller alike. The [Portal Tour](portal-tour.md) shows it in a four-minute
video.

The portal opens with a short animated intro of about three seconds, with its own sound. The intro shows the suite's
icon and its name, **BC250 BAZZITE SUITE**, before the view appears. To skip it, press any key, click, or press any
button on the controller. When the intro has played to its end, a short welcome sound follows. A skipped intro gets
none.

**The header** holds these parts:

- The suite's icon, as large as a tile's. Click it to watch the [Portal Tour](portal-tour.md) over the whole screen.
  **A** or Space pauses the tour, and **B** or Esc closes it. Without a connection, the tour opens in the browser.
- The suite's name, with the version and the **Beta** stage in orange. Click the name to open this wiki.
- A small **i** that says where the apps install from.
- A line that says in a few words what the open category is for.
- **☰ Settings** at the top right, then **– Minimize** and **✕ Exit** in the corner. **– Minimize** hides the
  portal in the system tray. **✕ Exit** closes the portal.
- A battery for each connected device with one, left of **☰ Settings**. It shows a controller, a mouse, a keyboard
  or a headset. The level is under it, and the fill turns red at 20 % or less. A yellow bolt means the device is
  charging. Hover a battery to see the device's name. Without such a device, no battery shows.

Under them is a row of thirteen big symbols. Four act on the apps:

- **Refresh**, two circling arrows, looks again at which apps are installed
- **Sys info**, a chip
- **Install all apps**, a grid of apps with an arrow down
- **Install all updates**, a circular arrow around an arrow down

Nine are shortcuts to what is outside the suite:

- **Files**, a folder
- **Steam**
- **Discord**, a round face with two eyes
- **YouTube**, a screen with a play triangle
- **GitHub**, a cat in a disc
- **Bluetooth**
- **Network**
- **Volume**, a loudspeaker
- **Screen**, a screen on its foot

Each one is described below. Hover over a symbol to see what it does. The symbol with the focus has a silver frame,
as a tile does. A symbol that has nothing to do is grayed out. On a screen 1280 pixels wide, the portal draws the
symbols smaller when the row would not fit otherwise.

On the right of the symbols, you see how many apps are installed. Under that is the status, with a line for each of
these:

- The CPU's and the GPU's load and temperature, as in **CPU 12% 54°C | GPU 3% 61°C**
- The date and the time, as in **Thursday 11/5/26 | 07:44 PM CEST**
- The weather in the place you chose on the Settings page, after its symbol, as in **Amsterdam 8°C Partly cloudy**

The line at the bottom says what the keys and the controller's buttons do.

**Board Test** and **Quickfix** are always installed with the portal. Every other app is optional. Below the header
is a strip with a name for each [category](apps/categories.md): Sustainable, Graphics, Gaming and Utilities. The
notice of updates sits beside the strip. Each app is a large tile under its category. The tiles run left to right in
the order of `apps.toml`, as many to a row as the screen fits. Board Test is always the first tile on Sustainable,
and the quickfixes come first on Utilities. The tile with the focus has a silver frame. Move the focus with the arrow
keys, the d-pad or the stick, or point at a tile with the mouse. A tile has these parts:

- **The icon** is its category's. The portal draws it from a 512 px picture, so it stays sharp on a 4K screen. The
  icon is gray while the app is not installed. Hover over the tile to see what the app does, its state and the
  release this portal pins.
- **The name** shows without the suite's "BC-250" prefix.
- **Press the tile** to open the app. Click it, press Enter, or press A on the controller. An app with more than one
  window asks which one. Pressing a tile that is not installed offers to install it. An app that is open already
  comes to the front instead, without the board warning again. This also works for an app behind the portal or
  minimized. It needs KDE's desktop (KWin), which Bazzite's desktop is.
- **Update** installs the tile's update or reinstall at once. Right-click the tile, or press Y on the controller. An
  app that changes the board asks first. While a newer portal is out, these update the portal instead, as
  **Updates** below describes. A right click on a tile with nothing to update opens its menu.
- **The tile's menu** holds every action. Open it with the Menu key or M. On the controller, press the left button
  of the four. That is X on an XBOX controller and Square on a PlayStation one. The menu has **Open**, or the app's
  two windows. It has **Install**, an arrow into a tray. That entry reads **Update**, in red, when an update is
  waiting. It reads **Reinstall** for an installed app, in red with a circular arrow when its version is unknown.
  Last comes **Uninstall**, a bin. What you cannot do now is grayed out. Board Test and the quickfixes have no
  Uninstall. The portal's own uninstall removes them.
- **A quickfix** is a tile of its own on Utilities, such as Quickfix, MangoHud Config and Fix GPU Metrics.
  [BC-250 Quickfix](apps/quickfix.md) is an app of small quickfixes, each for one job. Pressing a quickfix's tile
  opens that quickfix's window. A quickfix that changes the board says so under its name and asks first. Reinstall
  in its menu reinstalls the whole app, since every quickfix's tile shows the app's state.
- **A red dot** in the icon and **Update** under the name mean that an update is available.
- **A red circular arrow** in the icon and **Reinstall needed** under the name mean that you should reinstall the
  app. The app is installed, but not by this portal. It was installed by hand, or under an earlier name of the app.
  So the portal does not know its version. Reinstall in its menu installs the version this portal pins. An app
  installed from a checkout of the repository without its version recorded shows it too.
- **changes the board**, in orange under the name, marks an app that changes how the board runs. Hover over the tile
  to read its popup. The popup says what the app touches and what stays after a restart or a power off. It also says
  what the app never touches and how you undo the change. It is the same text that opens the app's chapter of this
  wiki.
- **App not available**, in red under the name, means that this app's release was withdrawn because of a problem.
  The problem may be privacy, security or another reason. Hover over the tile to read which. You cannot install or
  open the app. When it is installed, the portal says so at start. Then the portal removes the app with the app's
  own uninstaller in a terminal. If that fails, Uninstall stays in its menu, so you can try again.
- **Installing…**, **Removing…** or **Downloading…** shows in blue under the name while that runs on the app. A
  download counts its megabytes as they come in, as in **Downloading… 40 MB**.

**The categories.** The line under the title says what the open category is for. [The apps](apps/index.md) lists the
apps by category. To change the category, click a name in the strip. You can also press LB or RB on the controller,
or Page Up and Page Down on the keyboard. The portal always opens on the first one, Sustainable.

| Keyboard | Controller | Mouse | Does |
|---|---|---|---|
| Arrow keys | D-pad or left stick | Point | Move the focus between the tiles, the symbols and the notices |
| Enter | A | Click | Open the app, press a symbol, open a notice |
| U | Y | Right click | Update or reinstall the tile's app. While a newer portal is out, update the portal |
| Menu key, M | X, or Square on a PlayStation controller | | The tile's menu with Open, Install, Update, Reinstall and Uninstall |
| Page Up, Page Down (or Q, E) | LB, RB | Click a name | The category before and after |
| S | ☰ (Start) | Click ☰ | The Settings page, and back from it |
| K | R3 (the right stick pressed) | | Show or hide Bazzite's on-screen keyboard, Plasma Keyboard. R3 also works in a question or the file dialog |
| Escape | B | Click ✕ | Close a menu or a question. On the Settings page, go back to the apps. Else, exit the portal |

**The TV remote.** Your TV's remote moves the focus in the portal too, over HDMI, with no setup. Its arrows
work as the arrow keys do.

**Exiting.** The **✕** symbol in the top right corner closes the portal. B and Escape do so too, when no menu,
question or Settings page is open. The portal closes at once, without a question. Only while a download or an
install runs, it first asks *Do you really want to exit the Portal?* It also says what exiting does to the job. A
download stops. An installer finishes in its terminal window, but the portal does not record it. **No** has the focus
there. To exit, move to **Yes** with the arrow keys, the d-pad or the stick, and press Enter or A. B or Escape
answers No.

**Questions.** A question has buttons such as Yes and No, or Install and Cancel. The arrow keys, the d-pad and the
stick move between the buttons. Press Enter or A for the button with the focus.

**The on-screen keyboard.** R3 shows Plasma Keyboard, the desktop's virtual keyboard, so you can type with the
controller. You need it for a file name when you choose a wallpaper, for example. Bazzite shows the keyboard only
after touch or pen input, which a controller is not. So while it shows, the portal sets it to show for any input. R3
again hides it and sets your own choice back. Closing the portal does so too. When the desktop has no virtual
keyboard chosen, R3 says where to choose it. That is System Settings, Keyboard, Virtual Keyboard, Plasma Keyboard.

The portal reads the controller with [pygame-ce](https://pypi.org/project/pygame-ce/), which the portal's installer
adds to the suite's venv. It takes any controller that SDL knows, such as XBOX, PlayStation and most others. The
portal listens to the controller only while its own window has the focus, so a game's input never moves it. Without
a controller, the keyboard and the mouse work as always.

**The touchpad as the mouse.** On a DualShock 4, a DualSense or a DualSense Edge, the touchpad moves the mouse
pointer. Steam does the same for the Steam Controller. Slide a finger to move the pointer, and press the pad to
click. Press it with two fingers on it for a right click. **Touchpad** on the Settings page sets how fast the pointer
goes. Like the rest of the controller, the touchpad works while the portal has the focus, in its menus and questions
too. In an app the portal opened, the app's own touchpad mouse takes over, at the same speed. Wayland lets no program move the pointer, so the portal makes a mouse of its own for the touchpad. The desktop
lists it as **BC250 Bazzite Suite touchpad** while the portal runs. Bazzite gives you the access it needs. A
controller that Steam Input owns has the touchpad of Steam's desktop layout instead.

**Handhelds.** The view is made for a TV at 1080 p or 4K as much as for a handheld. Examples are the Steam Deck at
1280 x 800 and the ROG XBOX Ally X. The Ally X has 1920 x 1080, shown at 1280 x 720 with the desktop's scaling. Below
1000 px of height, the portal draws the icons, the type, the header and its symbols smaller, down to about two
thirds. Then the header, two rows of icons and the line of keys fit on the screen. You can also swipe a page with a
finger on the touch screen. The built-in controls are controllers like any other. Steam Input may already turn them
into keys. The Deck's desktop layout does so, with the d-pad as the arrow keys, A as Enter and B as Escape. Then the
keyboard column above applies and works as it is.

**The Steam Controller, and any controller Steam Input owns.** While Steam runs, it takes the controllers it has
Steam Input on for. These are always the Steam Controller and a Steam Deck's own controls. Outside a game, Steam's
desktop layout turns their buttons into keys and the mouse. The portal sees only those keys. By default, that layout
gives the d-pad the arrow keys, A Enter and B Escape. LB, RB, R3, the back buttons and others have no key, so they do
nothing in the portal. You can get every button in two ways:

- **Start the portal from Steam.** In Steam, choose **Games**, **Add a Non-Steam Game to My Library**, and pick
  **BC250 Bazzite Suite**. You can also browse to `~/.local/bin/bc250-bazzite-suite`. Started from Steam, the portal
  reads the controller as an XBOX controller, with the buttons in the table above. Steam's controller settings for
  that entry can give any button or key you like to the back buttons, the touchpads and the other extras.
- **Give the buttons keys in the desktop layout.** In Steam, open **Settings**, **Controller**, **Desktop Layout**
  (Edit). Then set the keys of the table's keyboard column:

    - LB to Page Up
    - RB to Page Down
    - Y to U
    - X to M
    - ☰ to S
    - R3 to K

    The back buttons can take any of these keys too. The layout is Steam's, and it applies to every program outside
    a game.

The tools for working on the suite are not in the portal. They are in `dev/` of the repository. They run from a
checkout and have no release. [Nexus Dashboard for BC-250](development/dashboard.md) opens them all:

- Nexus Release Tool
- Nexus Deps, for the suite's packages and tools on this machine
- Nexus Garbage Remover, for crash dumps, the Trash and caches
- Nexus Installer Tests, which runs the installer tests one at a time
- Nexus Demo Recorder
- Nexus Sound Lab, for short sound effects for the windows
- Nexus TTS, which speaks a text aloud
- Nexus Remix Studio, which mixes a voice with a synthesized background
- the video tours
- the icons

Start Nexus Dashboard for BC-250 from the checkout, or give it a menu entry with its `install.sh`.

- `apps/` may also contain standalone tools with a `.standalone` marker. They do not appear in `apps.toml`, and the
  portal does not install or open them.
- Install, update and uninstall run **the app's own installer** in a terminal window over the portal. Installers may
  ask for the sudo password, and they print what they do. The portal watches for the result and refreshes. A
  terminal whose installer ended well closes by itself. One that failed stays open with what happened until you
  press Enter.
- Apps that change how the board runs are marked **changes the board**. They cover the CU/core unlocks, the GPU
  governor, GPU overclocking, the ACPI override, the VRAM split and a patched GPU driver. The portal warns before it
  installs or opens them. The tile's popup says what each one changes and how you undo it.
- Each portal release pins one tested release of every app in
  [`apps.toml`](https://github.com/RobertoTorino/bc250-bazzite/blob/main/portal/apps.toml). The portal downloads
  exactly those tarballs from the suite's GitHub releases. It checks each one against the SHA-256 pinned there. Until
  one is pinned, it checks against the release's `SHA256SUMS`. Then it unpacks the tarball, and it never writes
  outside its folder.
- **Updates:** a red dot marks every app whose installed version differs from the one this portal pins. Update in its
  menu installs the pinned version. An app installed from a checkout of the repository counts as well. The portal
  records the checkout's version of it and compares that with the one it pins. A portal that runs from a checkout
  shows what it installed from there as installed, whatever it pins. The red notice beside the category strip counts
  these apps and the apps that need a reinstall, for example **● 2 updates, 1 reinstall**. Press it to list each one
  with its category and versions. Choose one to go to its tile. A category with such an app shows their number in red
  after its name. So you see them also when their category is not open. To install an update, press Y or right-click
  its tile.
- **Portal updates:** newer app versions come with a newer portal release. At start, the portal looks for one on
  GitHub. When there is one, an orange **PORTAL UPDATE AVAILABLE** shows under the name on the intro. An orange
  **UPDATE AVAILABLE, PRESS Y TO UPDATE** shows beside the category strip. Its tooltip says what the release brings,
  with each app's old and new version. An example is **Portal 0.9.1: updates ACE Queues and Memory Manager**. To
  update, press Y, right-click a tile, or click the banner. With the focus on the banner, Enter or A clicks it too.
  The portal downloads the release and checks it against the release's `SHA256SUMS`. Then it runs the release's
  `install.sh` in a terminal. The installer asks for your sudo password for Board Test's copy to `/opt`. The banner
  says **DOWNLOADING THE UPDATE…** and then **INSTALLING THE UPDATE…**. When the installer has ended well, the portal
  starts again as the new version. The installed apps it updates then show the red dot. When the installer fails, the
  terminal stays open with what happened, and Y tries again. While an app installs, the portal update waits for it.

    The portal also offers a release built again under its own version. The tooltip then says **a new build of this
    version**. The installer keeps the checksum of the tarball it installed from, in `build.sha256` beside the
    program. It does so when the tarball is next to the unpacked folder, as the install steps and the portal's own
    update leave it. The portal compares that checksum with the newest release's. A portal installed from a checkout
    is not offered the release of its own version, because that would replace the checkout's portal. It is still
    offered a newer version. The unpacked release stays in `~/.local/share/bc250-bazzite-suite/state/portal-update/`
    until the next one. Its tarball and `SHA256SUMS` are removed once it is installed.

- **Outside the suite**, in orange beside the red notice, names newer releases of programs outside the suite. Each is
  a program that an installed app installs in its newest version, so the app can install it now. Press the notice to
  list them, for example **Upscaler Manager (Graphics): HelixSR 1.9.3 is out**. Each line says what to do in the
  app. Choose one to go to its tile. The tile says it too, under the name. This covers HelixSR, in the BC-250
  Upscaler Manager. The portal shows what the app found the last time it looked, so open the app now and then. When
  you come back to the portal, the notice follows. The notice leaves out the programs an app pins. These are
  shadPS4, PPSSPP, RPCS3, Vita3K, PCSX2's stable release, Xenia and DirectMesh. A newer one of those comes with a new
  version of the app, as an update above.
- **Restart: portal x.y.z is installed** is a red button. You may install a newer portal by hand while a portal
  window is open, with its `install.sh` in a terminal. That window keeps running the old portal, with its old app
  versions. Starting the portal again only brings that window to the front. When you come back to the window, it
  sees the newer portal and shows this button. Click it to restart into the new portal. The new portal then shows the
  red dot on the apps it updates. While an app installs or uninstalls, the button waits for it to end.
- **Installed apps**, on the right of the symbols, says how many of the portal's apps are installed, for example
  **12/27 installed**. An app that is not available anymore is not counted.
- **The status**, under it, has three lines:

    - The first line shows the CPU's load and temperature and the GPU's load and temperature. The portal reads them
      every two seconds. The load is the share of the last two seconds.
    - The second line shows the day, the date (month/day/year) and the time with its time zone. The portal reads
      them every second. **Clock** on the Settings page sets how the time reads.
    - The third line shows the weather's symbol, the place, the temperature and the sky. It needs a place chosen
      under **Weather** on the Settings page. Without a place, there are two lines.

    Nothing is read while the portal is minimized. The GPU's load comes from the kernel's load sensor where there is
    one. The BC-250's stock kernel has none. Then the portal adds up the GPU time of your own programs, the games and
    the desktop among them. Or it reads GPU Governor's corrected metrics, when GPU Governor has set them up. What the
    system does not report is left out of the line.

- **Install all updates**, a symbol at the top, is active when the notice names any app. A red badge on it says how
  many, and its tooltip says what it does. Click it to install them all, updates and reinstalls, one after the
  other. The portal asks once, with the list. It warns when one of them changes the board. Each app's installer runs
  in its own terminal, as a single install does. When one asks for your password, type it in that terminal. The
  next one waits until it has ended. While the batch runs, the badge shows which one of how many it is at, for
  example **2/5**. When one install fails, the others go on. At the end, the portal names those that failed,
  and Install in their tiles' menus tries again. If a terminal was closed while the portal waits for it, **Refresh**
  can stop waiting. That stops the rest of the batch too.
- **Install all apps**, a symbol at the top, is active when the open category has apps that are not installed yet.
  Its tooltip says how many. Click it to install them one after the other, the same way as **Install all updates**.
  You get one question with the list and the board warning. Each installer runs in its own terminal, and the badge
  shows which one of how many. The symbol is grayed out once every app of the category is installed. So a portal
  installed for the first time fills a category with one click.
- **Files**, a symbol at the top, opens the desktop's file manager on your home folder. On Bazzite's KDE Plasma,
  that is Dolphin.
- **Steam**, a symbol at the top, opens Steam. When Steam runs already, it brings Steam's window to the front.
- **Discord**, a symbol at the top, opens Discord in a maximized window of Brave Browser.
  Brave Browser must be installed as a Flatpak, `com.brave.Browser`. Get it from Bazzite's software store, or with
  `flatpak install flathub com.brave.Browser`. Without it, the portal says so and opens nothing.
- **YouTube**, a symbol at the top, opens YouTube in a maximized window of Brave Browser.
  Brave Browser must be installed as a Flatpak, `com.brave.Browser`. Get it from Bazzite's software store, or with
  `flatpak install flathub com.brave.Browser`. Without it, the portal says so and opens nothing.
- **GitHub**, a symbol at the top, opens github.com in the desktop's own browser. It opens in a normal window with
  its tabs and address bar. A browser that runs already comes to the front with a new tab.
- **Bluetooth**, **Network**, **Volume** and **Screen** are four symbols at the top. Each opens a page of the
  desktop's settings:

    - **Bluetooth** opens the Bluetooth settings, where you pair or remove a controller or a headset
    - **Network** opens the network settings, with the connections and Wi-Fi
    - **Volume** opens the sound settings, with the volume, the output and the input
    - **Screen** opens the display settings, with the resolution, the refresh rate and the scaling

    On KDE Plasma, that is System Settings on that page. On GNOME, it is GNOME's Settings.

- **✕ Exit**, the symbol in the top right corner, closes the portal, as B and Escape do. See **Exiting** above.
- **– Minimize**, left of **✕ Exit**, hides the portal in the system tray, next to the clock on the taskbar.
  The portal's icon shows there while it is hidden. Click that icon to bring the portal back. Starting the
  portal again from the menu or the Desktop brings it back too. Right-click the icon for **Show the portal**
  and **Exit**. While the portal is hidden, its music waits. It reads no status, batteries or weather until it
  comes back. On a desktop without a system tray, the portal goes to the taskbar instead.
- **☰ Settings** is the symbol at the top right. The ☰ button on the controller opens the page too. That button is
  Start, or Options on a PlayStation controller. The Settings page takes the place of the category strip and the
  tiles, under the same header. It holds the nine settings below, each a pill with a short line beside it. On a
  small screen, the page scrolls and follows the focus. Move between the settings with the arrow keys, the d-pad or
  the stick. Press A or Enter to change one. B, Escape or ☰ again goes back to the apps.
- **Icons on Desktop**, on the Settings page, says Yes or No. Click it to switch. When it is on, every installed app
  has an icon on the Desktop. When it is off, only the portal's icon is there, and you start the apps from the
  portal. The apps stay in the app menu either way. So KDE's search and Steam's **Add a Non-Steam Game** still find
  them. The first time the portal starts with app icons on the Desktop, it asks whether to keep them. While the
  switch is off, the portal removes the icons that the apps' installers put there. It does so at start and after
  each install. It only touches the icons of the suite's apps, never its own or anything else on the Desktop.
- **Sound**, on the Settings page, says Yes or No. Click it to switch. With Sound on, the intro plays its sound when
  the portal opens, and the welcome sound follows it. Every action also gives a short sound:

    - each move and button on a controller
    - each key that acts, which are the arrow keys, Enter, Space, Escape, Tab, Page Up and Page Down, Q, E, U, S, K,
      M and the Menu key
    - each click on a tile, a symbol, a pill, a button, a category or a menu entry

    Any controller works, also one that Steam turns into keys. A key held down sounds once, and typing in a text
    field stays silent. No turns both sounds off. The portal remembers the choice. When the board has no audio
    output, the pill says No and is grayed out, and the portal stays silent.

- **Music**, on the Settings page, says Yes or No. Click it to switch. With Music on, a track plays quietly, over and
  over, while the portal is in front. Music has its own switch, apart from Sound. With Sound off, the music plays
  on. With Music off, the intro and the actions keep their sound. The music waits while the intro or the Portal Tour
  plays. It also waits while the portal is minimized, and while another window such as a game or an app has the
  focus. When you are back, it plays on from where it was. The portal remembers the choice. When the board has no
  audio output, the pill says No and is grayed out.
- **Music track**, on the Settings page, sets which track the music plays. **Built-in** is the portal's own. To use
  a track of your own, click the pill, then **Choose a track…**. The pill then says **Custom**. Your track can be an
  Ogg, Opus, MP3, FLAC, WAV or M4A sound file. It plays at once, from its start. The portal refuses another file and
  says why. **The portal's track** brings the portal's own back. The portal keeps a copy of your track in
  `~/.local/share/bc250-bazzite-suite/state/`, so you may move or delete the original. The portal's `--purge`
  removes the copy.
- **Theme switcher**, on the Settings page, shows the theme, which is the look of every app in the suite. Click it
  for the next one:

    - **Gunmetal**, dark and cool blue-gray, the default
    - **Silver**, light
    - **Warm**, dark warm gray with a bronze accent

    The theme is one choice for all the apps, kept in `~/.config/bc250-bazzite-suite/theme`. The portal shows it at
    once and stays open. Each app takes it the next time it starts.

- **Wallpaper**, on the Settings page, sets a picture behind the portal. You see it through the pills that are not
  active. The portal starts with the picture that comes with it, **Example**. Click the pill for these choices:

    - **Choose a picture…** for your own picture, shown as **Custom**
    - **Example wallpaper** for the portal's own again
    - **No wallpaper** for none

    The portal remembers that choice. Your picture must be a PNG, JPEG or WebP of at least 1920 x 1080 pixels, in
    16:9. Examples are 1920 x 1080, 2560 x 1440 and 3840 x 2160. The portal refuses another picture and says why.
    The picture fills the window, under a veil of the theme's color, so the text stays readable. **Transparency**, a
    slider in the same menu, sets that veil from 0 to 90 %. It starts at 60 %. Move it up for a dark or busy
    picture, so the icons stand out. Move it down to see more of the picture. The window changes while you move the
    slider, and the portal remembers it. The portal keeps a copy of your picture in
    `~/.local/share/bc250-bazzite-suite/state/`, so you may move or delete the original. The portal's `--purge`
    removes the copy. The menu also lists the last 10 wallpapers you chose, newest first, under **Used before**.
    Click one to use it again. The portal remembers only where each picture was, in `wallpapers.json` in the same
    folder. So a picture that was moved or deleted since shows as not found until it is back.

- **Clock**, on the Settings page, shows **12 h** or **24 h**. It sets how the time in the status reads. Click it
  for its menu:

    - **12-hour clock (AM/PM)** or **24-hour clock**
    - **Seconds**, on or off
    - the time zone, which is **the board's own**, **CET** or **UTC**

    The board's own zone is the system's, as at first. **CET** is Central European Time, which is CEST in
    summer. The date follows the zone too. The portal remembers the choice.

- **Weather**, on the Settings page, shows the place or **None**. It puts the weather in the status at the top. The
  weather comes from [Open-Meteo](https://open-meteo.com/), free and without an account. To choose a place, follow
  these steps:

    1. Click the pill, then **Choose a place…**.
    2. Type a city or town. R3 brings the on-screen keyboard.
    3. Press **Search**.
    4. Pick the right place from the list, then press **Use this place**.

    The status' third line then shows the weather, under the date and the time. It shows a symbol, the place's
    name, the temperature and the sky. The symbol is a sun or moon, clouds, fog, rain, snow or thunder. Hover over
    the line to see the wind and the humidity too. Click the line to open the forecast for the place at
    [wttr.in](https://wttr.in/), a page without ads, in Brave Browser. Brave Browser must be installed as a Flatpak.
    Without it, the portal says so. The portal gets the weather again every 30 minutes while it is
    not minimized. **Update the weather now** asks at once. When Open-Meteo cannot be reached, the last weather
    stays, and its tooltip says why. **No weather** removes it, and nothing goes to Open-Meteo anymore. Until you
    choose a place, the portal sends nothing. See [Privacy](privacy.md).

- **Touchpad**, on the Settings page, shows the speed. It sets how fast the touchpad of a DualShock 4 or a DualSense
  moves the mouse pointer. Click it for the next speed. The steps are 50, 75, 100, 125 and 150 %, then 50 again. At
  first, it is 100 %, the normal speed. The new speed applies at once, and the portal remembers it.
- **Sys info**, a symbol at the top, opens a small window with what the system reports about the board. It lists
  these parts:

    - the board
    - the BIOS, with UEFI and Secure Boot
    - the CPU, with its model, the cores and threads online, the top clock and the microcode
    - each GPU, with its name, driver, VRAM, shared memory, clock levels, VBIOS and PCIe link
    - the memory
    - the drives, with the free space in your home folder
    - the displays, with each output, the monitor's name and its preferred mode
    - the resolution, refresh rate and scale of each screen in use
    - the sound cards
    - the network adapters and Bluetooth controllers, with their driver and link
    - the USB devices
    - the input devices, such as keyboards, mice and controllers, each with its bus, such as USB, Bluetooth or PS/2
    - the sensors, with the temperatures, fan speeds, power, voltages and currents at that moment
    - the OS, with its version, the Bazzite image, the kernel and the desktop

    The portal reads it all each time the window opens. What a system does not report is left out. **Copy** puts it
    all on the clipboard as text, for an issue or a forum post. It holds nothing personal. It has no host or user
    name, no serial numbers, and no MAC or IP addresses.

## Install

[Install](install.md) has the lines to paste into a terminal. They download the portal's release, check it and run
its `install.sh`, as your own user. Later versions install from the portal itself. Press Y when it says **UPDATE
AVAILABLE**, as **Portal updates** above describes.

What it installs:

| What | Where | Why there |
|---|---|---|
| The portal, its `apps.toml` and the `bc250_core` it was tested with | `~/.local/share/bc250-bazzite-suite/portal` | In your home folder, since the portal needs no root |
| What the portal remembers, such as the apps it installed and their releases, the wallpaper, the music track and a downloaded portal update | `~/.local/share/bc250-bazzite-suite/state` | Apart from the program, so an update of the portal keeps it. Each app's matching uninstaller stays at hand |
| BC-250 Board Test, bundled in the portal release | `/opt/bc250-board-test`, through its own installer, which asks for the sudo password | Its test engine runs as root and must be root-owned |
| BC-250 Quickfix, bundled in the portal release | `~/.local/share/bc250-quickfix/app`, through its own installer | An app of your own. A quickfix asks for your password when it changes the board |
| The suite's shared venv with PyQt6 and pygame-ce | `~/.local/share/bc250-bazzite-suite/venv` | One copy of the ~100 MB of Qt for all suite apps. The last app that uses it removes it (`venv-users/`) |
| What the apps found outside the suite, one file per app | `~/.local/share/bc250-bazzite-suite/upstream/` | For **Outside the suite** in the notice. The apps write it, and the portal reads it |
| Launcher, menu entry, Desktop icon | `~/.local/bin/bc250-bazzite-suite`, `~/.local/share/applications/`, the Desktop | The portal's icon is the one way in. The apps' own icons are optional, with **Icons on Desktop** |

To uninstall, run `~/.local/share/bc250-bazzite-suite/portal/install.sh --uninstall`. This removes the portal,
Board Test and Quickfix. It keeps the settings and the wallpaper. Add `--purge` to remove those too. First it asks
about each other suite app that is installed:

- `y` uninstalls it
- `s` skips it, so it stays installed
- `c` cancels the whole uninstall before anything is removed

The list has every app this portal lists. It also has the apps an earlier portal installed that this one no longer
lists, such as an app dropped from the suite. Each one is removed with its own uninstaller. Those apps keep their own
settings, also with `--purge`. Of what the portal remembers, only the records of the apps you kept stay, with the
release each one's uninstaller needs. The wallpaper and the music track stay beside them. To remove the whole suite
at once, use `--uninstall --all`. It first shows a warning that names every app it will remove. Then it asks one
question instead of one per app. With `--purge`, the apps' own settings, history and results go as well.

When nothing of the suite is installed, the uninstaller says so and removes nothing. It does not ask for a password.
Each app's own `install.sh --uninstall` does the same when the app is not installed.

### What stays after an uninstall

Uninstalling an app removes the app. Two things stay on purpose:

- **changes it made to the board**, which you undo in the app or with its script before you uninstall it
- **your settings and results**, which `--purge` removes

| App | Still active on the board after its uninstall | Undo it with |
|---|---|---|
| CU Unlock | A persisted CU unlock, with `bc250-cu-unlock.service` at every boot | **Uninstall** in CU Unlock, or `sudo /usr/local/sbin/bc250-cu-unlock.sh --uninstall`. Stock CUs come back after the next restart |
| Core Unlock | A persisted core unlock, with its boot service | **Uninstall** in Core Unlock, or `sudo /usr/local/sbin/bc250-cores-unlock.sh --uninstall`. Stock cores come back after the next full power off |
| GPU Manager | The step its GPU sweep installed in the governor's `config.toml` | **Restore selected** on the app's **Backups** page. Or copy the `config.toml.bak-<stamp>` that Install made back over `config.toml`, then restart the governor |
| Persistent ACPI | The ACPI override, with `/boot/acpi_override.cpio` and its GRUB line | **Uninstall** in the app, or `sudo ./bc250-acpi-override.sh --uninstall`. Then restart |
| ACE Queues | An installed patched driver | **Remove** in the app |
| Memory Manager | The VRAM split in CMOS | Set the split back in the app, or press **Undo**. Then restart |

The GPU Manager changes nothing of its own. The governor and its `config.toml` belong to the governor package, which
stays installed. HelixSR keeps the imported payload (`~/.local/share/bc250-upscaler`). It leaves the games it
deployed to as they are. So **Remove** each deployment in the app first.

Settings live in `~/.config/bc250-*`. Results and logs live in `~/.local/share/bc250-*`. Board Test also writes its
reports to `~/Desktop/bc250-board-test`. Each app's `install.sh --uninstall --purge` removes them. The portal's
`--purge` does so for the portal, Board Test and Quickfix.

## Development

Run the portal straight from the checkout. Apps then install from the local source, staged exactly as the release
workflow stages them. So you can try everything before anything is released. The portal needs PyQt6, and Bazzite's
own `python3` has no PyQt6. So use the development venv from [Set up and test](development/index.md#set-up-and-test):

```shell
cd portal                  # from the repository's root
PYTHONPATH=../core ../.venv-linux/bin/python -m bc250_portal    # --source release: the pinned GitHub releases
```

To install from the checkout, run `./install.sh` in the repository's root, or here in `portal/`. It copies the
portal into your home folder, as a release does. It bundles the repository's `core/`, and it installs `../apps/check`
and `../apps/quickfix`. The installed portal names the checkout and installs the other apps from it too. So keep the
checkout where it is.

## apps.toml and releases

The comment at the top of [`apps.toml`](https://github.com/RobertoTorino/bc250-bazzite/blob/main/portal/apps.toml)
describes its fields. CI checks these rules with
[`tools/check_manifest.py`](https://github.com/RobertoTorino/bc250-bazzite/blob/main/tools/check_manifest.py):

- **Pinned tags.** Every pinned tag must exist when the portal is released. On `main`, a tag may also be the next
  release. That means its version equals that app's `VERSION`.
- **Version bumps.** A change to `apps.toml` needs a `portal/VERSION` bump at least as large as the largest app bump
  it pins. An app patch release needs at least a portal patch release. An app minor release needs at least a portal
  minor release, and so on. An added, removed or withdrawn app needs at least a minor portal release.
- **Withdrawn releases.** `withdrawn = "<reason>"` in an app's entry withdraws its pinned release, as
  [Withdrawing a release](#withdrawing-a-release) describes. It is not for the required apps, Board Test and
  Quickfix, which are always installed.
- **Required apps.** `required = true` marks an app that the portal installs with itself and lists without
  Uninstall. These are Board Test, with the key `check`, and BC-250 Quickfix. Board Test is always the first tile. A
  portal release bundles the pinned release of each one.
- **Quickfixes.** An app made of small quickfixes lists them as `[[apps.<key>.quickfixes]]` tables. Each table has a
  key, name, summary and launch. A quickfix that changes the board also has `changes_board` with its `board_change`.
  The portal shows a tile per quickfix and none for the app. In the app's wiki chapter, the section of each quickfix
  that changes the board opens with its `board_change`. It stands in a "Changes the board" box, and
  `tools/check_manifest.py` compares the two.

Nexus Release Tool makes a release of the suite with one action, **Start new release**, on its release tab. It
writes the versions, the CHANGELOG entries and the new tags in `apps.toml`. It commits and pushes, and starts
[`release.yml`](https://github.com/RobertoTorino/bc250-bazzite/blob/main/.github/workflows/release.yml) on that
commit. The run waits for CI and builds every new app release side by side. It publishes each one and pins its
checksum in a commit *Pin ...* on `main`. Then it builds the portal from that commit as a draft. The **Device test**
installs the draft on a board, as [Testing a portal release before its
tag](#testing-a-portal-release-before-its-tag) below describes. When it works, you publish it from the tool. That
makes the portal tag and GitHub's **Latest** release. [The release](development/releases.md#the-release) has the
steps one by one. The same workflow still builds a tag pushed by hand, one release at a time. That is the way below.

To release one app by hand and pin it in the portal, follow these steps:

1. Bump `apps/<app>/VERSION` and the copies that `tools/check_versions.py` lists. Update its CHANGELOG.
2. Commit and push. Then tag with `tools/tag-release.sh bc250-<app>-v<x.y.z>`, which waits until CI passed on that
   commit. [`release.yml`](https://github.com/RobertoTorino/bc250-bazzite/blob/main/.github/workflows/release.yml)
   builds `<tag>.tar.gz` and `SHA256SUMS` with
   [`tools/build_release.py`](https://github.com/RobertoTorino/bc250-bazzite/blob/main/tools/build_release.py).
3. Run `python3 tools/pin_app.py <tag>`. It sets the tag and checksum in `apps.toml`.
4. Bump `portal/VERSION` as `tools/check_manifest.py` asks. List the app release in the portal CHANGELOG.
5. Test the pinned app releases together on a BC-250, as
   [Testing a portal release before its tag](#testing-a-portal-release-before-its-tag) describes. Then commit steps 3
   and 4, push, and tag with `tools/tag-release.sh bc250-portal-v<x.y.z>`. That release bundles the pinned Board Test
   and Quickfix releases (`bc250-check-v…`, `bc250-quickfix-v…`).
6. Once `release.yml` has published it, it is GitHub's **Latest** release. Users download the portal there, as
   [The releases on GitHub](development/releases.md#the-releases-on-github) describes.

### The release front end

**Nexus Release Tool** is the suite's release front end. It makes the whole release with **Start new release**, and
it runs the device test below. [Releases](development/releases.md) says how to start and use it.

### Testing a portal release before its tag

A portal release promises one set of app releases, each with its checksum. Once its tag is out, every installed
portal offers those releases as updates. So before the tag, check on a BC-250 that exactly those pinned releases
install and run.

In a release made with **Start new release**, the portal is a **draft** on GitHub. The workflow builds it with the
pins already in it. You check it with the tool's **Device test** on the release tab, or by hand:

```bash
tools/check-release.sh draft                 # the draft of portal/VERSION
tools/check-release.sh draft bc250-portal-v14.1.0
```

It downloads the draft's tarball and `SHA256SUMS` with `gh`. A draft needs you to sign in with `gh auth login`. Then
it checks the checksum, installs the portal and starts it, as a user's board will once it is published. Test it as a
user would. Then press **Publish** in the tool, or **Not OK**, which leaves it a draft. The portal tag exists only
once it is published.

For a release by hand, follow these steps before the portal tag:

1. Bump the portal (step 4) and commit. You do not need to push for this test.
2. Run `tools/check-release.sh local`. It installs the portal from the checkout, with `./install.sh` in the
   repository root. That is this portal version, with its new pins in `apps.toml`. Then it starts the portal with the
   pinned releases instead of the checkout:

    ```bash
    bc250-bazzite-suite --source release
    ```

    Apps then install as on a user's board. The portal downloads each pinned tarball from GitHub and refuses it
    unless its checksum matches the pin. Without `--source release`, a portal installed from a checkout installs the
    apps from the checkout.

3. The apps whose pin changed show a red dot and a red **Update** in their menu. Update them, then open each one and
   check that it starts and works. Afterward, the red dots and the update count in the header are gone.
4. When all is good, tag the portal (step 5). When something is wrong, fix the app and release a new patch version
   of it (steps 1 to 4). Nothing has reached users yet.

This does not test the portal tarball itself, which GitHub builds from the tag. The release workflow checks it with
`tools/check_manifest.py --require-tags`. It also checks the bundled Board Test and Quickfix against their pins. The
next section tests the tarball on the board.

### Testing a portal release after its tag

Once GitHub's release workflow has built the portal release, run:

```bash
tools/check-release.sh release              # the release of portal/VERSION
tools/check-release.sh release bc250-portal-v0.9.2
```

It downloads the release tarball and its `SHA256SUMS` from GitHub into `~/.cache/bc250-release-check/`. It checks
the checksum, installs the portal and starts it. The board then runs the official release, as a user's board does.
Check that the portal starts, that its version is the new one, and that the apps install. To go back to the
checkout, run `./install.sh` in the repository root. A portal from the checkout shows an orange banner at the top,
"Local build". The published release has none.

A test cleans up after itself. On a board without the suite, the test marks what it installs as a test's. It removes
that again when the portal closes. That covers the portal, Board Test and the apps installed during the test. A board
that had the suite installed keeps it, and the test replaces its portal. `--keep` keeps what a test installed.
Installing by hand afterward (`./install.sh`) makes it the board's own.

```bash
tools/check-release.sh status            # what of the suite is installed, and whether a test put it there
tools/check-release.sh restore           # put back the install a test went over, when the test did not
tools/check-release.sh remove            # remove every app, the portal, Board Test and Quickfix; settings stay
tools/check-release.sh remove --purge    # their settings, history and results too
```

`remove` runs each part's own uninstaller. Nexus Release Tool's **Remove suite** tab runs it in a terminal.

### Withdrawing a release

You withdraw a release that must not be used anymore with Nexus Release Tool.
[Withdrawing a release](development/releases.md#withdrawing-a-release) has the steps. On a BC-250, **Test
withdrawal** installs the portal from the checkout and starts it (`check-release.sh local`). The portal says that the
app is not available anymore and removes it. Then it shows **App not available** on its tile. Board Test and
Quickfix are always installed, so they cannot be withdrawn.

### Checking a release

[Checking a release](development/releases.md#checking-a-release) says how to build a release's tag yourself and
compare it with the published tarball.

---

### a new app gets into the portal

`tools/new_app.py` makes a new app and lists it everywhere the suite lists its apps. So a new app reaches the portal
the same way every time:

```bash
python3 tools/new_app.py <name> "<App Name>" --category <category>
```

It writes the app's folder with `VERSION` 0.1.0, its installer test and its wiki chapter. It adds the app's
`[apps.<name>]` entry to `portal/apps.toml`. It also adds the app to `icons/categories.toml` and the wiki's lists.
[Adding a new app](development/architecture.md#adding-a-new-app) has the steps, and what to fill in after it.

Nexus Release Tool then releases the app with the portal, as [Releases](development/releases.md#the-release)
describes. It works out each version from the CHANGELOG entries. GitHub then builds and publishes the app's release.
It pins the release in `apps.toml` with its checksum and makes the portal a draft. After your device test, it
publishes the portal. You never change a `VERSION` by hand.

Users then see the new tile. An installed app whose version differs from the pinned one gets the red update dot.
