#!/usr/bin/env python3
"""
Unit tests for utils_reporter

"""

import unittest

from megalinter.utils_reporter import (
    _build_missing_output_message,
    _build_table_content,
    _sort_linters_by_icon_severity,
    get_linter_status_icon,
    get_linter_summary_data,
)


class FakeLinter:
    def __init__(
        self,
        status="success",
        return_code=0,
        number_errors=0,
        total_number_errors=0,
        total_number_warnings=0,
        disable_errors_if_less_than=None,
        linter_name="fake_linter",
        can_output_sarif=False,
        output_sarif=False,
        sarif_output_file=None,
        report_folder="/tmp/lint/megalinter-reports",
    ):
        self.can_output_sarif = can_output_sarif
        self.output_sarif = output_sarif
        self.sarif_output_file = sarif_output_file
        self.report_folder = report_folder
        self.status = status
        self.return_code = return_code
        self.number_errors = number_errors
        self.total_number_errors = total_number_errors
        self.total_number_warnings = total_number_warnings
        self.disable_errors_if_less_than = disable_errors_if_less_than
        self.linter_name = linter_name
        self.descriptor_id = "FAKE"
        self.cli_lint_mode = "list_of_files"
        self.files = []
        self.number_fixed = 0
        self.try_fix = False
        self.elapsed_time_s = 1.0
        self.is_active = True


class FakeMaster:
    show_elapsed_time = False


class FakeReporter:
    master = FakeMaster()


class utils_reporter_test(unittest.TestCase):
    def test_status_icon_success(self):
        linter = FakeLinter(status="success", return_code=0)
        self.assertEqual("✅", get_linter_status_icon(linter))

    def test_status_icon_success_with_max_errors(self):
        linter = FakeLinter(
            status="success", return_code=0, disable_errors_if_less_than=10
        )
        self.assertEqual("✅", get_linter_status_icon(linter))

    def test_status_icon_warnings_only(self):
        linter = FakeLinter(status="warning", return_code=0, total_number_warnings=3)
        self.assertEqual("⚠️", get_linter_status_icon(linter))

    def test_status_icon_disable_errors(self):
        linter = FakeLinter(
            status="warning", return_code=0, number_errors=1, total_number_errors=3
        )
        self.assertEqual("⚠️", get_linter_status_icon(linter))

    def test_status_icon_warnings_only_with_max_errors(self):
        # Max errors is configured but no error has been found:
        # the threshold played no part, so this stays a plain warning
        linter = FakeLinter(
            status="warning",
            return_code=0,
            total_number_warnings=3,
            disable_errors_if_less_than=10,
        )
        self.assertEqual("⚠️", get_linter_status_icon(linter))

    def test_status_icon_under_max_errors(self):
        linter = FakeLinter(
            status="error",
            return_code=0,
            number_errors=1,
            total_number_errors=3,
            disable_errors_if_less_than=10,
        )
        self.assertEqual("☑️", get_linter_status_icon(linter))

    def test_status_icon_over_max_errors(self):
        linter = FakeLinter(
            status="error",
            return_code=1,
            number_errors=1,
            total_number_errors=14,
            disable_errors_if_less_than=10,
        )
        self.assertEqual("❌", get_linter_status_icon(linter))

    def test_status_icon_error(self):
        linter = FakeLinter(
            status="error", return_code=1, number_errors=1, total_number_errors=5
        )
        self.assertEqual("❌", get_linter_status_icon(linter))

    def test_sort_linters_by_icon_severity(self):
        error = FakeLinter(status="error", return_code=1, number_errors=1)
        warning = FakeLinter(status="warning", return_code=0, total_number_warnings=1)
        under_max = FakeLinter(
            status="error",
            return_code=0,
            number_errors=1,
            total_number_errors=3,
            disable_errors_if_less_than=10,
        )
        success = FakeLinter()
        linters = [success, under_max, warning, error]
        linters.sort(key=_sort_linters_by_icon_severity)
        self.assertEqual([error, warning, under_max, success], linters)

    def test_summary_data_max_errors_cell(self):
        linter = FakeLinter(
            status="error",
            return_code=0,
            number_errors=1,
            total_number_errors=3,
            disable_errors_if_less_than=10,
        )
        self.assertEqual("10", get_linter_summary_data(linter)["max_errors_cell"])

    def test_summary_data_max_errors_cell_empty(self):
        self.assertEqual("", get_linter_summary_data(FakeLinter())["max_errors_cell"])

    def test_markdown_table_max_errors_column(self):
        under_max = FakeLinter(
            status="error",
            return_code=0,
            number_errors=1,
            total_number_errors=3,
            disable_errors_if_less_than=10,
        )
        table = _build_table_content([under_max, FakeLinter()], FakeReporter(), "")
        self.assertIn("Max errors", table)
        self.assertIn("☑️", table)
        self.assertIn("10", table)

    @staticmethod
    def sarif_linter():
        return FakeLinter(
            linter_name="ruff",
            can_output_sarif=True,
            output_sarif=True,
            sarif_output_file="/tmp/lint/megalinter-reports/sarif/PYTHON_RUFF.sarif",
        )

    # A SARIF linter writes nothing to stdout: instead of a dead end, the
    # details section names the report and links the artifacts
    def test_missing_output_sarif_linter_with_run_url(self):
        message = _build_missing_output_message(
            self.sarif_linter(), "https://ci.example/run/1", "No output available"
        )
        self.assertIn("reports in SARIF format", message)
        self.assertIn("[MegaLinter artifacts](https://ci.example/run/1)", message)
        self.assertIn("`sarif/PYTHON_RUFF.sarif`", message)
        # The absolute container path must never be shown to the user
        self.assertNotIn("/tmp/lint", message)

    def test_missing_output_sarif_linter_without_run_url(self):
        message = _build_missing_output_message(
            self.sarif_linter(), "", "No output available"
        )
        self.assertIn("reports in SARIF format", message)
        self.assertIn("`sarif/PYTHON_RUFF.sarif`", message)
        self.assertNotIn("](", message)

    # The hint keys on the linter's SARIF intent, not on the file still being
    # on disk: SarifReporter runs first and removes it when LOG_FILE is "none"
    def test_missing_output_sarif_hint_does_not_need_the_file(self):
        linter = self.sarif_linter()
        self.assertIn(
            "sarif/PYTHON_RUFF.sarif",
            _build_missing_output_message(linter, "", "No output available"),
        )

    def test_missing_output_applies_to_the_file_not_found_case(self):
        message = _build_missing_output_message(
            self.sarif_linter(), "", "Linter output file not found"
        )
        self.assertIn("reports in SARIF format", message)

    # Non-SARIF linters keep the previous wording untouched
    def test_missing_output_non_sarif_linter_unchanged(self):
        for default_message in ("No output available", "Linter output file not found"):
            self.assertEqual(
                default_message,
                _build_missing_output_message(FakeLinter(), "", default_message),
            )

    def test_missing_output_sarif_capable_but_not_enabled_unchanged(self):
        linter = FakeLinter(
            can_output_sarif=True,
            output_sarif=False,
            sarif_output_file="/tmp/lint/megalinter-reports/sarif/PYTHON_RUFF.sarif",
        )
        self.assertEqual(
            "No output available",
            _build_missing_output_message(linter, "", "No output available"),
        )

    # report_folder is "" when the linter got no report_folder param: the
    # message must stay a clean path, not walk out of the reports folder
    def test_missing_output_sarif_without_report_folder(self):
        linter = FakeLinter(
            can_output_sarif=True,
            output_sarif=True,
            sarif_output_file="/sarif/PYTHON_RUFF.sarif",
            report_folder="",
        )
        message = _build_missing_output_message(linter, "", "No output available")
        self.assertIn("`sarif/PYTHON_RUFF.sarif`", message)
        self.assertNotIn("..", message)

    def test_missing_output_sarif_enabled_without_output_file_unchanged(self):
        linter = FakeLinter(can_output_sarif=True, output_sarif=True)
        self.assertEqual(
            "No output available",
            _build_missing_output_message(linter, "", "No output available"),
        )
