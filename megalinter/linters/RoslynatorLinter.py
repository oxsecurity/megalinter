#!/usr/bin/env python3
"""
Use roslynator to lint CSharp files
"""

import logging
import os

from megalinter import Linter, config


class RoslynatorLinter(Linter):
    def process_linter(self, file=None):
        # dotnet restore is a project-setup prerequisite, not the actual lint
        # invocation: run it through the lower-level subprocess primitive
        # directly rather than execute_lint_command(), which also triggers
        # manage_sarif_output() — that expects self.sarif_output_file to
        # already be resolved by build_lint_command(), which hasn't run yet
        # at this point
        command = ["dotnet", "restore", file]

        logging.debug(f"[{self.linter_name}] command: {str(command)}")

        subprocess_env = getattr(self, "_cached_subprocess_env", None) or {
            **config.build_env(self.request_id, True, self.unsecured_env_variables),
            "FORCE_COLOR": "0",
        }
        return_code, return_output = self._run_lint_subprocess(
            command,
            {"cwd": os.path.abspath(self.workspace), "env": subprocess_env},
        )

        logging.debug(
            f"[{self.linter_name}] result: {str(return_code)} {return_output}"
        )

        return super().process_linter(file)
