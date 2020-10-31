#!/usr/bin/env python3
"""
Use black to lint/format python files
https://github.com/psf/black
"""

from megalinter import Linter


class PythonBlackLinter(Linter):

    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        if self.try_fix is True:
            cmd.remove('--diff')
            cmd.remove('--check')
            cmd.remove('--megalinter-fix-flag')
        return cmd
