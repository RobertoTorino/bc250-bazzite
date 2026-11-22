<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-8b4fd8)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# BC-250 Memory Manager

BC-250 Memory Manager sets the VRAM split of the **AMD BC-250** on **Bazzite** in the board's CMOS. It also sets
the GTT limit (`ttm.pages_limit`) on the kernel command line, and the swap layout. The swap layout is zram, or zswap
with a swap file. The app shows the GTT, the TTM limit, the system RAM and the swap that go with them. Each setting
changes only when you apply it, and takes effect after a restart.

How to install and use it: [BC-250 Memory Manager in the wiki](https://robertotorino.github.io/bc250-bazzite/apps/vram/).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE). The CMOS layout comes from
[fanoush/bc250_memcfg](https://github.com/fanoush/bc250_memcfg) (MIT).
