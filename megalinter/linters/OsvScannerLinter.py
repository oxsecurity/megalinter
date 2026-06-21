#!/usr/bin/env python3
"""
Use OsvScanner to check for dependency vulnerabilities.
Treat exit code 128 ("No package sources found") as a clean pass —
osv-scanner upstream declined to add a --no-fail-if-no-package flag
(https://github.com/google/osv-scanner/issues/348), so we handle it here.
"""

import logging

from megalinter import Linter


class OsvScannerLinter(Linter):

    def execute_lint_command(self, command):
        return_code, return_output = super().execute_lint_command(command)
        if return_code == 128 and "no package sources found" in return_output.lower():
            logging.info(
                "[osv-scanner] No package sources found (exit 128) — "
                "treating as success (nothing to scan)"
            )
            return 0, return_output
        return return_code, return_output
