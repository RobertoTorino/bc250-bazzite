<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# Contributing

Bug reports, ideas and pull requests are welcome. Report security problems privately, as the
[security policy](docs/SECURITY.md) says. Do not report them in an issue or a pull request.

## Licenses

Each app keeps its own `LICENSE`. What you contribute to a folder is under that folder's license:

- GPL-3.0-or-later: the suite, the portal, `core/`, `tools/` and most apps
- MIT: BC-250 Persistent ACPI (`apps/acpi`)
- AGPL-3.0-or-later: BC-250 PS Remote Play (`apps/consoles`), whose ported protocol code is AGPL-3.0-only

Icons and sounds are under the license of the folder they are in, the same as the code. Contribute only what you may
license that way. That is your own work, or work under a compatible license. For work under a compatible license,
name its source and license in the pull request. Say so when you made something with generative AI tools.

## Icons

Every app in a category has the same icon. A new or changed icon goes in `icons/<category>/`. The file
`icons/categories.toml` names each app's category. Then `python3 tools/sync_icons.py` writes the copies that the apps,
the portal and the wiki use. **Convert icons** in Nexus Dashboard for BC-250 does the same from a window. The wiki's
[Architecture and consistency](docs/development/architecture.md#icons) page describes it. It also says how to build a
new app.

## Before a pull request

- Add a CHANGELOG entry. A change to one app goes in that app's own CHANGELOG. A change to the whole suite goes in
  the root `CHANGELOG`. The format is a `Changelog: DD-MM-YYYY HH:MM:SS` line (Europe/Amsterdam time), a blank line,
  then plain sentences starting with `Breaking.`, `Added.` or `Fixed.`.
- Leave `VERSION` files and `portal/apps.toml` as they are. Versions and releases are the maintainer's.
- Run the checks CI runs: `tools/ci-local.sh` (podman), or at least `./test.sh`.
