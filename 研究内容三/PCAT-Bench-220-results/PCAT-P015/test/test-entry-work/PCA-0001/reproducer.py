#!/usr/bin/env python3
"""
PCA-0001 Reproducer: Test _encodeFilenameFlags OUTPUT_FORMAT_CHANGE

Tests the encoding behavior change in ZipInfo._encodeFilenameFlags:
- Old: always tries 'ascii', falls back to 'utf-8' on failure
- New: uses 'cp437' when flag_bits has no UTF-8 flag, 'ascii' when set
"""

import os
import sys
import tempfile
import struct
import io

# Constants from Lib/zipfile/__init__.py
_MASK_UTF_FILENAME = 1 << 11
_MASK_USE_DATA_DESCRIPTOR = 1 << 3
_MASK_COMPRESS_OPTION_1 = 1 << 11

# Test filenames (as ZipInfo would store them after reading a ZIP)
# All are cp437-encodable but NOT ascii-encodable
CP437_ENCODABLE_NAMES = [
    'fünf',         # German, cp437 encodable
    'café',         # French
    'résumé',       # French
    'München',      # German
    'São Paulo',    # Portuguese
]

# Non-cp437-encodable names (should still fall back to utf-8)
UNICODE_ONLY_NAMES = [
    '你好',         # Chinese
    '日本語',       # Japanese
    '한국어',       # Korean
]

ASCII_NAMES = [
    'hello.txt',
    'simple',
    'test_file.zip',
]


class OldEncoder:
    """Original _encodeFilenameFlags implementation (before patch)"""
    @staticmethod
    def encode(filename, flag_bits):
        try:
            return filename.encode('ascii'), flag_bits
        except UnicodeEncodeError:
            return filename.encode('utf-8'), flag_bits | _MASK_UTF_FILENAME


class NewEncoder:
    """New _encodeFilenameFlags implementation (after patch)"""
    @staticmethod
    def encode(filename, flag_bits):
        if flag_bits & _MASK_UTF_FILENAME:
            encoding = 'ascii'
        else:
            encoding = 'cp437'
        try:
            return filename.encode(encoding), flag_bits & ~_MASK_UTF_FILENAME
        except UnicodeEncodeError:
            return filename.encode('utf-8'), flag_bits | _MASK_UTF_FILENAME


def format_flag_bits(bits):
    """Human-readable flag_bits representation"""
    parts = []
    if bits & _MASK_UTF_FILENAME:
        parts.append('UTF8')
    if bits & _MASK_USE_DATA_DESCRIPTOR:
        parts.append('DD')
    if bits & _MASK_COMPRESS_OPTION_1:
        parts.append('CMP1')
    if bits == 0:
        parts.append('0')
    return '|'.join(parts) if parts else '0'


def test_encoding(name, flag_bits):
    """Test encoding a filename with old and new implementations."""
    try:
        old_bytes, old_flags = OldEncoder.encode(name, flag_bits)
        old_encoding_detected = 'ascii' if old_flags & _MASK_UTF_FILENAME != old_flags else 'ascii'
        # Infer what encoding was actually used
        if old_flags & _MASK_UTF_FILENAME and flag_bits & _MASK_UTF_FILENAME == 0:
            old_enc_used = 'utf-8'
        elif old_flags & _MASK_UTF_FILENAME == 0 and flag_bits & _MASK_UTF_FILENAME:
            old_enc_used = 'ascii'
        elif old_flags & _MASK_UTF_FILENAME:
            old_enc_used = 'utf-8 (fallback)'
        else:
            old_enc_used = 'ascii'
    except Exception as e:
        old_bytes, old_flags = f'ERROR: {e}', 0
        old_enc_used = str(e)

    try:
        new_bytes, new_flags = NewEncoder.encode(name, flag_bits)
        if new_flags & _MASK_UTF_FILENAME and flag_bits & _MASK_UTF_FILENAME == 0:
            new_enc_used = 'utf-8 (fallback)'
        elif new_flags & _MASK_UTF_FILENAME == 0 and flag_bits & _MASK_UTF_FILENAME:
            new_enc_used = 'ascii'
        elif new_flags & _MASK_UTF_FILENAME:
            new_enc_used = 'utf-8 (fallback)'
        elif isinstance(new_bytes, bytes) and new_bytes == name.encode('cp437', errors='replace'):
            new_enc_used = 'cp437'
        else:
            new_enc_used = 'utf-8 (fallback)'
    except Exception as e:
        new_bytes, new_flags = f'ERROR: {e}', 0
        new_enc_used = str(e)

    return {
        'filename': name,
        'input_flags': format_flag_bits(flag_bits),
        'old_bytes': old_bytes.hex() if isinstance(old_bytes, bytes) else 'ERROR',
        'old_flags': format_flag_bits(old_flags) if isinstance(old_flags, int) else 'ERROR',
        'old_encoding': old_enc_used,
        'new_bytes': new_bytes.hex() if isinstance(new_bytes, bytes) else 'ERROR',
        'new_flags': format_flag_bits(new_flags) if isinstance(new_flags, int) else 'ERROR',
        'new_encoding': new_enc_used,
        'bytes_match': old_bytes == new_bytes if isinstance(old_bytes, bytes) and isinstance(new_bytes, bytes) else False,
        'flags_match': old_flags == new_flags if isinstance(old_flags, int) and isinstance(new_flags, int) else False,
    }


def main():
    results = []
    changed = 0
    unchanged = 0

    print("=" * 80)
    print("PCA-0001: _encodeFilenameFlags OUTPUT_FORMAT_CHANGE Test")
    print("=" * 80)

    # Test 1: cp437-encodable names WITHOUT UTF-8 flag
    # This is the primary scenario where behavior changes
    print("\n--- Scenario 1: CP437-encodable names, no UTF-8 flag (flag_bits=0) ---")
    for name in CP437_ENCODABLE_NAMES:
        r = test_encoding(name, 0)
        results.append(r)
        if not r['bytes_match']:
            changed += 1
            status = "CHANGED"
        else:
            unchanged += 1
            status = "UNCHANGED"
        print(f"\n  Name: '{r['filename']}'")
        print(f"  [{status}]")
        print(f"    Old: bytes={r['old_bytes']}, flags={r['old_flags']} ({r['old_encoding']})")
        print(f"    New: bytes={r['new_bytes']}, flags={r['new_flags']} ({r['new_encoding']})")

    # Test 2: cp437-encodable names WITH UTF-8 flag
    # Both implementations should use ascii -> utf-8 fallback
    print("\n--- Scenario 2: CP437-encodable names, WITH UTF-8 flag (flag_bits=0x800) ---")
    for name in CP437_ENCODABLE_NAMES:
        r = test_encoding(name, _MASK_UTF_FILENAME)
        results.append(r)
        if not r['bytes_match']:
            changed += 1
            status = "CHANGED"
        else:
            unchanged += 1
            status = "UNCHANGED"
        print(f"\n  Name: '{r['filename']}'")
        print(f"  [{status}]")
        print(f"    Old: bytes={r['old_bytes']}, flags={r['old_flags']} ({r['old_encoding']})")
        print(f"    New: bytes={r['new_bytes']}, flags={r['new_flags']} ({r['new_encoding']})")

    # Test 3: ASCII names
    print("\n--- Scenario 3: ASCII names (should be identical) ---")
    for name in ASCII_NAMES:
        for flags in [0, _MASK_UTF_FILENAME]:
            r = test_encoding(name, flags)
            results.append(r)
            if not r['bytes_match'] or not r['flags_match']:
                changed += 1
                status = "CHANGED"
            else:
                unchanged += 1
                status = "UNCHANGED"
            print(f"\n  Name: '{r['filename']}', input_flags={r['input_flags']}")
            print(f"  [{status}]")
            print(f"    Old: bytes={r['old_bytes']}, flags={r['old_flags']} ({r['old_encoding']})")
            print(f"    New: bytes={r['new_bytes']}, flags={r['new_flags']} ({r['new_encoding']})")

    # Test 4: Unicode-only names (not cp437 encodable)
    print("\n--- Scenario 4: Unicode-only names (not cp437-encodable) ---")
    for name in UNICODE_ONLY_NAMES:
        for flags in [0, _MASK_UTF_FILENAME]:
            r = test_encoding(name, flags)
            results.append(r)
            if not r['bytes_match']:
                changed += 1
                status = "CHANGED"
            else:
                unchanged += 1
                status = "UNCHANGED"
            print(f"\n  Name: '{r['filename']}', input_flags={r['input_flags']}")
            print(f"  [{status}]")
            print(f"    Old: bytes={r['old_bytes']}, flags={r['old_flags']} ({r['old_encoding']})")
            print(f"    New: bytes={r['new_bytes']}, flags={r['new_flags']} ({r['new_encoding']})")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Total tests: {len(results)}")
    print(f"  Changed behaviors: {changed}")
    print(f"  Unchanged behaviors: {unchanged}")

    # Verify the key finding: cp437-encodable names w/o UTF-8 flag should differ
    key_test = test_encoding(CP437_ENCODABLE_NAMES[0], 0)
    if not key_test['bytes_match']:
        print(f"\n  ✓ KEY FINDING CONFIRMED: '{CP437_ENCODABLE_NAMES[0]}' w/o UTF-8 flag")
        print(f"    Old encoding: {key_test['old_encoding']} (bytes={key_test['old_bytes']})")
        print(f"    New encoding: {key_test['new_encoding']} (bytes={key_test['new_bytes']})")
        print(f"    -> This confirms the OUTPUT_FORMAT_CHANGE")
    else:
        print(f"\n  ✗ KEY FINDING NOT REPRODUCED: bytes match unexpectedly")

    # Save structured results
    import json
    result_path = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(result_path, 'w') as f:
        json.dump({
            'finding_id': 'PCA-0001',
            'entry_id': 'PCA-TE-0001',
            'total_tests': len(results),
            'changed': changed,
            'unchanged': unchanged,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {result_path}")

    return 0 if changed > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
