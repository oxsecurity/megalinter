#!/usr/bin/env python3
"""
ApexGuru engine of Salesforce Code Analyzer
https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-apexguru.html
"""

import logging

from megalinter.linters.SalesforceCodeAnalyzerLinter import (
    SalesforceCodeAnalyzerLinter,
)

SFDX_AUTH_URL_VAR = "SFDX_AUTH_URL"
ORG_ALIAS = "megalinter-apexguru"


class SalesforceCodeAnalyzerApexGuruLinter(SalesforceCodeAnalyzerLinter):
    # Unlike the other Code Analyzer engines, ApexGuru runs server-side: it
    # sends the Apex sources to a connected org and needs an authenticated
    # default org. SFDX_AUTH_URL (the same variable that activates this linter)
    # holds a Salesforce DX auth url, so log in with it before linting.
    # SFDX_AUTH_URL matches the default secured variables regexes, so it is
    # replaced by HIDDEN_BY_MEGALINTER in sub-process environments unless it is
    # explicitly allowed: the auth url is expanded by the login command itself,
    # never by MegaLinter, so it stays out of the logs.
    # The default org must be set with `sf config set --global`: the login runs
    # from the root folder, never inside the analyzed sources, so a project
    # scoped default would not be visible from the workspace where
    # `sf code-analyzer run` is executed.
    def before_lint_files(self):
        if SFDX_AUTH_URL_VAR not in self.unsecured_env_variables:
            self.unsecured_env_variables += [SFDX_AUTH_URL_VAR]
        login_command = (
            f'echo "${SFDX_AUTH_URL_VAR}" | sf org login sfdx-url'
            f" --sfdx-url-stdin --alias {ORG_ALIAS}"
            f" && sf config set target-org={ORG_ALIAS} --global"
        )
        logging.debug("apexguru before_lint_files: " + login_command)
        if self.pre_commands is None:
            self.pre_commands = []
        self.pre_commands.append({"command": login_command, "cwd": "root"})
