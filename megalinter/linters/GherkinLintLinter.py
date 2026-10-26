#!/usr/bin/env python3
"""
Use gherkin-lint to check Gherkin files
"""

from megalinter import Linter


class GherkinLintLinter(Linter):
    # Forward excluded directories through --ignore, which overrides the
    # .gherkin-lintignore file: its patterns are merged in. Without that file,
    # gherkin-lint ignores node_modules/** by default, which --ignore replaces
    def manage_excluded_directories_config(self, cmd):
        if any(arg in ("-i", "--ignore") for arg in cmd):
            return cmd
        patterns = self.read_workspace_file_lines(".gherkin-lintignore")
        if any("," in pattern for pattern in patterns):
            # gherkin-lint splits --ignore on commas, which would cut a brace
            # pattern (ex: {a,b}/**) in two: keep the user's ignore file alone
            self.log_project_exclude_forwarding(
                f"EXCLUDED_DIRECTORIES are not forwarded to {self.linter_name}: "
                ".gherkin-lintignore holds patterns with commas, that its --ignore "
                "argument can not receive"
            )
            return cmd
        if len(patterns) == 0:
            patterns = ["node_modules/**"]
        for excluded_dir in self.get_project_exclude_directories():
            pattern = f"**/{excluded_dir}/**"
            if pattern not in patterns:
                patterns += [pattern]
        cmd += ["--ignore", ",".join(patterns)]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through "
            f"--ignore, merged with .gherkin-lintignore patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
