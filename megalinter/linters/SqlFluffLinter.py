#!/usr/bin/env python3
"""
Use SqlFluff to lint any type of file according to local config
"""

import configparser
import logging

from megalinter import Linter

IGNORE_PATHS_KEY = "ignore_paths"
CORE_SECTION = "sqlfluff"
GENERATED_CONFIG_NAME = "sqlfluff-megalinter.cfg"


class SqlFluffLinter(Linter):

    # Manage case when we want to add --show-lint-violations when fix mode is active
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        # if fix arg is in the arguments, add --show-lint-violations just after
        if (
            self.apply_fixes is True
            and self.cli_lint_fix_arg_name is not None
            and self.cli_lint_fix_arg_name in cmd
        ):
            fix_index = cmd.index(self.cli_lint_fix_arg_name)
            cmd = (
                cmd[: fix_index + 1]
                + ["--show-lint-violations"]
                + cmd[fix_index + 1 :]  # noqa: E203
            )
            logging.debug("[SqlFluffLinter] Added --show-lint-violations argument")
        return cmd

    # sqlfluff has no CLI exclusion argument, and its .sqlfluffignore files are
    # only discovered inside the analyzed sources, where MegaLinter must not
    # write. Excluded directories are forwarded through the ignore_paths key of
    # a copy of the resolved configuration, generated in the report folder
    def manage_excluded_directories_config(self, cmd):
        excluded_dirs = self.get_project_exclude_directories()
        if len(excluded_dirs) == 0:
            return cmd
        parser = configparser.ConfigParser()
        if self.final_config_file is not None:
            parser.read(self.final_config_file, encoding="utf-8")
        if not parser.has_section(CORE_SECTION):
            parser.add_section(CORE_SECTION)
        # Patterns follow .sqlfluffignore syntax: a trailing / matches the
        # directory at any level of the analyzed tree
        ignore_paths = [
            value.strip()
            for value in parser.get(CORE_SECTION, IGNORE_PATHS_KEY, fallback="").split(
                ","
            )
            if value.strip() != ""
        ]
        for excluded_dir in excluded_dirs:
            pattern = f"{excluded_dir}/"
            if pattern not in ignore_paths:
                ignore_paths.append(pattern)
        parser.set(CORE_SECTION, IGNORE_PATHS_KEY, ",".join(ignore_paths))
        config_lines = []
        for section in parser.sections():
            config_lines += [f"[{section}]"]
            config_lines += [f"{key} = {value}" for key, value in parser.items(section)]
            config_lines += [""]
        generated_config_file = self.write_report_generated_file(
            GENERATED_CONFIG_NAME, config_lines
        )
        value_index = self.find_cli_argument_value_index(cmd, ["--config"])
        cmd = self.replace_or_append_cli_argument(
            cmd, value_index, "--config", generated_config_file
        )
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through the "
            f"{IGNORE_PATHS_KEY} key of {generated_config_file} "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
