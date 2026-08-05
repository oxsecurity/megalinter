#!/usr/bin/env python3
"""
Use markdownlint to check Markdown files
"""

from megalinter import Linter


class MarkdownlintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode through a generated
        # ignore file: -p replaces the default .markdownlintignore, so merge it
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not any(arg in ("-p", "--ignore-path") for arg in cmd)
        ):
            cmd += [
                "--ignore-path",
                self.build_project_exclude_ignore_file(
                    "markdownlint-ignore-paths.txt",
                    seed_file_name=".markdownlintignore",
                ),
            ]

        return cmd
