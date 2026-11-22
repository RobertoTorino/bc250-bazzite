<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Webcam](../assets/webcam/bc250-webcam.webp){ .app-logo }

# BC-250 Webcam

BC-250 Webcam makes the **PS5 HD Camera (CFI-ZEY1)** a webcam on **Bazzite**. After that, OBS, a browser, Discord
or any other app can use it like any USB camera. The app changes nothing on the board.

## How the camera works

The camera has no memory of its own. When you plug it in, it is only a bootloader. A bootloader is a small program
that waits for the real firmware. In this camera, it shows up as an OmniVision OV580:

```bash
lsusb | grep 05a9           # ... ID 05a9:0580 OmniVision Technologies, Inc. USB Boot
```

A PlayStation sends the firmware each time you plug in the camera, and this app does the same. Then the camera
leaves the bus. Within a few seconds it comes back as a USB video camera:

```bash
lsusb | grep 05a9           # ... ID 05a9:058c OmniVision Technologies, Inc. USB Camera-OV580
```

From there on, Linux's own `uvcvideo` driver drives it. So the camera needs **no kernel driver**. It shows up as
`/dev/video<n>`.

The camera needs a **USB 3 port** (5 Gbit/s). These ports are usually blue. The bootloader also starts on a USB 2
port, but the video does not fit through it. The header's **USB** box shows the port's speed. It flags a port that
is too slow. The BC-250's two USB 3 ports are on the same controller, so either one will do.

## USB bandwidth

The firmware asks for the largest video stream USB 3 has. That is about 3 Gbit/s, reserved in every mode. Some USB
controllers cannot give that, and the BC-250's is one of them. Then the camera sends no picture at all. The
kernel's log says "Not enough bandwidth". You read it with `journalctl -k`. **USB bandwidth** in the Firmware box
chooses what the camera asks for:

| Setting | What it asks for | What streams |
|---|---|---|
| **Reduced** (the default) | Two thirds, about 2 Gbit/s | Every one-camera mode at its full rate. Side by side, up to 2560 × 800 at 30 fps, and 3840 × 1080 at 8 fps. |
| **Full** | The firmware as it is | Every mode at every rate, on a controller that allows it |

The app changes only the copy of the firmware that it sends. It changes 2 bytes of the camera's USB description.
The file itself stays as it is. A change takes effect the next time the app sends the firmware. So unplug the camera
and plug it in again.

## Access to the camera

The bootloader belongs to root. The first time, the window shows **Access to the camera**. **Allow access…** asks
for your password. It adds a udev rule that gives the bootloader to the user at the board. The rule covers only the
bootloader's USB ID. The same rule starts the load service when you plug in the camera (see [Loading by
itself](#loading-by-itself)). The rule takes effect at once. You do not need to unplug the camera or log out.

The rule is `/etc/udev/rules.d/70-bc250-webcam.rules`:

```
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="05a9", ATTR{idProduct}=="0580", TAG+="uaccess", TAG+="systemd", ENV{SYSTEMD_USER_WANTS}+="bc250-webcam-load.service"
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="05a9", ATTR{idProduct}=="058c|058a", TEST=="power/control", ATTR{power/control}="on"
```

Once the camera has its firmware, it needs no rule for access. Bazzite already gives the user at the board its
video cameras. The second line keeps the camera powered while it is plugged in. Otherwise, Linux suspends it two
seconds after the last app lets go of it. A suspended camera forgets its picture settings. The picture is then dark
again the next time, although the settings still read Auto Mode.

When the app finds a rule from an earlier version, it offers **Allow access…** again to update it.
`install.sh --uninstall` removes the rule again (with sudo).

## The firmware

The firmware is Sony's, so the suite does not include it. The **Firmware** box offers two ways to get it:

- **Download…** gets the firmware of the camera that is plugged in, from a project that publishes it. The app
  downloads one fixed version of each file and checks its SHA-256. So it uses the file it was tested with, or
  nothing:

    | Camera | Firmware | From |
    |---|---|---|
    | PS5 HD Camera | 21.01-03.20.00.04 (67 KB) | [prosperodev/hdcamera](https://github.com/prosperodev/hdcamera) |
    | PS4 Camera | From PS4 system software 1.50 to 3.15 (65 KB). PS Move API tested this file on a CUH-ZEY2. | [psxdev/luke_firmwares](https://github.com/psxdev/luke_firmwares) |

- **Use a file…** takes a firmware file you have.

The app checks the SHA-256 of the file it has, and it names the files it knows. A known file turns the header's
**Firmware** box green and shows its version. The line under the file's name then says "SHA-256 checked: it is the
known file", with the hash. A file of your own turns the box orange. The SHA-1 is the hash that the projects that
publish the files quote.

| Firmware | SHA-256 | SHA-1 |
|---|---|---|
| PS5 HD Camera 21.01-03.20.00.04, the download | `10af1aee76fe0057a88db7ebf5f3ebf32430633effb93722be4cd0a9ed4fce54` | `0fa4da31a12b662a9a80abc8b84932770df8f7e1` |
| The same with the Discord and gamma fix | `42ce5f7033a1115988cada3ebb8e0a143e8b241661f203a12275354dd2ba0bf6` | `a5d8aadab91d78e33f4c038798c047066e6713d7` |
| PS4 Camera, from PS4 system software 1.00 to 1.05 | `8262c2a785128a04273bbcf360e29e30c10c9f3b1c3e2571a5eea5b929f41e16` | `7390be76a163c2d4a68d939577d46d7c20165881` |
| PS4 Camera, from PS4 system software 1.50 to 3.15, the download | `d550c4abc416385810ca181867f4dd650198e1214d371ba058005a10f420fd9b` | `fe86162309518a0ffe267075a2fcf728c5856b3e` |
| PS4 Camera, from PS4 system software 3.50 to 5.05 | `a6f99b283b707ece098602aea823415e614db3d64b21a22c53d45476e5405b24` | `c556911796202deef1cbb051390b5c3a2e6c0a7a` |
| PS4 Camera, from PS4 system software 6.00 to 7.02 | `09513d1068b9b5e23b09e03bca5640ed4d01830b034b9802395006b14a927b01` | `8b8a6621d358f6782c2e3b31aac2cdfb25102c00` |

Any other file of a sensible size is your choice, and the app calls it an own file. The app refuses a file that it
knows to be the other camera's firmware. It keeps the files in `~/.local/share/bc250-webcam/firmware/`:

- `cfi-zey1.bin` for the PS5 HD Camera
- `ps4-camera.bin` for the PS4 Camera

## Loading by itself

With **Load it by itself when the camera is plugged in** on, you do not need to open the app again. That works
once the camera has its firmware file and access. The option is on by default. The installer adds a service for
your user, `~/.config/systemd/user/bc250-webcam-load.service`. This load service sends the firmware:

- when you plug in the camera, started by the udev rule
- at login, for a camera that was plugged in before

It runs as your user, not as root. To see what it did:

```bash
journalctl --user -u bc250-webcam-load.service
```

With the option off, the service does nothing. Then the **Load firmware** pill in the window's header sends the
firmware. With the option on, the open window also sends the firmware itself when the service could not. For
example, the firmware file or the access came later. It does that once per plug-in.

Without the app, the same is a terminal command:

```bash
bc250-webcam --load      # sends the firmware to every camera that waits for it
```

### After a restart

When the board restarts, the camera may not come back at all. `lsusb` does not list it, and the load service finds
no camera. The USB port keeps its power through a restart. So the camera keeps running its firmware, but it does
not connect to the restarted system.

Unplug the camera and plug it in again. It starts as a bootloader, and the load service sends the firmware as
usual. Switching the port off and on from Linux does not bring it back on the BC-250. After a shutdown and power
on, the camera starts fresh. The load service then sends its firmware at login. When the app finds no camera, the
window and the load service's journal both say so.

## The picture

Once the camera is ready, the header shows its video node. The **Picture** box offers every mode the camera
reports, each frame size at each of its rates. The camera has two image sensors, and its modes are of two kinds:

| Kind | Frame sizes |
|---|---|
| One camera | 1920 × 1080, 1280 × 800, 960 × 520, 640 × 376, 448 × 256, 320 × 184 |
| Both cameras, side by side | 3840 × 1080, 2560 × 800, 1920 × 520, 1280 × 376, 896 × 256, 640 × 184 |
| Both cameras and smaller copies of them | 5148 × 1088 |

The list shows what your camera reports, with the largest one-camera mode first. Not every mode gives a picture.
With Reduced bandwidth, some fast side-by-side modes do not fit, and their frames arrive damaged. At 15 fps, the
1080-line modes send nothing at all. After a few seconds, the window says which of the two it is and stops the
preview. Measured on the BC-250 with Reduced bandwidth:

| Mode | Picture |
|---|---|
| Every one-camera mode, at every rate, but one | Yes |
| 1920 × 1080 at 15 fps | None, the camera sends nothing. At 30 and 8 fps it works. |
| 2560 × 800 at 30, 15 or 8 fps, 1920 × 520 at 60, 1280 × 376 at 120, 896 × 256 at 120, 640 × 184 at 240 | Yes |
| 3840 × 1080 and 5148 × 1088 at 8 fps | Yes |
| 3840 × 1080 and 5148 × 1088 at 15 fps | None, the camera sends nothing |
| 2560 × 800 at 60, 3840 × 1080 and 5148 × 1088 at 30 | Frames damaged, too much for the bandwidth |

For a side-by-side mode, **Show** picks the whole frame or either half. Each half is the lens on that side as you
face the camera. So the left half is the lens on your left. Seen from behind the camera, that is its right lens.

**Save picture…** saves what the preview shows as a PNG, at the camera's own size. The preview shows up to 30
frames a second, and fewer in the largest modes. Other apps get every frame the camera sends.

While the preview runs, the app holds the camera, and other apps cannot use it. **Stop preview** gives it back.
Closing the window does too.

### Full screen

**Full screen** shows the picture over the whole screen. It starts the preview when it was not running. The row at
the bottom holds its buttons. The line above the row shows the mode and the zoom. While it records, the line also
shows the recording's time.

| Button | What it does |
|---|---|
| **Screenshot** (S) | Saves what the screen shows as a PNG in your **Pictures** folder |
| **Record**, **Stop** (R) | Starts a recording of what the screen shows, and stops it. The recording goes to your **Videos** folder. |
| **Gray**, **Color** (G) | Black and white, or color again. The app remembers your choice. |
| **Zoom −**, **Zoom +** (−, +, mouse wheel) | Zooms out or in: 1x, 1.5x, 2x, 3x and 4x |
| the arrow keys, or a drag with the mouse | Move the zoomed picture |
| **Mode −**, **Mode +** (PageUp, PageDown) | The mode before or the next one. The picture starts again in that mode. |
| **Close** (Esc) | Back to the window. A recording stops, and the app keeps it. |

Screenshots and recordings show what you see, also zoomed in and in black and white. Each goes in a **BC-250
Webcam** folder. Its name holds the date and the time (`BC-250 Webcam 2026-11-01 21-04-09.png`). After a
screenshot, the file manager opens on that folder with the new file selected.

A recording is an MP4 at the mode's size, or the size of the half that **Show** picks. It has at most 30 frames a
second. The app writes it with the video encoder that Qt brings. That is MPEG-4, or H.264 where the system has one.

The mode does not change while the app records. Stop the recording first. If the camera stops sending, the screen
says so and stays open. Then choose another mode with **Mode −** or **Mode +**. When you close the app while it
records, it stops the recording and writes its file first.

## Picture settings

Beside the preview, **Picture settings** shows the camera's own settings, as the camera reports them. On the PS5 HD
Camera, these are:

- brightness, contrast, saturation, gain and sharpness, from 0 to 8
- hue, from 0 to 11
- automatic white balance, or a color temperature
- the power line frequency, 50 or 60 Hz, against flicker under lamps
- the exposure, Auto or the camera's default Shutter Priority

A setting that another one decides is grayed. For example, the color temperature is grayed while the white balance
is automatic. **Defaults** puts every setting back.

The app sets **Auto Exposure** to **Auto Mode**, unless you choose otherwise. In its own default mode, Shutter
Priority, the camera keeps a short exposure. Then the picture stays dark, even in a well-lit room. **Defaults**
keeps Auto Mode too. These figures were measured at 1280 × 800. Brightness is the average brightness of a frame,
from 0 to 255:

| Setting | Brightness | Near black | White clipped |
|---|---|---|---|
| The camera's default (Shutter Priority) | 48 | 24 % | 0 % |
| Auto Mode | 111 | 0 % | 4 % |
| Auto Mode, gain 8 | 136 | 0 % | 6 % |
| Auto Mode, brightness 8 | 166 | 0 % | 9 % |
| Shutter Priority, brightness 8 | 112 | 0 % | 1 % |

Gain changes the picture only in Auto Mode. The camera reports an exposure time, but you cannot use it. The app
shows it grayed, for completeness. The camera has no manual exposure:

- In both of its modes, it marks the exposure time as set by its automatic exposure.
- So Linux's driver refuses a value for it.
- A value sent to the camera directly goes back to 1000 when the picture starts.

The camera also has one vendor control of its own. It is an extension unit of 3 bytes, and nothing documents it.
The app leaves it alone.

The camera forgets its settings when you unplug it. The app keeps the ones you changed. It sets them again each
time the camera is ready, also when the load service loaded it. So other apps get the same picture. The settings
also work while another app shows the camera. So you can open the window to adjust the picture of a call or a
stream.

## Using it in other apps

Any app that uses a webcam finds the camera as **USB Camera-OV580**. In OBS, add a **Video Capture Device (V4L2)**
source and choose that device. A one-camera mode such as 1920 × 1080 gives an ordinary webcam picture. Many apps
pick the camera's first mode by themselves. Choose the resolution in the app if it offers one.

## PS4 Camera

The PS4 Camera (CUH-ZEY1 or CUH-ZEY2) also works, on Sony's PlayStation Camera Adapter (CFI-ZAA1). It starts as the
same bootloader. The app knows it by the adapter between them and shows **PS4 Camera**. The adapter does not say
which of the two models it is.

The PS4 Camera has its own firmware, which **Download…** gets for it. The same USB bandwidth setting applies. Once
loaded, it is USB ID `05a9:058a`. A PS4 Camera on a homemade adapter, without Sony's, looks like a PS5 HD Camera to
the app. That setup is not supported.

## Install

Install it from the BC250 Bazzite Suite portal, or from a clone or release folder, as your own user:

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
./install.sh --uninstall             # remove the app, its udev rule and its load service; keeps its settings and firmware
./install.sh --uninstall --purge     # also remove its settings and firmware
```

It installs:

- the app in `~/.local/share/bc250-webcam/app`, with the `bc250_core` it was tested with
- PyQt6 in the suite's shared venv `~/.local/share/bc250-bazzite-suite/venv`
- the launcher `~/.local/bin/bc250-webcam`, an app menu entry and a Desktop icon
- the load service `~/.config/systemd/user/bc250-webcam-load.service`, turned on for your login

The app keeps its settings in `~/.config/bc250-webcam/bc250-webcam.ini`.

## Credits

The PS4EYECam driver by Antonio Jose Ramos Marquez found the upload protocol. [PS Move
API](https://github.com/thp/psmoveapi) uses it, and this app follows its camera firmware loader. The firmware file
and the camera's USB description come from [prosperodev/hdcamera](https://github.com/prosperodev/hdcamera).

## License

GPL-3.0-or-later. See [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/webcam/LICENSE).
The camera's firmware is Sony's and is not part of the app.
