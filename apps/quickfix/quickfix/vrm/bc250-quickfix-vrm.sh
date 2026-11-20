#!/usr/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# BC-250 Quickfix (VRM Sensors): loads the bc250_vrm module, and builds it first when there is none for the running
# kernel. bc250-quickfix-vrm.service runs it as root at every boot, so a new kernel gets its own build at its first
# boot. Its folder (the argument; /var/lib/bc250-quickfix/vrm) holds src/, the module's source, and one folder named
# after the kernel it was built for.
set -eu

DIR="${1:-/var/lib/bc250-quickfix/vrm}"
KERNEL="$(uname -r)"
MODULE="$DIR/$KERNEL/bc250_vrm.ko"

if [ -d /sys/module/bc250_vrm ]; then
    echo "bc250_vrm is loaded already."
    exit 0
fi

if [ ! -f "$MODULE" ]; then
    KDIR="/lib/modules/$KERNEL/build"
    if [ ! -f "$KDIR/Makefile" ]; then
        echo "The kernel's build files for $KERNEL are missing ($KDIR): the module cannot be built." >&2
        exit 1
    fi
    for tool in make gcc; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "$tool is missing: the module cannot be built." >&2
            exit 1
        fi
    done
    BUILD="$(mktemp -d "$DIR/build.XXXXXX")"
    trap 'rm -rf "$BUILD"' EXIT
    cp "$DIR"/src/* "$BUILD"/
    echo "Building bc250_vrm for $KERNEL"
    make -C "$KDIR" M="$BUILD" modules
    # One build is kept: the running kernel's. An older kernel that is booted again builds its own again.
    find "$DIR" -mindepth 1 -maxdepth 1 -type d ! -name src ! -name "$(basename "$BUILD")" -exec rm -rf {} +
    mkdir -p "$DIR/$KERNEL"
    cp "$BUILD/bc250_vrm.ko" "$MODULE"
fi

echo "Loading $MODULE"
insmod "$MODULE"
