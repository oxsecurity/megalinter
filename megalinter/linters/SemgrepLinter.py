#!/usr/bin/env python3
"""
Use dotnet-format to lint CSharp files
"""

import logging

from megalinter import Linter, config


class SemgrepLinter(Linter):

    # Manage case when we want semgrep rulesets to be selected related to security
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        replace_index = cmd.index(self.cli_config_default_value)
        custom_rulesets = self.get_custom_rulesets()
        if len(custom_rulesets) > 0 and replace_index > -1:
            cmd = cmd[:replace_index] + custom_rulesets + cmd[replace_index + 1 :]
            logging.debug(
                "[SemgrepLinter] Custom rulesets: " + ",".join(custom_rulesets)
            )
        return cmd

    def get_custom_rulesets(self):
        if config.exists("REPOSITORY_SEMGREP_RULESETS"):
            # User defined rulesets
            return config.get_list("REPOSITORY_SEMGREP_RULESETS")
        elif (
            # security rulesets
            self.master.megalinter_flavor in ["security", "none"]
            or config.get("REPOSITORY_SEMGREP_RULESETS", "") == "security"
        ):
            return [
                "p/docker-compose",
                "p/expressjs",
                "p/github-actions",
                "p/headless-browser",
                "p/jwt",
                "p/kubernetes",
                "p/nginx",
                "p/nodejsscan",
                "p/owasp-top-ten",
                "p/phpcs-security-audit",
                "p/react",
                "p/security-audit",
                "p/sql-injection",
                "p/xss"
            ]
        return []
