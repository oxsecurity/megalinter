#!/usr/bin/env python3
"""
Use rst-lint to lint reStructuredText files
SARIF is built from the output of --format json
https://github.com/twolfson/restructuredtext-lint
"""

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

# docutils system message levels: 2 warning, 3 error, 4 severe
RST_LINT_ERROR_LEVEL = 3
RST_LINT_WARNING_LEVEL = 2


class RstLintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return rst_lint_json_to_sarif(return_stdout, self.workspace)


# rst-lint prints one JSON array per linted file
def rst_lint_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "rst-lint", url="https://github.com/twolfson/restructuredtext-lint"
    )
    for diagnostics in utils.find_json_values(stdout, list):
        for diagnostic in diagnostics:
            if not isinstance(diagnostic, dict) or "message" not in diagnostic:
                continue
            level_number = diagnostic.get("level")
            if isinstance(level_number, int) and level_number >= RST_LINT_ERROR_LEVEL:
                level = LEVEL_ERROR
            elif level_number == RST_LINT_WARNING_LEVEL:
                level = LEVEL_WARNING
            else:
                level = LEVEL_NOTE
            run.add_result(
                SarifResultBuilder().init_simple(
                    level,
                    diagnostic["message"],
                    "rst-lint",
                    file_uri=to_sarif_uri(diagnostic.get("source"), workspace),
                    start_line=to_one_based(diagnostic.get("line")),
                )
            )
    return SarifBuilder().add_run(run)
