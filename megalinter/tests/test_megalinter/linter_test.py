#!/usr/bin/env python3
"""
Unit tests for Linter class

"""

import unittest
import uuid

from megalinter.Linter import Linter


class LinterTest(unittest.TestCase):
    @staticmethod
    def build_activation_params(enable_linters, disable_linters, priority):
        return {
            "default_linter_activation": len(enable_linters) == 0,
            "enable_linters": enable_linters,
            "disable_linters": disable_linters,
            "enable_descriptors": [],
            "disable_descriptors": [],
            "enable_disable_linters_priority": priority,
        }

    def run_activation(self, enable_linters, disable_linters, priority):
        linter = Linter.__new__(Linter)
        linter.name = "JAVASCRIPT_ES"
        linter.descriptor_id = "JAVASCRIPT"
        linter.request_id = str(uuid.uuid1())
        linter.activation_rules = []
        linter.manage_activation(
            self.build_activation_params(enable_linters, disable_linters, priority)
        )
        return linter.is_active

    def test_activation_overlap_default_priority_keeps_enabled(self):
        # Backward compatibility: ENABLE_LINTERS wins when a linter is in both lists
        self.assertTrue(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_ES"], "ENABLE")
        )

    def test_activation_overlap_disable_priority_skips(self):
        # New behavior: DISABLE_LINTERS overrides ENABLE_LINTERS when priority is DISABLE
        self.assertFalse(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_ES"], "DISABLE")
        )

    def test_activation_enable_only_with_disable_priority_stays_enabled(self):
        # Disable list must not over-reach when the linter is only in ENABLE_LINTERS
        self.assertTrue(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_STANDARD"], "DISABLE")
        )

    def test_activation_disable_only_is_skipped(self):
        self.assertFalse(self.run_activation([], ["JAVASCRIPT_ES"], "ENABLE"))

    def test_activation_unknown_priority_falls_back_to_enable(self):
        # Any value other than DISABLE preserves the default ENABLE-wins behavior
        self.assertTrue(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_ES"], "WHATEVER")
        )

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
