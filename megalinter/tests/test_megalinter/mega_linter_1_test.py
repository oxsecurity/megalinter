#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest

import megalinter
from megalinter.constants import ML_REPO
from megalinter.tests.test_megalinter.helpers import utilstest


class mega_linter_1_test(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project"
            }
        )

    def test_disable_language(self):
        mega_linter, output = utilstest.call_mega_linter({"DISABLE": "GROOVY"})
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        utilstest.assert_is_skipped("GROOVY", output, self)

    def test_disable_language_legacy(self):
        mega_linter, output = utilstest.call_mega_linter({"VALIDATE_GROOVY": "false"})
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        utilstest.assert_is_skipped("GROOVY", output, self)

    def test_disable_linter(self):
        mega_linter, output = utilstest.call_mega_linter(
            {"DISABLE_LINTERS": "JAVASCRIPT_ES"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        utilstest.assert_is_skipped("JAVASCRIPT_ES", output, self)
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [standard", output)

    def test_disable_linter_legacy(self):
        mega_linter, output = utilstest.call_mega_linter(
            {"VALIDATE_JAVASCRIPT_ES": "false"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        utilstest.assert_is_skipped("JAVASCRIPT_ES", output, self)
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [standard", output)

    def test_enable_only_one_linter(self):
        mega_linter, output = utilstest.call_mega_linter(
            {"ENABLE_LINTERS": "JAVASCRIPT_ES"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [eslint", output)
        utilstest.assert_is_skipped("JAVASCRIPT_STANDARD", output, self)
        utilstest.assert_is_skipped("GROOVY", output, self)

    def test_enable_only_one_linter_legacy(self):
        mega_linter, output = utilstest.call_mega_linter(
            {"VALIDATE_JAVASCRIPT_ES": "true"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [eslint", output)
        utilstest.assert_is_skipped("JAVASCRIPT_STANDARD", output, self)
        utilstest.assert_is_skipped("GROOVY", output, self)

    def test_enable_only_one_language(self):
        mega_linter, output = utilstest.call_mega_linter({"ENABLE": "JAVASCRIPT"})
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [eslint", output)
        self.assertIn("Using [standard", output)
        utilstest.assert_is_skipped("GROOVY", output, self)

    def test_enable_only_one_language_legacy(self):
        mega_linter, output = utilstest.call_mega_linter(
            {"VALIDATE_JAVASCRIPT": "true"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [eslint", output)
        self.assertIn("Using [standard", output)
        utilstest.assert_is_skipped("GROOVY", output, self)

    def test_validate_all_code_base_false(self):
        megalinter.config.set_value(
            "GITHUB_WORKSPACE",
            (
                "/tmp/lint"
                if os.path.isdir("/tmp/lint")
                else os.path.relpath(
                    os.path.relpath(os.path.dirname(os.path.abspath(__file__)))
                    + "/../../.."
                )
            ),
        )
        mega_linter, output = utilstest.call_mega_linter(
            {"ENABLE_LINTERS": "PYTHON_PYLINT", "VALIDATE_ALL_CODEBASE": "false"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )

    def test_override_linter_rules_path(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "LINTER_RULES_PATH": ".",
                "JAVASCRIPT_ES_CONFIG_FILE": ".eslintrc-custom.yml",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [eslint", output)
        self.assertIn(".eslintrc-custom.yml", output)

    def test_override_linter_rules_path_remote(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "LINTER_RULES_PATH": f"https://raw.githubusercontent.com/{ML_REPO}/main"
                "/.automation/test/sample_project",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [eslint", output)
        self.assertIn(
            f"- Rules config: [https://raw.githubusercontent.com/{ML_REPO}/main/"
            ".automation/test/sample_project/.eslintrc.json]",
            output,
        )

    def test_override_linter_rules_path_remote_custom_file_name(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "LINTER_RULES_PATH": f"https://raw.githubusercontent.com/{ML_REPO}/main/"
                ".automation/test/sample_project",
                "JAVASCRIPT_ES_CONFIG_FILE": ".eslintrc-custom.yml",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("Using [eslint", output)
        self.assertIn(
            f"- Rules config: [https://raw.githubusercontent.com/{ML_REPO}/main/"
            ".automation/test/sample_project/.eslintrc-custom.yml]",
            output,
        )
        self.assertIn(".eslintrc-custom.yml", output)

    def test_override_linter_rules_path_remote_error(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "LINTER_RULES_PATH": "https://raw.githubusercontent.com/notexisting/wesh",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn(
            "Unable to fetch https://raw.githubusercontent.com/notexisting/wesh",
            output,
        )

    def test_custom_config_on_language(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "JAVASCRIPT_LINTER_RULES_PATH": ".",
                "JAVASCRIPT_CONFIG_FILE": ".eslintrc-custom.yml",
                "JAVASCRIPT_FILTER_REGEX_INCLUDE": r"(.*_good_.*|.*\/good\/.*)",
                "JAVASCRIPT_FILTER_REGEX_EXCLUDE": r"(.*_bad_.*|.*\/bad\/.*)",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn(".eslintrc-custom.yml", output)

    def test_general_include_exclude(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "FILTER_REGEX_INCLUDE": r"(.*_good_.*|.*\/good\/.*)",
                "FILTER_REGEX_EXCLUDE": r"(.*_bad_.*|.*\/bad\/.*)",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)

    def test_custom_config_on_linter(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "JAVASCRIPT_ES_LINTER_RULES_PATH": ".",
                "JAVASCRIPT_ES_CONFIG_FILE": ".eslintrc-custom.yml",
                "JAVASCRIPT_FILTER_REGEX_INCLUDE": r"(.*_good_.*|.*\/good\/.*)",
                "JAVASCRIPT_FILTER_REGEX_EXCLUDE": r"(.*_bad_.*|.*\/bad\/.*)",
                "MULTI_STATUS": "false",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)

    def test_user_arguments_on_linter(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "JAVASCRIPT_ES_FILTER_REGEX_INCLUDE": r"(.*_good_.*|.*\/good\/.*)",
                "JAVASCRIPT_ES_FILTER_REGEX_EXCLUDE": r"(.*_bad_.*|.*\/bad\/.*)",
                "JAVASCRIPT_ES_ARGUMENTS": "--debug --env-info",
                "MULTI_STATUS": "false",
                "LOG_LEVEL": "DEBUG",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processed [JAVASCRIPT] files", output)
        self.assertIn("--debug --env-info", output)

    def test_alpaca(self):
        res = megalinter.alpaca()
        self.assertTrue(res is True)

    def test_new_flavor_suggestion(self):
        mega_linter, output = utilstest.call_mega_linter(
            {"MULTI_STATUS": "false", "LOG_LEVEL": "DEBUG"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertEqual("new", mega_linter.flavor_suggestions[0])

    def test_json_output(self):
        mega_linter, output = utilstest.call_mega_linter({"JSON_REPORTER": "true"})
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        expected_output_file = (
            mega_linter.report_folder + os.path.sep + "mega-linter-report.json"
        )
        self.assertTrue(
            os.path.isfile(expected_output_file),
            "Output json file " + expected_output_file + " should exist",
        )

    def test_json_output_detailed(self):
        mega_linter, output = utilstest.call_mega_linter(
            {"JSON_REPORTER": "true", "JSON_REPORTER_OUTPUT_DETAIL": "detailed"}
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        expected_output_file = (
            mega_linter.report_folder + os.path.sep + "mega-linter-report.json"
        )
        self.assertTrue(
            os.path.isfile(expected_output_file),
            "Output json file " + expected_output_file + " should exist",
        )

    def test_config_reporter(self):
        mega_linter, output = utilstest.call_mega_linter({"CONFIG_REPORTER": "true"})
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        expected_output_file = (
            mega_linter.report_folder + os.path.sep + "IDE-config.txt"
        )
        self.assertTrue(
            os.path.isfile(expected_output_file),
            "Output IDE config file " + expected_output_file + " should exist",
        )

    def test_override_cli_lint_mode(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE": "YAML",
                "YAML_YAMLLINT_CLI_LINT_MODE": "file",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertTrue(
            len(
                list(
                    filter(
                        lambda x: (
                            x.name == "YAML_YAMLLINT" and x.cli_lint_mode == "file"
                        ),
                        mega_linter.linters,
                    )
                )
            )
            == 1,
            "YAML_YAMLLINT should have been processed with cli_lint_mode = file",
        )

    def test_override_cli_executable(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "ENABLE": "PHP",
                "PHP_BUILTIN_CLI_EXECUTABLE": "/usr/bin/php8",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertTrue(
            len(
                list(
                    filter(
                        lambda x: (
                            x.name == "PHP_BUILTIN"
                            and x.cli_executable == "/usr/bin/php8"
                        ),
                        mega_linter.linters,
                    )
                )
            )
            == 1,
            "PHP_BUILTIN should have been processed with cli_executable = /usr/bin/php8",
        )
