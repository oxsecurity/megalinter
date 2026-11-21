#!/usr/bin/env python3
"""
Use dart analyze to lint Dart files
SARIF is built from the output of the json format
"""

import logging

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_NOTE,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)

DART_LEVELS = {"error": LEVEL_ERROR, "warning": LEVEL_WARNING}


class DartAnalyzerLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return dart_json_to_sarif(return_stdout, self.workspace)


def dart_json_to_sarif(stdout, workspace=None):
    output = utils.find_json_value(stdout, dict, lambda value: "diagnostics" in value)
    if output is None and stdout.strip() != "":
        logging.warning("[dartanalyzer] No JSON output found to build SARIF from")
    run = SarifRunBuilder().init_simple(
        "dart analyze", url="https://dart.dev/tools/dart-analyze"
    )
    for diagnostic in (output or {}).get("diagnostics", []):
        code = diagnostic.get("code") or "dart-analyze"
        run.add_rule(
            SarifRuleBuilder().init_simple(
                code, help_uri=diagnostic.get("documentation")
            )
        )
        message = diagnostic.get("problemMessage") or code
        if diagnostic.get("correctionMessage"):
            message += " " + diagnostic["correctionMessage"]
        location = diagnostic.get("location", {})
        start = location.get("range", {}).get("start", {})
        end = location.get("range", {}).get("end", {})
        run.add_result(
            SarifResultBuilder().init_simple(
                DART_LEVELS.get(str(diagnostic.get("severity")).lower(), LEVEL_NOTE),
                message,
                code,
                file_uri=to_sarif_uri(location.get("file", ""), workspace),
                start_line=start.get("line"),
                start_column=start.get("column"),
                end_line=end.get("line"),
                end_column=end.get("column"),
            )
        )
    return SarifBuilder().add_run(run)
