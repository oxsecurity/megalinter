#!/usr/bin/env python3
"""
Use yamllint to check YAML files
"""

import yaml
from megalinter import Linter


class YamllintLinter(Linter):
    # Forward excluded directories through a generated config extending the
    # resolved one, since yamllint has no CLI exclusion argument. An extending
    # config's ignore key replaces the parent's, so the parent patterns are
    # lifted and merged into the generated config
    def manage_excluded_directories_config(self, cmd):
        config_index = self.find_cli_argument_value_index(cmd, ("-c", "--config-file"))
        ignore_patterns = []
        if config_index is not None:
            extends_value = cmd[config_index].replace("\\", "/")
            with open(cmd[config_index], encoding="utf-8") as config_file:
                existing_config = yaml.safe_load(config_file) or {}
            if "ignore-from-file" in existing_config:
                # ignore and ignore-from-file cannot be combined: keep the
                # user's configuration untouched
                return cmd
            existing_ignore = existing_config.get("ignore", [])
            if isinstance(existing_ignore, str):
                ignore_patterns += [
                    line.strip()
                    for line in existing_ignore.splitlines()
                    if line.strip()
                ]
            else:
                ignore_patterns += existing_ignore
        else:
            extends_value = "default"
        for excluded_dir in self.get_project_exclude_directories():
            pattern = f"{excluded_dir}/"
            if pattern not in ignore_patterns:
                ignore_patterns += [pattern]
        generated_config = self.write_report_generated_file(
            "yamllint-config.yml",
            yaml.safe_dump(
                {"extends": extends_value, "ignore": ignore_patterns}
            ).splitlines(),
        )
        cmd = self.replace_or_append_cli_argument(
            cmd, config_index, "-c", generated_config
        )
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} extending {extends_value} with "
            f"EXCLUDED_DIRECTORIES as ignore patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
