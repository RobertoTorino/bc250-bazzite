<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Mesh Shaders](../assets/mesh/bc250-mesh-shaders.webp){ .app-logo }

# BC-250 Mesh Shaders

!!! warning "Changes the board"
    The app builds RADV, Mesa's Vulkan driver, with DirectMesh in a container and installs it under
    /usr/local/lib/bc250-mesh-shaders, beside the system Mesa, which is never changed, with a wrapper in
    /usr/local/bin. A game uses it only through the wrapper in its launch options, and only after the app's test
    passed on the running kernel; nothing is set for every app. The files stay across reboots, power offs and
    Bazzite updates. Nothing is written to the BIOS, the firmware, the kernel or its arguments. Remove takes the
    driver and the wrapper away: games are back on the system Mesa, and the launch options you gave them must go
    by hand.

BC-250 Mesh Shaders brings **mesh shaders** to games on the **AMD BC-250**. Mesh shaders are how newer DirectX 12
games (DirectX 12 Ultimate) draw their scenes. Some of these games need mesh shaders to start. Others fall back to an
older path without them.

The BC-250's GPU has an older design than mesh shaders were made for. That is why the stock Mesa driver does not
offer them. [DirectMesh](https://github.com/lonewolf0622/bc250meshtaskwork) adds them to RADV (Mesa's Vulkan driver)
for the BC-250. It draws every mesh shader on a route that avoids the patterns that hang this chip. Some task and mesh
shader pairs fit none of these routes. Such a pair runs as compute work with an ordinary draw after it. That is
slower, but the game still draws it.

The app builds RADV with DirectMesh and installs it **beside** the system Mesa. The system Mesa is never changed.
Games use the new driver only when you say so. They also need the app's test to have passed on the running kernel.

The DirectMesh project reports these games running with it on a BC-250:

- Final Fantasy VII Rebirth
- Control
- Hellblade 2
- Alan Wake 2
- Crimson Desert

Only games that use mesh shaders gain anything.

## Before you start

- A BC-250 on **Bazzite**. The app builds for the Fedora version that Bazzite is based on.
- About 1 GB free in your home folder during a build, and an internet connection.
- `podman`, which Bazzite ships.

## Using it

Install the app from the BC250 Bazzite Suite portal. You find it under Graphics. You can also install it from a clone
or a release folder. Run the installer as your own user, not with sudo:

```bash
./install.sh                         # app menu entry and Desktop icon
./install.sh --no-desktop-shortcut   # app menu entry only
```

Installing the app changes nothing on the board. Open **BC-250 Mesh Shaders** and go through the four steps.

The window has two rows of boxes and pills under its introduction.

- The first row shows where the steps stand, in the **Build**, **Driver** and **Test** boxes. **Copy options** and
  **Switches** sit beside them.
- The second row has the pills for the steps: **Build**, **Install**, **Remove** and **Run test**.
- Under the rows, the boxes **1. Build** to **4. Use** name the steps. Beside each box, you see where its step stands.

The round arrow in the title row reads the state again. The round **i** says what the app changes.

1. **Build.** Builds RADV with DirectMesh in a Fedora container, as your own user. It downloads the Mesa source and
   the build tools, several hundred MB in all. It takes 20 to 40 minutes. Nothing on the system changes.
2. **Install.** Copies the driver to `/usr/local/lib/bc250-mesh-shaders`. You will be asked for your password.
   Nothing uses the driver yet.
3. **Test.** Runs the mesh test with the installed driver. This takes a few minutes. Games only get the driver once
   the test has passed on the running kernel.
4. **Use.** Click **Copy options**. Paste the options into the game's *Properties → Launch options* in Steam:

    ```
    /usr/local/bin/bc250-mesh-shaders-run %command%
    ```

    The test may not have passed on the running kernel yet. This happens after a kernel update, or with a new
    driver. The game then starts with the system Mesa instead. `~/.local/state/bc250-mesh-shaders/run.log` says why.

The status next to the title sums it up. It shows **Not built**, **Not installed**, **Test needed**, **Ready** or
**Test failed**. On a board that is not a BC-250, it shows **No BC-250**.

The driver is only for the games you give the launch options. No switch makes it the driver of every app.

## The test

The test draws a grid of 256 colored tiles in four ways:

- with a task shader and a mesh shader
- with a mesh shader alone, at the largest size a mesh shader may have, which the driver has to split on this chip
- both of these again, from an indirect draw

It compares every pixel with the color its tile must have.

Meanwhile, the BC-250's compute queues (the ACE) work beside the draws. DirectMesh opens these queues. Each queue
does two things:

- it copies an image through the driver's own copy shaders
- it runs dispatches whose last workgroup is a partial one

The test compares the results word for word. Task shaders run on the GPU's compute side too. So the test has both at
work at once. Some DirectMesh releases keep these queues closed. The test then says so and checks the draws alone.

It does this ten times, each time with a new Vulkan device. It checks the kernel log for GPU ring timeouts and resets.

A failed test means that you should not use the driver on this kernel. Its output is in
`~/.local/state/bc250-mesh-shaders/test.log`.

!!! note "Why a test per kernel"
    The compute queues need fixes in the kernel to set them up and tear them down properly. Bazzite's kernel does
    not have these fixes. The driver runs without them, as BC-250 ACE Queues does. The app tests each kernel before
    games may use the driver.

## Switches

**Switches** puts the driver's switches in front of the launch options. They are for comparisons, and for finding the
cause of a problem in one game. Leave them all off to play, unless the game needs one. With every switch off, the
driver works as DirectMesh ships it. After a change, copy the launch options to the game again.

| Switch | What it does |
|---|---|
| No indexed mesh draws (`RADV_BC250_MESH_IDXPASS=0`) | Keeps DirectMesh's protected mesh routes, without its indexed mesh draws. |
| No Task index route (`RADV_BC250_MESH_TASK_IDX=0`) | The driver refuses a task and mesh shader pair that no mesh route can take. The game draws nothing for it. Without this switch, the pair runs as slower compute work with an ordinary draw. |
| No renumbered vertices (`RADV_BC250_MESH_SAFE_COMPACT=0`) | Culling can leave a workgroup with unused vertices. Such a workgroup then exports private triangle corners instead of only the vertices it uses. |
| Private corners only (`RADV_BC250_MESH_SAFE_ADAPTIVE=0`) | No shared vertices at all. Every triangle exports its own corners. This is slower, and the most cautious route. |
| DirectMesh off (`RADV_DIRECTMESH=0`) | The driver falls back to its base BC-250 settings, for a comparison on the same driver. |
| Hide mesh shaders (`RADV_DEBUG=nomeshshader`) | The game does not see mesh shaders and takes its own path without them, for a comparison. |
| Split mesh shaders that write memory (`RADV_BC250_MESH_SPLIT_WRITES=1`) | For a game whose large mesh shaders write to buffers, such as PS5 emulators. The driver splits these shaders anyway and runs their writes once. It cannot check that the game never reads them back in the same draw. Use it only for the game that needs it. |

`run.log` notes the switches each game was started with.

## When the kernel or the app changes

- **A kernel update:** games with the launch options start with the system Mesa until you run the test again.
- **A Mesa update of the system** changes nothing for the driver. The app builds the driver from the Mesa release
  that its DirectMesh release is made for.
- **An update of the app** can bring a newer DirectMesh release (see [New DirectMesh releases](#new-directmesh-releases)).
  The Build step then says so. Build and install again, then run the test.

## New DirectMesh releases

Each version of the app builds one DirectMesh release and brings its patch along. The Build step names that release.
When the app starts, it asks GitHub whether DirectMesh has a newer release. This is one small request. The Build
step then says what it found. It shows **DirectMesh v1.x is out** with a link to the release notes. Or it says that
the release the app builds is the newest.

The app does not build a newer release by itself. A new version of the app brings it through the portal, once its
patch has been checked. Then build, install and test again. Uncheck **Look for a newer DirectMesh release at start**
to stop the request. The link in the Build step then looks once, when you click it.

## If something goes wrong

- **A game does not start, hangs or shows corruption:** take the launch options out of the game. Or try the game
  with **Switches** to narrow the cause down. If the test passed, please report it with the game, the switches and
  `run.log`.
- **The board locks up during a game:** this is a GPU hang. DirectMesh asks for hang reports with the kernel
  parameter `amdgpu.gpu_recovery=0`. With it, the board stays reachable over SSH. Send `dmesg`, the game and its
  launch options.
- **Remove** in the window removes the driver. Take the launch options out of your games first. Without the driver,
  those games do not start.

## Together with BC-250 ACE Queues

Both apps install a driver of their own, and a game uses one of them. DirectMesh opens the compute queues as BC-250
ACE Queues does. So a game that needs mesh shaders gets async compute from this driver too. Give a game the launch
options of one app only.

## From a terminal

The window runs `bc250-mesh-shaders.sh` in the app's folder (`/opt/bc250-mesh-shaders`). You can run the same steps
by hand:

```bash
/opt/bc250-mesh-shaders/bc250-mesh-shaders.sh --status
/opt/bc250-mesh-shaders/bc250-mesh-shaders.sh --build            # as your own user
sudo /opt/bc250-mesh-shaders/bc250-mesh-shaders.sh --install-driver
/opt/bc250-mesh-shaders/bc250-mesh-shaders.sh --test
sudo /opt/bc250-mesh-shaders/bc250-mesh-shaders.sh --remove-driver
```

## What goes where

| Where | What |
|---|---|
| `/opt/bc250-mesh-shaders` | the app, owned by root |
| `~/.cache/bc250-mesh-shaders` | the Mesa source and your build, removed when you remove the app |
| `~/.local/state/bc250-mesh-shaders` | test results, the test log and `run.log` |
| `/usr/local/lib/bc250-mesh-shaders` | the installed driver and the mesh test |
| `/usr/local/bin/bc250-mesh-shaders-run` | the launch options wrapper |

On Bazzite, `/usr/local` is `/var/usrlocal`. That folder is writable and kept across image updates. So the driver
needs no layering and no restart.

To remove the app, run `./install.sh --uninstall`. This removes the app and the build. An installed driver stays.
So remove the driver first, with **Remove**. `--purge` also removes the settings and the test results.

## How it is built

- **Mesa source:** the release from `archive.mesa3d.org` that the DirectMesh release is made for. The build checks
  it against its signature, with the keys of the Mesa release maintainers. These keys come from Mesa's own source.
  The app brings them along.
- **The patch** (`mesa/bc250-directmesh-mesa-<version>.patch`): the patch for stock Mesa that DirectMesh publishes
  with its release. The app brings it along. The build checks it against the SHA-256 the release publishes.
- **The suite's patch** (`mesa/bc250-suite-mesa-<version>.patch`): applied on top of DirectMesh's patch. It adds
  the suite's own change. With it, the driver can split mesh shaders that write memory, through the switch above.
  The Build step names this patch by the start of its SHA-256 (`suite patch 1a2b3c4d`). When an app update changes
  it, build again.
- **The build:** RADV alone (no OpenGL, no LLVM), with the prefix `/usr/local/lib/bc250-mesh-shaders`. It runs in a
  `registry.fedoraproject.org/fedora` container of your Bazzite's Fedora version. So it links against the same
  libraries. The driver's game profiles (`drirc`) point at the system's.

`bc250-mesh-shaders.sh --version` names the DirectMesh release and the Mesa version that an app version builds.

## Credits

- [DirectMesh](https://github.com/lonewolf0622/bc250meshtaskwork) by LoneWolf (MIT), for the mesh shader support and
  the game results above.
- [Mesa](https://mesa3d.org/) (MIT).
