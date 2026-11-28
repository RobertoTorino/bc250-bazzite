<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Bluetooth Pairing](../assets/btpair/bc250-bluetooth-pairing.webp){ .app-logo }

# BC-250 Bluetooth Pairing

BC-250 Bluetooth Pairing lets you use the board with only a Bluetooth keyboard, mouse and controllers. You need no
USB ones, also on a new board and after a fresh install. The app installs a small system service, a background
program that runs before anyone logs in. After every boot the service looks for the devices you listed. It pairs the
ones in pairing mode, on the login screen.

## Using it

1. Click **Add…** and choose the devices to pair. Pick one Bluetooth knows, or type its name exactly as the device
   gives it. Bluetooth knows a device that you paired before. It also knows one that **Search nearby** found while
   the device was in pairing mode.
2. Turn on **Pair the listed devices after every boot**. It installs a small system service and asks for your
   password.
3. From then on, put the keyboard and the mouse in pairing mode after a boot. To do that, hold the connect button
   until the light blinks fast. They connect within a few seconds, on the login screen.

The list shows each device with what Bluetooth knows of it:

- connected
- paired
- known
- not seen yet

**Remove** takes a name off the list. The device itself stays paired. Once the service is installed, a changed list
waits for **Save**, which asks for your password once.

The header shows four boxes:

- **Bluetooth** shows whether Bluetooth is on.
- **After boot** shows whether the service pairs after boot.
- **Batteries** shows whether the controller batteries go to the Bluetooth icon.
- **At login** shows what Plasma does with Bluetooth at login.

The small round **i** beside the state says in short what the app does.

## Pair after boot

For 5 minutes after every boot, the service searches for the listed devices. It stops as soon as every one is
connected.

- The service trusts, pairs and connects a listed device in pairing mode.
- A listed device that you paired before reconnects.
- A device can refuse its old pairing, because you paired it with another computer or reset it. After two refusals
  the service removes the device and pairs it again.
- The service never pairs devices with other names.
- Every DualSense calls itself the same. So the service pairs any DualSense nearby in pairing mode while none is
  connected. Once one is connected, the service leaves another alone.

**Search now** searches again without a restart, for another 5 minutes. Put the device in pairing mode first. It asks
for your password. **The search after this boot** at the bottom shows what the search did, with the time of each
line.

Someone nearby can copy a name with deliberate effort. So the search takes only the listed names. It runs only in the
first minutes after a boot.

## Controller batteries

A DualSense or DualSense Edge reports its battery through its own driver, not through Bluetooth. So the Bluetooth
icon shows no battery for it. For a keyboard or a mouse the icon does show one. **Show controller batteries in the
Bluetooth icon** installs a second small service. That service hands each controller's battery to Bluetooth every 30
seconds. It uses Bazzite's own D-Bus and GLib for Python (`python3-dbus`, `python3-gobject`).
[Nexus Dependencies](../development/dashboard.md#deps) checks them.

## Bluetooth at login

Plasma switches Bluetooth on or off when you log in. By default, it restores the state it saved when the last session
ended. A restart from a terminal, or one that an update starts, stops Bluetooth before the desktop session ends.
Plasma then saves it as off. The keyboard and the mouse then work on the login screen. They stop as soon as the
desktop appears, with nothing to say why.

**Switch Bluetooth on at every login** sets Plasma's own setting, so Bluetooth is on at every login whatever Plasma
saved. You find that setting in System Settings, Bluetooth, under **When logging in**, as Enable Bluetooth. It is your
own setting and asks for no password. When you turn it off, Plasma restores the saved state again. On a desktop other
than Plasma it does not apply.

## A USB 3 device beside the receiver

A device in a USB 3 port can heavily interfere with a Bluetooth receiver in a USB port beside it. That holds for
USB 3.0 to 3.2, and for devices such as these:

- a drive
- a hub
- a camera
- a Wi-Fi stick

USB 3 gives off noise in the same 2.4 GHz band that Bluetooth uses. Devices then pair late or not at all, or lose
their connection. A mouse or controller can lag. A USB extension cable helps. Put the receiver or the USB 3 device on
it, and keep the two as far apart as you can.

## Install

Install it from the portal (the **Utilities** tab), or from a checkout of the repository:

```bash
apps/btpair/install.sh                         # the app, its launcher, a menu entry and a Desktop icon
apps/btpair/install.sh --no-desktop-shortcut   # without the Desktop icon
apps/btpair/install.sh --uninstall             # remove it; --purge removes its settings too
```

The launcher is `~/.local/bin/bc250-bluetooth-pairing`. The app runs on the suite's shared Python environment.
You need a keyboard and a mouse once, to install the app and list the devices.

## Files

- `~/.config/bc250-bluetooth-pairing/bc250-bluetooth-pairing.ini` holds the list while the service is not installed.
- The search after boot and the controller batteries have these files, only while one of them is on:
    - `/etc/bc250-bluetooth-pairing/` (`boot.py`, `boot.json`)
    - `/etc/systemd/system/bc250-bluetooth-pairing.service`
    - `/etc/systemd/system/bc250-bluetooth-pairing-battery.service`
- `boot.json` holds the names and the two choices.
- Removing the app removes the files in `/etc`. It asks for the sudo password then.
- `journalctl -b -u bc250-bluetooth-pairing` shows what the search did.
- `~/.config/bluedevilglobalrc` holds Plasma's Bluetooth at login, as `launchState` under `[General]`. Removing the
  app leaves it as it is, because it is Plasma's own setting.

## License

GPL-3.0-or-later.
