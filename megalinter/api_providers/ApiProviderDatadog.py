#!/usr/bin/env python3
"""
Datadog provider: posts logs to the HTTP logs intake and metrics to the
metrics series API.
https://docs.datadoghq.com/api/latest/logs/
https://docs.datadoghq.com/api/latest/metrics/
"""

import json
import logging
import time

from megalinter import config
from megalinter.api_providers.ApiProvider import ApiProvider

DATADOG_DEFAULT_SITE = "datadoghq.com"


class ApiProviderDatadog(ApiProvider):
    name = "datadog"

    site: str = DATADOG_DEFAULT_SITE
    headers: dict = {}

    def manage_activation(self) -> bool:
        self.site = config.get(
            self.request_id, "API_REPORTER_DATADOG_SITE", DATADOG_DEFAULT_SITE
        )
        api_key = config.get(self.request_id, "API_REPORTER_DATADOG_API_KEY", None)
        bearer_token = config.get(
            self.request_id, "API_REPORTER_DATADOG_BEARER_TOKEN", None
        )
        if api_key is None and bearer_token is None:
            logging.error(
                "[Api Reporter] [Datadog] Define API_REPORTER_DATADOG_API_KEY "
                "(or API_REPORTER_DATADOG_BEARER_TOKEN) to use the datadog provider"
            )
            return False
        self.headers = {"content-type": "application/json"}
        if api_key is not None:
            self.headers["DD-API-KEY"] = api_key
        else:
            self.headers["Authorization"] = f"Bearer {bearer_token}"
        return True

    # Datadog lowercases tag keys: use snake_case explicitly so queries are predictable
    def datadog_tags_dict(self):
        return {
            "source": self.payload["source"],
            "org_identifier": self.payload["orgIdentifier"],
            "git_identifier": self.payload["gitIdentifier"],
            "git_repo_name": self.payload["gitRepoName"],
            "git_branch_name": self.payload["gitBranchName"],
        }

    def send(self) -> bool:
        logs_ok = self.send_logs()
        metrics_ok = self.send_metrics()
        return logs_ok and metrics_ok

    def send_logs(self) -> bool:
        tags = self.datadog_tags_dict()
        dd_tags_base = ",".join([f"{key}:{value}" for key, value in tags.items()])
        events = [
            {
                "ddsource": "megalinter",
                "ddtags": dd_tags_base + ",record_type:run",
                "service": "megalinter",
                "hostname": self.payload["gitRepoName"],
                "message": (
                    f"MegaLinter run {self.payload['run']['qualityGateStatus']}: "
                    f"{self.payload['run']['totalErrors']} errors"
                ),
                "megalinter": {**self.payload, "linters": None},
            }
        ]
        for linter_payload in self.payload["linters"]:
            data, rules_breakdown, files_breakdown = self.split_linter_data(
                linter_payload
            )
            linter_tags = (
                dd_tags_base
                + f",linter_key:{linter_payload['linterKey']}"
                + f",descriptor:{linter_payload['descriptor']}"
            )
            events += [
                {
                    "ddsource": "megalinter",
                    "ddtags": linter_tags + ",record_type:linter",
                    "service": "megalinter",
                    "hostname": self.payload["gitRepoName"],
                    "message": (
                        f"[{linter_payload['linterKey']}] {data['severity']}: "
                        f"{data['numberErrorsFound']} errors"
                    ),
                    "megalinter": {**linter_payload, "data": data},
                }
            ]
            for record_type, breakdown in [
                ("rule", rules_breakdown),
                ("file", files_breakdown),
            ]:
                for item in breakdown or []:
                    events += [
                        {
                            "ddsource": "megalinter",
                            "ddtags": linter_tags + f",record_type:{record_type}",
                            "service": "megalinter",
                            "hostname": self.payload["gitRepoName"],
                            "message": f"[{linter_payload['linterKey']}] {record_type}: "
                            + json.dumps(item),
                            "megalinter": {
                                "linterKey": linter_payload["linterKey"],
                                "descriptor": linter_payload["descriptor"],
                                **item,
                            },
                        }
                    ]
        return self.post_json(
            f"https://http-intake.logs.{self.site}/api/v2/logs",
            self.headers,
            events,
            "Datadog Logs",
        )

    def send_metrics(self) -> bool:
        now = int(time.time())
        tag_list = [f"{key}:{value}" for key, value in self.datadog_tags_dict().items()]
        run_tag_list = tag_list + [
            f"megalinter_version:{self.payload['megalinterVersion']}",
            f"megalinter_flavor:{self.payload['megalinterFlavor']}",
        ]
        series = []
        for name, value in self.run_metric_fields().items():
            series += [
                {
                    "metric": f"megalinter.run.{name}",
                    "type": 3,
                    "points": [{"timestamp": now, "value": value}],
                    "tags": run_tag_list,
                }
            ]
        for linter_payload in self.payload["linters"]:
            linter_tags = tag_list + [
                f"descriptor:{linter_payload['descriptor']}",
                f"linter:{linter_payload['linter']}",
                f"linter_key:{linter_payload['linterKey']}",
            ]
            for name, value in self.linter_metric_fields(linter_payload).items():
                series += [
                    {
                        "metric": f"megalinter.linter.{name}",
                        "type": 3,
                        "points": [{"timestamp": now, "value": value}],
                        "tags": linter_tags,
                    }
                ]
        return self.post_json(
            f"https://api.{self.site}/api/v2/series",
            self.headers,
            {"series": series},
            "Datadog Metrics",
        )
