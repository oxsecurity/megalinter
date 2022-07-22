#!/usr/bin/env python3
"""
Use GitLeaks to check for credentials in repository
"""

from megalinter import Linter
from megalinter.utils import is_git_repo


class GitleaksLinter(Linter):

    # Manage presence of --no-git in command line
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        # --no-git has been sent by user in REPOSITORY_GITLEAKS_ARGUMENTS
        # make sure that it is only once in the arguments list
        if "--no-git" in self.cli_lint_user_args:
            cmd = list(dict.fromkeys(cmd))
        # --no-git has been sent by default from ML descriptor
        # but as it is a git repo, remove all --no-git from arguments list
        elif "--no-git" in cmd and is_git_repo(self.workspace):
            cmd = list(filter(lambda a: a != "--no-git", cmd))
        return cmd
