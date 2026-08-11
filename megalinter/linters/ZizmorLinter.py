#!/usr/bin/env python3
"""
Use zizmor to lint GitHub Actions files
https://zizmor.sh/
"""

import os

import megalinter
from megalinter import config


class ZizmorLinter(megalinter.Linter):
    def pre_test(self, test_name):
        config.set_value(
            self.request_id, "ACTION_ZIZMOR_UNSECURED_ENV_VARIABLES", "GITHUB_TOKEN"
        )

    def execute_lint_command(self, command):
        return_code, return_output = super().execute_lint_command(command)
        # --format=sarif always exits 0 regardless of findings (unless zizmor
        # itself errors), which would otherwise skip MegaLinter's error
        # counting: it's gated on a non-zero return code. Recover a
        # findings-reflecting return code from the SARIF results just written
        if (
            return_code == 0
            and self.can_output_sarif is True
            and self.output_sarif is True
            and self.sarif_output_file is not None
            and os.path.isfile(self.sarif_output_file)
            and (
                self.get_sarif_result_count(return_output, "error") > 0
                or self.get_sarif_result_count(return_output, "warning") > 0
            )
        ):
            return_code = 1
        return return_code, return_output
