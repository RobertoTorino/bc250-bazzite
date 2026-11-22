<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Turing Screen](../assets/turing/bc250-turing-screen.webp){ .app-logo }

# BC-250 Turing Screen

BC-250 Turing Screen shows the live system values of the **AMD BC-250** on a small **Turzx USB IPS screen** on
**Bazzite**. It shows the CPU, GPU, memory, fan, temperatures, network and disk, and the weather if you want it. It
reads the same sensors as [BC-250 System Overlay](overlay.md), without root. It changes nothing on the board.

## Screens

The app works with the Turzx screens that report USB ID `1a86:5722`:

| Screen | Size | How the app knows it |
|---|---|---|
| Turing Smart Screen 3.5" | 320 × 480 | it does not answer the app's hello |
| UsbMonitor 3.5" | 320 × 480 | answers 1 |
| UsbMonitor 5" | 480 × 800 | answers 2 |
| UsbMonitor 7" | 600 × 1024 | answers 3 |

The header shows which one it found. To check which screen you plugged in:

```bash
lsusb | grep 1a86:5722          # ... QinHeng Electronics UsbMonitor
```

These screens need **no driver** on Linux. They are USB serial devices. As soon as you plug one in, the kernel's
`cdc_acm` driver makes it `/dev/ttyACM0`, or the next free number. The "driver" in the Windows download is only
Microsoft's USB serial setup file.

## Access to the screen

The port belongs to root and the `dialout` group. Bazzite's users are not in that group. The first time, the window
shows **Access to the screen**. **Allow access…** adds a udev rule that gives the user at the board the screen's
port. A udev rule tells Linux who may use a device. This rule covers this USB ID only. You will be asked for your
password. The rule takes effect at once. You don't need to unplug the screen or log out.

The rule is `/etc/udev/rules.d/70-bc250-turing-screen.rules`:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="5722", TAG+="uaccess"
```

`install.sh --uninstall` removes it again (with sudo).

## What it shows

Each value is a tile. Check the ones you want on the **Values** tab. The tiles fill the screen in one column when it
stands up, and in two columns when it lies down. The header shows your own text from the **Look** tab and the time.
It can add the time zone and the date, on the **Clock** tab. Hover a value on the **Values** tab to see what it
shows.

| Tile | What it shows |
|---|---|
| CPU | the load with a bar, and the clock and temperature |
| GPU | the load with a bar, and the clock and temperature. With Quickfix's **VRM Sensors** on, it also shows the GPU's own power. Without the GPU governor's fix-metrics, the BC-250 reports no GPU load. The tile then shows the clock instead |
| CPU temp | the CPU's temperature in large, with a bar from 0 to 100 °C |
| GPU temp | the GPU's temperature in large, with a bar from 0 to 100 °C |
| VRAM | used / total of the GPU's share of the memory, with a bar |
| RAM | used / total, with a bar |
| Fan | the fastest spinning fan and its name |
| VRM temp | the temperature of the VRM, the voltage regulator module. These regulators beside the chip feed it its power |
| CPU power | what the CPU's supply delivers, with its voltage and current. It needs Quickfix's **VRM Sensors** |
| GPU power | what the GPU's supply delivers, with its voltage and current. It needs Quickfix's **VRM Sensors** |
| Chip power | what the whole chip draws, as the GPU driver reports it. That is the CPU, the GPU and the rest together |
| 12 V input | the board's 12 V input, as the voltage regulator measures it. It needs Quickfix's **VRM Sensors** |
| NVMe temp | the SSD's temperature |
| Network | download, with upload beside it. It measures all network interfaces, or the one chosen on the **Values** tab |
| Disk | read, with write beside it |
| Weather | the temperature, the sky in words and an icon for it, at the place chosen on the **Weather** tab. At night the icon is a moon |

A temperature turns the tile orange from 80 °C and red from 90 °C. A tile shows "—" when the board does not offer
its value. The values update every second.

The link to the screen is slow. A whole 3.5" picture takes almost two seconds. So the app sends only the parts that
changed, usually a few KB a second. Hover **Connected** in the header to see how much the last update sent.

## Settings

The window shows the screen's picture at its own size. The pictures of the 5" and 7" screens are scaled down to fit.
The settings are on six tabs beside the picture, or under it when the screen lies down. Every change shows on the
screen at once.

Under the picture:

- **Save picture…** saves what the screen shows, at the screen's own size, as a PNG.
- **Save report…** saves every value at that moment as a text file. It also holds the values that are not on the
  screen, with the date, the time and its time zone.

**Screen**

- **Brightness:** 0 to 100 %. The **Screen off** pill in the header switches the screen dark while the app keeps
  running. The pill then reads **Screen on** until you click it again.
- **Orientation:** portrait or landscape, each either way up. Choose the one that matches how the screen stands. The
  side with its USB cable tells you.

**Values**

- The tiles to show.
- **Network tile:** the network interface the Network tile measures. Each one shows its kind: Ethernet (a cable),
  Wi-Fi or Virtual. A virtual interface is a bridge, VPN or container network. The default is **All interfaces**. That
  choice adds them up.

**Look**

- **Theme:** Dark, Light, Midnight, Ember, Forest or Mono. Dark takes the suite's accent color. Moving through the
  list shows each theme in the window's picture. The screen changes only when you choose one.
- **Colors:** your own color for the **Text**, the **Tiles**, the **Accent** or the **Background**, over the theme.
  The accent is the tiles' edge and bars. The window's picture shows each color you try in the color dialog. The
  screen changes when you choose OK. A button with your own color shows it. **Theme's** puts back the theme's colors.
  The warm and hot temperatures stay orange and red.
- **Header text:** your own text, up to 24 characters. Write the board's name, its CPU or anything else. Empty leaves
  only the time.
- **Background:** a picture of your own behind the tiles, cut to the screen's shape. The tiles let it show through a
  little. The app remembers where the picture is and does not copy it. If you move or remove it, the theme's color
  comes back, and the tab says so.

**Clock**

- **Time:** 24-hour, or 12-hour with AM or PM.
- **Time zone:** not shown, its name (CEST) or its offset from UTC (UTC+2). The choices show the zone the system is
  in now.
- **Date:** not shown, or under the time as Thu 22 Oct, 22-10-2026, 10/22/2026 or 2026-10-22.

The time is the system's, in its time zone. Summer and winter time follow by themselves. In Amsterdam, the header
says CEST (UTC+2) in summer and CET (UTC+1) in winter.

**Weather**

- Type a city or town and click **Search**. Pick the right place from the list. The region and country tell places
  with the same name apart. Then click **Use this place**. The app turns on the Weather tile with it. **No weather**
  forgets the place.
- The tab shows the current weather in more detail. It gives the temperature, sky, wind and humidity.
- The weather comes from [Open-Meteo](https://open-meteo.com/), free and without an account or key. **Search** sends
  the name you typed. After that, the app sends the place's coordinates to Open-Meteo every 30 minutes. It does so
  only while the Weather tile is on the screen. Without a place, the app sends nothing.
- Open-Meteo may be out of reach, or busy. Busy means that it answers 429, 502, 503 or 504. The tab then says so, with
  Open-Meteo's own reason. It also says that the app asks again in 30 minutes. Until then, the screen keeps the last
  weather it had. Without any weather yet, it says *unavailable*.
- The tile cuts a long place name short, so it never runs into the weather beside it. See [Privacy](../privacy.md).

**Start**

- **Start with the desktop, minimized:** the screen shows the values from the moment you log in. The window may stay
  minimized. The app keeps updating the screen.
- **Switch the screen off when the app quits:** on by default. Then the screen does not keep showing values that no
  longer change.

Each time the app connects to the screen, it restarts the screen once. The screen is then gone from USB for about two
seconds. The restart also clears a picture that was cut off halfway. An app that was killed or a cable that was
pulled can leave such a picture. Without the restart, everything after it would land shifted. If you unplug the
screen, the app finds it again when you plug it back in.

## Install

Install it from the BC250 Bazzite Suite portal, or from a clone or release folder, as your own user:

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
./install.sh --uninstall             # remove the app, its udev rule and its autostart entry; keeps its settings
./install.sh --uninstall --purge     # also remove its settings
```

It installs:

- the app in `~/.local/share/bc250-turing-screen/app`, with the `bc250_core` it was tested with
- PyQt6 in the suite's shared Python environment, `~/.local/share/bc250-bazzite-suite/venv`
- the launcher `~/.local/bin/bc250-turing-screen`, an app menu entry and a Desktop icon

`bc250-turing-screen --minimized` starts it minimized, as **Start with the desktop, minimized** does. The app keeps
its settings in `~/.config/bc250-turing-screen/bc250-turing-screen.ini`.

## License

GPL-3.0-or-later — see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/turing/LICENSE).
