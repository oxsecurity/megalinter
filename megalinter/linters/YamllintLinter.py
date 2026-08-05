#!/usr/bin/env python3
"""
Use yamllint to check YAML files
"""

import os

import yaml
from megalinter import Linter


class YamllintLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
        ):
            cmd = self.manage_excluded_directories_config(cmd)

        return cmd

    # Forward excluded directories through a generated config extending the
    # resolved one, since yamllint has no CLI exclusion argument. An extending
    # config's ignore key replaces the parent's, so the parent patterns are
    # lifted and merged into the generated config
    def manage_excluded_directories_config(self, cmd):
        existing_config_index = None
        for index, arg in enumerate(cmd):
            if arg in ("-c", "--config-file") and index + 1 < len(cmd):
                existing_config_index = index + 1
                break
        ignore_patterns = []
        if existing_config_index is not None:
            extends_value = cmd[existing_config_index].replace("\\", "/")
            with open(cmd[existing_config_index], encoding="utf-8") as config_file:
                existing_config = yaml.safe_load(config_file) or {}
            if "ignore-from-file" in existing_config:
                # ignore and ignore-from-file cannot be combined: keep the
                # user's configuration untouched
                return cmd
            existing_ignore = existing_config.get("ignore", [])
            if isinstance(existing_ignore, str):
                ignore_patterns += [
                    line.strip() for line in existing_ignore.splitlines() if line.strip()
                ]
            else:
                ignore_patterns += existing_ignore
        else:
            extends_value = "default"
        for excluded_dir in self.get_project_exclude_directories():
            pattern = f"{excluded_dir}/"
            if pattern not in ignore_patterns:
                ignore_patterns += [pattern]
        generated_config_content = {
            "extends": extends_value,
            "ignore": ignore_patterns,
        }
        generated_config = os.path.join(self.report_folder, "yamllint-config.yml")
        os.makedirs(self.report_folder, exist_ok=True)
        with open(generated_config, "w", encoding="utf-8") as config_file:
            yaml.safe_dump(generated_config_content, config_file)
        if existing_config_index is not None:
            cmd[existing_config_index] = generated_config
        else:
            cmd += ["-c", generated_config]
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} extending {extends_value} with "
            f"EXCLUDED_DIRECTORIES as ignore patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
