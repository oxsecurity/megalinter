#!/usr/bin/env python3
"""
Use tekton-lint to lint Tekton files
SARIF is built from the output of --format json
https://github.com/IBM/tekton-lint
"""

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)


class TektonLintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return tekton_lint_json_to_sarif(return_stdout, self.workspace)


# The JSON array shares the output with the logs of tekton-lint
def tekton_lint_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "tekton-lint", url="https://github.com/IBM/tekton-lint"
    )
    for findings in utils.find_json_values(stdout, list):
        for finding in findings:
            if not isinstance(finding, dict) or "message" not in finding:
                continue
            location = finding.get("loc") or {}
            run.add_result(
                SarifResultBuilder().init_simple(
                    LEVEL_WARNING if finding.get("level") == "warning" else LEVEL_ERROR,
                    finding["message"],
                    finding.get("rule") or "tekton-lint",
                    file_uri=(
                        to_sarif_uri(finding["path"], workspace)
                        if finding.get("path")
                        else None
                    ),
                    start_line=to_one_based(location.get("startLine")),
                    start_column=to_one_based(location.get("startColumn")),
                    end_line=to_one_based(location.get("endLine")),
                    end_column=to_one_based(location.get("endColumn")),
                )
            )
    return SarifBuilder().add_run(run)
