<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Quickfix](../assets/quickfix/bc250-quickfix.webp){ .app-logo }

# BC-250 Quickfix

BC-250 Quickfix gives you quickfixes, small windows for one job each. They come with the suite. The portal installs
them together with itself and Board Test, and keeps them. In the portal's **Utilities** tab, each quickfix is a tile of
its own. The app's menu entry, **BC-250 Quickfix**, lists them all in one window.

Every quickfix's window has the suite's header. It shows the quickfix's name with the version, and its state.
The status boxes and the pills are on the rows under it.
The round arrow at the right end of the title row reads the state again.
The small round **i** beside the state says what the quickfix contains and does.

Some quickfixes change the board, and say so on their tile. The portal asks before it opens one of them. Each of them
works like this:

- It asks for your password (pkexec) for every change.
- It turns on only what is off.
- It turns off only what it turned on itself. Fix GPU Metrics is the exception. Its **Turn off** sets `fix-metrics`
  back to false, whoever turned it on.

| Quickfix | What it does | Changes the board |
|--------|--------------|-------------------|
| [Quickfix](#quickfix) | Shows which optional tools Board Test's tests use, which are there, and installs them. | No |
| [MangoHud Config](#mangohud-config) | Opens MangoHud's config to edit and save. Turns on the FPS log that Board Test reads. | No |
| [Fix GPU Metrics](#fix-gpu-metrics) | Lets the GPU governor write the real GPU load into `gpu_metrics`, for the overlays. | Yes |
| [Sensors Module](#sensors-module) | Loads a driver for the board's SuperIO chip at every boot, for its temperatures and fans. | Yes |
| [VRM Sensors](#vrm-sensors) | Builds and loads the module that reads the voltage, current and temperature of the CPU and GPU supply. | Yes |
| [Game Memory Map](#game-memory-map) | Raises `vm.max_map_count`, the number of memory areas a game may map. | Yes |
| [Persistent Journal](#persistent-journal) | Keeps the system journal on the disk. Then you can read the logs of a boot that crashed. | Yes |
| [IOMMU Off](#iommu-off) | Keeps the kernel from using the board's IOMMU, which is broken on the BC-250 (`amd_iommu=off`). | Yes |
| [CPU Mitigations Off](#cpu-mitigations-off) | Turns off the kernel's CPU mitigations, which cost speed in games (`mitigations=off`). | Yes |

## Quickfix

**Quickfix** shows you which optional tools Board Test's tests use, and installs the missing ones. Board Test runs
without extra tools. A test whose tool is missing says so.

The window lists the tools with the tests that use them. A filled dot marks each tool that is there. The **Tools
found** box counts them. The window looks where the tests look:

- on `PATH`
- in `~/.local/bin`
- in Homebrew

Each group's heading is a pill. Click it (**Install**) to run Board Test's own installer for that group in a terminal.
The installer is `/opt/bc250-board-test/development/tools/install-requirements.sh`, with the group's option. When
everything in the group is there, the pill reads **Installed** and is off. **Install all** installs every group but
the development extras (`--all`).
The round arrow in the title row reads the tools again.
Each group's tools are listed beside its pill.
[BC-250 Board Test](check.md#download-and-install) lists the groups and their tools, with the tests that use each one.
Layered RPM packages are active after a restart (`systemctl reboot`). Until then, the tools of that group still show
as missing.

The group **Prime95** is `mprime`, which no test uses. [BC-250 CPU Tools](cores.md#longer-burn-in-mprime--rasdaemon)
runs its torture test for a longer burn-in. The pill installs the release that mersenne.org's download page lists at
that moment. It compares the download with the SHA-256 listed there. It installs `mprime` into `~/mprime`, with a link
in `~/.local/bin`. A newer release later shows in Nexus Deps as **Prime95 (mprime)**. Its **Update** installs it over
the old one.

## MangoHud Config

**MangoHud Config** opens MangoHud's own settings file, `~/.config/MangoHud/MangoHud.conf`, in an editor. When the
file is not there yet, **Save** makes it. **Revert** reads the file again. The boxes show you three things:

- whether the file is there
- whether MangoHud's log is on
- how many log files there are

Board Test shows a game's FPS from MangoHud's log, which MangoHud writes while the game runs. **FPS log** sets the
three lines that Board Test needs:

```ini
output_folder=/home/<you>/mangohud-logs
autostart_log=1
log_interval=500
```

When a line sets one of them already, **FPS log** changes that line where it is. It adds the others at the end.
**Save** writes the file and makes the log folder. MangoHud must be active for the game, for example with the Steam
launch option `mangohud %command%`. MangoHud writes a log file per game session. **Delete logs** removes the ones
older than 30 days. **Log folder** opens the folder. Without the log, Board Test still shows the game's name and its
CPU and GPU share.

## Fix GPU Metrics

!!! warning "Changes the board"
    Turn on sets fix-metrics and the load method in the [gpu-usage] table of the GPU governor's settings file,
    /etc/cyan-skillfish-governor-smu/config.toml, after a dated backup of it beside it, and restarts the governor
    when it runs; the governor then mounts a patched copy of gpu_metrics over the sysfs file while it runs. The
    setting stays across reboots and power offs. Nothing is written to the BIOS, the firmware or the kernel's
    arguments. Turn off sets fix-metrics back to false and restarts the governor; any earlier settings file is in
    its backups.

With **Fix GPU Metrics**, the Steam performance overlay, MangoHud and radeontop show a real GPU %. The GPU governor,
cyan-skillfish-governor-smu, measures the real GPU load to drive the clock. With `fix-metrics` on, it also writes that
load into a patched copy of `gpu_metrics`. It mounts that copy over the sysfs file.

The boxes show you three things:

- whether the governor is installed, which means its settings file is there
- whether `fix-metrics` is on
- whether the patched copy is mounted

Pick the method and click **Turn on**. When `fix-metrics` is on already, the pill reads **Apply** for another method.
The methods are these:

- `busy-flag` samples the GPU's busy bit. It is the default.
- `process` sums the programs' GPU time from `/proc/*/fdinfo`. It costs more CPU. It can stall on Proton games with
  many open files.
- `kernel` only works on a patched kernel that reports the load.

The quickfix makes the same dated backup as [BC-250 GPU Manager](gpu.md) (`config.toml.bak-YYYYMMDD-HHMMSS`). GPU
Manager's Backups page lists it. A governor that is stopped stays stopped. The governor mounts the patched copy when
it runs. Check it with `mount | grep gpu_metrics`. On some kernels the patching misbehaves. If the overlay or the
governor acts up, click **Turn off** again. A kernel that reports the load itself does not need the quickfix.

## Sensors Module

!!! warning "Changes the board"
    Turn on writes one line, options nct6683 force=true, to /etc/modprobe.d/bc250-quickfix-nct6683.conf and loads the
    nct6683 driver, which reads the board's SuperIO chip: its temperatures and fan speeds. The file stays across
    reboots and power offs, so the driver loads at every boot. Nothing is written to the BIOS, the firmware or the
    chip. Turn off removes the file; the driver stays loaded until the next boot.

**Sensors Module** makes sure a driver reads the temperatures and fan speeds of the board's SuperIO chip. The chip is
a Nuvoton NCT6686D. Board Test's test 22 and the `sensors` command of `lm_sensors` show its values. Bazzite loads the
nct6687 driver for the chip by itself since image 45.20261117. There, you do not need the quickfix. Other images may
not load that driver. The kernel's own nct6683 driver loads only when something forces it.

The boxes show you three things:

- which driver is loaded
- whether something forces nct6683 at boot
- the chip's sensors, as it reports them

**Turn on** is offered only when no driver serves the chip. A modprobe file of your own that forces nct6683 already
counts too. **Turn off** removes only the quickfix's file.

## VRM Sensors

!!! warning "Changes the board"
    Turn on copies the source of the bc250_vrm kernel module to /var/lib/bc250-quickfix/vrm, writes the service
    /etc/systemd/system/bc250-quickfix-vrm.service and starts it. The service builds the module for the running
    kernel and loads it, now and at every boot, so a new kernel gets its own build. The module reads the voltage,
    current and temperature of the CPU and GPU supply from the board's voltage regulator, through the SuperIO
    chip. When it loads it sets up the SuperIO chip's SMBus port, which stays so until the board powers off. For
    every reading it writes the regulator's page register, which selects the CPU or the GPU supply. It writes no
    voltage, current or limit. The folder and the service stay across reboots and power offs. Nothing is written
    to the BIOS or the firmware. Turn off stops the service, which unloads the module, and removes the service and
    the folder.

The board's voltage regulator knows what the CPU and the GPU draw. **VRM Sensors** gives you those values:

- the voltage, current and power of the CPU supply and of the GPU supply
- the temperature of each supply's regulators
- the 12 V input voltage

BC-250 System Overlay shows them in its **CPU rail**, **GPU rail**, **CPU VRM temp** and **GPU VRM temp** rows.
Board Test's test 22 and the `sensors` command of `lm_sensors` report them too.

The values come from a kernel module, `bc250_vrm`, which Bazzite does not include.
Its source is [Hexxeh/bc250-vrm-dkms](https://github.com/Hexxeh/bc250-vrm-dkms), unchanged, and comes with the app.
**Turn on** builds it for the running kernel and loads it, which takes a few seconds.
A service then loads it at every boot.
After a kernel update, the first boot builds the module again.
SELinux loads only a file labeled as a kernel module, so the service gives its build that label.

The boxes show you three things:

- whether the module is loaded
- whether the service loads it at boot
- whether its sensors are there

**Turn on** is offered when the module is not loaded and the kernel's build files are on the image.
When the service is there, but the module is not loaded, **Turn on** is available again.
It copies the module's source and the service's script anew, and starts the service once more.
Use it after an update of the quickfix when an earlier load failed.
When the service is on and the module is not loaded, the window names the command that shows why.
**Turn off** unloads the module and removes the service and its folder.

## Game Memory Map

!!! warning "Changes the board"
    Turn on writes vm.max_map_count = 2147483642 to /etc/sysctl.d/90-bc250-quickfix-max-map-count.conf and sets it
    now: the number of memory areas one program may map. The file stays across reboots and power offs. Nothing is
    written to the BIOS, the firmware or the kernel's arguments. Turn off removes the file and reads the system's
    settings again, so the value the other settings files give, else the kernel's own, is back.

**Game Memory Map** keeps games from crashing for lack of memory areas. `vm.max_map_count` is the number of memory
areas one program may map. Some games, and Proton, need far more than the kernel's default. Without them, they
crash. SteamOS and Bazzite set 2147483642.

The boxes show you the value now and what set it. That is the quickfix, or the system. The system means another file
in `/etc/sysctl.d`, or the image's own setting. **Turn on** is offered only when the value is lower. Board Test's test
37 reports it.

## Persistent Journal

!!! warning "Changes the board"
    Turn on makes the folder /var/log/journal, with systemd-tmpfiles, and moves the journal there: journald then
    keeps the system's logs on the disk, within its own size limits, instead of in memory only. The folder stays
    across reboots and power offs. Nothing is written to the BIOS or the firmware. Turn off works only on a folder
    this quickfix made: it moves the journal back to memory and removes the folder, with the logs in it.

**Persistent Journal** keeps the logs of a boot that crashed or froze. Without `/var/log/journal`, journald keeps the
system journal in memory only. Then the logs of a boot that crashed or froze are gone after it. Board Test's test 34
cannot read the previous boot's logs then.

The boxes show you where the journal is kept, and who made the folder. **Turn on** is offered only when the folder is
not there. **Turn off** asks first, because it removes the logs of every earlier boot.

## IOMMU Off

!!! warning "Changes the board"
    Turn on adds the kernel argument amd_iommu=off with rpm-ostree kargs, which makes a new deployment with it, and
    notes in /var/lib/bc250-quickfix/iommu.karg that the quickfix added it; from the next boot the kernel leaves the AMD
    IOMMU unused. The argument stays across reboots, power offs and Bazzite's updates. Nothing is written to the BIOS or
    the firmware. Turn off works only on an argument this quickfix added: it removes it with rpm-ostree kargs, and the
    kernel uses the IOMMU again from the next boot. Both need a reboot, which the quickfix advises and never does.

**IOMMU Off** keeps the BC-250 stable. The board's AMD IOMMU (AMD-Vi) is broken on the BC-250. A system that uses
it is unstable. When the BIOS leaves it on, the kernel argument `amd_iommu=off` keeps the kernel from using it. That
switches it off from Linux's side.

With the IOMMU off, there are no IOMMU groups. Board Test's test 23 checks for that. You can no longer pass a PCI
device to a virtual machine (VFIO) then.

The boxes show you four things:

- whether the IOMMU is on now, which means there are IOMMU groups
- whether `amd_iommu=off` is on the running kernel's command line
- whether it is on the next boot's command line (`rpm-ostree kargs`)
- who added it

**Turn on** is offered when the next boot lacks the argument and the BIOS does not have the IOMMU off already. After
**Turn on** or **Turn off**, the window says **Reboot to apply**. Restart the board with `systemctl reboot`. An
argument `amd_iommu=off` that you added yourself counts too. **Turn off** removes only the one the quickfix added.

## CPU Mitigations Off

!!! warning "Changes the board"
    Turn on adds the kernel argument mitigations=off with rpm-ostree kargs, which makes a new deployment with it, and
    notes in /var/lib/bc250-quickfix/mitigations.karg that the quickfix added it; from the next boot the kernel no longer
    guards against the CPU's speculative execution flaws (Spectre, Meltdown and the like). The argument stays across
    reboots, power offs and Bazzite's updates. Nothing is written to the BIOS or the firmware. Turn off works only on an
    argument this quickfix added: it removes it with rpm-ostree kargs, and the mitigations are back from the next boot.
    Both need a reboot, which the quickfix advises and never does.

**CPU Mitigations Off** gives games more speed. The kernel guards against the CPU's speculative execution flaws, such
as Spectre and Meltdown. These guards cost roughly 18 FPS in games on this board. The kernel argument
`mitigations=off` turns those guards off. Without them, a program could, in principle, read the memory of other
programs. Keep them on where the board runs code you do not trust. Board Test's test 24 reports the setting.

The boxes show you three things:

- whether `mitigations=off` is on the running kernel's command line
- whether it is on the next boot's command line (`rpm-ostree kargs`)
- who added it

**Turn on** is offered when the next boot lacks the argument. After a change, the window says **Reboot to apply**
(`systemctl reboot`). An argument `mitigations=off` that you or the image set counts too. **Turn off** removes only the
one the quickfix added.

## Install

The portal installs the quickfixes together with itself. When you remove the portal, it removes them too. The portal
lists no Uninstall for them.
From a checkout of the repository:

```bash
apps/quickfix/install.sh                         # the app, its launcher, a menu entry and a Desktop icon
apps/quickfix/install.sh --no-desktop-shortcut   # without the Desktop icon
apps/quickfix/install.sh --uninstall             # remove it; --purge removes its settings too
```

The launcher is `~/.local/bin/bc250-quickfix`. Without an argument, it opens the list. With a quickfix's key, it opens
that quickfix's own window, for example `bc250-quickfix tools`. The keys are `tools`, `mangohud`, `metrics`,
`sensors`, `vrm`, `mapcount`, `journal`, `iommu` and `mitigations`.

The app runs on the suite's shared Python environment.

## Files

The quickfixes use these files:

- `~/.config/MangoHud/MangoHud.conf` and `~/mangohud-logs/` are MangoHud's own settings file and its log folder.
- `/etc/cyan-skillfish-governor-smu/config.toml` is the governor's settings file. Its backups are
  `config.toml.bak-*`.
- `/etc/modprobe.d/bc250-quickfix-nct6683.conf` is there while Sensors Module is on.
- `/etc/sysctl.d/90-bc250-quickfix-max-map-count.conf` is there while Game Memory Map is on.
- `/var/log/journal/.bc250-quickfix` is there while Persistent Journal is on.
- `/etc/systemd/system/bc250-quickfix-vrm.service` is VRM Sensors' service. `/var/lib/bc250-quickfix/vrm/` holds the
  module's source and build. Both are there while VRM Sensors is on.
- `/var/lib/bc250-quickfix/iommu.karg` and `mitigations.karg` note that IOMMU Off and CPU Mitigations Off added their
  kernel argument. Each is there while its quickfix is on.

Removing the app leaves all these files as they are. To undo a quickfix, turn it off first.

## License

GPL-3.0-or-later.
