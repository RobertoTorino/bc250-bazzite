<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 ACE Queues](../assets/ace/bc250-ace-queues.webp){ .app-logo }

# BC-250 ACE Queues

!!! warning "Changes the board"
    The app builds a patched RADV, Mesa's Vulkan driver, in a container and installs it under
    /usr/local/lib/bc250-ace-queues, beside the system Mesa, which is never changed, with a wrapper in
    /usr/local/bin. A game uses it only through the wrapper in its launch options, and only after the app's test
    passed on the running kernel. All apps adds an environment file under /etc and a small boot service that
    switches it off again when the kernel or the driver changes. The files stay across reboots, power offs and
    Bazzite updates. Nothing is written to the BIOS, the firmware, the kernel or its arguments. Remove takes the
    driver, the wrapper and the All apps files away: every app is back on the system Mesa, and the launch
    options you gave games must go by hand.

BC-250 ACE Queues lets games on the **AMD BC-250** use the GPU's dedicated compute queues. This is called
**async compute**. Games split a frame into graphics work and compute work. Compute work is lighting, particles,
post-processing and upscaling. With a compute queue of its own, the compute work runs beside the graphics work on
shader cores that would otherwise wait.

The BC-250's GPU has these queues. They are the ACE, short for Asynchronous Compute Engines. The stock Mesa driver
keeps them closed, because its compute dispatches came out wrong on this chip. The app builds a patched RADV,
Mesa's Vulkan driver. The patched driver opens the queues and runs their dispatches in a mode that works on this
chip. The app installs that driver **beside** the system Mesa and never changes the system Mesa. Games use the
driver only when you say so, and only after the app's test passed on the running kernel.

The upstream project measured +21 to +25 % in Cyberpunk 2077. It measured at 1440p and Medium, with the 40-CU
unlock. The gain depends on the game. Only games that use async compute gain anything.

## Before you start

- A BC-250 on **Bazzite**. The app builds for the Fedora version of your Bazzite.
- About 1 GB free in your home folder during a build, and an internet connection.
- `podman`, which Bazzite ships.

## Using it

Install the app from the BC250 Bazzite Suite portal, where it is under Graphics. You can also install it from a
clone or a release folder. Run the installer as your own user, not with sudo.

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
```

Installing the app changes nothing on the board. Open **BC-250 ACE Queues** and go through the four steps.

1. **Build.** Builds the patched RADV for the Mesa version your system has. The build runs as your own user, in a
   Fedora container. It downloads the Mesa source and the build tools, several hundred MB. It takes 20 to 40
   minutes. Nothing on the system changes.
2. **Install.** Copies the driver to `/usr/local/lib/bc250-ace-queues`. It asks for your password. Nothing uses the
   driver yet.
3. **Test.** Runs the ACE queue test with the installed driver. It takes about a minute. Games get the driver
   only after the test has passed on the running kernel.
4. **Use.** Use the driver per game, or for every app.
    - **Per game:** press **Copy launch options** and paste them into the game's *Properties → Launch options* in
      Steam.

        ```
        /usr/local/bin/bc250-ace-queues-run %command%
        ```

        After a kernel update, or with a new driver, the test has not passed on the running kernel yet. The game
        then starts with the system Mesa instead. `~/.local/state/bc250-ace-queues/run.log` says why.
    - **All apps:** press **All apps: on**. Every app then uses the patched driver, the desktop included, without
      launch options. It applies after you log out and back in. Flatpak apps keep their own driver.

The status next to the title sums it up:

- **Not built**
- **Not installed**
- **Test needed**
- **Ready**
- **Test failed**
- **On for all apps**

## The test

The test runs the same work on every compute queue at once. The work has four parts:

- a buffer fill
- a buffer copy
- a copy into an image and back
- a compute dispatch whose last workgroup is a partial one

The driver runs the copy into an image and back with its own copy shaders, where the bug dropped rows. The test
compares every result word for word. Then it closes the queues and opens them again. It does all of this ten
times. It also checks the kernel log for GPU ring timeouts and resets during the test.

After a failed test, don't use the driver on this kernel. The test's output is in
`~/.local/state/bc250-ace-queues/test.log`.

!!! note "Why a test per kernel"
    The upstream fix also patches the kernel. Those patches repair how the kernel sets the compute queues up and
    tears them down. Bazzite's kernel does not have them. The Bazzite port of the fix runs without the kernel
    patches on Bazzite's kernels, so this app does too. The app checks each kernel with its test before games may
    use the driver.

## When the kernel or Mesa changes

- **A kernel update:** games with the launch options start with the system Mesa until you run the test again.
  With **All apps** on, a check at boot switches it off. The check runs before anyone logs in. The window then
  says so. Run the test, then switch it on again.
- **A Mesa update:** the installed driver keeps working. The Build step says when the system has a newer Mesa.
  Build and install again to keep up with it, then run the test.

## If something goes wrong

- **A game does not start, or shows corruption:** take the launch options out of the game. If the test passed,
  please report it with the game and `run.log`.
- **The desktop does not come back after switching on All apps:** press Ctrl+Alt+F3, log in and run:

    ```bash
    sudo rm /etc/environment.d/90-bc250-ace-queues.conf
    sudo reboot
    ```

- **Remove** in the window switches All apps off and removes the driver. Take the launch options out of your games
  first. Without the driver they do not start.

## From a terminal

The window runs `bc250-ace-queues.sh` in the app's folder, `/opt/bc250-ace-queues`. The same steps by hand:

```bash
/opt/bc250-ace-queues/bc250-ace-queues.sh --status
/opt/bc250-ace-queues/bc250-ace-queues.sh --build            # as your own user
sudo /opt/bc250-ace-queues/bc250-ace-queues.sh --install-driver
/opt/bc250-ace-queues/bc250-ace-queues.sh --test
sudo /opt/bc250-ace-queues/bc250-ace-queues.sh --all-apps on # or off
sudo /opt/bc250-ace-queues/bc250-ace-queues.sh --remove-driver
```

## What goes where

| Where | What |
|---|---|
| `/opt/bc250-ace-queues` | the app (root-owned) |
| `~/.cache/bc250-ace-queues` | the Mesa source and your build, removed when you remove the app |
| `~/.local/state/bc250-ace-queues` | test results, the test log and `run.log` |
| `/usr/local/lib/bc250-ace-queues` | the installed driver and the ACE queue test |
| `/usr/local/bin/bc250-ace-queues-run` | the launch options wrapper |
| `/etc/environment.d/90-bc250-ace-queues.conf`, `/etc/profile.d/90-bc250-ace-queues.sh` | only with All apps on |
| `bc250-ace-queues-guard.service` | the check at boot, only with All apps on |

On Bazzite `/usr/local` is `/var/usrlocal`. That folder is writable, and Bazzite keeps it across image updates. So
the driver needs no layering and no restart.

`./install.sh --uninstall` removes the app and the build. It leaves an installed driver as it is, so remove the
driver first with **Remove**. `--purge` also removes the settings and the test results.

## How it is built

- **Mesa source:** the release from `archive.mesa3d.org` that matches the system's Mesa version. The build checks
  it against its signature, with the keys of the Mesa release maintainers. The keys come from Mesa's own source,
  and the app bundles them.
- **The patch:** `mesa/gfx1013-ace-queue.patch` changes one file, `src/amd/common/ac_gpu_info.c`. It opens the
  compute queue on GFX1013. It gives the queue the async compute workaround RADV already has for the Iceland and
  Tonga GPUs. That workaround runs compute dispatches in thread-dimension mode instead of threadgroup-dimension
  mode.
- **The build:** RADV alone, with no OpenGL and no LLVM. Its prefix is `/usr/local/lib/bc250-ace-queues`. The
  build runs in a `registry.fedoraproject.org/fedora` container of your Bazzite's Fedora version, so the driver
  links against the same libraries. The driver's game profiles (`drirc`) point at the system's.

## Credits

- The fix, with the benchmark above, is
  [DryhoppedIPA/bc250-gfx1013-fix](https://github.com/DryhoppedIPA/bc250-gfx1013-fix) (MIT).
- The Bazzite port, without the kernel half, is
  [tri3gubki-ops/bc250-async-compute-bazzite](https://github.com/tri3gubki-ops/bc250-async-compute-bazzite) (MIT).
- [Mesa](https://mesa3d.org/) (MIT).
