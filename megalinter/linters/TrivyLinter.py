#!/usr/bin/env python3
"""
Use Trivy to check for vulnerabilities
"""

import logging
import time

from megalinter import Linter


class TrivyLinter(Linter):
    counter = 0

    def execute_lint_command(self, command):
        return_code, return_output = super().execute_lint_command(command)
        if "TOOMANYREQUESTS" in return_output:
            # Try 5 times
            if self.counter < 5:
                time.sleep(3.0)
                logging.info("[Trivy] Hit TOOMANYREQUESTS: try again")
                self.counter = self.counter + 1
                return_code, return_output = self.execute_lint_command(command)
            else:
                logging.warning(
                    "[Trivy] Hit TOOMANYREQUESTS 5 times: Run trivy "
                    + "with --skip-db-update and --skip-check-update"
                )
                if isinstance(command, str):
                    command_without_db = (
                        command + " --skip-db-update --skip-check-update"
                    )
                else:
                    command_without_db = command + [
                        "--skip-db-update",
                        "--skip-check-update",
                    ]
                return super().execute_lint_command(command_without_db)
        return return_code, return_output
