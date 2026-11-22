<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-8b4fd8)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# BC-250 Webcam

BC-250 Webcam makes the **PS5 HD Camera (CFI-ZEY1)** a webcam on **Bazzite**. Linux then sees an ordinary USB
video camera, for OBS, a browser or any other app.

The camera has no memory of its own. It starts as a bootloader, a small program that waits for its firmware. A
PlayStation sends that firmware each time you plug the camera in. The app does the same:

- It gets the firmware, as a pinned and checked download or as a file of your own.
- It gives your user the camera, once.
- It sends the firmware by itself whenever you plug the camera in.

The window shows the camera's state and its picture in every mode the camera reports. That is one camera's picture,
or both side by side. A PS4 Camera on Sony's adapter works the same way, with its own firmware.

How to install and use it: [BC-250 Webcam in the wiki](https://robertotorino.github.io/bc250-bazzite/apps/webcam/).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE). The camera's firmware is Sony's. It is not part of this app.
