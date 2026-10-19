#!/usr/bin/env python3
"""Coverage runner for sysconfig parse_config_h — avoids sys.path pollution."""
import importlib.util
import io
import json
import os
import sys

source_dir = os.path.abspath(sys.argv[1])
module_path = os.path.join(source_dir, 'Lib', 'sysconfig', '__init__.py')

spec = importlib.util.spec_from_file_location('sysconfig', module_path)
sysconfig_module = importlib.util.module_from_spec(spec)

import coverage
cov = coverage.Coverage(
    source=[os.path.join(source_dir, 'Lib', 'sysconfig')],
    data_file=os.environ.get('COVERAGE_FILE', '.coverage')
)
cov.start()

spec.loader.exec_module(sysconfig_module)

config_content = """#define PY_BUILTIN_HASHLIB_HASHES "blake2,sha256,sha512"
#define PY_VERSION "3.14"
#define PY_MAJOR_VERSION 3
#define PY_MINOR_VERSION 14
#define PY_MICRO_VERSION 0
#define HAVE_STDARG_H 1
#define SIZEOF_INT 4
#define SIZEOF_VOID_P 8
#define MULTIARCH "x86_64-linux-gnu"
#define HOST_GNU_TYPE "x86_64-pc-linux-gnu"
#define BUILTIN_MODULE_ARRAY
#define EMPTY_STRING ""
#define QUOTES_INSIDE "hello \\"world\\""
#define LEADING_SPACE "  indented"
#define TRAILING_SPACE "trailing  "
/****** #undef DISABLED_FEATURE ******/
/****** #undef OTHER_FEATURE ******/
"""

fp = io.StringIO(config_content)
result = sysconfig_module.parse_config_h(fp)

cov.stop()
cov.save()

json_path = os.environ.get('COVERAGE_JSON', 'coverage.json')
cov.json_report(outfile=json_path)

print(json.dumps({
    "status": "ok",
    "coverage_file": os.environ.get('COVERAGE_FILE', '.coverage'),
    "coverage_json": json_path,
    "result": dict(result)
}))
