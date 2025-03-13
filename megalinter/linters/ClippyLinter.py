#!/usr/bin/env python3
"""
Use Clippy to lint rust files
"""
import logging
import os

import megalinter


class ClippyLinter(megalinter.Linter):
    # To execute before linting files
    def before_lint_files(self):
        # Build pre-command
        if not os.path.isfile(os.path.expandvars("${HOME}/.rustup/settings.toml")):
            rustup_init_command = 'echo "Init RUST toolkit" && rustup default stable'
            if self.pre_commands is None:
                self.pre_commands = []
            # Add to pre-commands
            logging.debug("clippy before_lint_files: " + rustup_init_command)
            self.pre_commands.append(
                {"command": rustup_init_command, "cwd": self.workspace}
            )
        else:
            logging.debug(
                "RUST settings found: "
                + os.path.expandvars("${HOME}/.rustup/settings.toml")
            )
