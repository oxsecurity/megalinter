#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest
import uuid

from megalinter import utilstest


class mega_linter_4_dependencies_test(unittest.TestCase):
    def before_start(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {
                "request_id": self.request_id,
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}dependencies",
            }
        )

    def test_override_cli_executable(self):
        self.before_start()
        mega_linter, output = utilstest.call_mega_linter(
            {
                "APPLY_FIXES": "all",
                "ENABLE_LINTERS": "TYPESCRIPT_ES",
                "TYPESCRIPT_ES_CLI_EXECUTABLE": ["yarn", "run", "eslint"],
                "PRINT_ALL_FILES": "false",
                "MEGALINTER_FLAVOR": "javascript",
                "FLAVOR_SUGGESTIONS": "false",
                "request_id": self.request_id,
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("- Number of files analyzed", output)

    # def test_override_cli_executable_with_pre_commands(self):
    #     mega_linter, output = utilstest.call_mega_linter(
    #         {
    #             "ENABLE_LINTERS": "TYPESCRIPT_ES",
    #             "TYPESCRIPT_ES_CLI_EXECUTABLE": ["yarn", "run", "eslint"],
    #             "PRINT_ALL_FILES": "false",
    #             "MEGALINTER_FLAVOR": "javascript",
    #             "FLAVOR_SUGGESTIONS": "false",
    #             "TYPESCRIPT_ES_PRE_COMMANDS": [
    #                 {
    #                     "command": "npm install @tsconfig/node18-strictest-esm@1.0.1",
    #                     "continue_if_failed": False,
    #                     "cwd": "workspace",
    #                 }
    #             ],
    #             "request_id": self.request_id,
    #         }
    #     )
    #     self.assertTrue(
    #         len(mega_linter.linters) > 0, "Linters have been created and run"
    #     )
    #     self.assertIn("- Number of files analyzed", output)
