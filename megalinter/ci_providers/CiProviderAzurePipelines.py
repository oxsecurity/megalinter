#!/usr/bin/env python3
"""
Azure Pipelines CI provider
"""

import logging
import os
import re

import git
from megalinter import config, utils
from megalinter.ci_providers.CiProvider import CiProvider


class CiProviderAzurePipelines(CiProvider):
    name = "Azure Pipelines"

    @staticmethod
    def is_pr_context() -> bool:
        return utils.is_azure_devops_pr()

    def get_pr_commit_shas(self):
        source_sha = config.get(self.request_id, "SYSTEM_PULLREQUEST_SOURCECOMMITID")
        target_sha = self.resolve_target_branch_sha(
            config.get(self.request_id, "SYSTEM_PULLREQUEST_TARGETBRANCH")
        )
        return source_sha, target_sha

    # Azure Pipelines exposes the target branch name, not its SHA. The default
    # checkout is shallow and creates no remote tracking ref, so several ref
    # spellings are tried and a failure returns None instead of raising
    def resolve_target_branch_sha(self, target_branch_name):
        if target_branch_name is None:
            return None
        short_name = re.sub(r"^refs/heads/", "", target_branch_name)
        candidates = [
            f"origin/{short_name}",
            f"refs/remotes/origin/{short_name}",
            target_branch_name,
            short_name,
        ]
        # dict.fromkeys removes duplicates while keeping the candidate order
        candidates = list(dict.fromkeys(candidates))
        try:
            with git.Repo(os.path.realpath(self.workspace)) as repo:
                for candidate in candidates:
                    try:
                        return repo.commit(candidate).hexsha
                    except (git.exc.GitError, git.exc.ODBError):
                        continue
        except (git.exc.GitError, git.exc.ODBError):
            return None
        logging.warning(
            f"[{self.name}] Unable to resolve target branch {target_branch_name} "
            f"to a commit (tried {', '.join(candidates)})"
        )
        return None

    def get_pr_commit_shas_hint(self) -> str:
        return (
            "check out the repository with `fetchDepth: 0` and forward "
            "SYSTEM_PULLREQUEST_SOURCECOMMITID, SYSTEM_PULLREQUEST_TARGETBRANCH "
            "and BUILD_REASON to the MegaLinter container"
        )
