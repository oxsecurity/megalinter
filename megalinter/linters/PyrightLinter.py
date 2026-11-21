#!/usr/bin/env python3
"""
Use Pyright to lint py files
https://github.com/Microsoft/pyright/
"""

import os

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_NOTE,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)

PYRIGHT_LEVELS = {
    "error": LEVEL_ERROR,
    "warning": LEVEL_WARNING,
    "information": LEVEL_NOTE,
}


class PyrightLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return pyright_json_to_sarif(return_stdout, self.workspace)

    def pre_test(self, test_name):
        # The file must be in the root of the repository so we create it temporarily for the test.
        # By default pyright ignores files starting with "." so we override this behavior
        # to work with the .automation folder
        # https://microsoft.github.io/pyright/#/configuration?id=environment-options
        with open(
            os.path.join(os.getcwd(), "pyproject.toml"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write("""[tool.pyright]
exclude = [
    "**/node_modules",
    "**/__pycache__"
]""")

    def post_test(self, test_name):
        os.remove(os.path.join(os.getcwd(), "pyproject.toml"))


# pyright positions are 0-based, and its end position is exclusive
def pyright_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "pyright", url="https://github.com/microsoft/pyright"
    )
    for output in utils.find_json_values(
        stdout, dict, lambda value: isinstance(value.get("generalDiagnostics"), list)
    ):
        for diagnostic in output["generalDiagnostics"]:
            position = diagnostic.get("range") or {}
            start = position.get("start") or {}
            end = position.get("end") or {}
            run.add_result(
                SarifResultBuilder().init_simple(
                    PYRIGHT_LEVELS.get(diagnostic.get("severity"), LEVEL_ERROR),
                    diagnostic.get("message"),
                    diagnostic.get("rule") or "pyright",
                    file_uri=to_sarif_uri(diagnostic.get("file"), workspace),
                    start_line=to_one_based(start.get("line"), zero_based=True),
                    start_column=to_one_based(start.get("character"), zero_based=True),
                    end_line=to_one_based(end.get("line"), zero_based=True),
                    end_column=to_one_based(end.get("character")),
                )
            )
    return SarifBuilder().add_run(run)
