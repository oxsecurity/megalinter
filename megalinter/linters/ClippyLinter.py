#!/usr/bin/env python3
"""
Use Clippy to lint rust files
"""

import logging
import os

import megalinter
from megalinter import config


class ClippyLinter(megalinter.Linter):
    # To execute before linting files
    def before_lint_files(self):
        # The image installs a single pinned toolchain and makes it the default
        # in RUSTUP_HOME: switching to "stable" there would download a second one
        rustup_home = config.get(
            self.request_id,
            "RUSTUP_HOME",
            os.path.expandvars("${HOME}/.rustup"),
        )
        rustup_settings = os.path.join(rustup_home, "settings.toml")
        if not os.path.isfile(rustup_settings):
            rustup_init_command = 'echo "Init RUST toolkit" && rustup default stable'
            if self.pre_commands is None:
                self.pre_commands = []
            # Add to pre-commands
            logging.debug("clippy before_lint_files: " + rustup_init_command)
            self.pre_commands.append(
                {"command": rustup_init_command, "cwd": self.workspace}
            )
        else:
            logging.debug("RUST settings found: " + rustup_settings)
