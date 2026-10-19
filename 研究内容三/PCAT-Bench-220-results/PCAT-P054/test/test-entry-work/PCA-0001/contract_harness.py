#!/usr/bin/env python3
"""
Contract verification harness for PCA-0001.

Demonstrates the behavioral difference between the OLD (startswith/==) and
NEW (fnmatch) matching logic for usr_drift_protected_paths configuration values.

This harness tests the fnmatch vs startswith behavioral contract change directly
and standalone, without requiring the DNF system libraries (hawkey, libdnf, etc.).
"""

import os
import sys
import csv
from fnmatch import fnmatch

# --- REPLICATED OLD BEHAVIOR (startswith / ==) ---

def old_match(pkg_file_path, protected_path):
    """Old behavior: path prefix matching."""
    return pkg_file_path.startswith("%s/" % protected_path) or pkg_file_path == protected_path

def old_check(protected_paths, pkg_file_paths):
    """Old behavior: check all package file paths against protected paths."""
    matched = {}
    for pkg_file_path in sorted(pkg_file_paths):
        for protected_path in protected_paths:
            if old_match(pkg_file_path, protected_path):
                matched.setdefault("default", []).append(pkg_file_path)
                break
    return matched

# --- REPLICATED NEW BEHAVIOR (fnmatch) ---

def new_match(pkg_file_path, protected_pattern):
    """New behavior: glob pattern matching via fnmatch."""
    return fnmatch(pkg_file_path, protected_pattern)

def new_check(protected_patterns, pkg_file_paths):
    """New behavior: check all package file paths against protected patterns."""
    matched = {}
    for pkg_file_path in sorted(pkg_file_paths):
        for protected_pattern in protected_patterns:
            if new_match(pkg_file_path, protected_pattern):
                matched.setdefault("default", []).append(pkg_file_path)
                break
    return matched

# --- TEST INPUTS ---

TEST_PROTECTED_PATHS = [
    "/usr/lib",           # bare directory (NO wildcard) - OLD: prefix match, NEW: exact match only
    "/usr/local",         # bare directory - same issue
    "/etc",               # bare directory - same issue
    "/usr/lib/*",         # with wildcard - OLD: literal '*', NEW: glob match
    "/usr/local/*/bin",   # glob pattern
    "/etc/os-release",    # exact file path - should work with both
    "/opt/*/lib",         # glob pattern
    "/data/[a-z]*",       # glob with character class
]

TEST_FILE_PATHS = [
    "/usr/lib/python3.11/site-packages/foo",  # OLD: matched by /usr/lib, NEW: NOT matched (needs /usr/lib/*)
    "/usr/lib",                                # OLD: matched, NEW: matched (exact match)
    "/usr/local/bin/tool",                     # OLD: matched by /usr/local, NEW: NOT matched
    "/usr/local",                              # OLD: matched, NEW: matched (exact match)
    "/usr/local/foo/bin/tool",                 # matched by /usr/local/*/bin (NEW only)
    "/etc/os-release",                         # exact file - matched by both
    "/etc/issue",                              # OLD: matched by /etc, NEW: NOT matched (needs /etc/*)
    "/opt/python/lib/file.so",                # matched by /opt/*/lib (NEW only)
    "/data/abc123/file",                       # matched by /data/[a-z]*
    "/data/123456/file",                       # NOT matched by /data/[a-z]* (starts with digit)
    "/usr/share/doc/readme",                   # not matched by any
    "/var/log/syslog",                         # not matched by any
]

# --- RESULTS ---

def run_tests():
    results = []

    for pfile in TEST_FILE_PATHS:
        for ppath in TEST_PROTECTED_PATHS:
            old_result = old_match(pfile, ppath)
            new_result = new_match(pfile, ppath)

            agreement = "SAME" if old_result == new_result else "DIFFERENT"

            if agreement == "DIFFERENT":
                if old_result and not new_result:
                    change_type = "REGRESSION: old protected, new does NOT protect"
                else:
                    change_type = "EXPANSION: new protects, old did NOT"
            else:
                change_type = ""

            results.append({
                "protected_path": ppath,
                "file_path": pfile,
                "old_matches": old_result,
                "new_matches": new_result,
                "agreement": agreement,
                "change_type": change_type,
            })

    return results


def print_results(results):
    """Print results in a readable table format."""
    print("=" * 120)
    print(f"{'Protected Path':<30} {'File Path':<40} {'Old':<6} {'New':<6} {'Change Type'}")
    print("=" * 120)

    diffs = [r for r in results if r["agreement"] == "DIFFERENT"]
    for r in results:
        marker = " *** " if r["agreement"] == "DIFFERENT" else "     "
        print(f"{marker} {r['protected_path']:<28} {r['file_path']:<38} {str(r['old_matches']):<6} {str(r['new_matches']):<6} {r['change_type']}")

    print()
    print("=" * 120)
    print(f"SUMMARY: {len(diffs)} behavioral differences out of {len(results)} test cases")

    if diffs:
        print()
        print("DIFFERENCES DETECTED:")
        print("-" * 120)
        old_protected_not_new = [d for d in diffs if d["old_matches"] and not d["new_matches"]]
        new_protected_not_old = [d for d in diffs if not d["old_matches"] and d["new_matches"]]

        if old_protected_not_new:
            print(f"\n  REGRESSIONS ({len(old_protected_not_new)} cases) — old protected, new does NOT protect:")
            for d in old_protected_not_new:
                print(f"    - {d['file_path']} against '{d['protected_path']}'")

        if new_protected_not_old:
            print(f"\n  EXPANSIONS ({len(new_protected_not_old)} cases) — new protects, old did NOT:")
            for d in new_protected_not_old:
                print(f"    - {d['file_path']} against '{d['protected_path']}'")


if __name__ == "__main__":
    results = run_tests()

    print_results(results)

    # Check if there are regressions (old protected, new does not)
    diffs = [r for r in results if r["old_matches"] and not r["new_matches"]]
    if diffs:
        print(f"\nCONTRACT BREACH DETECTED: {len(diffs)} cases where previously protected paths are no longer matched.")
        print("This confirms an INPUT_CONTRACT_CHANGE: existing usr_drift_protected_paths configurations")
        print("using bare directory paths will lose protection coverage after this patch.")
        sys.exit(1)
    else:
        print("\nNo contract breaches detected (all previously protected paths remain protected).")
        sys.exit(0)
