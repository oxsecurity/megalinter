#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""

import glob
import os
import tempfile
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

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

    def test_api_output(self):
        self.before_start()
        mega_linter, output = utilstest.call_mega_linter(
            {
                "APPLY_FIXES": "false",
                "LOG_LEVEL": "DEBUG",
                "MULTI_STATUS": "false",
                "ENABLE_LINTERS": "JAVASCRIPT_ES,PYTHON_BANDIT",
                "API_REPORTER": "true",
                "API_REPORTER_URL": "https://jsonplaceholder.typicode.com/posts",
                "API_REPORTER_METRICS_URL": "https://httpbin.org/anything",
                "API_REPORTER_DEBUG": "true",
                "request_id": self.request_id,
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertTrue(
            "[Api Reporter] Successfully posted data" in output,
            "Api Reporter failed to post message",
        )
        self.assertTrue(
            "[Api Reporter Metrics] Successfully posted data" in output,
            "Api Reporter Metrics failed to post message",
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
