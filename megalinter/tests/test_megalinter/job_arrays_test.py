"""
Unit tests for Megalinter class

"""
import os
import unittest

import megalinter
from megalinter.tests.test_megalinter.helpers import utilstest
from unittest.mock import create_autospec
from unittest.mock import patch


class job_array_configuration_test(unittest.TestCase):

    def test_job_array_vars_are_parsed(self):
        """
        Test that the various job array variables are parsed correctly
        """

        scenario = [
            # Style                           Inputs                                       Expected
            ("Native",    {"MEGALINTER_ARRAY_INDEX": "5", "MEGALINTER_ARRAY_SIZE":  "10"}, (5, 10)),  # nopep8
            ("Gitlab",    {"CI_NODE_INDEX":          "5", "CI_NODE_TOTAL":          "10"}, (4, 10)),  # nopep8
            ("Circle CI", {"CIRCLE_NODE_INDEX":      "5", "CIRCLE_NODE_TOTAL":      "10"}, (5, 10)),  # nopep8
            ("SLURM",     {"SLURM_ARRAY_TASK_ID":    "5", "SLURM_ARRAY_TASK_COUNT": "10"}, (5, 10)),  # nopep8
        ]

        for provider, inputs, expected in scenario:
            utilstest.linter_test_setup(
                {
                    "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_fixes"
                }
            )
            with self.subTest(msg=f'Parsing {provider} array vars'):
                mega_linter, output = utilstest.call_mega_linter(
                    {**inputs, "ENABLE_LINTERS": "JAVASCRIPT_ES"}
                )
                self.assertEqual(
                    (mega_linter.array_index, mega_linter.array_size),
                    expected,
                    f"{provider} job array vars not parsed"
                )


class job_array_test(unittest.TestCase):

    def test_native_job_array_vars_take_priority(self):
        utilstest.linter_test_setup()
        mega_linter, output = utilstest.call_mega_linter(
            {
                "MEGALINTER_ARRAY_INDEX": "1", "MEGALINTER_ARRAY_SIZE":  "5",
                "CI_NODE_INDEX":          "2", "CI_NODE_TOTAL":          "6",
                "CIRCLE_NODE_INDEX":      "3", "CIRCLE_NODE_TOTAL":      "7",
                "SLURM_ARRAY_TASK_ID":    "4", "SLURM_ARRAY_TASK_COUNT": "8",
                "ENABLE_LINTERS": ","
            }
        )
        self.assertEqual(
            (mega_linter.array_index, mega_linter.array_size),
            (1, 5),
            "Native job array vars should take precedence"
        )

    @patch('megalinter.MegaLinter.Megalinter.collect_files')
    def test_uneven_job_array_splits(self, patch):
        all_linters = [
            "JAVASCRIPT", "REPOSITORY_TRIVY",
            "GROOVY", "JAVASCRIPT_PRETTIER", "TERRAFORM_KICS"
        ]
        scenario = (
            ['JAVASCRIPT', 'GROOVY', 'TERRAFORM_KICS'],
            ["REPOSITORY_TRIVY", "JAVASCRIPT_PRETTIER"],
        )

        for index, expected_result in enumerate(scenario):
            utilstest.linter_test_setup()
            with self.subTest(msg=f"Expected index {index} to run {expected_result}"):
                mega_linter, output = utilstest.call_mega_linter(
                    {
                        "ENABLE_LINTERS": ",",
                        "MEGALINTER_ARRAY_INDEX": index,
                        "MEGALINTER_ARRAY_SIZE":  "2",
                    }
                )
                linters_for_index = mega_linter.filter_linters_by_array_index(
                    all_linters)
                self.assertEqual(linters_for_index, expected_result)
