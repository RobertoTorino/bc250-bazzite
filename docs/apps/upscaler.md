<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 Upscaler Manager](../assets/upscaler/bc250-upscaler.webp){ .app-logo }

# BC-250 Upscaler Manager

BC-250 Upscaler Manager puts **[HelixSR](https://github.com/lonewolf0622/HelixSR)** into games on an **AMD BC-250**
board running **Bazzite** (Fedora Atomic / rpm-ostree). It also keeps track of where it put HelixSR. HelixSR is an
FSR 3.1 drop-in upscaler with DLSS-style neural networks. It runs NVIDIA's DLSS Model E network as plain compute
shaders on an AMD GPU. Games talk to it as FSR 3.1. The app is a PyQt6 front-end.

HelixSR is not an injector. It replaces the `amd_fidelityfx_upscaler_dx12.dll` / `amd_fidelityfx_dx12.dll` that a
game ships with. To deploy it, the app renames the game's DLL to `*.original.dll`. Then it puts HelixSR's DLL, its
two network files and an optional `helixsr.ini` in the same folder. The `*.original.dll` is the backup, and HelixSR
still uses it. HelixSR forwards frame generation and the other FidelityFX effects to it.

The app does exactly that, and you can undo it. It touches nothing else on the system. You need no launch options,
no `WINEDLLOVERRIDES` and no Proton tweaks. Only OptiScaler, for games without FSR 3.1, needs a launch option. The
app sets that one too, as described below.

From HelixSR 3 on, what goes in is **HLX FSR 4**, HelixSR's FSR 4-class upscaler. It is one DLL from the release's
`HLX-FSR4` folder, and it comes built with its network inside. Nothing is built on the PC for it. No network files
or `helixsr.ini` go next to it. The app removes network files that an earlier HelixSR left there. In the game, pick
**AMD FSR**. Games without FSR 3.1 get **HelixSR Scaler**, with HLX DLSS, as described below.

---

## What it manages

- **Setup in one click.** *Download and build* gets the latest HelixSR release from
  [GitHub](https://github.com/lonewolf0622/HelixSR/releases). It checks the release
  against the SHA-256 that GitHub publishes for it. Then it reads the exact URLs and SHA-256 sums that the
  release's setup scripts pin. It downloads what the PC still needs **in parallel**, and it verifies each file:

    - NVIDIA's DLSS 310.7.0 DLL, 59 MB, from NVIDIA's GitHub under NVIDIA's license
    - Microsoft's DirectX Shader Compiler, 25 MB
    - on read-only systems such as Bazzite, a portable Python with numpy, 67 MB

    It runs `helixsr-setup.sh --yes` with live output and imports the result as the payload. The payload is your
    copy of a HelixSR release, described below. The app deletes the DLSS DLL afterward. The downloads go into
    `~/.local/share/bc250-upscaler/work` and `~/.local/share/HelixSR`. The second folder is the script's own cache,
    and the setup uses it again next time.

    You can use a DLSS 310.7.0 DLL from a game you own instead. Check **Use a nvngx_dlss.dll already on this PC**
    and let *Find in Steam* find it. It compares checksums and offers only the exact build HelixSR pins. That skips
    NVIDIA's download. The downloads are not what takes time. The build is.

    The build itself is HelixSR's own script, unchanged. It takes about 5–6 minutes on a BC-250. That is because it
    compiles the network's shaders for both wave sizes through Proton. The Setup page shows the elapsed time.

    What the setup runs depends on the HelixSR version:

    - From HelixSR 1.7.0 on, the script ends with its own game installer, which asks about each Steam game. The app
      gives it no input. So it stops there, and only the network files are built.
    - From HelixSR 1.8.0 on, the network is built into HelixSR's DLL instead of two separate files. Deploy then
      copies only the DLL and the ini. It removes network files that an older release left next to the DLL.
    - From HelixSR 1.9.0 on, the script can also build frame generation for HelixSR Scaler, about 400 MB from
      NVIDIA. The app does not deploy that, so it skips this step (`--no-fg`).
    - HelixSR 2.x keeps its DLL in the release's `HelixSR-fsrfg` folder. Its `helixsr-setup.sh --yes` would install
      HelixSR Scaler into every game it finds. So for 2.x, the app runs what that script runs before its game
      installer. That is HelixSR's own builder (`setup/helixsr_setup.py`, unchanged) on `HelixSR-fsrfg`. It uses
      the same Python, shader compiler and Proton, and builds without frame generation (`--no-fg`). Then the app
      checks that the DLL carries the network.
    - For HelixSR 3.x, *Download and build* downloads the release, about 280 MB, checked against GitHub's SHA-256.
      It imports HLX FSR 4 from the release's `HLX-FSR4` folder, which comes built. Then it builds HLX DLSS's
      network into the release's `HelixSR/helixsr.dll` for HelixSR Scaler. It uses HelixSR's own builder, without
      frame generation. When that build fails, HLX FSR 4 is ready all the same, and the Setup page says why.

    *Native Vulkan kernels for HLX DLSS* is off by default. It builds the network for Vulkan too. Vulkan games then
    run HLX DLSS in Vulkan instead of through HelixSR Scaler's DirectX 12 bridge. The build then takes about 11
    minutes on a BC-250 instead of 5–6. HelixSR's builder downloads the Linux shader compiler for it once (13 MB).
    If you turn it on later, *Download and build* builds again. The Overview says whether the payload has them.
    Deploy again per game afterward.

    The whole release stays in the payload, because HelixSR Scaler and HelixSR's installer run from it. It is kept
    as hard links where it can, so it takes no second copy. Only the Deploy and Games pages change your games.
    When a later major version is out that the app does not support yet, the Setup page says so. The app then keeps
    getting the newest release it supports.

- **Version choice.** *Version* on the Setup page picks what *Download and build* gets. That is the latest HelixSR
  release, the default, or HelixSR 1.8.1. HelixSR's developer recommends 1.8.1 when the latest one does not work
  for you. In that case, please open an issue at [HelixSR](https://github.com/lonewolf0622/HelixSR/issues) with the
  game's `helixsr.log`. You find that file in the game folder. Switching builds the network files for that version
  and replaces the payload. Deploy again per game afterward. The Overview marks the games *Older build* or *Newer
  build*.

- **Update checks.** The app compares the payload with the latest HelixSR release on GitHub. It does that at start,
  with one small request, or when you click **Check now**. You can turn off the check at start. The app itself is
  updated through the BC250 Bazzite Suite portal.

    The Overview flags a newer HelixSR. Building again updates the payload, and deployed games then show *Older
    build*. After switching back to 1.8.1 they show *Newer build*. After a build the app offers to update them.
    *Update older games* on the Overview does the same, for older builds and for games whose own DLL is back. It
    keeps their `helixsr.ini`. *Download and build* needs about 1.5 GB free where it downloads and builds. It does
    not start with less.

- **Games.** The Games page lists every Steam game. It looks through each one in the background for an AMD FSR
  3.1 DLL. The games that have one come first, with HelixSR's state in each:

    - *Not installed*
    - *HelixSR x.y.z installed*
    - *x.y.z installed; a.b.c is available*, when the payload has a newer build
    - *The game put its own DLL back*

    The others are grayed out. Games that only offer DLSS, XeSS or FSR 2 can still use HelixSR through
    OptiScaler. *Open on Deploy page* takes them there.

    *Run with HelixSR*, or a double click, puts HelixSR in when it is missing or older. It does the same when a
    game update put the game's own DLL back. Then it starts the game through Steam
    (`steam://rungameid/<AppID>`). It asks before the first install into a game. It does nothing while the game
    runs, because HelixSR goes in before the game starts. Choose **AMD FSR** in the game.

- **Payload.** The payload is one imported HelixSR release, kept under `~/.local/share/bc250-upscaler/payload`. It
  holds the DLL, the two network files and the ini. The Setup page fills it. You can also fill it by hand. Run
  the release's `helixsr-setup.sh` yourself in that folder once, then import the folder or the zip. The script
  builds `helixsr_weights.bin` and `helixsr_kernels.pak` from NVIDIA's DLSS DLL. Those files are NVIDIA's
  property, so this app never ships them. They are for your own PC and are never part of this app or its
  releases. *Import release zip…* takes the download as is. The network files are then missing. They arrive once the
  setup has run and you import the folder. Only the known HelixSR files are copied. The payload survives updates and
  `./install.sh --uninstall`.

- **Deployments.** The app lists every place it put HelixSR in `~/.config/bc250-upscaler/deployments.json`. Each
  one has a live state:

    - *In place*
    - *Older build* or *Newer build*. The payload has changed since, so deploy again to update the game.
    - *Network files missing*
    - *Original restored*, when a game update or Steam put the game's own DLL back
    - *Removed*, or *Folder gone*

    *Forget entry* drops a line without touching the game. *Update older games* puts the payload's HelixSR into
    every deployment marked *Older build* or *Original restored*. It keeps the `helixsr.ini` there, and the game's
    backup. It leaves a game that is running alone. It does not touch deployments of a newer build, such as the
    fallback.

- **Three deploy modes.** The **How** box on the Deploy page offers them.

    - *Replace the selected DLL* is for games with native FSR 3.1. It is the way HelixSR is meant to go in. Pick
      the game folder. The app looks in `steamapps/common` of every Steam library in `libraryfolders.vdf`, also for
      the Flatpak Steam. It finds every upscaler DLL, backs it up and deploys. Unreal games bury the DLL under
      `Engine/Plugins/.../ThirdParty/Win64`. *Remove* deletes HelixSR's files and gives the `.original.dll` its
      name back. Deploying again over an existing deployment updates HelixSR's files. A newer build never
      overwrites the real original.

        With a HelixSR 3 payload, this mode puts in HLX FSR 4 under the game's file name. HLX FSR 4 lists the game's
        own FSR, the `.original.dll`, after its own upscalers. It uses the game's FSR when it cannot start itself. A
        game deployed with HelixSR 1 or 2 shows *Older build*. *Update older games* puts HLX FSR 4 in, and *Remove*
        puts the game's file back as before.

    - *HelixSR Scaler* is for games without FSR 3.1, with a HelixSR 3 payload. These are games with DLSS, XeSS or
      FSR 2, also DirectX 11 and Vulkan games. It takes the place of the stand-alone folder below. HelixSR Scaler is
      OptiScaler with HelixSR, and it runs HLX DLSS, the network the setup builds. Pick the game's folder. The app
      then has HelixSR's own installer put HelixSR Scaler next to the game's `.exe`. That installer is the bridge
      HelixSR Desktop uses.

        It goes in as `dxgi.dll`, which Proton loads without a launch option. When the game has its own `dxgi.dll`,
        it goes in under another name. The app then copies the Steam launch option it needs to the clipboard. The
        game's files it replaces are kept in `HelixSR-Scaler-backup`. `HelixSR-Scaler.files` lists what it put in.
        So HelixSR's own setup and HelixSR Desktop can update or remove it too, and the other way round.

        Pick **DLSS** in the game. **Insert** opens its menu. HelixSR's frame generation is not installed. *Remove*
        puts the game's files back. *Update older games* brings a newer HelixSR in and keeps the game's
        `OptiScaler.ini`.

    - *Stand-alone folder for OptiScaler* is for games without FSR 3.1, and it needs HelixSR 1 or 2. These are
      DLSS, XeSS and FSR 2 / 3.0 games that do not ship FSR 3.1 as a separate DLL.
      [OptiScaler](https://github.com/OptiScaler/OptiScaler) routes their upscaler calls to an FSR 3.1 DLL.
      HelixSR 3 has no DLL for this mode. The fallback on the Setup page brings one.

        The app writes a folder of its own, by default `<game>/HelixSR`. It holds the DLL under both FidelityFX
        names, the network files and the ini.

        With a payload from HelixSR 1.7.0 to 1.8.1, the app also installs OptiScaler next to the game's `.exe`.
        These releases ship the official OptiScaler, and 1.9.0 and newer do not. The fallback on the Setup page
        brings it. The payload keeps it when you switch back to the latest. Scan finds the folder of the game's
        `.exe`. OptiScaler goes there as `dxgi.dll`, with `fakenvapi`. If the game already has an OptiScaler, it
        takes that name. Its `OptiScaler.ini` points at the HelixSR folder. Select DLSS in the game. The app
        keeps what it replaces in the HelixSR folder's `backup`. That includes any `OptiScaler.ini` the game
        already had. *Remove* puts it back.

        Under Proton, OptiScaler only loads with `WINEDLLOVERRIDES="dxgi=n,b"` in the game's Steam launch options.
        So for a Steam game, the app adds that for every Steam user. It adds it to the launch options already
        there. When there are none, it sets `WINEDLLOVERRIDES="dxgi=n,b" %command%`. Steam writes its settings
        again when it closes, so Steam has to be closed for this. The app asks, closes Steam, sets the options and
        starts Steam again. In Game Mode, Steam stays open. The app then copies the line to the clipboard. You
        paste it into the game's *Properties* in Steam. *Remove* puts the launch options back as they were, unless
        you changed them since.

        Uncheck **Install OptiScaler next to the game's .exe** to install OptiScaler yourself, as its documentation
        describes. The page then gives you the `OptiScaler.ini` lines to paste:

        - `Dx12Upscaler=fsr31`
        - `FfxDx12Path`
        - `FfxDx12SRPath`

        The two paths are `Z:\` paths. These are Windows paths, and `Z:` is the Linux root under Proton. Then pick
        **FSR HelixSR (3.1.5)** in OptiScaler's FFX Upscaler menu.

        *Second upscaler* is optional and only for the OptiScaler folder. You can add another FidelityFX upscaler
        DLL, for example AMD's `amd_fidelityfx_upscaler_dx12.dll` with FSR 4. It goes into the folder as
        `amd_fidelityfx_upscaler_dx12.amd.dll`, with `UpscalerDll` pointing at it. OptiScaler's FFX Upscaler menu
        then lists its upscalers after HelixSR. The one you pick runs in that DLL.

- **helixsr.ini.** The helixsr.ini page is a form over every key HelixSR reads: `[Sharpening]`, `[ModelE]`,
  `[Log]` and `[Forwarding]`. It checks the values and shows a live preview. The preview keeps the comments of the
  payload's own `helixsr.ini`, and only the values change. Save it as the default for new deployments, or push it
  to an existing one. The keys are listed below.

    The page grays out what the payload's HelixSR version does not read. HelixSR 1.7 ignores `[Sharpening]` and
    `[ModelE] Network`. HelixSR 1.8 reads sharpening again, through `Sharpener` (`off`, `nvidia` or `rcas`),
    `Sharpness` and `UseGameSlider` instead of `Mode`.

## helixsr.ini keys

| Section | Key | Default | Meaning |
|---|---|---|---|
| [Sharpening] | Mode | off | *off* as in DLSS. *game* uses the game's FSR sharpness, or Sharpness if it sends none. *override* always uses Sharpness. |
| [Sharpening] | Sharpener | off | HelixSR 1.8+. *off* as in DLSS 4, *nvidia* for NVIDIA's sharpening filter, *rcas* for AMD FSR's. |
| [Sharpening] | Sharpness | 0.3 | 0–1, on the FidelityFX RCAS scale |
| [Sharpening] | UseGameSlider | false | HelixSR 1.8+. Follows the game's sharpness slider when it has one. |
| [Sharpening] | MotionAdaptive, MotionThreshold, MotionLimit, MotionReduction | true, 2, 16, 0.6 | Less sharpening on fast-moving pixels. The keys set where the reduction starts and where it is complete, in output pixels per frame, and how much it removes. |
| [ModelE] | Enabled | true | Runs the Model E network. Off, HelixSR uses a placeholder upscale. |
| [ModelE] | Network | auto | *auto* runs the main network at every ratio. On GPUs without matrix cores, that is about 30 % faster than NVIDIA's Ultra Performance network. *nvidia* picks as DLSS does. Or force *main* / *ultraperformance*. |
| [ModelE] | InvertJitter, InvertMotionVectors | false | For games whose jitter or motion vectors come out mirrored |
| [ModelE] | MotionVectorFrontEnd | false | Converts render-resolution motion vectors to display resolution first. HelixSR does that anyway when the game's vectors include the jitter. |
| [Log] | Enabled | true | Writes `helixsr.log` next to the DLL. The log names the network that runs and reports missing network files. |
| [Forwarding] | Dll | (auto) | The DLL for the other FidelityFX effects, such as frame generation. That is `amd_fidelityfx_dx12.original.dll` if present, else `amd_fidelityfx_framegeneration_dx12.dll`. |
| [Forwarding] | UpscalerDll | (empty) | A second FidelityFX upscaler DLL, such as AMD's with FSR 4. OptiScaler's menu lists it after HelixSR. |

Sharpening off costs nothing. Sharpening on costs about 0.4 ms at 4K on the BC-250.

## Privilege model

Everything runs as your normal desktop user. The game folders under Steam are yours. The payload and the deployment
list live in your XDG directories. The app uses no `pkexec`, no root and no `rpm-ostree` layering. It only copies,
renames and deletes files inside the game folders you point it at and inside its own payload folder. With
OptiScaler, it also changes the game's launch options in your Steam settings
(`userdata/<user>/config/localconfig.vdf`), and only that line.

## Requirements

```text
Python 3.11+
PyQt6>=6.11,<7
```

The PyQt6 wheels bundle Qt. HelixSR itself needs a game with an FSR 3.1 DX12 upscaler, or OptiScaler. It also needs
the network files that its `helixsr-setup.sh` builds. For the game side, see the
[HelixSR README](https://github.com/lonewolf0622/HelixSR#readme).

HelixSR is for RDNA 1 and newer. Its developer builds and tests it on the BC-250 (gfx1013, Mesa RADV, Proton). The
DLL that takes the place of a game's FSR 3.1 works in Direct3D 12 games. DirectX 11 and Vulkan games use HelixSR
Scaler, from HelixSR 3 on.

## Install on Bazzite

Install it from the BC250 Bazzite Suite portal, where it is under Graphics. You can also download
`bc250-upscaler-v<version>.tar.gz` from the suite's
[releases](https://github.com/RobertoTorino/bc250-bazzite/releases). Unpack it and run the installer:

```shell
tar -xzf bc250-upscaler-v*.tar.gz
cd bc250-upscaler-v*/
./install.sh
```

It installs the app for your user only. You get:

- a private venv with PyQt6, and the app under `~/.local/share/bc250-upscaler`
- the launcher `~/.local/bin/bc250-upscaler`
- a desktop entry and the icon
- a Desktop icon, which `./install.sh --no-desktop-shortcut` leaves out

**BC-250 Upscaler Manager** then appears in the application menu. You can also add it to Steam's Game Mode, via
*Add a Non-Steam Game*. To update, run `./install.sh` again from a newer release. `./install.sh --uninstall`
removes the app. It leaves the imported payload and the deployed games alone. `./install.sh --uninstall --purge`
also removes the payload and the settings. The list of deployed games stays. So a reinstalled app can still
restore them.

The installer takes over a copy installed under the app's former name, HelixSR Manager. Its payload, settings and
list of deployed games move to the new folders. Its launcher and menu entry go.

## Run from the repository

```shell
git clone https://github.com/RobertoTorino/bc250-bazzite.git
cd bc250-bazzite/apps/upscaler
python3 -m venv python && python/bin/pip install -r requirements.txt
PYTHONPATH=../../core python/bin/python -m upscaler
```

For development on a machine without Steam, three options point the app at other places:

- `--payload DIR` sets the payload folder
- `--deployments FILE` sets the deployment list
- `--work DIR` sets the download folder

`--no-update-check` skips the release lookup at start. `--version` prints the version.

## Pages

- **Overview** shows the payload status, with the version from the release's README, the DLL, the weights, the
  kernels and the ini. Its buttons are *Import release folder…*, *Import release zip…* and *Open payload folder*.
  The deployment table has *Open folder*, *Remove HelixSR from game*, *Forget entry* and *Update older games*.
  *Remove HelixSR from game* restores the original or deletes the stand-alone folder.
- **Setup** shows the release status for HelixSR, with *Check now*. You pick the version to get, latest or 1.8.1.
  For HelixSR 3 you can also pick *Native Vulkan kernels for HLX DLSS*. *Download and build* shows its progress
  and the script's output. The page also has *Cancel*, *Import built release*, *Open work folder* and the optional
  local `nvngx_dlss.dll`.
- **Games** lists every Steam game with its FSR 3.1 DLL and HelixSR's state. Its buttons are *Run with HelixSR*,
  *Open on Deploy page* and *Rescan*.
- **Deploy** lets you choose a Steam game, or **Browse…** to any folder, such as one of Heroic, Lutris or Bottles.
  It scans the folder for FSR 3.1 upscaler DLLs. Each one shows whether it is the game's own file or HelixSR, and
  whether the network files are next to it. Select the one the game loads, usually the only one. Then pick the
  mode and decide whether to write the current `helixsr.ini`. Deploy or remove. In folder mode the page shows the
  OptiScaler snippet with a *Copy OptiScaler.ini lines* button.
- **helixsr.ini** holds the settings form, the checks, the preview, *Save as payload default* and *Write to game*.
  *Save as payload default* makes the file the one Deploy starts from. *Write to game* replaces the ini of a chosen
  deployment.
- **Help** says what the app does, links to this chapter and shows where the app's files are.

The header shows four things. It refreshes every 5 seconds.

- the payload version
- the network-file status
- the deployments (ok / total)
- the number of Steam games found

## Good to know

- Steam verifies game files on updates and may put the game's own DLL back. The Overview then shows *Original
  restored*, and the backup stays. *Run with HelixSR* or *Update older games* puts HelixSR back.
- For per-stage GPU timings, set the launch option `HELIXSR_PROFILE=1 %command%`. HelixSR then writes them to
  `helixsr.log`.
- The app keeps its window size and page per user.

## Development

```
upscaler/
  __init__.py       app name, version, XDG paths
  __main__.py       entry point (python -m upscaler)
  backend.py        pure file logic: payload import, DLL discovery, deploy/remove (both modes),
                    helixsr.ini parse/render/validate, deployment store, Steam library discovery
  acquire.py        GitHub release lookup, pinned-source parsing, verified parallel downloads,
                    the build (QThread: helixsr-setup.sh for 1.x, HelixSR's builder for 2.x) and the
                    update checker
  setup_page.py     Setup page
  main_window.py    header, navigation, polling, confirmations, wiring of page signals to the backend
  pages.py          Overview, Deploy and helixsr.ini pages
  help.py           Help page
  widgets.py        status pills, metric boxes, rounded tooltip (shared with bc250-governor-manager)
bc250_core/         the suite's shared code (its steam.py closes and starts Steam), bundled by install.sh and
                    the release
  fonts/            Inter (SIL OFL), used for the header on Linux
install.sh          per-user installer (venv, launcher, desktop entry, icon); --uninstall removes it, keeps the payload
bc250-upscaler.desktop  desktop entry template, Exec is filled in by install.sh
tests/              pytest suite (offscreen Qt, temporary payload and game folders, no real HelixSR needed)
```

`./test.sh` in the suite's root runs every test suite, this one included. Extra arguments go to pytest, for example
`./test.sh -k ini`. For this app alone, run `pip install -r requirements-dev.txt`, then
`QT_QPA_PLATFORM=offscreen python -m pytest -q tests`. The tests cover:

- the `helixsr.ini` round-trip against the upstream file
- the payload import from folders and zips
- the DLL discovery
- deploy and remove in both modes, including deploying over an older build and refusing foreign DLLs
- the deployment store and the Steam library parsing
- the release lookup
- the whole Setup run, with downloads over `file://` URLs against a fake `helixsr-setup.sh` and a fake 2.x builder
- checksum and script failures, and a local DLSS DLL
- the main window, driven through its page signals

The suite's CI (`.github/workflows/ci.yml`) runs them on every push and pull request. Releases are tagged
`bc250-upscaler-v<x.y.z>` in the suite repository. `.github/workflows/release.yml` then builds the tarball and
publishes it on GitHub.

The backend has no Qt dependency, so you can run it from the command line or reuse it.

## License

The source and the issues are in the
[suite repository](https://github.com/RobertoTorino/bc250-bazzite/tree/main/apps/upscaler).

GPL-3.0-or-later, see [LICENSE](https://github.com/RobertoTorino/bc250-bazzite/blob/main/apps/upscaler/LICENSE).
The bundled Inter font is under the SIL Open Font License (`upscaler/fonts/Inter-LICENSE.txt`). HelixSR is a
separate project under its own license, the HelixSR Freeware License. This app ships none of it. HelixSR's network
files are derived from NVIDIA's DLSS, and this app never distributes them.
