<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-shape-outline:</span>

# App categories

An app's icon tells you what kind of app it is. Every app in the suite belongs to one of four categories. Every app
in a category has the same icon. The four categories are for these kinds of app:

- An app that keeps the board running well
- An app for graphics in games
- An app for playing
- A utility

## Why categories

- **You see at a glance what an app is for.** In the portal, the menu, on the Desktop and in Steam, the icon shows
  its kind before you read the name.
- **The suite looks like one suite.** Thirty-odd apps with thirty-odd styles would look like a pile of separate
  tools. Four icons look like one family.
- **One place to change them.** The suite keeps each category's icon once, in `icons/<category>/`. A new app picks a
  category and gets its icon. A new icon for a category reaches every app in it. How that works is in
  [Architecture and consistency](../development/architecture.md#icons).

The categories are also the [portal's](../portal.md) categories. In the portal, an app's tile is under its category's
name.

## Legend

| Icon | Category | What it stands for |
|---|---|---|
| ![](../assets/categories/sustainable.webp){ .app-icon } | **Sustainable** | The board itself: test it, tune it, unlock it, cool it, and keep it running well for a long time. Most of these apps change how the board runs. |
| ![](../assets/categories/graphics.webp){ .app-icon } | **Graphics** | Upscaling, async compute and mesh shaders for games on the board's GPU. |
| ![](../assets/categories/gaming.webp){ .app-icon } | **Gaming** | Apps for playing games. They include the emulators, Remote Play with your console and PlayStation trivia. |
| ![](../assets/categories/utilities.webp){ .app-icon } | **Utilities** | Handy tools around the board. They include an overlay, a USB stats screen and the PS5 HD Camera as a webcam. Others cover the DualSense's firmware, the BIOS settings, the TV over HDMI-CEC and file transfer. They also include an SSD check, Bluetooth pairing at boot, small quickfixes and a password generator. |

## Apps by category

Every app with its icon and its category.

| App | Category |
|---|---|
| ![](../assets/apps/check.webp){ .app-icon } [BC-250 Board Test](check.md) | Sustainable |
| ![](../assets/apps/gpu.webp){ .app-icon } [BC-250 GPU Manager](gpu.md) | Sustainable |
| ![](../assets/apps/compute.webp){ .app-icon } [BC-250 CU Tools](compute.md) | Sustainable |
| ![](../assets/apps/cores.webp){ .app-icon } [BC-250 CPU Tools](cores.md) | Sustainable |
| ![](../assets/apps/oc.webp){ .app-icon } [BC-250 GPU OC Bisect](oc.md) | Sustainable |
| ![](../assets/apps/acpi.webp){ .app-icon } [BC-250 Persistent ACPI](acpi.md) | Sustainable |
| ![](../assets/apps/vram.webp){ .app-icon } [BC-250 Memory Manager](vram.md) | Sustainable |
| ![](../assets/apps/fan.webp){ .app-icon } [BC-250 Fan Control](fan.md) | Sustainable |
| ![](../assets/apps/upscaler.webp){ .app-icon } [BC-250 Upscaler Manager](upscaler.md) | Graphics |
| ![](../assets/apps/ace.webp){ .app-icon } [BC-250 ACE Queues](ace.md) | Graphics |
| ![](../assets/apps/mesh.webp){ .app-icon } [BC-250 Mesh Shaders](mesh.md) | Graphics |
| ![](../assets/apps/consoles.webp){ .app-icon } [BC-250 PS Remote Play](consoles.md) | Gaming |
| ![](../assets/apps/clb.webp){ .app-icon } [BC-250 XB Remote Play](clb.md) | Gaming |
| ![](../assets/apps/shadps4.webp){ .app-icon } [shadPS4 Manager](shadps4.md) | Gaming |
| ![](../assets/apps/rpcs3.webp){ .app-icon } [RPCS3 Manager](rpcs3.md) | Gaming |
| ![](../assets/apps/ppsspp.webp){ .app-icon } [PPSSPP Manager](ppsspp.md) | Gaming |
| ![](../assets/apps/pcsx2.webp){ .app-icon } [PCSX2 Manager](pcsx2.md) | Gaming |
| ![](../assets/apps/vita3k.webp){ .app-icon } [Vita3K Manager](vita3k.md) | Gaming |
| ![](../assets/apps/xenia.webp){ .app-icon } [Xenia Manager](xenia.md) | Gaming |
| ![](../assets/apps/datstation.webp){ .app-icon } [Bazzite DatStation](datstation.md) | Gaming |
| ![](../assets/apps/overlay.webp){ .app-icon } [BC-250 System Overlay](overlay.md) | Utilities |
| ![](../assets/apps/turing.webp){ .app-icon } [BC-250 Turing Screen](turing.md) | Utilities |
| ![](../assets/apps/webcam.webp){ .app-icon } [BC-250 Webcam](webcam.md) | Utilities |
| ![](../assets/apps/controller.webp){ .app-icon } [BC-250 Controller](controller.md) | Utilities |
| ![](../assets/apps/bios.webp){ .app-icon } [BC-250 BIOS Reader](bios.md) | Utilities |
| ![](../assets/apps/cec.webp){ .app-icon } [BC-250 CEC Manager](cec.md) | Utilities |
| ![](../assets/apps/sftp.webp){ .app-icon } [BC-250 SFTP Tools](sftp.md) | Utilities |
| ![](../assets/apps/ssd.webp){ .app-icon } [BC-250 SSD Check](ssd.md) | Utilities |
| ![](../assets/apps/btpair.webp){ .app-icon } [BC-250 Bluetooth Pairing](btpair.md) | Utilities |
| ![](../assets/apps/quickfix.webp){ .app-icon } [BC-250 Quickfix](quickfix.md) | Utilities |
| ![](../assets/apps/password.webp){ .app-icon } [BC-250 Password Generator](password.md) | Utilities |
