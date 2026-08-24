#!/usr/bin/env python3
"""
Use tofu validate to check the validity of OpenTofu configurations
https://opentofu.org/docs/cli/commands/validate/
"""

import logging
import os

from megalinter import Linter, config

DEFAULT_INIT_ARGUMENTS = ["-backend=false", "-input=false", "-no-color"]


class TofuValidateLinter(Linter):
    initialized_directories: set

    def before_lint_files(self):
        self.initialized_directories = set()

    # tofu validate takes no file argument: it validates the module found in
    # the directory selected by the global -chdir option
    def build_lint_command(self, file=None) -> list:
        cmd = super().build_lint_command(file)
        cmd.remove(file)
        return self.add_chdir_argument(cmd, self.get_module_directory(file))

    # tofu validate needs the provider schemas and the installed child modules
    # of the directory it validates, so that directory must be initialized
    # first. -backend=false keeps the initialization away from the state: no
    # backend is configured, nothing is read or locked, no credentials needed
    def process_linter(self, file=None):
        module_directory = self.get_module_directory(file)
        if module_directory not in self.initialized_directories:
            self.initialized_directories.add(module_directory)
            return_code, return_output = self.initialize_module(module_directory)
            if return_code != 0:
                return return_code, return_output
        return super().process_linter(file)

    def initialize_module(self, module_directory: str):
        init_arguments = config.get_list(
            self.request_id, self.name + "_INIT_ARGUMENTS", DEFAULT_INIT_ARGUMENTS
        )
        command = self.add_chdir_argument(
            [*self.cli_executable, "init"] + init_arguments, module_directory
        )
        logging.debug(f"[{self.linter_name}] init command: {str(command)}")
        return_code, return_output = self.execute_lint_command(command)
        logging.debug(
            f"[{self.linter_name}] init result: {str(return_code)} {return_output}"
        )
        return return_code, return_output

    # -chdir is a global option: OpenTofu accepts it only before the subcommand
    def add_chdir_argument(self, cmd: list, module_directory: str) -> list:
        cmd.insert(len(self.cli_executable), f"-chdir={module_directory}")
        return cmd

    # noinspection PyMethodMayBeStatic
    def get_module_directory(self, file) -> str:
        return os.path.dirname(file) or "."
