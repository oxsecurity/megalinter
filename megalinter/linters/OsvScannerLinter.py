#!/usr/bin/env python3
"""
Use OsvScannerLinter to lint Infrastructure as Code
"""

from megalinter import Linter, config


class OsvScannerLinter(Linter):
    def pre_test(self, test_name):
        if test_name.endswith("file_lint_mode") or test_name.endswith("list_of_files_lint_mode"):
            config.set_value(self.request_id, "REPOSITORY_OSV_SCANNER_FILE_NAMES_REGEX", ["package.*json"])
