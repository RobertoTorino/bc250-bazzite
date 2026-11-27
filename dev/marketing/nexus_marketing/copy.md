<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- The words of the article that Nexus Marketing for BC-250 writes. Each "##" part below is read by its heading.
The tables have a line for each category and each app of portal/apps.toml, by its key. The app's tests fail when
one is missing or names something the portal does not have. {apps} becomes the number of apps in the portal.
Run tools/text_check.py --details on this file to check it. -->

# Nexus Marketing copy

## Headline

One portal. Every part of your AMD BC-250.

## Claim

Test it, tune it, unlock it and play on it. The BC250 Bazzite Suite brings {apps} apps running in Bazzite on
the AMD BC-250. One portal installs them opens them and keeps them up to date.

## Specs

<!-- The board's numbers in a row under the hero: the number, a space, then its label as the page shows it. A label
that ends in asterisks has its note under "Spec notes", at the bottom of the page. -->

- 8 ZEN 2 CPU CORES*
- 16 THREADS*
- 3.5 GHz
- 40 COMPUTE UNITS*
- 16 GIGABYTE GDDR6
- 3840 PIXELS 4K ULTRA HD
- 2 TERABYTE SSD NVME**

## Spec notes

- * The most the board can unlock in theory. Every board is unique.
- ** Storage depends on your own setup. This is a real-life example.

## Portal

The portal runs fullscreen. It works as well on a TV with a controller as on a monitor with a keyboard and mouse.

- A big tile for every app, sharp on a 4K screen
- The keyboard, the mouse or a controller, all alike
- A red dot as soon as an update is out
- Install all apps or all updates with one press
- Shortcuts to Steam, Discord, YouTube, Twitch and GitHub
- Live CPU and GPU temperatures, time and weather
- Three themes, your own wallpaper and your own music
- Every download checked against its checksum

## And more

Small touches that make the board a joy to use, everywhere you look.

- An overlay with your CPU, GPU and temperatures, always on top
- Everything the board reports, in one Sys info window
- The battery of your controller, mouse or headset, right in the header
- You pick an emulator version or add your own, the tested one is marked
- Steam covers for your games from SteamGridDB, with your own API key
- Share + Options brings up the quit menu in PS3 and PS4 games
- The weather for your own place, with the forecast one click away
- The on-screen keyboard at a press of R3
- Check out The Portal's Tour with a click on the suite's icon

## Safety

Push your board further, with your eyes open. Apps that change how the board runs carry a clear mark. The portal
asks before it installs or opens them. Every change is software-only, and you can undo it.

## Categories

| Category | Line |
|---|---|
| sustainable | Test it, tune it, unlock it and keep it cool. |
| graphics | Upscaling, async compute and mesh shaders for your games. |
| gaming | Classic consoles, Remote Play and PlayStation trivia with DatStation. |
| utilities | Handy tools around the board, from the TV remote to your SSD. |

## Apps

| App | Line |
|---|---|
| check | Know your board inside out. Diagnostics, a stress test and benchmarks come with every portal. |
| gpu | Take control of the GPU governor. Tune it, find safe points, and keep profiles and backups. |
| compute | Unlock more compute units with confidence. It tells bad CUs apart from an unstable unlock. |
| cores | Go for 8 cores and 16 threads. It finds bad cores before you make the unlock stick. |
| acpi | Give the CPU its C-states and frequency scaling, through a persistent ACPI override. |
| vram | Memory set for your games. It sets the VRAM split, GTT and swap, and learns from the games you play. |
| fan | Stay cool under load. A thermal guard warns, cools and shuts down cleanly at a critical temperature. |
| upscaler | Sharper games with HelixSR, a drop-in upscaler for FSR 3.1 with DLSS-style networks. |
| ace | Async compute for your games. A patched RADV, built on the board and tested. |
| mesh | Mesh shaders for your games, with RADV and DirectMesh beside the system Mesa. |
| consoles | Play your PS4 and PS5 from the board. Find, wake and register them, then start Remote Play. |
| clb | Stream your XBOX or XBOX Cloud Gaming to the board, signed in with your Microsoft account. |
| shadps4 | PS4 games in Steam. It sets up a tested shadPS4 release, finds your games and unpacks .pkg files. |
| kytyps5 | PS5 games in Steam. It sets up a tested KytyPS5-Native release, checks the board's memory settings and finds your games. |
| rpcs3 | PS3 classics in Steam. It sets up a tested RPCS3 build and the firmware, then finds your games. |
| datstation | Test your PlayStation knowledge. A quiz, console history, region codes, user guides and news. |
| ppsspp | PSP games in Steam. It sets up a tested PPSSPP release and finds your games. |
| pcsx2 | PS2 favorites in Steam. It sets up a tested PCSX2 release and your PS2 BIOS, then finds your games. |
| vita3k | PS Vita games in Steam. It sets up a tested Vita3K build, then installs the firmware and your games. |
| xenia | XBOX 360 games in Steam. It sets up a tested Xenia build. Xenia is experimental on Linux. |
| overlay | Your vitals, always in sight. CPU, GPU, refresh rate, fan and temperatures in a window on top. |
| bios | See every BIOS setting, hidden menus included. Stock or modded BIOS, and read-only. |
| cec | One remote for the TV and the board. Turn the TV on and off and switch its input over HDMI-CEC. |
| sftp | Move files between computers over SFTP, and manage the SSH server of a Bazzite host. |
| turing | Put your stats on display. CPU, GPU, memory, fan and temperatures on a Turzx USB screen. |
| webcam | The PS5 HD Camera becomes a webcam. It loads the camera's firmware at every plug-in. |
| controller | Your DualSense in top form. Battery, firmware updates from the official server and the Edge's profiles. |
| ssd | Know how your SSDs are doing. It shows their health, power cycles and power-on hours. |
| btpair | Your Bluetooth keyboard, mouse and controllers, paired at boot. No USB keyboard or mouse needed. |
| quickfix | Always installed. Quickfixes for MangoHud, GPU metrics, sensors, the journal, the IOMMU and more. |
| password | A random password of 8 or 15 characters, kept nowhere. |

## Video

The Portal Tour shows the portal in four minutes. A voice reads every caption out.

## Get it

Ready for the next level? It takes four steps.

1. Download the newest portal from the latest release
2. Check it against its SHA256SUMS file
3. Run its installer
4. Pick your apps in the portal

## Closing

Open source and free. Made by the community, for the BC-250.
