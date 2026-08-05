#!/usr/bin/env python3
"""
Unit tests for Megalinter prerun analysis mode (MEGALINTER_PRERUN=true)

"""

import json
import os
import unittest
import uuid

from megalinter import config, utilstest
from megalinter.prerun_report import PRERUN_REPORT_FILE_NAME


class mega_linter_prerun_test(unittest.TestCase):
    def before_start(self):
        config.delete()
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {
                "request_id": self.request_id,
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project",
            }
        )

    def test_prerun_mode(self):
        self.before_start()
        mega_linter, output = utilstest.call_mega_linter(
            {
                "MEGALINTER_PRERUN": "true",
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "FLAVOR_SUGGESTIONS": "true",
                "MULTI_STATUS": "false",
                "request_id": self.request_id,
            }
        )
        self.assertTrue(
            len(mega_linter.active_linters) > 0, "Active linters have been identified"
        )
        # No linter has been run
        self.assertNotIn("Linted [", output)
        self.assertIn("MegaLinter prerun analysis", output)
        # Prerun report file has been written
        report_file = mega_linter.report_folder + os.path.sep + PRERUN_REPORT_FILE_NAME
        self.assertTrue(
            os.path.isfile(report_file),
            "Prerun report file " + report_file + " should exist",
        )
        with open(report_file, "r", encoding="utf-8") as json_file:
            report = json.load(json_file)
        self.assertEqual("prerun", report["mode"])
        self.assertTrue(report["files"]["found"] > 0)
        self.assertTrue(report["files"]["kept"] > 0)
        self.assertTrue(len(report["active_linters"]) > 0)
        active_linter = report["active_linters"][0]
        self.assertEqual("JAVASCRIPT_ES", active_linter["key"])
        self.assertTrue(active_linter["files_count"] > 0)
        # A single active linter matches smaller flavors: a flavor suggestion is expected
        flavor_suggestions = [
            suggestion
            for suggestion in report["suggestions"]
            if suggestion["variable"] == "MEGALINTER_FLAVOR"
        ]
        self.assertTrue(len(flavor_suggestions) == 1)
        self.assertTrue(len(flavor_suggestions[0]["values"]) == 1)

    def test_prerun_mode_no_flavor_suggestion(self):
        self.before_start()
        mega_linter, output = utilstest.call_mega_linter(
            {
                "MEGALINTER_PRERUN": "true",
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "FLAVOR_SUGGESTIONS": "false",
                "MULTI_STATUS": "false",
                "request_id": self.request_id,
            }
        )
        self.assertIn("MegaLinter prerun analysis", output)
        report_file = mega_linter.report_folder + os.path.sep + PRERUN_REPORT_FILE_NAME
        with open(report_file, "r", encoding="utf-8") as json_file:
            report = json.load(json_file)
        flavor_suggestions = [
            suggestion
            for suggestion in report["suggestions"]
            if suggestion["variable"] == "MEGALINTER_FLAVOR"
        ]
        self.assertTrue(len(flavor_suggestions) == 0)
