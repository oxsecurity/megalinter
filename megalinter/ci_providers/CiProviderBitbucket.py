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

    def get_pr_commit_shas_hint(self) -> str:
        return (
            "Bitbucket Pipelines exposes no Pull Request commit range: define "
            "the SHAs manually"
        )
