#!/usr/bin/env python3
"""
Use roslynator to lint CSharp files
"""
import logging

from megalinter.linters.DotNetToolLinter import DotNetToolLinter


class RoslynatorLinter(DotNetToolLinter):
    def process_linter(self, file=None):
        command = f"dotnet restore {file}"

        logging.debug(f"[{self.linter_name}] command: {str(command)}")

        return_code, return_output = self.execute_lint_command(command)

        logging.debug(
            f"[{self.linter_name}] result: {str(return_code)} {return_output}"
        )

        return super().process_linter(file)
