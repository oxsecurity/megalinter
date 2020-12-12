# !/usr/bin/env python3
"""
Unit tests for Linter class (and sub-classes)
"""
from megalinter import linter_factory
from megalinter.tests.test_megalinter.helpers import utilstest


class LinterTestRoot:
    descriptor_id = None
    linter_name = None

    def get_linter_instance(self):
        return linter_factory.build_linter(self.descriptor_id, self.linter_name)

    def test_success(self):
        utilstest.linter_test_setup()
        utilstest.test_linter_success(self.get_linter_instance(), self)

    def test_failure(self):
        utilstest.linter_test_setup()
        utilstest.test_linter_failure(self.get_linter_instance(), self)

    def test_get_linter_version(self):
        utilstest.linter_test_setup()
        utilstest.test_get_linter_version(self.get_linter_instance(), self)

    def test_get_linter_help(self):
        utilstest.linter_test_setup()
        utilstest.test_get_linter_help(self.get_linter_instance(), self)

    def test_report_tap(self):
        utilstest.linter_test_setup({"report_type": "tap"})
        utilstest.test_linter_report_tap(self.get_linter_instance(), self)
