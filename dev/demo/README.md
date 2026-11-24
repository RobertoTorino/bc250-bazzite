<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-17b6a7)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# Nexus Demo Recorder

Nexus Demo Recorder records a demo video of a portal installation with OBS. It installs one of these in a terminal
while OBS records the screen:

- a portal release extracted in Downloads
- the suite in this checkout

Then it opens the portal, and you install and show one optional app. It is a development app. It runs from the
checkout it lives in and has no releases of its own. Start it from [Nexus Dashboard for BC-250](../dash), or:

| | Linux |
|---|---|
| Open it | `dev/demo/run.sh` |
| Menu entry and Desktop icon | `dev/demo/install.sh` (`--no-desktop-shortcut`, `--uninstall`, `--uninstall --purge`) |

The installer copies nothing. The entry starts the app of the checkout you installed it from.

How to use it: [Demo Recorder in the wiki](https://robertotorino.github.io/bc250-bazzite/development/dashboard/#demo-recorder).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE).
