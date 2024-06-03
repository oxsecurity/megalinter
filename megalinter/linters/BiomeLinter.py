#!/usr/bin/env python3
"""
Class for Biome Linter
"""

from megalinter import Linter


class BiomeLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        if self.cli_lint_mode == "project":
            cmd.append(".")
        return cmd
