#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Exercise portal/install.sh: from the checkout (through the root install.sh), from a release-shaped tree, the
# portal's own update from its state folder, uninstall and purge.
set -u
SUITE=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
NEXUS=$SUITE                        # the repository: the Nexus tools (stage_app.py) and core/
T=/tmp/bc250-portal-test
# shellcheck source=tools/installer-tests/shims.sh
source "$(dirname "${BASH_SOURCE[0]}")/shims.sh" "$T"; set +e
fail=0
check() { if eval "$2"; then echo "  ok   $1"; else echo "  FAIL $1"; fail=1; fi; }
D=$XDG_DATA_HOME
P=$D/bc250-bazzite-suite/portal        # the installed portal
S=$D/bc250-bazzite-suite/state         # what it remembers
logs=()
V=$(cat "$SUITE/portal/VERSION")
NEXT="${V%.*}.$(( ${V##*.} + 1 ))"   # a later portal release, for the update in step 2
BT="bc250-check-v$(tr -d '[:space:]' < "$SUITE/apps/check/VERSION")"   # the bundled releases
HB="bc250-helpers-v$(tr -d '[:space:]' < "$SUITE/apps/helpers/VERSION")"

echo "== 1. install from the suite checkout, with the install.sh at its root"
bash "$SUITE/install.sh" > "$T/log1" 2>&1; rc=$?; logs+=("$T/log1")
check "exit 0" "[ $rc -eq 0 ]"
check "portal installs apps from the checkout" "[ \"\$(cat $P/suite-checkout)\" = \"\$(cd $NEXUS && pwd -P)\" ]"
check "portal in the home folder without the dependency checker catalog" "[ -f $P/bc250_portal/__main__.py ] && [ -f $P/apps.toml ] && [ ! -e $P/dependencies.toml ]"
check "nothing of the portal in /opt" "[ ! -e $T/opt/bc250-bazzite-suite ] && [ -z \"\$(ls -d $T/opt/bc250-bazzite-suite-v* 2>/dev/null)\" ]"
check "no staging folder left" "[ ! -e $D/bc250-bazzite-suite/.portal.new ]"
check "core bundled with portal" "[ -f $P/bc250_core/platform.py ]"
check "no tests in the copy" "[ ! -d $P/tests ]"
check "the sound is in the copy" "[ -s $P/bc250_portal/sounds/bigpicture.wav ] && [ ! -e $P/bc250_portal/sounds/swoosh.wav ]"
check "the controller reader is in the requirements" "grep -q '^pygame-ce' $P/requirements.txt"
check "check installed too" "[ -f $T/opt/bc250-board-test/test-board.sh ] && [ -x $HOME/.local/bin/bc250-board-test ]"
check "check has its manual" "cmp -s $SUITE/docs/apps/check.md $T/opt/bc250-board-test/MANUAL.md"
check "helpers installed too" "[ -f $D/bc250-helpers/app/helpers/__main__.py ] && [ -x $HOME/.local/bin/bc250-helpers ]"
check "the venv users" "[ -f $D/bc250-bazzite-suite/venv-users/bc250-bazzite-suite ] && [ -f $D/bc250-bazzite-suite/venv-users/bc250-board-test ] && [ -f $D/bc250-bazzite-suite/venv-users/bc250-helpers ]"
check "portal launcher" "grep -qF 'm bc250_portal' $HOME/.local/bin/bc250-bazzite-suite"
check "desktop icons" "[ -x $HOME/Desktop/bc250-bazzite-suite.desktop ] && [ -x $HOME/Desktop/bc250-board-test.desktop ]"
check "records say local" "grep -q '\"check\": \"local\"' $S/installed.json && grep -q '\"helpers\": \"local\"' $S/installed.json"
check "portal imports its bundled core" "(cd $P && /usr/bin/python3 -c 'import bc250_core, os, sys; sys.exit(0 if os.path.abspath(bc250_core.__file__).startswith(\"$P\") else 1)')"
check "manifest parses on Linux python" "(cd $P && /usr/bin/python3 -c 'import tomllib; d=tomllib.load(open(\"apps.toml\",\"rb\")); assert list(d[\"apps\"])[0]==\"check\"')"

echo "== 2. release-shaped tree: portal staged + bundled check and helpers, no desktop icons"
R="$T/release/bc250-portal-v$NEXT"; rm -rf "$T/release"; mkdir -p "$T/release"
/usr/bin/python3 "$NEXUS/tools/stage_app.py" portal "$R" > /dev/null
/usr/bin/python3 "$NEXUS/tools/stage_app.py" check "$R/bundled/$BT" > /dev/null
/usr/bin/python3 "$NEXUS/tools/stage_app.py" helpers "$R/bundled/$HB" > /dev/null
sed -i "s/^__version__ = \"$V\"\$/__version__ = \"$NEXT\"/" "$R/bc250_portal/__init__.py"
(cd "$T/release" && tar -czf "bc250-portal-v$NEXT.tar.gz" "bc250-portal-v$NEXT")      # the tarball beside it, as a download leaves it
(cd "$T/release" && sha256sum "bc250-portal-v$NEXT.tar.gz" > SHA256SUMS)
SUM=$(sha256sum "$T/release/bc250-portal-v$NEXT.tar.gz" | cut -c1-64)
bash "$R/install.sh" --no-desktop-shortcut > "$T/log2" 2>&1; rc=$?; logs+=("$T/log2")
check "exit 0" "[ $rc -eq 0 ]"
check "the tarball's sha256 is kept beside the program" "[ \"\$(cut -c1-64 $P/build.sha256)\" = $SUM ]"
check "the tarball and its SHA256SUMS are removed" "[ ! -e $T/release/bc250-portal-v$NEXT.tar.gz ] && [ ! -e $T/release/SHA256SUMS ] && [ -f $R/install.sh ]"
check "the new portal version replaced the old" "grep -q '^__version__ = \"$NEXT\"' $P/bc250_portal/__init__.py"
check "the release has the sound" "[ -s $P/bc250_portal/sounds/bigpicture.wav ]"
check "bundled/ not copied" "[ ! -d $P/bundled ]"
check "portal installs apps from releases" "[ ! -e $P/suite-checkout ]"
check "records have the bundled tags" "grep -q '\"check\": \"$BT\"' $S/installed.json && grep -q '\"helpers\": \"$HB\"' $S/installed.json"
check "helpers from the bundled release" "[ -f $D/bc250-helpers/app/bc250_core/__init__.py ]"
check "desktop icons removed" "[ ! -e $HOME/Desktop/bc250-bazzite-suite.desktop ] && [ ! -e $HOME/Desktop/bc250-board-test.desktop ] && [ ! -e $HOME/Desktop/bc250-helpers.desktop ]"

echo "== 3. the portal's own update: a release unpacked in the state folder, installed from there"
U="$S/portal-update/bc250-portal-v$NEXT"; mkdir -p "$S/portal-update"; cp -r "$R" "$U"
echo picture > "$S/wallpaper.png"
(cd "$U" && ./install.sh --no-desktop-shortcut) > "$T/log2b" 2>&1; rc=$?; logs+=("$T/log2b")
check "exit 0" "[ $rc -eq 0 ]"
check "the portal is installed, the state untouched" "[ -f $P/bc250_portal/__main__.py ] && grep -q '\"check\": \"$BT\"' $S/installed.json && [ -f $S/wallpaper.png ]"
check "run again without its tarball: the build is still recorded" "[ \"\$(cut -c1-64 $P/build.sha256)\" = $SUM ]"
# A tarball beside a SHA256SUMS of another download: the tarball goes, that SHA256SUMS stays.
(cd "$S/portal-update" && tar -czf "bc250-portal-v$NEXT.tar.gz" "bc250-portal-v$NEXT" && echo "$SUM  other.tar.gz" > SHA256SUMS)
(cd "$U" && ./install.sh --no-desktop-shortcut) > "$T/log2d" 2>&1; rc=$?; logs+=("$T/log2d")
check "another download's SHA256SUMS is kept" "[ $rc -eq 0 ] && [ ! -e $S/portal-update/bc250-portal-v$NEXT.tar.gz ] && grep -q other.tar.gz $S/portal-update/SHA256SUMS"
# An earlier portal kept its downloads in what is the portal's own folder now: the copy replaces the folder the
# update runs from, after Board Test is installed from it.
U="$P/portal-update/bc250-portal-v$NEXT"; mkdir -p "$P/portal-update"; cp -r "$R" "$U"
(cd "$U" && ./install.sh --no-desktop-shortcut) > "$T/log2c" 2>&1; rc=$?; logs+=("$T/log2c")
check "from inside the portal's folder: exit 0, the portal installed" "[ $rc -eq 0 ] && [ -f $P/bc250_portal/__main__.py ] && [ ! -e $P/portal-update ] && [ -x $HOME/.local/bin/bc250-bazzite-suite ]"

echo "== 4. uninstall keeps the venv for another suite app and the wallpaper, drops the state of apps that are gone"
touch "$D/bc250-bazzite-suite/venv-users/bc250-governor-manager"
mkdir -p "$S/releases/governor-v0.0.1" "$S/releases/local-bios"
bash "$P/install.sh" --uninstall > "$T/log3" 2>&1; rc=$?; logs+=("$T/log3")
check "exit 0" "[ $rc -eq 0 ]"
check "portal gone, check gone from /opt" "[ ! -e $P ] && [ -z \"\$(ls $T/opt)\" ]"
check "launchers gone" "[ ! -e $HOME/.local/bin/bc250-bazzite-suite ] && [ ! -e $HOME/.local/bin/bc250-board-test ] && [ ! -e $HOME/.local/bin/bc250-helpers ] && [ ! -e $D/bc250-helpers ]"
check "venv kept, only governor left" "[ -x $D/bc250-bazzite-suite/venv/bin/python ] && [ \"\$(ls $D/bc250-bazzite-suite/venv-users)\" = bc250-governor-manager ]"
check "mentions what is left" "grep -q 'Still installed: bc250-governor-manager' $T/log3"
check "the wallpaper kept, the records and releases of the apps that are gone dropped" "[ -f $S/wallpaper.png ] && [ ! -e $S/installed.json ] && [ ! -e $S/releases ]"
rm "$S/wallpaper.png" "$S/portal-update" -r

echo "== 5. reinstall and purge as the last user"
rm "$D/bc250-bazzite-suite/venv-users/bc250-governor-manager"
mkdir -p "$T/log/bc250-board-test" && touch "$T/log/bc250-board-test/bc250-test-results-20260101-000000.log"
bash "$R/install.sh" > "$T/log4" 2>&1 && bash "$P/install.sh" --uninstall --purge >> "$T/log4" 2>&1; rc=$?; logs+=("$T/log4")
check "exit 0" "[ $rc -eq 0 ]"
check "suite data dir gone" "[ ! -e $D/bc250-bazzite-suite ]"
check "check results gone" "[ ! -e $T/log/bc250-board-test ]"
check "/opt empty" "[ -z \"\$(ls $T/opt)\" ]"

echo "== 6. uninstall asks about each other app: cancel, then skip one and uninstall the others"
# The others: overlay and bios as the portal installs them from the checkout, and datstation, installed the same
# way. Then bios and datstation are dropped from the installed portal's manifest, as a newer portal drops an app: bios
# keeps its record and release folder (the portal's), datstation neither (found by its own installed copy under
# ~/.local/share). Nexus Installer Tests (dev/itests, a Nexus app), installed from the checkout too, is not the
# portal's (no Development tab, owner 27-10-2026): the portal's uninstall leaves it.
bash "$SUITE/install.sh" > "$T/log5" 2>&1; logs+=("$T/log5")
for app in overlay bios datstation; do
    /usr/bin/python3 "$NEXUS/tools/stage_app.py" "$app" "$S/releases/local-$app" > /dev/null
    (cd "$S/releases/local-$app" && bash install.sh) >> "$T/log5" 2>&1
done
bash "$NEXUS/dev/itests/install.sh" --no-desktop-shortcut >> "$T/log5" 2>&1
rm -rf "$S/releases/local-datstation"
/usr/bin/python3 - "$S/installed.json" "$P/apps.toml" <<'PY'
import json, re, sys
from pathlib import Path
data = json.load(open(sys.argv[1]))
data.update({"overlay": "local", "bios": "local"})
json.dump(data, open(sys.argv[1], "w"))
manifest = Path(sys.argv[2])
text = manifest.read_text(encoding="utf-8")
for key in ("bios", "datstation"):                # dropped from this portal's manifest
    text = re.sub(rf"^\[apps\.{key}\]\n(?:(?!^\[).*\n)*", "", text, flags=re.M)
manifest.write_text(text, encoding="utf-8")
PY
installed() { [ -x "$HOME/.local/bin/$1" ]; }
check "the apps are installed" "installed bc250-system-overlay && installed bc250-bios-reader && installed bazzite-datstation && installed nexus-installer-tests"
check "two of them dropped from the installed manifest" "! grep -q 'apps.bios' $P/apps.toml && ! grep -q 'apps.datstation' $P/apps.toml && grep -q 'apps.overlay' $P/apps.toml"
mkdir -p "$S/releases/overlay-v0.0.1"   # an older release it was updated from
printf 'y\nc\n' | BC250_INTERACTIVE=1 bash "$SUITE/install.sh" --uninstall >> "$T/log5" 2>&1; rc=$?
check "cancel: exit 1" "[ $rc -eq 1 ]"
check "cancel: nothing removed" "installed bc250-system-overlay && installed bc250-bios-reader && installed bazzite-datstation && installed nexus-installer-tests && installed bc250-bazzite-suite && installed bc250-board-test"
check "cancel: says so" "grep -q 'Canceled: nothing was uninstalled.' $T/log5"
printf 'x\ns\ny\ny\n' | BC250_INTERACTIVE=1 bash "$SUITE/install.sh" --uninstall >> "$T/log5" 2>&1; rc=$?
check "exit 0" "[ $rc -eq 0 ]"
check "asked about overlay three times (the cancel run, an unknown answer), bios twice, datstation once, Installer Tests never" "[ \$(grep -o 'Uninstall BC-250 System Overlay?' $T/log5 | wc -l) -eq 3 ] && [ \$(grep -o 'Uninstall BC-250 BIOS Reader?' $T/log5 | wc -l) -eq 2 ] && [ \$(grep -o 'Uninstall Bazzite DatStation?' $T/log5 | wc -l) -eq 1 ] && ! grep -q 'Uninstall Nexus Installer Tests?' $T/log5"
check "skipped app stays" "installed bc250-system-overlay && [ -d $S/releases/local-overlay ]"
check "chosen app gone" "! installed bc250-bios-reader && [ ! -e $S/releases/local-bios ]"
check "Installer Tests stays: the checkout's, not the portal's" "installed nexus-installer-tests"
check "dropped app without a record gone" "! installed bazzite-datstation && [ ! -e $D/bazzite-datstation/app ]"
check "record drops the chosen app" "! grep -q bios $S/installed.json && grep -q overlay $S/installed.json"
check "record and folder of check gone" "! grep -q check $S/installed.json && [ ! -e $S/releases/local-check ]"
check "older release of the skipped app gone" "[ ! -e $S/releases/overlay-v0.0.1 ]"
check "portal, check and helpers gone" "! installed bc250-bazzite-suite && ! installed bc250-board-test && ! installed bc250-helpers"
check "mentions what is left" "grep -q 'Still installed: bc250-system-overlay' $T/log5"
(cd "$S/releases/local-overlay" && bash install.sh --uninstall) >> "$T/log5" 2>&1
bash "$NEXUS/dev/itests/install.sh" --uninstall >> "$T/log5" 2>&1

echo "== 7. after an uninstall that kept nothing, no suite folder is left"
bash "$SUITE/install.sh" > "$T/log6" 2>&1 && bash "$P/install.sh" --uninstall >> "$T/log6" 2>&1
rc=$?; logs+=("$T/log6")
check "exit 0" "[ $rc -eq 0 ]"
check "suite data dir gone (settings stay in ~/.config)" "[ ! -e $D/bc250-bazzite-suite ]"

echo "== 8. --uninstall --all: one confirmation for the whole suite, no question per app"
bash "$SUITE/install.sh" > "$T/log7" 2>&1; logs+=("$T/log7")
for app in overlay bios; do
    rm -rf "$S/releases/local-$app"
    /usr/bin/python3 "$NEXUS/tools/stage_app.py" "$app" "$S/releases/local-$app" > /dev/null
    (cd "$S/releases/local-$app" && bash install.sh) >> "$T/log7" 2>&1
done
mkdir -p "$XDG_CONFIG_HOME/bc250-system-overlay" && echo x > "$XDG_CONFIG_HOME/bc250-system-overlay/settings.ini"
check "both apps installed, overlay has settings" "installed bc250-system-overlay && installed bc250-bios-reader && [ -f $XDG_CONFIG_HOME/bc250-system-overlay/settings.ini ]"
bash "$SUITE/install.sh" --all > "$T/log7a" 2>&1; rc=$?
check "--all without --uninstall refused" "[ $rc -ne 0 ] && grep -q 'only goes with --uninstall' $T/log7a"
bash "$SUITE/install.sh" --uninstall --all < /dev/null >> "$T/log7" 2>&1; rc=$?
check "without a terminal: refused, nothing removed" "[ $rc -ne 0 ] && grep -q 'needs a terminal' $T/log7 && installed bc250-system-overlay && installed bc250-bazzite-suite"
printf 'n\n' | BC250_INTERACTIVE=1 bash "$SUITE/install.sh" --uninstall --all >> "$T/log7" 2>&1; rc=$?
check "no: canceled, nothing removed" "[ $rc -eq 1 ] && grep -q 'Canceled: nothing was uninstalled.' $T/log7 && installed bc250-system-overlay && installed bc250-bios-reader && installed bc250-bazzite-suite"
check "the warning names every app" "grep -q 'WARNING: --all removes the whole suite from this computer: BC-250 System Overlay, BC-250 BIOS Reader, with the portal, Board Test and Helpers.' $T/log7"
check "asks once, not per app" "grep -q 'Are you sure you want to delete everything permanently?' $T/log7 && ! grep -q 'Uninstall BC-250 System Overlay?' $T/log7"
printf 'y\n' | BC250_INTERACTIVE=1 bash "$SUITE/install.sh" --uninstall --all --purge >> "$T/log7" 2>&1; rc=$?
check "yes: exit 0" "[ $rc -eq 0 ]"
check "the warning says the settings go too" "grep -q 'WARNING: --purge removes their settings' $T/log7"
check "everything gone, the apps' settings too" "! installed bc250-system-overlay && ! installed bc250-bios-reader && ! installed bc250-bazzite-suite && ! installed bc250-board-test && [ ! -e $XDG_CONFIG_HOME/bc250-system-overlay ] && [ ! -e $D/bc250-bazzite-suite ]"
check "nothing left to mention" "! grep -q 'Still installed' $T/log7"

[ $fail -eq 0 ] && echo "ALL OK" || for l in "${logs[@]}"; do echo "--- $l"; cat "$l"; done
exit $fail
