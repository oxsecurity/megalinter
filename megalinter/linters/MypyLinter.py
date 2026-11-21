#!/usr/bin/env python3
"""
Use mypy to check the types of Python files
SARIF is built from the JSON lines of --output json
https://mypy.readthedocs.io
"""

import json

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_NOTE,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)


class MypyLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return mypy_json_to_sarif(return_stdout, self.workspace)


# mypy prints one JSON object per line, among other messages (ex: installed stubs)
def mypy_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple("mypy", url="https://mypy-lang.org")
    for line in stdout.splitlines():
        if not line.strip().startswith("{"):
            continue
        try:
            diagnostic = json.loads(line)
        except ValueError:
            continue
        if (
            not isinstance(diagnostic, dict)
            or "file" not in diagnostic
            or "message" not in diagnostic
        ):
            continue
        message_text = diagnostic["message"]
        if diagnostic.get("hint"):
            message_text += "\n" + diagnostic["hint"]
        run.add_result(
            SarifResultBuilder().init_simple(
                LEVEL_NOTE if diagnostic.get("severity") == "note" else LEVEL_ERROR,
                message_text,
                diagnostic.get("code") or "mypy",
                file_uri=to_sarif_uri(diagnostic["file"], workspace),
                start_line=to_one_based(diagnostic.get("line")),
                # mypy columns are 0-based, and its end column is exclusive
                start_column=to_one_based(diagnostic.get("column"), zero_based=True),
                end_line=to_one_based(diagnostic.get("end_line")),
                end_column=to_one_based(diagnostic.get("end_column"), zero_based=True),
            )
        )
    return SarifBuilder().add_run(run)
