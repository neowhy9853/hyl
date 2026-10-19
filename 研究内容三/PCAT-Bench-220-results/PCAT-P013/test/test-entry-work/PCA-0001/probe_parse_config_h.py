#!/usr/bin/env python3
"""Probe for parse_config_h() RETURN_CONTRACT_CHANGE.

Tests whether sysconfig.parse_config_h() strips double quotes from string
values found in pyconfig.h-style #define lines.

BEFORE (unpatched): values like '"md5,sha1,sha256"' keep their quotes
AFTER (patched):    values like 'md5,sha1,sha256' have quotes stripped
"""
import io
import sys
import sysconfig

QUOTED_VALUE = '"md5,sha1,sha256"'
UNQUOTED_VALUE = 'md5,sha1,sha256'
NUMERIC_VALUE = '42'
QUOTED_NUMERIC = '"42"'

# Test 1: Mock config.h to test parse_config_h directly
config_h_content = (
    '#define PY_BUILTIN_HASHLIB_HASHES "md5,sha1,sha256"\n'
    '#define SOME_NUMBER 42\n'
    '#define QUOTED_NUMBER "42"\n'
    '#define PLAIN_STRING some_value\n'
)

def test_parse_config_h_direct():
    """Test parse_config_h directly with mock pyconfig.h content."""
    fp = io.StringIO(config_h_content)
    vars_dict = {}
    result = sysconfig.parse_config_h(fp, vars_dict)
    
    failures = []
    
    # Check if PY_BUILTIN_HASHLIB_HASHES has quotes stripped
    val = result.get('PY_BUILTIN_HASHLIB_HASHES', '')
    if val == QUOTED_VALUE:
        failures.append(f"BEFORE behavior: PY_BUILTIN_HASHLIB_HASHES still has quotes: {val!r}")
    elif val == UNQUOTED_VALUE:
        print(f"PASS: PY_BUILTIN_HASHLIB_HASHES quotes stripped: {val!r}")
    else:
        failures.append(f"UNEXPECTED: PY_BUILTIN_HASHLIB_HASHES = {val!r}")
    
    # Check numeric value unchanged
    val = result.get('SOME_NUMBER', '')
    if val == 42:
        print(f"PASS: SOME_NUMBER (numeric) = {val!r}")
    else:
        failures.append(f"UNEXPECTED: SOME_NUMBER = {val!r} (type={type(val).__name__})")
    
    # Check QUOTED_NUMBER: after patch, quotes stripped then int conversion happens
    val = result.get('QUOTED_NUMBER', '')
    if val == 42:
        print(f"PASS: QUOTED_NUMBER (quoted numeric) = {val!r} (quotes stripped AND int-converted)")
    elif val == QUOTED_NUMERIC:
        failures.append(f"BEFORE behavior: QUOTED_NUMBER retains quotes: {val!r}")
    else:
        print(f"INFO: QUOTED_NUMBER = {val!r} (type={type(val).__name__})")
    
    # Check plain string unchanged
    val = result.get('PLAIN_STRING', '')
    if val == 'some_value':
        print(f"PASS: PLAIN_STRING = {val!r}")
    else:
        failures.append(f"UNEXPECTED: PLAIN_STRING = {val!r}")
    
    return failures


def test_get_config_vars_quotes():
    """Check if get_config_vars() returns values with no leading quote."""
    # This test verifies the build-time effect - only meaningful when Python
    # was BUILT with the patch. For a baseline build, PY_BUILTIN_HASHLIB_HASHES
    # may still have quotes.
    try:
        vars_val = sysconfig.get_config_var('PY_BUILTIN_HASHLIB_HASHES')
    except (KeyError, AttributeError):
        vars_val = None
    
    if vars_val is None:
        print("SKIP: PY_BUILTIN_HASHLIB_HASHES not defined in this build")
        return []
    
    if isinstance(vars_val, str) and vars_val.startswith('"'):
        return [f"BEFORE behavior: PY_BUILTIN_HASHLIB_HASHES starts with quote: {vars_val!r}"]
    elif isinstance(vars_val, str):
        print(f"PASS: PY_BUILTIN_HASHLIB_HASHES (no leading quote): {vars_val!r}")
    else:
        print(f"INFO: PY_BUILTIN_HASHLIB_HASHES = {vars_val!r} (type={type(vars_val).__name__})")
    
    return []


def main():
    all_failures = []
    
    print("=" * 60)
    print("Test 1: Direct parse_config_h() API behavior")
    print("=" * 60)
    all_failures.extend(test_parse_config_h_direct())
    
    print()
    print("=" * 60)
    print("Test 2: get_config_vars() PY_BUILTIN_HASHLIB_HASHES")
    print("=" * 60)
    all_failures.extend(test_get_config_vars_quotes())
    
    print()
    if all_failures:
        print(f"FAILURES ({len(all_failures)}):")
        for f in all_failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
