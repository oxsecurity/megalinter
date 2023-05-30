#!/usr/bin/env python3
"""
Use Raku to lint raku files
https://raku.org/
"""
import logging
import os
import subprocess

import megalinter
from megalinter import config


class RakuLinter(megalinter.Linter):
    # To execute before linting files
    def before_lint_files(self):
        if os.path.isfile(
            self.workspace + os.path.sep + self.config_file_name
        ):  # META6.json
            pre_command = f"cd {self.workspace} && zef install --deps-only --/test ."
            logging.debug("Raku before_lint_files: " + pre_command)
            process = subprocess.run(
                pre_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                env=config.build_env(
                    self.request_id, True, self.unsecured_env_variables
                ),
            )
            return_code = process.returncode
            return_stdout = megalinter.utils.decode_utf8(process.stdout)
            logging.debug(f"{return_code} : {return_stdout}")

    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        cmd = [*self.cli_executable]
        # Add other lint cli arguments if defined
        cmd += self.cli_lint_extra_args
        # Add fix argument if defined
        if self.apply_fixes is True and self.cli_lint_fix_arg_name is not None:
            cmd += [self.cli_lint_fix_arg_name]
        # Add user-defined extra arguments if defined
        cmd += self.cli_lint_user_args
        cmd += ["-I", self.workspace + os.path.sep + "lib", "-c", file]
        return cmd
