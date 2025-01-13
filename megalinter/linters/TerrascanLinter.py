#!/usr/bin/env python3
"""
Use TerrascanLinter to lint tf files
"""

from megalinter import Linter


class TerrascanLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if self.cli_lint_mode == "file":
            cmd += ["--iac-file", f"{file}"]
            
        return cmd
