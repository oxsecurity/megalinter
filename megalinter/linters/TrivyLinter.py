#!/usr/bin/env python3
"""
Use Trivy to check for vulnerabilities
"""

import logging

from megalinter import Linter


class TrivyLinter(Linter):
    counter = 0

    def execute_lint_command(self, command):
        return_code, return_output = super().execute_lint_command(command)
        if "TOOMANYREQUESTS" in return_output and self.counter < 10:
            logging.info("[Trivy] Hit TOOMANYREQUESTS: try again")
            self.counter = self.counter + 1
            return_code, return_output = self.execute_lint_command(command)
        return return_code, return_output
