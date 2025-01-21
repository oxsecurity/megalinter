#!/usr/bin/env python3
"""
Use dotnet-format to lint CSharp files
"""

from megalinter import Linter


class DotnetFormatLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        # cli_lint_mode = list_of_files or project
        dotnet_format_command = " ".join(super().build_lint_command(None))
        commands = [
            dotnet_format_command + " | tee /dev/tty2 2>&1",
            'exit "${PIPESTATUS[0]}"',
        ]
        return " && ".join(commands)
