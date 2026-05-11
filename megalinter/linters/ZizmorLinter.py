#!/usr/bin/env python3
"""
Use zizmor to lint GitHub Actions files
https://zizmor.sh/
"""

import megalinter
from megalinter import config


class ZizmorLinter(megalinter.Linter):
    def execute_lint_command(self, command):
        return_code, return_stdout = super().execute_lint_command(command)
        if return_code != 0 and "accessing GitHub API" in return_stdout:
            return_stdout += (
                "\n\n[ZizmorLinter] Zizmor failed to reach the GitHub API.\n"
                "To allow zizmor to use GITHUB_TOKEN, add the following to your .mega-linter.yml:\n"
                "ACTION_ZIZMOR_UNSECURED_ENV_VARIABLES:\n"
                "  - GITHUB_TOKEN\n"
            )
        return return_code, return_stdout

    def pre_test(self, test_name):
        config.set_value(
            self.request_id, "ACTION_ZIZMOR_UNSECURED_ENV_VARIABLES", "GITHUB_TOKEN"
        )
