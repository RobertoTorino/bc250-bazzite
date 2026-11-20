<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-8b4fd8)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# BC-250 Quickfix

Small quickfixes for one job each: Board Test's optional tools, MangoHud's config, GPU metrics, the sensors driver, the regulator's sensors, the memory map, the journal, the IOMMU and the CPU mitigations. Always installed.

How to install and use it: [BC-250 Quickfix in the wiki](https://robertotorino.github.io/bc250-bazzite/apps/quickfix/).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE). The kernel module's source in `quickfix/vrm` is
[bc250-vrm-dkms](https://github.com/Hexxeh/bc250-vrm-dkms) by Liam McLoughlin, unchanged, under its own license
(GPL-2.0, see [quickfix/vrm/LICENSE](quickfix/vrm/LICENSE)).
