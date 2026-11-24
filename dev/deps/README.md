<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-17b6a7)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# Nexus Deps

Nexus Deps shows the Python packages and external tools of the suite's apps installed on this machine. It shows
which apps use them, and what is missing or must be updated. It names the known vulnerabilities from OSV.dev. It also
shows Bazzite's update state and every update of the machine:

- Bazzite's image
- Flatpaks
- Homebrew
- Rust
- the development venv
- Prime95's mprime

**Fix** installs what is missing, outdated or newer. It shows every command first and asks. An hourly notification
tells you when something needs you. Nexus Deps is a development app. It runs from the checkout it lives in and has no
releases of its own. Start it from [Nexus Dashboard for BC-250](../dash), or:

| | Linux |
|---|---|
| Open it | `dev/deps/run.sh`. With `--fix`, it offers Fix at once. With `--remind`, it runs the hourly check. |
| Menu entry, Desktop icon and hourly reminder | `dev/deps/install.sh` (`--no-desktop-shortcut`, `--uninstall`, `--uninstall --purge`) |

The installer copies nothing. The entry starts the app of the checkout you installed it from. The app's catalog of
the suite is `nexus_deps/catalogs/bc250-bazzite.toml`.

How to use it: [Deps in the wiki](https://robertotorino.github.io/bc250-bazzite/development/dashboard/#deps).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE).
