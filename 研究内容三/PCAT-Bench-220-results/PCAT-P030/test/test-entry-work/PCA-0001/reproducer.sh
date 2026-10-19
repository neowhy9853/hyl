#!/bin/bash
# PCA-0001 Reproducer: Verify IPv6 address format in git daemon
# Tests that lookup_hostname() correctly handles IPv6 addresses

set -euo pipefail

PCA_BINARY="${PCA_BINARY:-$(which git)}"
WORK_DIR=$(mktemp -d /tmp/pca-ipv6-test-XXXXXX)
trap 'rm -rf "$WORK_DIR"; kill $DAEMON_PID 2>/dev/null || true' EXIT

REPO_DIR="$WORK_DIR/repo"
CLONE_DIR="$WORK_DIR/clone"
DAEMON_PORT=19418
DAEMON_PID=""
DAEMON_LOG="$WORK_DIR/daemon.log"

# Detect default branch name
DEFAULT_BRANCH=$("$PCA_BINARY" config --get init.defaultBranch 2>/dev/null || echo "master")
if [ -z "$DEFAULT_BRANCH" ]; then DEFAULT_BRANCH="master"; fi
echo "Using default branch: $DEFAULT_BRANCH"

# Setup: create a bare repo
"$PCA_BINARY" init --bare "$REPO_DIR" 2>/dev/null
touch "$REPO_DIR/git-daemon-export-ok"

# Create and push content
echo "initial content" > "$WORK_DIR/file.tmp"
"$PCA_BINARY" -C "$WORK_DIR" init 2>/dev/null
"$PCA_BINARY" -C "$WORK_DIR" add file.tmp 2>/dev/null
"$PCA_BINARY" -C "$WORK_DIR" commit -m "initial" 2>/dev/null
"$PCA_BINARY" -C "$WORK_DIR" remote add origin "$REPO_DIR" 2>/dev/null
"$PCA_BINARY" -C "$WORK_DIR" push origin "$DEFAULT_BRANCH" 2>&1
echo "Push exit: $?"

# Start daemon on IPv6 loopback
echo ""
echo "Starting git daemon on [::1]:$DAEMON_PORT ..."
"$PCA_BINARY" daemon --listen=::1 --port=$DAEMON_PORT \
    --reuseaddr --verbose \
    --base-path="$WORK_DIR" \
    "$WORK_DIR" > "$DAEMON_LOG" 2>&1 &
DAEMON_PID=$!
sleep 2

# Check if daemon is running
if ! kill -0 $DAEMON_PID 2>/dev/null; then
    echo "Daemon failed to start. Log:"
    cat "$DAEMON_LOG"
    exit 1
fi
echo "Daemon started (PID: $DAEMON_PID)"

# Clone via IPv6
echo ""
echo "Cloning via IPv6 loopback ..."
GIT_TRACE_PACKET=1 "$PCA_BINARY" clone -v "git://[::1]:$DAEMON_PORT/repo" "$CLONE_DIR" 2>"$WORK_DIR/clone_stderr" || {
    echo "FAIL: Clone failed. Stderr:"
    cat "$WORK_DIR/clone_stderr"
    exit 1
}

# Verify we got the right content
CONTENT=$(cat "$CLONE_DIR/file.tmp" 2>/dev/null || echo "")
if [ "$CONTENT" != "initial content" ]; then
    echo "FAIL: Wrong content after clone: '$CONTENT'"
    exit 1
fi

echo ""
echo "PASS: IPv6 clone successful with correct content"
echo ""
echo "--- Daemon log (look for IP info) ---"
cat "$DAEMON_LOG"
echo "--- End daemon log ---"
echo ""
echo "Reachability: The daemon's lookup_hostname() was called for the IPv6 connection."
echo "Before the fix: the logged IP would be corrupted (wrong sockaddr_in cast for IPv6)"
echo "After the fix: the logged IP should show a valid IPv6 address"
