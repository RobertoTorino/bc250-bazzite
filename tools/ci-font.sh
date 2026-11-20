#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Bazzite's font (Noto Sans) on a GitHub runner, for the tests that measure a window and for the picture of the
# portal: the runner's own font is wider and lower. The font comes from Ubuntu's mirror, and a download from it
# that stalls is cut off and tried again: on 20-11-2026 two jobs of one run waited on the 13 MB package until the
# step's 5 minutes were over and failed before a test ran. Where the font is installed already (tools/ci-local.sh's
# image) nothing is asked of the mirror.
#
#   tools/ci-font.sh
set -euo pipefail

FONT=/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf
if [ -f "$FONT" ]; then
    echo "Noto Sans is installed already"
    exit 0
fi

apt_options=(-o Acquire::Retries=3 -o Acquire::http::Timeout=30 -o Acquire::https::Timeout=30)
# One try, cut off after $1 seconds: apt's own timeouts do not end a download that only slows down.
try() { sudo timeout -k 5 "$1" apt-get "${apt_options[@]}" "${@:2}"; }

# The runner's package lists usually name the font's version still, so the mirror is asked for the lists only when
# the install fails; an install that was cut off is put right before the next try.
for attempt in 1 2 3; do
    if try 45 install -y -q fonts-noto-core; then
        break
    fi
    [ "$attempt" -lt 3 ] || { echo "Ubuntu's mirror did not deliver fonts-noto-core in three tries" >&2; exit 1; }
    echo "Try $attempt failed or stalled: once more"
    sudo dpkg --configure -a || true
    try 40 update -q || true
done
fc-match sans | grep -F "Noto Sans"
