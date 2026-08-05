#!/usr/bin/env python3
"""
Use PHP CS Fixer to check PHP code formatting
"""

from megalinter import Linter


class PhpCsFixerLinter(Linter):
    # Forward excluded directories through a generated PHP config requiring
    # the resolved one and chaining Finder exclusions. Only applied when a
    # config is passed: php-cs-fixer configs are code, so there is no
    # resolved file to extend otherwise
    def manage_excluded_directories_config(self, cmd):
        config_index = self.find_cli_argument_value_index(cmd, ("--config",))
        if config_index is None:
            return cmd
        included_config = cmd[config_index].replace("\\", "/")
        exclude_dirs = ", ".join(
            f"'{excluded_dir}'"
            for excluded_dir in self.get_project_exclude_directories()
        )
        generated_config = self.write_report_generated_file(
            "php-cs-fixer-config.php",
            [
                "<?php",
                "",
                f"$config = require '{included_config}';",
                f"$config->getFinder()->exclude([{exclude_dirs}]);",
                "return $config;",
            ],
        )
        cmd[config_index] = generated_config
        self.php_cs_fixer_generated_config = True
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} chaining {included_config} with "
            f"EXCLUDED_DIRECTORIES as Finder exclusions "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd

    # A path argument makes php-cs-fixer override the config Finder entirely
    # ("Paths from configuration have been overridden"): drop the trailing "."
    # so the generated config's Finder exclusions actually apply
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        if (
            getattr(self, "php_cs_fixer_generated_config", False) is True
            and len(cmd) > 0
            and cmd[-1] == "."
        ):
            cmd = cmd[:-1]
        return cmd
