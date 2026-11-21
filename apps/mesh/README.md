<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![Status: Beta](https://img.shields.io/badge/status-Beta-8b4fd8)
[![CI](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml/badge.svg)](https://github.com/RobertoTorino/bc250-bazzite/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

# BC-250 Mesh Shaders

BC-250 Mesh Shaders brings mesh shaders to games on the **AMD BC-250** with **Bazzite**. It uses RADV with
[DirectMesh](https://github.com/lonewolf0622/bc250meshtaskwork). The app builds the driver on the board and installs
it beside the system Mesa. Games use it only after its test has passed on the running kernel.

How to install and use it: [BC-250 Mesh Shaders in the wiki](https://robertotorino.github.io/bc250-bazzite/apps/mesh/).

## License

GPL-3.0-or-later, see [LICENSE](LICENSE). The DirectMesh patch in `mesa/` is the published patch of
[DirectMesh](https://github.com/lonewolf0622/bc250meshtaskwork) by lonewolf0622, unchanged, and MIT, as Mesa. The
suite's patch in `mesa/`, applied on top of it, is GPL-3.0-or-later, as the app.
