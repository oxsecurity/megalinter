# !/usr/bin/env python3
"""
Unit tests for Linter class (and sub-classes)
"""

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
            self.request_id, self.descriptor_id.upper() + "_" + self.linter_name.upper() + "_CLI_LINT_MODE", mode
        )

    def test_success_file_lint_mode(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        self.lint_mode_setup("file")
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_success_file_lint_mode")
        utilstest.test_linter_success_file_lint_mode(linter, self)
        linter.post_test("test_success_file_lint_mode")

    def test_success_list_of_files_lint_mode(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        self.lint_mode_setup("list_of_files")
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_success_list_of_files_lint_mode")
        utilstest.test_linter_success_list_of_files_lint_mode(linter, self)
        linter.post_test("test_success_list_of_files_lint_mode")

    def test_success_project_lint_mode(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        self.lint_mode_setup("project")
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_success_project_lint_mode")
        utilstest.test_linter_success_project_lint_mode(linter, self)
        linter.post_test("test_success_project_lint_mode")

    def test_failure_file_lint_mode(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        self.lint_mode_setup("file")
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_failure_file_lint_mode")
        utilstest.test_linter_failure_file_lint_mode(linter, self)
        linter.post_test("test_failure_file_lint_mode")

    def test_failure_list_of_files_lint_mode(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        self.lint_mode_setup("list_of_files")
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_failure_list_of_files_lint_mode")
        utilstest.test_linter_failure_list_of_files_lint_mode(linter, self)
        linter.post_test("test_failure_list_of_files_lint_mode")

    def test_failure_project_lint_mode(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        self.lint_mode_setup("project")
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test("test_failure_project_lint_mode")
        utilstest.test_linter_failure_project_lint_mode(linter, self)
        linter.post_test("test_failure_project_lint_mode")

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
