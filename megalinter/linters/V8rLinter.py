#!/usr/bin/env python3
"""
Use v8r to validate JSON, YAML and TOML files
https://github.com/chris48s/v8r
"""

from megalinter import Linter, config


class V8rLinter(Linter):
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
