#!/usr/bin/env python3
"""
Elastic provider: indexes run/linter/rule/file documents with the bulk API.
https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
"""

import json
import logging

from megalinter import config
from megalinter.api_providers.ApiProvider import ApiProvider


class ApiProviderElastic(ApiProvider):
    name = "elastic"

    url: str | None = None
    index_prefix: str = "megalinter"
    headers: dict = {}

    def manage_activation(self) -> bool:
        self.url = config.get(self.request_id, "API_REPORTER_ELASTIC_URL", None)
        if self.url is None:
            logging.error(
                "[Api Reporter] [Elastic] Define API_REPORTER_ELASTIC_URL "
                "to use the elastic provider"
            )
            return False
        self.index_prefix = config.get(
            self.request_id, "API_REPORTER_ELASTIC_INDEX_PREFIX", "megalinter"
        )
        self.headers = {"content-type": "application/x-ndjson"}
        api_key = config.get(self.request_id, "API_REPORTER_ELASTIC_API_KEY", None)
        if api_key is not None:
            self.headers["Authorization"] = f"ApiKey {api_key}"
        return True

    def send(self) -> bool:
        timestamp = self.payload["timestamp"]
        base_tags = self.base_tags_dict()
        bulk_lines = []
        run_doc = {**self.payload, "linters": None, "@timestamp": timestamp}
        bulk_lines += [
            json.dumps({"index": {"_index": f"{self.index_prefix}-runs"}}),
            json.dumps(run_doc),
        ]
        for linter_payload in self.payload["linters"]:
            data, rules_breakdown, files_breakdown = self.split_linter_data(
                linter_payload
            )
            linter_doc = {
                **base_tags,
                **linter_payload,
                "data": data,
                "runId": self.payload["runId"],
                "@timestamp": timestamp,
            }
            bulk_lines += [
                json.dumps({"index": {"_index": f"{self.index_prefix}-linters"}}),
                json.dumps(linter_doc),
            ]
            for record_type, breakdown in [
                ("rules", rules_breakdown),
                ("files", files_breakdown),
            ]:
                for item in breakdown or []:
                    bulk_lines += [
                        json.dumps(
                            {"index": {"_index": f"{self.index_prefix}-{record_type}"}}
                        ),
                        json.dumps(
                            {
                                **base_tags,
                                "linterKey": linter_payload["linterKey"],
                                "descriptor": linter_payload["descriptor"],
                                **item,
                                "runId": self.payload["runId"],
                                "@timestamp": timestamp,
                            }
                        ),
                    ]
        bulk_body = "\n".join(bulk_lines) + "\n"
        return self.post_raw(
            (self.url or "").rstrip("/") + "/_bulk",
            self.headers,
            bulk_body.encode("utf-8"),
            "Elastic",
        )
