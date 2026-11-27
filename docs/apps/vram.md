<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Memory Manager](../assets/vram/bc250-memory-manager.webp){ .app-logo }

# BC-250 Memory Manager

!!! warning "Changes the board"
    The app writes the VRAM split into the board's CMOS. It writes only the firmware's own memory block of 28 bytes in
    bank 2, with its checksum, and never a byte outside it. The firmware reads the split at the next boot. The board's
    battery keeps the CMOS. So the split stays across reboots and power offs until it is written again, or until the
    CMOS is cleared. A fresh install of Bazzite does not reset it. Clearing the CMOS with the jumper or the battery
    brings the firmware's 512 MB back. The GTT limit
    is a kernel argument, set with rpm-ostree kargs in the next deployment. Nothing is written to the BIOS itself, the
    firmware or the real-time clock. The app refuses to write when the block's signature or checksum does not match. It
    also refuses when the kernel is locked down. Undo writes the previous split back. The Default profile writes 512 MB
    and removes the kernel argument. Both take effect after a restart. The swap layout is a few files of the app's own
    in /etc. They are a zram-generator drop-in, a sysctl file, a tmpfiles line for zswap and a swap unit. The zswap
    layout also makes the swap file /var/swap/swapfile. They stay across reboots and power offs. Nothing is started or
    stopped before the next boot. Bazzite's own layout removes the files, and Delete swap file removes the swap file.
    The memory guard is four systemd-oomd drop-ins of the app's own in /etc. They take effect at once, because
    systemd-oomd restarts with them. They stay across reboots and power offs. Bazzite's own guard removes them.
    Recording is a user service that writes the sessions in the app's own folder. The app turns it on and off without a
    password. A learning step that needs a restart restarts the board after a countdown of 15 seconds. Until that
    restart, an autostart entry of the app's own opens the window after the login. The app removes it after the restart.
    While a game runs and the board stalls for memory, the recording service ends the game with SIGKILL.

BC-250 Memory Manager sets up the memory of the **AMD BC-250** on **Bazzite**. It sets four things:

- the **VRAM split** in the board's CMOS
- the **GTT limit** on the kernel command line
- the **swap layout**
- the **memory guard**, which ends a program before the board freezes

It also shows the memory figures that go with them, such as the GTT, the TTM limit, the system RAM and the swap.
It records how much memory each game needed, and how it ended. From those records, five steps learn the settings
that suit the games you play.

## The split, GTT and RAM

The BC-250 has 16 GB of GDDR6, shared by the CPU and the GPU. At boot the firmware divides it in two parts:

- **The split (VRAM):** the part the GPU keeps for itself, from 512 MB up.
- **System RAM:** the rest. Linux and the games run in it.

The board keeps the split in its CMOS, not on the drive. So a fresh install of Bazzite leaves the split as it
was. It does remove the GTT limit, which is a kernel argument.

The GPU can also borrow system RAM on top of the split. That is the **GTT**. amdgpu sizes it from
`ttm.pages_limit` on the kernel command line. By default, the limit is half the RAM. amdgpu never makes the GTT
larger than the RAM.

A small split leaves the most RAM, and the GPU grows into GTT when it needs more. But the screen's framebuffers
must fit in the split itself. When a game fills a 512 MB split, the GPU cannot show the next frame, and the session
ends. Board Test reports this as a framebuffer pin failure (test 37). A 6 GB split fixes it. That is why the app
marks 6 GB as recommended for games.

## Learning the settings

The window has three tabs under its header. **Learning** has five steps. **Advanced** has each setting on its own,
as described below. **Log** lists what the recording kept, as described under [Log](#log). The window is as high as the Learning tab. The current step has a frame and its pill on its row. The line under the title
says what to do. Done steps have a green check mark.

1. **Start point:** **Write** writes the Games profile, with the 6 GB split and the 11.5 GiB GTT limit. It also brings
   back Bazzite's own swap layout and memory guard, and turns on recording. It writes only what differs from the
   board. It asks once, and each part asks for your password.
2. **Restart:** **Restart** restarts the board after a countdown of 15 seconds. **Restart now** does not wait, and
   **Cancel** stops the countdown. The window opens again after you log in. The step is done at once when nothing
   waits for a restart.
3. **Play and record:** Play your games as usual. The window can stay closed. After 3 game sessions, the step is
   done. When a game runs out of memory or freezes the board, the step is done at once. The table under the steps
   shows the sessions so far. Only games count, not other programs.
4. **Try one change:** The app proposes one change, from what it measured. The table under the steps shows the
   measurements. **Write** writes the change, and the board restarts after the countdown.
5. **Play and compare:** Play the same games again. The app compares the two rounds after 3 sessions. It does so
   sooner when each game that ran out of memory has been played again. **Keep**
   keeps the change. **Undo** writes back the setting from before, and the board restarts after the countdown. The
   pill on the step is the one the app advises. The other one is in the bottom row.

Then step 4 comes again with the next change. When nothing measured asks for a change, a green bar says **Done. Your
board already runs these settings. They stay after a restart.** These settings are the Learned profile. You have
nothing to save, because each step wrote its settings to the board. A table compares the start point with the
Learned profile, with the reason for each change. When no change stayed, the line under it says so. Keep playing.
Recording stays on. When a game runs out of memory again, step 4 proposes a new change.

What points to a change, in this order:

- **zram one size up:** a session ended with the swap full, or the board froze or stalled with the swap full.
- **A GTT limit of the RAM less 2 GiB:** a game ran out of memory while the GPU borrowed half the RAM or more.
- **The suite's memory guard:** the kernel ended a program, or the board froze, with Bazzite's guard.

The app tries each change once. A larger zram keeps the compressor and `vm.swappiness` the board runs. The split
stays at 6 GB, because nothing measured yet tells when another split is better.

How the app compares two rounds:

- It counts only the games played in both rounds. Step 5 names a game you have not played again yet.
- A round is better when fewer of its sessions ended for lack of memory or a freeze.
- When those are equal, a round is better when the peak wait for memory is 5 points lower.
- Otherwise, the change is no better, and the app advises you to undo it.

The CPU load is in the tables for context only. It never decides anything.

The header shows the split, the GTT limit and the swap of this boot, whether recording is on, and the round.
**Start over** deletes the rounds and their verdicts, and goes back to step 1. The recorded sessions stay, and so
do the board's settings. **Programs** opens the memory over time.

## Using it

The **Advanced** tab shows each setting on its own. The top row of the window shows the **VRAM split**,
the GTT limit, **ttm.pages_limit**, and the **swap** layout that the kernel got at this boot. Above the memory map
are the **GTT** and the **system RAM**.

The GTT limit box is marked default when the limit is not on the command line. When the limit is above the RAM,
the GTT box says so. The GTT is then all the RAM, and a higher limit has no effect. While a new limit waits for a
restart, the GTT limit box's caption names it ("next boot 16.0 GiB"). Hover over a box for the details.

Beside them is `vm.swappiness`. It says how readily Linux moves pages out of the RAM into swap, from 0 to 200. 60
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

Under **Profiles: the split, the GTT limit, the swap and the guard at once**, three buttons set several settings:

- **Default profile…:** The firmware's 512 MB split and the kernel's GTT limit, half the RAM. A board runs this
  without any change, as after a CMOS clear on a kernel command line without `ttm.pages_limit`.
- **Games profile…:** The 6 GB split that prevents the framebuffer pin failures (Board Test, test 37), and the
  11.5 GiB limit. The limit is all the RAM with that split. The suite's boards run this profile.
- **Smooth profile…:** The 6 GB split, and a GTT limit of the RAM less 2 GiB. With 9.4 GiB of RAM, that is 7.4 GiB.
  It also sets zram the size of the RAM with zstd and `vm.swappiness` 180, and the suite's memory guard.

The Default and Games profiles leave the swap layout and the guard as they are.

The GTT limit of the Smooth profile keeps 2 GiB of RAM for the system. When a program's GPU work fills the rest, that
program gets an error, and the board keeps running. Without the room, the GPU can take all the RAM. Swap cannot hold
what the GPU borrows, so the board then stalls.

A profile writes only what differs from the board. The split goes to CMOS. The limit goes to the next boot's kernel
arguments. The swap layout and the guard go to files in /etc. The profile asks once and names what it will write.
Each part it writes then asks for your password. A profile the board already has is off. The split, the limit and the
swap take effect after you restart the board, which stays yours to do. The guard takes effect at once.

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

## The memory guard

When the RAM and the swap run out, the board stalls. Games freeze, and the desktop stops answering. The kernel ends a
program only at the end, which can take minutes. systemd-oomd ends the program that uses the most memory before
that.

Under **Memory guard** you pick when systemd-oomd acts:

- **The suite's guard:** when memory pressure stays above 60% for 10 seconds, or when the swap is 90% full.
- **Bazzite's own:** when memory pressure stays above 80% for 20 seconds. Bazzite does not watch the swap.

Memory pressure is the share of time the programs wait for memory. The suite's values are starting values. We test
them on the suite's boards.

**Apply…** asks first, names what will change, and then asks for your password. The guard takes effect at once,
without a restart. Apply is off while the guard you picked is the one already written.

The guard does not turn recording on or off.

## Recording

Under **Recording**, **Turn on** starts a user service that records the sessions. **Turn off** stops it. It needs no
password. Step 1 of the learning steps turns it on. The **Recording** box in the header says whether it is on.

The service looks every two seconds. It records these figures of the board:

- the RAM in use
- the VRAM in use
- what the GPU borrows, the GTT in use
- the swap in use
- the wait for memory
- the CPU load of all cores

The CPU load is for context only.

While a game runs, the service also does two things:

- **A memory stall:** the wait for memory stays at 40% or more for 10 seconds. The service then ends the game, to
  free the board. A notification says so, with a button that opens the window. Step 4 then has a change to try.
- **A crash:** a notification says so at once, with the memory figures of that moment. The crash report can take
  half a minute, and the game's window stays frozen until it is written.

A program other than a game that crashes gets a notification when it ends. The notification names the process that
crashed and its signal, such as SIGSEGV. A program another one started runs under that one's name. Steam started
from the suite runs under BC250 Bazzite Suite, for example. The notification then names both.

The 40% and the 10 seconds are starting values. We test them on the suite's boards.

## Sessions

While recording is on, a service watches the programs of your desktop session. It looks every two seconds. A
program that takes 1 GiB or more, its memory and swap together, becomes a session. A game always becomes one,
whatever its size. A program that is killed always becomes one too. A game is a Steam game, or a game of the suite's
emulators started from Steam.

During step 3, a table under the steps shows the sessions of round 1, the newest first. Each row has these
columns:

- **Game:** the game's name in Steam, or the app's name
- **How it ended:** how the program ended
- **RAM:** the board's peak RAM in use while it ran
- **VRAM:** the board's peak VRAM in use
- **GPU borrows:** the board's peak GTT in use
- **Swap:** the board's peak swap in use
- **Waited:** the highest memory pressure, as the share of time every task waited for memory
- **CPU:** the board's peak CPU load, for context only

The **How it ended** column says one of these:

- **Closed:** the program ended by itself, or you closed it.
- **Guard: swap full:** systemd-oomd ended it, because the swap was over the guard's limit.
- **Guard: memory pressure:** systemd-oomd ended it, because memory pressure stayed over the guard's limit.
- **Killed: swap full:** the kernel ended it, and the swap was 95% full or more.
- **Killed: GPU memory:** the kernel ended it, and the GPU borrowed half the RAM or more.
- **Killed: RAM full:** the kernel ended it otherwise.
- **Crashed:** the program crashed and wrote a crash dump. A crash is not a lack of memory.
- **Ended: memory stall:** the app ended the game, because the board stalled for memory.
- **Running when the session ended:** you logged out or shut down while it ran.
- **Board restarted while it ran:** the board froze or lost power while it ran.

## Log

The **Log** tab lists each session the recording kept, the newest first. It keeps the last 50. Each row has these
columns:

- **When:** the day and time the program ended
- **Program:** the game's name in Steam, or the app's name
- **How it ended:** as in the list above, in red when something went wrong
- **Memory then:** the board's peak RAM in use, swap in use and wait for memory while it ran
- **What the crash report says:** for a crash, the process that crashed and its signal

**Only what went wrong** hides the programs that closed as usual. A crash of a program started by another program
shows both names. The crash report comes from systemd-coredump.

## Programs

**Programs** in the bottom row opens a window with the memory over time and every program the service has seen. It
shows only what the service recorded while recording was on.

**Memory over time** draws three lines, against the RAM as a dashed line:

- **RAM in use**
- **GPU borrows,** the GTT in use
- **Swap in use**

Each point is the peak of one minute. A red line marks where a lack of memory ended a program, with its name. Pick
the last hour, the last 4 hours or the last 24 hours. The service keeps 24 hours.

The table lists the programs, the largest first:

- **Runs:** how often the program ran
- **Peak** and **Average:** the program's own memory, swap included
- **Killed:** how often a lack of memory ended it
- **Close for games:** your mark

### Closing programs for games

Check **Close for games** for a program you do not need while you play. When a game starts, each checked program that
runs gets systemd's stop signal, SIGTERM. A game is a Steam game or a game of the suite's emulators, started from
Steam. Most programs save and quit on the stop signal. Some do not ask about unsaved files the way their close button
does. Save your work before you start a game.

The app checks no program by itself. Steam and the games say **Never** and cannot be checked, because closing them
would end the game. When the service starts during a game, it closes nothing for that game. The programs stay closed
after the game.

Each close goes to `close-for-games.log`, with the program and the game. The program's session ends as **Closed for a
game**.

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
- **After a fresh install of Bazzite:** the split is still the one set before. Install the app again and use
  **Default profile…** for the firmware's 512 MB, or pick another split.

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

The memory guard:

- **In the app:** pick **Bazzite's own** under Memory guard and apply it. This takes effect at once.
- **Without the app:** remove the four guard files below with `sudo rm`. Then run `sudo systemctl daemon-reload`,
  `sudo systemctl restart systemd-oomd` and `systemctl --user daemon-reload`.

The learning steps:

- **A change:** **Undo** in step 5 writes back the setting from before.
- **All of it:** each setting above undoes on its own. **Start over** only deletes the rounds.
- **Recording:** **Turn off** under Recording, on the Advanced tab.

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

- `/etc/systemd/oomd.conf.d/90-bc250-memory-manager.conf`: the guard's limits and duration.
- `/etc/systemd/system/-.slice.d/90-bc250-memory-manager.conf`: the swap, watched for the whole board.
- `/etc/systemd/system/user@.service.d/90-bc250-memory-manager.conf`: memory pressure, watched for your session.
- `/etc/systemd/user/slice.d/90-bc250-memory-manager.conf`: the limit for the apps and games in your session.
- `~/.config/systemd/user/bc250-memory-watch.service`: the service that records the sessions.
- `~/.local/share/bc250-memory-manager/sessions.jsonl`: the last 50 sessions, with the oldest first.
- `~/.local/share/bc250-memory-manager/sessions-open.json`: the sessions of the programs that run now.
- `~/.local/share/bc250-memory-manager/history.jsonl`: one point a minute for the last 24 hours.
- `~/.local/share/bc250-memory-manager/programs.json`: each program's runs, peak, average and kills.
- `~/.local/share/bc250-memory-manager/close-for-games.json`: the programs checked to close for games.
- `~/.local/share/bc250-memory-manager/close-for-games.log`: each program closed for a game.
- `~/.local/share/bc250-memory-manager/learn.json`: the learning steps' rounds, their settings and verdicts.
- `~/.config/autostart/bc250-memory-manager-resume.desktop`: opens the window after the next login while a learning
  step waits for a restart.

How the app reads and writes CMOS: [Memory Manager internals](../development/memory-manager.md).

## Install

Install it from the BC250 Bazzite Suite portal, or from a clone or release folder, as your own user:

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
./install.sh --uninstall             # remove the app and the sessions service; keeps its settings and CMOS backups
./install.sh --uninstall --purge     # also remove its settings, CMOS backups and memory records
```

Reading and writing CMOS needs `pkexec` and the system `python3`. The GTT limit needs `rpm-ostree`. Bazzite has all
three. Removing the app changes neither the split in CMOS nor the kernel arguments.

## License

GPL-3.0-or-later. See [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/vram/LICENSE).
The CMOS layout comes from [fanoush/bc250_memcfg](https://github.com/fanoush/bc250_memcfg) (MIT).
