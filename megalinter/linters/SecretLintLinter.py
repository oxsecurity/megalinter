#!/usr/bin/env python3
"""
Use secretlint to find secrets in sources
https://github.com/secretlint/secretlint
"""

import os

from megalinter import Linter, config


class SecretLintLinter(Linter):
    # Called before linting files
    def get_ignore_arguments(self, cmd):
        ignore_args = super().get_ignore_arguments(cmd)
        # Use .gitignore as .secretlintignore
        # only if --secretlintignore is not defined and .secretlintignore not found
        if (
            len(ignore_args) == 0
            and "--secretlintignore" not in self.cli_lint_user_args
            and (
                os.path.isfile(os.path.join(self.workspace, ".gitignore"))
                and (
                    not os.path.isfile(
                        os.path.join(self.workspace, ".secretlintignore")
                    )
                )
            )
        ):
            ignore_args = ["--secretlintignore", ".gitignore"]
        return ignore_args

    def pre_test(self, test_name):
        if test_name.endswith("file_lint_mode") or test_name.endswith("list_of_files_lint_mode"):
            config.set_value(self.request_id, "REPOSITORY_SECRETLINT_FILE_EXTENSIONS", [".ini"])
