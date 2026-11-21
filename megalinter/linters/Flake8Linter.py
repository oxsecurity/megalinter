#!/usr/bin/env python3
"""
Use flake8 to lint Python files
SARIF is built from the default output format
"""

import logging
import re

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifRunBuilder,
    result_from_match,
)

FLAKE8_LINE_REGEX = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+):(?P<column>\d+): (?P<code>[A-Z]+\d+) (?P<message>.*)$"
)


class Flake8Linter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return flake8_output_to_sarif(return_stdout, self.workspace)


# flake8 has no severity: every finding is an error
def flake8_output_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple("flake8", url="https://flake8.pycqa.org")
    has_result = False
    for line in stdout.splitlines():
        match = FLAKE8_LINE_REGEX.match(line.strip())
        if match is None:
            continue
        has_result = True
        run.add_result(
            result_from_match(
                match,
                workspace,
                LEVEL_ERROR,
                match.group("message"),
                match.group("code"),
            )
        )
    if has_result is False and stdout.strip() != "":
        logging.warning(
            "[flake8] No finding matches the default output format. "
            "Is a custom --format set in the flake8 configuration ?"
        )
    return SarifBuilder().add_run(run)
