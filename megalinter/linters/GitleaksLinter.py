#!/usr/bin/env python3
"""
Use GitLeaks to check for credentials in repository
"""

from megalinter import Linter
from megalinter.utils import is_git_repo


class GitleaksLinter(Linter):

    # Manage case when we want semgrep rulesets to be selected related to security
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        if '--no-git' in cmd and is_git_repo(self.workspace):
            cmd.remove("--no-git")
        return cmd

