#!/usr/bin/env python3
"""
Use Prettier to check code formatting
"""

import os

from megalinter import Linter


class PrettierLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: prettier has no exclusion
        # argument, but accepts extra ignore files. Passing --ignore-path disables
        # the default .gitignore/.prettierignore discovery, so re-add them
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not any(
                arg == "--ignore-path" or arg.startswith("--ignore-path=")
                for arg in cmd
            )
        ):
            for default_ignore_file in [".gitignore", ".prettierignore"]:
                default_ignore_path = os.path.join(self.workspace, default_ignore_file)
                if os.path.isfile(default_ignore_path):
                    cmd += ["--ignore-path", default_ignore_path]
            cmd += [
                "--ignore-path",
                self.build_project_exclude_ignore_file("prettier-ignore-paths.txt"),
            ]

        return cmd
