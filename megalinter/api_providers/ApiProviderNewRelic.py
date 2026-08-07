#!/usr/bin/env python3
"""
New Relic provider: posts logs to the Log API and metrics to the Metric API.
https://docs.newrelic.com/docs/logs/log-api/introduction-log-api/
https://docs.newrelic.com/docs/data-apis/ingest-apis/metric-api/
"""

import json
import logging
import time

from megalinter import config
from megalinter.api_providers.ApiProvider import ApiProvider

NEWRELIC_ENDPOINTS = {
    "US": {
        "logs": "https://log-api.newrelic.com/log/v1",
        "metrics": "https://metric-api.newrelic.com/metric/v1",
    },
    "EU": {
        "logs": "https://log-api.eu.newrelic.com/log/v1",
        "metrics": "https://metric-api.eu.newrelic.com/metric/v1",
    },
}


class ApiProviderNewRelic(ApiProvider):
    name = "newrelic"

    endpoints: dict = NEWRELIC_ENDPOINTS["US"]
    headers: dict = {}

    def manage_activation(self) -> bool:
        license_key = config.get(
            self.request_id, "API_REPORTER_NEWRELIC_LICENSE_KEY", None
        )
        if license_key is None:
            logging.error(
                "[Api Reporter] [New Relic] Define API_REPORTER_NEWRELIC_LICENSE_KEY "
                "to use the newrelic provider"
            )
            return False
        region = config.get(self.request_id, "API_REPORTER_NEWRELIC_REGION", "US")
        self.endpoints = NEWRELIC_ENDPOINTS.get(
            region.upper(), NEWRELIC_ENDPOINTS["US"]
        )
        self.headers = {"content-type": "application/json", "Api-Key": license_key}
        return True

    def send(self) -> bool:
        now_ms = int(time.time() * 1000)
        # runId is a logs-only attribute: it must never tag metrics
        # (unbounded cardinality)
        logs_attributes = {**self.base_tags_dict(), "runId": self.payload["runId"]}
        logs_ok = self.send_logs(now_ms, logs_attributes)
        metrics_ok = self.send_metrics(now_ms, self.base_tags_dict())
        return logs_ok and metrics_ok

    def send_logs(self, now_ms, common_attributes) -> bool:
        logs = [
            {
                "timestamp": now_ms,
                "message": (
                    f"MegaLinter run {self.payload['run']['qualityGateStatus']}: "
                    f"{self.payload['run']['totalErrors']} errors"
                ),
                "attributes": {
                    "recordType": "run",
                    "megalinter": {**self.payload, "linters": None},
                },
            }
        ]
        for linter_payload in self.payload["linters"]:
            data, rules_breakdown, files_breakdown = self.split_linter_data(
                linter_payload
            )
            logs += [
                {
                    "timestamp": now_ms,
                    "message": (
                        f"[{linter_payload['linterKey']}] {data['severity']}: "
                        f"{data['numberErrorsFound']} errors"
                    ),
                    "attributes": {
                        "recordType": "linter",
                        "linterKey": linter_payload["linterKey"],
                        "descriptor": linter_payload["descriptor"],
                        "megalinter": {**linter_payload, "data": data},
                    },
                }
            ]
            for record_type, breakdown in [
                ("rule", rules_breakdown),
                ("file", files_breakdown),
            ]:
                for item in breakdown or []:
                    logs += [
                        {
                            "timestamp": now_ms,
                            "message": f"[{linter_payload['linterKey']}] {record_type}: "
                            + json.dumps(item),
                            "attributes": {
                                "recordType": record_type,
                                "linterKey": linter_payload["linterKey"],
                                "descriptor": linter_payload["descriptor"],
                                **item,
                            },
                        }
                    ]
        return self.post_json(
            self.endpoints["logs"],
            self.headers,
            [{"common": {"attributes": common_attributes}, "logs": logs}],
            "New Relic Logs",
        )

    def send_metrics(self, now_ms, common_attributes) -> bool:
        metrics = []
        run_attributes = {
            "megalinterVersion": self.payload["megalinterVersion"],
            "megalinterFlavor": self.payload["megalinterFlavor"],
        }
        for name, value in self.run_metric_fields().items():
            metrics += [
                {
                    "name": f"megalinter.run.{name}",
                    "type": "gauge",
                    "value": value,
                    "timestamp": now_ms,
                    "attributes": run_attributes,
                }
            ]
        for linter_payload in self.payload["linters"]:
            linter_attributes = {
                "descriptor": linter_payload["descriptor"],
                "linter": linter_payload["linter"],
                "linterKey": linter_payload["linterKey"],
            }
            for name, value in self.linter_metric_fields(linter_payload).items():
                metrics += [
                    {
                        "name": f"megalinter.linter.{name}",
                        "type": "gauge",
                        "value": value,
                        "timestamp": now_ms,
                        "attributes": linter_attributes,
                    }
                ]
        return self.post_json(
            self.endpoints["metrics"],
            self.headers,
            [{"common": {"attributes": common_attributes}, "metrics": metrics}],
            "New Relic Metrics",
        )
