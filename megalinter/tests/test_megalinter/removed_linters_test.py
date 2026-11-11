#!/usr/bin/env python3
"""
Unit tests for removed linters and descriptors detection

"""

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

from megalinter.removed_linters import (
    DESCRIPTOR_VARIABLE_SUFFIXES,
    REMOVED_DESCRIPTORS,
    REMOVED_LINTERS,
    find_removed_references,
    is_removed_related_variable,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_SCHEMA_PATH = (
    REPO_ROOT
    / "megalinter"
    / "descriptors"
    / "schemas"
    / "megalinter-configuration.jsonschema.json"
)
CUSTOM_FLAVOR_SCHEMA_PATH = (
    REPO_ROOT
    / "megalinter"
    / "descriptors"
    / "schemas"
    / "megalinter-custom-flavor.jsonschema.json"
)
V11_REMOVED_LINTERS = (
    "COFFEE_COFFEELINT",
    "GRAPHQL_GRAPHQL_SCHEMA_LINTER",
    "REPOSITORY_DUSTILOCK",
    "TYPESCRIPT_STANDARD",
)
V11_REMOVED_DESCRIPTORS = ("COFFEE",)


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

    def _load_json_schema(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def test_v11_removed_linters(self) -> None:
        cases = (
            ("COFFEE_COFFEELINT", "PYTHON_RUFF", "COFFEE_COFFEELINT_ARGUMENTS", "-x"),
            (
                "GRAPHQL_GRAPHQL_SCHEMA_LINTER",
                "GRAPHQL_BIOME",
                "GRAPHQL_GRAPHQL_SCHEMA_LINTER_CONFIG_FILE",
                ".graphql-schema-linterrc",
            ),
            (
                "REPOSITORY_DUSTILOCK",
                "REPOSITORY_TRIVY",
                "REPOSITORY_DUSTILOCK_DISABLE_ERRORS",
                "true",
            ),
            (
                "TYPESCRIPT_STANDARD",
                "TYPESCRIPT_ES",
                "TYPESCRIPT_STANDARD_ARGUMENTS",
                "--fix",
            ),
        )
        for linter, active_linter, var_name, var_value in cases:
            with self.subTest(linter=linter):
                self.assertEqual(
                    find_removed_references({}, [linter, active_linter], []),
                    [linter],
                )
                self.assertEqual(
                    find_removed_references({var_name: var_value}, [], []),
                    [linter],
                )
                self.assertTrue(is_removed_related_variable(var_name))

    def test_v11_coffee_descriptor(self) -> None:
        self.assertEqual(
            find_removed_references({}, [], ["COFFEE", "PYTHON"]),
            ["COFFEE"],
        )
        self.assertIn("_FILTER_REGEX_EXCLUDE", DESCRIPTOR_VARIABLE_SUFFIXES)
        self.assertIn("_PRE_COMMANDS", DESCRIPTOR_VARIABLE_SUFFIXES)
        for suffix in DESCRIPTOR_VARIABLE_SUFFIXES:
            var_name = f"COFFEE{suffix}"
            with self.subTest(variable=var_name):
                self.assertEqual(
                    find_removed_references({var_name: "x"}, [], []),
                    ["COFFEE"],
                )
                self.assertTrue(is_removed_related_variable(var_name))
        for unrelated in ("COFFEE_HOME", "COFFEE_MACHINE"):
            with self.subTest(variable=unrelated):
                self.assertEqual(
                    find_removed_references({unrelated: "x"}, [], []),
                    [],
                )

    def test_v11_removed_config_validates_against_schema(self) -> None:
        if importlib.util.find_spec("jsonschema") is None:
            raise unittest.SkipTest("jsonschema is not installed")
        import jsonschema

        schema = self._load_json_schema(CONFIG_SCHEMA_PATH)
        config = {
            "ENABLE_LINTERS": list(V11_REMOVED_LINTERS),
            "ENABLE": list(V11_REMOVED_DESCRIPTORS),
            "REPOSITORY_DUSTILOCK_ARGUMENTS": ["--verbose"],
            "TYPESCRIPT_STANDARD_ARGUMENTS": ["--fix"],
            "GRAPHQL_GRAPHQL_SCHEMA_LINTER_CONFIG_FILE": ".graphql-schema-linterrc",
            "COFFEE_COFFEELINT_ARGUMENTS": ["--quiet"],
            "COFFEE_FILTER_REGEX_EXCLUDE": "vendor/",
        }
        jsonschema.validate(instance=config, schema=schema)

    def test_v11_removed_schema_properties_marked_deprecated(self) -> None:
        schema = self._load_json_schema(CONFIG_SCHEMA_PATH)
        props = schema["properties"]
        prefixes = V11_REMOVED_LINTERS + V11_REMOVED_DESCRIPTORS
        matched_counts = {prefix: 0 for prefix in prefixes}
        for prop_name, prop_schema in props.items():
            matched_prefix = next(
                (
                    p
                    for p in prefixes
                    if prop_name == p or prop_name.startswith(f"{p}_")
                ),
                None,
            )
            if matched_prefix is None:
                continue
            self.assertTrue(is_removed_related_variable(prop_name), prop_name)
            matched_counts[matched_prefix] += 1
            with self.subTest(property=prop_name):
                self.assertIs(prop_schema.get("deprecated"), True, prop_name)
                title = prop_schema.get("title", "")
                self.assertTrue(
                    title.startswith("(deprecated) "),
                    f"{prop_name} title missing '(deprecated) ' prefix: {title!r}",
                )
        for prefix, count in matched_counts.items():
            self.assertGreater(count, 0, f"No schema properties found for {prefix}")

    def test_v11_removed_keys_retained_in_schema_enums(self) -> None:
        config_schema = self._load_json_schema(CONFIG_SCHEMA_PATH)
        flavor_schema = self._load_json_schema(CUSTOM_FLAVOR_SCHEMA_PATH)

        descriptor_enum = config_schema["definitions"]["enum_descriptor_keys"]["enum"]
        for descriptor in V11_REMOVED_DESCRIPTORS:
            self.assertIn(descriptor, descriptor_enum)

        config_linter_enum = config_schema["definitions"]["enum_linter_keys"]["enum"]
        flavor_linter_enum = flavor_schema["definitions"]["enum_linter_keys"]["enum"]
        for linter in V11_REMOVED_LINTERS:
            self.assertIn(linter, config_linter_enum)
            self.assertIn(linter, flavor_linter_enum)
