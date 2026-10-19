"""Contract verification for os.makedirs parent_mode parameter (PCA-0001, PCA-0002)."""
import sys
import os
import tempfile
import json
import stat

PATCHED_LIB = "/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/_worktrees/patched/Lib"
sys.path.insert(0, PATCHED_LIB)

import importlib
import os as os_mod
importlib.reload(os_mod)

results = {"finding_ids": ["PCA-0001", "PCA-0002"], "tests": [], "summary": {"passed": 0, "failed": 0, "skipped": 0}}

def record(test_id, status, detail=""):
    entry = {"test_id": test_id, "status": status, "detail": detail}
    results["tests"].append(entry)
    if status == "PASS":
        results["summary"]["passed"] += 1
    elif status == "FAIL":
        results["summary"]["failed"] += 1
    else:
        results["summary"]["skipped"] += 1

# PCA-0001: INPUT_CONTRACT_CHANGE - signature backward compatibility
# Test 1: Old call styles still work
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        # Test old positional args
        path1 = os.path.join(testdir, "a", "b")
        os_mod.makedirs(path1)
        assert os.path.isdir(path1), "path1 should exist"
        record("PCA-0001-backward-pos", "PASS", "makedirs(name) still works")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0001-backward-pos", "FAIL", str(e))

# Test 2: Old keyword args still work
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        path2 = os.path.join(testdir, "c", "d")
        os_mod.makedirs(path2, exist_ok=True)
        assert os.path.isdir(path2)
        record("PCA-0001-backward-kw", "PASS", "makedirs(name, exist_ok=True) still works")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0001-backward-kw", "FAIL", str(e))

# Test 3: Old mode+exist_ok still work
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        path3 = os.path.join(testdir, "e", "f")
        os_mod.makedirs(path3, 0o755, True)
        assert os.path.isdir(path3)
        record("PCA-0001-backward-mode", "PASS", "makedirs(name, mode, exist_ok) still works")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0001-backward-mode", "FAIL", str(e))

# Test 4: New parent_mode parameter works
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            parent = os.path.join(testdir, "dir1")
            path4 = os.path.join(parent, "dir2")
            old_umask = os.umask(0o022)
            try:
                os_mod.makedirs(path4, 0o777, parent_mode=0o700)
                assert os.path.isdir(path4)
                parent_st = os.stat(parent).st_mode & 0o777
                leaf_st = os.stat(path4).st_mode & 0o777
                expected_parent = 0o700 & ~0o022
                expected_leaf = 0o777 & ~0o022
                if parent_st == expected_parent and leaf_st == expected_leaf:
                    record("PCA-0001-parent-mode", "PASS",
                           f"parent_mode works: parent={oct(parent_st)} leaf={oct(leaf_st)}")
                else:
                    record("PCA-0001-parent-mode", "FAIL",
                           f"mode mismatch: parent={oct(parent_st)} expected={oct(expected_parent)} leaf={oct(leaf_st)} expected={oct(expected_leaf)}")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0001-parent-mode", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0001-parent-mode", "FAIL", str(e))

# Test 5: Keyword-only enforcement (positional parent_mode should fail)
try:
    try:
        path5 = os.path.join(tempfile.mkdtemp(prefix="pca_test_"), "g", "h")
        os_mod.makedirs(path5, 0o755, False, 0o700)
        record("PCA-0001-kw-only", "FAIL", "Should have raised TypeError for positional parent_mode")
    except TypeError as e:
        record("PCA-0001-kw-only", "PASS", f"Correctly raised TypeError: {e}")
    except FileNotFoundError:
        record("PCA-0001-kw-only", "FAIL", "Raised FileNotFoundError instead of TypeError")
except Exception as e:
    record("PCA-0001-kw-only", "FAIL", str(e))

# PCA-0002: SIDE_EFFECT_CHANGE - recursive mode propagation
# Test 6: Without parent_mode, behavior unchanged
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            path6 = os.path.join(testdir, "parent", "child")
            old_umask = os.umask(0o002)
            try:
                os_mod.makedirs(path6, 0o555)
                leaf_st = os.stat(path6).st_mode & 0o777
                parent_st = os.stat(os.path.dirname(path6)).st_mode & 0o777
                if leaf_st == 0o555:
                    record("PCA-0002-no-parent-mode-leaf", "PASS", f"leaf mode correct: {oct(leaf_st)}")
                else:
                    record("PCA-0002-no-parent-mode-leaf", "FAIL", f"leaf mode {oct(leaf_st)} != 0o555")
                if parent_st == 0o775:
                    record("PCA-0002-no-parent-mode-parent", "PASS", f"parent default mode: {oct(parent_st)}")
                else:
                    record("PCA-0002-no-parent-mode-parent", "FAIL", f"parent mode {oct(parent_st)} != 0o775")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0002-no-parent-mode", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0002-no-parent-mode", "FAIL", str(e))

# Test 7: Deep hierarchy with parent_mode
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            base = os.path.join(testdir, "l1", "l2", "l3")
            old_umask = os.umask(0o002)
            try:
                os_mod.makedirs(base, 0o755, parent_mode=0o700)
                p1 = os.path.join(testdir, "l1")
                p2 = os.path.join(testdir, "l1", "l2")
                for level, p in enumerate([p1, p2], 1):
                    mode = os.stat(p).st_mode & 0o777
                    if mode == 0o700:
                        record(f"PCA-0002-deep-level{level}", "PASS", f"level {level} parent mode: {oct(mode)}")
                    else:
                        record(f"PCA-0002-deep-level{level}", "FAIL", f"level {level} mode {oct(mode)} != 0o700")
                leaf_mode = os.stat(base).st_mode & 0o777
                if leaf_mode == 0o755:
                    record("PCA-0002-deep-leaf", "PASS", f"leaf mode: {oct(leaf_mode)}")
                else:
                    record("PCA-0002-deep-leaf", "FAIL", f"leaf mode {oct(leaf_mode)} != 0o755")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0002-deep", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0002-deep", "FAIL", str(e))

# Test 8: parent_mode same as mode (emulate Python 3.6 behavior)
try:
    testdir = tempfile.mkdtemp(prefix="pca_test_")
    try:
        if os.name != 'nt':
            parent = os.path.join(testdir, "dir1")
            path8 = os.path.join(parent, "dir2")
            old_umask = os.umask(0o002)
            try:
                os_mod.makedirs(path8, 0o705, parent_mode=0o705)
                p_mode = os.stat(parent).st_mode & 0o777
                l_mode = os.stat(path8).st_mode & 0o777
                if p_mode == 0o705 and l_mode == 0o705:
                    record("PCA-0002-same-mode", "PASS", f"both dirs: {oct(p_mode)}")
                else:
                    record("PCA-0002-same-mode", "FAIL", f"parent={oct(p_mode)} leaf={oct(l_mode)}")
            finally:
                os.umask(old_umask)
        else:
            record("PCA-0002-same-mode", "SKIP", "Windows mode test skipped")
    finally:
        import shutil
        shutil.rmtree(testdir, ignore_errors=True)
except Exception as e:
    record("PCA-0002-same-mode", "FAIL", str(e))

print(json.dumps(results, indent=2, default=str))
