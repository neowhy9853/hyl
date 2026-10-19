#!/bin/bash
# Test sideband output format change (PCA-0001)
# Compares before/after raw stderr output in both pipe and TTY modes
set -e

TEST_RESULT_DIR="/home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/compatibility-testing"
WORK_DIR="$TEST_RESULT_DIR/test-entry-work/PCA-0001/runs"
BEFORE_GIT="/tmp/pca-git-before/git"
AFTER_GIT="/tmp/pca-git-after/git"
RESULTS_FILE="$WORK_DIR/results.txt"

echo "=== Sideband Output Format Compatibility Test ===" > "$RESULTS_FILE"
echo "Before binary: $BEFORE_GIT" >> "$RESULTS_FILE"
echo "After binary: $AFTER_GIT" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Create test repository with a remote that will generate sideband output
setup_repos() {
    local server_repo="/tmp/pca-test-server"
    local client_repo="/tmp/pca-test-client"
    rm -rf "$server_repo" "$client_repo"

    # Create server repo
    mkdir -p "$server_repo"
    "$BEFORE_GIT" -C "$server_repo" init --bare

    # Create client repo with some commits
    mkdir -p "$client_repo"
    "$BEFORE_GIT" -C "$client_repo" init
    "$BEFORE_GIT" -C "$client_repo" config user.email "test@test.com"
    "$BEFORE_GIT" -C "$client_repo" config user.name "Test"
    echo "initial" > "$client_repo/file.txt"
    "$BEFORE_GIT" -C "$client_repo" add file.txt
    "$BEFORE_GIT" -C "$client_repo" commit -m "initial commit"
    "$BEFORE_GIT" -C "$client_repo" remote add origin "$server_repo"
    "$BEFORE_GIT" -C "$client_repo" push origin master

    echo "$client_repo"
}

cleanup() {
    rm -rf /tmp/pca-test-server /tmp/pca-test-client /tmp/pca-test-output
}

echo "=== 1. Setup test repositories ===" >> "$RESULTS_FILE"
CLIENT_REPO=$(setup_repos)
echo "Server: /tmp/pca-test-server, Client: $CLIENT_REPO" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Test 1: Pipe mode (dumb terminal) - should have identical output
echo "=== Test 1: Pipe mode (stderr redirected) ===" >> "$RESULTS_FILE"
echo "Expected: identical output between before and after" >> "$RESULTS_FILE"

# Before: fetch with piped stderr
BEFORE_PIPE_OUTPUT=$(mktemp)
BEFORE_PIPE_EXIT=0
"$BEFORE_GIT" -C "$CLIENT_REPO" fetch origin 2>"$BEFORE_PIPE_OUTPUT" || BEFORE_PIPE_EXIT=$?
echo "Before exit code: $BEFORE_PIPE_EXIT" >> "$RESULTS_FILE"

# After: fetch with piped stderr
AFTER_PIPE_OUTPUT=$(mktemp)
AFTER_PIPE_EXIT=0
"$AFTER_GIT" -C "$CLIENT_REPO" fetch origin 2>"$AFTER_PIPE_OUTPUT" || AFTER_PIPE_EXIT=$?
echo "After exit code: $AFTER_PIPE_EXIT" >> "$RESULTS_FILE"

echo "Before stderr (pipe):" >> "$RESULTS_FILE"
cat "$BEFORE_PIPE_OUTPUT" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "After stderr (pipe):" >> "$RESULTS_FILE"
cat "$AFTER_PIPE_OUTPUT" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

if diff -q "$BEFORE_PIPE_OUTPUT" "$AFTER_PIPE_OUTPUT" > /dev/null 2>&1; then
    echo "PIPE MODE: PASS (output identical)" >> "$RESULTS_FILE"
else
    echo "PIPE MODE: DIFFERS (output changed)" >> "$RESULTS_FILE"
    diff "$BEFORE_PIPE_OUTPUT" "$AFTER_PIPE_OUTPUT" >> "$RESULTS_FILE" 2>&1 || true
fi
echo "" >> "$RESULTS_FILE"

# Test 2: Fetch from server with advice/hint messages to trigger sideband
echo "=== Test 2: Fetch with sideband messages (pipe mode) ===" >> "$RESULTS_FILE"

# Create a new commit on server and push it
"$BEFORE_GIT" -C "$CLIENT_REPO" commit --allow-empty -m "second commit"
"$BEFORE_GIT" -C "$CLIENT_REPO" push origin master

# Now fetch again - the remote output should trigger sideband
BEFORE_FETCH_OUT=$(mktemp)
AFTER_FETCH_OUT=$(mktemp)

"$BEFORE_GIT" -C "$CLIENT_REPO" fetch origin 2>"$BEFORE_FETCH_OUT" || true
"$AFTER_GIT" -C "$CLIENT_REPO" fetch origin 2>"$AFTER_FETCH_OUT" || true

echo "Before fetch stderr:" >> "$RESULTS_FILE"
cat "$BEFORE_FETCH_OUT" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "After fetch stderr:" >> "$RESULTS_FILE"
cat "$AFTER_FETCH_OUT" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

if diff -q "$BEFORE_FETCH_OUT" "$AFTER_FETCH_OUT" > /dev/null 2>&1; then
    echo "FETCH PIPE MODE: PASS (output identical)" >> "$RESULTS_FILE"
else
    echo "FETCH PIPE MODE: DIFFERS" >> "$RESULTS_FILE"
    diff "$BEFORE_FETCH_OUT" "$AFTER_FETCH_OUT" >> "$RESULTS_FILE" 2>&1 || true
fi
echo "" >> "$RESULTS_FILE"

# Test 3: TTY mode simulation using 'script' command
echo "=== Test 3: TTY mode (PTY simulation via script) ===" >> "$RESULTS_FILE"
echo "Note: This tests the ANSI escape sequence position change" >> "$RESULTS_FILE"

# Use script(1) to create a PTY and capture raw output
TTY_BEFORE_OUT=$(mktemp)
TTY_AFTER_OUT=$(mktemp)

if command -v script > /dev/null 2>&1; then
    # Check if script supports -q (quiet mode)
    SCRIPT_OPTS="-q"
    script $SCRIPT_OPTS -c "$BEFORE_GIT -C $CLIENT_REPO fetch origin 2>&1 || true" "$TTY_BEFORE_OUT" > /dev/null 2>&1 || true
    script $SCRIPT_OPTS -c "$AFTER_GIT -C $CLIENT_REPO fetch origin 2>&1 || true" "$TTY_AFTER_OUT" > /dev/null 2>&1 || true

    echo "Before TTY raw output:" >> "$RESULTS_FILE"
    xxd "$TTY_BEFORE_OUT" | head -50 >> "$RESULTS_FILE" 2>&1 || true
    echo "" >> "$RESULTS_FILE"
    echo "After TTY raw output:" >> "$RESULTS_FILE"
    xxd "$TTY_AFTER_OUT" | head -50 >> "$RESULTS_FILE" 2>&1 || true
    echo "" >> "$RESULTS_FILE"

    # Check for ANSI clear-to-eol sequence (\033[K = 1b 5b 4b)
    BEFORE_ANSI_COUNT=$(xxd "$TTY_BEFORE_OUT" | grep -c "1b5b.*4b" 2>/dev/null || echo 0)
    AFTER_ANSI_COUNT=$(xxd "$TTY_AFTER_OUT" | grep -c "1b5b.*4b" 2>/dev/null || echo 0)
    echo "ANSI sequences found - Before: $BEFORE_ANSI_COUNT, After: $AFTER_ANSI_COUNT" >> "$RESULTS_FILE"
else
    echo "script command not available, skipping TTY test" >> "$RESULTS_FILE"
fi
echo "" >> "$RESULTS_FILE"

# Test 4: Run existing git test suite for sideband-related tests
echo "=== Test 4: Existing test suite regression ===" >> "$RESULTS_FILE"

# Run the sideband-related tests from AGENTS.md
# t5516-fetch-push.sh is the primary test for fetch/push sideband
echo "Running t5516-fetch-push.sh (before)..." >> "$RESULTS_FILE"
BEFORE_TEST_LOG=$(mktemp)
make -C /tmp/pca-git-before/t -j4 NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 t5516-fetch-push.sh 2>&1 > "$BEFORE_TEST_LOG" || true
echo "Before test results:" >> "$RESULTS_FILE"
tail -5 "$BEFORE_TEST_LOG" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

AFTER_TEST_LOG=$(mktemp)
echo "Running t5516-fetch-push.sh (after)..." >> "$RESULTS_FILE"
make -C /tmp/pca-git-after/t -j4 NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 t5516-fetch-push.sh 2>&1 > "$AFTER_TEST_LOG" || true
echo "After test results:" >> "$RESULTS_FILE"
tail -5 "$AFTER_TEST_LOG" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

echo "" >> "$RESULTS_FILE"
echo "=== Test Summary ===" >> "$RESULTS_FILE"
echo "Test complete. See individual test results above." >> "$RESULTS_FILE"

# Cleanup test repos
cleanup

echo "Results written to $RESULTS_FILE"
