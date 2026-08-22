#!/usr/bin/env python3
"""
GitHub Actions CI provider
"""

import json
import logging
import re

from megalinter import config, utils
from megalinter.ci_providers.CiProvider import CiProvider


class CiProviderGithubActions(CiProvider):
    name = "GitHub Actions"

    @staticmethod
    def is_current() -> bool:
        return utils.is_github_actions()

    @staticmethod
    def is_pr_context() -> bool:
        return utils.is_github_pr()

    # The event payload is read from a path provided by the runner: a missing,
    # unreadable or non Pull Request payload must not abort the run
    def get_pr_commit_shas(self):
        gh_event_path = config.get(self.request_id, "GITHUB_EVENT_PATH")
        if gh_event_path is None:
            return None, None
        try:
            with open(gh_event_path, encoding="utf-8") as gh_event_file:
                gh_event = json.load(gh_event_file)
            return (
                gh_event["pull_request"]["head"]["sha"],
                gh_event["pull_request"]["base"]["sha"],
            )
        except (OSError, ValueError, KeyError, TypeError):
            logging.warning(
                f"[{self.name}] Unable to read Pull Request commit SHAs from "
                f"event payload {gh_event_path}"
            )
            return None, None

    def get_pr_commit_shas_hint(self) -> str:
        return "check out the repository with `fetch-depth: 0`"

    def get_repo_name(self):
        return self.split_repo_name(config.get(self.request_id, "GITHUB_REPOSITORY"))

    def get_branch_name(self):
        return config.get_first_var_set(
            self.request_id, ["GITHUB_HEAD_REF", "GITHUB_REF_NAME"], None
        )

    def get_server_url(self) -> str:
        return config.get(self.request_id, "GITHUB_SERVER_URL", "https://github.com")

    def get_job_url(self) -> str:
        repo = config.get(self.request_id, "GITHUB_REPOSITORY", "")
        if repo == "":
            return ""
        run_id = config.get(self.request_id, "GITHUB_RUN_ID")
        return f"{self.get_server_url()}/{repo}/actions/runs/{run_id}"

    def get_api_url(self) -> str:
        return config.get(self.request_id, "GITHUB_API_URL", "https://api.github.com")

    def get_commit_sha(self):
        return config.get(self.request_id, "GITHUB_SHA")

    def get_repo_slug(self):
        return config.get(self.request_id, "GITHUB_REPOSITORY")

    # Pull Request number carried by GITHUB_REF on pull_request events
    def get_pr_number(self):
        ref = config.get(self.request_id, "GITHUB_REF", "")
        match = re.compile("refs/pull/(\\d+)/merge").match(ref)
        return match.group(1) if match is not None else None

    # Token provided by the runner, scoped by the workflow permissions
    def get_auth_token(self):
        token = config.get(self.request_id, "GITHUB_TOKEN", "")
        return token if token != "" else None

    # User-provided Personal Access Token, used only where the runner token is
    # not enough (a push must re-trigger workflows). It is NOT a drop-in
    # replacement: the documented fine-grained PAT is scoped to Contents only,
    # so operations needing other scopes must keep using get_auth_token()
    def get_user_auth_token(self):
        token = config.get(self.request_id, "PAT", "")
        return token if token != "" else None

    def log_section_start(self, section_key: str, section_title: str) -> str:
        return f"::group::{section_title} (expand for details)"

    def log_section_end(self, section_key: str) -> str:
        return "::endgroup::"

    def set_output(self, name: str, value) -> bool:
        github_output = config.get(self.request_id, "GITHUB_OUTPUT", "")
        if github_output == "":
            return False
        return self.append_to_platform_file(github_output, f"{name}={value}\n")

    def publish_job_summary(self, markdown: str) -> bool:
        summary_file = config.get(self.request_id, "GITHUB_STEP_SUMMARY", "")
        if summary_file == "":
            return False
        return self.append_to_platform_file(summary_file, markdown)

    # The runner owns these files: a failure to write must never break the run
    @staticmethod
    def append_to_platform_file(file_path, content) -> bool:
        try:
            with open(file_path, "a", encoding="utf-8") as platform_file:
                platform_file.write(content)
            return True
        except OSError as e:
            logging.warning(f"[GitHub Actions] Unable to write {file_path}: {str(e)}")
            return False
