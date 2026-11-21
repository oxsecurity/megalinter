#!/usr/bin/env python3
"""
Unit tests for removed linters and descriptors detection

"""

import unittest

from megalinter.removed_linters import (
    REMOVED_DESCRIPTORS,
    REMOVED_LINTERS,
    find_removed_references,
    is_removed_related_variable,
)


class removed_linters_test(unittest.TestCase):
    def test_find_in_linter_lists(self):
        found = find_removed_references({}, ["REPOSITORY_GITLEAKS", "PYTHON_RUFF"], [])
        self.assertEqual(found, ["REPOSITORY_GITLEAKS"])

    def test_find_in_descriptor_lists(self):
        found = find_removed_references({}, [], ["PUPPET", "PYTHON"])
        self.assertEqual(found, ["PUPPET"])

    def test_find_in_config_variables(self):
        found = find_removed_references(
            {"TERRAFORM_TERRASCAN_ARGUMENTS": "-x", "LOG_LEVEL": "INFO"}, [], []
        )
        self.assertEqual(found, ["TERRAFORM_TERRASCAN"])

    def test_longest_prefix_wins(self):
        found = find_removed_references(
            {"SALESFORCE_SFDX_SCANNER_APEX_CONFIG_FILE": "x"}, [], []
        )
        self.assertEqual(found, ["SALESFORCE_SFDX_SCANNER_APEX"])

    def test_clean_config_finds_nothing(self):
        found = find_removed_references(
            {"LOG_LEVEL": "INFO", "PYTHON_RUFF_ARGUMENTS": "-x"},
            ["PYTHON_RUFF"],
            ["PYTHON"],
        )
        self.assertEqual(found, [])

    def test_deduplicates_across_sources(self):
        found = find_removed_references(
            {"REPOSITORY_GITLEAKS_ARGUMENTS": "-x"}, ["REPOSITORY_GITLEAKS"], []
        )
        self.assertEqual(found, ["REPOSITORY_GITLEAKS"])

    def test_unrelated_variables_with_removed_descriptor_prefix(self):
        # CI and system variables sharing a removed descriptor prefix (issue #9024)
        for name in (
            "GIT_STRATEGY",
            "GIT_DEPTH",
            "GIT_SUBMODULE_STRATEGY",
            "GIT_DIR",
            "GIT_WORK_TREE",
            "GIT_CONFIG_COUNT",
            "CREDENTIALS_DIRECTORY",
            "CREDENTIALS_PROFILE",
            "MAKEFILE_HOME",
            "OPENAPI_AUTH",
            "PUPPET_ENVIRONMENT",
            "PUPPET_REPORTER",
            "GIT_REPORTER_URL",
            "GIT",
        ):
            with self.subTest(variable=name):
                self.assertEqual(find_removed_references({name: "x"}, [], []), [])

    def test_removed_descriptor_options_still_found(self):
        for name, removed in (
            ("GIT_FILTER_REGEX_INCLUDE", "GIT"),
            ("GIT_PRE_COMMANDS", "GIT"),
            ("MAKEFILE_FILTER_REGEX_EXCLUDE", "MAKEFILE"),
            ("PUPPET_POST_COMMANDS", "PUPPET"),
            ("OPENAPI_CONFIG_FILE", "OPENAPI"),
            ("CREDENTIALS_DISABLE_ERRORS", "CREDENTIALS"),
        ):
            with self.subTest(variable=name):
                self.assertEqual(
                    find_removed_references({name: "x"}, [], []), [removed]
                )

    def test_removed_linter_options_found_with_any_suffix(self):
        for name, removed in (
            ("GIT_GIT_DIFF_ARGUMENTS", "GIT_GIT_DIFF"),
            ("REPOSITORY_GITLEAKS_ARGUMENTS", "REPOSITORY_GITLEAKS"),
            ("MAKEFILE_CHECKMAKE_CUSTOM_OPTION", "MAKEFILE_CHECKMAKE"),
        ):
            with self.subTest(variable=name):
                self.assertEqual(
                    find_removed_references({name: "x"}, [], []), [removed]
                )

    def test_is_removed_related_variable(self):
        self.assertTrue(
            is_removed_related_variable("MARKDOWN_REMARK_LINT_CLI_EXECUTABLE")
        )
        self.assertTrue(is_removed_related_variable("MAKEFILE_FILTER_REGEX_INCLUDE"))
        self.assertFalse(is_removed_related_variable("PYTHON_RUFF_ARGUMENTS"))
        # A removed descriptor key must not match unrelated variables sharing its prefix
        self.assertFalse(is_removed_related_variable("GITHUB_TOKEN"))

    def test_entries_are_complete(self):
        for key, info in {**REMOVED_LINTERS, **REMOVED_DESCRIPTORS}.items():
            self.assertRegex(info["removed_in"], r"^\d+\.\d+\.\d+$", key)
            self.assertTrue(info["reason"], key)
            self.assertIn("replacement", info, key)
