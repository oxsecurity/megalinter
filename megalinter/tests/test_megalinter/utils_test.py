#!/usr/bin/env python3
"""
Unit tests for utils class

"""

import re
import unittest
import warnings

from megalinter.logger import fetch_betterleaks_regexes, sanitize_string
from megalinter.utils import fix_regex_pattern


class utils_test(unittest.TestCase):
    def test_sanitize_string(self):
        input_string = "AWS Key: AKIAIOSFODNN7EXAMPLE and GitHub Token: ghp_abcdEFGHijklMNOPqrstUVWXyz1234567890"
        sanitized = sanitize_string(input_string)

        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", sanitized)
        self.assertNotIn("ghp_abcdEFGHijklMNOPqrstUVWXyz1234567890", sanitized)
        self.assertIn("HIDDEN_BY_MEGALINTER", sanitized)

        # Optional: stricter check if needed
        self.assertEqual(
            sanitized.count("HIDDEN_BY_MEGALINTER"),
            2,
            "There should be exactly 2 HIDDEN_BY_MEGALINTER in the output",
        )

    def test_fetch_betterleaks_regexes(self):
        # Test loading betterleaks regexes from the vendored ruleset
        regexes = fetch_betterleaks_regexes()
        self.assertIsInstance(regexes, list, "Regexes should be a list")
        self.assertGreater(len(regexes), 0, "Regexes list should not be empty")

    def test_fix_regex_pattern_posix_character_classes(self):
        fixed = fix_regex_pattern(r"\b(pat[[:alnum:]]{14}\.[a-f0-9]{64})\b")
        self.assertEqual(fixed, r"\b(pat[a-zA-Z0-9]{14}\.[a-f0-9]{64})\b")
        # The translated pattern must match a real Airtable personal access token
        token = "patAbCdEf01234567." + "0123456789abcdef" * 4  # betterleaks:allow
        self.assertIsNotNone(re.search(fixed, f"token: {token} used"))

    def test_betterleaks_regexes_compile_without_warnings(self):
        regexes = fetch_betterleaks_regexes()
        re.purge()  # Clear the compile cache so warnings are re-emitted
        with warnings.catch_warnings():
            warnings.simplefilter("error", FutureWarning)
            for pattern in regexes:
                re.compile(pattern)
