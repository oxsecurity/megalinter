# !/usr/bin/env python3
"""
Unit tests for Linter class (and sub-classes)
"""
import uuid
from typing import Optional

from megalinter import linter_factory, utilstest


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

    def test_success(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test()
        utilstest.test_linter_success(linter, self)
        linter.post_test()

    def test_failure(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test()
        utilstest.test_linter_failure(linter, self)
        linter.post_test()

    def test_get_linter_version(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test()
        utilstest.test_get_linter_version(linter, self)
        linter.post_test()

    def test_get_linter_help(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test()
        utilstest.test_get_linter_help(linter, self)
        linter.post_test()

    def test_report_tap(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {"request_id": self.request_id, "report_type": "tap"}
        )
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test()
        utilstest.test_linter_report_tap(linter, self)
        linter.post_test()

    def test_report_sarif(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {"request_id": self.request_id, "report_type": "SARIF"}
        )
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test()
        utilstest.test_linter_report_sarif(linter, self)
        linter.post_test()

    def test_format_fix(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        linter = self.get_linter_instance(self.request_id)
        linter.pre_test()
        utilstest.test_linter_format_fix(linter, self)
        linter.post_test()
