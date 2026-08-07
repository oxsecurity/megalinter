#!/usr/bin/env python3
"""
Unit tests for ApiReporter payload v2 and its ApiProvider classes
(Grafana, Datadog, Elastic, New Relic), with mocked HTTP calls
"""

import json
import os
import sys
import tempfile
import types
import unittest
import uuid

from megalinter import config
from megalinter.reporters.ApiReporter import ApiReporter

SARIF_SAMPLE = {
    "runs": [
        {
            "results": [
                {
                    "ruleId": "E501",
                    "locations": [
                        {"physicalLocation": {"artifactLocation": {"uri": "src/a.py"}}}
                    ],
                },
                {
                    "ruleId": "E501",
                    "locations": [
                        {"physicalLocation": {"artifactLocation": {"uri": "src/b.py"}}}
                    ],
                },
                {
                    "ruleId": "F401",
                    "locations": [
                        {"physicalLocation": {"artifactLocation": {"uri": "src/a.py"}}}
                    ],
                },
            ]
        }
    ]
}


def fake_linter(
    descriptor, name, key, status, return_code, errors, fixed=None, sarif=None
):
    linter = types.SimpleNamespace()
    linter.is_active = True
    linter.descriptor_id = descriptor
    linter.linter_name = name
    linter.name = key
    linter.status = status
    linter.return_code = return_code
    linter.stdout_human = f"output of {key}\nline2"
    linter.stdout = linter.stdout_human
    linter.cli_lint_mode = "list_of_files"
    linter.files = ["src/a.py", "src/b.py"]
    linter.total_number_errors = errors
    linter.disable_errors_if_less_than = None
    linter.try_fix = fixed is not None
    linter.number_fixed = fixed or 0
    linter.elapsed_time_s = 12.345
    linter.sarif_output_file = sarif
    linter.is_formatter = False
    return linter


class FakeSession:
    def __init__(self, captured):
        self.auth = None
        self.captured = captured

    def post(self, url, headers=None, json=None, data=None, timeout=None):
        self.captured.append(
            {"url": url, "headers": headers, "json": json, "data": data}
        )
        return types.SimpleNamespace(status_code=200, text="ok")


class api_reporter_v2_test(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        self.captured = []
        self.sarif_path = os.path.join(
            tempfile.gettempdir(), f"megalinter-sarif-{self.request_id}.sarif"
        )
        with open(self.sarif_path, "w", encoding="utf-8") as f:
            json.dump(SARIF_SAMPLE, f)
        captured = self.captured

        def fake_post(url, headers=None, json=None, data=None, timeout=None):
            captured.append(
                {"url": url, "headers": headers, "json": json, "data": data}
            )
            return types.SimpleNamespace(status_code=200, text="ok")

        fake_requests = types.SimpleNamespace(
            post=fake_post, Session=lambda: FakeSession(captured)
        )
        self.patched_modules = [
            sys.modules["megalinter.api_providers.ApiProvider"],
            sys.modules["megalinter.api_providers.ApiProviderGrafana"],
        ]
        self.real_requests = [module.requests for module in self.patched_modules]
        for module in self.patched_modules:
            module.requests = fake_requests

    def tearDown(self):
        for module, real in zip(self.patched_modules, self.real_requests):
            module.requests = real
        if os.path.isfile(self.sarif_path):
            os.remove(self.sarif_path)
        config.delete(self.request_id)

    def build_master(self):
        master = types.SimpleNamespace()
        master.request_id = self.request_id
        master.github_workspace = "."
        master.show_elapsed_time = True
        master.megalinter_flavor = "python"
        master.linters = [
            fake_linter(
                "PYTHON", "ruff", "PYTHON_RUFF", "error", 1, 12, sarif=self.sarif_path
            ),
            fake_linter("PYTHON", "black", "PYTHON_BLACK", "success", 0, 0, fixed=3),
            fake_linter(
                "MARKDOWN", "markdownlint", "MARKDOWN_MARKDOWNLINT", "warning", 0, 4
            ),
        ]
        return master

    def init_reporter(self, extra_config=None):
        config.init_config(
            self.request_id,
            None,
            {
                "API_REPORTER": "true",
                "API_REPORTER_PROVIDER": "grafana,datadog,elastic,newrelic",
                "API_REPORTER_URL": "https://fake-loki/loki/api/v1/push",
                "API_REPORTER_METRICS_URL": "https://fake-influx/api/v1/push/influx/write",
                "API_REPORTER_DATADOG_SITE": "datadoghq.eu",
                "API_REPORTER_DATADOG_BEARER_TOKEN": "xxx",
                "API_REPORTER_ELASTIC_URL": "https://elastic.example.com",
                "API_REPORTER_ELASTIC_API_KEY": "yyy",
                "API_REPORTER_NEWRELIC_LICENSE_KEY": "zzz",
                "API_REPORTER_NEWRELIC_REGION": "EU",
                "GITHUB_REPOSITORY": "oxsecurity/megalinter-tests",
                **(extra_config or {}),
            },
        )
        return ApiReporter({"master": self.build_master(), "report_folder": "."})

    def test_payload_v2_run_aggregates(self):
        reporter = self.init_reporter()
        self.assertTrue(reporter.is_active)
        self.assertEqual(
            ["grafana", "datadog", "elastic", "newrelic"],
            [provider.name for provider in reporter.providers],
        )
        reporter.build_payload()
        run = reporter.payload["run"]
        self.assertEqual(2, reporter.payload["payloadVersion"])
        self.assertEqual("fail", run["qualityGateStatus"])
        # 1 success + 0.5 * 1 warning out of 3 linters = 50.0
        self.assertEqual(50.0, run["healthScore"])
        self.assertEqual(12, run["blockingErrors"])
        self.assertEqual(4, run["nonBlockingErrors"])
        self.assertEqual(16, run["totalErrors"])
        self.assertEqual(3, run["totalErrorsFixed"])
        self.assertEqual(3, run["lintersCount"])
        self.assertEqual(1, run["lintersError"])

    def test_sarif_breakdowns(self):
        reporter = self.init_reporter()
        reporter.build_payload()
        data = reporter.payload["linters"][0]["data"]
        self.assertEqual(
            [
                {"ruleId": "E501", "occurrences": 2},
                {"ruleId": "F401", "occurrences": 1},
            ],
            data["rulesBreakdown"],
        )
        self.assertEqual(
            [
                {"file": "src/a.py", "occurrences": 2},
                {"file": "src/b.py", "occurrences": 1},
            ],
            data["filesBreakdown"],
        )

    def test_providers_send(self):
        reporter = self.init_reporter()
        reporter.produce_report()
        urls = [post["url"] for post in self.captured]
        self.assertEqual(
            [
                "https://fake-loki/loki/api/v1/push",
                "https://fake-influx/api/v1/push/influx/write",
                "https://http-intake.logs.datadoghq.eu/api/v2/logs",
                "https://api.datadoghq.eu/api/v2/series",
                "https://elastic.example.com/_bulk",
                "https://log-api.eu.newrelic.com/log/v1",
                "https://metric-api.eu.newrelic.com/metric/v1",
            ],
            urls,
        )
        # Loki streams: run + linters + rule/file breakdowns, low-cardinality labels
        loki_payload = json.loads(self.captured[0]["data"])
        record_types = {
            stream["stream"]["recordType"] for stream in loki_payload["streams"]
        }
        self.assertEqual({"run", "linter", "rule", "file"}, record_types)
        for stream in loki_payload["streams"]:
            self.assertNotIn("runId", stream["stream"])
            self.assertNotIn("jobUrl", stream["stream"])
        # Metrics: v2 measurements, with version/flavor tags on the run series
        metrics_lines = self.captured[1]["data"].splitlines()
        self.assertTrue(metrics_lines[0].startswith("megalinter_run,"))
        self.assertIn("megalinterVersion=", metrics_lines[0])
        self.assertIn("megalinterFlavor=python", metrics_lines[0])
        for line in metrics_lines[1:]:
            self.assertTrue(line.startswith("megalinter_linter_run,"))
        dd_series = self.captured[3]["json"]["series"]
        run_series = [
            series_entry
            for series_entry in dd_series
            if series_entry["metric"].startswith("megalinter.run.")
        ]
        self.assertTrue(
            all(
                any(
                    tag.startswith("megalinter_version:")
                    for tag in series_entry["tags"]
                )
                for series_entry in run_series
            )
        )
        # Datadog: snake_case tags + rule events
        dd_events = self.captured[2]["json"]
        self.assertTrue(
            any(",record_type:rule" in event["ddtags"] for event in dd_events)
        )
        self.assertTrue(all("git_repo_name:" in event["ddtags"] for event in dd_events))
        # Elastic: rule & file documents indexed
        bulk = self.captured[4]["data"].decode()
        self.assertIn('"_index": "megalinter-rules"', bulk)
        self.assertIn('"_index": "megalinter-files"', bulk)
        # New Relic: rule logs with occurrences attribute
        nr_logs = self.captured[5]["json"][0]["logs"]
        self.assertTrue(
            any(log["attributes"].get("recordType") == "rule" for log in nr_logs)
        )

    def test_inactive_without_variable(self):
        config.init_config(self.request_id, None, {})
        reporter = ApiReporter({"master": self.build_master(), "report_folder": "."})
        self.assertFalse(reporter.is_active)

    def test_unknown_provider_ignored(self):
        reporter = self.init_reporter(
            {"API_REPORTER_PROVIDER": "grafana,invalid_provider"}
        )
        self.assertTrue(reporter.is_active)
        self.assertEqual(
            ["grafana"], [provider.name for provider in reporter.providers]
        )
