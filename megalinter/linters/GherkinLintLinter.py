#!/usr/bin/env python3
"""
Use gherkin-lint to check Gherkin files
"""

from megalinter import Linter


class GherkinLintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: gherkin-lint --ignore
        # overrides the .gherkin-lintignore file, so merge its patterns in
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not any(arg in ("-i", "--ignore") for arg in cmd)
        ):
            patterns = self.read_workspace_file_lines(".gherkin-lintignore")
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
