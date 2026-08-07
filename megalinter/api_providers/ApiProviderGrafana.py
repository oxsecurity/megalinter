#!/usr/bin/env python3
"""
Grafana / generic HTTP provider: posts logs to a Loki-compatible (or plain JSON)
endpoint and metrics to a Prometheus/Influx write endpoint.
Also handles the legacy NOTIF_API_* variables.
"""

import copy
import json
import logging
import time

import requests
from megalinter import config
from megalinter.api_providers.ApiProvider import ApiProvider

RUN_STREAM_LINTER_KEY = "MEGALINTER_RUN"
MAX_LOKI_LOG_LENGTH = 200000
TRUNCATE_LOKI_CHARS_LENGTH = 5000


class ApiProviderGrafana(ApiProvider):
    name = "grafana"

    api_url: str | None = None
    api_metrics_url: str | None = None
    payloadFormatted: dict = {}
    metrics_payload: str = ""

    def manage_activation(self) -> bool:
        self.api_url = config.get_first_var_set(
            self.request_id, ["API_REPORTER_URL", "NOTIF_API_URL"]
        )
        if self.api_url is None:
            logging.error(
                "[Api Reporter] [Grafana] You need to define API_REPORTER_URL to use ApiReporter"
            )
            return False
        return True

    def send(self) -> bool:
        self.format_payload()
        logs_ok = self.send_to_api()
        metrics_ok = True
        if config.exists(self.request_id, "API_REPORTER_METRICS_URL") or config.exists(
            self.request_id, "NOTIF_API_METRICS_URL"
        ):
            self.api_metrics_url = config.get_first_var_set(
                self.request_id,
                ["API_REPORTER_METRICS_URL", "NOTIF_API_METRICS_URL"],
            )
            self.build_metrics_payload()
            metrics_ok = self.send_to_metrics_api()
        return logs_ok and metrics_ok

    def format_payload(self):
        payload_format = config.get_first_var_set(
            self.request_id,
            ["API_REPORTER_PAYLOAD_FORMAT", "NOTIF_API_PAYLOAD_FORMAT"],
            "auto",
        ).lower()
        if payload_format == "loki" or (
            payload_format == "auto" and "loki/api/v1/push" in self.api_url
        ):
            self.format_payload_loki()
            return
        self.payloadFormatted = self.payload

    def format_payload_loki(self):
        time_ns = time.time_ns()
        streams = []
        # Run-level stream
        run_stream_info = copy.deepcopy(self.payload)
        del run_stream_info["data"]
        del run_stream_info["run"]
        del run_stream_info["linters"]
        del run_stream_info["timestamp"]
        # High-cardinality values must stay out of Loki labels
        del run_stream_info["runId"]
        del run_stream_info["jobUrl"]
        run_stream_info["linterKey"] = RUN_STREAM_LINTER_KEY
        run_stream_info["recordType"] = "run"
        run_values = {
            **self.payload["run"],
            "runId": self.payload["runId"],
            "jobUrl": self.payload["jobUrl"],
        }
        streams += [
            {
                "stream": self.stringify_labels(run_stream_info),
                "values": [[str(time_ns), json.dumps(run_values)]],
            }
        ]
        # One stream per linter (recordType=linter), plus rule/file breakdown streams
        for linter in self.payload["linters"]:
            stream_info = copy.deepcopy(run_stream_info)
            del stream_info["linterKey"]
            stream_info["recordType"] = "linter"
            linter_copy = copy.deepcopy(linter)
            del linter_copy["data"]
            stream_info.update(linter_copy)
            data = copy.deepcopy(linter["data"])
            data.update(self.payload["data"])
            rules_breakdown = data.pop("rulesBreakdown", None)
            files_breakdown = data.pop("filesBreakdown", None)
            # Truncate if too long
            payload_data_json = json.dumps(data)
            body_bytes_len = len(payload_data_json.encode("utf-8"))
            if body_bytes_len > MAX_LOKI_LOG_LENGTH:
                output: str = data["output"]
                data["output"] = output[:TRUNCATE_LOKI_CHARS_LENGTH] + "\n(truncated)"
            data["output"] = data["output"].splitlines()
            stream = {
                "stream": self.stringify_labels(stream_info),
                "values": [[str(time_ns), json.dumps(data)]],
            }
            streams.append(stream)
            # One line per rule / per file, in dedicated streams, so that
            # dashboards can aggregate them with simple queries
            for record_type, breakdown in [
                ("rule", rules_breakdown),
                ("file", files_breakdown),
            ]:
                if breakdown:
                    breakdown_stream_info = copy.deepcopy(stream_info)
                    breakdown_stream_info["recordType"] = record_type
                    streams.append(
                        {
                            "stream": self.stringify_labels(breakdown_stream_info),
                            "values": [
                                [str(time_ns), json.dumps(item)] for item in breakdown
                            ],
                        }
                    )
        self.payloadFormatted = {"streams": streams}

    def stringify_labels(self, stream_info: dict):
        return {key: str(value) for key, value in stream_info.items()}

    def build_session_and_headers(self, prefix):
        session = requests.Session()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        var_prefixes = [f"API_REPORTER{prefix}", f"NOTIF_API{prefix}"]
        basic_auth_username_vars = [f"{p}_BASIC_AUTH_USERNAME" for p in var_prefixes]
        basic_auth_password_vars = [f"{p}_BASIC_AUTH_PASSWORD" for p in var_prefixes]
        bearer_token_vars = [f"{p}_BEARER_TOKEN" for p in var_prefixes]
        if any(config.exists(self.request_id, var) for var in basic_auth_username_vars):
            session.auth = (
                config.get_first_var_set(self.request_id, basic_auth_username_vars),
                config.get_first_var_set(self.request_id, basic_auth_password_vars),
            )
            if self.is_debug():
                logging.info("[Api Reporter] [Grafana] Using Basic Auth")
        elif any(config.exists(self.request_id, var) for var in bearer_token_vars):
            bearer = config.get_first_var_set(self.request_id, bearer_token_vars)
            headers["Authorization"] = f"Bearer {bearer}"
            if self.is_debug():
                logging.info("[Api Reporter] [Grafana] Using Bearer Token")
        return session, headers

    def send_to_api(self) -> bool:
        session, headers = self.build_session_and_headers("")
        return self.post_raw(
            self.api_url,
            headers,
            json.dumps(self.payloadFormatted),
            "Grafana Logs",
            session=session,
        )

    # Influx line protocol (Grafana Cloud Prometheus/Influx write endpoint)
    # megalinter_run,<tags> qualityGate=1,blockingErrors=0,...
    # megalinter_linter_run,<tags>,linterKey=... numberErrorsFound=0,...
    def build_metrics_payload(self):
        metric_base_tags = ",".join(
            [
                f"{key}={self.escape_influx_tag(value)}"
                for key, value in self.base_tags_dict().items()
            ]
        )
        all_metrics_lines = []
        run_fields = self.run_metric_fields()
        run_fields_str = ",".join(
            [f"{name}={value}" for name, value in run_fields.items()]
        )
        run_tags = (
            metric_base_tags
            + f",megalinterVersion={self.escape_influx_tag(self.payload['megalinterVersion'])}"
            + f",megalinterFlavor={self.escape_influx_tag(self.payload['megalinterFlavor'])}"
        )
        all_metrics_lines += [f"megalinter_run,{run_tags} {run_fields_str}"]
        for linter_payload in self.payload["linters"]:
            linter_tags = (
                metric_base_tags
                + f",descriptor={self.escape_influx_tag(linter_payload['descriptor'])}"
                + f",linter={self.escape_influx_tag(linter_payload['linter'])}"
                + f",linterKey={self.escape_influx_tag(linter_payload['linterKey'])}"
            )
            linter_fields = self.linter_metric_fields(linter_payload)
            linter_fields_str = ",".join(
                [f"{name}={value}" for name, value in linter_fields.items()]
            )
            all_metrics_lines += [
                f"megalinter_linter_run,{linter_tags} {linter_fields_str}"
            ]
        self.metrics_payload = "\n".join(all_metrics_lines)

    def escape_influx_tag(self, value):
        return str(value).replace(",", "\\,").replace("=", "\\=").replace(" ", "\\ ")

    def send_to_metrics_api(self) -> bool:
        session, headers = self.build_session_and_headers("_METRICS")
        return self.post_raw(
            self.api_metrics_url,
            headers,
            self.metrics_payload,
            "Grafana Metrics",
            session=session,
        )
