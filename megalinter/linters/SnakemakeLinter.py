#!/usr/bin/env python3
"""
Use snakemake --lint to check Snakemake workflows
SARIF is built from the text output: a header per rule or snakefile, then one bullet per lint
https://snakemake.readthedocs.io/en/stable/snakefiles/best_practices.html
"""

import re

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    strip_ansi,
    to_sarif_uri,
)

SNAKEMAKE_RULE_HEADER_REGEX = re.compile(
    r"^Lints for rule (?P<rule>\S+) \(line (?P<line>\d+), (?P<path>.+)\):$"
)
SNAKEMAKE_FILE_HEADER_REGEX = re.compile(r"^Lints for snakefile (?P<path>.+):$")
SNAKEMAKE_LINT_REGEX = re.compile(r"^\s{2,4}\* (?P<title>.+):$")
SNAKEMAKE_TITLE_LINE_REGEX = re.compile(r"\bin lines? (?P<line>\d+)")


class SnakemakeLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return snakemake_lint_to_sarif(return_stdout, self.workspace)


# snakemake logs every lint as a warning, without severity. The line is the one of the
# rule, or the one written in the title of the lints of the snakefile
def snakemake_lint_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "snakemake", url="https://snakemake.readthedocs.io"
    )
    path = None
    rule_name = None
    header_line = None
    for line in strip_ansi(stdout).splitlines():
        rule_header = SNAKEMAKE_RULE_HEADER_REGEX.match(line)
        file_header = SNAKEMAKE_FILE_HEADER_REGEX.match(line)
        lint = SNAKEMAKE_LINT_REGEX.match(line)
        if rule_header is not None:
            path = rule_header.group("path")
            rule_name = rule_header.group("rule")
            header_line = int(rule_header.group("line"))
        elif file_header is not None:
            path = file_header.group("path")
            rule_name = None
            header_line = None
        elif lint is not None and path is not None:
            title = lint.group("title")
            title_line = SNAKEMAKE_TITLE_LINE_REGEX.search(title)
            title_line_number = int(title_line.group("line")) if title_line else None
            run.add_result(
                SarifResultBuilder().init_simple(
                    LEVEL_WARNING,
                    f"rule {rule_name}: {title}" if rule_name else title,
                    "snakemake-lint",
                    file_uri=to_sarif_uri(path, workspace),
                    start_line=header_line or title_line_number,
                )
            )
    return SarifBuilder().add_run(run)
