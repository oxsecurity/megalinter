#!/usr/bin/env python3
"""
Use yamllint to check YAML files
"""

import os

import yaml
from megalinter import Linter

YAMLLINT_BUILTIN_CONFIGS = ("default", "relaxed")


class YamllintLinter(Linter):
    # Forward excluded directories through a generated config extending the
    # resolved one, since yamllint has no CLI exclusion argument. An extending
    # config's ignore key replaces the parent's, so the effective user patterns
    # (found along the extends chain) are lifted and merged into the generated
    # config. ignore and ignore-from-file can not be combined: when the user
    # relies on ignore-from-file, the excluded directories go to an extra file
    def manage_excluded_directories_config(self, cmd):
        config_index = self.find_cli_argument_value_index(cmd, ("-c", "--config-file"))
        ignore_patterns = []
        ignore_files = []
        if config_index is not None:
            extends_value = cmd[config_index].replace("\\", "/")
            ignore_patterns, ignore_files = self.find_effective_ignore(
                cmd[config_index]
            )
        else:
            extends_value = "default"
        excluded_patterns = [
            f"{excluded_dir}/"
            for excluded_dir in self.get_project_exclude_directories()
        ]
        generated = {"extends": extends_value}
        if len(ignore_files) > 0:
            excluded_file = self.write_report_generated_file(
                "yamllint-excluded-directories.txt", excluded_patterns
            )
            generated["ignore-from-file"] = ignore_files + [
                excluded_file.replace("\\", "/")
            ]
        else:
            for pattern in excluded_patterns:
                if pattern not in ignore_patterns:
                    ignore_patterns += [pattern]
            generated["ignore"] = ignore_patterns
        generated_config = self.write_report_generated_file(
            "yamllint-config.yml", yaml.safe_dump(generated).splitlines()
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

    # The ignore setting in effect for a config: its own, else the one of the
    # config it extends. yamllint resolves extended file paths from the
    # working directory, which is the workspace
    def find_effective_ignore(self, config_path):
        visited = set()
        while True:
            if not os.path.isabs(config_path):
                config_path = os.path.join(self.workspace, config_path)
            if not os.path.isfile(config_path) or config_path in visited:
                break
            visited.add(config_path)
            with open(config_path, encoding="utf-8") as config_file:
                config_content = yaml.safe_load(config_file) or {}
            if not isinstance(config_content, dict):
                break
            if "ignore-from-file" in config_content:
                ignore_files = config_content["ignore-from-file"] or []
                if isinstance(ignore_files, str):
                    ignore_files = [ignore_files]
                return [], [str(ignore_file) for ignore_file in ignore_files]
            if "ignore" in config_content:
                ignore = config_content["ignore"] or []
                if isinstance(ignore, str):
                    return [
                        line.strip() for line in ignore.splitlines() if line.strip()
                    ], []
                return [str(pattern) for pattern in ignore], []
            extends = config_content.get("extends")
            if not isinstance(extends, str) or extends in YAMLLINT_BUILTIN_CONFIGS:
                break
            config_path = extends
        return [], []
