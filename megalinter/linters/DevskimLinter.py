#!/usr/bin/env python3
"""
Use Devskim to lint Infrastructure as Code
"""

from megalinter import Linter, config


class DevskimLinter(Linter):
    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_DEVSKIM_FILE_EXTENSIONS", [".sh"]
            )
