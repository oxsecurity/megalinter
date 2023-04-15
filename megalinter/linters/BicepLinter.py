#!/usr/bin/env python3
"""
Use Bicep to lint bicep files
"""
import os

from megalinter import Linter


class BicepLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        os.environ["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"

        cmd = super().build_lint_command(file)

        return cmd
