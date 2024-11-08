#!/usr/bin/env python3
"""
Use lintr to lint R files
https://github.com/r-lib/lintr
"""
from pathlib import Path

from megalinter import Linter


class RLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        # Build command in R format

        r_commands = [
            # Change the working directory to match the file
            f"setwd('{Path(file).parent}')",
        ]

        if self.config_file:
            # Instruct lintr to load an absolute filepath
            r_commands.append(f"options('lintr.linter_file' = '{self.config_file}')")
        else:
            # Instruct lintr to walk up the directory tree
            r_commands.append(f"lintr:::read_settings('{self.config_file_name}')")

        r_commands.extend(
            [
                f"lints <- lintr::lint('{Path(file).name}')",
                "print(lints)",
                "quit(save = 'no', status = if (length(lints) > 0) 1 else 0)",
            ]
        )
        # Build shell command
        cmd = ["R", "--slave", "-e", ";".join(r_commands)]
        return cmd

    # Build the CLI command to request lintr version
    def build_version_command(self):
        # Build command in R format
        r_commands = ['packageVersion("lintr");']
        # Build shell command
        cmd = ["R", "--slave", "-e", "".join(r_commands)]
        return cmd

    # Build the CLI command to request lintr help
    def build_help_command(self):
        # Build command in R format
        r_commands = ['help("lintr");']
        # Build shell command
        cmd = ["R", "--slave", "-e", "".join(r_commands)]
        return cmd
