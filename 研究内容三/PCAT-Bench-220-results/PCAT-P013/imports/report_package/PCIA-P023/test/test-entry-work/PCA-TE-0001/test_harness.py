#!/usr/bin/env python3
"""Test harness for parse_config_h OUTPUT_FORMAT_CHANGE compatibility testing.

Tests parse_config_h from sysconfig module with a synthetic pyconfig.h-like
input containing various #define patterns (quoted and unquoted values).

Usage:
  python3 test_harness.py <sysconfig_source_dir>

The sysconfig_source_dir must contain a Lib/sysconfig/ package.
For BEFORE: point to base_commit checkout
For AFTER:  point to patched worktree
"""

import json
import io
import sys
import os


def make_config_h_content():
    """Generate a pyconfig.h-like file with diverse value patterns."""
    lines = [
        '#define PY_BUILTIN_HASHLIB_HASHES "blake2,sha256,sha512"\n',
        '#define PY_VERSION "3.14"\n',
        '#define PY_MAJOR_VERSION 3\n',
        '#define PY_MINOR_VERSION 14\n',
        '#define PY_MICRO_VERSION 0\n',
        '#define HAVE_STDARG_H 1\n',
        '#define SIZEOF_INT 4\n',
        '#define SIZEOF_VOID_P 8\n',
        '#define MULTIARCH "x86_64-linux-gnu"\n',
        '#define HOST_GNU_TYPE "x86_64-pc-linux-gnu"\n',
        '#define BUILTIN_MODULE_ARRAY\n',
        '#define EMPTY_STRING ""\n',
        '#define QUOTES_INSIDE "hello \\"world\\""\n',
        '#define LEADING_SPACE "  indented"\n',
        '#define TRAILING_SPACE "trailing  "\n',
        '/****** #undef DISABLED_FEATURE ******/\n',
        '/****** #undef OTHER_FEATURE ******/\n',
    ]
    return ''.join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_harness.py <sysconfig_source_dir>", file=sys.stderr)
        sys.exit(1)

    source_dir = os.path.abspath(sys.argv[1])
    lib_dir = os.path.join(source_dir, 'Lib')

    if not os.path.isdir(lib_dir):
        print(f"ERROR: Lib directory not found at {lib_dir}", file=sys.stderr)
        sys.exit(2)

    sys.path.insert(0, lib_dir)
    import sysconfig

    config_content = make_config_h_content()
    fp = io.StringIO(config_content)

    result = sysconfig.parse_config_h(fp)

    output = {
        "parse_config_h_result": dict(result),
        "keys": sorted(result.keys()),
        "num_entries": len(result),
    }

    print(json.dumps(output, indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
