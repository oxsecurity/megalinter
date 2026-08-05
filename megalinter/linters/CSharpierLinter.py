#!/usr/bin/env python3
"""
Use CSharpier to check C# code formatting
"""

from megalinter import Linter


class CSharpierLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: csharpier has no exclusion
        # argument, but --ignore-path can point to a generated ignore file.
        # Merge the workspace .csharpierignore since --ignore-path relocates it
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not any(
                arg == "--ignore-path" or arg.startswith("--ignore-path=")
                for arg in cmd
            )
        ):
            cmd += [
                "--ignore-path",
                self.build_project_exclude_ignore_file(
                    "csharpier-ignore-paths.txt", seed_file_name=".csharpierignore"
                ),
            ]

        return cmd
