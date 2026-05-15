#!/usr/bin/env python3
"""
Use Kingfisher Linter to find secrets
"""

from megalinter import Linter, config, utils


class KingfisherLinter(Linter):
    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(self.request_id, "REPOSITORY_KINGFISHER_FILE_EXTENSIONS", [".txt"])
