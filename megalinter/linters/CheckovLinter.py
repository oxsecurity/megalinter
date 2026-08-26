#!/usr/bin/env python3
"""
Use Checkov to lint Infrastructure as Code
"""

import logging
import os
import re

import megalinter.utils as utils
from megalinter import Linter, config


class CheckovLinter(Linter):
    # MegaLinter linters fully dedicated to secrets detection. When at least
    # one of them is active in the same run, checkov's default behavior of
    # running every framework (including "secrets") only duplicates their
    # work, and its secrets framework can stall for hours spawning long-lived
    # "git cat-file --batch-check" subprocesses on bind-mounted workspaces
    # (seen on Windows -> WSL2 Docker mounts). REPOSITORY_GITLEAKS is not
    # listed because it was removed in MegaLinter v10 (betterleaks replaces
    # it and reads the same configuration files).
    DEDICATED_SECRET_SCANNERS = [
        "REPOSITORY_BETTERLEAKS",
        "REPOSITORY_KINGFISHER",
        "REPOSITORY_SECRETLINT",
        "REPOSITORY_TRUFFLEHOG",
    ]

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

    # In project lint mode, checkov scans the whole workspace by itself. During a
    # pull request run with VALIDATE_ALL_CODEBASE=false, restrict the scan to the
    # files updated in the pull request. In file and list_of_files lint modes,
    # MegaLinter already sends only the updated files to checkov.
    def is_pr_diff_scan(self) -> bool:
        return (
            self.cli_lint_mode == "project"
            and config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
            and utils.is_pr()
        )

    # Files updated in the pull request. Defensive on purpose: master can be
    # absent when the linter is run standalone or instantiated in unit tests
    def get_pr_diff_files(self) -> list:
        master = getattr(self, "master", None)
        return getattr(master, "all_diff_files", None) or []

    def collect_files(self, all_files):
        super().collect_files(all_files)
        # No file updated in the pull request means there is nothing for checkov
        # to scan: skip it, instead of scanning the whole project (which the user
        # opted out of with VALIDATE_ALL_CODEBASE=false)
        if self.is_pr_diff_scan() and len(self.get_pr_diff_files()) == 0:
            logging.info(
                "[Checkov] Skipped, as no file has been updated in the pull request"
            )
            self.is_active = False

    def build_lint_command(self, file=None) -> list:
        if self.is_pr_diff_scan():
            diff_files = self.get_pr_diff_files()
            # Never append --file without any value: checkov would fail on its
            # own arguments ("expected at least one argument") instead of linting
            if len(diff_files) > 0 and "--file" not in self.cli_lint_extra_args_after:
                self.cli_lint_extra_args_after.append("--file")
                self.cli_lint_extra_args_after += diff_files

        cmd = super().build_lint_command(file)

        # Delegate secrets scanning to the dedicated secret scanners active in
        # the same run. Applied in every cli_lint_mode (project, file and
        # list_of_files): the duplication with dedicated secret scanners does
        # not depend on how the linted paths are passed to checkov. Never
        # applied when the user expressed an explicit framework intent, either
        # in REPOSITORY_CHECKOV_ARGUMENTS or in the checkov config file.
        # Appended to the local cmd only (not to self.cli_lint_* attributes) so
        # repeated build_lint_command calls do not accumulate the arguments
        if not any(
            str(arg).startswith(("--framework", "--skip-framework")) for arg in cmd
        ):
            active_secret_scanners = self.get_active_secret_scanner_names()
            if (
                len(active_secret_scanners) > 0
                and self.config_file_defines_frameworks() is False
            ):
                cmd += ["--skip-framework", "secrets"]
                # build_lint_command runs once per file in file lint mode:
                # log the delegation notice only once per linter run
                if getattr(self, "skip_secrets_framework_logged", False) is False:
                    logging.info(
                        "[Checkov] Adding '--skip-framework secrets' to the checkov "
                        "command, as secrets scanning is delegated to "
                        f"{', '.join(active_secret_scanners)}. Define --framework or "
                        "--skip-framework in REPOSITORY_CHECKOV_ARGUMENTS to override "
                        "this behavior."
                    )
                    self.skip_secrets_framework_logged = True
        return cmd

    # Names of the dedicated secret scanners active in the current run.
    # Defensive on purpose: master or active_linters can be absent when the
    # linter is run standalone or instantiated directly in unit tests
    def get_active_secret_scanner_names(self) -> list:
        master = getattr(self, "master", None)
        active_linters = getattr(master, "active_linters", None) or []
        return [
            linter.name
            for linter in active_linters
            if getattr(linter, "name", None) in self.DEDICATED_SECRET_SCANNERS
        ]

    # True if the checkov config file in use already defines framework or
    # skip-framework: the user's framework selection must always win
    def config_file_defines_frameworks(self) -> bool:
        checkov_config_file = getattr(self, "final_config_file", None) or getattr(
            self, "config_file", None
        )
        if checkov_config_file is None:
            return False
        try:
            with open(checkov_config_file, "r", encoding="utf-8") as file_handler:
                checkov_config_text = file_handler.read()
        except OSError as e:
            # Fail open: if the config file can not be read, keep the
            # automatic skip and let checkov report the config issue itself
            logging.debug(
                f"[Checkov] Unable to read config file {checkov_config_file}: {str(e)}"
            )
            return False
        return (
            re.search(
                r"^\s*(framework|skip-framework)\s*:", checkov_config_text, re.MULTILINE
            )
            is not None
        )

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_CHECKOV_FILE_EXTENSIONS", [".tf"]
            )
