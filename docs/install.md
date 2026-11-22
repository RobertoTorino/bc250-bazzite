<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-tray-arrow-down:</span>

# Install

Install the portal, not the apps one by one: it installs, updates and removes the apps for you. Run it as your own
user, not with `sudo`: the portal installs into your home folder, and only Board Test's copy to `/opt` asks for the
sudo password. In a terminal (Konsole), paste:

```bash
mkdir -p ~/Downloads/bc250-bazzite && cd ~/Downloads/bc250-bazzite &&
curl -fLO https://github.com/RobertoTorino/bc250-bazzite/releases/download/{{ portal_tag }}/{{ portal_tag }}.tar.gz &&
curl -fLO https://github.com/RobertoTorino/bc250-bazzite/releases/download/{{ portal_tag }}/SHA256SUMS &&
sha256sum --check SHA256SUMS &&
tar -xzf {{ portal_tag }}.tar.gz &&
./{{ portal_tag }}/install.sh
```

It downloads the portal, checks that the download is intact, unpacks it and installs it. Once installed,
`install.sh` removes the downloaded archive and `SHA256SUMS`; the unpacked folder stays. If a line fails, nothing
after it runs: fix what its message names and paste the block again. Prefer the browser? The same two files are on
the [portal's release page](https://github.com/RobertoTorino/bc250-bazzite/releases/tag/{{ portal_tag }}); extract
the archive beside them and run `install.sh` in the extracted folder.

This installs the portal in `~/.local/share/bc250-bazzite-suite/portal`, BC-250 Board Test and BC-250 Quickfix. Install
the other apps from the portal. The other releases on the Releases page (`bc250-gpu-v…`, `bc250-upscaler-v…` and so on)
are the app downloads the portal uses; you do not need them. What goes where and how to uninstall: [Portal](portal.md).

To test from a clone of the repository instead, run `./install.sh` in its root. The portal then installs every app
from the clone, so keep it where it is. `./install.sh --uninstall` removes it again, and asks about each other
installed app.

To uninstall the portal, run `~/.local/share/bc250-bazzite-suite/portal/install.sh --uninstall`. It removes the
portal, Board Test and Quickfix, and first asks about each other app that is installed.

What each app does: [The apps](apps/index.md).

## After a Bazzite update to a new Python

The apps run in Python venvs in your home folder. When a Bazzite update brings a new version of Python, a venv made
by the old one no longer finds its packages, and the portal and the apps stop starting. Run `./install.sh` again
where you installed from (the release folder or the clone): it makes the venv again. Then reinstall from the portal
any app that still does not start (Reinstall in its tile's menu).
