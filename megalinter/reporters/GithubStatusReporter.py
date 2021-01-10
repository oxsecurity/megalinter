#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging

import requests
from megalinter import Reporter, config


class GithubStatusReporter(Reporter):
    name = "GITHUB_STATUS"
    scope = "linter"

    github_api_url = "https://api.github.com"
    github_server_url = "https://github.com"

    def __init__(self, params=None):
        # Activate GitHub Status by default
        self.is_active = True
        super().__init__(params)

    def manage_activation(self):
        # Disable status for each linter if MULTI_STATUS is 'false'
        if config.exists("MULTI_STATUS") and config.get("MULTI_STATUS") == "false":
            self.is_active = False
        elif config.get("GITHUB_STATUS_REPORTER", "true") != "true":
            self.is_active = False

    def produce_report(self):
        if (
            config.exists("GITHUB_REPOSITORY")
            and config.exists("GITHUB_SHA")
            and config.exists("GITHUB_TOKEN")
            and config.exists("GITHUB_RUN_ID")
        ):
            github_repo = config.get("GITHUB_REPOSITORY")
            github_server_url = config.get("GITHUB_SERVER_URL", self.github_server_url)
            github_api_url = config.get("GITHUB_API_URL", self.github_api_url)
            sha = config.get("GITHUB_SHA")
            run_id = config.get("GITHUB_RUN_ID")
            success_msg = "No errors were found in the linting process"
            error_not_blocking = "Errors were detected but are considered not blocking"
            error_msg = f"Found {self.master.total_number_errors}, please check logs"
            url = f"{github_api_url}/repos/{github_repo}/statuses/{sha}"
            headers = {
                "accept": "application/vnd.github.v3+json",
                "authorization": f"Bearer {config.get('GITHUB_TOKEN')}",
                "content-type": "application/json",
            }
            target_url = f"{github_server_url}/{github_repo}/actions/runs/{run_id}"
            description = (
                success_msg
                if self.master.status == "success" and self.master.return_code == 0
                else error_not_blocking
                if self.master.status == "error" and self.master.return_code == 0
                else error_msg
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
