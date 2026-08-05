#!/usr/bin/env python3
"""
Use Luacheck to check Lua files
"""

from megalinter import Linter, utils


class LuacheckLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode. --exclude-files greedily
        # consumes following positional arguments, so it must come last, after
        # the "." path provided by cli_lint_mode_project_extra_args_after
        if self.cli_lint_mode == "project" and "--exclude-files" not in cmd:
            cmd += ["--exclude-files"] + [
                f"**/{excluded_dir}"
                for excluded_dir in sorted(
                    utils.get_excluded_directories(self.request_id)
                )
            ]

        return cmd
