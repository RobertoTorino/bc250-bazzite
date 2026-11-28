<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-eye-off-outline:</span>

# Privacy

The BC250 Bazzite Suite collects nothing about you. It has no accounts, statistics, analytics, crash reports or
advertising. We run no server that anything could go to. What the apps store stays on the board, in your home
folder. The list below names the few things that go over the network, with when and to whom.

Everything about the suite itself is public. The code, the plans and the issues are on
[GitHub](https://github.com/RobertoTorino/bc250-bazzite). Personal data is the exception. The apps keep it out of
what they show and save where they can.

## What goes over the network

Each request names the app and its version, for example `bc250-shadps4-manager/0.1.5`. It says nothing about you.
A request for cover art names only the suite, as `bc250-bazzite-suite`. The servers see your IP address, as any
website you open does.

**GitHub** (`github.com`, `api.github.com`, `raw.githubusercontent.com`) serves the releases:

- The [portal](portal.md) downloads the apps you install from the suite's releases. At start, it asks whether a
  newer portal release is out.
- The shadPS4, RPCS3, PPSSPP, PCSX2, Vita3K and Xenia Managers ask for the emulator's newest release when their
  window opens. They download the release you install.
- [BC-250 Upscaler Manager](apps/upscaler.md), [BC-250 Mesh Shaders](apps/mesh.md) and the
  [GPU Manager](apps/gpu.md) look for a newer release of what they install at start. You can turn this off in each
  app's settings.

**Sony** (`fwupdater.dl.playstation.net`): [BC-250 Controller](apps/controller.md#the-firmware-update) asks Sony's
update server for the controllers' latest firmware when its window opens. It asks at most once a day, and you can
turn this off. It downloads the firmware when you update a controller.

**PyPI and OSV.dev**: [Nexus Dependencies](development/dashboard.md#deps) is a development app that you run from a checkout
of the repository. It sends the names and versions of the Python packages in the apps' environments. It learns from
them whether newer versions or known vulnerabilities exist. The rest of its cards work like this:

- Its Bazzite card reads Bazzite's update state on the board itself and sends nothing.
- Its cards of the machine's updates, and its hourly reminder, ask each source's own tool what is newer. These
  tools are rpm-ostree, Flatpak, Homebrew, rustup and pip.
- Those tools talk to their own servers, as they do when you run them yourself.
- Its mprime card reads mersenne.org's download page.
- Its cards of the emulators and the PlayStation firmware ask GitHub for each emulator's latest release. They ask
  Sony for its firmware lists and read its system software pages (`www.playstation.com`). They send nothing about the board.

Installing an app downloads its Python packages from PyPI.

**Only when you ask for it:**

- [BC-250 PS Remote Play](apps/consoles.md#privacy) talks to your own consoles on your own network. It talks to
  PlayStation (PSN) only for **Find my account ID**. The sign-in happens in your browser. Its window masks your
  account ID, online ID and the consoles' addresses.
- [BC-250 XB Remote Play](apps/clb.md#privacy) talks to Microsoft's XBOX services when you sign in, refresh, wake a
  console or stream. The sign-in happens in your browser. Its log masks the account's tokens, your gamertag, the
  consoles' IDs and network addresses.
- [BC-250 shadPS4 Manager](apps/shadps4.md#shadnet) lets shadPS4 sign in to the shadNet server you set, with the account
  you set. shadPS4 keeps the password unchanged, and shadNet sends it unencrypted. Use a password you use nowhere
  else.
- [BC-250 SFTP Tools](apps/sftp.md) connects only to the host you enter.
- The emulator managers take the games' pictures for Steam from SteamGridDB (`www.steamgriddb.com`). They do this
  only with an API key you enter. [Covers from SteamGridDB](apps/covers.md) has the details.
- [BC-250 Quickfix](apps/quickfix.md) downloads mprime from mersenne.org when you use its **Prime95** pill.
- [Bazzite DatStation](apps/datstation.md#privacy) loads the PlayStation Blog's feed on its PS News page.
- [BC-250 Board Test](apps/check.md) resolves and pings `google.com` in its network test. It also asks
  `www.example.com` for a page header. The optional speed test uses Ookla's servers and about 1 GB of data.
- The [portal](portal.md) shows the weather in its status only for a place you choose on its Settings page. The
  name you search for goes to Open-Meteo (`geocoding-api.open-meteo.com`, `api.open-meteo.com`). After that, the
  place's coordinates go there every 30 minutes while the portal is not minimized. Open-Meteo needs no account.
  When you click the weather, Brave Browser opens the place's forecast at `wttr.in`. That sends the place's
  coordinates to wttr.in.
- [BC-250 Turing Screen](apps/turing.md#settings) shows the weather only for a place you choose. The name you search
  for goes to Open-Meteo (`geocoding-api.open-meteo.com`, `api.open-meteo.com`). After that, the place's
  coordinates go there every 30 minutes while the screen shows its Weather tile. Open-Meteo needs no account.
- [BC-250 Webcam](apps/webcam.md#the-firmware) downloads the camera's firmware from GitHub
  (`raw.githubusercontent.com`) only when you click Download.
- [BC-250 ACE Queues](apps/ace.md) and [BC-250 Mesh Shaders](apps/mesh.md) download Mesa's source
  from `archive.mesa3d.org` when they build their driver.

Links you click open in your browser, under that site's own privacy terms. Examples are a release page, the wiki and
a PlayStation page.

## What stays on the board

Each app keeps its settings in `~/.config/<app>`. It keeps its data and logs in `~/.local/share/<app>`. Each chapter
has the exact list. The apps upload none of it. Removing an app with `--purge` removes the settings and logs too.

Some of what the apps store can identify you:

- host names and usernames
- serial numbers
- MAC and IP addresses
- account IDs

An app that shows or saves such details masks them:

- [Board Test](apps/check.md) masks them in saved logs. This is on by default, in **Settings › Privacy**.
- [BC-250 PS Remote Play](apps/consoles.md#privacy) masks them in its window and log.
- [BC-250 XB Remote Play](apps/clb.md#privacy) masks them in its log.

An app that shows a path on its screen or writes one in its log writes your home folder as `~`. So your username is
not in it. Before you share a log or a screenshot, for example in an issue, look it over. Remove anything you would
rather keep to yourself.

## This wiki

GitHub Pages serves the wiki. So GitHub's
[privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement)
applies to your visit, as it does on any GitHub page. The wiki itself adds no analytics and no cookies. Its fonts
and scripts come from the wiki, not from other sites. The theme keeps a little state, such as the search, in your
browser's session storage. That state stays in your browser, and your browser clears it when you close it.

## A privacy problem

We withdraw an app release with a privacy problem. The portal stops offering it and removes it from the boards, as
[the portal](portal.md) describes. To report a problem, open an issue on
[GitHub](https://github.com/RobertoTorino/bc250-bazzite/issues). If it should stay private until we fix it, use
**Security → Report a vulnerability** as the [security policy](SECURITY.md) says. Leave personal data out of the
report.
