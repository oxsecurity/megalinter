#!/usr/bin/env python3
"""
Use Checkov to lint Infrastructure as Code
"""

import megalinter.utils as utils

from megalinter import Linter, config


class CheckovLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if (
            config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
            and utils.is_pr()
        ):
            self.cli_lint_extra_args_after.append("--file")

            for file_to_lint in self.files:
                self.cli_lint_extra_args_after.append(file_to_lint)
        else:
            if self.cli_lint_mode == "file" or self.cli_lint_mode == "list_of_files":
                self.cli_lint_extra_args_after.append("--file")
            else:
                self.cli_lint_extra_args_after.append("--directory")
                self.cli_lint_extra_args_after.append(".")

        return super().build_lint_command(file)

    def pre_test(self, test_name):
        config.set_value(
            self.request_id, "REPOSITORY_CHECKOV_FILE_NAMES_REGEX", ["Dockerfile"]
        )
        config.set_value(
            self.request_id, "REPOSITORY_CHECKOV_FILE_EXTENSIONS", [".tf"]
        )
