#!/usr/bin/env python3
"""
PCA-0002: OUTPUT_FORMAT_CHANGE - Source-level verification.

Verifies the CLI output change by parsing Python source and
comparing before/after gpgsigcheck method differences.
"""
import ast
import sys
import os

def get_method_source(filepath, method_name):
    """Extract a method definition source from a Python file."""
    with open(filepath) as f:
        content = f.read()
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            lines = content.split('\n')
            return '\n'.join(lines[node.lineno - 1:node.end_lineno])
    return None

def check_contains_keywords(source, keywords, label):
    """Check source contains certain keywords."""
    for kw in keywords:
        if kw in source:
            print(f"  PASS [{label}]: Contains '{kw}'")
        else:
            print(f"  FAIL [{label}]: Missing '{kw}'")
            return False
    return True

def verify():
    after_file = os.environ.get("AFTER_CLI")
    before_file = os.environ.get("BEFORE_CLI")
    
    after_source = get_method_source(after_file, "gpgsigcheck") if after_file else None
    before_source = get_method_source(before_file, "gpgsigcheck") if before_file else None
    
    # After verification
    if after_source:
        print("=== AFTER (patched) gpgsigcheck ===")
        
        # Check for the plugin recommendation feature
        checks = [
            ("print_plugin_recommendation = False", "flag initialization"),
            ("InvalidInstalledGPGKeyError", "specific exception catch"),
            ("print_plugin_recommendation = True", "flag set on expired key"),
            ("Try to add '--enableplugin=expired-pgp-keys'", "plugin suggestion message"),
            ("logger.info(msg)", "info-level output"),
        ]
        all_pass = True
        for keyword, label in checks:
            if keyword in after_source:
                print(f"  PASS: Contains '{keyword}' ({label})")
            else:
                print(f"  FAIL: Missing '{keyword}' ({label})")
                all_pass = False
        
        # Verify BEFORE for comparison 
        if before_source:
            print("\n=== BEFORE (unpatched) gpgsigcheck ===")
            # Before should NOT have any of these new features
            before_checks = [
                ("print_plugin_recommendation", "plugin recommendation flag"),
                ("InvalidInstalledGPGKeyError", "specific exception catch"),
                ("expired-pgp-keys", "plugin suggestion"),
            ]
            for keyword, label in before_checks:
                if keyword in before_source:
                    print(f"  INFO: Before already contains '{keyword}' ({label})")
                else:
                    print(f"  PASS: Before does NOT contain '{keyword}' ({label})")
            
            # Check the output section changed
            if "if print_plugin_recommendation" not in before_source:
                print("  PASS: Before has no plugin recommendation output block")
            else:
                print("  INFO: Before already has plugin recommendation output block")
        
        if all_pass:
            print("\nRESULT: All output format change verifications PASSED")
            return True
        else:
            print("\nRESULT: Some verifications FAILED")
            return False
    else:
        print("FAIL: Could not find gpgsigcheck method")
        return False

if __name__ == "__main__":
    try:
        result = verify()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
