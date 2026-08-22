#!/usr/bin/env python3
"""
Azure Pipelines CI provider
"""

import base64
import logging
import os
import re
import urllib.parse

import git
import requests
from megalinter import config, utils
from megalinter.ci_providers.CiProvider import CiProvider


class CiProviderAzurePipelines(CiProvider):
    name = "Azure Pipelines"
    api_version = "7.1"

    @staticmethod
    def is_current() -> bool:
        return utils.is_azure_pipelines()

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

    def get_repo_name(self):
        return self.split_repo_name(config.get(self.request_id, "BUILD_REPOSITORYNAME"))

    def get_branch_name(self):
        return config.get(self.request_id, "BUILD_SOURCEBRANCHNAME")

    # Azure exposes the build id under two different names depending on the
    # agent version
    def get_build_id(self):
        return config.get(
            self.request_id,
            "BUILD_BUILDID",
            config.get(self.request_id, "BUILD_BUILD_ID"),
        )

    def get_collection_uri(self) -> str:
        return config.get(self.request_id, "SYSTEM_COLLECTIONURI", "")

    # Url-encoded, so a project name containing spaces builds a valid url
    def get_team_project(self) -> str:
        return urllib.parse.quote(config.get(self.request_id, "SYSTEM_TEAMPROJECT", ""))

    def get_job_url(self) -> str:
        collection_uri = self.get_collection_uri()
        if collection_uri == "":
            return ""
        return (
            f"{collection_uri}{self.get_team_project()}/_build/results"
            f"?buildId={self.get_build_id()}"
        )

    # Same build page, opened on its published artifacts
    def get_artifacts_url(self) -> str:
        job_url = self.get_job_url()
        if job_url == "":
            return ""
        return f"{job_url}&view=artifacts&pathAsName=false&type=publishedArtifacts"

    def get_pr_number(self):
        pr_id = config.get(self.request_id, "SYSTEM_PULLREQUEST_PULLREQUESTID", "")
        return pr_id if pr_id != "" else None

    def get_auth_token(self):
        token = config.get(self.request_id, "SYSTEM_ACCESSTOKEN", "")
        return token if token != "" else None

    def get_api_headers(self):
        # The ADO REST API expects Basic auth with an empty user name
        encoded_credentials = base64.b64encode(
            f":{self.get_auth_token()}".encode("utf-8")
        ).decode("utf-8")
        return {"Authorization": f"Basic {encoded_credentials}"}

    def build_git_api_url(self, path: str) -> str:
        return (
            f"{self.get_collection_uri()}{self.get_team_project()}/_apis/git{path}"
            f"?api-version={self.api_version}"
        )

    # Resolves the id of the repository being built. The source repository URI
    # gives the real repository even when the build runs from a fork, so it is
    # preferred over BUILD_REPOSITORY_ID, which stays the fallback
    def get_repository_id(self):
        build_repository_id = config.get(self.request_id, "BUILD_REPOSITORY_ID")
        source_repository_uri = config.get(
            self.request_id, "SYSTEM_PULLREQUEST_SOURCEREPOSITORYURI", ""
        )
        if source_repository_uri == "":
            logging.info(
                f"[{self.name}] Missing ADO variable System.PullRequest.SourceRepositoryURI\n"
                + "Falling back to ADO variable Build.Repository.ID\n"
                + "See https://learn.microsoft.com/en-us/azure/devops/pipelines/"
                + "build/variables?view=azure-devops&tabs=yaml"
            )
            return build_repository_id
        logging.info(
            f"[{self.name}] Using ADO variable System.PullRequest.SourceRepositoryURI\n"
            + "See https://learn.microsoft.com/en-us/azure/devops/pipelines/"
            + "build/variables?view=azure-devops&tabs=yaml"
        )
        repository_name = source_repository_uri.split("/")[-1]
        if (
            config.get(
                self.request_id, "AZURE_COMMENT_REPORTER_REPLACE_WITH_SPACES", "true"
            )
            == "true"
        ):
            repository_name = repository_name.replace("%20", " ")
        try:
            get_repository_response = requests.get(
                self.build_git_api_url(f"/repositories/{repository_name}"),
                headers=self.get_api_headers(),
            )
            if get_repository_response.status_code != 200:
                get_repository_response.raise_for_status()
            return get_repository_response.json()["id"]
        except Exception as err:
            logging.warning(
                f"[{self.name}] Unable to find repo {repository_name}:"
                + str(err)
                + "\nUse fallback with BUILD_REPOSITORY_ID."
            )
            return build_repository_id

    def log_section_start(self, section_key: str, section_title: str) -> str:
        return f"##[group]{section_title} (expand for details)"

    def log_section_end(self, section_key: str) -> str:
        return "##[endgroup]"
