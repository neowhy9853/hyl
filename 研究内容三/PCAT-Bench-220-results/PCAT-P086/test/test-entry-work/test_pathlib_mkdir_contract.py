"""Contract verification for pathlib.Path.mkdir parent_mode parameter (PCA-0003, PCA-0004)."""
import sys
import os
import tempfile
import json

PATCHED_LIB = "/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/_worktrees/patched/Lib"
sys.path.insert(0, PATCHED_LIB)

import pathlib

results = {"finding_ids": ["PCA-0003", "PCA-0004"], "tests": [], "summary": {"passed": 0, "failed": 0, "skipped": 0}}

def record(test_id, status, detail=""):
    entry = {"test_id": test_id, "status": status, "detail": detail}
    results["tests"].append(entry)
    if status == "PASS":
        results["summary"]["passed"] += 1
    elif status == "FAIL":
        results["summary"]["failed"] += 1
    else:
        results["summary"]["skipped"] += 1

# PCA-0003: INPUT_CONTRACT_CHANGE - signature backward compatibility
# Test 1: Old call styles still work
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        p1 = pathlib.Path(testdir) / "a"
        p1.mkdir()
        assert p1.is_dir()
        record("PCA-0003-backward-basic", "PASS", "Path.mkdir() still works")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0003-backward-basic", "FAIL", str(e))

# Test 2: Old parents=True still works
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        p2 = pathlib.Path(testdir) / "b" / "c"
        p2.mkdir(parents=True)
        assert p2.is_dir()
        record("PCA-0003-backward-parents", "PASS", "Path.mkdir(parents=True) still works")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0003-backward-parents", "FAIL", str(e))

# Test 3: Old exist_ok=True still works
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        p3 = pathlib.Path(testdir) / "d" / "e"
        p3.mkdir(parents=True, exist_ok=True)
        p3.mkdir(parents=True, exist_ok=True)
        assert p3.is_dir()
        record("PCA-0003-backward-existok", "PASS", "Path.mkdir(exist_ok=True) still works")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0003-backward-existok", "FAIL", str(e))

# Test 4: New parent_mode parameter works
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            p4 = pathlib.Path(testdir) / "dir1" / "dir2"
            old_umask = os.umask(0o022)
            try:
                p4.mkdir(parents=True, mode=0o755, parent_mode=0o700)
                parent = pathlib.Path(testdir) / "dir1"
                parent_st = parent.stat().st_mode & 0o777
                leaf_st = p4.stat().st_mode & 0o777
                expected_parent = 0o700 & ~0o022
                expected_leaf = 0o755 & ~0o022
                if parent_st == expected_parent and leaf_st == expected_leaf:
                    record("PCA-0003-parent-mode", "PASS",
                           f"parent_mode works: parent={oct(parent_st)} leaf={oct(leaf_st)}")
                else:
                    record("PCA-0003-parent-mode", "FAIL",
                           f"mode mismatch: parent={oct(parent_st)} leaf={oct(leaf_st)}")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0003-parent-mode", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0003-parent-mode", "FAIL", str(e))

# PCA-0004: SIDE_EFFECT_CHANGE - recursive mode propagation
# Test 5: Without parent_mode, behavior unchanged
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            p5 = pathlib.Path(testdir) / "parent" / "child"
            old_umask = os.umask(0o002)
            try:
                p5.mkdir(parents=True, mode=0o555)
                leaf_st = p5.stat().st_mode & 0o777
                parent_st = p5.parent.stat().st_mode & 0o777
                if leaf_st == 0o555:
                    record("PCA-0004-no-parent-leaf", "PASS", f"leaf mode: {oct(leaf_st)}")
                else:
                    record("PCA-0004-no-parent-leaf", "FAIL", f"leaf mode {oct(leaf_st)}")
                if parent_st == 0o775:
                    record("PCA-0004-no-parent-parent", "PASS", f"parent default: {oct(parent_st)}")
                else:
                    record("PCA-0004-no-parent-parent", "FAIL", f"parent mode {oct(parent_st)}")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0004-no-parent", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0004-no-parent", "FAIL", str(e))

# Test 6: Deep hierarchy with parent_mode
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            p6 = pathlib.Path(testdir) / "l1" / "l2" / "l3"
            old_umask = os.umask(0o002)
            try:
                p6.mkdir(parents=True, mode=0o755, parent_mode=0o700)
                for i, p in enumerate([pathlib.Path(testdir) / "l1", pathlib.Path(testdir) / "l1" / "l2"], 1):
                    mode = p.stat().st_mode & 0o777
                    if mode == 0o700:
                        record(f"PCA-0004-deep-level{i}", "PASS", f"level {i}: {oct(mode)}")
                    else:
                        record(f"PCA-0004-deep-level{i}", "FAIL", f"level {i}: {oct(mode)}")
                leaf_mode = p6.stat().st_mode & 0o777
                if leaf_mode == 0o755:
                    record("PCA-0004-deep-leaf", "PASS", f"leaf: {oct(leaf_mode)}")
                else:
                    record("PCA-0004-deep-leaf", "FAIL", f"leaf: {oct(leaf_mode)}")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0004-deep", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0004-deep", "FAIL", str(e))

# Test 7: parent_mode same as mode
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            p7 = pathlib.Path(testdir) / "dir1" / "dir2"
            old_umask = os.umask(0o002)
            try:
                p7.mkdir(parents=True, mode=0o705, parent_mode=0o705)
                parent_st = p7.parent.stat().st_mode & 0o777
                leaf_st = p7.stat().st_mode & 0o777
                if parent_st == 0o705 and leaf_st == 0o705:
                    record("PCA-0004-same-mode", "PASS", f"both {oct(parent_st)}")
                else:
                    record("PCA-0004-same-mode", "FAIL", f"parent={oct(parent_st)} leaf={oct(leaf_st)}")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0004-same-mode", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0004-same-mode", "FAIL", str(e))

print(json.dumps(results, indent=2, default=str))
