#!/usr/bin/env python3
"""
Use Luacheck to check Lua files
"""

from megalinter import Linter


class LuacheckLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode. --exclude-files greedily
        # consumes following positional arguments, so it must come last, after
        # the "." path provided by cli_lint_mode_project_extra_args_after
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and len(self.get_project_exclude_directories()) > 0
            and "--exclude-files" not in cmd
        ):
            cmd += ["--exclude-files"] + [
                f"**/{excluded_dir}"
                for excluded_dir in self.get_project_exclude_directories()
            ]
            self.log_project_exclude_forwarding(
                f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through "
                f"--exclude-files "
                f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
            )

        return cmd
