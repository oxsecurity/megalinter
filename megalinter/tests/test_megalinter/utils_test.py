#!/usr/bin/env python3
"""
Unit tests for utils class

"""
import re
import unittest

from megalinter import utils
from megalinter.logger import sanitize_string, fetch_gitleaks_regexes


class utils_test(unittest.TestCase):
    def test_sanitize_string(self):
        input_string = (
            "AWS Key: AKIAIOSFODNN7EXAMPLE and GitHub Token: ghp_abcdEFGHijklMNOPqrstUVWXyz1234567890"
        )
        expected_output = (
            "AWS Key: [HIDDEN BY MEGALINTER] and GitHub Token: [HIDDEN BY MEGALINTER]"
        )

        sanitized = sanitize_string(input_string)

        # We don't know exactly what pywhat will match, so check if sensitive parts are gone
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", sanitized)
        self.assertNotIn("ghp_abcdEFGHijklMNOPqrstUVWXyz1234567890", sanitized)
        self.assertIn("[HIDDEN BY MEGALINTER]", sanitized)

        # Optional: stricter check if needed
        self.assertEqual(
            sanitized.count("[HIDDEN BY MEGALINTER]"), 2,
            "There should be exactly 2 [HIDDEN BY MEGALINTER] in the output"
        )

    def test_fetch_gitleaks_regexes_remote(self):
        # Test fetching Gitleaks regexes from the remote URL
        regexes = fetch_gitleaks_regexes(force_use_local_file=False)
        self.assertIsInstance(regexes, list, "Regexes should be a list")
        self.assertGreater(len(regexes), 0, "Regexes list should not be empty")

    def test_fetch_gitleaks_regexes_local(self):
        # Test fetching Gitleaks regexes from the local file
        regexes = fetch_gitleaks_regexes(force_use_local_file=True)
        self.assertIsInstance(regexes, list, "Regexes should be a list")
        self.assertGreater(len(regexes), 0, "Regexes list should not be empty")