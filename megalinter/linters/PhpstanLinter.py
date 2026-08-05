#!/usr/bin/env python3
"""
Use PHPStan to analyze PHP files
"""

from megalinter import Linter


class PhpstanLinter(Linter):
    # Forward excluded directories through a generated neon config including
    # the resolved one: phpstan merges excludePaths arrays across includes, and
    # fnmatch patterns stay valid wherever the generated config lives
    def manage_excluded_directories_config(self, cmd):
        config_index = self.find_cli_argument_value_index(
            cmd, ("-c", "--configuration")
        )
        config_lines = []
        if config_index is not None:
            included_config = cmd[config_index].replace("\\", "/")
            config_lines += ["includes:", f"    - {included_config}"]
        config_lines += ["parameters:", "    excludePaths:"]
        for excluded_dir in self.get_project_exclude_directories():
            config_lines += [f"        - */{excluded_dir}/*"]
        generated_config = self.write_report_generated_file(
            "phpstan-config.neon", config_lines
        )
        cmd = self.replace_or_append_cli_argument(
            cmd, config_index, "-c", generated_config
        )
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} to forward EXCLUDED_DIRECTORIES to "
            f"{self.linter_name} as merged excludePaths patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
