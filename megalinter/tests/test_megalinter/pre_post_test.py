#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest
import uuid

from megalinter import config, utilstest


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
        config.SKIP_DELETE_CONFIG = True
        mega_linter, output = utilstest.call_mega_linter(
            {
                "MULTI_STATUS": "false",
                "GITHUB_COMMENT_REPORTER": "false",
                "LOG_LEVEL": "DEBUG",
                "request_id": self.request_id,
                "MY_INPUT_VARIABLE": "SHOULD_BE_REPLACED",
                "MY_INPUT_VARIABLE_REPLACEMENT": "HAS_BEEN_REPLACED"
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
        self.assertTrue(
            config.get(self.request_id, "MY_OUTPUT_VARIABLE", "")
            == "my output variable value",
            "MY_OUTPUT_VARIABLE should be found",
        )
        self.assertTrue(
            config.get(self.request_id, "MY_OUTPUT_VARIABLE2", "")
            == "my output variable value2",
            "MY_OUTPUT_VARIABLE2 should be found",
        )
        self.assertTrue(
            config.get(self.request_id, "MY_OUTPUT_VARIABLE_REPLACED", "")
            == "HAS_BEEN_REPLACED",
            "MY_OUTPUT_VARIABLE_REPLACED has not been replaced",
        )
        self.assertTrue(
            config.get(self.request_id, "MY_OUTPUT_LINTER_VARIABLE", "")
            == "my output linter variable value",
            "MY_OUTPUT_LINTER_VARIABLE should be found",
        )
        self.assertTrue(
            config.get(self.request_id, "MY_OUTPUT_LINTER_VARIABLE2", "")
            == "my output linter variable value2",
            "MY_OUTPUT_LINTER_VARIABLE2 should be found",
        )
        config.SKIP_DELETE_CONFIG = False
        config.delete(self.request_id)
