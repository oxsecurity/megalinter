#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""

import os
import unittest
import uuid
from types import SimpleNamespace

from megalinter import config, pre_post_factory, utilstest


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
                "MY_INPUT_VARIABLE_REPLACEMENT": "HAS_BEEN_REPLACED",
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
        replaced_val = config.get(self.request_id, "MY_OUTPUT_VARIABLE_REPLACED", "")
        self.assertTrue(
            replaced_val == "HAS_BEEN_REPLACED",
            f"MY_OUTPUT_VARIABLE_REPLACED has not been replaced (value: {replaced_val})",
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


class PrePostReplacementEnvVarsTest(unittest.TestCase):
    def setUp(self):
        if "MEGALINTER_CONFIG" in os.environ:
            del os.environ["MEGALINTER_CONFIG"]

    def build_command_env(self, with_replacement: bool):
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            None,
            {
                "GITHUB_TOKEN": "GITHUB_TOKEN_VALUE",
                "PAT_GITHUB_COM": "PAT_GITHUB_COM_VALUE",
            },
        )
        command_info = {"command": "echo test", "cwd": "root", "secured_env": True}
        if with_replacement is True:
            command_info["replacement_env_vars"] = [
                {"var_dest": "GITHUB_TOKEN", "var_src": "PAT_GITHUB_COM"}
            ]
        mega_linter = SimpleNamespace(request_id=request_id, workspace=os.getcwd())
        command_env = pre_post_factory.build_command_env(command_info, mega_linter)
        config.delete(request_id)
        return command_env

    def test_secured_env_vars_are_hidden_from_commands(self):
        command_env = self.build_command_env(False)
        self.assertEqual(
            command_env["GITHUB_TOKEN"],
            "HIDDEN_BY_MEGALINTER",
            "GITHUB_TOKEN is not visible",
        )
        self.assertEqual(
            command_env["PAT_GITHUB_COM"],
            "HIDDEN_BY_MEGALINTER",
            "PAT_GITHUB_COM is not visible",
        )

    def test_replacement_env_vars_use_raw_config_value(self):
        command_env = self.build_command_env(True)
        self.assertEqual(
            command_env["GITHUB_TOKEN"],
            "PAT_GITHUB_COM_VALUE",
            "GITHUB_TOKEN has received the value of PAT_GITHUB_COM",
        )
        self.assertEqual(
            command_env["PAT_GITHUB_COM"],
            "HIDDEN_BY_MEGALINTER",
            "PAT_GITHUB_COM is not visible",
        )
