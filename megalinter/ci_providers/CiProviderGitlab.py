#!/usr/bin/env python3
"""
GitLab CI provider
"""

import re
import time

from megalinter import config, utils
from megalinter.ci_providers.CiProvider import CiProvider


class CiProviderGitlab(CiProvider):
    name = "GitLab CI"

    @staticmethod
    def is_current() -> bool:
        return utils.is_gitlab_ci()

    @staticmethod
    def is_pr_context() -> bool:
        return utils.is_gitlab_mr() or utils.is_gitlab_external_pr()

    # Source and target SHAs are predefined variables available only on
    # Premium/Ultimate with merged results pipelines enabled
    def get_pr_commit_shas(self):
        if not utils.is_gitlab_premium():
            return None, None
        if utils.is_gitlab_mr():
            prefix = "CI_MERGE_REQUEST"
        else:
            prefix = "CI_EXTERNAL_PULL_REQUEST"
        return (
            config.get(self.request_id, f"{prefix}_SOURCE_BRANCH_SHA"),
            config.get(self.request_id, f"{prefix}_TARGET_BRANCH_SHA"),
        )

    def get_pr_commit_shas_hint(self) -> str:
        return (
            "merge request pipelines expose the source and target SHAs only on "
            "GitLab Premium/Ultimate with merged results pipelines enabled: set "
            "`GIT_DEPTH: 0` and enable them, or define the SHAs manually"
        )

    def get_repo_name(self):
        return self.split_repo_name(config.get(self.request_id, "CI_PROJECT_NAME"))

    def get_branch_name(self):
        return config.get(self.request_id, "CI_COMMIT_REF_NAME")

    def get_job_url(self) -> str:
        return config.get(self.request_id, "CI_JOB_URL", "")

    def get_server_url(self) -> str:
        return config.get(self.request_id, "CI_SERVER_URL", "https://gitlab.com")

    def get_project_id(self):
        return config.get(self.request_id, "CI_PROJECT_ID")

    # Token provided by the runner, restricted to the job scope
    def get_auth_token(self):
        token = config.get(self.request_id, "CI_JOB_TOKEN", "")
        return token if token != "" else None

    # User-provided token, needed for anything the job token can not do
    def get_user_auth_token(self):
        token = config.get(self.request_id, "GITLAB_ACCESS_TOKEN_MEGALINTER", "")
        return token if token != "" else None

    # python-gitlab takes the two token kinds under different names
    def get_api_auth_options(self):
        user_token = self.get_user_auth_token()
        if user_token is not None:
            return {"private_token": user_token}
        return {"job_token": self.get_auth_token()}

    # Merge request iid, read from CI_MERGE_REQUEST_ID then from the
    # "project!iid" pairs of CI_OPEN_MERGE_REQUESTS
    def get_pr_number(self):
        merge_request_id = config.get(self.request_id, "CI_MERGE_REQUEST_ID", "")
        if merge_request_id != "":
            return merge_request_id
        open_merge_requests = config.get(self.request_id, "CI_OPEN_MERGE_REQUESTS", "")
        if open_merge_requests != "":
            return open_merge_requests.split(",")[0].split("!")[1]
        return None

    # Second spelling tried when the first id does not resolve
    def get_pr_number_fallback(self):
        return config.get(self.request_id, "CI_MERGE_REQUEST_IID", "none")

    # GitLab section names accept only letters, numbers, '_', '.' and '-'
    @staticmethod
    def sanitize_section_key(key: str) -> str:
        key = re.sub(r"[^0-9A-Za-z_.-]+", "_", (key or "")).strip("._")
        return (key or "section")[:80]

    def log_section_start(self, section_key: str, section_title: str) -> str:
        ts = int(time.time())
        safe_key = self.sanitize_section_key(section_key)
        return (
            f"section_start:{ts}:{safe_key}"  # noqa: W605
            + f"[collapsed=true]\r\x1b[0K{section_title}"  # noqa: W605
        )

    def log_section_end(self, section_key: str) -> str:
        ts = int(time.time())
        safe_key = self.sanitize_section_key(section_key)
        return f"section_end:{ts}:{safe_key}\r\x1b[0K"  # noqa: W605
