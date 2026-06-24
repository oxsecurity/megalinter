#!/usr/bin/env python3
"""
Use BetterLeaks to check for credentials in repository
"""

import json
import os

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
