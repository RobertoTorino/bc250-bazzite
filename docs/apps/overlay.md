<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 System Overlay](../assets/overlay/bc250-system-overlay.webp){ .app-logo }

# BC-250 System Overlay

A small window that stays on top of your desktop and shows the **AMD BC-250**'s live system values on
**Bazzite**. It only reads sensors. Nothing on the board changes, and it needs no root.

| Row | What it shows | Source |
|---|---|---|
| CPU | load over the last second and the average core clock | `/proc/stat`, cpufreq |
| GPU | load averaged over the last second, the clock, and the GPU's own power with **VRM Sensors** on | the GPU governor's `gpu_metrics`, `amdgpu`, `bc250_vrm` |
| Chip power | what the whole chip draws: CPU, GPU and the rest together | `amdgpu` (its PPT value) |
| Governor | the GPU governor's current clock range | the governor, over D-Bus |
| GPU volt | core voltage (vddgfx) | `amdgpu` |
| CPU rail | voltage, current and power of the CPU's supply | `bc250_vrm` |
| GPU rail | voltage, current and power of the GPU's supply | `bc250_vrm` |
| 12 V input | the board's 12 V input, as the voltage regulator measures it | `bc250_vrm` |
| VRAM | used / total of the GPU's share of the memory | `amdgpu` |
| RAM | used / total | `/proc/meminfo` |
| Screen | the resolution, scale and refresh rate of the screen the window is on | Qt |
| Fan | the fastest spinning fan. Hover it to see every fan. | `nct6686` and any other fan sensor |
| CPU temp | Tctl | `k10temp` |
| GPU temp | edge | `amdgpu` |
| VRM temp | the voltage regulators | `nct6686` ("VRM MOS") |
| CPU VRM temp | the regulators of the CPU's supply | `bc250_vrm` |
| GPU VRM temp | the regulators of the GPU's supply | `bc250_vrm` |
| NVMe temp | the SSD | `nvme` |
| Network | download and upload, all interfaces except loopback | `/proc/net/dev` |
| Disk | read and write, all disks | `/proc/diskstats` |

The BC-250's GPU has no load sensor of its own. Its driver does not support `gpu_busy_percent`. The GPU governor
measures the load instead. With its **fix-metrics** setting on (the default), it publishes the load in the
`gpu_metrics` table. The GPU row reads it from there. Without fix-metrics the row shows clock and power only.
Hovering the row says why. The Governor row shows "—" when the governor does not run.

The five `bc250_vrm` rows need the kernel module of that name. It reads the board's voltage regulator. Bazzite
does not include it. [VRM Sensors](quickfix.md#vrm-sensors) in BC-250 Quickfix builds and loads it.
Without the module these rows show "—", and hovering one says why.
The power is the voltage times the current.

A row shows "—" when the board or kernel does not offer its value. Temperatures turn orange from 80 °C and red
from 90 °C. The values update every second.

## Using it

- **Move it:** drag it with the left mouse button. It opens where you left it.
- **Options:** right-click it.
  - **Rows:** check the rows you want to see. The window resizes to fit.
  - **Background:** from **Solid** to **Very see-through**. The text stays fully visible.
  - **Always on top:** on by default.
  - **Quit.**

The window is frameless and see-through, with rounded corners and a thin border in the theme's accent.

### Where it shows

- **Desktop mode:** on top of the desktop and of windowed or borderless games. A game in exclusive fullscreen can
  still cover it.
- **Game Mode (gamescope):** not visible. Gamescope only shows the running game. Use MangoHud there.

On Wayland a window cannot keep itself on top or choose where it opens. That is why the overlay runs through XWayland.
`bc250-system-overlay --native-wayland` runs it as a Wayland window instead. It looks sharper on a scaled screen.
KDE then decides whether it stays on top. A KWin window rule can keep it there.

## Install

Install it from the BC250 Bazzite Suite portal, or from a clone or release folder, as your own user:

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
./install.sh --uninstall             # remove the app; keeps its settings
./install.sh --uninstall --purge     # also remove its settings
```

It installs:

- the app in `~/.local/share/bc250-system-overlay/app`, with the tested `bc250_core` beside it
- PyQt6 in the suite's shared venv `~/.local/share/bc250-bazzite-suite/venv`
- the launcher `~/.local/bin/bc250-system-overlay`, an app menu entry and a Desktop icon

The app keeps its settings in `~/.config/bc250-system-overlay/bc250-system-overlay.ini`.

## License

GPL-3.0-or-later — see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/overlay/LICENSE).
