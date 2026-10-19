#!/usr/bin/env python3
"""
PCA-0001: ERROR_EXCEPTION_CHANGE - Verify InvalidInstalledGPGKeyError
exception type compatibility.

Tests:
1. The new exception class is importable from dnf.exceptions
2. InvalidInstalledGPGKeyError is a subclass of Error
3. except Error still catches InvalidInstalledGPGKeyError
4. The exception message is preserved through the constructor
5. type(e).__name__ returns 'InvalidInstalledGPGKeyError' (behavior change)
"""

import sys

def test_import_and_hierarchy():
    """Test that InvalidInstalledGPGKeyError exists and inherits from Error."""
    from dnf.exceptions import InvalidInstalledGPGKeyError, Error
    assert issubclass(InvalidInstalledGPGKeyError, Error), \
        "InvalidInstalledGPGKeyError must be a subclass of Error"
    print("PASS: InvalidInstalledGPGKeyError is a subclass of Error")
    return True

def test_except_error_still_catches():
    """Test that 'except Error' still catches InvalidInstalledGPGKeyError."""
    from dnf.exceptions import InvalidInstalledGPGKeyError, Error
    try:
        raise InvalidInstalledGPGKeyError("test message")
    except Error:
        print("PASS: except Error catches InvalidInstalledGPGKeyError")
        return True
    except Exception:
        print("FAIL: except Error did NOT catch InvalidInstalledGPGKeyError")
        return False

def test_message_preserved():
    """Test that the exception message is preserved."""
    from dnf.exceptions import InvalidInstalledGPGKeyError
    try:
        raise InvalidInstalledGPGKeyError("key fingerprint mismatch")
    except InvalidInstalledGPGKeyError as e:
        msg = str(e)
        assert "key fingerprint mismatch" in msg, \
            f"Expected message to contain 'key fingerprint mismatch', got: {msg}"
        print(f"PASS: Exception message preserved: '{msg}'")
        return True
    return False

def test_type_name_change():
    """
    Test that type(e).__name__ returns 'InvalidInstalledGPGKeyError'.
    This confirms the exception type change from generic Error.
    """
    from dnf.exceptions import InvalidInstalledGPGKeyError
    try:
        raise InvalidInstalledGPGKeyError("test")
    except InvalidInstalledGPGKeyError as e:
        type_name = type(e).__name__
        assert type_name == "InvalidInstalledGPGKeyError", \
            f"Expected 'InvalidInstalledGPGKeyError', got '{type_name}'"
        print(f"PASS: type(e).__name__ = '{type_name}' (specifically catchable)")
        return True
    return False

def test_isinstance_check():
    """Test isinstance checks work correctly with the new exception type."""
    from dnf.exceptions import InvalidInstalledGPGKeyError, Error
    exc = InvalidInstalledGPGKeyError("test")
    assert isinstance(exc, InvalidInstalledGPGKeyError), "isinstance with specific type"
    assert isinstance(exc, Error), "isinstance with parent type"
    print("PASS: isinstance checks work for both specific and parent types")
    return True

if __name__ == "__main__":
    # Add the dnf module path to sys.path
    # The DNF source tree needs to be in the Python path
    import os
    dnf_dir = os.environ.get("DNF_SRC_DIR")
    if dnf_dir:
        sys.path.insert(0, os.path.dirname(dnf_dir))
    
    tests = [
        test_import_and_hierarchy,
        test_except_error_still_catches,
        test_message_preserved,
        test_type_name_change,
        test_isinstance_check,
    ]
    
    failures = 0
    for t in tests:
        try:
            if not t():
                failures += 1
        except Exception as e:
            print(f"FAIL: {t.__name__} raised: {e}")
            failures += 1
    
    if failures:
        print(f"\nRESULT: {len(tests) - failures}/{len(tests)} passed, {failures} failed")
        sys.exit(1)
    else:
        print(f"\nRESULT: All {len(tests)} tests PASSED")
        sys.exit(0)
