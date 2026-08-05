#!/usr/bin/env python3
"""
Use PHP CS Fixer to check PHP code formatting
"""

import os

from megalinter import Linter


class PhpCsFixerLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode through a generated PHP
        # config requiring the resolved one and chaining Finder exclusions.
        # Only applied when a config is passed: php-cs-fixer configs are code,
        # so there is no resolved file to extend otherwise
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
        ):
            existing_config_index = None
            for index, arg in enumerate(cmd):
                if arg == "--config" and index + 1 < len(cmd):
                    existing_config_index = index + 1
                    break
            if existing_config_index is not None:
                included_config = cmd[existing_config_index].replace("\\", "/")
                exclude_dirs = ", ".join(
                    f"'{excluded_dir}'"
                    for excluded_dir in self.get_project_exclude_directories()
                )
                config_lines = [
                    "<?php",
                    f"$config = require '{included_config}';",
                    f"$config->getFinder()->exclude([{exclude_dirs}]);",
                    "return $config;",
                ]
                generated_config = os.path.join(
                    self.report_folder, "php-cs-fixer-config.php"
                )
                os.makedirs(self.report_folder, exist_ok=True)
                with open(generated_config, "w", encoding="utf-8") as config_file:
                    config_file.write("\n".join(config_lines) + "\n")
                cmd[existing_config_index] = generated_config
                self.log_project_exclude_forwarding(
                    f"Generated {generated_config} chaining {included_config} with "
                    f"EXCLUDED_DIRECTORIES as Finder exclusions "
                    f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
                )

        return cmd
