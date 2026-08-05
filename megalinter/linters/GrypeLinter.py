#!/usr/bin/env python3
"""
Use GrypeLinter to lint Infrastructure as Code
"""

from megalinter import Linter, config


class GrypeLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if self.cli_lint_mode == "file":
            cmd.remove(file)

        return cmd

    # grype CLI --exclude replaces the exclude list of the config file:
    # re-emit the resolved config's entries alongside the excluded directories
    def manage_excluded_directories_config(self, cmd):
        if "--exclude" in cmd:
            return cmd
        return self.forward_excludes_with_config_list(
            cmd, ("--config",), "exclude", "--exclude", "**/{{DIR}}"
        )

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_GRYPE_FILE_NAMES_REGEX", ["package.*json"]
            )
