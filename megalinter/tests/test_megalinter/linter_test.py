#!/usr/bin/env python3
"""
Unit tests for Linter class

"""

import json
import os
import tempfile
import uuid
from unittest import mock
from unittest.mock import patch

from megalinter.Linter import Linter
from megalinter.linters.StyleLintLinter import StyleLintLinter
from megalinter.tests.test_megalinter.isolated_config_test_case import (
    IsolatedConfigTestCase,
)
from megalinter.tests.test_megalinter.linter_run_stub import build_project_run_linter


class LinterTest(IsolatedConfigTestCase):
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

    def test_remove_command_args_removes_existing_args(self):
        linter = Linter.__new__(Linter)
        linter.name = "CSS_STYLELINT"
        linter.cli_command_remove_args = ["--formatter", "json"]

        cmd = linter.remove_command_args(
            ["stylelint", "--formatter", "json", "--config", "conf.json"]
        )

        self.assertEqual(["stylelint", "--config", "conf.json"], cmd)

    def test_remove_command_args_ignores_missing_args(self):
        # Missing arguments must not raise ValueError: they can be conditionally
        # added by linter subclasses after the removal has been performed
        linter = Linter.__new__(Linter)
        linter.name = "CSS_STYLELINT"
        linter.cli_command_remove_args = ["--config-basedir"]

        cmd = linter.remove_command_args(["stylelint", "--config", "conf.json"])

        self.assertEqual(["stylelint", "--config", "conf.json"], cmd)

    def test_stylelint_skips_config_basedir_when_removed_by_user(self):
        linter = StyleLintLinter.__new__(StyleLintLinter)
        linter.name = "CSS_STYLELINT"
        linter.cli_lint_mode = "list_of_files"
        linter.cli_command_remove_args = ["--config-basedir"]

        with (
            mock.patch.object(Linter, "build_lint_command", return_value=["stylelint"]),
            mock.patch("os.path.isdir", return_value=True),
        ):
            cmd = linter.build_lint_command()

        self.assertEqual(["stylelint"], cmd)

    def test_stylelint_adds_config_basedir_by_default(self):
        linter = StyleLintLinter.__new__(StyleLintLinter)
        linter.name = "CSS_STYLELINT"
        linter.cli_lint_mode = "list_of_files"
        linter.cli_command_remove_args = []

        with (
            mock.patch.object(Linter, "build_lint_command", return_value=["stylelint"]),
            mock.patch("os.path.isdir", return_value=True),
        ):
            cmd = linter.build_lint_command()

        self.assertEqual(["stylelint", "--config-basedir", "/node-deps"], cmd)

    def test_stylelint_does_not_duplicate_user_defined_config_basedir(self):
        linter = StyleLintLinter.__new__(StyleLintLinter)
        linter.name = "CSS_STYLELINT"
        linter.cli_lint_mode = "list_of_files"
        linter.cli_command_remove_args = []

        with (
            mock.patch.object(
                Linter,
                "build_lint_command",
                return_value=["stylelint", "--config-basedir", "/tmp"],
            ),
            mock.patch("os.path.isdir", return_value=True),
        ):
            cmd = linter.build_lint_command()

        self.assertEqual(["stylelint", "--config-basedir", "/tmp"], cmd)

    def test_sarif_zero_results_is_not_a_warning(self):
        linter = Linter.__new__(Linter)
        linter.linter_name = "test_linter"
        linter.sarif_output_file = None
        linter.sarif_default_output_file = None
        sarif = json.dumps(
            {
                "runs": [
                    {
                        "tool": {"driver": {}},
                        "results": [
                            {"level": "note", "locations": [{"physicalLocation": {}}]}
                        ],
                    }
                ]
            }
        )

        with self.assertNoLogs(level="WARNING"):
            result = linter.get_sarif_result_count(sarif, "error")

        self.assertEqual(0, result)

    @staticmethod
    def build_sarif_linter(sarif_output_file=None):
        linter = Linter.__new__(Linter)
        linter.linter_name = "secretlint"
        linter.sarif_output_file = sarif_output_file
        linter.sarif_default_output_file = None
        linter.sarif_parse_failed = False
        return linter

    @staticmethod
    def build_sarif_payload():
        # One error plus one warning: the fixture both the stdout path and the
        # sarif_output_file path count findings against
        return json.dumps(
            {
                "runs": [
                    {
                        "tool": {"driver": {"name": "secretlint"}},
                        "results": [
                            {"level": "error", "locations": [{}]},
                            {"level": "warning", "locations": [{}]},
                        ],
                    }
                ]
            }
        )

    def test_sarif_count_from_stdout(self):
        # Normal path: a linter with findings exits non-zero AND emits valid SARIF
        linter = self.build_sarif_linter()
        stdout = self.build_sarif_payload()
        self.assertEqual(linter.get_sarif_result_count(stdout, "error"), 1)
        self.assertEqual(linter.get_sarif_result_count(stdout, "warning"), 1)

    def test_sarif_count_on_crash_output_is_zero(self):
        # A linter that died before producing SARIF must not be counted as a finding
        linter = self.build_sarif_linter()
        stdout = (
            "[Error: ENOENT: no such file or directory, open "
            "'/github/workspace/megalinter-reports/copy-paste/html/jscpd-report.json'] {\n"
            "  errno: -2,\n"
            "  code: 'ENOENT',\n"
            "  syscall: 'open',\n"
            "  path: '/github/workspace/megalinter-reports/copy-paste/html/jscpd-report.json'\n"
            "}"
        )
        self.assertEqual(linter.get_sarif_result_count(stdout, "error"), 0)

    def test_sarif_count_on_crash_output_logs_raw_output(self):
        linter = self.build_sarif_linter()
        stdout = "Error: ENOENT: no such file or directory, open 'x.json'"
        with self.assertLogs(level="ERROR") as captured:
            linter.get_sarif_result_count(stdout, "error")
        self.assertIn("secretlint", "\n".join(captured.output))
        self.assertIn("ENOENT", "\n".join(captured.output))

    def test_sarif_unparsable_stdout_marks_parse_failed(self):
        # A linter that exited 0 with a stack trace instead of SARIF must not be
        # silently reported as clean: the sticky flag has to be raised
        linter = self.build_sarif_linter()
        stdout = (
            "TypeError: Cannot read properties of undefined (reading 'map')\n"
            "    at Object.<anonymous> (/usr/lib/node_modules/jscpd/dist/index.js:1:1)"
        )
        result = linter.get_sarif_result_count(stdout, "error")
        self.assertEqual(result, 0)
        self.assertTrue(linter.sarif_parse_failed)

    def test_sarif_incomplete_structure_marks_parse_failed(self):
        # SARIF-shaped output that passes the "runs" gate in find_json_in_stdout but
        # is missing "results" must hit the except branch, not be silently swallowed
        linter = self.build_sarif_linter()
        stdout = json.dumps({"runs": [{"tool": {"driver": {}}}]})
        with self.assertLogs(level="ERROR") as captured:
            result = linter.get_sarif_result_count(stdout, "error")
        self.assertEqual(result, 0)
        self.assertTrue(linter.sarif_parse_failed)
        log_text = "\n".join(captured.output)
        self.assertIn("secretlint", log_text)
        # Distinguishes this from the empty-stdout path: only the except handler
        # (triggered by the KeyError on "results") emits this message
        self.assertIn("unable to compute total", log_text)

    def test_sarif_valid_output_leaves_parse_failed_false(self):
        linter = self.build_sarif_linter()
        stdout = json.dumps(
            {
                "runs": [
                    {
                        "tool": {"driver": {"name": "secretlint"}},
                        "results": [
                            {"level": "error", "locations": [{}]},
                        ],
                    }
                ]
            }
        )
        linter.get_sarif_result_count(stdout, "error")
        self.assertFalse(linter.sarif_parse_failed)

    def test_sarif_count_from_output_file(self):
        # The dominant production path: 23 descriptors pass {{SARIF_OUTPUT_FILE}}
        # in cli_sarif_args, so the sarif_output_file branch, not stdout, is what
        # most linters actually use
        sarif = self.build_sarif_payload()
        with tempfile.TemporaryDirectory() as tmpdir:
            sarif_output_file = os.path.join(tmpdir, "sarif_output.json")
            with open(sarif_output_file, "w", encoding="utf-8") as f:
                f.write(sarif)
            linter = self.build_sarif_linter(sarif_output_file=sarif_output_file)
            self.assertEqual(linter.get_sarif_result_count("", "error"), 1)
            self.assertEqual(linter.get_sarif_result_count("", "warning"), 1)
            self.assertFalse(linter.sarif_parse_failed)

    def test_sarif_empty_output_file_marks_parse_failed(self):
        # yaml.safe_load on an empty file returns None, so sarif_output["runs"]
        # raises TypeError, which the broad except handler in
        # get_sarif_result_count catches
        with tempfile.TemporaryDirectory() as tmpdir:
            sarif_output_file = os.path.join(tmpdir, "sarif_output.json")
            open(sarif_output_file, "w", encoding="utf-8").close()
            linter = self.build_sarif_linter(sarif_output_file=sarif_output_file)
            with self.assertLogs(level="ERROR") as captured:
                result = linter.get_sarif_result_count("", "error")
            self.assertEqual(result, 0)
            self.assertTrue(linter.sarif_parse_failed)
            self.assertIn("secretlint", "\n".join(captured.output))

    def test_get_total_number_errors_reflects_status_when_unmeasured(self):
        # get_total_number_errors falls back to 1 error for any non-success status
        # when no count could be extracted from stdout; success stays at 0
        linter = Linter.__new__(Linter)
        linter.cli_lint_errors_count = None
        linter.output_sarif = False
        linter.status = "success"
        self.assertEqual(linter.get_total_number_errors("irrelevant stdout"), 0)

        linter.status = "warning"
        self.assertEqual(linter.get_total_number_errors("irrelevant stdout"), 1)

    def test_run_project_mode_unparsable_sarif_promotes_to_warning(self):
        # End-to-end: a linter that exits 0 while emitting garbage instead of SARIF
        # must not be reported as a clean success (issue this change fixes)
        linter = build_project_run_linter(self.request_id)
        stdout = (
            "TypeError: Cannot read properties of undefined (reading 'map')\n"
            "    at Object.<anonymous> (/usr/lib/node_modules/jscpd/dist/index.js:1:1)"
        )
        with patch.object(Linter, "process_linter", return_value=(0, stdout)):
            with self.assertLogs(level="WARNING") as captured:
                linter.run()

        self.assertEqual(linter.status, "warning")
        self.assertEqual(linter.total_number_errors, 0)
        self.assertEqual(linter.total_number_warnings, 0)
        self.assertEqual(linter.return_code, 0)
        # Every reporter shows this linter with 0 errors and 0 warnings, so the
        # promotion has to say why, naming the linter, or a yellow run is unexplained
        log_text = "\n".join(captured.output)
        self.assertIn("test_linter", log_text)
        self.assertIn("results could not be counted", log_text)

    def test_run_project_mode_valid_sarif_zero_results_stays_success(self):
        # Negative case proving the promotion is conditional: valid SARIF with no
        # findings and exit code 0 must remain "success", not be promoted
        linter = build_project_run_linter(self.request_id)
        stdout = json.dumps(
            {
                "runs": [
                    {
                        "tool": {"driver": {}},
                        "results": [],
                    }
                ]
            }
        )
        with patch.object(Linter, "process_linter", return_value=(0, stdout)):
            linter.run()

        self.assertEqual(linter.status, "success")
        self.assertEqual(linter.total_number_errors, 0)
        self.assertEqual(linter.total_number_warnings, 0)
        self.assertEqual(linter.return_code, 0)

    def test_run_project_mode_real_failure_not_downgraded_by_unparsable_sarif(self):
        # The promotion in Linter.run() must only ever raise a "success" to
        # "warning", never override a genuine "error": a linter that both exits
        # non-zero AND emits unparsable SARIF has to stay "error", with the
        # error count still reflecting the real failure
        linter = build_project_run_linter(self.request_id)
        stdout = (
            "TypeError: Cannot read properties of undefined (reading 'map')\n"
            "    at Object.<anonymous> (/usr/lib/node_modules/jscpd/dist/index.js:1:1)"
        )
        with patch.object(Linter, "process_linter", return_value=(1, stdout)):
            linter.run()

        self.assertEqual(linter.status, "error")
        self.assertEqual(linter.total_number_errors, 1)
        self.assertEqual(linter.total_number_warnings, 0)
        self.assertEqual(linter.return_code, 1)
