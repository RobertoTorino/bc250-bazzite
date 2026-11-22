<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 SSD Check](../assets/ssd/bc250-ssd-check.webp){ .app-logo }

# BC-250 SSD Check

BC-250 SSD Check shows how an SSD is doing. You see these values:

- its **health**
- its **power cycles**
- its **power-on hours**
- the drive's specs
- whether the board lets it run at its full speed

SSD Check only reads the drive. The speed test writes a test file and deletes it. Nothing on the drive changes, and
the app needs no root.

| Value | What it shows | NVMe | SATA SSD |
|---|---|---|---|
| Health | how much of its rated life the drive has left, in percent | 100 minus "percentage used" | an attribute of the drive's maker, see below |
| Power cycles | how often the drive was turned on | "power cycles" | attribute 12 |
| Power-on hours | how long it has run in all. Hover it to see the years. | "power-on hours" | attribute 9 |

## Using it

- **The top row**, beside the icon:

  | Pill | What it does |
  |---|---|
  | Health | the drive's health, see above |
  | Serial | the drive's serial number, hidden. Click the pill to see it in a small window below it. There you can select it to copy. A click anywhere else closes it. It also closes when you choose another drive or Refresh. |
  | Measured R / W MB/s | **Test**. Click it to measure the drive's read and write speed in this board, see below. |
  | Refresh | reads the drives again |

- **Drive:** with more than one drive, choose it by its number (Drive 1, Drive 2) in the list under the top row.
  Under the list are the drive's model and size. A line below them gives its bus and when udisks last read it.
- **Screenshot**, beside the list, saves the window with the values it shows now as a PNG. The file goes in your
  Pictures folder, in a folder named BC-250 SSD Check. The file's name holds the date and time, for example
  `~/Pictures/BC-250 SSD Check/BC-250 SSD Check 2026-11-05 18-04-09.png`. The file manager opens on the folder with
  the new file selected. The line beside the button names the file. Hover it for the folder. The serial stays hidden
  in the picture, even while its small window is open.
- The specs, a pill each:

  | Pill | What it shows |
  |---|---|
  | Power cycles | how often the drive was turned on |
  | Power-on hours | how long it has run in all |
  | Power-on days | the power-on hours in full days. A day not yet complete does not count, so 4,025 hours are 167 days. |
  | Drive | the device name (`nvme0n1`, `sda`) |
  | Host reads | how much data the computer has read from the drive in all |
  | Host writes | how much data the computer has written to the drive in all |
  | Firmware | the version of the drive's firmware |
  | Update | whether fwupd knows a newer firmware for the drive, see below |
  | Interface | NVMe with its version, SATA or USB |
  | Speed | the link the drive runs at now. For an NVMe drive that is the PCIe generation and lanes. For a SATA or USB drive it is the link's speed. Hover it to see what the drive could do. |
  | Board link | the most the board's port offers the drive. That port is its PCIe slot, SATA port or USB bus. Orange means the port carries less than the drive can do, so the board holds the drive back. Green means the port is fast enough. Hover it for the numbers. |
  | Rated R / W MB/s | the maker's rated read and write speed, from SSD Check's list of drives, see below |

- The state beside the name:

    | State | Meaning |
    |---|---|
    | No problems reported | the drive flags nothing |
    | The drive reports a problem | the drive itself flags a problem. Hover the state to see which, from the list below this table. Back up what you want to keep. |
    | Health not reported | the drive gives its hours and cycles, but no health value SSD Check knows |
    | Partly read | SSD Check could not read the drive's SMART attributes this time. The boxes show what udisks had. Refresh tries again. |
    | No SMART over USB | the drive is on USB, and its adapter does not pass its SMART values on. The specs still show. |
    | No drive found | udisks knows no NVMe or SATA drive with SMART values, and no drive on USB |
    | udisks does not answer | the udisks service is not running. The line under the boxes says what it answered. |

    A drive can flag these problems:

    - little spare space left
    - too hot or too cold
    - less reliable
    - read-only
    - its backup power failed
    - SMART says it is failing

- The **Health** box is green, orange at 0 % and red when the drive reports a problem. At 0 % the drive has used
  its rated endurance. Many drives keep working long after that, but make sure your backup is current.
- The small **i** explains the values.

### Where the values come from

udisks is the service that mounts drives on the desktop. It reads each drive's SMART values now and then, and it
answers any user over D-Bus. SSD Check asks it with `busctl`. The line under the boxes says when udisks last read
the drive. Refresh shows what udisks read last. It does not make the drive read again.

An NVMe drive reports all three values in the same way on every make. A SATA SSD reports its health in an attribute
its maker chose. SSD Check reads the first of these it finds, as the life left in percent:

| Attribute | Name | Used by |
|---|---|---|
| 231 | SSD life left | Kingston, SandForce and many others |
| 169 | Remaining lifetime | Western Digital |
| 202 | Percent lifetime remaining | Crucial, Micron |
| 233 | Media wearout indicator | Intel |
| 177 | Wear leveling count | Samsung |

A SATA drive with none of them shows **Not reported** in the Health box. Hover a known value to see which attribute
it came from. SSD Check lists a hard disk too, with its hours and cycles.

SSD Check lists a drive on USB with its specs. Such a drive can be a stick, an external SSD or disk, or an M.2 drive
in an enclosure. udisks cannot read SMART values through most USB adapters. Some adapters pass them only to
`smartctl`, which needs root. Then these stay empty:

- the health
- the power cycles
- the hours
- the data read and written

The state then says **No SMART over USB**. An M.2 enclosure with a known NVMe bridge shows **NVMe over USB** as its
interface. The known bridges are the Realtek RTL9210, ASMedia ASM2362 and JMicron JMS583.

**A drive stuck at USB 2.0.** A USB 3 port is two ports to Linux, one for USB 2.0 and one for USB 3. USB 2.0
carries 480 Mb/s, about 40 MB/s in practice. When a drive links at USB 2.0 in a port that does USB 3, the **Speed**
pill turns orange. Hover it to see what to try:

- another cable, because many USB-C cables carry only USB 2.0
- the drive straight in the board instead of through a hub
- plugging it in again

**Board link** then shows what the port can do.

The speed test needs a folder on the drive you may write to. A drive with another system on it has file systems
that belong to root. The **Test** pill then stays empty. Hover it to see why.

**Host reads** and **Host writes** of an NVMe drive come from its own counters. A SATA drive keeps them in
attributes 242 and 241. SSD Check counts them as 512-byte sectors, as most makers do. A maker that counts in other
units shows a number that is off. The **Speed** comes from the kernel (sysfs).

### Speed: the drive, the board and the measurement

The last row of specs and the **Test** pill at the top answer whether the drive can run at its full speed in
this board.

- **Board link** is the most the board's port carries, with about how many MB/s that is. It shows one of these:

    - a PCIe port's generation and lanes
    - a SATA port's limit
    - the USB bus's speed

    On the BC-250, the M.2 slot is a PCIe 2.0 x2 port. It carries at most about 1,000 MB/s. So the board holds a
    PCIe 3.0 or 4.0 drive back there.

- **Rated R / W** is what the maker says the drive reads and writes, in MB/s. No drive reports it. So SSD Check
  keeps a list from the makers' data sheets. It holds the NVMe drives of PCIe 3.0 and later and a few SATA SSDs.
  Where the maker rates the capacities apart, the list gives each one its own speeds:

    | Maker | Drive | Capacities |
    | --- | --- | --- |
    | Samsung | 970 EVO Plus | 250GB, 500GB, 1TB, 2TB |
    |  | 980 | 250GB, 500GB, 1TB |
    |  | 980 PRO | 250GB, 500GB, 1TB, 2TB. With heatsink: 1TB, 2TB |
    |  | 990 EVO | 1TB, 2TB |
    |  | 990 EVO Plus | 1TB, 2TB, 4TB |
    |  | 990 PRO | 1TB, 2TB, 4TB, also with heatsink |
    |  | 9100 PRO | 1TB, 2TB, 4TB, 8TB, also with heatsink |
    |  | 860 EVO, 870 EVO (SATA) | every capacity |
    | WD_BLACK | SN750 | 250GB, 500GB, 1TB, 2TB, 4TB |
    |  | SN750 SE | 250GB, 500GB, 1TB |
    |  | SN770 | 250GB, 500GB, 1TB, 2TB |
    |  | SN770M | 500GB, 1TB, 2TB |
    |  | SN850 | 500GB, 1TB, 2TB |
    |  | SN850X, SN850P | 1TB, 2TB, 4TB, 8TB |
    |  | SN7100 | 500GB, 1TB, 2TB, 4TB |
    |  | SN8100 | 1TB, 2TB, 4TB, 8TB |
    | Crucial | P3, P3 Plus | 500GB, 1TB, 2TB, 4TB |
    |  | P5 Plus | 500GB, 1TB, 2TB |
    |  | T500 | 500GB, 1TB, 2TB, 4TB |
    |  | P310 | 500GB, 1TB, 2TB |
    |  | T700, T705, T710 | 1TB, 2TB, 4TB |
    |  | P510 | 1TB |
    |  | MX500 (SATA) | every capacity |
    | SK hynix | Gold P31, Platinum P41 | 500GB, 1TB, 2TB |

    A drive that is not in the list shows **Unknown**. Hover it to see what its fastest link carries instead. A few
    drives are left out on purpose, because their maker's rated speeds are not clear:

    - the Crucial E100, because only shops give speeds
    - the Crucial P310 4TB and the P510 2TB
    - SK hynix's Platinum P51, because the maker's only document rates it lower than the drive that went on sale

    Two brands always show Unknown:

    - **Netac:** every Netac NVMe drive tells the system only its capacity ("Netac NVMe SSD 1TB"), never which
      model it is. A 1TB Netac can be anything from a PCIe 3.0 NV3000 (3,100 MB/s read) to a PCIe 5.0 NV150HK
      (13,000 MB/s). So SSD Check cannot know its rated speed. Netac's product pages list them per model.
    - **CUSU:** its drives do tell their model ("CUSU CV3500Q 1TB"). But CUSU publishes no specifications, and
      the speeds sellers list are not the maker's.

- **Measured R / W** is what the drive does in this board. Click the **Test** pill at the top. SSD Check writes a test
  file of about 1 GB to the drive, reads it back and deletes it. This takes a few seconds. On a slow drive it writes
  for at most ten seconds. The file goes in your home folder when that is on the drive (`~/.cache/bc250-ssd-check/`).
  Otherwise, it goes on the drive's first mount point you can write to, such as a USB stick. SSD Check cannot measure
  a drive that is not mounted. The test needs about 2 GB of free space. It writes random data and bypasses the cache,
  so the numbers are the drive's.

When the board holds the drive back, the measured speeds stay under what the board link carries. The maker's rated
speed does not change that.

### Firmware updates

The **Update** pill asks fwupd, Bazzite's firmware updater, whether the LVFS has a newer firmware for the drive. The
LVFS is the Linux Vendor Firmware Service.

| Update | Meaning |
|---|---|
| Available | a newer firmware is on the LVFS. Hover the pill for its version. GNOME Software or `fwupdmgr update` installs it. Back up first. |
| Up to date | fwupd knows no newer firmware for the drive |
| Unknown | fwupd does not answer, or has no firmware list yet. `fwupdmgr refresh` downloads the list. Hover the pill to see which. |
| Not supported | fwupd does not know the drive, or cannot update its firmware |

SSD Check only asks. It never installs firmware.

The serial number shows only when you click its pill, and is never written to a log.

## Install

Install it from the portal (the **Utilities** tab), or from a checkout of the repository:

```bash
apps/ssd/install.sh                         # the app, its launcher, a menu entry and a Desktop icon
apps/ssd/install.sh --no-desktop-shortcut   # without the Desktop icon
apps/ssd/install.sh --uninstall             # remove it; --purge removes its settings too
```

The launcher is `~/.local/bin/bc250-ssd-check`. The app runs on the suite's shared Python environment. It needs
`busctl` (systemd's) and the udisks service, which every Bazzite has.

## License

GPL-3.0-or-later, see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/ssd/LICENSE).
