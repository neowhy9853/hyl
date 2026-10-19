# Test Entry Verification Report

## Summary

| Status | Count |
|--------|-------|
| Total entries | 2 |
| runnable_verified | 1 |
| needs_env | 1 |

## PCA-TE-0001 (PCA-0001: ERROR_EXCEPTION_CHANGE) — ✅ runnable_verified

**Command**: Standalone Python exception class hierarchy test

**Result**: All 5 tests passed:
1. InvalidInstalledGPGKeyError is subclass of Error
2. except Error catches InvalidInstalledGPGKeyError
3. Exception message is preserved through constructor
4. type(e).__name__ returns 'InvalidInstalledGPGKeyError'
5. isinstance checks work for both specific and parent types

**Evidence**: The new exception class is properly defined in `dnf/exceptions.py` (line 88-89) and raised in `dnf/base.py` (line 2671). Before version (d1b50259) does NOT have this class.

## PCA-TE-0002 (PCA-0002: OUTPUT_FORMAT_CHANGE) — ❌ needs_env

**Command**: Would need `/usr/bin/dnf install` with expired GPG key fixture

**Result**: Cannot run — missing native bindings:
- libdnf (transaction, etc.)
- hawkey
- librepo
- rpm

**Host check per AGENTS.md**: All 91 CTest modules fail before execution due to missing bindings.
