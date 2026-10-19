#!/usr/bin/env python3
"""
PCA-0002 test harness: _read_conf_file signature compatibility.

Tests that:
1. A subclass overriding _read_conf_file with old 1-parameter signature fails
2. A subclass overriding _read_conf_file with new 3-parameter signature works
3. The old-style override receives TypeError when called with 3 args
4. Direct calls with old signature (1 arg) continue to work

This is a standalone test that recreates the pattern of Cli._read_conf_file
without requiring libdnf/hawkey imports.
"""
import sys
import os
import unittest


# ============ Simulated old code (before patch) ============

class ConfigStub:
    """Minimal config stub for testing."""
    def __init__(self):
        self.releasever = None
        self.releasever_major = None
        self.releasever_minor = None


class CliOld:
    """Simulated Cli class with OLD _read_conf_file signature."""

    def configure_internal(self, releasever_val):
        """Simulates the call site that passes args to _read_conf_file."""
        # OLD call: only releasever
        return self._read_conf_file(releasever_val)

    def _read_conf_file(self, releasever=None):
        """OLD signature: only releasever parameter."""
        conf = ConfigStub()
        conf.releasever = releasever
        return conf


class CliOldSubclassOverride(CliOld):
    """Subclass that overrides _read_conf_file with old signature."""
    def _read_conf_file(self, releasever=None):
        conf = ConfigStub()
        conf.releasever = f"overridden:{releasever}"
        return conf


# ============ Simulated new code (after patch) ============

class CliNew:
    """Simulated Cli class with NEW _read_conf_file signature."""

    def configure_internal(self, releasever_val, releasever_major_val=None, releasever_minor_val=None):
        """NEW call site: passes 3 arguments."""
        return self._read_conf_file(releasever_val, releasever_major_val, releasever_minor_val)

    def _read_conf_file(self, releasever=None, releasever_major=None, releasever_minor=None):
        """NEW signature: three optional parameters."""
        conf = ConfigStub()
        conf.releasever = releasever
        conf.releasever_major = releasever_major
        conf.releasever_minor = releasever_minor
        return conf


class CliNewSubclassOverride(CliNew):
    """Subclass that overrides _read_conf_file with OLD signature - THIS WILL BREAK."""
    def _read_conf_file(self, releasever=None):
        conf = ConfigStub()
        conf.releasever = f"overridden:{releasever}"
        return conf


class TestReadConfFileSignature(unittest.TestCase):
    """Test the signature compatibility of _read_conf_file."""

    def test_00_old_class_works_with_old_call(self):
        """Old-style class with 1-arg call site should work."""
        cli = CliOld()
        result = cli.configure_internal("40")
        self.assertEqual(result.releasever, "40")

    def test_01_new_class_works_with_new_call(self):
        """New-style class with 3-arg call site should work."""
        cli = CliNew()
        result = cli.configure_internal("40", "4", "0")
        self.assertEqual(result.releasever, "40")
        self.assertEqual(result.releasever_major, "4")
        self.assertEqual(result.releasever_minor, "0")

    def test_02_new_class_default_args(self):
        """New-style class with defaults should work (only releasever)."""
        cli = CliNew()
        result = cli.configure_internal("40")
        self.assertEqual(result.releasever, "40")
        self.assertIsNone(result.releasever_major)
        self.assertIsNone(result.releasever_minor)

    def test_03_old_override_with_new_call_BREAKS(self):
        """Subclass with OLD override called via NEW 3-arg call site should BREAK."""
        cli = CliNewSubclassOverride()
        with self.assertRaises(TypeError) as ctx:
            cli.configure_internal("40", "4", "0")
        # The error should mention the positional argument count
        self.assertIn("argument", str(ctx.exception).lower())

    def test_04_new_forward_compatible(self):
        """New class called with old-style 1-arg should still work (optional params)."""
        cli = CliNew()
        # Direct call with old signature (releasever only)
        result = cli._read_conf_file("40")
        self.assertEqual(result.releasever, "40")
        self.assertIsNone(result.releasever_major)
        self.assertIsNone(result.releasever_minor)

    def test_05_or_else_logic(self):
        """Test the or_else priority logic used in the patch."""
        def or_else(*args):
            for arg in args:
                if arg is not None:
                    return arg
            return None

        # Priority: first non-None wins
        self.assertEqual(or_else("cli", "detected", "config"), "cli")
        self.assertEqual(or_else(None, "detected", "config"), "detected")
        self.assertEqual(or_else(None, None, "config"), "config")
        self.assertEqual(or_else(None, None, None), None)

    def test_06_old_subclass_old_call_works(self):
        """Old subclass with old-style 1-arg call should still work (no regression)."""
        cli = CliOldSubclassOverride()
        result = cli.configure_internal("40")
        self.assertEqual(result.releasever, "overridden:40")


if __name__ == "__main__":
    unittest.main()
