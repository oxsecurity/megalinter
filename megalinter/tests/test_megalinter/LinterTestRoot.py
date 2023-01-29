# !/usr/bin/env python3
"""
Unit tests for Linter class (and sub-classes)
"""
from typing import Optional

from megalinter import config, linter_factory
from megalinter.tests.test_megalinter.helpers import utilstest


class LinterTestRoot:
    descriptor_id: Optional[str] = None
    linter_name: Optional[str] = None

    def get_linter_instance(self):
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
            },
        )

    def test_success(self):
        utilstest.linter_test_setup()
        linter = self.get_linter_instance()
        linter.pre_test()
        utilstest.test_linter_success(linter, self)
        linter.post_test()

    def test_failure(self):
        utilstest.linter_test_setup()
        linter = self.get_linter_instance()
        linter.pre_test()
        utilstest.test_linter_failure(linter, self)
        linter.post_test()

    def test_get_linter_version(self):
        utilstest.linter_test_setup()
        linter = self.get_linter_instance()
        linter.pre_test()
        utilstest.test_get_linter_version(linter, self)
        linter.post_test()

    def test_get_linter_help(self):
        utilstest.linter_test_setup()
        linter = self.get_linter_instance()
        linter.pre_test()
        utilstest.test_get_linter_help(linter, self)
        linter.post_test()

    def test_report_tap(self):
        utilstest.linter_test_setup({"report_type": "tap"})
        linter = self.get_linter_instance()
        linter.pre_test()
        utilstest.test_linter_report_tap(linter, self)
        linter.post_test()

    def test_report_sarif(self):
        utilstest.linter_test_setup({"report_type": "SARIF"})
        linter = self.get_linter_instance()
        linter.pre_test()
        utilstest.test_linter_report_sarif(self.get_linter_instance(), self)
        linter.post_test()

    def test_format_fix(self):
        utilstest.linter_test_setup()

        if self.linter_name == "prettier":
            config.set_value("JAVASCRIPT_DEFAULT_STYLE", "prettier")

        if self.linter_name == "standard":
            config.set_value("JAVASCRIPT_DEFAULT_STYLE", "standard")

        if self.linter_name == "xmllint":
            config.set_value("XML_XMLLINT_AUTOFORMAT", "true")
            config.set_value("XML_XMLLINT_CLI_LINT_MODE", "file")

        linter = self.get_linter_instance()

        if self.linter_name == "standard":
            config.set_value(
                "JAVASCRIPT_STANDARD_ARGUMENTS",
                config.get("DEFAULT_WORKSPACE").replace("\\", "/")
                + f"/{linter.test_folder}/*_fix_*.js",
            )

        utilstest.test_linter_format_fix(linter, self)
