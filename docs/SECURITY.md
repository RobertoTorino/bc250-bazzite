<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-shield-lock-outline:</span>

# Security

## Reporting a vulnerability

Please don't open a public issue for a security problem. Use **Security → Report a vulnerability** in this
repository instead. That way we can fix the problem before it's public. You'll get an answer within a week.

## Verifying a download

Every release comes with a `SHA256SUMS` file. Check the download before you install it:

```bash
sha256sum --check --ignore-missing SHA256SUMS
```

Board Test also checks its test engine before every run. It refuses to run tests when someone changed the engine.

## Dependencies and known vulnerabilities

The suite answers for its own code and for the Python packages its apps install. Bazzite updates and patches its own
packages. These include the system tools some apps run, such as `systemctl`, `sudo` or `cec-ctl`.

[Nexus Deps](development/dashboard.md#deps) shows where the suite's dependencies stand on a board. It is a
development app that you run from a checkout of the repository. It shows these:

- **Python packages.** Nexus Deps reads them from the environment each installed app runs in. That is the suite's
  shared environment or the app's own. A card shows the version in each environment and the latest version on PyPI.
  It also shows whether the version meets what the app needs.
- **Known vulnerabilities.** Nexus Deps looks up each installed version in [OSV.dev](https://osv.dev). OSV.dev is
  the open database that collects the GitHub, PyPA and NVD advisories. A green **✓ CVE** means no known
  vulnerability. A red **✗ CVE** lists each one by its CVE ID, with the release that fixes it. Each ID links to
  [Snyk's vulnerability database](https://security.snyk.io/). The card says which version to update to and for
  which apps. **CVE ?** means the check could not run, for example without a network. It never counts as clean.
- **External tools.** Nexus Deps checks only whether they are available. For each tool it shows these:
    - whether it is installed
    - which apps need it
    - whether it needs root

    It doesn't look up their versions. They come with Bazzite or from their makers, and OSV.dev has no reliable
    record of those builds.

Its check changes nothing. It sends the names and versions of the Python packages to PyPI and OSV.dev, and
nothing else. Its **Fix** changes only what it lists and what you confirm. It can change these:

- the Python packages in an app's environment
- a missing tool an installed app needs, installed with Homebrew
- a missing tool an installed app needs, layered into the Bazzite image with rpm-ostree

When a package of an app has a known vulnerability, the card names the version with the fix. The fix reaches the
app through an app release that requires that version. If no release does yet, report it as described above.

## Root and passwords

- The apps run as your own user. Their installers refuse to run with sudo, and so do the bisect scripts. Only the
  steps that need root ask for your password. They ask through sudo in a terminal or pkexec in a desktop dialog.
- The installers put apps whose scripts run as root under `/opt`, owned by root. That way a normal user cannot
  change code that sudo runs. Board Test never runs a tool as root from a folder you can write to, such as
  `~/.local/bin`.
- [Nexus Deps](development/dashboard.md#deps) marks the tools that only work as root with **Needs root.**
- The portal asks before it installs or opens an app that changes how the board runs. Each of these apps is
  software-only, and you can undo what it does. Such an app changes one or more of these:
    - unlocks
    - clocks
    - voltages
    - firmware tables
    - the VRAM split
    - the patched driver
