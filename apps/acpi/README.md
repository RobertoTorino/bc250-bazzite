<!-- SPDX-License-Identifier: MIT -->

![Status: Beta](https://img.shields.io/badge/status-Beta-8b4fd8)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

# BC-250 Persistent ACPI

Gives the CPU of the **AMD BC-250** its idle states (C-states) and frequency scaling on Linux. The frequency scales
from 800 MHz to 3.2 GHz in 8 steps. The fix is **persistent**, so it stays across restarts and updates. It is a safe
alternative to BIOS flashing. You don't need the P3.00 MeiMeiDXE v3 modded BIOS.

How to install and use it: [BC-250 Persistent ACPI in the wiki](https://robertotorino.github.io/bc250-bazzite/apps/acpi/).

## License

MIT, see [LICENSE](LICENSE).
