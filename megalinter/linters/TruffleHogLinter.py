#!/usr/bin/env python3
"""
Use TruffleHog Linter to find secrets
"""

import os
import re

from megalinter import Linter, config, utils


class TruffleHogLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if not any(arg.startswith("--exclude-paths") for arg in cmd):
            cmd += ["--exclude-paths=" + self.build_exclude_paths_file()]

        return cmd

    # Merge default ignore rules with excluded directories, so trufflehog
    # does not crawl heavy directories like node_modules or build caches
    def build_exclude_paths_file(self):
        default_rules_location = utils.get_default_rules_location()
        default_trufflehog_ignore_file = default_rules_location + "/.trufflehogignore"
        exclude_regexes = []
        if os.path.isfile(default_trufflehog_ignore_file):
            with open(
                default_trufflehog_ignore_file, "r", encoding="utf-8"
            ) as ignore_file:
                exclude_regexes = [
                    line.strip() for line in ignore_file if line.strip() != ""
                ]
        for excluded_dir in sorted(utils.get_excluded_directories(self.request_id)):
            # Unanchored regex: matches the directory at any nesting level,
            # consistently with EXCLUDED_DIRECTORIES behavior in file listing
            excluded_dir_regex = re.escape(excluded_dir.replace("\\", "/")) + "/"
            if excluded_dir_regex not in exclude_regexes:
                exclude_regexes += [excluded_dir_regex]
        exclude_paths_file = os.path.join(
            self.report_folder, "trufflehog-exclude-paths.txt"
        )
        os.makedirs(self.report_folder, exist_ok=True)
        with open(exclude_paths_file, "w", encoding="utf-8") as exclude_file:
            exclude_file.write("\n".join(exclude_regexes) + "\n")
        return exclude_paths_file

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_TRUFFLEHOG_FILE_EXTENSIONS", [".keys"]
            )
