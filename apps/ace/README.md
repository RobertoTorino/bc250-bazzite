<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-8b4fd8)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# BC-250 ACE Queues

BC-250 ACE Queues lets games on the **AMD BC-250** use its dedicated compute queues (async compute) on
**Bazzite**. It builds a patched RADV on the board and installs it beside the system Mesa. Games use it only
after its test passed on the running kernel.

How to install and use it: [BC-250 ACE Queues in the wiki](https://robertotorino.github.io/bc250-bazzite/apps/ace/).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE). The Mesa patch in `mesa/` is MIT, as the Mesa file it changes.
