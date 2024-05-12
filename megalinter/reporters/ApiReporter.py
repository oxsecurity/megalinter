#!/usr/bin/env python3
"""
API Reporter
Send MegaLinter results to an external API, like Grafana Loki
"""
import copy
import json
import logging
import os
import time

import requests
from megalinter import Reporter, config
from megalinter.constants import ML_DOC_URL_DESCRIPTORS_ROOT
from megalinter.utils import get_git_context_info


class ApiReporter(Reporter):
    name = "API_REPORTER"
    scope = "mega-linter"

    api_url: str | None = None
    payload: dict = {"linters": []}
    linter_payloads: list[dict] = []
    payloadFormatted: dict = {}

    def __init__(self, params=None):
        # Deactivate Api reporter by default
        self.is_active = False
        self.processing_order = 20  # Run after text reporter
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "API_REPORTER", "false") == "true":
            if (
                config.exists(self.master.request_id, "API_REPORTER_URL") or 
                config.exists(self.master.request_id, "NOTIF_API_URL")
            ):
                self.is_active = True
                self.api_url = config.get_first_var_set(self.master.request_id, ["API_REPORTER_URL","NOTIF_API_URL"])
            else:
                logging.error("You need to define API_REPORTER_URL to use ApiReporter")

    # Send JSON log to remote api
    def produce_report(self):
        # Build payload
        self.build_payload()
        # Format payload according to target
        self.format_payload()
        # Call API
        self.send_to_api()

    def build_payload(self):
        # Git info
        repo_info = get_git_context_info(self.master.request_id, os.path.realpath(self.master.github_workspace))
        git_identifier = f"{repo_info["repo_name"]}/{repo_info["branch_name"]}"
        org_identifier = self.get_org_identifier(git_identifier)
        self.payload = {
            "source": "MegaLinter",
            "gitRepoName": repo_info["repo_name"],
            "gitBranchName": repo_info["branch_name"],
            "gitIdentifier": git_identifier,
            "orgIdentifier": org_identifier,
            "data": {},
            "linters": [],
        }
        for linter in self.master.linters:
            if linter.is_active is True:
                lang_lower = linter.descriptor_id.lower()
                linter_name_lower = linter.linter_name.lower().replace("-", "_")
                linter_doc_url = (
                    f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
                )
                linter_payload = {
                    "descriptor": linter.descriptor_id,
                    "linter": linter.linter_name,
                    "linterKey": linter.name,
                    "linterDocUrl": linter_doc_url,
                    "data": {},
                }
                # Status
                linter_payload["severity"] = (
                    "success"
                    if linter.status == "success" and linter.return_code == 0
                    else (
                        "warning"
                        if linter.status != "success" and linter.return_code == 0
                        else "error"
                    )
                )
                linter_payload_data = {}
                linter_payload_data["severityIcon"] = (
                    "✅"
                    if linter.status == "success" and linter.return_code == 0
                    else (
                        "⚠️"
                        if linter.status != "success" and linter.return_code == 0
                        else "❌"
                    )
                )
                # Number of files & errors
                linter_payload_data["cliLintMode"] = linter.cli_lint_mode
                if linter.cli_lint_mode != "project":
                    linter_payload_data["numberFilesFound"] = len(linter.files)
                linter_payload_data["numberErrorsFound"] = linter.total_number_errors
                # Fixed cells
                if linter.try_fix is True:
                    linter_payload_data["numberErrorsFixed"] = linter.number_fixed
                # Elapsed time
                if self.master.show_elapsed_time is True:
                    linter_payload_data["elapsedTime"] = round(linter.elapsed_time_s, 2)
                # Add to linters
                linter_payload["data"] = linter_payload_data
                self.payload["linters"].append(linter_payload)


    def get_org_identifier(self, git_identifier: str):
        org_identifier = config.get(
                        self.master.request_id, "API_REPORTER_ORG_IDENTIFIER", None
                    )
        if org_identifier is not None:
            return org_identifier
        return git_identifier.replace("monitoring_","").replace("__","--").replace("_sandbox",".sandbox")


    def format_payload(self):
        if (
            "loki/api/v1/push" in self.api_url
            or self.api_url
            == "https://jsonplaceholder.typicode.com/posts"  # For test class
        ):
            self.format_payload_loki()
            return
        self.payloadFormatted = self.payload

    def format_payload_loki(self):
        time_ns = time.time_ns()
        streams = []
        for linter in self.payload["linters"]:
            stream_info = copy.deepcopy(self.payload)
            del stream_info["data"]
            del stream_info["linters"]
            linter_copy = copy.deepcopy(linter)
            del linter_copy["data"]
            stream_info.update(linter_copy)
            data = copy.deepcopy(linter["data"])
            data.update(self.payload["data"])
            stream = {
                "stream": stream_info,
                "values": [[str(time_ns), json.dumps(data)]],
            }
            streams.append(stream)
        self.payloadFormatted = {"streams": streams}

    def send_to_api(self):
        session = requests.Session()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        # Use username & password
        if (
            config.exists(self.master.request_id, "API_REPORTER_BASIC_AUTH_USERNAME") or 
            config.exists(self.master.request_id, "NOTIF_API_BASIC_AUTH_USERNAME")
        ):
            session.auth = (
                config.get_first_var_set(self.master.request_id, ["API_REPORTER_BASIC_AUTH_USERNAME","NOTIF_API_BASIC_AUTH_USERNAME"]),
                config.get_first_var_set(self.master.request_id, ["API_REPORTER_BASIC_AUTH_PASSWORD","NOTIF_API_BASIC_AUTH_PASSWORD"]),
            )
        # Use token
        if (
            config.exists(self.master.request_id, "API_REPORTER_BEARER_TOKEN") or 
            config.exists(self.master.request_id, "NOTIF_API_BEARER_TOKEN") 
        ):
            headers["Authorization"] = (
                f"Bearer {config.get_first_var_set(self.master.request_id, ["API_REPORTER_BEARER_TOKEN","NOTIF_API_REPORTER_BEARER_TOKEN"])}"
            )
        try:
            response = session.post(
                self.api_url, headers=headers, json=self.payloadFormatted
            )
            if 200 <= response.status_code < 300:
                logging.info(
                    f"[Api Reporter] Successfully posted data to {self.api_url}"
                )
                if config.get_first_var_set(self.master.request_id,[ "API_REPORTER_DEBUG","NOTIF_API_DEBUG"]):
                    logging.info(json.dumps(obj=self.payloadFormatted, indent=True))
            else:
                logging.warning(
                    f"[Api Reporter] Error posting data to {self.api_url} ({response.status_code})\n"
                    f"Api request: {json.dumps(obj=self.payloadFormatted, indent=True)}\n"
                    f"API response: {response.text}"
                )
        except ConnectionError as e:
            logging.warning(
                f"[Api Reporter] Error posting data to {self.api_url}:"
                f"Connection error {str(e)}"
            )
        except Exception as e:
            logging.warning(
                f"[Api Reporter] Error posting data to {self.api_url}:"
                f"Connection error {str(e)}"
            )
