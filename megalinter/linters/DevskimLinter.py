#!/usr/bin/env python3
"""
Use Devskim as a set of language analyzers and rules that provide security "linting" capabilities
"""


class DevskimLinter(Linter):
    def execute_lint_command(self, command):
        return_code, return_stdout = super().execute_lint_command(command)
        if '-E' in command:
            # w/-E exit >0 denotes warnings, <0 errors
            min(return_code, 0), return_stdout 

        return return_code, return_stdout
