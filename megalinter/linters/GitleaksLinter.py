#!/usr/bin/env python3
"""
Use GitLeaks to check for credentials in repository
"""
import json
import os

from git import Repo

from megalinter import Linter, config
from megalinter.utils import is_git_repo


class GitleaksLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super().__init__(params, linter_config)
        self.only_pr_commits = config.get("REPOSITORY_GITLEAKS_ONLY_PR_COMMITS", "false")
        if self.only_pr_commits == "true":
            self.is_pr, self.pr_source_sha, self.pr_target_sha = self.get_pr_data()


    def get_pr_data(self):
        # https://learn.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml
        is_azure_devops_pr = config.get("BUILD_REASON") == "PullRequest"
        azure_devops_pr_source_sha = config.get("BUILD_SOURCEVERSION")
        azure_devops_pr_target_sha = self.get_azure_devops_pr_target_sha(config.get("SYSTEM_PULLREQUEST_TARGETBRANCH"), is_azure_devops_pr)

        # https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
        is_github_pr = config.get("GITHUB_EVENT_NAME") == "pull_request"
        github_pr_source_sha, github_pr_target_sha = self.get_github_sha(is_github_pr)

        # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
        # SHAs are available only on GitLab Premium
        is_gitlab_premium = (
            True
            if config.get("CI_MERGE_REQUEST_EVENT_TYPE") == "merged_result" or config.get("CI_MERGE_REQUEST_EVENT_TYPE") == "merge_train"
            else False
        )

        # GitLab merge request
        is_gitlab_mr = config.get("CI_PIPELINE_SOURCE") == "merge_request_event"
        gitlab_mr_source_sha = config.get("CI_MERGE_REQUEST_SOURCE_BRANCH_SHA")
        gitlab_mr_target_sha = config.get("CI_MERGE_REQUEST_TARGET_BRANCH_SHA")

        # GitLab external PR #
        is_gitlab_external_pr = config.get("CI_PIPELINE_SOURCE") == "external_pull_request_event"
        gitlab_external_pr_source_sha = config.get("CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_SHA")
        gitlab_external_pr_target_sha = config.get("CI_EXTERNAL_PULL_REQUEST_TARGET_BRANCH_SHA")

        is_pr = (
            True
            if (
                is_azure_devops_pr
                or is_github_pr
                or (is_gitlab_mr and is_gitlab_premium)
                or (is_gitlab_external_pr and is_gitlab_premium)
            )
            else False
        )

        pr_source_sha = None
        pr_target_sha = None

        if is_azure_devops_pr:
            pr_source_sha = azure_devops_pr_source_sha
            pr_target_sha = azure_devops_pr_target_sha
        elif is_github_pr:
            pr_source_sha = github_pr_source_sha
            pr_target_sha = github_pr_target_sha
        elif is_gitlab_mr:
            pr_source_sha = gitlab_mr_source_sha
            pr_target_sha = gitlab_mr_target_sha
        elif is_gitlab_external_pr:
            pr_source_sha = gitlab_external_pr_source_sha
            pr_target_sha = gitlab_external_pr_target_sha

        return is_pr, pr_source_sha, pr_target_sha

    def get_azure_devops_pr_target_sha(self, target_branch_name, is_pr=False):
        if not is_pr:
            return None
        repo = Repo(os.path.realpath(self.workspace))
        return repo.commit(target_branch_name.replace("refs/heads", "origin"))

    def get_github_sha(self, is_pr=False):
        if not is_pr:
            return None, None
        gh_event_file = open(os.environ["GITHUB_EVENT_PATH"])
        gh_event = json.load(gh_event_file)
        gh_event_file.close()
        return (
            gh_event["pull_request"]["head"]["sha"],
            gh_event["pull_request"]["base"]["sha"],
        )

    # Manage presence of --no-git in command line
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        # --no-git has been sent by user in REPOSITORY_GITLEAKS_ARGUMENTS
        # make sure that it is only once in the arguments list
        if "--no-git" in self.cli_lint_user_args:
            cmd = list(dict.fromkeys(cmd))
        # --no-git has been sent by default from ML descriptor
        # but as it is a git repo, remove all --no-git from arguments list
        elif "--no-git" in cmd and is_git_repo(self.workspace):
            cmd = list(filter(lambda a: a != "--no-git", cmd))

        if config.get("VALIDATE_ALL_CODEBASE") == "false" and self.only_pr_commits == "true":
            if self.is_pr:
                if self.pr_target_sha != self.pr_source_sha:
                    cmd += [
                        f"--log-opts={self.pr_target_sha}^..{self.pr_source_sha}"
                    ]

        return cmd
