#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest

from megalinter.constants import DEFAULT_SARIF_REPORT_FILE_NAME
from megalinter.tests.test_megalinter.helpers import utilstest


class mega_linter_3_sarif_test(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_sarif"
            }
        )

    def test_sarif_output(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "APPLY_FIXES": "false",
                "LOG_LEVEL": "DEBUG",
                "MULTI_STATUS": "false",
                "ENABLE_LINTERS": "JAVASCRIPT_ES,REPOSITORY_TRIVY,REPOSITORY_GITLEAKS,PYTHON_BANDIT,TERRAFORM_KICS",
                "SARIF_REPORTER": "true"
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
