#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging
import os

import requests

from megalinter import Reporter


class GithubStatusReporter(Reporter):
    name = 'GITHUB_STATUS'
    scope = 'linter'

    github_api_url = 'https://api.github.com'

    def __init__(self, params=None):
        # Activate GitHub Status by default
        self.is_active = True
        super().__init__(params)

    def manage_activation(self):
        # Disable status for each linter if MULTI_STATUS is 'false'
        if "MULTI_STATUS" in os.environ and os.environ["MULTI_STATUS"] == 'false':
            self.is_active = False
        elif os.environ.get("GITHUB_STATUS_REPORTER", "true") != "true":
            self.is_active = False

    def produce_report(self):
        if 'GITHUB_REPOSITORY' in os.environ and 'GITHUB_SHA' in os.environ and \
                'GITHUB_TOKEN' in os.environ and 'GITHUB_RUN_ID' in os.environ:
            github_repo = os.environ['GITHUB_REPOSITORY']
            sha = os.environ['GITHUB_SHA']
            run_id = os.environ['GITHUB_RUN_ID']
            success_msg = 'No errors were found in the linting process'
            error_not_blocking = 'Errors were detected but are considered not blocking'
            error_msg = 'Errors were detected, please view logs'
            url = f"{self.github_api_url}/repos/{github_repo}/statuses/{sha}"
            headers = {
                'accept': 'application/vnd.github.v3+json',
                'authorization': f"Bearer {os.environ['GITHUB_TOKEN']}",
                'content-type': 'application/json'
            }
            target_url = f"https://github.com/{github_repo}/actions/runs/{run_id}"
            data = {
                'state': 'success' if self.master.return_code == 0 else 'error',
                'target_url': target_url,
                'description': success_msg if self.master.status == 'success' and self.master.return_code == 0
                else error_not_blocking if self.master.status == 'error' and self.master.return_code == 0
                else error_msg,
                'context': f"--> Lint: {self.master.descriptor_id} with {self.master.linter_name}"
            }
            response = requests.post(url,
                                     headers=headers,
                                     json=data)
            if 200 <= response.status_code < 299:
                logging.debug(
                    f"Successfully posted Github Status for {self.master.descriptor_id} with {self.master.linter_name}")
            else:
                logging.error(
                    f"Error posting Github Status for {self.master.descriptor_id}"
                    f"with {self.master.linter_name}: {response.status_code}")
                logging.error(f"GitHub API response: {response.text}")
        else:
            logging.debug(
                f"Skipped post of Github Status for {self.master.descriptor_id} with {self.master.linter_name}")
