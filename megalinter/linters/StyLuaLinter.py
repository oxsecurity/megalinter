#!/usr/bin/env python3
"""
Use StyLua to check Lua code formatting
"""

from megalinter import Linter


class StyLuaLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode through negated glob
        # patterns. Any -g value replaces stylua's default "**/*.lua" include,
        # so it must be restated before the negations
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not any(arg in ("-g", "--glob") for arg in cmd)
        ):
            glob_args = ["-g", "**/*.lua"]
            for excluded_dir in self.get_project_exclude_directories():
                glob_args += ["-g", f"!**/{excluded_dir}/**"]
            if cmd[-1] == ".":
                cmd = cmd[:-1] + glob_args + ["."]
            else:
                cmd += glob_args
            self.log_project_exclude_forwarding(
                f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through "
                f"-g negated globs "
                f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
            )

        return cmd
