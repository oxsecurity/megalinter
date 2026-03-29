#!/usr/bin/env python3
"""
Use Standard to lint js files
https://github.com/standard/standard
"""

from megalinter import Linter, utilstest


class JavaScriptStandardLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if self.cli_lint_mode == "project":
            self.cli_lint_extra_args_after.append(".")
        
        return super().build_lint_command(file)

    def pre_test(self, test_name):
        utilstest.write_eslintignore()

    def post_test(self, test_name):
        utilstest.delete_eslintignore()
