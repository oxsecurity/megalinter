#!/usr/bin/env python3
"""
Class for lychee
"""

from megalinter import Linter


# ref: https://github.com/lycheeverse/lychee#commandline-parameters
class LycheeLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # `--no-progress` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--no-progress" in self.cli_lint_user_args:
            cmd.pop(cmd.index("--no-progress"))

        # `-n` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "-n" in self.cli_lint_user_args:
            cmd.pop(cmd.index("-n"))

        # `--format <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--format" in self.cli_lint_user_args:
            cmd.pop(cmd.index("--format") + 1)
            cmd.pop(cmd.index("--format"))

        # `-f <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "-f" in self.cli_lint_user_args:
            cmd.pop(cmd.index("-f") + 1)
            cmd.pop(cmd.index("-f"))

        # `--output <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--output" in self.cli_lint_user_args:
            cmd.pop(cmd.index("--output") + 1)
            cmd.pop(cmd.index("--output"))

        # `--output <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "-o" in self.cli_lint_user_args:
            cmd.pop(cmd.index("-o") + 1)
            cmd.pop(cmd.index("-o"))

        if self.cli_lint_mode == "project":
            cmd.append(".")

        return cmd
