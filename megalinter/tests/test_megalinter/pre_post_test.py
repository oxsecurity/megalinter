#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest
import uuid

from megalinter import utilstest


class PrePostTest(unittest.TestCase):
    def __init__(self, args) -> None:
        self.request_id = str(uuid.uuid1())
        super().__init__(args)

    def setUp(self):
        utilstest.linter_test_setup(
            {
                "request_id": self.request_id,
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
                "request_id": self.request_id,
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("pre-test command has been called", output)
        self.assertIn("npm run test has been called", output)
        self.assertIn("descriptor pre-command has been run", output)
        self.assertIn("descriptor post-command has been run", output)
        self.assertIn("linter pre-command has been run", output)
        self.assertIn("linter post-command has been run", output)
