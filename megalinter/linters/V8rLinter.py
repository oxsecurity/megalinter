#!/usr/bin/env python3
"""
Use v8r to validate JSON, YAML and TOML files
https://github.com/chris48s/v8r
"""

from megalinter import Linter, config, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)


class V8rLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return v8r_json_to_sarif(return_stdout, self.workspace)

    def execute_lint_command(self, command):
        # v8r does not support a CLI argument to specify the config file.
        # Instead, it reads the V8R_CONFIG_FILE environment variable.
        # When MegaLinter has resolved a config file, pass it via that env var.
        if self.config_file is not None:
            # _cached_subprocess_env is pre-built by Linter.run() before any files are linted.
            # If it hasn't been set yet (e.g. in standalone/test scenarios), build it here.
            cached_env = getattr(self, "_cached_subprocess_env", None)
            if cached_env is not None:
                cached_env["V8R_CONFIG_FILE"] = self.config_file
            else:
                self._cached_subprocess_env = {
                    **config.build_env(
                        self.request_id, True, self.unsecured_env_variables
                    ),
                    "FORCE_COLOR": "0",
                    "V8R_CONFIG_FILE": self.config_file,
                }
        return_code, return_stdout = super().execute_lint_command(command)
        if return_stdout:
            return_stdout = V8rLinter._filter_output(return_stdout)
        return return_code, return_stdout

    @staticmethod
    def _filter_output(output):
        lines = output.splitlines()
        noise = set()
        for i, line in enumerate(lines):
            s = line.strip()
            if (
                s.startswith("✔")
                or s.startswith("ℹ")
                or "Could not find a schema to validate" in s
                or ("unknown format" in s and "ignored in schema" in s)
                or ("schema with key or id" in s and "already exists" in s)
            ):
                noise.add(i)
            elif "Found multiple possible schemas to validate" in s:
                noise.add(i)
                # Walk backwards to discard the candidate schema-list lines that precede this
                j = i - 1
                while j >= 0:
                    prev = lines[j].strip()
                    if prev == "" or not prev.startswith("✖"):
                        noise.add(j)
                        j -= 1
                    else:
                        break
        # Build filtered output, collapsing consecutive blank lines
        result = []
        prev_blank = False
        for i, line in enumerate(lines):
            if i in noise:
                continue
            is_blank = line.strip() == ""
            if is_blank and prev_blank:
                continue
            result.append(line)
            prev_blank = is_blank
        return "\n".join(result).strip()


# v8r prints its JSON on stdout, and its logs on stderr. A result that is not valid is
# located in the file only by a JSON pointer: a result for a file that could not be
# validated (no schema found...) is ignored, as --ignore-errors does
def v8r_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple("v8r", url="https://github.com/chris48s/v8r")
    for output in utils.find_json_values(
        stdout, dict, lambda value: isinstance(value.get("results"), list)
    ):
        for result in output["results"]:
            if result.get("valid") is not False:
                continue
            document = (
                f" (document {result['documentIndex'] + 1})"
                if isinstance(result.get("documentIndex"), int)
                else ""
            )
            for error in result.get("errors") or []:
                additional = (error.get("params") or {}).get("additionalProperty")
                found = (
                    f", found additional property '{additional}'" if additional else ""
                )
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_ERROR,
                        f"{error.get('instancePath') or '/'} {error.get('message')}"
                        f"{found}{document}",
                        error.get("keyword") or "schema-validation",
                        file_uri=to_sarif_uri(result["fileLocation"], workspace),
                    )
                )
    return SarifBuilder().add_run(run)
