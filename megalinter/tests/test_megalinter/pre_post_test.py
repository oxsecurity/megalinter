#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest

from megalinter.tests.test_megalinter.helpers import utilstest


class PrePostTest(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}pre-post-test",
                "required_config_file": True,
            }
        )

    def test_pre_post_success(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "MULTI_STATUS": "false",
                "GITHUB_COMMENT_REPORTER": "false",
                "LOG_LEVEL": "DEBUG",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("pre-test command has been called", output)
        self.assertIn("npm run test has been called", output)
