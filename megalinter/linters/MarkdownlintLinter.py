#!/usr/bin/env python3
"""
Use markdownlint to lint Markdown files
SARIF is built from the output of the --json option
"""

import logging

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)


class MarkdownlintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return markdownlint_json_to_sarif(return_stdout, self.workspace)


def markdownlint_json_to_sarif(stdout, workspace=None):
    findings = utils.find_json_value(
        stdout,
        list,
        lambda value: len(value) > 0
        and all(isinstance(item, dict) and "ruleNames" in item for item in value),
    )
    if findings is None and "ruleNames" in stdout:
        logging.warning("[markdownlint] No JSON output found to build SARIF from")
    run = SarifRunBuilder().init_simple(
        "markdownlint", url="https://github.com/DavidAnson/markdownlint"
    )
    for finding in findings or []:
        rule_names = finding["ruleNames"]
        rule_id = rule_names[0]
        run.add_rule(
            SarifRuleBuilder().init_simple(
                rule_id,
                short_description_text=finding.get("ruleDescription"),
                help_uri=finding.get("ruleInformation"),
                name=" ".join(rule_names[1:]) or None,
            )
        )
        message = finding.get("ruleDescription") or rule_id
        if finding.get("errorDetail"):
            message += f" [{finding['errorDetail']}]"
        if finding.get("errorContext"):
            message += f' [Context: "{finding["errorContext"]}"]'
        error_range = finding.get("errorRange")
        run.add_result(
            SarifResultBuilder().init_simple(
                LEVEL_WARNING if finding.get("severity") == "warning" else LEVEL_ERROR,
                message,
                rule_id,
                file_uri=to_sarif_uri(finding.get("fileName", ""), workspace),
                start_line=finding.get("lineNumber"),
                start_column=error_range[0] if error_range else None,
                end_line=finding.get("lineNumber") if error_range else None,
                end_column=error_range[0] + error_range[1] if error_range else None,
            )
        )
    return SarifBuilder().add_run(run)
