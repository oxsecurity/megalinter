#!/usr/bin/env python3
"""
Use StyLua to check Lua code formatting
"""

from megalinter import Linter


class StyLuaLinter(Linter):
    # Forward excluded directories through negated glob patterns. Any -g value
    # replaces stylua's default "**/*.lua" include, so it must be restated
    # before the negations
    def manage_excluded_directories_config(self, cmd):
        if any(arg in ("-g", "--glob") for arg in cmd):
            return cmd
        cmd += ["-g", "**/*.lua"]
        for excluded_dir in self.get_project_exclude_directories():
            cmd += ["-g", f"!**/{excluded_dir}/**"]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through "
            f"-g negated globs "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
