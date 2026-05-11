#!/usr/bin/env python3
"""
Use Checkov to lint Infrastructure as Code
"""

import megalinter.utils as utils
from megalinter import Linter, config


class CheckovLinter(Linter):
    def pre_test(self, test_name):
        config.set_value(
            self.request_id, "REPOSITORY_CHECKOV_FILE_NAMES_REGEX", ["Dockerfile"]
        )
        config.set_value(self.request_id, "REPOSITORY_CHECKOV_FILE_EXTENSIONS", [".tf"])