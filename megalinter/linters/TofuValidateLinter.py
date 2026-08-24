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
    # tofu validate takes no file argument: it validates the whole module found
    # in the directory selected by the global -chdir option. Each collected
    # directory is therefore initialized and validated exactly once, so a
    # module error is counted once instead of being repeated for every file of
    # that module
    def process_linter(self, file=None):
        return_code = 0
        outputs = []
        for module_directory in self.get_module_directories():
            module_return_code, output = self.process_module(module_directory)
            if module_return_code != 0:
                return_code = module_return_code
            outputs += [output]
        return return_code, "\n".join(outputs)

    # tofu validate needs the provider schemas and the installed child modules
    # of the directory it validates, so the directory is initialized first.
    # -backend=false keeps the initialization away from the state: no backend
    # is configured, nothing is read or locked, and no credentials are needed
    def process_module(self, module_directory: str):
        init_arguments = config.get_list(
            self.request_id, self.name + "_INIT_ARGUMENTS", DEFAULT_INIT_ARGUMENTS
        )
        init_command = self.add_chdir_argument(
            [*self.cli_executable, "init"] + init_arguments, module_directory
        )
        logging.debug(f"[{self.linter_name}] init command: {str(init_command)}")
        return_code, output = self.execute_lint_command(init_command)
        if return_code != 0:
            return return_code, output
        return self.execute_lint_command(self.build_validate_command(module_directory))

    def build_validate_command(self, module_directory: str) -> list:
        cmd = super().build_lint_command()
        # The base class appends every collected file in list_of_files mode
        cmd = [argument for argument in cmd if argument not in self.files]
        return self.add_chdir_argument(cmd, module_directory)

    def get_module_directories(self) -> list:
        module_directories = []
        for file in self.files:
            module_directory = os.path.dirname(file) or "."
            if module_directory not in module_directories:
                module_directories += [module_directory]
        return module_directories

    # -chdir is a global option: OpenTofu accepts it only before the subcommand
    def add_chdir_argument(self, cmd: list, module_directory: str) -> list:
        cmd.insert(len(self.cli_executable), f"-chdir={module_directory}")
        return cmd
