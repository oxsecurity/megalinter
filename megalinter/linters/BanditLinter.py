#!/usr/bin/env python3
"""
Use bandit to check for security issues in Python code
"""

from megalinter import Linter, utils

# bandit -x replaces its built-in exclusion list, so it must be re-included
BANDIT_DEFAULT_EXCLUDED_PATHS = [
    ".svn",
    "CVS",
    ".bzr",
    ".hg",
    ".git",
    "__pycache__",
    ".tox",
    ".eggs",
    "*.egg",
]


class BanditLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if self.cli_lint_mode == "project" and not any(
            arg in ("-x", "--exclude") for arg in cmd
        ):
            excluded_paths = list(BANDIT_DEFAULT_EXCLUDED_PATHS)
            for excluded_dir in sorted(utils.get_excluded_directories(self.request_id)):
                if excluded_dir not in excluded_paths:
                    excluded_paths += [excluded_dir]
            cmd += ["-x", ",".join(excluded_paths)]

        return cmd
