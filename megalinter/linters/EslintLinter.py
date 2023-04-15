#!/usr/bin/env python3
"""
Use Eslint to check so many file formats :)
"""

from megalinter import Linter


class EslintLinter(Linter):
    # Remove --no-ignore if there are arguments about ignoring stuff
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        if "--ignore-path" in cmd or "--ignore-pattern" in cmd:
            cmd = list(filter(lambda a: a != "--no-ignore", cmd))
        if self.cli_lint_mode == "project":
            cmd.append(".")
        return cmd
