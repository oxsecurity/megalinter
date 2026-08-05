#!/usr/bin/env python3
"""
Use Devskim to lint Infrastructure as Code
"""

import yaml
from megalinter import Linter, config

# devskim -g replaces its default ignore globs, so they must be re-included
DEVSKIM_DEFAULT_IGNORE_GLOBS = ["**/.git/**", "**/bin/**"]


class DevskimLinter(Linter):
    # devskim -g is a single comma-separated occurrence replacing both its
    # built-in default globs and the Globs list of the resolved config file:
    # re-emit both alongside the excluded directories
    def manage_excluded_directories_config(self, cmd):
        if any(arg in ("-g", "--ignore-globs") for arg in cmd):
            return cmd
        ignore_globs = list(DEVSKIM_DEFAULT_IGNORE_GLOBS)
        config_index = self.find_cli_argument_value_index(cmd, ("--options-json",))
        if config_index is not None:
            with open(cmd[config_index], encoding="utf-8") as config_file:
                config_globs = (yaml.safe_load(config_file) or {}).get("Globs", [])
            for config_glob in config_globs:
                if config_glob not in ignore_globs:
                    ignore_globs += [config_glob]
        for excluded_dir in self.get_project_exclude_directories():
            glob = f"**/{excluded_dir}/**"
            if glob not in ignore_globs:
                ignore_globs += [glob]
        cmd += ["-g", ",".join(ignore_globs)]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through -g, "
            f"merged with devskim default and configured ignore globs "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_DEVSKIM_FILE_EXTENSIONS", [".sh"]
            )
