#!/usr/bin/env python3
"""
Use SwiftLint to check Swift files
"""

import os

from megalinter import Linter


class SwiftLintLinter(Linter):
    # Forward excluded directories through a generated config, since swiftlint
    # has no CLI path exclusion argument. The workspace .swiftlint.yml that
    # swiftlint would have auto-discovered is chained as parent_config
    # (relative to the generated config), and excluded entries use absolute
    # paths so their base does not matter
    def manage_excluded_directories_config(self, cmd):
        if "--config" in cmd:
            return cmd
        workspace_abs = os.path.abspath(self.workspace).replace("\\", "/")
        config_lines = []
        workspace_config = os.path.join(self.workspace, ".swiftlint.yml")
        if os.path.isfile(workspace_config):
            parent_relative = os.path.relpath(
                workspace_config, self.report_folder
            ).replace("\\", "/")
            config_lines += [f"parent_config: {parent_relative}"]
        config_lines += ["excluded:"]
        for excluded_dir in self.get_project_exclude_directories():
            config_lines += [
                f"  - '{workspace_abs}/{excluded_dir}'",
                f"  - '{workspace_abs}/**/{excluded_dir}'",
            ]
        generated_config = self.write_report_generated_file(
            "swiftlint-config.yml", config_lines
        )
        cmd += ["--config", generated_config]
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} to forward EXCLUDED_DIRECTORIES to "
            f"{self.linter_name} as excluded paths "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
