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
            if self.is_project_exclude_forwarding_active():
                cmd += ["--exclude-paths=" + self.build_exclude_paths_file()]
            else:
                cmd += [
                    "--exclude-paths="
                    + utils.get_default_rules_location()
                    + "/.trufflehogignore"
                ]

        return cmd

    # Merge ignore rules with excluded directories, so trufflehog does not
    # crawl heavy directories like node_modules or build caches. A workspace
    # .trufflehogignore takes precedence over the default embedded rules.
    # Cached: build_lint_command runs once per file in file lint mode
    def build_exclude_paths_file(self):
        cached_file = getattr(self, "trufflehog_exclude_paths_file", None)
        if cached_file is not None:
            return cached_file
        workspace_ignore_file = os.path.join(self.workspace, ".trufflehogignore")
        default_trufflehog_ignore_file = (
            utils.get_default_rules_location() + "/.trufflehogignore"
        )
        seed_ignore_file = (
            workspace_ignore_file
            if os.path.isfile(workspace_ignore_file)
            else default_trufflehog_ignore_file
        )
        exclude_regexes = []
        if os.path.isfile(seed_ignore_file):
            with open(seed_ignore_file, "r", encoding="utf-8") as ignore_file:
                exclude_regexes = [
                    line.strip() for line in ignore_file if line.strip() != ""
                ]
        for excluded_dir in self.get_project_exclude_directories():
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
        self.trufflehog_exclude_paths_file = exclude_paths_file
        return exclude_paths_file

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_TRUFFLEHOG_FILE_EXTENSIONS", [".keys"]
            )
