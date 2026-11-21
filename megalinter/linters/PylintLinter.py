#!/usr/bin/env python3
"""
Use pylint to lint Python files
SARIF is built from the output of the json2 reporter
"""

import logging

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_NOTE,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)

PYLINT_LEVELS = {"fatal": LEVEL_ERROR, "error": LEVEL_ERROR, "warning": LEVEL_WARNING}
PYLINT_DOC_FOLDERS = {"info": "information"}
PYLINT_DOC_URL = "https://pylint.readthedocs.io/en/stable/user_guide/messages"


class PylintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return pylint_json2_to_sarif(return_stdout, self.workspace)


def pylint_json2_to_sarif(stdout, workspace=None):
    output = utils.find_json_value(stdout, dict, lambda value: "messages" in value)
    if output is None and stdout.strip() != "":
        logging.warning("[pylint] No json2 output found to build SARIF from")
    run = SarifRunBuilder().init_simple("pylint", url="https://pylint.readthedocs.io")
    for message in (output or {}).get("messages", []):
        category = message.get("type", "")
        symbol = message.get("symbol") or message.get("messageId")
        run.add_rule(
            SarifRuleBuilder().init_simple(
                symbol,
                short_description_text=symbol,
                help_uri=f"{PYLINT_DOC_URL}/{PYLINT_DOC_FOLDERS.get(category, category)}"
                f"/{symbol}.html",
                name=message.get("messageId"),
            )
        )
        # pylint columns are 0-based
        end_column = message.get("endColumn")
        run.add_result(
            SarifResultBuilder().init_simple(
                PYLINT_LEVELS.get(category, LEVEL_NOTE),
                message.get("message"),
                symbol,
                file_uri=to_sarif_uri(message.get("path", ""), workspace),
                start_line=message.get("line"),
                start_column=message.get("column", 0) + 1,
                end_line=message.get("endLine"),
                end_column=None if end_column is None else end_column + 1,
            )
        )
    return SarifBuilder().add_run(run)
