#!/usr/bin/env python3
"""
PCA-0001: ERROR_EXCEPTION_CHANGE - Source-level verification.

Verifies the exception hierarchy by parsing Python source and
comparing before/after exception module differences.
"""
import ast
import sys
import os

def parse_exception_hierarchy(filepath):
    """Parse Python source to extract exception class hierarchy."""
    with open(filepath) as f:
        tree = ast.parse(f.read())
    
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(f"{base.value.id}.{base.attr}")
            classes[node.name] = {
                'bases': bases,
                'lineno': node.lineno,
                'end_lineno': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
            }
    return classes

def verify():
    """Main verification logic."""
    # Get file paths from environment
    after_file = os.environ.get("AFTER_EXCEPTIONS")
    before_file = os.environ.get("BEFORE_EXCEPTIONS")
    
    if not after_file:
        print("FAIL: AFTER_EXCEPTIONS env var not set")
        return False
    
    after_classes = parse_exception_hierarchy(after_file)
    
    # Check InvalidInstalledGPGKeyError exists in AFTER
    assert "InvalidInstalledGPGKeyError" in after_classes, \
        "InvalidInstalledGPGKeyError class not found in patched dnf/exceptions.py"
    
    cls = after_classes["InvalidInstalledGPGKeyError"]
    print(f"PASS: InvalidInstalledGPGKeyError found at line {cls['lineno']}")
    print(f"  Bases: {cls['bases']}")
    
    # Verify it inherits from Error
    assert "Error" in cls['bases'], \
        f"InvalidInstalledGPGKeyError should inherit from Error, got bases: {cls['bases']}"
    print("PASS: InvalidInstalledGPGKeyError inherits from Error")
    
    # Verify Error inherits from Exception
    error_cls = after_classes.get("Error")
    if error_cls:
        assert "Exception" in error_cls['bases'] or "BaseException" in error_cls['bases'], \
            f"Error should inherit from Exception, got bases: {error_cls['bases']}"
        print(f"PASS: Error inherits from {error_cls['bases']}")
    
    # Verify the hierarchy: InvalidInstalledGPGKeyError -> Error -> Exception
    hierarchy = "InvalidInstalledGPGKeyError"
    for base in cls['bases']:
        if base in after_classes:
            hierarchy += f" -> {base}"
            for b2 in after_classes[base]['bases']:
                if b2 in after_classes or b2 in ('Exception', 'BaseException'):
                    hierarchy += f" -> {b2}"
    
    print(f"PASS: Hierarchy: {hierarchy}")
    
    # Compare with BEFORE if available
    if before_file and os.path.exists(before_file):
        before_classes = parse_exception_hierarchy(before_file)
        # Before should NOT have InvalidInstalledGPGKeyError
        has_invalid = "InvalidInstalledGPGKeyError" in before_classes
        print(f"PASS: Before file does NOT contain InvalidInstalledGPGKeyError (found={has_invalid})")
        assert not has_invalid, f"Before file unexpectedly contains InvalidInstalledGPGKeyError"
    
    # Verify the exception type change location in base.py
    after_base = os.environ.get("AFTER_BASE")
    if after_base and os.path.exists(after_base):
        with open(after_base) as f:
            content = f.read()
        assert "InvalidInstalledGPGKeyError" in content, \
            "After base.py should raise InvalidInstalledGPGKeyError"
        assert "raise dnf.exceptions.InvalidInstalledGPGKeyError" in content, \
            "After base.py should raise dnf.exceptions.InvalidInstalledGPGKeyError"
        print("PASS: After base.py raises InvalidInstalledGPGKeyError on expired key path")
    
    before_base = os.environ.get("BEFORE_BASE")
    if before_base and os.path.exists(before_base):
        with open(before_base) as f:
            content = f.read()
        assert "InvalidInstalledGPGKeyError" not in content, \
            "Before base.py should NOT raise InvalidInstalledGPGKeyError"
        # But should still have the old Error raise
        assert "raise dnf.exceptions.Error(_prov_key_data(msg))" in content or \
               "raise dnf.exceptions.Error(_prov_key_data" in content, \
            "Before base.py should raise Error (old behavior)"
        print("PASS: Before base.py raises generic Error (old behavior)")
    
    return True

if __name__ == "__main__":
    try:
        result = verify()
        if result:
            print("\nRESULT: All verifications PASSED")
            sys.exit(0)
        else:
            sys.exit(1)
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
