#!/usr/bin/env python3
"""
Contract verification for PCA-0001: INPUT_CONTRACT_CHANGE in rpm2py_format.

Verifies that:
1. Lowercase query tags produce the same output before and after the patch
2. Uppercase query tags change from literal pass-through (old) to formatted (new)
3. Invalid/unknown tags are unaffected
"""
import re
import sys

# Pure Python reimplementation of the relevant DNF function
# No native bindings required

QFORMAT_MATCH = re.compile(r'%(-?\d*?){([:\w]+?)}')
ALLOWED_QUERY_TAGS = ('name', 'arch', 'epoch', 'version', 'release',
                      'reponame', 'repoid', 'from_repo', 'evr', 'debug_name',
                      'source_name', 'source_debug_name', 'installtime',
                      'buildtime', 'size', 'downloadsize', 'installsize',
                      'provides', 'requires', 'obsoletes', 'conflicts',
                      'suggests', 'recommends', 'enhances', 'supplements',
                      'sourcerpm', 'description', 'summary', 'license', 'url',
                      'reason', 'group', 'vendor', 'packager',)

OPTS_MAPPING = {
    'conflicts': 'conflicts', 'enhances': 'enhances', 'obsoletes': 'obsoletes',
    'provides': 'provides', 'recommends': 'recommends', 'requires': 'requires',
    'requires-pre': 'requires_pre', 'suggests': 'suggests', 'supplements': 'supplements'
}

def brackets(txt):
    return txt.replace('{', '{{').replace('}', '}}')

def rpm2py_format_old(queryformat):
    """Old code BEFORE the patch: no key.lower() before ALLOWED_QUERY_TAGS check."""
    queryformat = queryformat.replace('\\n', '\n').replace('\\t', '\t')
    for key, value in OPTS_MAPPING.items():
        queryformat = queryformat.replace(key, value)
    fmt = ''
    spos = 0
    for item in QFORMAT_MATCH.finditer(queryformat):
        fmt += brackets(queryformat[spos:item.start()])
        fill = item.groups()[0]
        key = item.groups()[1]
        if key not in ALLOWED_QUERY_TAGS:
            fmt += brackets(item.group())
        else:
            if fill:
                if fill[0] == '-':
                    fill = '>' + fill[1:]
                else:
                    fill = '<' + fill
                fill = ':' + fill
            fmt += '{0.' + key.lower() + fill + '}'
        spos = item.end()
    fmt += brackets(queryformat[spos:])
    return fmt

def rpm2py_format_new(queryformat):
    """New code AFTER the patch: key.lower() before ALLOWED_QUERY_TAGS check."""
    queryformat = queryformat.replace('\\n', '\n').replace('\\t', '\t')
    for key, value in OPTS_MAPPING.items():
        queryformat = queryformat.replace(key, value)
    fmt = ''
    spos = 0
    for item in QFORMAT_MATCH.finditer(queryformat):
        fmt += brackets(queryformat[spos:item.start()])
        fill = item.groups()[0]
        key = item.groups()[1]
        key = key.lower()  # THE PATCH: lowercase before lookup
        if key not in ALLOWED_QUERY_TAGS:
            fmt += brackets(item.group())
        else:
            if fill:
                if fill[0] == '-':
                    fill = '>' + fill[1:]
                else:
                    fill = '<' + fill
                fill = ':' + fill
            fmt += '{0.' + key + fill + '}'
        spos = item.end()
    fmt += brackets(queryformat[spos:])
    return fmt

# Test cases: (name, input_format, expect_identical)
# expect_identical=True means old and new must produce same output
# expect_identical=False means they must differ (uppercase tag behavior change)
TESTS = [
    ("lowercase_simple",    '%{name}', True),
    ("uppercase_simple",    '%{NAME}', False),
    ("lowercase_combo",     '%{name}-%{version}-%{release}.%{arch} (%{reponame})', True),
    ("uppercase_combo",     '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH} (%{REPONAME})', False),
    ("mixed_case_combo",    '%{NAME}-%{version}-%{RELEASE}.%{arch} (%{REPONAME})', False),
    ("invalid_tag_lower",   '%{notfound}', True),
    ("invalid_tag_upper",   '%{NOTFOUND}', True),
    ("empty_string",        '', True),
    ("no_tags",             'plain text', True),
    ("mix_tags_and_text",   'pkg: %{name} (%{ARCH})', False),
]

failed = 0
total = len(TESTS)

print("=" * 72)
print("PCA-0001 Contract Verification: INPUT_CONTRACT_CHANGE")
print("=" * 72)
print()

for name, fmt_input, expect_same in TESTS:
    old = rpm2py_format_old(fmt_input)
    new = rpm2py_format_new(fmt_input)
    identical = (old == new)
    if identical == expect_same:
        status = "PASS"
    else:
        status = "FAIL"
        failed += 1
    
    diff_mark = "✔ same" if identical else "✗ DIFFER"
    print(f"  [{status:4s}] {name:25s} old={old!r:45s}")
    print(f"       {'':25s} new={new!r:45s}")
    print(f"       {'':25s} {diff_mark}  (expect_same={expect_same})")
    print()

print("-" * 72)
print(f"Result: {total - failed}/{total} passed", end="")
if failed:
    print(f", {failed} FAILED", end="")
print()
print()

if failed:
    print("CONCLUSION: ❌ Some contract checks failed - unexpected behavior difference")
    sys.exit(1)
else:
    print("CONCLUSION: ✅ All contract checks passed")
    print("  - Lowercase query tags: behavior preserved (backward compatible)")
    print("  - Uppercase query tags: now correctly formatted (was literal pass-through)")
    print("  - Invalid/unknown tags: behavior unchanged")
    print("  - This is the EXPECTED INPUT_CONTRACT_CHANGE behavior")
    sys.exit(0)
