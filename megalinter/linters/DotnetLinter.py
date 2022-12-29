#!/usr/bin/env python3
"""
Class for all linters using dotnet tools
"""

from megalinter import Linter


class DotnetLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = ["dotnet"] + super().build_lint_command(file)
        return cmd

    def build_version_command(self):
        cmd = ["dotnet"] + super().build_version_command()
        return cmd

    def build_help_command(self):
        cmd = ["dotnet"] + super().build_help_command()
        return cmd
