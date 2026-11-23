<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Persistent ACPI](../assets/acpi/bc250-persistent-acpi.webp){ .app-logo }

# BC-250 Persistent ACPI

!!! warning "Changes the board"
    The app copies three ACPI tables to /boot/acpi_override.cpio and adds one line to /etc/default/grub. Then it
    regenerates the GRUB configuration. At every boot GRUB hands the tables to the kernel. The kernel uses them in
    memory instead of the BIOS's own. Both files stay across reboots, power offs and Bazzite updates. Nothing is written
    to the BIOS, the firmware or the CMOS. The BIOS keeps its own tables, and the override is gone the moment the two
    files are. Uninstall removes the file and the line, puts back any line that was there before, and regenerates GRUB.
    After the next restart the board runs on the BIOS's tables again.

BC-250 Persistent ACPI gives the CPU of the **AMD BC-250** its idle states (C-states) and frequency scaling on
Linux. The frequency scales from 800 MHz to 3.2 GHz in 8 steps. The fix is **persistent**, so it stays across
restarts and updates. It is a safe alternative to BIOS flashing. You don't need the P3.00 MeiMeiDXE v3 modded BIOS.

The ACPI tables come from [e-tho/bc250-acpi-fix](https://github.com/e-tho/bc250-acpi-fix). That project is the
maintained fork of [bc250-collective/bc250-acpi-fix](https://github.com/bc250-collective/bc250-acpi-fix). The app
carries a copy of its release **v1.1.1**. Three SSDT overrides do the work. The kernel loads them from an early
initrd with its [ACPI table upgrade](https://docs.kernel.org/admin-guide/acpi/initrd_table_override.html). An early
initrd is a file that GRUB hands to the kernel at boot.

| Table | Fixes |
|---|---|
| `SSDT-CPU` | Replaces the broken idle-state table (C-states) |
| `SSDT-PST` | Publishes the 8 frequency states |
| `SSDT-STUBS` | Defines missing firmware methods as no-ops |

It works on stock 6-core and unlocked 8-core boards. It works on all stock BIOS versions, because 1.00, 2.00, 3.00
and 5.00 share the same DSDT.

## Is this ACPI fix persistent?

**Yes, it survives updates**.

* `/boot/acpi_override.cpio` stays. `rpm-ostree` and bootc image updates leave extra files in `/boot` alone. They
  manage only `/boot/ostree` and `/boot/loader`.
* `/etc/default/grub` stays. `/etc` is machine-local state on ostree systems, and it is 3-way-merged across
  deployments. So the `GRUB_EARLY_INITRD_LINUX_CUSTOM` line stays. An early initrd line that was in the file before
  is kept beside it as a comment. **Uninstall** puts it back.
* **Kernel updates** need nothing from you. Fedora's `blscfg` GRUB module prepends the early initrd to **every** BLS
  boot entry at boot time. That includes kernels installed later. You don't install again or regenerate GRUB after
  a kernel or image update.

Unlike BIOS flashing, you can reverse it fully, and it carries zero bricking risk. You can reverse it in three ways:

* **Uninstall** in the app
* `sudo ./bc250-acpi-override.sh --uninstall`
* Delete the file and the GRUB line

## Install (Bazzite / Universal Blue)

Install the app from the BC250 Bazzite Suite portal. You can also install it from a clone or a release folder. Run
the installer as your own user, not with sudo.

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
```

Installing the app changes nothing on the board. Open **BC-250 Persistent ACPI** and click **Install**, then
restart. The window shows:

* Whether the override is installed
* The CPU's frequency steps and idle states
* With **Status with sudo**, whether the kernel loaded the tables this boot

From a terminal, without the app:

```bash
sudo ./bc250-acpi-override.sh --install
# reboot
```

The installer takes these steps:

1. It checks for a BC-250 GPU.
2. It warns when the BIOS looks modded. Duplicate tables fail to load, so do **not** combine this with a modded
   BIOS that injects its own fixes.
3. It verifies `CONFIG_ACPI_TABLE_UPGRADE`.
4. It installs the cpio.
5. It adds the GRUB line, and only once.
6. It runs `ujust regenerate-grub`. On plain Fedora it runs `grub2-mkconfig`, where the path in
   `GRUB_EARLY_INITRD_LINUX_CUSTOM` is relative to `/boot/grub2/`.

In a terminal a warning asks "Continue anyway?". The app shows the warning in a dialog. `--yes` answers yes to both
warnings.

### Manual install

```bash
sudo cp tables/acpi_override.cpio /boot/
echo 'GRUB_EARLY_INITRD_LINUX_CUSTOM="../../acpi_override.cpio"' | sudo tee -a /etc/default/grub
ujust regenerate-grub   # then reboot
```

## Verify

The app's status shows the same information. From a terminal:

```bash
./bc250-acpi-override.sh --status                    # installed? frequency steps, idle states
sudo dmesg | grep -iE 'ACPI.*(SSDT|Table Upgrade)'   # 3 tables loaded as override
cpupower frequency-info                              # 8 steps, 800 MHz - 3.2 GHz
cpupower idle-info                                   # POLL, C1, C2 (C2 at 0x414)
```

Or run test 26 of [BC-250 Board Test](check.md). It reports whether the ACPI tables came from the initrd override
or the BIOS.

## Uninstall

Click **Uninstall** in the app and restart. Or from a terminal:

```bash
sudo ./bc250-acpi-override.sh --uninstall
# reboot
```

To remove the app itself, run `./install.sh --uninstall`. Add `--purge` to also remove its settings. This leaves
the override as it is. Uninstall the override first if you want the board back on the BIOS tables.

## Vendored artifacts

`tables/` contains the unmodified assets of e-tho/bc250-acpi-fix v1.1.1 (MIT):

```
b2f5cd6279ef5992f6482a1702e1dd5c0ebeeaf950fde487d7556ef7a291956b  acpi_override.cpio
9cfc1a254ea8814988d5a700e2dba8ebbe4f290a3895435512ea8afa3ba6a46f  SSDT-CPU.aml
cb3c96c622d2d653777020283c434f92c26bf2c83502a27d9a398f98424a771f  SSDT-PST.aml
c219ce775476725d49739024e149556228436a1c3faf0768a7c3eff9d85f66c2  SSDT-STUBS.aml
```

To rebuild from source instead, see the upstream `Makefile` (needs `acpica`/`iasl`).

## Acknowledgements

* [e-tho](https://github.com/e-tho/bc250-acpi-fix) — maintained tables and installation method
* [shinf1x](https://github.com/bc250-collective/bc250-acpi-fix) — original tables
* [rw-r-r-0644](https://github.com/rw-r-r-0644/bc250-acpi-fix) — idle-table diagnosis and ACPI error cleanup
* [mendesrr](https://github.com/mendesrr/bc250-acpi-fix-updated-8c) — 8-core extension

## License

MIT, see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/acpi/LICENSE). The vendored tables are
MIT-licensed by their upstream authors.
