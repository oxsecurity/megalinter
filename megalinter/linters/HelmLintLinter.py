#!/usr/bin/env python3
"""
Use helm lint to check Helm charts
SARIF is built from the text output: a line per chart, then one line per finding
https://helm.sh/docs/helm/helm_lint/
"""

import os
import re

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_NOTE,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    strip_ansi,
    to_sarif_uri,
)

HELM_LINT_CHART_REGEX = re.compile(r"^==> Linting (?P<chart>.*)$")
HELM_LINT_FINDING_REGEX = re.compile(
    r"^\[(?P<severity>INFO|WARNING|ERROR|UNKNOWN)\] (?P<path>[^:]*): (?P<message>.*)$"
)
# Go template errors give the position in the template: template: chart/templates/x.yaml:5:12
HELM_LINT_TEMPLATE_POSITION_REGEX = re.compile(r"templates/[^\s:]+:(?P<line>\d+):\d+")
HELM_LINT_LEVELS = {
    "INFO": LEVEL_NOTE,
    "WARNING": LEVEL_WARNING,
    "ERROR": LEVEL_ERROR,
    "UNKNOWN": LEVEL_WARNING,
}


class HelmLintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return helm_lint_to_sarif(return_stdout, self.workspace)


# The path of a finding is relative to the chart that precedes it
def helm_lint_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple("helm", url="https://helm.sh")
    chart = "."
    for line in strip_ansi(stdout).splitlines():
        chart_match = HELM_LINT_CHART_REGEX.match(line)
        if chart_match is not None:
            chart = chart_match.group("chart").strip() or "."
            continue
        match = HELM_LINT_FINDING_REGEX.match(line)
        if match is None:
            continue
        position = HELM_LINT_TEMPLATE_POSITION_REGEX.search(match.group("message"))
        run.add_result(
            SarifResultBuilder().init_simple(
                HELM_LINT_LEVELS[match.group("severity")],
                match.group("message"),
                "helm-lint",
                file_uri=to_sarif_uri(
                    os.path.join(chart, match.group("path").strip()), workspace
                ),
                start_line=int(position.group("line")) if position else None,
            )
        )
    return SarifBuilder().add_run(run)
