#!/usr/bin/env python3
"""
Unit tests for utils_reporter

"""

import unittest

from megalinter.utils_reporter import (
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
    ):
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
