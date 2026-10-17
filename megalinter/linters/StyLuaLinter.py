#!/usr/bin/env python3
"""
Use StyLua to check Lua code formatting
"""

from megalinter import Linter


class StyLuaLinter(Linter):
    # Forward excluded directories through negated glob patterns. Any -g value
    # replaces stylua's default "**/*.lua" + "**/*.luau" includes, so they must
    # be restated before the negations. -g globs are overrides, taking
    # precedence over the ignore files for files: the file patterns of the root
    # .styluaignore and .gitignore are restated as negations so they still apply
    def manage_excluded_directories_config(self, cmd):
        if any(arg in ("-g", "--glob") for arg in cmd):
            return cmd
        cmd += ["-g", "**/*.lua", "-g", "**/*.luau"]
        for ignore_file in [".gitignore", ".styluaignore"]:
            patterns = [
                pattern
                for pattern in self.read_workspace_file_lines(ignore_file)
                if not pattern.startswith("#")
            ]
            if any(pattern.startswith("!") for pattern in patterns):
                # A negation can not be restated as an override: an allowlist
                # (ex: "/*" then "!/src/") would turn into "ignore everything"
                self.log_project_exclude_forwarding(
                    f"The file patterns of {ignore_file} are not restated for "
                    f"{self.linter_name}, as it holds negated (!) patterns"
                )
                continue
            for pattern in patterns:
                cmd += ["-g", f"!{pattern}"]
        for excluded_dir in self.get_project_exclude_directories():
            cmd += ["-g", f"!**/{excluded_dir}/**"]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through "
            f"-g negated globs, with the root .styluaignore and .gitignore patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
