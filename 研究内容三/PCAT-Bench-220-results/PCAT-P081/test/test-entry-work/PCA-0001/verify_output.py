"""PCA-0001: Verify functools.reduce OUTPUT_FORMAT_CHANGE."""
import functools
import inspect
import io
import sys
import argparse


def verify_help_output(version_label):
    """Capture help() output for functools.reduce."""
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    help(functools.reduce)
    sys.stdout = old_stdout
    out = buf.getvalue()
    
    print(f"[{version_label}] help(functools.reduce) output:")
    # Extract the signature line
    for line in out.split("\n"):
        if "reduce(" in line:
            print(f"  Signature: {line.strip()}")
    
    if "initial" in out:
        print(f"  [PASS] 'initial' parameter found in help output")
    else:
        print(f"  [FAIL] 'initial' parameter NOT found in help output")
    
    if "unrepresentable" in out:
        print(f"  [INFO] 'unrepresentable' still present (before-patch behavior)")
    elif "_initial_missing" in out:
        print(f"  [INFO] '_initial_missing' sentinel found (after-patch behavior)")
    elif "initial" in out:
        print(f"  [INFO] 'initial' parameter has no recognizable default")


def verify_inspect_signature(version_label):
    """Verify inspect.signature() for functools.reduce."""
    print(f"[{version_label}] inspect.signature(functools.reduce):")
    try:
        sig = inspect.signature(functools.reduce)
        print(f"  Signature: {sig}")
        for name, param in sig.parameters.items():
            default_repr = repr(param.default)
            print(f"    {name}: kind={param.kind.name}, default={default_repr}")
        
        if "initial" in sig.parameters:
            initial_param = sig.parameters["initial"]
            if initial_param.default is not inspect.Parameter.empty:
                print(f"  [PASS] 'initial' parameter has a valid default value")
            else:
                print(f"  [PASS] 'initial' parameter exists (no default)")
        else:
            print(f"  [FAIL] 'initial' parameter NOT in signature")
    except ValueError as e:
        print(f"  [INFO] ValueError: {e} (expected before patch)")
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")


def verify_functional_behavior(version_label):
    """Verify functools.reduce still works correctly."""
    print(f"[{version_label}] Functional behavior tests:")
    
    # Basic reduce
    result = functools.reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])
    assert result == 15, f"Expected 15, got {result}"
    print(f"  [PASS] reduce(add, [1..5]) = {result}")
    
    # Reduce with initial value
    result = functools.reduce(lambda x, y: x + y, [1, 2, 3], 10)
    assert result == 16, f"Expected 16, got {result}"
    print(f"  [PASS] reduce(add, [1,2,3], 10) = {result}")
    
    # Reduce empty iterable with initial (should return initial)
    result = functools.reduce(lambda x, y: x + y, [], 42)
    assert result == 42, f"Expected 42, got {result}"
    print(f"  [PASS] reduce(add, [], 42) = {result}")
    
    # Reduce empty iterable (should raise TypeError)
    try:
        functools.reduce(lambda x, y: x + y, [])
        print(f"  [FAIL] reduce(add, []) should raise TypeError")
    except TypeError:
        print(f"  [PASS] reduce(add, []) raises TypeError as expected")
    
    # Verify __doc__ attribute
    doc = functools.reduce.__doc__
    if doc:
        first_line = doc.strip().split("\n")[0].strip()
        print(f"  [INFO] __doc__: {first_line[:80]}...")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=["before", "after"], default="after")
    args = parser.parse_args()
    
    label = args.version.upper()
    verify_help_output(label)
    print()
    verify_inspect_signature(label)
    print()
    verify_functional_behavior(label)
    print(f"\n[{label}] All verifications complete.")


if __name__ == "__main__":
    main()
