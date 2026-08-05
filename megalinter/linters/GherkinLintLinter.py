#!/usr/bin/env python3
"""
Use gherkin-lint to check Gherkin files
"""

import os

from megalinter import Linter, utils


class GherkinLintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: gherkin-lint --ignore
        # overrides the .gherkin-lintignore file, so merge its patterns in
        if self.cli_lint_mode == "project" and not any(
            arg in ("-i", "--ignore") for arg in cmd
        ):
            patterns = []
            workspace_ignore = os.path.join(self.workspace, ".gherkin-lintignore")
            if os.path.isfile(workspace_ignore):
                with open(workspace_ignore, encoding="utf-8") as ignore_file:
                    patterns = [
                        line.strip() for line in ignore_file if line.strip() != ""
                    ]
            for excluded_dir in sorted(utils.get_excluded_directories(self.request_id)):
                pattern = f"**/{excluded_dir}/**"
                if pattern not in patterns:
                    patterns += [pattern]
            cmd += ["--ignore", ",".join(patterns)]

        return cmd
