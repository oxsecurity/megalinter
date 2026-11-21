#!/usr/bin/env python3
"""
Use StyleLint to lint css, scss and saas files
"""

import logging
import os

from megalinter import Linter, config, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)

NODE_DEPS_DIR = "/node-deps"
CONFIG_BASEDIR_ARG = "--config-basedir"
STYLELINT_RULES_URL = "https://stylelint.io/user-guide/rules"
STYLELINT_INVALID_OPTION_RULE = "invalid-option"


# SARIF is built from the output of the json formatter
def stylelint_json_to_sarif(stdout, workspace=None):
    results = utils.find_json_value(
        stdout,
        list,
        lambda value: all(
            isinstance(item, dict) and "warnings" in item for item in value
        ),
    )
    if results is None and stdout.strip() != "":
        logging.warning("[stylelint] No JSON output found to build SARIF from")
    run = SarifRunBuilder().init_simple("stylelint", url="https://stylelint.io")
    for file_result in results or []:
        file_uri = to_sarif_uri(file_result.get("source", ""), workspace)
        for warning in file_result["warnings"]:
            rule_id = warning.get("rule") or "stylelint"
            # Only the core rules have a page in the stylelint documentation
            run.add_rule(
                SarifRuleBuilder().init_simple(
                    rule_id,
                    help_uri=(
                        None if "/" in rule_id else f"{STYLELINT_RULES_URL}/{rule_id}/"
                    ),
                )
            )
            run.add_result(
                SarifResultBuilder().init_simple(
                    (
                        LEVEL_WARNING
                        if warning.get("severity") == "warning"
                        else LEVEL_ERROR
                    ),
                    warning.get("text"),
                    rule_id,
                    file_uri=file_uri,
                    start_line=warning.get("line"),
                    start_column=warning.get("column"),
                    end_line=warning.get("endLine"),
                    end_column=warning.get("endColumn"),
                )
            )
        # A broken configuration makes stylelint fail without any warning
        for invalid_option in file_result.get("invalidOptionWarnings", []):
            run.add_result(
                SarifResultBuilder().init_simple(
                    LEVEL_ERROR,
                    invalid_option.get("text"),
                    STYLELINT_INVALID_OPTION_RULE,
                )
            )
    return SarifBuilder().add_run(run)


class StyleLintLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if self.cli_lint_mode == "project":
            self.cli_lint_extra_args_after.append(
                f"**/*{self.file_extensions[0]}"
                if len(self.file_extensions) == 1
                else f"**/*.{{{",".join(self.file_extensions).replace(".", "")}}}"
            )

        cmd = super().build_lint_command(file)
        # stylelint v17 (ESM) resolves config extends from the config file's directory.
        # In the MegaLinter Docker container all npm packages are installed in /node-deps,
        # which is not on the standard Node.js resolution path when the config file lives
        # elsewhere (e.g. /action/lib/.automation/ or the user's workspace).
        # Passing --config-basedir tells stylelint where to look for extended packages.
        # Do not add it if the user already defined it in CSS_STYLELINT_ARGUMENTS,
        # or asked to get rid of it using CSS_STYLELINT_COMMAND_REMOVE_ARGUMENTS
        node_deps_dir = self.get_node_deps_dir()
        if (
            node_deps_dir is not None
            and CONFIG_BASEDIR_ARG not in cmd
            and CONFIG_BASEDIR_ARG not in self.cli_command_remove_args
        ):
            cmd += [CONFIG_BASEDIR_ARG, node_deps_dir]
        return cmd

    def convert_output_to_sarif(self, return_stdout):
        return stylelint_json_to_sarif(return_stdout, self.workspace)

    def get_node_deps_dir(self):
        if self.native_toolchain is not None:
            return self.native_toolchain.install_dir
        return NODE_DEPS_DIR if os.path.isdir(NODE_DEPS_DIR) else None

    def pre_test(self, test_name):
        if test_name.startswith("test_failure"):
            config.set_value(
                self.request_id, "CSS_STYLELINT_CONFIG_FILE", ".stylelintrc_bad.json"
            )
