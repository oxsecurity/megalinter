#!/usr/bin/env python3
"""
Use ls-lint to check file and directory names
"""

import os

from megalinter import Linter


class LsLintLinter(Linter):
    # Forward excluded directories through an additional --config holding only
    # an ignore list: ls-lint merges repeated --config flags, appending their
    # ignore lists
    def manage_excluded_directories_config(self, cmd):
        if "--config" not in cmd:
            # Passing --config disables default discovery: re-add the
            # workspace config that ls-lint would have found by itself
            workspace_config = os.path.join(self.workspace, ".ls-lint.yml")
            if os.path.isfile(workspace_config):
                cmd += ["--config", workspace_config]
        # Literal root-level entries only: glob entries would make ls-lint
        # walk the whole tree once per pattern to expand them
        ignore_lines = ["ignore:"] + [
            f"  - {excluded_dir}"
            for excluded_dir in self.get_project_exclude_directories()
        ]
        generated_config = self.write_report_generated_file(
            "ls-lint-ignore.yml", ignore_lines
        )
        cmd += ["--config", generated_config]
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} to forward EXCLUDED_DIRECTORIES to "
            f"{self.linter_name} as an additional merged --config "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
