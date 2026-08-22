#!/usr/bin/env python3
"""
GitLab CI provider
"""

from megalinter import config, utils
from megalinter.ci_providers.CiProvider import CiProvider


class CiProviderGitlab(CiProvider):
    name = "GitLab CI"

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
