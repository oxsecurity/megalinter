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
        # Filter v8r output to show only validation errors:
        # - Remove success lines (✔ file is valid)
        # - Remove info lines (ℹ Could not find a schema...)
        # Only actual validation error lines (✖) and their details are kept.
        # Combined with --ignore-errors, "no schema found" produces no
        # output and exit code 0.
        if return_stdout:
            filtered_lines = []
            for line in return_stdout.splitlines():
                stripped = line.strip()
                if stripped.startswith("✔") or stripped.startswith("ℹ"):
                    continue
                filtered_lines.append(line)
            return_stdout = "\n".join(filtered_lines)
        return return_code, return_stdout
