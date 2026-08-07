#!/usr/bin/env python3
"""
API Reporter
Build the MegaLinter results payload (v2) and send it to observability
backends through ApiProvider classes (Grafana, Datadog, Elastic, New Relic)
"""

import json
import logging
import os
import time
import uuid
from collections import Counter
from datetime import datetime, timezone

from megalinter import Reporter, config, utils
from megalinter.api_providers import PROVIDER_CLASSES
from megalinter.constants import ML_DOC_URL_DESCRIPTORS_ROOT, ML_VERSION
from megalinter.utils import get_git_context_info
from megalinter.utils_reporter import get_linter_status_icon

PAYLOAD_VERSION = 2
TOP_BREAKDOWN_SIZE = 20


class ApiReporter(Reporter):
    name = "API_REPORTER"
    scope = "mega-linter"

    payload: dict = {"linters": []}
    providers: list = []

    def __init__(self, params=None):
        # Activate Api reporter by default
        self.is_active = True
        self.processing_order = 20  # Run after text reporter
        # Approximates run duration: mega-linter scope reporters are created at startup
        self.init_time = time.time()
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "API_REPORTER", "false") != "true":
            self.is_active = False
            logging.info(
                "[ApiReporter] Not enabled as API_REPORTER is not defined to true"
            )
            return
        provider_keys = [
            provider.strip().lower()
            for provider in config.get(
                self.master.request_id, "API_REPORTER_PROVIDER", "auto"
            ).split(",")
            if provider.strip() != ""
        ]
        self.providers = []
        for provider_key in provider_keys:
            provider_class = PROVIDER_CLASSES.get(provider_key)
            if provider_class is None:
                logging.error(
                    f"[ApiReporter] Unknown provider '{provider_key}' "
                    f"(expected one of: {', '.join(PROVIDER_CLASSES.keys())})"
                )
                continue
            provider = provider_class(self.master.request_id)
            if provider.manage_activation():
                self.providers.append(provider)
        self.is_active = len(self.providers) > 0
        if self.is_active:
            logging.info(
                "[ApiReporter] Enabled with providers: "
                + ", ".join([provider.name for provider in self.providers])
            )

    def produce_report(self):
        self.build_payload()
        for provider in self.providers:
            provider.payload = self.payload
            provider.send()

    def build_payload(self):
        # Git info
        repo_info = get_git_context_info(
            self.master.request_id, os.path.realpath(self.master.github_workspace)
        )
        git_identifier = f"{repo_info['repo_name']}/{repo_info['branch_name']}"
        org_identifier = self.get_org_identifier(repo_info["branch_name"])

        # Build comment marker
        multirun_key = config.get(self.master.request_id, "MEGALINTER_MULTIRUN_KEY", "")
        multirun_key = multirun_key and f"key={multirun_key!r}"

        self.payload = {
            "payloadVersion": PAYLOAD_VERSION,
            "source": "MegaLinter",
            "runId": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "megalinterVersion": ML_VERSION,
            "megalinterFlavor": getattr(self.master, "megalinter_flavor", "unknown"),
            "gitRepoName": repo_info["repo_name"],
            "gitBranchName": repo_info["branch_name"],
            "gitIdentifier": git_identifier,
            "orgIdentifier": org_identifier,
            "marker": multirun_key,
            "jobUrl": repo_info["job_url"],
            "data": {},
            "run": {},
            "linters": [],
        }
        include_details = (
            config.get(self.master.request_id, "API_REPORTER_DETAILS", "true") == "true"
        )
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
                linter_payload_data["severityIcon"] = get_linter_status_icon(linter)
                linter_payload_data["blocking"] = linter.return_code != 0
                linter_payload_data["isFormatter"] = linter.is_formatter is True
                # Linter output for humans
                linter_payload_data["output"] = utils.normalize_log_string(
                    linter.stdout_human if linter.stdout_human else linter.stdout
                )
                # Number of files & errors
                linter_payload_data["cliLintMode"] = linter.cli_lint_mode
                if linter.cli_lint_mode != "project":
                    linter_payload_data["numberFilesFound"] = len(linter.files)
                linter_payload_data["numberErrorsFound"] = linter.total_number_errors
                if linter.disable_errors_if_less_than is not None:
                    linter_payload_data["maxErrorsAllowed"] = (
                        linter.disable_errors_if_less_than
                    )
                # Fixed cells
                if linter.try_fix is True:
                    linter_payload_data["numberErrorsFixed"] = linter.number_fixed
                # Elapsed time
                if self.master.show_elapsed_time is True:
                    linter_payload_data["elapsedTime"] = round(linter.elapsed_time_s, 2)
                # Rules & files breakdowns from SARIF output when available
                if include_details:
                    breakdowns = self.build_sarif_breakdowns(linter)
                    if breakdowns is not None:
                        linter_payload_data["rulesBreakdown"] = breakdowns["rules"]
                        linter_payload_data["filesBreakdown"] = breakdowns["files"]
                # Add to linters
                linter_payload["data"] = linter_payload_data
                self.payload["linters"].append(linter_payload)
        self.build_run_aggregates()

    def build_run_aggregates(self):
        blocking_errors = 0
        non_blocking_errors = 0
        total_fixed = 0
        files_analyzed = 0
        counts = {"success": 0, "warning": 0, "error": 0}
        for linter_payload in self.payload["linters"]:
            data = linter_payload["data"]
            counts[data["severity"]] += 1
            if data["severity"] == "error":
                blocking_errors += data["numberErrorsFound"]
            elif data["severity"] == "warning":
                non_blocking_errors += data["numberErrorsFound"]
            total_fixed += data.get("numberErrorsFixed", 0)
            files_analyzed = max(files_analyzed, data.get("numberFilesFound", 0))
        linters_count = len(self.payload["linters"])
        # Health score (0-100): linters in success count fully, warnings half, errors zero
        health_score = (
            round(
                100 * (counts["success"] + 0.5 * counts["warning"]) / linters_count, 1
            )
            if linters_count > 0
            else 100.0
        )
        self.payload["run"] = {
            "qualityGateStatus": "fail" if counts["error"] > 0 else "pass",
            "healthScore": health_score,
            "blockingErrors": blocking_errors,
            "nonBlockingErrors": non_blocking_errors,
            "totalErrors": blocking_errors + non_blocking_errors,
            "totalErrorsFixed": total_fixed,
            "lintersCount": linters_count,
            "lintersSuccess": counts["success"],
            "lintersWarning": counts["warning"],
            "lintersError": counts["error"],
            "filesAnalyzed": files_analyzed,
            "runDurationS": round(time.time() - self.init_time, 2),
        }

    def build_sarif_breakdowns(self, linter):
        sarif_file = linter.sarif_output_file
        if sarif_file is None or not os.path.isfile(sarif_file):
            return None
        try:
            with open(sarif_file, "r", encoding="utf-8") as f:
                sarif = json.load(f)
            rules: Counter = Counter()
            files: Counter = Counter()
            for run in sarif.get("runs", []):
                for result in run.get("results", []):
                    rule_id = result.get("ruleId", "unknown")
                    rules[rule_id] += 1
                    for location in result.get("locations", [])[:1]:
                        uri = (
                            location.get("physicalLocation", {})
                            .get("artifactLocation", {})
                            .get("uri", None)
                        )
                        if uri is not None:
                            files[uri] += 1
            return {
                "rules": [
                    {"ruleId": rule_id, "occurrences": count}
                    for rule_id, count in rules.most_common(TOP_BREAKDOWN_SIZE)
                ],
                "files": [
                    {"file": file, "occurrences": count}
                    for file, count in files.most_common(TOP_BREAKDOWN_SIZE)
                ],
            }
        except Exception as e:
            logging.debug(f"[Api Reporter] Unable to parse SARIF for breakdowns: {e}")
            return None

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
