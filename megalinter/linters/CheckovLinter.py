#!/usr/bin/env python3
"""
Use Checkov to lint Infrastructure as Code
"""

import os

import megalinter.utils as utils
from megalinter import Linter, config


class CheckovLinter(Linter):
    def before_lint_files(self):
        # Redirect Checkov's transient github_conf/ out of the linted tree to
        # avoid an ansible-lint race condition (issue #8092). Prefer a hidden
        # subfolder of the MegaLinter report folder: it is gitignored,
        # auto-created and excluded from file discovery, while the leading dot
        # keeps project-mode linters (which walk the tree themselves) from
        # descending into it. Checkov joins CKV_GITHUB_CONF_DIR_NAME with the
        # current working directory, so an absolute path lands there verbatim.
        # Fall back to a hidden dir at the workspace root when reports are off.
        if self._cached_subprocess_env is not None:
            if self.report_folder not in ("", "none", "false"):
                github_conf_dir = os.path.abspath(
                    os.path.join(self.report_folder, ".checkov-github-conf")
                )
            else:
                github_conf_dir = ".megalinter_github_conf"
            self._cached_subprocess_env["CKV_GITHUB_CONF_DIR_NAME"] = github_conf_dir

    def build_lint_command(self, file=None) -> list:
        if (
            config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
            and utils.is_pr()
        ):
            if "--file" not in self.cli_lint_extra_args_after:
                self.cli_lint_extra_args_after.append("--file")
                for file_to_lint in self.master.all_diff_files:
                    self.cli_lint_extra_args_after.append(file_to_lint)

        return super().build_lint_command(file)

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_CHECKOV_FILE_EXTENSIONS", [".tf"]
            )
