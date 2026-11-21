<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Controller](../assets/controller/bc250-controller.webp){ .app-logo }

# BC-250 Controller

BC-250 Controller is for the **DualSense** and **DualSense Edge** controllers on **Bazzite**. It shows their battery,
their firmware and the Edge's profiles. It also updates the controllers' firmware. Officially, you can update that
firmware only on a PS5 and in an app for Windows. This app sends the same firmware, from the official update server,
over a USB cable. The app changes nothing on the board.

Linux's own `hid-playstation` driver drives the controller, so games and Steam see it as usual. The app talks to
the controller beside the driver, through its hidraw node (`/dev/hidraw<n>`).

## The window

The header shows the controller the window is looking at:

| Box | What it shows |
|---|---|
| **Controller** | Edge for the DualSense Edge, DualSense for the plain one |
| **Connection** | USB or Bluetooth |
| **Installed firmware** | The firmware the controller runs, as the update server numbers it, for example `0x0217`. The box is green when that is the latest official firmware. The box is orange when a newer one is out. Its tooltip has the build date. |
| **Latest firmware** | The latest official version for this controller. The box is orange when you can update the controller to it, on the USB cable. A click then starts the update. Otherwise, a click asks the update server again. Its tooltip says when the app last asked the server, and why an update cannot start. |
| **Reports** | How many input reports a second the controller sends now, for example `250 Hz`. Steady and high is a good connection. A low or jumpy number over Bluetooth points to interference or distance. |
| **Bluetooth off in** | For a controller on Bluetooth, the time left before it switches off unused. **Switch Bluetooth off when unused** sets that time. Any button, stick or trigger starts it over. The box shows **Cable** on the USB cable, **Never** when that setting is on **Never**, and "—" when the service is not running. |

At the right end of the header, the battery stands as a phone shows it, with the percentage inside it. Five modules
fill from the bottom up for the level. They are green, orange at 20 % or less, and red at 10 % or less. While the
controller charges, the modules above its level fill one after another, upward, in green. The controller reports its
level in steps of 10 %.

The state beside the title says whether an update is available.

With more than one controller connected, a tab for each appears under the header. Examples are **Player 1 · Edge ·
USB · 100 %** and **Player 2 · Edge · Bluetooth · 40 %**. A tab names four things:

- the player number its lights show
- the model
- the connection
- the battery

Click a tab to show that controller in the window, with its drawing, firmware, light bar and profiles. With one
controller there are no tabs.

Below the header, the window shows one of three pages:

- **Connect your controller** shows while no controller is connected. It is a drawing of the controller with a
  USB-C cable going into its port. The app finds the controller by itself once you plug it in or pair it.
- **The introduction** shows after the first controller connects. It has three short pages on what the app does,
  the firmware update and the Edge's profiles. On a plain DualSense, the third page is about the battery. **Skip**
  goes straight on. **Show the introduction**, at the bottom of the main page, brings it back.
- **The main page** has the **Controller** box with a drawing of your controller, the firmware box and the profiles.

## On the cable and over Bluetooth

Linux drives a controller over one connection at a time. A controller that you connect over Bluetooth and then plug
in stays on Bluetooth. The cable only charges it, and the firmware update cannot start. A PS5 switches to the cable
by itself. Linux does not. The window then says **On Bluetooth, not the cable**. It offers **Use the cable** in the
firmware box. That button disconnects the controller from Bluetooth with `bluetoothctl`, and needs no password. Then
unplug the cable and plug it in again, and Linux takes the cable. Switching the controller off before plugging it in
does the same. To switch it off, hold the PS button for 10 seconds.

## The controller box

The drawing is the app's own, not the official artwork. Its face buttons have the colors of the first PlayStation
pads. The color buttons for the light bar are under it. To its right are the light bar's color now and **Test
vibration**. The drawing follows your controller live:

- a button lights while you press it, also the Edge's Fn and back buttons
- the sticks move
- the triggers fill as far as you pull them

Hover over a part to see its name, for example Cross, L2 trigger, Left back button or Light bar.

The **i** at the top left opens the controller's spec sheet. It has three parts:

- What the controller reports now. That is its model, connection, firmware, hardware version and battery.
- The model's specifications, with the official source of each. For the DualSense Edge, the sources are its
  instruction manual and the PlayStation Blog. They give model CFI-ZCP1, released 26 January 2023 at $199.99, a
  1,050 mAh battery and about 325 g.
- The parts the drawing leaves out because the controller does not report them.

The parts left out are:

- the L2 and R2 stop sliders
- the RELEASE latch
- the reset button
- the headset jack
- the charging contacts
- the microphone
- the speaker

The plain DualSense has no specifications in the app yet. Only facts from an official source go in.

During a firmware update the drawing shows the cable plugged in, data flowing down it and the touchpad filling as
the firmware goes in.

- **Light bar** is set with the circles under the drawing. They are Blue, Red, Green, Purple, White and Off, and
  the color wheel for any color. The app sets the color at once, and again each time the controller connects while
  the app is open. The drawing shows it. The controller does not keep the color. It forgets it when it disconnects,
  and Steam or a game may set another. **Off** saves some battery.
- **Turn Bluetooth off** switches a controller on Bluetooth off by ending its connection. The PS button switches it
  on again. On the USB cable it stays on, because the cable powers it.
- **Switch Bluetooth off when unused** switches a controller on Bluetooth off the same way, as a PS5 does. It does
  so after 10, 30 or 60 minutes without a button pressed, a stick moved or a trigger pulled. **Never** leaves it on.
  10 minutes is the default. Linux does not do this by itself, and a controller left on drains its battery in a few
  hours. A small service that the installer adds does it, also while the window is closed. It ignores the motion
  sensors, so a controller lying on a table counts as unused. It leaves controllers on the USB cable alone. While a
  game started from Steam runs, every controller stays on, whether you use it or not. A game does not always pick a
  controller up again that went away and came back. So the wait starts over when the game ends. The journal says
  when the service saw a game start and end.

    With more than one controller connected, each has its own wait. One in use stays on while an unused one goes
    off. A desktop notification says which one, by the player number its lights showed. An example is **DualSense
    Edge (player 2) switched off: Not used for 10 minutes. Press the PS button to switch it on again.** If switching
    it off fails, the notification says so and why. Hold the PS button for 10 seconds then. The journal keeps the
    same lines. Read them with `journalctl --user -u bc250-controller-idle`.
- **Player indicator** is the short row of small white lights just under the touchpad. Linux lights it when the
  controller connects. It shows the player number, in the order the controllers connected:

    - one light in the middle for player 1
    - two for player 2
    - three for 3
    - four for 4
    - all five for 5

    All dark means the controller is off. The drawing shows the same lights, and hovering over them names the
    player. With two controllers connected, that is the number on the chosen tab. The app does not change the lights,
    because only root may.
- **Test vibration** runs the left motor, then the right one, almost a second each. The drawing shakes on that
  side. You should feel each motor on its own side. A motor that stays still while the drawing shakes is worth a
  closer look.

## The firmware update

**Check for an update** asks the official update server (`fwupdater.dl.playstation.net`) for the latest version of each
controller. **Check when the window opens** is on by default. With it on, the window asks by itself, at most once a
day.

When a newer version is out, **Latest firmware** in the header turns orange. A click on it does four things:

1. It downloads the firmware from the update server, about 1 MB, and keeps it. A second try then needs no network.
2. It checks that the firmware fits. The firmware names the controller it is for, by its USB product ID and its
   *target*. Its version must be newer than the one the controller runs.
3. It saves a backup of the Edge's profiles, as [Profiles](#profiles) describes.
4. It sends the firmware to the controller, with a progress bar.

It takes about half a minute. The controller then checks the firmware's signature, switches to it and restarts. It
leaves USB for a moment and comes back. The header then shows the new version. The profiles stay as they were. The
Bluetooth pairing does not. To use the controller without the cable again, first remove it from the system's
Bluetooth settings. Then pair it anew. To pair it, hold Create and PS until the light bar blinks quickly. Without
that it blinks for a while and switches off.

Before it starts:

- **Connect the controller with a USB cable.** The update does not go over Bluetooth.
- **Quit Steam** (Steam › Exit), and any other program that reads the controller. The app names the program that has
  the controller open. It does not start the update while one does. That way, nothing else talks to the controller
  during the update. In Game Mode, switch to the desktop first.
- Leave the cable in and the board on until the window says the update is done.

If the controller refuses the firmware or stops answering, the window says what it reported. Unplug the controller
and plug it in again. The header then shows which firmware it runs, and you can try the update again.

### The firmware files

The update server has one file per *target* and only the latest version of it. The DualSense's target depends on its
revision. The DualSense Edge's is `0044`. The app knows the files that were on the update server on 23-10-2026 by
their SHA-256:

| Target | Controller | Version | SHA-256 |
|---|---|---|---|
| `0044` | DualSense Edge | `0x0217` | `c157eec635f809232e06c255a0847e6b915b0032ca661b12ae35fb2e4eac49df` |
| `0004` | DualSense | `0x0630` | `861ad95a99b16805ff20f5690372988662c4f69c6ad0b266e793d7fc2292315a` |
| `000B` | DualSense | `0x0630` | `b66528795683d214ca06fe4672d298de75bf019bd5046442cbec63fc02974f86` |
| `000E` | DualSense | `0x0641` | `b9c217d8ded5f09f03034e7e5037af0c174c3c77a3cbd201ee5fd219ee448fc8` |

A newer file from the update server works too. The confirmation then says the app does not know it yet. The
controller checks its signature either way. The app keeps the files in `~/.local/share/bc250-controller/firmware/`,
named after their target and version, for example `FWUPDATE0044-0217.bin`. The **Firmware** box names the kept file
of the latest version with its SHA-256 check. A green ✓ marks a file the app knows. An orange ! marks a file it does
not know.

**Use a file…** sends a firmware file you have, for example one kept from the update server before. The app checks it
the same way and refuses a file for another controller or one that is not newer.

## Profiles

The DualSense Edge keeps four profiles. Fn and Triangle, Square, Cross or Circle chooses one. Triangle is the default
profile. The **Profiles** box shows them side by side, a column each, as the controller reports them. Each column
has:

- the name
- each stick's curve, which is Default, Quick, Precise, Steady, Digital or Dynamic
- each trigger's range
- the buttons that send something other than themselves, the back buttons included

The box marks a profile whose checksum does not match. The card of the profile the controller uses now says
**Active**, and follows when you switch with Fn. Click a profile to see on the drawing what it sets. The drawing
then lights the Fn buttons, and the sticks, triggers and buttons the profile changes from their defaults. Click it
again to let go.

**Back up…** saves them in a JSON file, exactly as the controller holds them. **Read again** reads them anew, for
example after you changed them on a PS5. The app also saves a backup before every firmware update and before every
change to a profile, in `~/.local/share/bc250-controller/profiles/`.

### Create, edit and clear

Under each card, with the controller on the USB cable:

- **Create…** on an empty slot makes a profile there, starting from the default profile's settings.
- **Edit…** changes a profile.
- **Clear** removes it from the controller, after asking.

The default profile (Fn + Triangle) has none of these, because the app never changes it. Over Bluetooth, and during
a firmware update, the buttons are grayed out.

The editor sets:

- **Name**: up to 39 characters.
- **Sticks**: each stick's curve and its sensitivity, 0 to 10. The curve is Default, Quick, Precise, Steady, Digital
  or Dynamic. A profile made on a PS5 shows "as it is" next to the slider. Its curve stays exactly as it was until
  you change the curve or the slider.
- **Triggers**: where on its travel L2 and R2 start and stop counting, in percent. The controller keeps the range in
  the profile, but on Linux it still reports the trigger's whole travel. A try on a DualSense Edge showed this. R2
  set to 0 to 50 % filled like L2. A PS5 may use the range.
- **Buttons**: what each button sends, the back buttons included. A button sends its own, another button, Options or
  the touchpad's click.

**Save to the controller** saves a backup of all four profiles and writes the profile. It then reads the profile back
to check that the controller kept it. If it did not, the window says so and names the backup. The parts of a profile
the app does not show stay as the controller holds them.

The controller applies a profile itself, also on Linux. After Fn + Square, a button you set to send another sends
that one. The drawing shows what the controller sends, so Cross set to Circle lights Circle. The sticks follow their
curves too. On Digital a stick jumps to the edge. The triggers' range is the exception, as above.

The plain DualSense has no profiles.

## From a terminal

```bash
bc250-controller --info
```

prints each controller's connection, battery, firmware and profiles, without a window and without the network.
`bc250-controller --idle-watch` is what the service runs. `journalctl --user -u bc250-controller-idle` shows
when it switched a controller off.

## Access to the controller

Bazzite gives the user at the board the controller's hidraw node, so the app needs no password and no udev rule. On
a system that does not, the window says so. There, a udev rule with `TAG+="uaccess"` for the controller's USB ID
gives the user at the board access. The ID is `054c:0ce6` for the DualSense and `054c:0df2` for the DualSense Edge.

## Install

Install it from the BC250 Bazzite Suite portal, or from a clone or release folder, as your own user:

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
./install.sh --uninstall             # remove the app; keeps its settings, firmware and profile backups
./install.sh --uninstall --purge     # also remove its settings, firmware and profile backups
```

It installs:

- the app in `~/.local/share/bc250-controller/app`, with the `bc250_core` it was tested with
- PyQt6 in the suite's shared venv `~/.local/share/bc250-bazzite-suite/venv`
- the launcher `~/.local/bin/bc250-controller`, an app menu entry and a Desktop icon
- the user service `bc250-controller-idle`, which switches unused controllers off, as the controller box describes

The app keeps its settings in `~/.config/bc250-controller/bc250-controller.ini`.

## Credits

The update protocol comes from [dualsense-updater-rs](https://github.com/nchie/dualsense-updater-rs) by nchie. The
layout and writing of the Edge's profiles come from
[dualsense-edge-profile-web-application](https://github.com/steffalon/dualsense-edge-profile-web-application) by
steffalon. The app reads the firmware report as Linux's `hid-playstation` driver reads it.

## License

GPL-3.0-or-later — see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/controller/LICENSE).
The code ported from the two projects above is MIT. The app's README keeps their notice. The controllers' firmware
is Sony's and is not part of the app.
