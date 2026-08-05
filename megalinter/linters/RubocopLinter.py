#!/usr/bin/env python3
"""
Use RuboCop to check Ruby files
"""

import os

from megalinter import Linter


class RubocopLinter(Linter):
    # Forward excluded directories through a generated config inheriting the
    # resolved one, since rubocop has no CLI path exclusion argument.
    # inherit_mode merge keeps inherited and default Exclude entries, and
    # absolute patterns stay valid wherever the generated config lives
    def manage_excluded_directories_config(self, cmd):
        config_index = self.find_cli_argument_value_index(cmd, ("-c", "--config"))
        workspace_abs = os.path.abspath(self.workspace).replace("\\", "/")
        config_lines = []
        if config_index is not None:
            inherited = cmd[config_index].replace("\\", "/")
            config_lines += ["inherit_from:", f"  - {inherited}"]
        config_lines += [
            "inherit_mode:",
            "  merge:",
            "    - Exclude",
            "AllCops:",
            "  Exclude:",
        ]
        for excluded_dir in self.get_project_exclude_directories():
            config_lines += [
                f"    - '{workspace_abs}/{excluded_dir}/**/*'",
                f"    - '{workspace_abs}/**/{excluded_dir}/**/*'",
            ]
        generated_config = self.write_report_generated_file(
            "rubocop-config.yml", config_lines
        )
        cmd = self.replace_or_append_cli_argument(
            cmd, config_index, "-c", generated_config
        )
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} to forward EXCLUDED_DIRECTORIES to "
            f"{self.linter_name} as merged AllCops Exclude patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
