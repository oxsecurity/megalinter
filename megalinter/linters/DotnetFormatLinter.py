#!/usr/bin/env python3
"""
Use dotnet-format to lint CSharp files
"""

import os.path

from megalinter import Linter


class DotnetFormatLinter(Linter):

    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        if file is not None:
            # cli_lint_mode = file
            file = os.path.basename(file)
            dotnet_format_command = " ".join(super().build_lint_command(file))
            commands = [
                f'cd "{os.path.realpath(os.path.dirname(file))}" || exit 1',
                dotnet_format_command + " | tee /dev/tty2 2>&1",
                'exit "${PIPESTATUS[0]}"',
            ]

        else:
            # cli_lint_mode = list_of_files or project
            dotnet_format_command = " ".join(super().build_lint_command(None))
            commands = [
                dotnet_format_command + " | tee /dev/tty2 2>&1",
                'exit "${PIPESTATUS[0]}"',
            ]
        return " && ".join(commands)
