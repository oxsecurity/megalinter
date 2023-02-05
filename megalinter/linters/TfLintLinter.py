#!/usr/bin/env python3
"""
Use TfLint to lint terraform files
https://github.com/terraform-linters/tflint
"""
import logging

import megalinter


class TfLintLinter(megalinter.Linter):
    # To execute before linting files
    def before_lint_files(self):
        # Build pre-command
        tflint_init_command = "tflint --init"
        if self.config_file is not None:
            tflint_init_command += f" --config {self.config_file}"
        logging.debug("tflint before_lint_files: " + tflint_init_command)
        # Add to pre-commands
        tflint_pre_command = {"command": tflint_init_command, "cwd": self.workspace}
        if self.pre_commands is None:
            self.pre_commands = []
        self.pre_commands.append(tflint_pre_command)
