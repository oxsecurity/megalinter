#!/usr/bin/env python3
"""
Bitbucket Pipelines CI provider
"""

import urllib.parse

from megalinter import config, utils
from megalinter.ci_providers.CiProvider import CiProvider


class CiProviderBitbucket(CiProvider):
    name = "Bitbucket Pipelines"
    # Bitbucket Cloud strips raw HTML from Pull Request comments
    markdown_supports_html_details = False

    @staticmethod
    def is_current() -> bool:
        return utils.is_bitbucket()

    @staticmethod
    def is_pr_context() -> bool:
        return utils.is_bitbucket_pr()

    def get_repo_name(self):
        return self.split_repo_name(config.get(self.request_id, "BITBUCKET_REPO_SLUG"))

    def get_branch_name(self):
        return config.get(self.request_id, "BITBUCKET_BRANCH")

    def get_job_url(self) -> str:
        step_uuid = config.get(self.request_id, "BITBUCKET_STEP_UUID", "")
        if step_uuid == "":
            return ""
        project_url = config.get(self.request_id, "BITBUCKET_GIT_HTTP_ORIGIN", "")
        build_number = config.get(self.request_id, "BITBUCKET_BUILD_NUMBER", "")
        return (
            f"{project_url}/pipelines/results/"
            f"{build_number}/steps/{urllib.parse.quote(step_uuid)}"
        )

    def get_repo_slug(self):
        slug = config.get(self.request_id, "BITBUCKET_REPO_FULL_NAME", "")
        return slug if slug != "" else None

    def get_pr_number(self):
        pr_id = config.get(self.request_id, "BITBUCKET_PR_ID", "")
        return pr_id if pr_id != "" else None

    def get_auth_token(self):
        token = config.get(self.request_id, "BITBUCKET_REPO_ACCESS_TOKEN", "")
        return token if token != "" else None

    def get_api_headers(self):
        return {"Authorization": f"Bearer {self.get_auth_token()}"}

    def get_pr_commit_shas_hint(self) -> str:
        return (
            "Bitbucket Pipelines exposes no Pull Request commit range: define "
            "the SHAs manually"
        )
