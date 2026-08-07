#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""

import glob
import logging
import os
import re
import tempfile
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

import requests
from megalinter import Linter, MegaLinter, utils_reporter, utils_sarif, utilstest
from megalinter.constants import DEFAULT_SARIF_REPORT_FILE_NAME
from megalinter.reporters.SarifReporter import SarifReporter

root = (
    os.path.dirname(os.path.abspath(__file__))
    + os.path.sep
    + ".."
    + os.path.sep
    + ".."
    + os.path.sep
    + ".."
)

# Public echo endpoints used to check that ApiReporter really posts data.
# They are tried in order, so that a single unavailable remote server does not
# fail the test: such an outage is not a MegaLinter issue
API_REPORTER_TEST_LOGS_URLS = [
    "https://jsonplaceholder.typicode.com/posts",
    "https://postman-echo.com/post",
    "https://httpbingo.org/anything",
    "https://httpbin.org/anything",
]
# Metrics are posted as Prometheus/Influx plain text, so only endpoints accepting
# a non-JSON body can be used here
API_REPORTER_TEST_METRICS_URLS = [
    "https://httpbin.org/anything",
    "https://postman-echo.com/post",
    "https://echo.free.beeceptor.com",
]
API_REPORTER_TEST_MAX_ATTEMPTS = 3
API_REPORTER_TEST_TIMEOUT_S = 10
# ApiReporter logs a failed post as "Error posting data to <url> (<status>)", which
# lets the test tell a remote-side outage (5xx) from an actual MegaLinter problem
API_REPORTER_ERROR_REGEX = re.compile(
    r"\[Api Reporter\](?: \[[^\]]+\])? Error posting data to \S+ \((?P<status>\d{3})\)"
)


class mega_linter_3_sarif_test(unittest.TestCase):
    def before_start(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {
                "request_id": self.request_id,
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_sarif",
            }
        )

    def test_sarif_output(self):
        self.before_start()
        mega_linter, output = utilstest.call_mega_linter(
            {
                "APPLY_FIXES": "false",
                "LOG_LEVEL": "DEBUG",
                "MULTI_STATUS": "false",
                "ENABLE_LINTERS": "JAVASCRIPT_ES,PYTHON_BANDIT",
                "SARIF_REPORTER": "true",
                "request_id": self.request_id,
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        expected_output_file = (
            mega_linter.report_folder + os.path.sep + DEFAULT_SARIF_REPORT_FILE_NAME
        )
        self.assertTrue(
            os.path.isfile(expected_output_file),
            "Output aggregated SARIF file " + expected_output_file + " should exist",
        )

    def test_sarif_fix(self):
        self.before_start()
        # Create megalinter
        mega_linter = MegaLinter.Megalinter({"request_id": uuid.uuid1()})
        # Create sample linters
        sarif_dir = (
            root
            + f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sarif_reports"
        )
        sarif_dir_absolute = os.path.realpath(sarif_dir)
        for sarif_file in glob.glob(f"{sarif_dir_absolute}{os.path.sep}*.sarif"):
            # Create linter
            linter = Linter(None, {})
            linter.name = "SAMPLE_" + os.path.basename(sarif_file)
            linter.can_output_sarif = True
            linter.sarif_output_file = sarif_file
            mega_linter.linters += [linter]

        # Create reporter
        tmp_report_folder = tempfile.gettempdir() + os.path.sep + str(uuid.uuid4())
        os.makedirs(tmp_report_folder)
        reporter = SarifReporter(
            {"master": mega_linter, "report_folder": tmp_report_folder}
        )
        # Produce report
        reporter.produce_report()
        expected_output_file = (
            tmp_report_folder + os.path.sep + DEFAULT_SARIF_REPORT_FILE_NAME
        )
        self.assertTrue(
            os.path.isfile(expected_output_file),
            "Output aggregated SARIF file " + expected_output_file + " should exist",
        )

    def test_sarif_fix_removes_empty_artifact_changes(self):
        linter = SimpleNamespace(
            name="BASH_SHELLCHECK", get_linter_version=lambda: "0.11.0"
        )
        valid_fix = {
            "artifactChanges": [
                {
                    "artifactLocation": {"uri": "test.sh"},
                    "replacements": [],
                }
            ]
        }
        sarif = {
            "runs": [
                {
                    "results": [
                        {
                            "fixes": [
                                {"artifactChanges": []},
                                valid_fix,
                            ]
                        },
                        {"fixes": [{"description": {"text": "["}}]},
                    ]
                }
            ]
        }

        with patch(
            "megalinter.utils_sarif.get_linter_doc_url",
            return_value="https://megalinter.io/",
        ):
            fixed_sarif = utils_sarif.fix_sarif(sarif, linter)

        self.assertEqual(fixed_sarif["runs"][0]["results"][0]["fixes"], [valid_fix])
        self.assertNotIn("fixes", fixed_sarif["runs"][0]["results"][1])

    # Keep only the endpoints that are currently up and accept the same kind of body
    # than ApiReporter, so a remote outage does not make the test fail.
    # Stops as soon as enough endpoints have been collected
    @staticmethod
    def find_available_api_endpoints(candidate_urls, max_endpoints, payload_kwargs):
        available_urls = []
        for candidate_url in candidate_urls:
            try:
                response = requests.post(
                    candidate_url,
                    headers={
                        "accept": "application/json",
                        "content-type": "application/json",
                    },
                    timeout=API_REPORTER_TEST_TIMEOUT_S,
                    **payload_kwargs,
                )
                if 200 <= response.status_code < 300:
                    available_urls += [candidate_url]
                else:
                    logging.warning(
                        f"[Api Reporter Test] {candidate_url} is not usable "
                        f"(HTTP {response.status_code})"
                    )
            except Exception as e:
                logging.warning(
                    f"[Api Reporter Test] {candidate_url} is not reachable: {str(e)}"
                )
            if len(available_urls) >= max_endpoints:
                break
        return available_urls

    def test_api_output(self):
        logs_probe_payload = {"json": {"source": "MegaLinter", "check": "availability"}}
        metrics_probe_payload = {
            "data": "megalinter_availability_check,source=MegaLinter check=1"
        }
        logs_urls = self.find_available_api_endpoints(
            API_REPORTER_TEST_LOGS_URLS,
            API_REPORTER_TEST_MAX_ATTEMPTS,
            logs_probe_payload,
        )
        metrics_urls = self.find_available_api_endpoints(
            API_REPORTER_TEST_METRICS_URLS,
            API_REPORTER_TEST_MAX_ATTEMPTS,
            metrics_probe_payload,
        )
        if len(logs_urls) == 0 or len(metrics_urls) == 0:
            raise unittest.SkipTest(
                "None of the public test API endpoints is available "
                f"(logs: {API_REPORTER_TEST_LOGS_URLS}, "
                f"metrics: {API_REPORTER_TEST_METRICS_URLS}). "
                "This is a remote servers issue, not a MegaLinter one"
            )
        # Retry with other remote servers if the post fails, to be sure that a
        # failure really comes from MegaLinter code and not from a flaky endpoint
        nb_attempts = min(
            API_REPORTER_TEST_MAX_ATTEMPTS, max(len(logs_urls), len(metrics_urls))
        )
        failures = []
        used_logs_urls = []
        used_metrics_urls = []
        attempt_outputs = []
        logs_ko = False
        metrics_ko = False
        for attempt in range(nb_attempts):
            logs_url = logs_urls[min(attempt, len(logs_urls) - 1)]
            metrics_url = metrics_urls[min(attempt, len(metrics_urls) - 1)]
            if logs_url not in used_logs_urls:
                used_logs_urls += [logs_url]
            if metrics_url not in used_metrics_urls:
                used_metrics_urls += [metrics_url]
            self.before_start()
            mega_linter, output = utilstest.call_mega_linter(
                {
                    "APPLY_FIXES": "false",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "ENABLE_LINTERS": "JAVASCRIPT_ES,PYTHON_BANDIT",
                    "API_REPORTER": "true",
                    "API_REPORTER_URL": logs_url,
                    "API_REPORTER_PAYLOAD_FORMAT": "loki",
                    "API_REPORTER_METRICS_URL": metrics_url,
                    "API_REPORTER_DEBUG": "true",
                    "request_id": self.request_id,
                }
            )
            attempt_outputs += [output]
            self.assertTrue(
                len(mega_linter.linters) > 0, "Linters have been created and run"
            )
            attempt_failures = []
            logs_ko = (
                "[Api Reporter] [Grafana Logs] Successfully posted data" not in output
            )
            metrics_ko = (
                "[Api Reporter] [Grafana Metrics] Successfully posted data"
                not in output
            )
            if logs_ko:
                attempt_failures += [
                    f"Api Reporter failed to post message to {logs_url}"
                ]
            if metrics_ko:
                attempt_failures += [
                    f"Api Reporter Metrics failed to post message to {metrics_url}"
                ]
            if len(attempt_failures) == 0:
                return
            failures += attempt_failures
            logging.warning(
                "[Api Reporter Test] Attempt "
                f"{attempt + 1}/{nb_attempts} failed: {attempt_failures}"
            )
        # A 5xx or a connection error means the endpoint failed on its own side, so
        # there is nothing for MegaLinter to fix. Decide from what the reporter logged
        # during the run rather than by re-probing: a flaky endpoint often answers
        # again moments later, which would hide a real outage behind a red test.
        all_output = "\n".join(attempt_outputs)
        remote_statuses = [
            int(match.group("status"))
            for match in API_REPORTER_ERROR_REGEX.finditer(all_output)
        ]
        had_connection_error = "Connection error" in all_output
        if (remote_statuses or had_connection_error) and all(
            500 <= status < 600 for status in remote_statuses
        ):
            raise unittest.SkipTest(
                "Remote API endpoints failed on their own side while MegaLinter was "
                f"running (HTTP {remote_statuses or 'connection error'}). "
                "This is a remote servers issue, not a MegaLinter one"
            )

        # Last check: if the remote servers went down while MegaLinter was running,
        # skip the test instead of failing, as this is not a MegaLinter issue
        unavailable_urls = []
        if logs_ko and not self.find_available_api_endpoints(
            used_logs_urls, len(used_logs_urls), logs_probe_payload
        ):
            unavailable_urls += used_logs_urls
        if metrics_ko and not self.find_available_api_endpoints(
            used_metrics_urls, len(used_metrics_urls), metrics_probe_payload
        ):
            unavailable_urls += used_metrics_urls
        if len(unavailable_urls) > 0:
            raise unittest.SkipTest(
                f"Remote API endpoints {unavailable_urls} became unavailable while "
                "MegaLinter was running. This is a remote servers issue, not a "
                "MegaLinter one"
            )
        self.fail(
            "Api Reporter could not post data using any of the available remote "
            "servers:\n" + "\n".join(failures)
        )

    def test_convert_sarif_to_human_failure(self):
        self.before_start()
        sample_sarif = '{"version": "2.1.0"}'
        with patch("megalinter.utils_reporter.subprocess.run") as mock_subprocess_run:
            for returncode, stdout in [(139, ""), (0, "")]:
                with self.subTest(returncode=returncode, stdout=stdout):
                    mock_result = mock_subprocess_run.return_value
                    mock_result.returncode = returncode
                    mock_result.stdout = stdout
                    result = utils_reporter.convert_sarif_to_human(
                        sample_sarif, self.request_id
                    )
                    self.assertEqual(
                        result,
                        sample_sarif,
                        "convert_sarif_to_human should return raw SARIF when sarif-fmt fails",
                    )
