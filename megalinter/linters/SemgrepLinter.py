#!/usr/bin/env python3
"""
Use SemGrep to lint any type of file according to local config
"""

import logging

from megalinter import Linter, config, flavor_factory, utils


class SemgrepLinter(Linter):
    # Activate SemGrep only if we have custom rulesets defined
    def manage_activation(self, params):
        super().manage_activation(params)
        if self.is_active is True:
            custom_rulesets = self.get_custom_rulesets()
            if (
                len(custom_rulesets) == 0
                and len(
                    config.get_list(self.request_id, "REPOSITORY_SEMGREP_ARGUMENTS", [])
                )
                == 0
                and "semgrep" not in utils.get_current_test_name(full_name=True)
            ):
                logging.info(
                    "[SemgrepLinter] Deactivated because no ruleset has been defined"
                )
                self.is_active = False

    # Manage case when we want semgrep rulesets to be selected related to security
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        replace_index = cmd.index(self.cli_config_default_value)
        custom_rulesets = self.get_custom_rulesets()
        if len(custom_rulesets) > 0 and replace_index > -1:
            custom_rulesets_args = []
            for custom_ruleset in custom_rulesets:
                custom_rulesets_args.append("--config")
                custom_rulesets_args.append(custom_ruleset)
            cmd = (
                cmd[: replace_index - 1]
                + custom_rulesets_args
                + cmd[replace_index + 1 :]  # noqa: E203
            )
            logging.debug(
                "[SemgrepLinter] Custom rulesets: " + ",".join(custom_rulesets)
            )
        return cmd

    def get_custom_rulesets(self):
        if config.exists(self.request_id, "REPOSITORY_SEMGREP_RULESETS"):
            # User defined rulesets
            return config.get_list(self.request_id, "REPOSITORY_SEMGREP_RULESETS")
        elif (
            # security rulesets
            flavor_factory.get_image_flavor() in ["security", "none"]
            or config.get(self.request_id, "REPOSITORY_SEMGREP_RULESETS_TYPE", "")
            == "security"
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
                "p/xss",
            ]
        return []
