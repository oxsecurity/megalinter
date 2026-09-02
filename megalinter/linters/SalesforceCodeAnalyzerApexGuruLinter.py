#!/usr/bin/env python3
"""
ApexGuru engine of Salesforce Code Analyzer
https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-apexguru.html
"""

import logging
import re

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
    # The auth url is written to a temporary file outside the workspace instead
    # of being piped to `--sfdx-url-stdin`: the sf CLI declares that flag as a
    # value flag, and quotes back the standard input it received in its
    # argument parsing errors, which would print the org refresh token in the
    # job log. With `--sfdx-url-file` an error can only quote the file path.
    def before_lint_files(self):
        if SFDX_AUTH_URL_VAR not in self.unsecured_env_variables:
            self.unsecured_env_variables += [SFDX_AUTH_URL_VAR]
        # mktemp creates the file with 0600 permissions, readable by root only
        login_command = (
            "auth_file=$(mktemp)"
            f' && printf "%s" "${SFDX_AUTH_URL_VAR}" > "$auth_file"'
            ' && sf org login sfdx-url --sfdx-url-file "$auth_file"'
            f" --alias {ORG_ALIAS}"
            '; login_status=$?; rm -f "$auth_file"'
            "; [ $login_status -ne 0 ] && exit $login_status"
            f"; sf config set target-org={ORG_ALIAS} --global"
        )
        logging.debug("apexguru before_lint_files: " + login_command)
        if self.pre_commands is None:
            self.pre_commands = []
        self.pre_commands.append({"command": login_command, "cwd": "root"})

    # The org must be named on the command line, not left to the sf CLI default
    # org resolution: nearly every Salesforce repository holds a
    # `.sfdx/sfdx-config.json` at its root, and that workspace local
    # `defaultusername` wins over the global default set by the login above.
    # It usually points to a long gone scratch org, and ApexGuru then skips
    # itself with `Failed to authenticate: No default org found`.
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        if "--target-org" not in cmd and "-o" not in cmd:
            cmd += ["--target-org", ORG_ALIAS]
        return cmd

    # `sf code-analyzer run` exits 0 when the ApexGuru engine could not run at
    # all: it prints `ApexGuru skipped: <reason>` as a warning, reports zero
    # violations and returns a success. That silently hides that nothing was
    # analyzed, so turn it into a linter error and let common_linter_errors
    # display the matching resolution.
    def execute_lint_command(self, command):
        return_code, return_stdout = super().execute_lint_command(command)
        if return_code == 0 and re.search(r"ApexGuru skipped: ", return_stdout or ""):
            logging.error(
                "[code-analyzer-apexguru] the ApexGuru engine did not analyze "
                "anything, see the reason in the linter output"
            )
            return_code = 1
        return return_code, return_stdout
