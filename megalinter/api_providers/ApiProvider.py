#!/usr/bin/env python3
"""
Base class for ApiReporter observability providers.
Child classes (ApiProviderGrafana, ApiProviderDatadog, ApiProviderElastic,
ApiProviderNewRelic) send the ApiReporter v2 payload to their backend.
"""

import json
import logging

import requests
from megalinter import config

MAX_OUTPUT_CHARS = 5000


class ApiProvider:
    name: str = ""
    request_id: str | None = None
    payload: dict = {}

    def __init__(self, request_id=None):
        self.request_id = request_id

    # Return True when the provider configuration is usable (log errors otherwise)
    def manage_activation(self) -> bool:
        return False

    # Send self.payload to the backend, return True on success
    def send(self) -> bool:
        return False

    def is_debug(self):
        return (
            config.get_first_var_set(
                self.request_id, ["API_REPORTER_DEBUG", "NOTIF_API_DEBUG"]
            )
            == "true"
        )

    def post_json(self, url, headers, body, label):
        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            if 200 <= response.status_code < 300:
                logging.info(
                    f"[Api Reporter] [{label}] Successfully posted data to {url}"
                )
                if self.is_debug():
                    logging.info(
                        f"[Api Reporter] [{label}] " + json.dumps(body, indent=1)
                    )
                return True
            logging.warning(
                f"[Api Reporter] [{label}] Error posting data to {url} ({response.status_code})\n"
                f"[Api Reporter] [{label}] API response: {response.text}"
            )
        except Exception as e:
            logging.warning(
                f"[Api Reporter] [{label}] Error posting data to {url}: {str(e)}"
            )
        return False

    def post_raw(self, url, headers, data, label, session=None):
        try:
            requester = session if session is not None else requests
            response = requester.post(url, headers=headers, data=data, timeout=30)
            if 200 <= response.status_code < 300:
                logging.info(
                    f"[Api Reporter] [{label}] Successfully posted data to {url}"
                )
                if self.is_debug():
                    logging.info(f"[Api Reporter] [{label}] " + str(data))
                return True
            logging.warning(
                f"[Api Reporter] [{label}] Error posting data to {url} ({response.status_code})\n"
                f"[Api Reporter] [{label}] API response: {response.text}"
            )
        except Exception as e:
            logging.warning(
                f"[Api Reporter] [{label}] Error posting data to {url}: {str(e)}"
            )
        return False

    def base_tags_dict(self):
        return {
            "source": self.payload["source"],
            "orgIdentifier": self.payload["orgIdentifier"],
            "gitIdentifier": self.payload["gitIdentifier"],
            "gitRepoName": self.payload["gitRepoName"],
            "gitBranchName": self.payload["gitBranchName"],
        }

    def run_metric_fields(self):
        run = self.payload["run"]
        return {
            "qualityGate": 1 if run["qualityGateStatus"] == "pass" else 0,
            "healthScore": run["healthScore"],
            "blockingErrors": run["blockingErrors"],
            "nonBlockingErrors": run["nonBlockingErrors"],
            "totalErrors": run["totalErrors"],
            "totalErrorsFixed": run["totalErrorsFixed"],
            "lintersCount": run["lintersCount"],
            "lintersSuccess": run["lintersSuccess"],
            "lintersWarning": run["lintersWarning"],
            "lintersError": run["lintersError"],
            "filesAnalyzed": run["filesAnalyzed"],
            "runDurationS": run["runDurationS"],
        }

    def linter_metric_fields(self, linter_payload):
        data = linter_payload["data"]
        fields = {
            "numberErrorsFound": data["numberErrorsFound"],
            "blocking": 1 if data.get("blocking") is True else 0,
        }
        if "numberFilesFound" in data:
            fields["numberFilesFound"] = data["numberFilesFound"]
        if "numberErrorsFixed" in data:
            fields["numberErrorsFixed"] = data["numberErrorsFixed"]
        if "elapsedTime" in data:
            fields["elapsedTime"] = data["elapsedTime"]
        return fields

    def truncated_output(self, data):
        output = data.get("output", "")
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + "\n(truncated)"
        return output

    # Returns [linter_payload data without breakdowns, rules breakdown, files breakdown]
    def split_linter_data(self, linter_payload):
        data = dict(linter_payload["data"])
        data["output"] = self.truncated_output(data)
        rules_breakdown = data.pop("rulesBreakdown", None)
        files_breakdown = data.pop("filesBreakdown", None)
        return data, rules_breakdown, files_breakdown
