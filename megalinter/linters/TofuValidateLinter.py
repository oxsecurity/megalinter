#!/usr/bin/env python3
"""
Use tofu validate to check the validity of OpenTofu configurations
https://opentofu.org/docs/cli/commands/validate/
"""

import logging
import os

from megalinter import Linter, config, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)

DEFAULT_INIT_ARGUMENTS = ["-backend=false", "-input=false", "-no-color"]


class TofuValidateLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        # Output of tofu validate for each module directory
        self.module_outputs = []
        self.collecting_modules = False
        super().__init__(params, linter_config)

    # tofu validate takes no file argument: it validates the whole module found
    # in the directory selected by the global -chdir option. Each collected
    # directory is therefore initialized and validated exactly once, so a
    # module error is counted once instead of being repeated for every file of
    # that module
    def process_linter(self, file=None):
        if self.sarif_output_file is not None and os.path.isfile(
            self.sarif_output_file
        ):
            os.remove(self.sarif_output_file)
        return_code = 0
        outputs = []
        self.module_outputs = []
        self.stdout_human = None
        self.collecting_modules = True
        for module_directory in self.get_module_directories():
            module_return_code, output = self.process_module(module_directory)
            if module_return_code != 0:
                return_code = module_return_code
            outputs += [output]
            self.module_outputs += [(module_directory, output)]
        self.collecting_modules = False
        # The SARIF is built once for all the modules, from their outputs
        self.last_return_code = return_code
        self.manage_sarif_output("\n".join(outputs))
        if self.stdout_human:
            return return_code, self.stdout_human
        return return_code, "\n".join(outputs)

    def manage_sarif_output(self, return_stdout):
        if self.collecting_modules is False:
            super().manage_sarif_output(return_stdout)

    def convert_output_to_sarif(self, return_stdout):
        return tofu_validate_json_to_sarif(self.module_outputs, self.workspace)

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


# The files of the diagnostics are relative to the directory of the module validated
def tofu_validate_json_to_sarif(module_outputs, workspace=None):
    run = SarifRunBuilder().init_simple(
        "tofu validate", url="https://opentofu.org/docs/cli/commands/validate/"
    )
    for module_directory, output in module_outputs:
        for validation in utils.find_json_values(
            output, dict, lambda value: isinstance(value.get("diagnostics"), list)
        ):
            for diagnostic in validation["diagnostics"]:
                position = diagnostic.get("range") or {}
                start = position.get("start") or {}
                end = position.get("end") or {}
                message_text = diagnostic.get("summary") or ""
                if diagnostic.get("detail"):
                    message_text += ": " + diagnostic["detail"]
                run.add_result(
                    SarifResultBuilder().init_simple(
                        (
                            LEVEL_WARNING
                            if diagnostic.get("severity") == "warning"
                            else LEVEL_ERROR
                        ),
                        message_text,
                        "tofu-validate",
                        file_uri=(
                            to_sarif_uri(
                                os.path.join(module_directory, position["filename"]),
                                workspace,
                            )
                            if position.get("filename")
                            else None
                        ),
                        start_line=to_one_based(start.get("line")),
                        start_column=to_one_based(start.get("column")),
                        end_line=to_one_based(end.get("line")),
                        end_column=to_one_based(end.get("column")),
                    )
                )
    return SarifBuilder().add_run(run)
