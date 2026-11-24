<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-17b6a7)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# Nexus Garbage Remover

Nexus Garbage Remover finds the garbage on this machine and deletes the places you check. It lists these places,
each with its size and the command that empties it:

- crash dumps
- Steam's crash reports
- the Trash
- caches that fill up

An hourly notification tells you when there is 1 GB or more. Nexus Garbage Remover is a development app. It runs from
the checkout it lives in and has no releases of its own. Start it from [Nexus Dashboard for BC-250](../dash), or with
these commands:

| | Linux |
|---|---|
| Open it | `dev/garbage/run.sh`, or `dev/garbage/run.sh --remind` for the hourly check |
| Menu entry, Desktop icon and hourly reminder | `dev/garbage/install.sh` (`--no-desktop-shortcut`, `--uninstall`, `--uninstall --purge`) |

How to use it: [Garbage Remover in the wiki](https://robertotorino.github.io/bc250-bazzite/development/dashboard/#garbage-remover).

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
