#!/usr/bin/env python3
"""
Use roslynator to lint CSharp files
"""

import json
import logging
import os

from megalinter import Linter, config


class RoslynatorLinter(Linter):
    merged_sarif = None

    # "roslynator fix" has no --output option
    def before_lint_files(self):
        if self.apply_fixes is True:
            self.output_sarif = False

    # roslynator writes no report file for a project without diagnostics:
    # start from an empty report, that roslynator overwrites when it has results
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        if self.output_sarif is True:
            with open(self.sarif_output_file, "w", encoding="utf-8") as sarif_file:
                json.dump(
                    {
                        "version": "2.1.0",
                        "runs": [
                            {"tool": {"driver": {"name": "Roslynator"}}, "results": []}
                        ],
                    },
                    sarif_file,
                )
        return cmd

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

        lint_result = super().process_linter(file)
        if self.output_sarif is True:
            self.merge_project_sarif()
        return lint_result

    # Each project is linted by its own roslynator call, and the next call
    # removes the SARIF file of the previous one: gather the results of all projects
    def merge_project_sarif(self):
        # utf-8-sig: roslynator writes its report with a BOM
        with open(self.sarif_output_file, "r", encoding="utf-8-sig") as sarif_file:
            project_sarif = json.load(sarif_file)
        if len(project_sarif.get("runs", [])) == 0:
            return
        if self.merged_sarif is None:
            self.merged_sarif = project_sarif
            return
        merged_run = self.merged_sarif["runs"][0]
        project_run = project_sarif["runs"][0]
        merged_run["results"] += project_run["results"]
        merged_run["artifacts"] = merged_run.get("artifacts", []) + project_run.get(
            "artifacts", []
        )

    def after_lint_files(self):
        if self.merged_sarif is not None:
            with open(self.sarif_output_file, "w", encoding="utf-8") as sarif_file:
                json.dump(self.merged_sarif, sarif_file, sort_keys=True, indent=2)
