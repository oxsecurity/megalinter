#!/usr/bin/env python3
"""
Use BetterLeaks to check for credentials in repository
"""

import json
import os
import re

import megalinter.utils as utils
from megalinter import Linter, config


class BetterleaksLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super().__init__(params, linter_config)
        if self.is_active is False:
            return
        self.pr_commits_scan = config.get(
            self.request_id, "REPOSITORY_BETTERLEAKS_PR_COMMITS_SCAN", "false"
        )
        if self.pr_commits_scan == "true" and utils.is_pr():
            self.pr_source_sha, self.pr_target_sha = self.get_pr_data()

    def get_pr_data(self):
        pr_source_sha = config.get(
            self.request_id, "REPOSITORY_BETTERLEAKS_PR_SOURCE_SHA"
        )
        pr_target_sha = config.get(
            self.request_id, "REPOSITORY_BETTERLEAKS_PR_TARGET_SHA"
        )

        if pr_source_sha is None or pr_target_sha is None:
            if utils.is_azure_devops_pr():
                pr_source_sha = config.get(
                    self.request_id, "SYSTEM_PULLREQUEST_SOURCECOMMITID"
                )
                pr_target_sha = self.get_azure_devops_pr_target_sha(
                    config.get(self.request_id, "SYSTEM_PULLREQUEST_TARGETBRANCH")
                )
            elif utils.is_github_pr():
                pr_source_sha, pr_target_sha = self.get_github_sha()
            elif utils.is_gitlab_mr() and utils.is_gitlab_premium():
                pr_source_sha = config.get(
                    self.request_id, "CI_MERGE_REQUEST_SOURCE_BRANCH_SHA"
                )
                pr_target_sha = config.get(
                    self.request_id, "CI_MERGE_REQUEST_TARGET_BRANCH_SHA"
                )
            elif utils.is_gitlab_external_pr() and utils.is_gitlab_premium():
                pr_source_sha = config.get(
                    self.request_id, "CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_SHA"
                )
                pr_target_sha = config.get(
                    self.request_id, "CI_EXTERNAL_PULL_REQUEST_TARGET_BRANCH_SHA"
                )

        return pr_source_sha, pr_target_sha

    def get_azure_devops_pr_target_sha(self, target_branch_name):
        repo = utils.git.Repo(os.path.realpath(self.workspace))
        return repo.commit(target_branch_name.replace("refs/heads", "origin"))

    def get_github_sha(self):
        with open(config.get(self.request_id, "GITHUB_EVENT_PATH")) as gh_event_file:
            gh_event = json.load(gh_event_file)
        return (
            gh_event["pull_request"]["head"]["sha"],
            gh_event["pull_request"]["base"]["sha"],
        )

    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Handle --redact deduplication if user also passed it in ARGUMENTS
        if "--redact" in self.cli_lint_user_args:
            cmd = list(dict.fromkeys(cmd))

        if (
            config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
            and self.pr_commits_scan == "true"
            and utils.is_pr()
        ):
            # Scanning a specific range of PR commits requires git history mode.
            # The default scan stays in filesystem ('dir') mode to avoid betterleaks
            # invoking git on the workspace, which fails with "dubious ownership"
            # because betterleaks does not read the global git safe.directory config.
            if "dir" in cmd:
                cmd[cmd.index("dir")] = "git"

            if (
                self.pr_target_sha is not None
                and self.pr_source_sha is not None
                and self.pr_target_sha != self.pr_source_sha
            ):
                if "--log-opts" in cmd:
                    cmd.pop(cmd.index("--log-opts") + 1)
                    cmd.pop(cmd.index("--log-opts"))

                if any(v.startswith("--log-opts=") for v in cmd):
                    cmd.pop(
                        cmd.index(next(v for v in cmd if v.startswith("--log-opts=")))
                    )

                self.cli_lint_extra_args = [
                    "--log-opts",
                    f"--no-merges --first-parent {self.pr_target_sha}^..{self.pr_source_sha}",
                ]
                cmd += self.cli_lint_extra_args

        return cmd

    # Forward excluded directories in project mode: betterleaks has no exclusion
    # argument, so generate a config extending the resolved one with allowlist
    # path regexes. When MegaLinter resolved no config, extend the workspace
    # config that betterleaks would have auto-discovered (e.g. a .gitleaks.toml
    # kept from gitleaks), and only fall back to the default embedded ruleset
    def manage_excluded_directories_config(self, cmd):
        config_index = self.find_cli_argument_value_index(cmd, ("-c", "--config"))
        extend_path = None
        if config_index is not None:
            extend_path = cmd[config_index].replace("\\", "/")
        else:
            for discoverable_config in [".betterleaks.toml", ".gitleaks.toml"]:
                workspace_config = os.path.join(self.workspace, discoverable_config)
                if os.path.isfile(workspace_config):
                    extend_path = workspace_config.replace("\\", "/")
                    break
        config_lines = ["[extend]"]
        if extend_path is not None:
            config_lines += [f"path = '{extend_path}'"]
        else:
            config_lines += ["useDefault = true"]
        config_lines += ["", "[allowlist]", "paths = ["]
        for excluded_dir in self.get_project_exclude_directories():
            path_regex = re.escape(excluded_dir.replace("\\", "/")) + "/"
            config_lines += [f"    '{path_regex}',"]
        config_lines += ["]"]
        generated_config = self.write_report_generated_file(
            "betterleaks-config.toml", config_lines
        )
        cmd = self.replace_or_append_cli_argument(
            cmd, config_index, "-c", generated_config
        )
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} extending "
            + (extend_path if extend_path is not None else "the default ruleset")
            + " with EXCLUDED_DIRECTORIES as allowlist paths "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_BETTERLEAKS_FILE_EXTENSIONS", [".txt"]
            )
