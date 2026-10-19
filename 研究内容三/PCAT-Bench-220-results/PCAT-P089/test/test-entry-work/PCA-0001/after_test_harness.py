#!/usr/bin/env python3
"""AFTER test: uses patched asyncio.base_subprocess.

This script copies the patched base_subprocess.py and hot-replaces
the BaseSubprocessTransport class in the running asyncio module.
"""
import importlib
import inspect
import os
import shutil
import sys
import tempfile
import types

PATCHED_MODULE = "/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P029/_worktrees/patched/Lib/asyncio/base_subprocess.py"
TEST_SCRIPT = "/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P029/compatibility-testing/test-entry-work/PCA-0001/standalone_test.py"

# Read patched module source
with open(PATCHED_MODULE) as f:
    patched_src = f.read()

# Load patched module and replace in asyncio namespace
# The base_subprocess module imports from asyncio.protocols, transports, log
# We need to handle the relative imports
tmpdir = tempfile.mkdtemp()
patched_path = os.path.join(tmpdir, "base_subprocess_patched.py")
with open(patched_path, "w") as f:
    f.write(patched_src)

# Add tmpdir to sys.path
sys.path.insert(0, tmpdir)

# Import the patched module
import importlib.util
spec = importlib.util.spec_from_file_location("base_subprocess_patched", patched_path)
patched_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patched_mod)

# Replace the class in the running asyncio module
import asyncio.base_subprocess
import asyncio.subprocess
# Also update the asyncio.subprocess module's references
asyncio.base_subprocess.BaseSubprocessTransport = patched_mod.BaseSubprocessTransport

print("Patched BaseSubprocessTransport applied")
print("Verifying _process_exited has wake-up code:")
src = inspect.getsource(asyncio.base_subprocess.BaseSubprocessTransport._process_exited)
has_wakeup = "Wake up futures" in src or "_exit_waiters" in src
print(f"  Has _exit_waiters wakeup in _process_exited: {has_wakeup}")

# Now run the actual test
print("\n=== Running AFTER test ===")
old_cwd = os.getcwd()
try:
    exec(open(TEST_SCRIPT).read())
finally:
    import shutil
    shutil.rmtree(tmpdir)
