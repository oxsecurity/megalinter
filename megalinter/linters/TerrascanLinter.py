#!/usr/bin/env python3
"""
Use Terrascan to lint terraform files
https://github.com/tenable/terrascan
"""
import logging

import megalinter


class TerrascanLinter(megalinter.Linter):
    # To execute before linting files
    def before_lint_files(self):
        # Build pre-command
        terrascan_init_command = "terrascan"
        if self.config_file is not None:
            terrascan_init_command += f" --config-path {self.config_file}"
        logging.debug("terrascan before_lint_files: " + terrascan_init_command)
        # Add to pre-commands
        terrascan_pre_command = {
            "command": terrascan_init_command,
            "cwd": self.workspace,
        }
        if self.pre_commands is None:
            self.pre_commands = []
        self.pre_commands.append(terrascan_pre_command)
