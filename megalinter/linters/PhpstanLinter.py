#!/usr/bin/env python3
"""
Use PHPStan to analyze PHP files
"""

import os

from megalinter import Linter


class PhpstanLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
        ):
            cmd = self.manage_excluded_directories_config(cmd)

        return cmd

    # Forward excluded directories through a generated neon config including
    # the resolved one: phpstan merges excludePaths arrays across includes, and
    # fnmatch patterns stay valid wherever the generated config lives
    def manage_excluded_directories_config(self, cmd):
        existing_config_index = None
        for index, arg in enumerate(cmd):
            if arg in ("-c", "--configuration") and index + 1 < len(cmd):
                existing_config_index = index + 1
                break
        config_lines = []
        if existing_config_index is not None:
            included_config = cmd[existing_config_index].replace("\\", "/")
            config_lines += ["includes:", f"    - {included_config}"]
        config_lines += ["parameters:", "    excludePaths:"]
        for excluded_dir in self.get_project_exclude_directories():
            config_lines += [f"        - */{excluded_dir}/*"]
        generated_config = os.path.join(self.report_folder, "phpstan-config.neon")
        os.makedirs(self.report_folder, exist_ok=True)
        with open(generated_config, "w", encoding="utf-8") as config_file:
            config_file.write("\n".join(config_lines) + "\n")
        if existing_config_index is not None:
            cmd[existing_config_index] = generated_config
        else:
            cmd += ["-c", generated_config]
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} to forward EXCLUDED_DIRECTORIES to "
            f"{self.linter_name} as merged excludePaths patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
