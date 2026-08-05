#!/usr/bin/env python3
"""
Use ls-lint to check file and directory names
"""

import os

from megalinter import Linter


class LsLintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode through an additional
        # --config holding only an ignore list: ls-lint merges repeated
        # --config flags, appending their ignore lists
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
        ):
            if "--config" not in cmd:
                # Passing --config disables default discovery: re-add the
                # workspace config that ls-lint would have found by itself
                workspace_config = os.path.join(self.workspace, ".ls-lint.yml")
                if os.path.isfile(workspace_config):
                    cmd += ["--config", workspace_config]
            ignore_lines = ["ignore:"]
            for excluded_dir in self.get_project_exclude_directories():
                ignore_lines += [f"  - {excluded_dir}", f"  - '**/{excluded_dir}'"]
            generated_config = os.path.join(self.report_folder, "ls-lint-ignore.yml")
            os.makedirs(self.report_folder, exist_ok=True)
            with open(generated_config, "w", encoding="utf-8") as config_file:
                config_file.write("\n".join(ignore_lines) + "\n")
            cmd += ["--config", generated_config]
            self.log_project_exclude_forwarding(
                f"Generated {generated_config} to forward EXCLUDED_DIRECTORIES to "
                f"{self.linter_name} as an additional merged --config "
                f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
            )

        return cmd
