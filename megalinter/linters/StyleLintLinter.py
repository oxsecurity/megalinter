#!/usr/bin/env python3
"""
Use StyleLint to lint css, scss and saas files
"""

from megalinter import Linter, config


class StyleLintLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if self.cli_lint_mode == "project":
            self.cli_lint_extra_args_after.append(f"**/*.{{{self.file_extensions.join(",").replace(".", "")}}}")
        
        return super().build_lint_command(file)

    def pre_test(self, test_name):
        if test_name.startsWith("test_failure"):
            config.set_value(
                self.request_id, "CSS_STYLELINT_CONFIG_FILE", ".stylelintrc_bad.json"
            )
