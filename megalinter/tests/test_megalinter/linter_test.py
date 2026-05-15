#!/usr/bin/env python3
"""
Unit tests for Linter class

"""

import unittest

from megalinter.Linter import Linter


class LinterTest(unittest.TestCase):
    def test_replace_vars_with_default_variables(self):
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = "test_sarif_output_file"
        linter.report_folder = "test_report_folder"
        linter.workspace = "test_workspace"

        args = ["{{SARIF_OUTPUT_FILE}}", "{{REPORT_FOLDER}}", "{{WORKSPACE}}"]
        additional_variables = None

        replaced_args = linter.replace_vars(args, additional_variables)

        self.assertEqual(
            ["test_sarif_output_file", "test_report_folder", "test_workspace"],
            replaced_args,
        )

    def test_replace_vars_with_unknown_variable(self):
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = "test_sarif_output_file"
        linter.report_folder = "test_report_folder"
        linter.workspace = "test_workspace"

        args = ["{{UNKNOWN_VAR}}"]
        additional_variables = None

        replaced_args = linter.replace_vars(args, additional_variables)

        self.assertEqual(["{{UNKNOWN_VAR}}"], replaced_args)

    def test_replace_vars_with_additional_variables(self):
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = "test_sarif_output_file"
        linter.report_folder = "test_report_folder"
        linter.workspace = "test_workspace"

        args = ["{{ADDITIONAL_VAR}}"]
        additional_variables = {"{{ADDITIONAL_VAR}}": "test_additional_var"}

        replaced_args = linter.replace_vars(args, additional_variables)

        self.assertEqual(["test_additional_var"], replaced_args)
