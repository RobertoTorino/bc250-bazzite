<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# This suite (BC250 Bazzite Suite)

What only this suite has. The rules every suite shares are in [CLAUDE.md](../CLAUDE.md), which reads this file.

## What it is

- **Name:** the **BC250 Bazzite Suite**, exactly that name: tools for the AMD BC-250 on Bazzite.
- **Repository:** `github.com/RobertoTorino/bc250-bazzite`, branch `main`. The owner works on it from Bazzite, and
  the BC-250 board is the development machine.
- **Wiki:** robertotorino.github.io/bc250-bazzite/
- **System:** `bazzite` (`SYSTEM`). **Tags:** `bc250-<app>-v<x.y.z>` and `bc250-portal-v<x.y.z>` (`TAG_PREFIX`,
  owner 15-11-2026; the releases made in Nexus had no prefix).
- **History:** the suite was the folder `bc250-bazzite/` of Nexus (`github.com/RobertoTorino/nexus`) until
  14-11-2026, with its tags, releases and wiki there (owner, 14-11-2026: one repository per suite). The app ids, the
  launchers and the suite's folder on the board stayed the same through the moves.
- **Twin:** the Bazzite Console Suite (`github.com/RobertoTorino/bazzite-console`), for the PlayStation 5, checked
  out beside this one. This suite may name its twin.
- **Design:** the Bazzite design, purple, for the apps' theme and the wiki's.

## Names

- **Portal package:** `bc250_portal`. **Core package:** `core/bc250_core/`.
- **On the board:** the program and the shared venv in `~/.local/share/bc250-bazzite-suite/` (`portal`, `state`,
  `venv`).
- **An app's package** drops the BC-250 or Bazzite prefix: `apps/ace/ace_queues/`, `apps/datstation/datstation/`.
- **Nexus Deps' catalog:** `dev/deps/nexus_deps/catalogs/bc250-bazzite.toml`.
- **A new app's name** starts with "BC-250".

## The apps

**check** (BC-250 Board Test) is always installed and always listed first.

`apps/<name>/`: check, gpu, upscaler, compute, cores, oc, acpi, overlay, turing, webcam, controller, bios, ace, mesh,
vram, fan, wifi, cec, sftp, consoles, clb, shadps4, rpcs3, ppsspp, pcsx2, vita3k, xenia, datstation, ssd, btpair,
quickfix, password.

**Licenses:** acpi is MIT. consoles is AGPL-3.0: its protocol code is ported from chiaki-ng, those files
AGPL-3.0-only, its own AGPL-3.0-or-later. clb (BC-250 XB Remote Play, XBOX) is GPL-3.0-or-later with protocol code
ported from Greenlight and xal-node, MIT, whose notice its README keeps. The rest is GPL-3.0-or-later.

**Apps that change the board:** the CU and core unlocks, the GPU governor, GPU overclocking, the ACPI override, the
patched RADV of ace, the DirectMesh RADV of mesh, the VRAM split of vram, the thermal guard of fan and the kernel
module of wifi. In `portal/apps.toml`: gpu, compute, cores, oc, acpi, ace, mesh, vram, fan, wifi.

**Upstreams an app pins** (`tools/check_upstream.py`): an emulator, HelixSR, DirectMesh, the USB Wi-Fi driver, Mesa,
FFmpeg.

## Rules for this suite alone

- **Reboots, the exceptions to "Advice, not reboots"** (owner, 15-10-2026): CU Bisect and Cores Bisect, whose rounds
  each need a fresh boot (they ask, or reboot by themselves with `--auto`), and Cores Unlock's boot service, which
  reboots warm once after a cold boot so the cores come up. A second exception (owner, 16-10-2026): the thermal
  guard shuts the board down cleanly at a critical temperature, to protect the hardware; the limits are the owner's.
- **The baseline** was tested extensively on two boards.
- **chiaki-ng is named only where licensing needs it:** PS Remote Play's LICENSE, the License sections of its README
  and wiki chapter, the suite's license overview (README, docs/index.md) and this file. Everywhere else (code,
  comments, tests, vectors, log messages, the wiki, CHANGELOGs) it is "the reference" (the reference
  implementation); user-facing text does not mention it at all.
- **KROU4's PS5CameraDriver is never named** (owner, 23-10-2026), only in this file: not in code, comments, tests,
  the wiki or CHANGELOGs. Where its tried firmware patch matters, it is "another project's firmware patch".
