<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-tray-arrow-down:</span>

# Install

Install the portal, not each app on its own. The portal installs, updates and removes the apps for you. Run it as
your own user, not with `sudo`. The portal installs into your home folder. Only Board Test's copy to `/opt` asks for
the sudo password. Open a terminal (Konsole) and paste this block:

```bash
mkdir -p ~/Downloads/bc250-bazzite && cd ~/Downloads/bc250-bazzite &&
curl -fLO https://github.com/RobertoTorino/bc250-bazzite/releases/download/{{ portal_tag }}/{{ portal_tag }}.tar.gz &&
curl -fLO https://github.com/RobertoTorino/bc250-bazzite/releases/download/{{ portal_tag }}/SHA256SUMS &&
sha256sum --check SHA256SUMS &&
tar -xzf {{ portal_tag }}.tar.gz &&
./{{ portal_tag }}/install.sh
```

The block downloads the portal and checks that the download is intact. Then it unpacks the portal and installs it.
After the install, `install.sh` removes the downloaded archive and `SHA256SUMS`. The unpacked folder
stays. If a line fails, nothing after it runs. Fix what its message names, then paste the block again.

Prefer the browser? The same two files are on the
[portal's release page](https://github.com/RobertoTorino/bc250-bazzite/releases/tag/{{ portal_tag }}). Extract the
archive beside them. Then run `install.sh` in the extracted folder.

This installs the portal in `~/.local/share/bc250-bazzite-suite/portal`, BC-250 Board Test and BC-250 Quickfix.
Install the other apps from the portal. The Releases page also lists other releases, such as `bc250-gpu-v…` and
`bc250-upscaler-v…`. Those are the app downloads the portal uses, and you do not need them. What goes where and how
to remove it: [Portal](portal.md).

To test from a clone of the repository instead, run `./install.sh` in its root. The portal then installs every app
from the clone, so keep the clone where it is. `./install.sh --uninstall` removes the portal again. It asks about
each other app you installed.

To remove the portal, run `~/.local/share/bc250-bazzite-suite/portal/install.sh --uninstall`. It removes the
portal, Board Test and Quickfix. First it asks about each other app you installed.

What each app does: [The apps](apps/index.md).

## After a Bazzite update to a new Python

The apps run in Python venvs in your home folder. A venv is a private Python environment. A Bazzite update can bring
a new version of Python. A venv made by the old version then no longer finds its packages. The portal and the apps
stop starting. To fix this, run `./install.sh` again in the folder you installed from. That is the release folder
or the clone. It makes the venv again. If an app still does not start, reinstall it from the portal. Choose
**Reinstall** in its tile's menu.
