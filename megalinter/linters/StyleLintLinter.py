#!/usr/bin/env python3
"""
Use StyleLint to lint css, scss and saas files
"""

from megalinter import Linter, config


class StyleLintLinter(Linter):
    def pre_test(self, test_name):
        if test_name == "test_failure":
            config.set_value(
                self.request_id, "CSS_STYLELINT_CONFIG_FILE", ".stylelintrc_bad.json"
            )
