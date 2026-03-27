#!/usr/bin/env python3
"""
Use Trivy to check for vulnerabilities
"""

import logging
import time

from megalinter import Linter


class TrivyLinter(Linter):

    def execute_lint_command(self, command):
        max_retries = 5
        for attempt in range(max_retries):
            return_code, return_output = super().execute_lint_command(command)
            if not (
                ("TOOMANYREQUESTS" in return_output)
                or ("failed to download Java DB" in return_output)
                or ("BLOB_UNKNOWN" in return_output)
            ):
                return return_code, return_output
            if attempt < max_retries - 1:
                time.sleep(3.0)
                logging.info(
                    f"[Trivy] Hit TOOMANYREQUESTS: try again (attempt {attempt + 2}/{max_retries})"
                )
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
