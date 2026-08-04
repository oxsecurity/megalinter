#!/usr/bin/env python3
"""
Unit tests for utils class

"""

import os
import unittest
import uuid
from unittest.mock import patch

from megalinter import config, utils
from megalinter.logger import fetch_betterleaks_regexes, sanitize_string


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

    def test_report_folder_excluded_by_default(self):
        # init_config(request_id, workspace=None) copies os.environ wholesale into
        # the config when no workspace is given, so REPORT_OUTPUT_FOLDER,
        # EXCLUDED_DIRECTORIES or MEGALINTER_CONFIG set in the ambient environment
        # (plausible when running inside a MegaLinter container) would otherwise
        # leak into this test
        request_id = str(uuid.uuid1())
        with patch.dict(os.environ, {}, clear=True):
            config.init_config(request_id)
        try:
            excluded = utils.get_excluded_directories(request_id)
            self.assertIn("megalinter-reports", excluded)
        finally:
            config.delete(request_id)

    def test_report_folder_excluded_despite_excluded_directories_override(self):
        # EXCLUDED_DIRECTORIES replaces the defaults, but MegaLinter's own output
        # folder must never become lintable
        request_id = str(uuid.uuid1())
        with patch.dict(os.environ, {}, clear=True):
            config.init_config(request_id)
        try:
            config.set_value(request_id, "EXCLUDED_DIRECTORIES", ["only_this"])
            excluded = utils.get_excluded_directories(request_id)
            self.assertIn("only_this", excluded)
            self.assertIn("megalinter-reports", excluded)
        finally:
            config.delete(request_id)

    def test_custom_report_folder_excluded_despite_override(self):
        request_id = str(uuid.uuid1())
        with patch.dict(os.environ, {}, clear=True):
            config.init_config(request_id)
        try:
            config.set_value(request_id, "REPORT_OUTPUT_FOLDER", "build/ml-reports")
            config.set_value(request_id, "EXCLUDED_DIRECTORIES", ["only_this"])
            excluded = utils.get_excluded_directories(request_id)
            self.assertIn("build/ml-reports", excluded)
        finally:
            config.delete(request_id)
