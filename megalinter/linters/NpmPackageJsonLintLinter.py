#!/usr/bin/env python3
"""
Use npm-package-json-lint to check package.json files
"""

import os

from megalinter import Linter


class NpmPackageJsonLintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: npm-package-json-lint has
        # no exclusion argument, but --ignorePath can point to a generated ignore
        # file. Merge the workspace .npmpackagejsonlintignore it would replace
        if self.cli_lint_mode == "project" and "--ignorePath" not in cmd:
            seed_lines = []
            workspace_ignore = os.path.join(
                self.workspace, ".npmpackagejsonlintignore"
            )
            if os.path.isfile(workspace_ignore):
                with open(workspace_ignore, encoding="utf-8") as ignore_file:
                    seed_lines = [
                        line.rstrip("\n") for line in ignore_file if line.strip() != ""
                    ]
            cmd += [
                "--ignorePath",
                self.build_project_exclude_ignore_file(
                    "npm-package-json-lint-ignore-paths.txt", seed_lines=seed_lines
                ),
            ]

        return cmd
