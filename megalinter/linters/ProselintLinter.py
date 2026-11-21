#!/usr/bin/env python3
"""
Use Proselint to check spell in files
https://github.com/amperser/proselint
"""

from megalinter import Linter, config, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    file_uri_to_path,
    to_one_based,
    to_sarif_uri,
)


class ProselintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return proselint_json_to_sarif(return_stdout, self.workspace)

    def pre_test(self, test_name):
        config.set_value(
            self.request_id, "SPELL_PROSELINT_FILE_EXTENSIONS", [".js", ".md"]
        )


# proselint has no severity: every diagnostic is an error, as in the text count.
# The files are file:// URIs, and a file that could not be linted has an error object
def proselint_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "proselint", url="https://github.com/amperser/proselint"
    )
    for output in utils.find_json_values(
        stdout, dict, lambda value: isinstance(value.get("result"), dict)
    ):
        for uri, file_result in output["result"].items():
            file_uri = to_sarif_uri(file_uri_to_path(uri), workspace)
            if isinstance(file_result.get("error"), dict):
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_ERROR,
                        file_result["error"].get("message"),
                        "proselint",
                        file_uri=file_uri,
                    )
                )
            for diagnostic in file_result.get("diagnostics") or []:
                position = diagnostic.get("pos") or [None, None]
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_ERROR,
                        diagnostic.get("message"),
                        diagnostic.get("check_path") or "proselint",
                        file_uri=file_uri,
                        start_line=to_one_based(position[0]),
                        start_column=to_one_based(position[1]),
                    )
                )
    return SarifBuilder().add_run(run)
