#!/usr/bin/env python3
"""
Class for cpplint
"""

import logging
import pathlib
import re

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    result_from_match,
)

CPPLINT_GUIDE_URL = "https://google.github.io/styleguide/cppguide.html"
CPPLINT_LINE_REGEX = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+):\s+(?P<message>.*?)\s+"
    r"\[(?P<category>[^\]]+)\]\s+\[(?P<confidence>\d)\]$"
)


class CppLintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return cpplint_output_to_sarif(return_stdout, self.workspace)

    def build_lint_command(self, file=None):
        # Dynamically add the list of extensions from list of files
        if (
            self.cli_lint_mode == "list_of_files"
            and self.files is not None
            and len(self.files) > 0
        ):
            extensions = []
            for file_to_lint in self.files:
                extension = pathlib.Path(file_to_lint).suffix.replace(".", "")
                if extension not in extensions:
                    extensions += [extension]
            self.cli_lint_extra_args += ["--extensions=" + ",".join(extensions)]
        cmd = super().build_lint_command(file)
        return cmd


# SARIF is built from the default output format. cpplint has no severity:
# every finding is an error
def cpplint_output_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "cpplint", url="https://github.com/cpplint/cpplint"
    )
    has_result = False
    for line in stdout.splitlines():
        match = CPPLINT_LINE_REGEX.match(line.strip())
        if match is None:
            continue
        has_result = True
        run.add_rule(
            SarifRuleBuilder().init_simple(
                match.group("category"), help_uri=CPPLINT_GUIDE_URL
            )
        )
        run.add_result(
            result_from_match(
                match,
                workspace,
                LEVEL_ERROR,
                match.group("message"),
                match.group("category"),
            )
        )
    if has_result is False and stdout.strip() != "":
        logging.debug("[cpplint] No finding found in the output")
    return SarifBuilder().add_run(run)
