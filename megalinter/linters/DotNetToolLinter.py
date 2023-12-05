#!/usr/bin/env python3
"""
Use to allow dotnet tools to be used on higher runtime than the one being targeted
"""
import os

from megalinter import Linter


class DotNetToolLinter(Linter):
    def build_lint_command(self, file=None):
        os.environ["DOTNET_ROLL_FORWARD"] = "LatestMajor"

        return super().build_lint_command(file)

    def build_version_command(self):
        os.environ["DOTNET_ROLL_FORWARD"] = "LatestMajor"

        return super().build_version_command()

    def build_help_command(self):
        os.environ["DOTNET_ROLL_FORWARD"] = "LatestMajor"

        return super().build_help_command()
