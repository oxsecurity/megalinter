#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""

import logging

import requests
from megalinter import Reporter, config
from megalinter.ci_providers import CiProviderGithubActions


class GithubStatusReporter(Reporter):
    name = "GITHUB_STATUS"
    scope = "linter"

    def __init__(self, params=None):
        # Activate GitHub Status by default
        self.is_active = False
        super().__init__(params)

    def manage_activation(self):
        # Disable status for each linter if MULTI_STATUS is 'false'
        if (
            config.exists(self.master.request_id, "MULTI_STATUS")
            and config.get(self.master.request_id, "MULTI_STATUS") == "true"
        ):
            self.is_active = True
        elif (
            config.get(self.master.request_id, "GITHUB_STATUS_REPORTER", "false")
            != "false"
        ):
            self.is_active = True

    def produce_report(self):
        if (
            config.exists(self.master.request_id, "GITHUB_REPOSITORY")
            and config.exists(self.master.request_id, "GITHUB_SHA")
            and config.exists(self.master.request_id, "GITHUB_TOKEN")
        ):
            ci_provider = CiProviderGithubActions(self.master.request_id)
            github_repo = ci_provider.get_repo_slug()
            github_api_url = ci_provider.get_api_url()
            sha = ci_provider.get_commit_sha()
            success_msg = "No errors were found in the linting process"
            error_not_blocking = "Errors were detected but are considered not blocking"
            error_msg = (
                f"Found {self.master.total_number_errors} errors, please check logs"
            )
            url = f"{github_api_url}/repos/{github_repo}/statuses/{sha}"
            headers = {
                "accept": "application/vnd.github.v3+json",
                # Deliberately the runner token, not PAT: a commit status needs
                # the statuses:write scope, which the documented fine-grained
                # PAT (Contents only) does not carry
                "authorization": f"Bearer {ci_provider.get_auth_token()}",
                "content-type": "application/json",
            }
            if config.exists(self.master.request_id, "GITHUB_RUN_ID"):
                target_url = ci_provider.get_job_url()
            else:
                target_url = config.get(self.master.request_id, "GITHUB_TARGET_URL")
            description = (
                success_msg
                if self.master.status == "success" and self.master.return_code == 0
                else (
                    error_not_blocking
                    if self.master.status == "error" and self.master.return_code == 0
                    else error_msg
                )
            )
            if self.master.show_elapsed_time is True:
                description += f" ({str(round(self.master.elapsed_time_s, 2))}s)"
            data = {
                "state": "success" if self.master.return_code == 0 else "error",
                "target_url": target_url,
                "description": description,
                "context": f"--> Lint: {self.master.descriptor_id} with {self.master.linter_name}",
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if 200 <= response.status_code < 299:
                    logging.debug(
                        f"Successfully posted Github Status for {self.master.descriptor_id} "
                        f"with {self.master.linter_name}"
                    )
                else:
                    logging.warning(
                        f"[GitHub Status Reporter] Error posting Status for {self.master.descriptor_id}"
                        f"with {self.master.linter_name}: {response.status_code}\n"
                        f"GitHub API response: {response.text}"
                    )
            except ConnectionError as e:
                logging.warning(
                    f"[GitHub Status Reporter] Error posting Status for {self.master.descriptor_id}"
                    f"with {self.master.linter_name}: Connection error {str(e)}"
                )
            except Exception as e:
                logging.warning(
                    f"[GitHub Status Reporter] Error posting Status for {self.master.descriptor_id}"
                    f"with {self.master.linter_name}: Error {str(e)}"
                )
        else:
            logging.debug(
                f"Skipped post of Github Status for {self.master.descriptor_id} with {self.master.linter_name}"
            )
