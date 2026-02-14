#!/usr/bin/env python3
"""
Use cljstyle to lint clojure files
"""

from megalinter import Linter


class CljStyleLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if self.cli_lint_mode == "project":
            self.cli_lint_extra_args_after.append(".")
        
        return super().build_lint_command(file)