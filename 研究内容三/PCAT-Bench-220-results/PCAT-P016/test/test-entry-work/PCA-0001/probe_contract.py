"""Contract probe for sys.lazy_modules type change (PCA-0001)."""
import sys
import json

results = {}

# 1. Type check
results["type_test"] = {
    "actual_type": str(type(sys.lazy_modules)),
    "is_dict": isinstance(sys.lazy_modules, dict),
    "is_set": isinstance(sys.lazy_modules, set),
}

# 2. Set operations (should work on set, may work on dict)
try:
    sys.lazy_modules.clear()
    results["clear"] = "ok - method exists and works"
except AttributeError as e:
    results["clear"] = f"FAIL - {e}"

try:
    sys.lazy_modules.add("test.module.name")
    results["add"] = "ok - method exists and works"
except AttributeError as e:
    results["add"] = f"FAIL - {e}"

try:
    present = "test.module.name" in sys.lazy_modules
    results["membership"] = f"ok - 'in' works: {present}"
except TypeError as e:
    results["membership"] = f"FAIL - {e}"

try:
    length = len(sys.lazy_modules)
    results["len"] = f"ok - len() works: {length}"
except TypeError as e:
    results["len"] = f"FAIL - {e}"

# 3. Dict operations (should fail on set, work on dict)
try:
    sys.lazy_modules["some.key"]
    results["dict_subscript"] = "SUCCEEDED - dict-style access works"
except (TypeError, KeyError) as e:
    results["dict_subscript"] = f"FAILED as expected for set - {type(e).__name__}: {e}"

try:
    sys.lazy_modules.keys()
    results["dict_keys"] = "SUCCEEDED - .keys() works"
except AttributeError as e:
    results["dict_keys"] = f"FAILED as expected for set - {e}"

try:
    sys.lazy_modules.items()
    results["dict_items"] = "SUCCEEDED - .items() works"
except AttributeError as e:
    results["dict_items"] = f"FAILED as expected for set - {e}"

print(json.dumps(results, indent=2))
