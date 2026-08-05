#!/usr/bin/env python3
"""
Use coffeelint to check CoffeeScript files
"""

import os

from megalinter import Linter


class CoffeelintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: coffeelint only reads a
        # .coffeelintignore discovered in the working directory, so one is
        # temporarily written at the workspace root when the repository has
        # none (removed after the run)
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not os.path.isfile(os.path.join(self.workspace, ".coffeelintignore"))
        ):
            self.write_workspace_generated_file(
                ".coffeelintignore",
                [
                    f"{excluded_dir}/"
                    for excluded_dir in self.get_project_exclude_directories()
                ],
            )

        return cmd

    def execute_lint_command(self, command):
        try:
            return super().execute_lint_command(command)
        finally:
            self.cleanup_workspace_generated_files()
