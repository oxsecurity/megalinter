#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import glob
import os
import tempfile
import unittest
import uuid

from megalinter import Linter, MegaLinter, utilstest
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
