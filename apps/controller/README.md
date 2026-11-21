<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-8b4fd8)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# BC-250 Controller

BC-250 Controller is for the **DualSense** and **DualSense Edge** controllers on **Bazzite**. The window shows the
controller's connection, battery and firmware. It updates the firmware from the official update server over a USB
cable. Officially, you get that update only on a PS5 and in an app for Windows. The window also shows the DualSense
Edge's four profiles, creates and edits them, and keeps a backup of them. A small service switches a controller on
Bluetooth off when you do not use it, as a PS5 does. Linux's own driver keeps driving the controller. The app needs no
root.

How to install and use it: [BC-250 Controller in the wiki](https://robertotorino.github.io/bc250-bazzite/apps/controller/).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE). The update protocol is ported from
[dualsense-updater-rs](https://github.com/nchie/dualsense-updater-rs), MIT, Copyright 2026 nchie. The layout and
writing of the Edge's profiles are ported from
[dualsense-edge-profile-web-application](https://github.com/steffalon/dualsense-edge-profile-web-application), MIT,
Copyright (c) 2023 steffalon. The files ported from them say so in their header and keep the MIT notice below. The
controllers' firmware is Sony's and is not part of this app.

```
MIT License

Copyright 2026 nchie (dualsense-updater-rs)
Copyright (c) 2023 steffalon (dualsense-edge-profile-web-application)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
