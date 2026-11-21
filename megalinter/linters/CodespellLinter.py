#!/usr/bin/env python3
"""
Use codespell to find misspellings
SARIF is built from the default output format
"""

import logging
import re

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    result_from_match,
)

CODESPELL_LINE_REGEX = re.compile(
    r"^(?P<path>.+?):(?:(?P<line>\d+):)? (?P<word>\S.*?) ==> (?P<suggestions>.*)$"
)
CODESPELL_RULE_ID = "misspelling"


class CodespellLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return codespell_output_to_sarif(return_stdout, self.workspace)


# codespell has no severity: every finding is an error
def codespell_output_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "codespell", url="https://github.com/codespell-project/codespell"
    )
    run.add_rule(
        SarifRuleBuilder().init_simple(
            CODESPELL_RULE_ID,
            short_description_text="Common misspelling",
            help_uri="https://github.com/codespell-project/codespell",
        )
    )
    has_result = False
    for line in stdout.splitlines():
        match = CODESPELL_LINE_REGEX.match(line.strip())
        if match is None:
            continue
        has_result = True
        run.add_result(
            result_from_match(
                match,
                workspace,
                LEVEL_ERROR,
                f'"{match.group("word")}" is a misspelling of '
                f'"{match.group("suggestions")}"',
                CODESPELL_RULE_ID,
            )
        )
    if has_result is False and stdout.strip() != "":
        logging.debug("[codespell] No misspelling found in the output")
    return SarifBuilder().add_run(run)
