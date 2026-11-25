<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-tag-outline:</span>

# Releases

The **Nexus Release Tool** makes a release of the suite with one action, **Start new release**. NRT is its short
name. It lives in `dev/nrt/` in the repository. It is a window that walks you through the release, step by step.
The release does these things:

- It writes the versions, the CHANGELOG entries, the pins and the portal bump.
- It commits and pushes them.
- It starts the release on GitHub.
- It runs the device test on a board.

The tool commits and pushes only when you press a step's pill. It edits the checkout it lives in. So it is not in
the portal's releases, and it has no releases of its own. The tool is never released and has no version. The header
names the checkout's last commit and its time instead.

What a release involves, step by step, is in [apps.toml and releases](../portal.md#appstoml-and-releases).

## Start it

Start it from the repository's root, with the checkout's venv (`.venv-linux`). The venv is described in
[Set up and test](index.md#set-up-and-test). Nothing is copied when you install it. The menu entry always starts the
app of the checkout you installed it from. After you move the checkout, install it again.

```bash
tools/nrt.sh                                # open it (dev/nrt/run.sh)
tools/nrt.sh --list                         # the same overview in the terminal, with the system python3
dev/nrt/install.sh                         # app menu entry and Desktop icon
dev/nrt/install.sh --no-desktop-shortcut   # app menu entry only
dev/nrt/install.sh --uninstall             # remove them; the checkout stays
```

`tools/nrt.sh --install` and `tools/nrt.sh --uninstall` do the same as `dev/nrt/install.sh`. `--uninstall --purge`
also removes the settings.

## The release

You make a release of the suite on the tool's first tab, the release tab. It takes one action, **Start new
release**. The release holds what changed since the last release:

- each app that ships something new
- the portal
- core, when it changed

That one action writes everything a release needs. It writes the versions, the CHANGELOG entries, the pins and the
portal's version. So there is nothing to apply, pin or bump by hand.

The tab **Contents** lists what the release holds:

- each app that ships something new since its last release
- the portal
- core, when it changed since its last version

Some parts changed only in their version and their "Release x.y.z." entry since their last tag. Retract's
"Withdrawn:" entry counts the same way. Such a part ships nothing new and is not in the release. The version offered
first follows the CHANGELOG entries since the last tag:

- `Breaking.` makes a major version.
- `Added.` makes a minor version.
- `Fixed.` makes a patch version.

The rules are in [semantic versioning](architecture.md#versions-changelogs-and-releases). Type another version to
override it. The portal's version says **auto**. The tool works it out when it writes the release. It is at least
what the app releases need. You can type it too.

The release tab holds the release's steps. They are numbered in the order you do them, and each has its pill. The
signs beside the steps say where each one stands:

- The step you do now has an orange ▶, and its pill is lit.
- A step that is done has a green ✓.
- A step that failed has a red !.
- While a pill's command runs, its step has a teal ⋯.

The line beside each step says what there is to do. While a command runs, the line says what runs. For example,
**Push them** first runs CI's jobs of what you changed here, then pushes. The step is done when its command ends. Its
output is on the Commands tab. Only the lit pill does anything. So you never need a command or another tab. Every tab
explains itself behind the round **i** in its first row. Click it to read the whole explanation.

1. **Get up to date** (**git pull**): you need this step only when this checkout lacks commits that GitHub has.
   They come from a push from the other machine.
2. **Commit your changes:** the message field holds *see changelog*. Keep it, or type what the changes do. Then press
   **Commit**. The step stages every change and new file. It commits them after the version and manifest checks.
   First, the **Commands** tab lists the wiki's sections to read again (`tools/check_wiki.py`). That list never stops
   the commit. Sometimes `apps.toml` changed since the last portal release. An app was added, removed or withdrawn,
   or a pin moved. Then that check needs a portal bump, and the step asks first. It offers the higher of two
   versions:
    - the version the release would suggest, where the portal's CHANGELOG entries count and a Breaking entry makes
      it major
    - the least version the check accepts

    On a yes, it writes the version with its CHANGELOG entry, then commits. A no leaves the commit where it is.
3. **Push them** (**Push**): first, the commits from GitHub that this checkout lacks come in under your commits
   (`git pull --rebase --autostash`). An example is the last release's `Pin ...` commit. Then CI's jobs run here
   first (`tools/ci-local.sh`). GitHub knows nothing of this push yet. While the jobs run, two lines count the jobs
   done and name a job that failed. These are the step's line and the line under the header's pills. When a job
   fails, nothing is pushed and the step turns red. It shows the job's name and where its log is. Fix it, then commit
   and push. When the failure was no fault of the code, push again.
   Sometimes GitHub's servers fail during the push. Git then shows a line such as
   `! [remote rejected] main -> main (fatal error in commit_refs_rules)`. The step then says the fault is GitHub's.
   [githubstatus.com](https://www.githubstatus.com) may report it only minutes later. Wait a few minutes, then push
   again. When GitHub refuses the push for another reason, the step shows GitHub's reason.
4. **CI passes:** the step waits until GitHub's CI (`ci.yml`) passed on that commit. When CI failed, the line says
   so. When a test failed, fix it, then commit and push again. Sometimes the trouble is GitHub's own, such as an error
   of its servers or a job that never started. [githubstatus.com](https://www.githubstatus.com) says when Actions are
   degraded. Then **Run CI again** starts the failed jobs again on the same commit. Once you press it, it stays off
   for those runs until GitHub shows them running again. When a run fails again, you can start it again.
5. **Start new release:** when the wiki's Portal Tour is older than the portal, its window or its tiles, an
   orange banner above the steps says so. It holds **Record new video now** (`tools/record-tour.sh --wiki`). The
   recording takes a few minutes, and its output is on the Commands tab. The tour's voice needs Nexus TTS's speech
   engine. This step waits until the video is
   recorded.

    The release can start by itself, without the pill and its question. It does so when CI passes on the commit
    while the tool's window is open and waits for it. So check the versions on the Contents tab before then. A
    window opened on a commit whose CI passed earlier starts nothing by itself. Then check the versions and press the
    pill. `release/autostart=false` in the tool's settings turns starting by itself off.

    The step writes the release:

    - the versions and their copies
    - the `Release x.y.z.` entries
    - the new tags in `portal/apps.toml`
    - the portal's version and its entry

    It commits the release, pushes it and starts `.github/workflows/release.yml` on that commit. If the push stops,
    fix what it says. The pill then reads **Push and start**.

    The step fetches GitHub's tags and `main` first, for three reasons:

    - The portal is tagged on GitHub when you publish it.
    - The last release of each part is read from the tags.
    - A release ends with a `Pin ...` commit on `main`.

    When that fetch fails, the message gives git's own words. A tag here can point to another commit than GitHub's
    tag. Git then refuses to move it with "would clobber existing tag". The message names the tag and the two
    commands that drop it and fetch again. GitHub's tag is the one the release was published from. What came in is
    put under this checkout, and the versions are read again. The question before the step writes shows each part's
    version as it will be. Each version comes from the part's CHANGELOG entries since its last tag, as on the
    Contents tab. So nothing is bumped by hand. Type another version in the list only to
    override it.
6. **The release on GitHub:** `release.yml` starts at once on the release commit. Your release commit only writes the
   release. So the CI that passed on your commit in step 4 counts for it, and CI does not have to run again first
   ([below](#the-releases-on-github)). The run does these things:

    - It builds the new app releases side by side and publishes them.
    - It writes their checksums into `apps.toml` in a commit *Pin ...* on top of yours.
    - It builds the portal from that commit as a **draft**.

    A draft has no tag yet, so no installed portal sees it. The line links the run. A run that ends badly gives a
    notification and lights **Resume run**. Resume run skips what is out already and makes the draft anew. **Stop
    run** stops a run that must not go on. Stopping is safe until the portal is published.

    Sometimes the code must change for the run to pass, for example when CI failed on the release commit. Never start
    a new release then, because the release is written and pushed already. Fix the code. The steps then light
    **Commit your changes**, **Push them** and **CI passes** for the fix. Step 6 reads **Start again on this commit**.
    It runs the release as it is written, on the fix's commit.
7. **Device test,** on a BC-250: this step tests the draft portal (`tools/check-release.sh draft`). It does these
   things:

    - It downloads the draft portal with `gh`, because a draft needs the sign-in.
    - It checks the portal against its `SHA256SUMS`.
    - It installs the portal and starts it.

    Test it as a user would. When more than one portal of the run is still a draft, a choice beside Device test
    lists them. Device test, Publish, Not OK and the step's line follow the one you pick there. Work pushed in the
    meantime does not end the release. An example is a fix found during the device test. While its draft
    waits, Device test and Publish stay at hand for it.
8. **Publish** when it works: the draft becomes a release, which makes its portal tag. It becomes GitHub's
   **Latest** release. The installed portals offer it from then on. The same command fetches the new tag. So the step
   shows ✓ as soon as the command ends, and you press Publish once. A portal that was open during the device test
   shows its newest release as it was when it looked. **Y Check again** on its Settings page shows the release just
   published. So does the portal's hourly look.

    **Not OK** leaves the draft unpublished. The Device test step turns red and says what comes next. Fix what the
    test showed. The steps start again from **Commit your changes**, then **Push them**, **CI passes** and **Start
    new release**. Start new release builds the portal anew. A portal that was never published keeps its version, and
    the apps already out are skipped. Until the fix is committed, **Device test** and **Publish** stay at hand. They
    are there for a Not OK pressed by mistake.
9. **All runs finished:** there is nothing to press. Publish starts more runs on GitHub, the wiki and the runs on the
   portal's tag. The step waits until they all finished and names the ones still running. **git pull** of the next
   step stays off until then.
10. **Bring in the pin commit** (**git pull**): this is the last step. The *Pin ...* commit is on main. The tool knows
    of it once Publish fetched main, or once GitHub's runs on main show that commit. The step lights when GitHub runs
    nothing more. After the pull, its line reads *The release is out and pulled in. Ready.* Every step then shows ✓.

Above the steps, three boxes say how long a release takes up to its device test. They are **Previous release**,
**Current release** and the **Deviation** between the two.

- **Previous release** is the last release that went out before the one you are making. Its time is the one the
  tool measured for it. The tool may not have timed a release. Then it is GitHub's own time, its CI before Start and
  its release run. The box's tooltip says which.
- **Current release** is the release you are making. Its time starts with the first step you press. That is Get up
  to date, Commit, Push or Start new release. It ends when the release on GitHub passed. It adds up the time the steps
  work:
    - a command that runs on this computer
    - GitHub's CI on the commit
    - the release run

    The time the tool waits for you between two steps is not counted. Until you press a step, it shows a dash. When
    you close the tool and open it again during a release, it keeps the time worked until then.
- **Deviation** compares the current release with the previous one. When the current one takes over 2 minutes
  longer, an orange banner shows it too. Otherwise, it shows in its box only, also at 0 or less. The limit is
  `DEVIATION_LIMIT` in `dev/nrt/nexus_release_tool/flow.py`.

You can start the same run by hand, without the tool. This starts it on the newest pushed commit:

```bash
gh workflow run release.yml --ref main -f commit="$(git rev-parse origin/main)"
```

A run started again skips what is already published. You can also push a tag by hand with `tools/tag-release.sh`
(below). Such a tag is `bc250-<app>-v<x.y.z>` or `bc250-portal-v<x.y.z>`. It still releases that one app or portal,
and the release is published at once. The portal tag Publish makes starts `release.yml` too, as any pushed tag does.
That run sees that the release is published already and ends at once. The tool's steps follow only the run Start
started on main, never one on a tag.

## The window

The window has these tabs:

- **Nexus release**, the steps above
- **Contents**, what the release holds
- **Retract app**, a withdrawal ([below](#withdrawing-a-release))
- **Remove suite**
- **Commands**

**Remove suite** works on a BC-250. It opens a terminal that lists what of the suite is installed on the board
(`tools/check-release.sh status`). It also says whether a test put it there. Then it removes it all
(`tools/check-release.sh remove`):

- every app
- the portal
- Board Test

Each one is removed with its own uninstaller. Board Test asks for the sudo password. Settings, history and results
stay. `tools/check-release.sh remove --purge` removes them too.

**Device test** and the other tests of `tools/check-release.sh` clean up after themselves. What they do depends on
the board:

- On a board without the suite, what the test installs is marked as a test's. It is removed again when the portal
  closes. That covers the portal, Board Test and the apps installed during the test.
- On a board that had the suite installed, the test first saves the portal, Board Test and Quickfix. It puts them
  back when the tested portal closes, with the saved portal's own installer. Board Test asks for the sudo password.
  The apps installed during the test are removed. An app updated during the test stays updated.

`--keep` keeps what a test installed. After a test that was cut short, `tools/check-release.sh restore` puts the
saved install back by hand.

**Commands** shows what a step writes. These steps write there:

- the release
- Retract
- Test withdrawal
- Remove suite

Each step's output comes under a line that names the step. The commands' output is on the same tab. A
step that writes its log opens Commands. Open the step again to go on. The steps' logs also go into the day's
command log (below).

**The command line** in **Commands** runs a command in the checkout. So you need no separate terminal for the
commands the steps show. Type a command and press Enter. Its output appears above the line as it runs. **Commands**
lists the commands the last step showed (Retract's), one per line. Pick one to put it on the line, then check it and
press Enter. Up and Down bring back earlier commands, also from earlier sessions. **Stop** or Ctrl+C interrupts a
command, along with anything it started in the background. `clear` or **Clear** empties the output.

Each command runs with `bash -lc` in the folder the last `cd` left. Variables you set do not carry over to the next
command. A command cannot read input, so nothing can ask you something:

- git does not prompt for a password.
- git opens no editor, so commit with `-m`.
- git pages nothing.

For a command that must ask, use a terminal. The `check-release` script asks for the sudo password and keeps the
portal running. So it is handed to a terminal by itself when you run it from the line, and the output says so. A
command can change the checkout, such as a commit, a push or a tag. After it, the window reads the checkout again, as
**Refresh** does. Every command is also kept in a file of the day,
`~/.cache/nexus-release-tool/commands/commands-<YYYY-MM-DD>.log`. The file holds the command, its whole output and
how it ended (its exit code). So you can read again afterward what a step said. You can also send the file along
when a step went wrong.

**GitHub build** in the header shows whether GitHub built your last push. It shows every workflow run on its commit,
such as CI, Release and Wiki, tags included. It reads the newest 30 runs of the repository. A release of many apps
starts many runs. So when all 30 belong to your commit, it reads the rest of that commit's runs too. That way the CI
runs under them count. It shows these states:

- **Building** while a run runs
- **Passed** or **Failed** after that
- **Building** right after a push, until GitHub has started the runs of that commit

In that last state, the line under the pills says that it waits for GitHub. The runs GitHub lists then are those of
the commit before. Hover for each run. Click to open the run that failed, or still runs, on GitHub. GitHub may cancel
a run because a later run of the same workflow on the same commit took its place. That is no failure, and hover says
**replaced by a later run**.

GitHub build looks at these times:

- every 15 seconds while a build runs
- every 10 seconds after a push, until GitHub has started its runs, a few seconds after the push
- every 5 minutes otherwise

**Refresh** looks at once. Its pill reads *Refreshing…* while it reads the checkout and GitHub's runs. That takes a
second or two. Then it reads *Refreshed* with the time. When a run it saw running finishes, a desktop notification
says whether it passed. It needs no GitHub token. Answers that did not change do not count against GitHub's limit of
60 requests an hour.

The **ticker** under the pills says where the runs of that push stand. So you need not open GitHub to follow a
build. It shows these things:

- for each run that is still going, how many of its jobs are done
- each job that runs, with the step it is at (*pytest (core): Run tests (4/7)*)
- the time since the run started
- for a run that failed, its job and step
- for a run that passed, that it passed

The dot is blue while something runs. It is red when a run failed and green when all passed. The line wraps when it
is longer than the window is wide, so its end is always visible. Hover for every job of every run. Click to open the
job that runs, or failed, on GitHub. While a run has failed, **Run again** at its right starts that run's failed jobs
again on the same commit. It runs `gh run rerun <id> --failed` in the Commands tab. The jobs need a gh login
(`gh auth login`). With one, the ticker reads them every 10 seconds while a run goes. Without one, it shows the runs
only. So the 60 requests an hour stay for the **GitHub build** pill.

**GitHub status** beside it says whether GitHub itself works, as
[githubstatus.com](https://www.githubstatus.com/) reports it. The dot is green while every part of GitHub is up. It
is red while the page reports a problem:

- an open incident
- an incident GitHub is still monitoring after the page says All Systems Operational again
- a part such as Actions or Pages that is degraded or down

A build that waits in *queued* for long is often such a problem. Hover for the incident and the parts affected.
Click to open the status page. It looks every 5 minutes, and **Refresh** looks at once.

**Claude tokens today** says how many tokens Claude Code on this computer used since midnight. It reads them from
Claude Code's own transcripts in `~/.claude`, or in the folder `CLAUDE_CONFIG_DIR` names. Hover for these numbers:

- the last 5 hours
- the input, output and cache tokens
- each model

Click to open [Claude's usage page](https://claude.ai/settings/usage), which shows your plan's limits. Other
computers and claude.ai are not counted. Without Claude Code, the pill is not shown. It looks every 5 minutes, and
**Refresh** looks at once.

The notifications are the desktop's own, through `notify-send`. Without it, they come from the Nexus Release Tool
icon in the notification area. That icon appears with the first notification and goes when the window closes. A
click on the notification or the icon brings the window to the front.

A red line at the top of the window means that a release tag points at the wrong commit. That commit's `VERSION` is
not the tag's version. The tag was made before the version bump was committed. `release.yml` cannot build it. To
fix it, follow these steps:

1. Delete the tag. The line shows how.
2. Commit and push the bump.
3. Tag again with `tools/tag-release.sh`.

`tools/tag-release.sh <tag> [...]` tags HEAD and pushes the tags. It refuses in these cases:

- HEAD does not hold each tag's version, because the bump is not committed yet.
- The tag's folder has uncommitted changes.
- HEAD is not pushed to `origin/main`.
- CI did not pass on HEAD.

For CI, it asks GitHub (`tools/ci_state.py`). While CI still runs, it waits, up to an hour. A portal tag also waits
for the app releases it pins. Each one must be tagged on GitHub and pinned with its sha256. The pin comes from the
release's *Pin ...* commit, or from `tools/pin_app.py`. The portal's release needs them. A plain `git tag` tags
whatever HEAD is at that moment. That can be the commit from before the bump, or one CI failed. `release.yml` asks
the same before it builds anything. A tag on a commit CI did not pass gives no release. After the check,
`release.yml` builds and publishes the release without an approval on GitHub
(see [GitHub settings](github-settings.md#environments)). `tools/tag-release.sh --help` prints its usage.

`tools/nrt.sh --list` lists every app with its version, its last tag and its pin, without Qt.

## Withdrawing a release

You withdraw a release that must not be used anymore. The reason can be privacy, security or any other problem. The
release stays on GitHub, so its history is kept. But nothing installs it anymore. These are the steps:

1. In Nexus Release Tool, open the tab **Retract app**. Choose the app's pinned release, write why, and press
   **Retract**. This adds `withdrawn = "<reason>"` to its entry in `portal/apps.toml`. It also adds a CHANGELOG
   entry to the app. **Take back** removes it again.
2. Press **Test withdrawal** on the same tab, on a BC-250 with the app installed. It installs the portal from the
   checkout and starts it (`check-release.sh local`). The portal must say that the app is not available anymore. It
   must remove the app, and then show **App not available** on its tile.
3. Mark the release on GitHub with the command the tab shows: `gh release edit <tag> --prerelease --title
   "Withdrawn: <tag>" --notes "..."`. Every update check skips a pre-release, so no app offers it.
4. Release the portal on the release tab, from **Commit your changes**. The commit asks for the portal bump the
   withdrawal needs, at least a minor version. **Start new release** then releases the portal. The withdrawn app is
   not released again. The portal's CHANGELOG entry names the withdrawal. A portal that updates to it removes the
   app. The portal update button says so beforehand ("withdraws ...").

Board Test and Quickfix are always installed, so they cannot be withdrawn.

## Checking a release

You can build a release's tag yourself and compare it with the release `tools/build_release.py` built. The content
is the same, but the checksum usually is not. The gzip compression of a `.tar.gz` differs between zlib builds.
Fedora uses zlib-ng, and GitHub's Ubuntu runners use zlib. So compare the unpacked files, not the `.tar.gz`. Board
Test's build time in `board_test/_build_info.py` is the commit time too. Older Board Test releases recorded the
clock. There only that line differs.

```bash
git archive <tag> | tar -x -C /tmp/src
SOURCE_DATE_EPOCH=$(git log -1 --format=%ct <tag>) python3 /tmp/src/tools/build_release.py <tag> /tmp/local
curl -LO https://github.com/RobertoTorino/bc250-bazzite/releases/download/<tag>/<tag>.tar.gz
mkdir -p /tmp/a /tmp/b && tar -xzf <tag>.tar.gz -C /tmp/a && tar -xzf /tmp/local/<tag>.tar.gz -C /tmp/b
diff -r /tmp/a /tmp/b
```

The checksum pinned in `apps.toml` is always the one of the published release. That is also why the release tests
pin their own local builds instead of the published ones.

## The releases on GitHub

Each release's title names the suite and the app. It comes from the portal's name and `apps.toml`, and
`tools/build_release.py` writes it. Examples are *BC250 Bazzite Suite: Portal 12.0.0* and *BC250 Bazzite Suite:
Xenia Manager 0.11.0*. The tags start with the suite's prefix, `bc250-` (`TAG_PREFIX`). They are
`bc250-<app>-v<x.y.z>` and `bc250-portal-v<x.y.z>`.

The release workflow (**Release**, `release.yml`) builds and publishes a release. It starts in one of these ways:

- on a release commit, by **Start new release**
- by `gh workflow run`, above
- by a tag pushed by hand

Every push and pull request starts **CI** (`ci.yml`). On the Actions page, each run is titled with the push's commit
message.

A release builds only a commit that CI passed (`tools/ci_state.py`). The release commit is the exception, which
saves a second CI run on the same code. This holds when it changes nothing but what a release writes
(`tools/release_commit.py`):

- `VERSION` files and their copies
- `Release x.y.z.` and `Version x.y.z.` entries on top of the CHANGELOGs
- the `tag` and `sha256` lines of `apps.toml`

Then the CI that passed on its parent counts for it (`ci_state.py --release-commit`). The parent is the commit you
pushed before Start new release. Any other change in the release commit makes the release wait for CI on that commit
itself. A line of code or a file added is such a change. The release also waits when CI failed on the parent. The
release commit may fix what failed there, such as a version that CI wanted to be bumped. So its own CI decides. CI
still runs on the release commit, but nothing waits for it.

The portal's part downloads the checksums of the app releases the run just made. GitHub can miss a release for a
short while after it was made. The run then tries again every 10 seconds for a minute. After that, it stops and
names the release it did not find.

GitHub's **Latest** release is the newest portal. The app releases are published with `--latest=false`, so they are
never Latest. The portal becomes Latest when it is published. **Publish** does that for a draft, and `release.yml`
does it for a portal tag pushed by hand. The READMEs and this wiki link to `/releases/latest` for the download. So
that link always opens the newest portal. Installed portals and apps do not use it. They find their releases by
their tag prefix (`bc250-portal-v`, `bc250-<app>-v`). They read GitHub's release list page by page, with the newest
first, until a page holds the prefix.
