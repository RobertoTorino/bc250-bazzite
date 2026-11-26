<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-memory:</span>

# Memory Manager internals

This page explains how BC-250 Memory Manager works inside. It covers these parts:

- how the app reads and writes the VRAM split in CMOS
- how it reads and writes the GTT limit on the kernel command line
- the board dumps the CMOS layout was checked against

How you use the app is in [its chapter](../apps/vram.md).

## Where the split is stored

The firmware is AMI Aptio, with AMD's ABL for the memory setup. It keeps the memory configuration in **CMOS bank
2**. That is battery-backed RAM behind the I/O ports **0x72** (index) and **0x73** (data). Bank 1 (0x70/0x71) holds
the RTC and the usual CMOS settings. The kernel's `cmos_nvram0` device only covers bank 1. So the app reaches bank 2
through `/dev/port`, where file offset N is I/O port N.

The memory block is 28 bytes at 0x90-0xAB, little-endian.

| Offset | Size | Field | Allowed range |
|---|---|---|---|
| 0x90 | 4 | Signature | see below |
| 0x94 | 2 | Checksum: 16-bit sum of the bytes 0x96-0xAB | |
| 0x96 | 2 | ClockSpeed (MHz) | 450-1750 |
| 0x98 | 1 | tCL | 8-33 |
| 0x99 | 1 | tRAS | 21-58 |
| 0x9A | 1 | tRCDRD | 8-27 |
| 0x9B | 1 | tRCDWR | 8-27 |
| 0x9C | 1 | tRCAb | 40-90 |
| 0x9D | 1 | tRCPb | 0-11 |
| 0x9E | 1 | tRPAb | 8-27 |
| 0x9F | 1 | tRPPb | 0-11 |
| 0xA0 | 1 | tRRDS | 4-12 |
| 0xA1 | 1 | tRRDL | 4-12 |
| 0xA2 | 1 | tRTP | 0-14 |
| 0xA3 | 1 | tFAW | 4-34 |
| 0xA4 | 2 | tREF | any |
| 0xA6 | 2 | RFCPb | any |
| 0xA8 | 2 | tRFC | any |
| 0xAA | 2 | UMA_SIZE: the split in MB, in 16 MB steps | 256-16383 |

Signatures:

| Value | Bytes | Name | Meaning |
|---|---|---|---|
| 0x4C424124 | `24 41 42 4C` ("$ABL") | ABL | written by the firmware |
| 0x42435041 | `41 50 43 42` | LINUX_TOOL | written by a Linux tool (bc250_memcfg, this app) |
| 0x42534D43 | | CMOS_BAD | A note the firmware leaves in the field when a boot went wrong. This one says the firmware found CMOS bad. |
| 0x46544457 | | WATCH_DOG_TIMER_FIRED | The firmware's watchdog fired during the memory setup. The owner's board showed it on 01-11-2026. The values were intact, and the board booted as before. |
| 0x454B4843 | | CHECKSUM_ERROR | the block's checksum was wrong |
| 0x45474953 | | SIGNATURE_ERROR | the block's signature was wrong |

The layout, the ranges and the signatures come from
[fanoush/bc250_memcfg](https://github.com/fanoush/bc250_memcfg) (MIT), which credits an earlier tool by ethkey.

## The layout on two boards

Bank 2 was read on two BC-250 boards. Both have BIOS P5.00 05/03/2022, kernel lockdown off and a 6 GB split. The
reads only set the index port and read the data port.

The memory block is byte for byte the same on both:

```
090  24 41 42 4C 10 04 D6 06 18 34 1B 13 4E 00 1A 00
0A0  08 08 02 20 F7 26 D2 00 18 01 00 18
```

| Field | Board 1 | Board 2 |
|---|---|---|
| Signature | 0x4C424124 (ABL) | 0x4C424124 (ABL) |
| Checksum stored / computed | 0x0410 / 0x0410 | 0x0410 / 0x0410 |
| ClockSpeed | 1750 MHz | 1750 MHz |
| tCL, tRAS, tRCDRD, tRCDWR, tRCAb | 24, 52, 27, 19, 78 | 24, 52, 27, 19, 78 |
| tRCPb, tRPAb, tRPPb | 0, 26, 0 | 0, 26, 0 |
| tRRDS, tRRDL, tRTP, tFAW | 8, 8, 2, 32 | 8, 8, 2, 32 |
| tREF, RFCPb, tRFC | 9975, 210, 280 | 9975, 210, 280 |
| UMA_SIZE | 6144 MB | 6144 MB |
| `mem_info_vram_total` | 6442450944 (6 GiB) | 6442450944 (6 GiB) |

Every timing is inside its range, and UMA_SIZE matches the split the kernel got.

The rest of bank 2:

- **0x00-0x0F and 0x40-0x46** are the same on both boards (`FF 00 00 00 00 00 00 00 98 42 EE 7D FF 30 3F 00` and
  `00 00 01 02 56 90 F0`). The firmware keeps something else there.
- **0x47-0x7F** is zero on both.
- **0x10-0x3F, 0x80-0x8F and 0xAC-0xFF** are mostly `FF`, with single bits cleared in different places on each
  board. This is unused memory that was never written.

So nothing outside 0x90-0xAB belongs to the memory configuration, and the app never writes there. The tests use
both reads as fixtures (`apps/vram/tests/dumps.py`).

## Reading and writing

The GUI runs as the user. Everything that touches CMOS is in `vram_manager/cmos.py`, which pkexec runs as
root with the system Python in isolated mode:

```
pkexec /usr/bin/python3 -I .../vram_manager/cmos.py --read
pkexec /usr/bin/python3 -I .../vram_manager/cmos.py --set-uma 6144
```

`-I` keeps the user's environment and the current folder out of the root process. The helper only needs the
standard library. It prints one JSON object: `{"ok": true, ...}` or `{"ok": false, "error": "..."}`.

Before it opens `/dev/port`, the helper checks that the DMI board name is `AMD BC-250` and that kernel lockdown is
off.

`--set-uma MB`:

1. Checks the split. It must be a multiple of 16 MB, from 512 to 10240 MB. Above 10 GB the system keeps less
   than 6 GB.
2. Reads the block and checks that it can be trusted. The checksum must match, and every timing must be in range.
   UMA_SIZE must be 256-16383, and the signature one of the six. If the block fails a check, the helper writes
   nothing. bc250_memcfg writes back whatever it read. So with that tool, a damaged block would reach the firmware
   with its wrong timings. The block's own numbers decide, case by case and not by a generic rule (owner,
   01-11-2026). A block with a firmware note in the signature field and intact numbers is written. Writing it
   replaces the note. A read shows the note as a `note` line. Only a signature that is none of the six makes the
   helper refuse. Such a block may not be a memory block at all.
3. Builds the new block. It keeps the same timings and gets the new UMA_SIZE, the LINUX_TOOL signature and a new
   checksum.
4. Writes the whole block from 0x90 upwards, as bc250_memcfg does, so the bytes the firmware finds are the same as
   with that tool.
5. Reads the block back and compares all 28 bytes.

It answers with the block before and after. The GUI saves both in `backups/cmos-<time>.json`. `--read` answers
with the decoded block and all 256 bytes of bank 2. The GUI shows them and saves them as
`backups/cmos-dump-<time>.txt`.

## After a reboot

The firmware reads the block at boot. The GUI keeps the split it wrote with the boot ID it wrote it in
(`/proc/sys/kernel/random/boot_id`). At the next boot it compares `mem_info_vram_total` with that split and says
whether the kernel got it. Undo writes back the UMA_SIZE of the block before the last change.

## The figures without root

`vram_manager/system.py` reads, without root:

| Figure | Source |
|---|---|
| Split | `/sys/class/drm/card*/device/mem_info_vram_total` |
| GTT | `/sys/class/drm/card*/device/mem_info_gtt_total` |
| System RAM | `MemTotal` in `/proc/meminfo` |
| TTM limit | `/sys/module/ttm/parameters/pages_limit` (4 KiB pages), and its value on `/proc/cmdline` |
| Swap | `/proc/swaps` (zram and disk swap) and `/sys/module/zswap/parameters/enabled`, as Board Test's test 14 |
| Swappiness | `/proc/sys/vm/swappiness` |

amdgpu sizes GTT from the TTM limit and caps it at the RAM on this APU. `amdgpu_ttm_init` logs this as "Capping
GTT to …M to not exceed available system memory". When the split is smaller than GTT, amdgpu also prefers GTT for the
GPU's allocations (`apu_prefer_gtt`).

## The swap layout

`vram_manager/swap.py` holds the three layouts and is also the root helper that writes one, run through pkexec with
the system Python like `cmos.py`. A layout is a set of the app's own files, so the image's files stay untouched.

| File | What it does |
|---|---|
| `/etc/systemd/zram-generator.conf.d/90-bc250-memory-manager.conf` | `[zram0]` with `zram-size` and `compression-algorithm`. Size 0 discards the device, which is the zswap layout. |
| `/etc/sysctl.d/90-bc250-memory-manager.conf` | `vm.swappiness` |
| `/etc/tmpfiles.d/bc250-memory-manager-zswap.conf` | `w` lines that write zswap's `compressor` and `enabled` under `/sys/module/zswap/parameters` |
| `/etc/systemd/system/var-swap-swapfile.swap` | The swap file's unit, enabled for `swap.target` |

The helper starts and stops nothing. zram-generator, sysctl, tmpfiles and the swap unit read the files at the next
boot. Bazzite's kernel arguments have `zswap.enabled=0`. The tmpfiles line turns zswap on after that, so the layout
needs no new deployment.

The helper makes the swap file before it writes any file in `/etc`. So a failure there changes nothing. On btrfs,
`/var/swap` is a subvolume and `btrfs filesystem mkswapfile` makes the file. That turns copy-on-write off for it.
On another file system, `fallocate` and `mkswap` make it. With SELinux on, the file gets the `swapfile_t` label,
by a `semanage fcontext` rule and `chcon`. systemd's `swapon` runs as `fsadm_t` and may not use a file with
another label. A swap file that is in `/proc/swaps` is never resized or deleted.

`read_setup()` reads the written layout back from the files, without root. The window compares it with the layout
picked, and Apply is off while they are equal.

## The memory guard

`vram_manager/guard.py` holds the two guards and is the root helper that writes one, run through pkexec like
`swap.py`. Bazzite's own guard comes from the image:

- `/usr/lib/systemd/oomd.conf.d/10-oomd-defaults.conf` sets `DefaultMemoryPressureDurationSec=20s`.
- The `slice.d` drop-ins of the system and the user manager set `ManagedOOMMemoryPressure=kill` at 80%.
- No unit has `ManagedOOMSwap`, so systemd-oomd does not watch the swap.

The suite's guard is four files of the app's own:

| File | What it does |
|---|---|
| `/etc/systemd/oomd.conf.d/90-bc250-memory-manager.conf` | `SwapUsedLimit=90%`, `DefaultMemoryPressureLimit=60%`, `DefaultMemoryPressureDurationSec=10s` |
| `/etc/systemd/system/-.slice.d/90-bc250-memory-manager.conf` | `ManagedOOMSwap=kill` for the whole board |
| `/etc/systemd/system/user@.service.d/90-bc250-memory-manager.conf` | `ManagedOOMMemoryPressure=kill` at 60% for the session |
| `/etc/systemd/user/slice.d/90-bc250-memory-manager.conf` | The same for the session's slices, in place of the image's 80% |

The helper reloads systemd and restarts systemd-oomd. The window then reloads the user manager, which hands its
slices' settings to systemd-oomd again. `oomctl` shows the limits systemd-oomd uses. `read_guard()` reads the written
guard back without root. Only the four files exactly as the app writes them count as the suite's guard.

## The sessions

`vram_manager/watch.py` is the watcher, and `vram_manager/service.py` writes its user unit,
`bc250-memory-watch.service`. The window writes, enables and starts it when recording is turned on, and removes it
when it is turned off. The guard does not touch it. The watcher needs no Qt. It runs from the app folder with the
suite's Python.

Every two seconds the watcher reads these:

- `/proc/meminfo` for the RAM and the swap in use
- `mem_info_gtt_used` for the RAM the GPU borrows
- `mem_info_vram_used` for the VRAM in use
- `full avg10` in `/proc/pressure/memory`
- the `cpu` line of `/proc/stat`, for the CPU load since the last look, with idle and iowait as idle
- each unit under the user manager's `app.slice`, with `memory.current`, `memory.swap.current` and `memory.events`

The watcher finds `app.slice` from its own control group in `/proc/self/cgroup`. A unit's name for people is a Steam
shortcut's `AppName` by its `appid`, a Steam game's `appmanifest_<id>.acf`, or the `Name` of the app's desktop file.

When a unit is gone, the watcher looks in the journal since the session started. systemd-oomd logs `Marked … for
killing due to memory used … and swap used …` for the swap and `Memory pressure for … is …` for the pressure. The
kernel logs `oom-kill:… task_memcg=…` with the unit's control group. A unit's `oom_kill` count in `memory.events` also
tells a kernel kill. When nothing ended it, an entry of `systemd-coredump` with `COREDUMP_USER_UNIT` set to the unit
means a crash. The sessions go to `sessions.jsonl`, and the open ones to `sessions-open.json`. An open session
from another boot ID is written as "Board restarted while it ran".

The watcher also writes the Programs window's records. Each minute's peaks go to `history.jsonl`, which keeps 24
hours. Each program's runs, peak, time-weighted average and kills go to `programs.json`, keyed by its name. A unit
named `steam-app<number>`, or Steam's own unit, is marked as a game and can never be closed.

The programs checked in the Programs window are in `close-for-games.json`. When a new `steam-app<number>` unit appears
after the watcher's first look, the watcher runs `systemctl --user --no-block stop` on each checked unit that runs.
systemd sends SIGTERM to the unit's processes. Each stop goes to `close-for-games.log`, and the session ends as
"Closed for a game".

While a game runs, the watcher reads `journalctl -b -t systemd-coredump` since its last look. This line comes at
the crash, before the dump:

```
Process <pid> (<name>) of user <uid> terminated abnormally with signal <n>/<NAME>, processing...
```

The watcher finds the game whose control group holds the PID and notifies at once. When the `full avg10` pressure
stays at `STALL_PERCENT`, 40%, for `STALL_S`, 10 seconds, the watcher runs `systemctl --user kill --signal=SIGKILL`
on each running game. The session then ends as a memory stall. Notifications go through `notify-send`. The one after
a stall has a button. A shell waits for it and then starts the app.

A session and a minute's point keep the peaks of the VRAM in use and the CPU load as well. Records from before keep
reading, with 0 for both.

## The learning steps

The rules are in `vram_manager/learn.py`, which needs no Qt. Each step's row comes from `vram_manager/steps.py`, a
copy of Core Unlock's `StepRow` on core's theme. The autostart entry and the restart come from
`vram_manager/resume.py`, as in Core Unlock.

`learn.json` holds the rounds. Each round has these fields:

- `since`: when its setting was written
- `settings`: the split, the next boot's GTT limit, the swap layout and the guard it runs with
- `boot`: the boot ID it was written in, empty when it took effect at once
- `change`: the change it tries, or none for the start point and after an undo
- `verdict`: empty, `kept` or `undone`

`restart_boot` is the boot ID a written change waits in. While the board runs that boot, the step offers the restart
and the autostart entry is there. A later boot clears both.

A round's sessions are the recorded games that began after its `since` and before the next round's. Sessions of its
`boot` ran the old setting and do not count. The baseline is the last round with the start point, a kept change or
the settings after an undo. Its sessions are those of every such round with the same settings, so an undo goes on
with what the earlier rounds recorded.

`propose()` needs three baseline sessions, or one that ended for lack of memory or a freeze. It proposes the first of these that was not tried yet:

- the next zram size, with the running compressor and `vm.swappiness`, when a session ended with the swap full
- `gtt_pages()`, the RAM less 2 GiB, after a kernel kill with the GPU borrowing half the RAM or more
- the suite's guard, after a kernel kill or a freeze with Bazzite's guard

`compare()` takes the games played in both rounds. Fewer endings for lack of memory or a freeze, as a share of the
sessions, decide first. The peak wait for memory decides next, with a margin of `WAIT_MARGIN`, 5 points. Otherwise,
the verdict is the same, and the window advises the undo.

## The GTT limit on the kernel command line

`vram_manager/kargs.py` reads and changes `ttm.pages_limit` in the next boot's kernel arguments with rpm-ostree.
rpm-ostree keeps the arguments per deployment.

```
rpm-ostree kargs --deploy-index=0                                           # the next boot's arguments, no root
rpm-ostree kargs --append-if-missing=ttm.pages_limit=N --unchanged-exit-77  # the argument is not there yet
rpm-ostree kargs --replace=ttm.pages_limit=N --unchanged-exit-77            # it is there
rpm-ostree kargs --delete=ttm.pages_limit=OLD --unchanged-exit-77           # the kernel default: the whole argument
```

The `--delete` command names the whole argument, key and value. On the owner's board,
`--delete-if-present=ttm.pages_limit` with the key alone matched nothing (01-11-2026). rpm-ostree answered
"unchanged" within a second and wrote no deployment. The app took that for done. So the app checks every change.
It reads the next boot's arguments again, and they must hold what was asked. Otherwise, it reports that nothing
changed, with the command to run by hand.

A change makes a new deployment with the argument. When a staged update waits, the deployment goes on top of it.
rpm-ostree's daemon asks polkit for the change. The polkit action is `org.projectatomic.rpmostree1.bootconfig`, with
`auth_admin_keep` on Bazzite. So the desktop's password dialog appears by itself. The app runs rpm-ostree as the
user, without pkexec. Exit code 77 means nothing changed and counts as done.

The window runs every command through `privileged.run_command`. That is a QProcess with its own event loop, so the
window keeps painting under the password dialog. A command that is not installed answers without starting. The
window stops a command that does not end in ten minutes. One change took 84 seconds on a board with 11 layered
packages. rpm-ostree puts those packages on the new deployment again.

The value is in 4 KiB pages (256 per MiB). The app offers these presets:

- 3014656 (11.5 GiB), Board Test's value
- 4194304 (16 GiB), all the RAM with any split
- the kernel default, which removes the argument

amdgpu then makes a GTT of `min(limit, RAM)`. The memory map's preview shows that with `gtt_ceiling()`.

"Waiting for a reboot" is not a setting. It means the next boot's value differs from `/proc/cmdline`. So a limit
set by hand with `rpm-ostree kargs` shows the same way. The settings keep only what the app itself wrote. That is
`pending_ttm`, with the boot ID. The app uses it for the message after the restart. The message says that the
command line got the limit, or that the board started another deployment.
