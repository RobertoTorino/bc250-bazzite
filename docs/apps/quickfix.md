<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Quickfix](../assets/quickfix/bc250-quickfix.webp){ .app-logo }

# BC-250 Quickfix

Small windows for one job each, which come with the suite: the portal installs them with itself, with Board Test,
and keeps them. In the portal's **Utilities** tab each quickfix is a tile of its own; the app's menu entry,
**BC-250 Quickfix**, lists them all in one window.

Every quickfix's window has the suite's header: the quickfix's name with the version, its state, and **Refresh**. The
small round **i** beside the state says what the quickfix contains and does. The quickfixes that change the board say so
on their tile; the portal asks before it opens one. Each of those asks for your password (pkexec) for every change,
turns on only what is off, and turns off only what it turned on itself.

| Quickfix | What it does | Changes the board |
|--------|--------------|-------------------|
| [Quickfix](#quickfix) | The optional tools Board Test's tests use: which are there, and their installer. | No |
| [MangoHud Config](#mangohud-config) | Open or create MangoHud's config, edit and save it; turn on the FPS log Board Test reads. | No |
| [Fix GPU Metrics](#fix-gpu-metrics) | Let the GPU governor write the real GPU load into gpu_metrics, for the overlays. | Yes |
| [Sensors Module](#sensors-module) | Load a driver for the board's SuperIO chip at every boot, for its temperatures and fans. | Yes |
| [Game Memory Map](#game-memory-map) | Raise vm.max_map_count, the number of memory areas a game may map. | Yes |
| [Persistent Journal](#persistent-journal) | Keep the system journal on the disk, so the logs of a boot that crashed can be read after it. | Yes |
| [IOMMU Off](#iommu-off) | Keep the kernel from using the board's IOMMU, which is broken on the BC-250 (amd_iommu=off). | Yes |
| [CPU Mitigations Off](#cpu-mitigations-off) | Turn off the kernel's CPU mitigations, which cost speed in games (mitigations=off). | Yes |

## Quickfix

Board Test runs without extra tools: a test whose tool is missing says so. **Quickfix** lists the tools the tests
use when they are there, with a dot for each one that is found and the tests that use it, and the **Tools found**
box counts them. It looks where the tests look: on `PATH`, in `~/.local/bin` and in Homebrew.

Each group's heading is a pill: a click on it (**Install**) runs Board Test's own installer for that group in a
terminal, `/opt/bc250-board-test/development/tools/install-requirements.sh` with the group's option; it reads
**Installed** and is off when everything in the group is there. **Install all** installs every group but
the development extras (`--all`), and **Refresh** beside it reads the tools again. The groups and their tools are listed in [BC-250 Board Test](check.md#download-and-install), with the tests that use each one. Layered RPM
packages are active after a reboot (`systemctl reboot`); until then the tools of that group still show as missing.

The group **Prime95** is `mprime`, which no test uses: [BC-250 CPU Tools](cores.md#longer-burn-in-mprime--rasdaemon)
runs its torture test for a longer burn-in. The pill installs the release that mersenne.org's download page lists
at that moment, compared with the SHA-256 listed there, into `~/mprime`, with a link in `~/.local/bin`. A newer
release later shows in Nexus Deps as **Prime95 (mprime)**, and its **Update** installs it over the old one.

## MangoHud Config

Opens MangoHud's own settings file, `~/.config/MangoHud/MangoHud.conf`, in an editor; a file that is not there yet
is made by **Save**. **Revert** reads the file again. The boxes show whether the file is there, whether MangoHud's
log is on, and how many log files there are.

Board Test shows a game's FPS from MangoHud's log, which MangoHud writes while the game runs. **FPS log** sets the
three lines it needs:

```ini
output_folder=/home/<you>/mangohud-logs
autostart_log=1
log_interval=500
```

A line that sets one of them already is changed where it is; the others are added at the end. **Save** writes the
file and makes the log folder. MangoHud must be active for the game, for example with the Steam launch option
`mangohud %command%`. A log file is written per game session: **Delete old logs** removes the ones older than 30
days, and **Log folder** opens the folder. Without the log, Board Test still shows the game's name and its CPU and
GPU share.

## Fix GPU Metrics

!!! warning "Changes the board"
    Turn on sets fix-metrics and the load method in the [gpu-usage] table of the GPU governor's settings file,
    /etc/cyan-skillfish-governor-smu/config.toml, after a dated backup of it beside it, and restarts the governor
    when it runs; the governor then mounts a patched copy of gpu_metrics over the sysfs file while it runs. The
    setting stays across reboots and power offs. Nothing is written to the BIOS, the firmware or the kernel's
    arguments. Turn off sets fix-metrics back to false and restarts the governor; any earlier settings file is in
    its backups.

The GPU governor, cyan-skillfish-governor-smu, measures the real GPU load to drive the clock. With `fix-metrics` on,
it also writes that load into a patched copy of `gpu_metrics` and mounts it over the sysfs file, so the Steam
performance overlay, MangoHud and radeontop show a real GPU %.

The boxes show whether the governor is installed (its settings file is there), whether `fix-metrics` is on, and
whether the patched copy is mounted. Pick the method and **Turn on** (or **Apply**, for another method):

- `busy-flag` samples the GPU's busy bit, the default.
- `process` sums the programs' GPU time from `/proc/*/fdinfo`; it costs more CPU and can stall on Proton games with
  very many open files.
- `kernel` only works on a patched kernel that reports the load.

The quickfix makes the same dated backup as [BC-250 GPU Manager](gpu.md) (`config.toml.bak-YYYYMMDD-HHMMSS`), whose
Backups page lists it. A governor that is stopped stays stopped: the patched copy is mounted when it runs. Check it
with `mount | grep gpu_metrics`. On some kernels the patching misbehaves: if the overlay or the governor acts up,
**Turn off** again. A kernel that reports the load itself does not need it.

## Sensors Module

!!! warning "Changes the board"
    Turn on writes one line, options nct6683 force=true, to /etc/modprobe.d/bc250-quickfix-nct6683.conf and loads the
    nct6683 driver, which reads the board's SuperIO chip: its temperatures and fan speeds. The file stays across
    reboots and power offs, so the driver loads at every boot. Nothing is written to the BIOS, the firmware or the
    chip. Turn off removes the file; the driver stays loaded until the next boot.

The board's SuperIO chip, a Nuvoton NCT6686D, reports its temperatures and fan speeds (Board Test's test 22,
lm_sensors' `sensors`). Bazzite loads the nct6687 driver for it by itself since image 45.20261117, so there the
quickfix is not needed. Other images may not load it. The kernel's own nct6683 driver loads only when it is forced. The boxes show which driver is loaded, whether nct6683 is forced at boot, and the
chip's sensors as it reports them. **Turn on** is offered only when no driver serves the chip. A modprobe file of
your own that forces nct6683 already counts too; **Turn off** removes only the quickfix's file.

## Game Memory Map

!!! warning "Changes the board"
    Turn on writes vm.max_map_count = 2147483642 to /etc/sysctl.d/90-bc250-quickfix-max-map-count.conf and sets it
    now: the number of memory areas one program may map. The file stays across reboots and power offs. Nothing is
    written to the BIOS, the firmware or the kernel's arguments. Turn off removes the file and reads the system's
    settings again, so the value the other settings files give, else the kernel's own, is back.

`vm.max_map_count` is the number of memory areas one program may map. Some games, and Proton, need far more than
the kernel's default and crash without them; SteamOS and Bazzite set 2147483642. The boxes show the value now and
what set it: the quickfix, or the system (another file in `/etc/sysctl.d` or the image's own). **Turn on** is offered
only when the value is lower. Board Test's test 37 reports it.

## Persistent Journal

!!! warning "Changes the board"
    Turn on makes the folder /var/log/journal, with systemd-tmpfiles, and moves the journal there: journald then
    keeps the system's logs on the disk, within its own size limits, instead of in memory only. The folder stays
    across reboots and power offs. Nothing is written to the BIOS or the firmware. Turn off works only on a folder
    this quickfix made: it moves the journal back to memory and removes the folder, with the logs in it.

Without `/var/log/journal`, journald keeps the system journal in memory only, and the logs of a boot that crashed or
froze are gone after it: Board Test's test 34 cannot read the previous boot's logs. The boxes show where the journal
is kept and who made the folder. **Turn on** is offered only when the folder is not there; **Turn off** asks first,
as it removes the logs of every earlier boot.

## IOMMU Off

!!! warning "Changes the board"
    Turn on adds the kernel argument amd_iommu=off with rpm-ostree kargs, which makes a new deployment with it, and
    notes in /var/lib/bc250-quickfix/iommu.karg that the quickfix added it; from the next boot the kernel leaves the AMD
    IOMMU unused. The argument stays across reboots, power offs and Bazzite's updates. Nothing is written to the BIOS or
    the firmware. Turn off works only on an argument this quickfix added: it removes it with rpm-ostree kargs, and the
    kernel uses the IOMMU again from the next boot. Both need a reboot, which the quickfix advises and never does.

The board's AMD IOMMU (AMD-Vi) is broken on the BC-250, and a system that uses it is unstable. The modded BIOS can
switch it off; without it, the kernel argument `amd_iommu=off` keeps the kernel from using it, which is the same from
Linux's side. With the IOMMU off there are no IOMMU groups, which is what Board Test's test 23 checks; passing a PCI
device to a virtual machine (VFIO) is then not possible.

The boxes show the IOMMU now (on when there are IOMMU groups), whether `amd_iommu=off` is on the running kernel's
command line and on the next boot's (`rpm-ostree kargs`), and who added it. **Turn on** is offered when the next boot
lacks the argument and the BIOS does not have the IOMMU off already. After **Turn on** or **Turn off** the window
says **Reboot to apply**: restart the board with `systemctl reboot`. An `amd_iommu=off` you added yourself counts
too; **Turn off** removes only the one the quickfix added.

## CPU Mitigations Off

!!! warning "Changes the board"
    Turn on adds the kernel argument mitigations=off with rpm-ostree kargs, which makes a new deployment with it, and
    notes in /var/lib/bc250-quickfix/mitigations.karg that the quickfix added it; from the next boot the kernel no longer
    guards against the CPU's speculative execution flaws (Spectre, Meltdown and the like). The argument stays across
    reboots, power offs and Bazzite's updates. Nothing is written to the BIOS or the firmware. Turn off works only on an
    argument this quickfix added: it removes it with rpm-ostree kargs, and the mitigations are back from the next boot.
    Both need a reboot, which the quickfix advises and never does.

The kernel guards against the CPU's speculative execution flaws (Spectre, Meltdown and the like), and that costs
speed: roughly 18 FPS in games on this board. The kernel argument `mitigations=off` turns those guards off. Without
them a program could, in principle, read the memory of other programs: keep them on where the board runs code you
do not trust. Board Test's test 24 reports it.

The boxes show whether `mitigations=off` is on the running kernel's command line and on the next boot's
(`rpm-ostree kargs`), and who added it. **Turn on** is offered when the next boot lacks it; after a change the window
says **Reboot to apply** (`systemctl reboot`). A `mitigations=off` you or the image set counts too; **Turn off**
removes only the one the quickfix added.

## Install

The portal installs the quickfixes with itself, and its uninstall removes them; the portal lists no Uninstall for them.
From a checkout of the repository:

```bash
apps/quickfix/install.sh                         # the app, its launcher, a menu entry and a Desktop icon
apps/quickfix/install.sh --no-desktop-shortcut   # without the Desktop icon
apps/quickfix/install.sh --uninstall             # remove it; --purge removes its settings too
```

The launcher is `~/.local/bin/bc250-quickfix`: without an argument it opens the list, with a quickfix's key the
quickfix's own window (`bc250-quickfix tools`, `mangohud`, `metrics`, `sensors`, `mapcount`, `journal`, `iommu`,
`mitigations`). The app runs on the suite's shared Python environment.

## Files

- `~/.config/MangoHud/MangoHud.conf` and `~/mangohud-logs/`: MangoHud's own settings file and its log folder.
- `/etc/cyan-skillfish-governor-smu/config.toml` and its `config.toml.bak-*` backups: the governor's settings file.
- `/etc/modprobe.d/bc250-quickfix-nct6683.conf`, `/etc/sysctl.d/90-bc250-quickfix-max-map-count.conf` and
  `/var/log/journal/.bc250-quickfix`: what Sensors Module, Game Memory Map and Persistent Journal turned on, while it
  is on.
- `/var/lib/bc250-quickfix/iommu.karg` and `mitigations.karg`: the notes that IOMMU Off and CPU Mitigations Off added
  their kernel argument, while it is on.

Uninstalling the app leaves all of them as they are: turn a quickfix off first to undo it.

## License

GPL-3.0-or-later.
