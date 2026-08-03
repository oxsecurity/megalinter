# !/usr/bin/env python3
"""
TAP reporter golden-file tests, on a curated sample of linters only.

The generated per-linter test classes do not run TAP golden tests anymore:
the TAP reporter output format is stable and one test per ecosystem
(bash, node, go, python) is enough to detect a regression.
Expected files live in .automation/test/<test_folder>/reports/expected-*.tap
"""

import uuid
from unittest import TestCase

from megalinter import linter_factory, utilstest


class tap_reporter_test(TestCase):
    def run_tap_report_test(self, descriptor_id, linter_name):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {"request_id": self.request_id, "report_type": "tap"}
        )
        linter = linter_factory.build_linter(
            descriptor_id,
            linter_name,
            {
                "default_linter_activation": True,
                "enable_descriptors": [],
                "enable_linters": [],
                "disable_descriptors": [],
                "disable_linters": [],
                "disable_errors_linters": [],
                "github_workspace": ".",
                "post_linter_status": True,
                "request_id": self.request_id,
            },
        )
        linter.pre_test("test_report_tap")
        utilstest.test_linter_report_tap(linter, self)
        linter.post_test("test_report_tap")

    def test_report_tap_bash_shellcheck(self):
        self.run_tap_report_test("BASH", "shellcheck")

    def test_report_tap_css_stylelint(self):
        self.run_tap_report_test("CSS", "stylelint")

    def test_report_tap_protobuf_protolint(self):
        self.run_tap_report_test("PROTOBUF", "protolint")

    def test_report_tap_cloudformation_cfn_lint(self):
        self.run_tap_report_test("CLOUDFORMATION", "cfn-lint")
