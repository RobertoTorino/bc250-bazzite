<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-github:</span>

# GitHub settings

This page lists the repository's settings on GitHub, and the reason for each. Use them as a starting point
for a new project. They suit a repository where one person pushes straight to `main`. Releases come from a release
commit or a tag.

## Features

Open **Settings → General** and scroll down to the section **Features**. It comes after the repository name and the
social preview.

| Feature | Setting | Why |
|---|---|---|
| Wikis | Off | The documentation is this wiki (`docs/`), built and checked by `mkdocs build --strict`. A GitHub wiki is a separate repository outside CI. Search engines skip it on small repositories. |
| Issues | On | Bug reports and feature requests. |
| Discussions | Off | Issues cover it. Turn it on for questions and reports that are not bugs. |
| Projects | Off | Not used. |

Also under **Settings → General**, find the section **Pull Requests**. Check **Automatically delete head branches**
there.

## The About box

Click the ⚙ next to **About** on the repository's front page. It is not in Settings.

- **Website:** check **Use your GitHub Pages website**. The address of the wiki then shows on the front page.
- **Topics:** the keywords people search and browse by, such as `bazzite`, `bc250`, `amd`, `linux-gaming`,
  `fedora-atomic`, `universal-blue` and `pyqt6`. Add only topics that really describe the project.

## Pages

**Settings → Pages.** Set the source to **GitHub Actions**. Then `.github/workflows/docs.yml` builds the wiki and
publishes it at <https://robertotorino.github.io/bc250-bazzite/>.

## Rulesets

**Settings → Rules → Rulesets.** These rules guard against mistakes without getting in the way of daily work.

**Release tags:** make one tag ruleset with **New ruleset → New tag ruleset**. You choose its name, such as
`release-tags`.

- Target tags: **Add target → Include by pattern** `*-v*`. That covers every app and portal tag (`bc250-portal-v1.1.3`,
  `bc250-gpu-v0.4.0`).
- Rules: **Restrict deletions** and **Block force pushes**. Then nobody can delete a released tag or move it to
  another commit. Leave **Restrict creations** off, or the rules block new release tags too.
- Bypass list: **Repository admin**, set to **Always allow**. An admin can still delete a tag and push it again on
  another commit when one really has to move. The rules hold everyone else.

The pins in `portal/apps.toml` name a tag and the sha256 of its asset. So a released tag must never move.

**The main branch:** make one with **New branch ruleset**.

- Target: **Include default branch**.
- Rules: **Restrict deletions** and **Block force pushes**, nothing else.
- Bypass list: **Repository admin**, set to **Always allow**. An admin can still force-push or delete `main` when
  it really has to change. The rules hold everyone else.

Direct pushes keep working. Rules that require pull requests or passing checks would block them, so they stay off.

## Environments

**Settings → Environments.** The release workflow (`release.yml`) runs in no environment. So a release needs no
approval on GitHub. The workflow builds and publishes it at once, from a release commit or from a tag on a commit
that CI passed.
An environment `release` left from before is no longer used. You can delete it.

Two things guard a release:

- Only someone who may push to the repository can start the release workflow or push a tag.
- The release workflow builds only a commit that CI passed.

## Actions

**Settings → Actions → General.**

- **Actions permissions:** choose **Allow RobertoTorino, and select non-RobertoTorino, actions and reusable
  workflows**. Check only **Allow actions created by GitHub**. The workflows use only `actions/*`, so they keep
  working. A third-party action fails until you allow it on purpose.
- **Require actions to be pinned to a full-length commit SHA:** off. The workflows refer to actions by version
  (`actions/checkout@v7`). This setting would fail every run until each `uses:` line names a commit hash.
- **Workflow permissions:** **Read repository contents**. A workflow that needs more asks for it in its own
  `permissions:` block:
    - `release.yml` writes releases
    - `docs.yml` publishes the wiki
    - `upstream.yml` writes the Upstream review issue

    `release.yml` also uses that token to push its *Pin ...* commit to main and to make the app tags. The rulesets
    allow this as they are. No rule covers new tags. The rules guard main only against deletion and force pushes.

## Security

**Settings → Advanced Security.**

- **Private vulnerability reporting:** on. The [Security policy](../SECURITY.md) sends people to it. With it off,
  that link fails.
- **Dependabot alerts** and **Dependabot security updates:** on.
- **Dependabot version updates:** set in `.github/dependabot.yml`. Once a week one pull request updates the
  actions the workflows use. Nothing changes until you merge it.

## Dependabot's pull requests

Dependabot opens two kinds of pull request:

- **Version updates**, from `.github/dependabot.yml`. Once a week, one pull request covers all the actions the
  workflows use. Its title reads like *ci: bump the actions group with 5 updates*.
- **Security updates**, from the setting above. They come when a security advisory names a dependency anywhere in
  the repository. That holds whether `dependabot.yml` lists it or not. An example is a Rust crate in PS Remote
  Play's `native/` folder. Its title reads like *Bump pyo3 from 0.25.1 to 0.29.0 in /apps/consoles/native*.

A pull request starts from `main` as `main` stood that day. `main` moves on while the pull request waits. Its checks
still show the result on that old commit. Go through these steps before merging one:

1. **Is it still needed?** Look at the file it changes on `main`, such as `Cargo.toml` and `Cargo.lock` or a
   workflow. If `main` already has that version or a newer one, close the pull request. Comment
   `@dependabot close`, or use **Close pull request** at the bottom of its Conversation tab. **Archive** in
   GitHub's notifications only hides the notification. The pull request stays open.
2. **Bring it up to date:** comment `@dependabot rebase`. *No conflicts* only means git can combine the files. It
   does not mean anyone tested the result. GitHub calls a pull request *unstable* while a check fails.
3. **Wait for CI on the rebased commit.** A failure from the old base that `main` has since fixed goes away. A
   failure that stays comes from the update. Leave the pull request open and fix the code first, or close it.
4. **Merge** once every check is green. Then run `git pull`, because the merge commit exists only on GitHub until
   then.
5. **Write the CHANGELOG entry**, which Dependabot doesn't do. A workflow's entry goes in the root `CHANGELOG`. The
   entry for an app's dependency goes in that app's own. An app's dependency reaches users only with that app's next
   release.

A command to Dependabot is the whole comment, nothing else: `@dependabot rebase`, not `@dependabot rebase on PR #2.`

Dependabot may answer *the branch … is protected* or *Something went wrong on our end*. Then the branch ruleset
covers more than `main`. A rebase force-pushes Dependabot's branch, and **Block force pushes** stops it. **Restrict
deletions** also keeps the branch after the merge. Set the ruleset's target to **Include default branch** only, as
in [Rulesets](#rulesets). Then comment `@dependabot rebase` again.

The release workflow runs only for a release, so CI does not test a change to it. The next release is the first run
on the new action versions. Watch it.

From a terminal, signed in with `gh` (see [The GitHub CLI](#the-github-cli)):

```bash
gh pr list --author app/dependabot             # Dependabot's open pull requests
gh pr checks <number>                          # its checks
gh pr comment <number> --body "@dependabot rebase"
gh pr merge <number>
gh pr close <number> --comment "main already has this version"
```

Dependabot answers these comments too:

- `@dependabot recreate` starts the pull request over and drops any edits.
- `@dependabot ignore this major version` stops pull requests for that major version.
- `@dependabot ignore this dependency` stops pull requests for that dependency.

## GitHub's API limit

GitHub's API answers a limited number of requests an hour:

- **60 without signing in**, counted per network address. Everything on your network that asks GitHub without
  signing in shares them.
- **5,000 when signed in**.

Answers that did not change since the last look ("304 Not Modified") do not count.

Nexus Release Tool asks the API whether the newest push built. It asks every 15 seconds while a build runs, and every
5 minutes otherwise. A running build with a busy hour of other requests can use up the 60.

The window shows how many requests you have left in **GitHub API left**, beside its GitHub build pill. Its tooltip
reads like *GitHub API: 4,894 of 5,000 left until 04:16, signed in*. When none are left, the pill says **Limited**.
Its tooltip then says *GitHub's limit is reached, back at …*, and the tool waits until then.

**Nothing is broken when the limit is reached**, and there is nothing to fix. GitHub answers again after the time
shown. To get the 5,000, sign in once with the GitHub CLI:

```bash
brew install gh
gh auth login
```

Nexus Release Tool then uses that login (`gh auth token`). A `GITHUB_TOKEN` or `GH_TOKEN` variable takes its place.
The app sends the token only to GitHub's API and never stores it. To see the limit as it stands right now:

```bash
curl -s https://api.github.com/rate_limit                                            # without signing in
curl -s -H "Authorization: Bearer $(gh auth token)" https://api.github.com/rate_limit # signed in
```

## The GitHub CLI

`gh` reads and steers the workflows from a terminal, signed in as above. It works from the checkout, so start it
there. These are the commands a release needs most.

The runs of the last push, and one run's jobs. The `<run id>` is the number in the list:

```bash
gh run list --limit 10
gh run view <run id>
gh run watch <run id>                       # follows it until it ends
```

The runs on one commit. `--commit` needs the full SHA, not the short one `git log` shows, so let git expand it:

```bash
gh run list --workflow CI --commit "$(git rev-parse HEAD)"
gh run list --workflow Release --commit "$(git rev-parse bfd16e3)" --limit 30
```

Whether CI passed on a commit, as `tools/tag-release.sh` and the release workflow ask it:

```bash
python3 tools/ci_state.py "$(git rev-parse HEAD)"
```

Why a run failed. The first command shows the log of its failed steps only. The second shows one job's full log,
with the `<job id>` from `gh run view`:

```bash
gh run view <run id> --log-failed
gh run view --job <job id> --log
```

A job that hangs keeps its log until it ends. Cancel the run to read it. Then run what failed again, on the same
commit:

```bash
gh run cancel <run id>
gh run rerun <run id> --failed
```

Start the release workflow on the newest pushed commit, as **Start new release** does:

```bash
gh workflow run release.yml --ref main -f commit="$(git rev-parse origin/main)"
```

A release, its files and its notes:

```bash
gh release view bc250-gpu-v0.4.0
gh release download bc250-gpu-v0.4.0 --pattern SHA256SUMS --output -
```
