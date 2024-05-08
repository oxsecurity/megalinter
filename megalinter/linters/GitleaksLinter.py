#!/usr/bin/env python3
"""
Use GitLeaks to check for credentials in repository
"""
import json
import os

import megalinter.utils as utils
from megalinter import Linter, config


class GitleaksLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super().__init__(params, linter_config)
        self.pr_commits_scan = config.get(
            self.request_id, "REPOSITORY_GITLEAKS_PR_COMMITS_SCAN", "false"
        )
        if self.pr_commits_scan == "true" and utils.is_pr():
            self.pr_source_sha, self.pr_target_sha = self.get_pr_data()

    def get_pr_data(self):
        # Azure DevOps ref:
        # https://learn.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml
        # GitHub ref:
        # https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
        # GitLab ref:
        # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html

        pr_source_sha = config.get(self.request_id, "REPOSITORY_GITLEAKS_PR_SOURCE_SHA")
        pr_target_sha = config.get(self.request_id, "REPOSITORY_GITLEAKS_PR_TARGET_SHA")

        if pr_source_sha is None or pr_target_sha is None:
            if utils.is_azure_devops_pr():
                # SYSTEM_PULLREQUEST_SOURCECOMMITID -> SHA of the last commit of the PR
                # BUILD_SOURCEVERSION -> SHA of the PR intermediate merge branch
                pr_source_sha = config.get(
                    self.request_id, "SYSTEM_PULLREQUEST_SOURCECOMMITID"
                )
                # SYSTEM_PULLREQUEST_TARGETBRANCH -> name of the target branch, e.g. refs/heads/main
                pr_target_sha = self.get_azure_devops_pr_target_sha(
                    config.get(self.request_id, "SYSTEM_PULLREQUEST_TARGETBRANCH")
                )
            elif utils.is_github_pr():
                pr_source_sha, pr_target_sha = self.get_github_sha()
            elif utils.is_gitlab_mr() and utils.is_gitlab_premium():
                # CI_MERGE_REQUEST_SOURCE_BRANCH_SHA -> SHA of the last commit of the PR
                pr_source_sha = config.get(
                    self.request_id, "CI_MERGE_REQUEST_SOURCE_BRANCH_SHA"
                )
                # CI_MERGE_REQUEST_TARGET_BRANCH_SHA -> SHA of the last commit in the target branch
                pr_target_sha = config.get(
                    self.request_id, "CI_MERGE_REQUEST_TARGET_BRANCH_SHA"
                )
            elif utils.is_gitlab_external_pr() and utils.is_gitlab_premium():
                # CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_SHA -> SHA of the last commit of the PR
                pr_source_sha = config.get(
                    self.request_id, "CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_SHA"
                )
                # CI_EXTERNAL_PULL_REQUEST_TARGET_BRANCH_SHA -> SHA of the last commit in the target branch
                pr_target_sha = config.get(
                    self.request_id, "CI_EXTERNAL_PULL_REQUEST_TARGET_BRANCH_SHA"
                )

        return pr_source_sha, pr_target_sha

    def get_azure_devops_pr_target_sha(self, target_branch_name):
        repo = utils.git.Repo(os.path.realpath(self.workspace))
        return repo.commit(target_branch_name.replace("refs/heads", "origin"))

    def get_github_sha(self):
        gh_event_file = open(config.get(self.request_id, "GITHUB_EVENT_PATH"))
        gh_event = json.load(gh_event_file)
        gh_event_file.close()
        return (
            # event.pull_request.head.sha -> SHA of the last commit of the PR
            gh_event["pull_request"]["head"]["sha"],
            # event.pull_request.base.sha -> SHA of the last commit in the target branch
            gh_event["pull_request"]["base"]["sha"],
        )

    # Manage presence of --no-git in command line
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        # --redact has been sent by user in REPOSITORY_GITLEAKS_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--redact" in self.cli_lint_user_args:
            cmd = list(dict.fromkeys(cmd))

        # --no-git has been sent by user in REPOSITORY_GITLEAKS_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--no-git" in self.cli_lint_user_args:
            cmd = list(dict.fromkeys(cmd))
        # --no-git has been sent by default from ML descriptor
        # but as it is a git repo, remove all --no-git from arguments list
        elif "--no-git" in cmd and utils.is_git_repo(self.workspace):
            cmd = list(filter(lambda a: a != "--no-git", cmd))

        if (
            config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
            and self.pr_commits_scan == "true"
            and utils.is_pr()
        ):
            if (
                self.pr_target_sha is not None
                and self.pr_source_sha is not None
                and self.pr_target_sha != self.pr_source_sha
            ):
                # `--log-opts <arg_value>` has been sent by user in REPOSITORY_GITLEAKS_ARGUMENTS
                if "--log-opts" in cmd:
                    cmd.pop(cmd.index("--log-opts") + 1)
                    cmd.pop(cmd.index("--log-opts"))

                # `--log-opts=<arg_value>` has been sent by user in REPOSITORY_GITLEAKS_ARGUMENTS
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
