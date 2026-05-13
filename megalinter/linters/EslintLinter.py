#!/usr/bin/env python3
"""
Use Eslint to check so many file formats :)
"""

from megalinter import Linter


class EslintLinter(Linter):
    # Drop ESLint v8-only flags that v9 removed.
    # Keep --no-ignore stripping when an explicit ignore source is present.
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        cmd = [arg for arg in cmd if arg not in ("--no-eslintrc",)]
        if "--ignore-path" in cmd or "--ignore-pattern" in cmd:
            cmd = list(filter(lambda a: a != "--no-ignore", cmd))
        if self.cli_lint_mode == "project":
            cmd.append(".")
        return cmd
