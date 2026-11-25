<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-17b6a7)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# Nexus Dashboard for BC-250

Nexus Dashboard for BC-250 is one door to the tools for working on the suite. Its tiles start the development apps of
the checkout. Each app opens in a window of its own:

- [Nexus Release Tool](../nrt)
- [Nexus Installer Tests](../itests)
- [Nexus Marketing for BC-250](../marketing)
- [Nexus Demo Recorder](../demo)
- [Nexus Sound Lab](../sounds)
- [Nexus Deps](../deps)
- [Nexus Garbage Remover](../garbage)
- [Nexus TTS](../text)
- [Nexus Remix Studio](../studio)

Other tiles open the suite's tools:

- record the portal's and the apps' video tours
- convert the category icons
- close the repository's open issues on GitHub that you check

Nexus Dashboard for BC-250 is a development app. It runs from the checkout it lives in. It has no releases of its own.

## Start it

From the repository's root, with the checkout's venv ([Set up and test](https://robertotorino.github.io/bc250-bazzite/development/#set-up-and-test)):

| | Linux |
|---|---|
| Open it | `dev/dash/run.sh` |
| Menu entry and Desktop icon | `dev/dash/install.sh` |

The installer takes these options:

- `--no-desktop-shortcut`
- `--uninstall`
- `--uninstall --purge`, which also removes the settings

The installer copies nothing. The menu entry starts the app of the checkout you installed it from.

How to use it: [Dashboard in the wiki](https://robertotorino.github.io/bc250-bazzite/development/dashboard/).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE).
