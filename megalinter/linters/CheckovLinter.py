#!/usr/bin/env python3
"""
Use Checkov to lint Infrastructure as Code
"""

import megalinter.utils as utils
from megalinter import Linter, config


class CheckovLinter(Linter):
    def before_lint_files(self):
        # Redirect Checkov's transient github_conf/ to a hidden dir to prevent ansible-lint race condition (issue #8092)
        if self._cached_subprocess_env is not None:
            self._cached_subprocess_env["CKV_GITHUB_CONF_DIR_NAME"] = (
                ".megalinter_github_conf"
            )

    def build_lint_command(self, file=None) -> list:
        if (
            config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
            and utils.is_pr()
        ):
            if "--file" not in self.cli_lint_extra_args_after:
                self.cli_lint_extra_args_after.append("--file")
                for file_to_lint in self.master.all_diff_files:
                    self.cli_lint_extra_args_after.append(file_to_lint)
        else:
            if (
                self.cli_lint_mode == "file"
                and "--file" not in self.cli_lint_extra_args_after
            ) or self.cli_lint_mode == "list_of_files":
                self.cli_lint_extra_args_after.append("--file")
            elif (
                self.cli_lint_mode == "project"
                and "--directory" not in self.cli_lint_extra_args_after
            ):
                self.cli_lint_extra_args_after.append("--directory")
                self.cli_lint_extra_args_after.append(".")

        return super().build_lint_command(file)

    def pre_test(self, test_name):
        config.set_value(
            self.request_id, "REPOSITORY_CHECKOV_FILE_NAMES_REGEX", ["Dockerfile"]
        )
        config.set_value(self.request_id, "REPOSITORY_CHECKOV_FILE_EXTENSIONS", [".tf"])
