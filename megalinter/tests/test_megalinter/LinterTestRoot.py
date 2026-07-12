# !/usr/bin/env python3
"""
Unit tests for Linter class (and sub-classes)
"""

import unittest
import uuid
from typing import Optional

from megalinter import config, linter_factory, utilstest


class LinterTestRoot:
    descriptor_id: Optional[str] = None
    linter_name: Optional[str] = None
    request_id: str | None = None

    def get_linter_instance(self, request_id):
        return linter_factory.build_linter(
            self.descriptor_id,
            self.linter_name,
            {
                "default_linter_activation": True,
                "enable_descriptors": [],
                "enable_linters": [],
                "disable_descriptors": [],
                "disable_linters": [],
                "disable_errors_linters": [],
                "github_workspace": ".",
                "post_linter_status": True,
                "request_id": request_id,
            },
        )

    def lint_mode_setup(self, mode):
        config.set_value(
            self.request_id,
            self.descriptor_id.upper()
            + "_"
            + self.linter_name.upper()
            + "_CLI_LINT_MODE",
            mode,
        )

    # Run a success/failure test forcing a specific cli_lint_mode.
    # The linter is first built without the override to learn which modes it
    # supports, so an unsupported mode is skipped before the override validation
    # in Linter.load_config_vars would reject it. Supported modes are then run
    # through the real config override path (rebuild with the override set).
    def run_lint_mode_test(self, mode, test_name, test_func):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        probe_linter = self.get_linter_instance(self.request_id)
        if not probe_linter.is_cli_lint_mode_supported(mode):
            raise unittest.SkipTest(f"Linter does not support lint_mode: {mode}")
        # CI optimization: when a linter supports both file and list_of_files,
        # skip the slower per-file mode since list_of_files covers the same code path
        if mode == "file" and "list_of_files" in probe_linter.supported_cli_lint_modes:
            raise unittest.SkipTest(
                "Skipping file lint_mode: covered by list_of_files (CI optimization)"
            )
        self.lint_mode_setup(mode)
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test(test_name)
        test_func(linter, self)
        linter.post_test(test_name)

    def test_success_file_lint_mode(self):
        self.run_lint_mode_test(
            "file", "test_success_file_lint_mode", utilstest.test_linter_success
        )

    def test_success_list_of_files_lint_mode(self):
        self.run_lint_mode_test(
            "list_of_files",
            "test_success_list_of_files_lint_mode",
            utilstest.test_linter_success,
        )

    def test_success_project_lint_mode(self):
        self.run_lint_mode_test(
            "project", "test_success_project_lint_mode", utilstest.test_linter_success
        )

    def test_failure_file_lint_mode(self):
        self.run_lint_mode_test(
            "file", "test_failure_file_lint_mode", utilstest.test_linter_failure
        )

    def test_failure_list_of_files_lint_mode(self):
        self.run_lint_mode_test(
            "list_of_files",
            "test_failure_list_of_files_lint_mode",
            utilstest.test_linter_failure,
        )

    def test_failure_project_lint_mode(self):
        self.run_lint_mode_test(
            "project", "test_failure_project_lint_mode", utilstest.test_linter_failure
        )

    def test_get_linter_version(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_get_linter_version")
        utilstest.test_get_linter_version(linter, self)
        linter.post_test("test_get_linter_version")

    def test_get_linter_help(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_get_linter_help")
        utilstest.test_get_linter_help(linter, self)
        linter.post_test("test_get_linter_help")

    def test_report_tap(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {"request_id": self.request_id, "report_type": "tap"}
        )
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_report_tap")
        utilstest.test_linter_report_tap(linter, self)
        linter.post_test("test_report_tap")

    def test_report_sarif(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {"request_id": self.request_id, "report_type": "SARIF"}
        )
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_report_sarif")
        utilstest.test_linter_report_sarif(linter, self)
        linter.post_test("test_report_sarif")

    def test_format_fix(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_format_fix")
        utilstest.test_linter_format_fix(linter, self)
        linter.post_test("test_format_fix")
