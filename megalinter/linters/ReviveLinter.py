#!/usr/bin/env python3
"""
Use Revive to lint go files
"""

from megalinter import Linter, config


class ReviveLinter(Linter):
    def pre_test(self, test_name):
        if test_name == "test_report_sarif":
            config.set_value(
                self.request_id, "GO_REVIVE_CONFIG_FILE", "revive_bad.toml"
            )
