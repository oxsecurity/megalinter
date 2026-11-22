#!/usr/bin/env python3
"""
Use npm-package-json-lint to lint package.json files
SARIF is built from the text output: a line with the file, then one line per finding
https://npmpackagejsonlint.org/
"""

import re

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    strip_ansi,
    to_sarif_uri,
)

NPM_PACKAGE_JSON_LINT_FINDING_REGEX = re.compile(
    r"^(?P<severity>ERROR|WARNING) (?P<rule>\S+) - node: (?P<node>\S+) - (?P<message>.*)$"
)


class NpmPackageJsonLintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return npm_package_json_lint_to_sarif(return_stdout, self.workspace)


# No line number is given: the node (key of package.json) is added to the message
def npm_package_json_lint_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "npm-package-json-lint", url="https://npmpackagejsonlint.org/"
    )
    current_file = None
    for line in strip_ansi(stdout).splitlines():
        line = line.strip()
        match = NPM_PACKAGE_JSON_LINT_FINDING_REGEX.match(line)
        if match is not None:
            run.add_result(
                SarifResultBuilder().init_simple(
                    (
                        LEVEL_WARNING
                        if match.group("severity") == "WARNING"
                        else LEVEL_ERROR
                    ),
                    f"{match.group('node')}: {match.group('message')}",
                    match.group("rule"),
                    file_uri=(
                        to_sarif_uri(current_file, workspace) if current_file else None
                    ),
                )
            )
        elif line.endswith("package.json"):
            current_file = line
    return SarifBuilder().add_run(run)
