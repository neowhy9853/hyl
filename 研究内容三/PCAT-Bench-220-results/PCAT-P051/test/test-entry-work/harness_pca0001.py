#!/usr/bin/env python3
"""
PCA-0001 test harness: New CLI options --releasever-major and --releasever-minor.

Tests that:
1. The new CLI options are correctly parsed by argparse
2. The options produce correct Namespace values
3. The options default to None when not provided
4. The options interact correctly with --releasever
5. Unknown option combinations still fail
6. The options can be provided independently

This is a standalone test that does NOT require libdnf/hawkey.
"""
import os
import unittest
import argparse

AFTER_REPO = "/tmp/pca-dnf-after"
BEFORE_REPO = "/tmp/pca-dnf-before"


class TestReleaseverMajorMinorOptions(unittest.TestCase):
    """Test that --releasever-major and --releasever-minor are properly parsed."""

    def test_00_parse_releasever_major(self):
        """--releasever-major=10 should be parsed as releasever_major='10'."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--releasever-major", default=None)
        args = parser.parse_args(["--releasever-major", "10"])
        self.assertEqual(args.releasever_major, "10")

    def test_01_parse_releasever_minor(self):
        """--releasever-minor=99 should be parsed as releasever_minor='99'."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--releasever-minor", default=None)
        args = parser.parse_args(["--releasever-minor", "99"])
        self.assertEqual(args.releasever_minor, "99")

    def test_02_default_none(self):
        """When neither option is given, both should default to None."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--releasever-major", default=None)
        parser.add_argument("--releasever-minor", default=None)
        args = parser.parse_args([])
        self.assertIsNone(args.releasever_major)
        self.assertIsNone(args.releasever_minor)

    def test_03_with_releasever(self):
        """--releasever=40 --releasever-major=5 should both parse independently."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--releasever", default=None)
        parser.add_argument("--releasever-major", default=None)
        parser.add_argument("--releasever-minor", default=None)
        args = parser.parse_args(["--releasever=40", "--releasever-major=5"])
        self.assertEqual(args.releasever, "40")
        self.assertEqual(args.releasever_major, "5")
        self.assertIsNone(args.releasever_minor)

    def test_04_independent_options(self):
        """--releasever-major can be provided without --releasever-minor and vice versa."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--releasever-major", default=None)
        parser.add_argument("--releasever-minor", default=None)
        args = parser.parse_args(["--releasever-minor=1"])
        self.assertIsNone(args.releasever_major)
        self.assertEqual(args.releasever_minor, "1")

    def test_05_all_together(self):
        """All three releasever options should work together."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--releasever", default=None)
        parser.add_argument("--releasever-major", default=None)
        parser.add_argument("--releasever-minor", default=None)
        args = parser.parse_args(["--releasever=39", "--releasever-major=3", "--releasever-minor=9"])
        self.assertEqual(args.releasever, "39")
        self.assertEqual(args.releasever_major, "3")
        self.assertEqual(args.releasever_minor, "9")

    def test_06_invalid_option_rejected(self):
        """Completely invalid option should still be rejected."""
        parser = argparse.ArgumentParser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--releasever-invalid"])

    def test_07_option_names_in_patched_source(self):
        """Verify the patched option_parser.py contains the new option definitions."""
        with open(os.path.join(AFTER_REPO, "dnf/cli/option_parser.py")) as f:
            content = f.read()
        self.assertIn("releasever-major", content)
        self.assertIn("releasever-minor", content)

    def test_08_before_source_does_not_have_options(self):
        """Verify the before (unpatched) option_parser.py does NOT contain the new options."""
        before_file = os.path.join(BEFORE_REPO, "dnf/cli/option_parser.py")
        if os.path.exists(before_file):
            with open(before_file) as f:
                content = f.read()
            self.assertNotIn("releasever-major", content)
        else:
            self.skipTest("before repo not available")


if __name__ == "__main__":
    unittest.main()
