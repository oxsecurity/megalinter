#!/usr/bin/env python3
"""
Use SqlFluff to lint any type of file according to local config
"""

import logging

from megalinter import Linter


class SqlFluffLinter(Linter):

    # Manage case when we want to add --show-lint-violations when fix mode is active
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        # if fix arg is in the arguments, add --show-lint-violations just after
        if (
            self.apply_fixes is True
            and self.cli_lint_fix_arg_name is not None
            and self.cli_lint_fix_arg_name in cmd
        ):
            fix_index = cmd.index(self.cli_lint_fix_arg_name)
            cmd = (
                cmd[: fix_index + 1]
                + ["--show-lint-violations"]
                + cmd[fix_index + 1 :]  # noqa: E203
            )
            logging.debug("[SqlFluffLinter] Added --show-lint-violations argument")
        return cmd
