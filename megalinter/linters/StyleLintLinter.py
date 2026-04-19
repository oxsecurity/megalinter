#!/usr/bin/env python3
"""
Use StyleLint to lint css, scss and saas files
"""

import os

from megalinter import Linter, config

NODE_DEPS_DIR = "/node-deps"


class StyleLintLinter(Linter):
    def pre_test(self, test_name):
        if test_name == "test_failure":
            config.set_value(
                self.request_id, "CSS_STYLELINT_CONFIG_FILE", ".stylelintrc_bad.json"
            )

    def build_lint_command(self, file=None) -> list:
        cmd = super().build_lint_command(file)
        # stylelint v17 (ESM) resolves config extends from the config file's directory.
        # In the MegaLinter Docker container all npm packages are installed in /node-deps,
        # which is not on the standard Node.js resolution path when the config file lives
        # elsewhere (e.g. /action/lib/.automation/ or the user's workspace).
        # Passing --config-basedir tells stylelint where to look for extended packages.
        if os.path.isdir(NODE_DEPS_DIR):
            cmd += ["--config-basedir", NODE_DEPS_DIR]
        return cmd
