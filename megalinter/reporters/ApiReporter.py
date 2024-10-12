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
from megalinter import Reporter, config, utils
from megalinter.constants import ML_DOC_URL_DESCRIPTORS_ROOT
from megalinter.utils import get_git_context_info


class ApiReporter(Reporter):
    name = "API_REPORTER"
    scope = "mega-linter"

    api_url: str | None = None
    payload: dict = {"linters": []}
    linter_payloads: list[dict] = []
    payloadFormatted: dict = {}
    api_metrics_url: str | None = None
    metrics_payload: str = ""
    MAX_LOKI_LOG_LENGTH = 200000
    TRUNCATE_LOKI_CHARS_LENGTH = 5000

    def __init__(self, params=None):
        # Deactivate Api reporter by default
        self.is_active = True
        self.processing_order = 20  # Run after text reporter
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "API_REPORTER", "false") == "true":
            if config.exists(
                self.master.request_id, "API_REPORTER_URL"
            ) or config.exists(self.master.request_id, "NOTIF_API_URL"):
                self.api_url = config.get_first_var_set(
                    self.master.request_id, ["API_REPORTER_URL", "NOTIF_API_URL"]
                )
                if self.api_url is not None:
                    self.is_active = True
                    logging.info("[ApiReporter] Enabled")
                else:
                    self.is_active = False
                    logging.error(
                        "[ApiReporter] API_REPORTER_URL must have a correct value to use ApiReporter"
                    )
            else:
                self.is_active = False
                logging.error(
                    "[ApiReporter] You need to define API_REPORTER_URL to use ApiReporter"
                )
        else:
            self.is_active = False
            logging.info(
                "[ApiReporter] Not enabled as API_REPORTER is not defined to true"
            )

    # Send JSON log to remote api
    def produce_report(self):
        # Build payload
        self.build_payload()
        # Format payload according to target
        self.format_payload()
        # Call API
        self.send_to_api()
        # Handle Metrics API if requested
        if config.exists(
            self.master.request_id, "API_REPORTER_METRICS_URL"
        ) or config.exists(self.master.request_id, "NOTIF_API_METRICS_URL"):
            self.api_metrics_url = config.get_first_var_set(
                self.master.request_id,
                ["API_REPORTER_METRICS_URL", "NOTIF_API_METRICS_URL"],
            )
            self.build_metrics_payload()
            self.send_to_metrics_api()

    def build_payload(self):
        # Git info
        repo_info = get_git_context_info(
            self.master.request_id, os.path.realpath(self.master.github_workspace)
        )
        git_identifier = f"{repo_info["repo_name"]}/{repo_info["branch_name"]}"
        org_identifier = self.get_org_identifier(repo_info["branch_name"])
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
                    "data": {},
                }
                linter_payload_data = {
                    "linterDocUrl": linter_doc_url,
                    "jobUrl": repo_info["job_url"],
                }
                # Status
                linter_payload_data["severity"] = (
                    "success"
                    if linter.status == "success" and linter.return_code == 0
                    else (
                        "warning"
                        if linter.status != "success" and linter.return_code == 0
                        else "error"
                    )
                )
                linter_payload_data["severityIcon"] = (
                    "✅"
                    if linter.status == "success" and linter.return_code == 0
                    else (
                        "⚠️"
                        if linter.status != "success" and linter.return_code == 0
                        else "❌"
                    )
                )
                # Linter output for humans
                linter_payload_data["output"] = utils.normalize_log_string(
                    linter.stdout_human
                    if linter.stdout_human is not None
                    else linter.stdout
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

    def get_org_identifier(self, branch_name: str):
        org_identifier = config.get(
            self.master.request_id, "API_REPORTER_ORG_IDENTIFIER", None
        )
        if org_identifier is not None:
            return org_identifier
        # Workaround for sfdx-hardis, but it's better to set ENV variable API_REPORTER_ORG_IDENTIFIER
        return (
            branch_name.replace("monitoring_", "")
            .replace("_", "-")
            .replace("__", "--")
            .replace("_sandbox", "__sandbox")
        )

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
            # Truncate if too long
            payload_data_json = json.dumps(data)
            body_bytes_len = len(payload_data_json.encode("utf-8"))
            if body_bytes_len > self.MAX_LOKI_LOG_LENGTH:
                output: str = data["output"]
                data["output"] = (
                    output[: self.TRUNCATE_LOKI_CHARS_LENGTH] + "\n(truncated)"
                )
            data["output"] = data["output"].splitlines()
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
        if config.exists(
            self.master.request_id, "API_REPORTER_BASIC_AUTH_USERNAME"
        ) or config.exists(self.master.request_id, "NOTIF_API_BASIC_AUTH_USERNAME"):
            session.auth = (
                config.get_first_var_set(
                    self.master.request_id,
                    [
                        "API_REPORTER_BASIC_AUTH_USERNAME",
                        "NOTIF_API_BASIC_AUTH_USERNAME",
                    ],
                ),
                config.get_first_var_set(
                    self.master.request_id,
                    [
                        "API_REPORTER_BASIC_AUTH_PASSWORD",
                        "NOTIF_API_BASIC_AUTH_PASSWORD",
                    ],
                ),
            )
            if self.is_notif_api_debug_active():
                logging.info("[Api Reporter] Using Basic Auth")
        # Use token
        elif config.exists(
            self.master.request_id, "API_REPORTER_BEARER_TOKEN"
        ) or config.exists(self.master.request_id, "NOTIF_API_BEARER_TOKEN"):
            bearer = config.get_first_var_set(
                self.master.request_id,
                ["API_REPORTER_BEARER_TOKEN", "NOTIF_API_BEARER_TOKEN"],
            )
            headers["Authorization"] = f"Bearer {bearer}"
            if self.is_notif_api_debug_active():
                logging.info("[Api Reporter] Using Bearer Token")
        try:
            response = session.post(
                self.api_url, headers=headers, json=self.payloadFormatted
            )
            if 200 <= response.status_code < 300:
                logging.info(
                    f"[Api Reporter] Successfully posted data to {self.api_url}"
                )
                if self.is_notif_api_debug_active():
                    logging.info(
                        "[Api Reporter] "
                        + json.dumps(obj=self.payloadFormatted, indent=True)
                    )
            else:
                logging.warning(
                    f"[Api Reporter] Error posting data to {self.api_url} ({response.status_code})\n"
                    f"[Api Reporter] API request: {json.dumps(obj=self.payloadFormatted, indent=True)}\n"
                    f"[Api Reporter] API response: {response.text}"
                )
        except ConnectionError as e:
            logging.warning(
                f"[Api Reporter] Error posting data to {self.api_url}:"
                f"[Api Reporter] Connection error {str(e)}"
            )
        except Exception as e:
            logging.warning(
                f"[Api Reporter] Error posting data to {self.api_url}:"
                f"[Api Reporter] Connection error {str(e)}"
            )

    # Build something like:
    # MetricName,source=sfdx-hardis,orgIdentifier=hardis-group metric=12.7,min=0,max=70,percent=0.63
    def build_metrics_payload(self):
        metric_base_tags = (
            f"source={self.payload["source"]},"
            + f"orgIdentifier={self.payload["orgIdentifier"]},"
            + f"gitIdentifier={self.payload["gitIdentifier"]},"
            + f"gitRepoName={self.payload["gitRepoName"]},"
            + f"gitBranchName={self.payload["gitBranchName"]},"
        )
        all_metrics_lines = []
        for linter in self.master.linters:
            if linter.is_active is True:
                metric_line = (
                    "linter_run,"
                    + metric_base_tags
                    + f"descriptor={linter.descriptor_id},"
                    + f"linter={linter.linter_name},"
                    + f"linterKey={linter.name}"
                    + " "
                )
                metric_line += f"numberErrorsFound={linter.total_number_errors}"
                # Number of files & errors
                if linter.cli_lint_mode != "project":
                    metric_line += f",numberFilesFound={len(linter.files)}"
                # Fixed files
                if linter.try_fix is True:
                    metric_line += f",numberErrorsFixed={str(linter.number_fixed)}"
                # Elapsed time
                if self.master.show_elapsed_time is True:
                    metric_line += f",elapsedTime={round(linter.elapsed_time_s, 2)}"
                all_metrics_lines += [metric_line]
        self.metrics_payload = "\n".join(all_metrics_lines)

    def send_to_metrics_api(self):
        session = requests.Session()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        # Use username & password
        if config.exists(
            self.master.request_id, "API_REPORTER_METRICS_BASIC_AUTH_USERNAME"
        ) or config.exists(
            self.master.request_id, "NOTIF_API_METRICS_BASIC_AUTH_USERNAME"
        ):
            session.auth = (
                config.get_first_var_set(
                    self.master.request_id,
                    [
                        "API_REPORTER_METRICS_BASIC_AUTH_USERNAME",
                        "NOTIF_API_METRICS_BASIC_AUTH_USERNAME",
                    ],
                ),
                config.get_first_var_set(
                    self.master.request_id,
                    [
                        "API_REPORTER_METRICS_BASIC_AUTH_PASSWORD",
                        "NOTIF_API_METRICS_BASIC_AUTH_PASSWORD",
                    ],
                ),
            )
            if self.is_notif_api_debug_active():
                logging.info("[Api Reporter Metrics] Using Basic Auth")
        # Use token
        elif config.exists(
            self.master.request_id, "API_REPORTER_METRICS_BEARER_TOKEN"
        ) or config.exists(self.master.request_id, "NOTIF_API_METRICS_BEARER_TOKEN"):
            bearer = config.get_first_var_set(
                self.master.request_id,
                ["API_REPORTER_METRICS_BEARER_TOKEN", "NOTIF_API_METRICS_BEARER_TOKEN"],
            )
            headers["Authorization"] = f"Bearer {bearer}"
            if self.is_notif_api_debug_active():
                logging.info("[Api Reporter Metrics] Using Bearer Token")
        try:
            response = session.post(
                self.api_metrics_url, headers=headers, data=self.metrics_payload
            )
            if 200 <= response.status_code < 300:
                logging.info(
                    f"[Api Reporter Metrics] Successfully posted data to {self.api_metrics_url}"
                )
                if self.is_notif_api_debug_active():
                    logging.info("[Api Reporter Metrics] " + self.metrics_payload)
            else:
                logging.warning(
                    f"[Api Reporter Metrics] Error posting data to {self.api_metrics_url} ({response.status_code})\n"
                    f"[Api Reporter Metrics] API request: {self.metrics_payload}\n"
                    f"[Api Reporter Metrics] API response: {response.text}"
                )
        except ConnectionError as e:
            logging.warning(
                f"[Api Reporter Metrics] Error posting data to {self.api_metrics_url}:"
                f"[Api Reporter Metrics] Connection error {str(e)}"
            )
        except Exception as e:
            logging.warning(
                f"[Api Reporter Metrics] Error posting data to {self.api_metrics_url}:"
                f"[Api Reporter Metrics] Connection error {str(e)}"
            )

    def is_notif_api_debug_active(self):
        return (
            config.get_first_var_set(
                self.master.request_id, ["API_REPORTER_DEBUG", "NOTIF_API_DEBUG"]
            )
            == "true"
        )
