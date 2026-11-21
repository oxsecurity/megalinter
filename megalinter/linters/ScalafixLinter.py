#!/usr/bin/env python3
"""
Use scalafix to check Scala files
SARIF is built from the output of --check: a diff per file to rewrite, and the lint diagnostics
https://scalacenter.github.io/scalafix/
"""

import re

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_NOTE,
    LEVEL_WARNING,
    SarifResultBuilder,
    sarif_from_results,
    strip_ansi,
    to_sarif_uri,
    unified_diff_to_results,
)

SCALAFIX_DIAGNOSTIC_REGEX = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+): (?P<severity>error|warning|info): "
    r"(?:\[(?P<rule>[^\]]+)\] )?(?P<message>.*)$"
)
SCALAFIX_LEVELS = {"error": LEVEL_ERROR, "warning": LEVEL_WARNING, "info": LEVEL_NOTE}


class ScalafixLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return scalafix_to_sarif(return_stdout, self.workspace)


# The diff of a file does not tell which rule rewrites it: one result per file, at its first hunk
def scalafix_to_sarif(stdout, workspace=None):
    results = unified_diff_to_results(
        stdout,
        workspace,
        LEVEL_ERROR,
        "The file is not rewritten as the scalafix rules expect",
        "scalafix",
    )
    for line in strip_ansi(stdout).splitlines():
        match = SCALAFIX_DIAGNOSTIC_REGEX.match(line)
        if match is not None:
            results.append(
                SarifResultBuilder().init_simple(
                    SCALAFIX_LEVELS[match.group("severity")],
                    match.group("message"),
                    match.group("rule") or "scalafix",
                    file_uri=to_sarif_uri(match.group("path"), workspace),
                    start_line=int(match.group("line")),
                )
            )
    return sarif_from_results(
        "scalafix", results, "https://scalacenter.github.io/scalafix/"
    )
