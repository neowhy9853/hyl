#!/usr/bin/env python3
"""Standalone test for PCA-0001: asyncio Process.wait() timing change.

Tests that Process.wait() returns on process exit rather than waiting
for all pipes to close. This test exercises the SIDE_EFFECT_CHANGE
introduced by commit f2521324e6bd.
"""
import asyncio
import os
import signal
import subprocess
import sys
import textwrap
import time


def _can_use_fork():
    try:
        pid = os.fork()
        if pid == 0:
            os._exit(0)
        os.waitpid(pid, 0)
        return True
    except (OSError, AttributeError):
        return False


async def test_wait_returns_on_process_exit():
    """Test that wait() returns as soon as process exits, even if
    a grandchild holds the stdout pipe open forever."""
    code = textwrap.dedent("""\
import subprocess, sys
subprocess.run([sys.executable, "-c",
    "import sys; sys.stdout.write('ready');"
    " sys.stdout.flush(); sys.stdin.read()"])
""")

    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-c", code,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        wait_task = asyncio.create_task(proc.wait())
        # Wait until grandchild writes 'ready' to stdout
        ready = await proc.stdout.readexactly(5)
        assert ready == b'ready', f"Expected b'ready', got {ready!r}"

        proc.kill()

        # wait() must return within 5 seconds (SHORT_TIMEOUT)
        start = time.monotonic()
        try:
            returncode = await asyncio.wait_for(wait_task, timeout=5.0)
            elapsed = time.monotonic() - start
            print(f"PASS: wait() returned {returncode} in {elapsed:.1f}s")
            assert returncode == -signal.SIGKILL, \
                f"Expected -{signal.SIGKILL}, got {returncode}"
            return True, elapsed
        except asyncio.TimeoutError:
            elapsed = time.monotonic() - start
            print(f"FAIL: wait() timed out after {elapsed:.1f}s")
            return False, elapsed
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            await asyncio.wait_for(proc.stdout.read(), timeout=2.0)
        except asyncio.TimeoutError:
            pass
        try:
            if proc.returncode is None:
                proc.kill()
        except Exception:
            pass


def main():
    if not _can_use_fork():
        print("SKIP: fork not available on this platform")
        print("RESULT: SKIPPED")
        return 2

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        success, elapsed = loop.run_until_complete(test_wait_returns_on_process_exit())
        if success:
            print(f"RESULT: PASS - wait() returned in {elapsed:.1f}s")
            return 0
        else:
            print(f"RESULT: FAIL - wait() timed out ({elapsed:.1f}s)")
            return 1
    except Exception as e:
        print(f"RESULT: ERROR - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        loop.close()


if __name__ == "__main__":
    sys.exit(main())
