#!/usr/bin/env python3
"""AFTER test: monkey-patch BaseSubprocessTransport with the patched behavior.

This replaces _process_exited, _try_finish, and _call_connection_lost
on the running BaseSubprocessTransport class with the patched versions.
"""
import asyncio
import asyncio.base_subprocess as bsp
import asyncio.subprocess
import functools
import os
import signal
import subprocess
import sys
import textwrap
import time


def patched__init__(self, loop, protocol, args, shell,
                    stdin, stdout, stderr, bufsize,
                    waiter=None, extra=None, **kwargs):
    from asyncio import transports
    transports.SubprocessTransport.__init__(self, extra)
    self._closed = False
    self._protocol = protocol
    self._loop = loop
    self._proc = None
    self._pid = None
    self._returncode = None
    self._exit_waiters = []
    self._pending_calls = __import__('collections').deque()
    self._pipes = {}
    self._finished = False
    # NOTE: _pipes_connected removed

    if stdin == subprocess.PIPE:
        self._pipes[0] = None
    if stdout == subprocess.PIPE:
        self._pipes[1] = None
    if stderr == subprocess.PIPE:
        self._pipes[2] = None

    try:
        self._start(args=args, shell=shell, stdin=stdin, stdout=stdout,
                    stderr=stderr, bufsize=bufsize, **kwargs)
    except:
        self.close()
        raise

    self._pid = self._proc.pid
    self._extra['subprocess'] = self._proc

    if self._loop.get_debug():
        if isinstance(args, (bytes, str)):
            program = args
        else:
            program = args[0]
        from asyncio.log import logger
        logger.debug('process %r created: pid %s',
                     program, self._pid)

    self._loop.create_task(self._connect_pipes(waiter))


async def patched__connect_pipes(self, waiter):
    from asyncio.log import logger
    try:
        proc = self._proc
        loop = self._loop
        if proc.stdin is not None:
            from asyncio.base_subprocess import WriteSubprocessPipeProto
            _, pipe = await loop.connect_write_pipe(
                lambda: WriteSubprocessPipeProto(self, 0),
                proc.stdin)
            self._pipes[0] = pipe

        if proc.stdout is not None:
            from asyncio.base_subprocess import ReadSubprocessPipeProto
            _, pipe = await loop.connect_read_pipe(
                lambda: ReadSubprocessPipeProto(self, 1),
                proc.stdout)
            self._pipes[1] = pipe

        if proc.stderr is not None:
            from asyncio.base_subprocess import ReadSubprocessPipeProto
            _, pipe = await loop.connect_read_pipe(
                lambda: ReadSubprocessPipeProto(self, 2),
                proc.stderr)
            self._pipes[2] = pipe

        assert self._pending_calls is not None

        loop.call_soon(self._protocol.connection_made, self)
        for callback, data in self._pending_calls:
            loop.call_soon(callback, *data)
        self._pending_calls = None
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        if waiter is not None and not waiter.cancelled():
            waiter.set_exception(exc)
    else:
        if waiter is not None and not waiter.cancelled():
            waiter.set_result(None)
        # NOTE: _pipes_connected = True removed


def patched__process_exited(self, returncode):
    from asyncio.log import logger
    assert returncode is not None, returncode
    assert self._returncode is None, self._returncode
    if self._loop.get_debug():
        logger.info('%r exited with return code %r', self, returncode)
    self._returncode = returncode

    if self._proc.returncode is None:
        self._proc.returncode = returncode
    self._call(self._protocol.process_exited)

    self._try_finish()

    # gh-119710: Wake up futures waiting for wait() as soon as the process exits.
    for waiter in self._exit_waiters:
        if not waiter.done():
            waiter.set_result(returncode)
    self._exit_waiters = None


def patched__try_finish(self):
    assert not self._finished
    if self._returncode is None:
        return
    # NOTE: _pipes_connected guard removed
    if all(p is not None and p.disconnected
           for p in self._pipes.values()):
        self._finished = True
        self._call(self._call_connection_lost, None)


def patched__call_connection_lost(self, exc):
    try:
        self._protocol.connection_lost(exc)
    finally:
        # NOTE: waiter wakeup removed from here
        self._loop = None
        self._proc = None
        self._protocol = None


print("Applying patched methods to BaseSubprocessTransport...")
bsp.BaseSubprocessTransport.__init__ = patched__init__
bsp.BaseSubprocessTransport._connect_pipes = patched__connect_pipes
bsp.BaseSubprocessTransport._process_exited = patched__process_exited
bsp.BaseSubprocessTransport._try_finish = patched__try_finish
bsp.BaseSubprocessTransport._call_connection_lost = patched__call_connection_lost

# Verify the patch
import inspect
src = inspect.getsource(bsp.BaseSubprocessTransport._process_exited)
assert "Wake up futures" in src, "Patch not applied correctly"
print("Patch verified: _process_exited has wake-up code")


# Now run the actual test
async def test_wait_returns_on_process_exit():
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
        ready = await proc.stdout.readexactly(5)
        assert ready == b'ready', f"Expected b'ready', got {ready!r}"

        proc.kill()

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


def _can_use_fork():
    try:
        pid = os.fork()
        if pid == 0:
            os._exit(0)
        os.waitpid(pid, 0)
        return True
    except (OSError, AttributeError):
        return False


if not _can_use_fork():
    print("SKIP: fork not available")
    sys.exit(2)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    success, elapsed = loop.run_until_complete(test_wait_returns_on_process_exit())
    if success:
        print(f"RESULT: PASS - wait() returned in {elapsed:.1f}s")
        sys.exit(0)
    else:
        print(f"RESULT: FAIL - wait() timed out ({elapsed:.1f}s)")
        sys.exit(1)
except Exception as e:
    print(f"RESULT: ERROR - {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    loop.close()
