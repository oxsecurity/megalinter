#!/usr/bin/env python3
"""
Use Checkov to lint Infrastructure as Code
"""

import megalinter.utils as utils

from megalinter import Linter, config


class CheckovLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        cmd = super().build_lint_command(file)

        if (
            config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
            and utils.is_pr()
        ):
            for file_path in self.files:
                cmd.append("--file")
                cmd.append(file_path)
        else:
            if self.cli_lint_mode == "file":
                cmd.append("--file")
                cmd.append(file)
            elif self.cli_lint_mode == "list_of_files":
                for file_path in self.files:
                    cmd.append("--file")
                    cmd.append(file_path)
            if self.cli_lint_mode == "project":
                cmd.append("--directory")
                cmd.append(".")

        return cmd
