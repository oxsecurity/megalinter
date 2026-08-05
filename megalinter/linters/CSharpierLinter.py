#!/usr/bin/env python3
"""
Use CSharpier to check C# code formatting
"""

import os

from megalinter import Linter


class CSharpierLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: csharpier has no exclusion
        # argument, but --ignore-path can point to a generated ignore file.
        # Merge the workspace .csharpierignore since --ignore-path relocates it
        if self.cli_lint_mode == "project" and not any(
            arg == "--ignore-path" or arg.startswith("--ignore-path=") for arg in cmd
        ):
            seed_lines = []
            workspace_ignore = os.path.join(self.workspace, ".csharpierignore")
            if os.path.isfile(workspace_ignore):
                with open(workspace_ignore, encoding="utf-8") as ignore_file:
                    seed_lines = [
                        line.rstrip("\n") for line in ignore_file if line.strip() != ""
                    ]
            cmd += [
                "--ignore-path",
                self.build_project_exclude_ignore_file(
                    "csharpier-ignore-paths.txt", seed_lines=seed_lines
                ),
            ]

        return cmd
