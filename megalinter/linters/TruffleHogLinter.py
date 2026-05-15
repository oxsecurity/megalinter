#!/usr/bin/env python3
"""
Use TruffleHog Linter to find secrets
"""

from megalinter import Linter, config, utils


class TruffleHogLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if not any(arg.startswith("--exclude-paths") for arg in cmd):
            default_rules_location = utils.get_default_rules_location()
            default_trufflehog_ignore_file = (
                default_rules_location + "/.trufflehogignore"
            )
            exclude_arg = "--exclude-paths=" + default_trufflehog_ignore_file
            cmd += [exclude_arg]

        return cmd

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(self.request_id, "REPOSITORY_TRUFFLEHOG_FILE_EXTENSIONS", [".keys"])
