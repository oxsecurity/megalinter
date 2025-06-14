#!/usr/bin/env python3
"""
Use Detekt to lint kt files
"""
from megalinter import Linter, config


class DetektLinter(Linter):
    def pre_test(self, test_name):
        if test_name == "test_report_sarif":
            config.set_value(
                self.request_id, "KOTLIN_DETEKT_CONFIG_FILE", "detekt-config_bad.yml"
            )
