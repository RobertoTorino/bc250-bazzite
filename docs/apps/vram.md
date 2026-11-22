<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Memory Manager](../assets/vram/bc250-memory-manager.webp){ .app-logo }

# BC-250 Memory Manager

!!! warning "Changes the board"
    The app writes the VRAM split into the board's CMOS: the firmware's own memory block of 28 bytes in bank 2,
    with its checksum, and never a byte outside it. The firmware reads the split at the next boot. CMOS is kept
    by the board's battery, so the split stays across reboots and power offs until it is written again or the
    CMOS is cleared with the jumper or the battery, which brings the firmware's 512 MB back. The GTT limit is a
    kernel argument, set with rpm-ostree kargs in the next deployment. Nothing is written to the BIOS itself,
    the firmware or the real-time clock, and the app refuses to write when the block's signature or checksum
    does not match or the kernel is locked down. Undo writes the previous split back, and the Default profile
    writes 512 MB and removes the kernel argument; both take effect after a reboot. The swap layout is a few
    files of the app's own in /etc. They are a zram-generator drop-in, a sysctl file, a tmpfiles line for zswap
    and a swap unit. The zswap layout also makes the swap file /var/swap/swapfile. They stay across reboots and
    power offs. Nothing is started or stopped before the next boot. Bazzite's own layout removes the files, and
    Delete swap file removes the swap file.

BC-250 Memory Manager sets up the memory of the **AMD BC-250** on **Bazzite**. It sets three things:

- the **VRAM split** in the board's CMOS
- the **GTT limit** on the kernel command line
- the **swap layout**

It also shows the memory figures that go with them, such as the GTT, the TTM limit, the system RAM and the swap.

## The split, GTT and RAM

The BC-250 has 16 GB of GDDR6, shared by the CPU and the GPU. At boot the firmware divides it in two parts:

- **The split (VRAM):** the part the GPU keeps for itself, from 512 MB up.
- **System RAM:** the rest. Linux and the games run in it.

The GPU can also borrow system RAM on top of the split. That is the **GTT**. amdgpu sizes it from
`ttm.pages_limit` on the kernel command line. By default, the limit is half the RAM. amdgpu never makes the GTT
larger than the RAM.

A small split leaves the most RAM, and the GPU grows into GTT when it needs more. But the screen's framebuffers
must fit in the split itself. When a game fills a 512 MB split, the GPU cannot show the next frame, and the session
ends. Board Test reports this as a framebuffer pin failure (test 37). A 6 GB split fixes it. That is why the app
marks 6 GB as recommended for games.

## Using it

The top row shows what the kernel got at this boot:

- the **VRAM split**
- the **GTT**
- the GTT limit, **ttm.pages_limit**
- the **system RAM**
- the **swap** layout

The ttm.pages_limit box is marked default when the limit is not on the command line. When the limit is above the
RAM, the GTT box says so. The GTT is then all the RAM, and a higher limit has no effect. While a new limit waits for
a restart, the ttm.pages_limit box's caption names it ("next boot 16.0 GiB"). Hover over a box for the details.

Under the row is `vm.swappiness`. It says how readily Linux moves pages out of the RAM into swap, from 0 to 200. 60
is the kernel's default. A higher value prefers swap to the file cache, which is usual with zram. **Swap layout**
sets it for the next boot.

The **memory map** under it draws the 16 GB as one bar. It follows the memory live, every two seconds. The bar
shows these parts:

- **The split:** the VRAM in use and the VRAM that is free.
- **The system RAM:** what the GPU borrows from it now (GTT), what zram or zswap take, what Linux and the apps use,
  and what is still available.
- **What the firmware keeps** at boot, the last part of the bar.

The bracket under the RAM is the GTT limit. It shows how much RAM the GPU may borrow, and what the TTM limit does to
it. The line under the bracket names the parts that are too narrow for a label. Under the bar is the swap. For zram,
it shows the pages zram holds and the RAM they cost, in light and dark. It also shows whether zswap or disk swap is
in use. Hover over any part to see what it is.

When you pick a split under **New split**, or a limit under **Next boot**, the map draws the next boot under the
bar. It shows the new split, the RAM that leaves, and about how much the GPU may then borrow.

- **New split** and **Apply…:** Pick a split and apply it. The app asks first and shows how much RAM the system
  keeps. Then it asks for your password. The status next to the title turns to **Reboot to apply**. Apply is off
  while the split you picked is the one the board has, or the one that waits for the restart.
- **Reboot.** After the restart the app says whether the kernel got the new split.
- **Undo:** Writes back the split from before the last change. This also takes effect after a restart.
- **Read CMOS…:** Shows the memory block in CMOS and the whole of CMOS bank 2. For the block, it shows:
    - the signature
    - the checksum
    - the split
    - the memory timings

  It saves the same text as a dump. This only reads.

Only the split changes. The memory timings in the same block stay as they are.

## The GTT limit

The GTT limit is how much RAM the GPU may borrow on top of the split. amdgpu takes it from `ttm.pages_limit` on
the kernel command line, in 4 KiB pages. Without the argument, the kernel takes half the RAM. Whatever the argument
says, the GTT never grows past the RAM. Take a 6 GB split with 9.4 GB of RAM. A limit of 11.5 GiB already means all
the RAM, and a higher one changes nothing. The argument matters with a small split. With 512 MB, the kernel's default
stops the GPU at half of the 15 GB of RAM.

The limit does not fix the framebuffer pin failures (Board Test, test 37). Those need a larger split.

Under **GTT limit on the kernel command line**:

- **Next boot** and **Apply…:** Pick a limit and apply it. Apply is off while the limit you picked is already the
  next boot's. The app asks first and says what the GTT will be after the restart with this split. With a limit
  above the RAM, the GTT stays where it is, since the kernel caps it at the RAM. Then rpm-ostree asks for your
  password and writes a new deployment with the argument. That takes a minute or two, since rpm-ostree puts the
  layered packages on the new deployment again. Meanwhile, the status next to the title says **Writing…**, and the
  note under the row counts the seconds. When it is done, the app says so, and the status turns to **Reboot to
  apply**. The restart is yours to do. The app never restarts the board. Use `systemctl reboot`, or the menu.
  The choices:
    - **Kernel default: half the RAM.** The app removes the argument.
    - **11.5 GiB, the suite's value (Board Test, test 37).** What Board Test advises. With a 6 GB split, it is all
      the RAM.
    - **16 GiB: all the RAM, whatever the split.** The kernel caps it at the RAM. So this is the most the GPU can
      borrow with any split.
    - A limit set by hand that is none of these appears as a fourth choice, **as set now**.
- **Reboot.** After the restart the app says whether the kernel got the new limit. When the board started another
  deployment (a rollback), it says that instead.

The split and the limit are independent. You apply each on its own, and either can wait for the restart. The
round **i** at the end of each row explains the split or the limit, with a link to this chapter.

## Profiles

Under **Profiles: the split and the GTT limit at once**, two buttons set both:

- **Default profile…:** The firmware's 512 MB split and the kernel's GTT limit, half the RAM. A board runs this
  without any change, as after a CMOS clear on a kernel command line without `ttm.pages_limit`.
- **Games profile…:** The 6 GB split that prevents the framebuffer pin failures (Board Test, test 37), and the
  11.5 GiB limit. The limit is all the RAM with that split. The suite's boards run this profile.

A profile writes only what differs from the board. The split goes to CMOS. The limit goes to the next boot's kernel
arguments. The profile asks once and names what it will write. Each part it writes then asks for your password. A
profile the board already has is off. Both take effect after you restart the board, which stays yours to do.

## The swap layout

Swap is where Linux puts pages that do not fit in the RAM.
Under **Swap layout** you pick how the board swaps from the next boot on.
Each of the three layouts is a complete setup:

- **Bazzite's own: zram as the image sets it.** The app removes its own files.
- **zram with your size and compressor.** Swapped-out pages stay in the RAM, compressed.
- **zswap with a swap file on disk, zram off.** Linux first compresses the pages in the RAM. The oldest move to a
  swap file on the disk.

zram is fast, but what it holds still takes RAM.
zswap with a swap file holds more than the RAM can, at the cost of disk writes.

The second row belongs to the layout you picked:

- **zram size:** half the RAM, the RAM, one and a half times the RAM or twice the RAM. The size follows the RAM at
  every boot, so it follows a new split by itself.
- **Swap file:** 4, 8 or 16 GiB, or as large as the RAM. The file is `/var/swap/swapfile`.
- **Compressor:** For zram, the ones the board's zram device offers. For zswap, zstd, lz4 or lzo.
- **vm.swappiness:** How readily Linux swaps, from 0 to 200. The app proposes 180 for zram and 60 for zswap.

**Apply…** asks first, names what it will write, and then asks for your password.
Apply is off while the layout you picked is the one already written.
The status next to the title turns to **Reboot to apply**.
Nothing changes before you restart the board, and the restart is yours to do.
After the restart the app says whether the board's swap is the layout you applied.

A swap file needs room on the disk.
When the size you picked does not fit, Apply is off and the line under the row says why.
The size of a swap file that is in use cannot change.
Apply another layout and restart first, then apply the new size.

After you leave the zswap layout, the swap file stays on the disk.
**Delete swap file…** then appears beside Apply and removes it.
The button is off until the board has restarted, because the file is in use until then.

The round **i** at the end of the row explains the terms, with a link to this chapter.

## When it refuses

The app reads and writes CMOS only when all the checks below pass. Otherwise, the buttons are off, or the app stops
before it changes anything. Either way, it gives the reason.

- **The board is a BC-250.** Other boards keep other things at the same place in CMOS.
- **The kernel has no lockdown.** Lockdown blocks direct port access. Secure Boot usually turns it on.
- **The memory block can be trusted.** Its checksum matches, and every timing is in its normal range. The app never
  writes a damaged block back, because the firmware would then start the memory with wrong timings.

The firmware sometimes leaves a note in the block's signature. For example, its watchdog fired at a boot, or it found
a wrong checksum. Such a note is no reason to refuse when the numbers are intact. **Read CMOS…** shows it as a note,
and the next write replaces it.

The GTT limit needs rpm-ostree, which reads and writes the kernel arguments. Another Linux may have no rpm-ostree.
Without it, the **Apply…** of the limit is off, with the reason. The same holds while the app cannot reach the
rpm-ostree daemon. While Bazzite's updater runs, rpm-ostree refuses with "transaction in progress". Wait for the
update to finish and apply again.

After every change the app reads the next boot's arguments back. When they do not hold the limit you asked for, the
app says so. It gives the command to run by hand, and nothing counts as written.

## Undoing a change

The split:

- **In the app:** Undo, then restart.
- **Without the app:** clear CMOS with the jumper on the board, or take the battery out for a minute. The firmware
  then starts with its own default split.

The GTT limit:

- **In the app:** pick the limit you had before, or the kernel default, and apply it. Then restart.
- **Without the app:** run `rpm-ostree kargs --delete=ttm.pages_limit=N`, with the value `rpm-ostree kargs`
  prints, and restart. `rpm-ostree rollback` also undoes it, together with everything else in that deployment.
  Clearing CMOS does not touch it.

The swap layout:

- **In the app:** pick **Bazzite's own: zram as the image sets it**, apply it and restart. Then use
  **Delete swap file…** when a swap file is left.
- **Without the app:** remove the files below with `sudo rm`. When the swap unit is there, run
  `sudo systemctl disable var-swap-swapfile.swap` first. Then restart.

## Files

- `~/.config/bc250-memory-manager/bc250-memory-manager.ini`: the pending changes and the split to undo to. The
  pending changes are the split, the GTT limit and the swap layout.
- `~/.local/share/bc250-memory-manager/backups/`: the CMOS block before and after every change
  (`cmos-<time>.json`), and every CMOS read (`cmos-dump-<time>.txt`).

- `/etc/systemd/zram-generator.conf.d/90-bc250-memory-manager.conf`: zram's size and compressor, or size 0 for
  the zswap layout.
- `/etc/sysctl.d/90-bc250-memory-manager.conf`: `vm.swappiness`.
- `/etc/tmpfiles.d/bc250-memory-manager-zswap.conf`: turns zswap on at boot, with its compressor.
- `/etc/systemd/system/var-swap-swapfile.swap`: the swap file's unit.
- `/var/swap/swapfile`: the swap file.

How the app reads and writes CMOS: [Memory Manager internals](../development/memory-manager.md).

## Install

Install it from the BC250 Bazzite Suite portal, or from a clone or release folder, as your own user:

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
./install.sh --uninstall             # remove the app; keeps its settings and CMOS backups
./install.sh --uninstall --purge     # also remove its settings and CMOS backups
```

Reading and writing CMOS needs `pkexec` and the system `python3`. The GTT limit needs `rpm-ostree`. Bazzite has all
three. Removing the app changes neither the split in CMOS nor the kernel arguments.

## License

GPL-3.0-or-later. See [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/vram/LICENSE).
The CMOS layout comes from [fanoush/bc250_memcfg](https://github.com/fanoush/bc250_memcfg) (MIT).
