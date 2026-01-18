#!/usr/bin/env python3
"""
Use Eslint to check so many file formats :)
"""

import os

from megalinter import Linter


class EslintLinter(Linter):
    def is_flat_config(self):
        """
        Detect if ESLint flat config is being used.
        Flat config files: eslint.config.js, eslint.config.mjs, eslint.config.cjs
        """
        flat_config_files = [
            "eslint.config.js",
            "eslint.config.mjs",
            "eslint.config.cjs",
        ]

        # Check if config_file_name points to a flat config file
        if self.config_file_name in flat_config_files:
            return True

        # Check if a flat config file exists in workspace
        for config_file in flat_config_files:
            if os.path.isfile(os.path.join(self.workspace, config_file)):
                return True

        return False

    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Handle flat config vs eslintrc
        if self.is_flat_config():
            # Remove flags that are incompatible with flat config
            cmd = list(filter(lambda a: a not in ["--no-eslintrc", "--no-ignore"], cmd))
            # Remove --ignore-path and its value
            if "--ignore-path" in cmd:
                idx = cmd.index("--ignore-path")
                # Remove both --ignore-path and the following path argument
                cmd.pop(idx)
                if idx < len(cmd):
                    cmd.pop(idx)
        else:
            # eslintrc format: Remove --no-ignore if there are arguments about ignoring stuff
            if "--ignore-path" in cmd or "--ignore-pattern" in cmd:
                cmd = list(filter(lambda a: a != "--no-ignore", cmd))

        if self.cli_lint_mode == "project":
            cmd.append(".")

        return cmd

