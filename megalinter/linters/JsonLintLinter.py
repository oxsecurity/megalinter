#!/usr/bin/env python3
"""
Use jsonlint to lint json files
"""

from megalinter import Linter


class JsonLintLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if self.cli_lint_mode == "project":
            self.cli_lint_extra_args_after.append(self.workspace)
        
        return super().build_lint_command(file)
