#!/usr/bin/env python3
"""
Use StyLua to check Lua code formatting
"""

from megalinter import Linter, utils


class StyLuaLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode through negated glob
        # patterns. Any -g value replaces stylua's default "**/*.lua" include,
        # so it must be restated before the negations
        if self.cli_lint_mode == "project" and not any(
            arg in ("-g", "--glob") for arg in cmd
        ):
            glob_args = ["-g", "**/*.lua"]
            for excluded_dir in sorted(utils.get_excluded_directories(self.request_id)):
                glob_args += ["-g", f"!**/{excluded_dir}/**"]
            if cmd[-1] == ".":
                cmd = cmd[:-1] + glob_args + ["."]
            else:
                cmd += glob_args

        return cmd
