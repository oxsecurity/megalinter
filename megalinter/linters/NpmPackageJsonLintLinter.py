#!/usr/bin/env python3
"""
Use npm-package-json-lint to check package.json files
"""

from megalinter import Linter


class NpmPackageJsonLintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: npm-package-json-lint has
        # no exclusion argument, but --ignorePath can point to a generated ignore
        # file. Merge the workspace .npmpackagejsonlintignore it would replace
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and "--ignorePath" not in cmd
        ):
            cmd += [
                "--ignorePath",
                self.build_project_exclude_ignore_file(
                    "npm-package-json-lint-ignore-paths.txt",
                    seed_file_name=".npmpackagejsonlintignore",
                ),
            ]

        return cmd
