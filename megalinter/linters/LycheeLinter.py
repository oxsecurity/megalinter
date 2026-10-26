#!/usr/bin/env python3
"""
Class for lychee
"""

import os

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

        cmd += self.build_ignore_file_exclude_arguments()

        return cmd

    # Lychee only reads .lycheeignore from its working directory and has no CLI
    # option to pass another location: forward the resolved file as --exclude
    def build_ignore_file_exclude_arguments(self):
        if self.ignore_file is None or not os.path.isfile(self.ignore_file):
            return []
        # Lint commands run in the workspace, where lychee finds it by itself
        if os.path.abspath(self.ignore_file) == os.path.abspath(
            os.path.join(self.workspace, ".lycheeignore")
        ):
            return []
        exclude_args = []
        with open(self.ignore_file, encoding="utf-8", errors="ignore") as file:
            for line in file.read().splitlines():
                line = line.strip()
                if line != "" and not line.startswith("#"):
                    exclude_args.append("--exclude=" + line)
        return exclude_args
