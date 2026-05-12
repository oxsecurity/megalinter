#!/usr/bin/env python3
"""
Use Kics to lint Infrastructure as Code
"""

from megalinter import Linter, config


class KicsLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if self.cli_lint_mode == "list_of_files":
            self.files_separator = ","

        return super().build_lint_command(file)

    def pre_test(self, test_name):
        if test_name.endswith("file_lint_mode") or test_name.endswith("list_of_files_lint_mode"):
            config.set_value(self.request_id, "REPOSITORY_KICS_FILE_EXTENSIONS", [".tf", ".yml"])
