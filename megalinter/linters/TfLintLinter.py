#!/usr/bin/env python3
"""
Use TfLint to lint terraform files
https://github.com/terraform-linters/tflint
"""
import logging

import megalinter
from megalinter import config


class TfLintLinter(megalinter.Linter):
    # To execute before linting files
    def before_lint_files(self):
        # Build pre-command
        tflint_init_command = "tflint --init"
        if self.config_file is not None:
            tflint_init_command += f" --config {self.config_file}"
        logging.debug("tflint before_lint_files: " + tflint_init_command)
        # Add to pre-commands
        tflint_secured_env = (
            False
            if config.get(self.request_id, "TERRAFORM_TFLINT_SECURED_ENV", "true")
            == "false"
            else True
        )
        tflint_pre_command = {
            "command": tflint_init_command,
            "cwd": self.workspace,
            "secured_env": tflint_secured_env,
        }
        if self.pre_commands is None:
            self.pre_commands = []
        self.pre_commands.append(tflint_pre_command)

    def pre_test(self):
        config.set_value(
            self.request_id, "TERRAFORM_TFLINT_UNSECURED_ENV_VARIABLES", "GITHUB_TOKEN"
        )
