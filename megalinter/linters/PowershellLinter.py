#!/usr/bin/env python3
"""
Use PowerShell to lint Powershell files
https://github.com/PowerShell/PSScriptAnalyzer
"""
import sys

from megalinter import Linter, config


class PowershellLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super(PowershellLinter, self).__init__(params, linter_config)
        self.cli_executable = ["powershell"] if sys.platform == "win32" else ["pwsh"]
        self.cli_executable_help = [*self.cli_executable]
        self.cli_executable_version = [*self.cli_executable]

    # Build the CLI command to call to lint a file with a powershell script
    def build_lint_command(self, file=None):
        pwsh_script = []
        if self.linter_name == "powershell":
            pwsh_script = ["Invoke-ScriptAnalyzer -EnableExit"]
        elif self.linter_name == "powershell_formatter":
            pwsh_script = ["Invoke-Formatter"]

        if self.config_file is not None:
            pwsh_script[0] += " -Settings " + self.config_file

        if self.linter_name == "powershell":
            if self.cli_lint_mode == "file":
                pwsh_script[0] += f" -Path '{file}'"
            elif self.cli_lint_mode == "project":
                pwsh_script[0] += f" -Path '{self.workspace}' -Recurse"
        elif self.linter_name == "powershell_formatter":
            pwsh_script[0] += f" -ScriptDefinition (Get-Content -Path '{file}' -Raw)"

            if self.apply_fixes is True:
                file_encoding = config.get(
                    self.request_id,
                    "POWERSHELL_POWERSHELL_FORMATTER_OUTPUT_ENCODING",
                    "utf8",
                )

                pwsh_script[
                    0
                ] += f" | Out-File '{file}' -Encoding {file_encoding} -NoNewline"

        if (
            self.linter_name == "powershell"
            and self.apply_fixes is True
            and self.cli_lint_fix_arg_name is not None
        ):
            pwsh_script[0] += f" {self.cli_lint_fix_arg_name}"
        cmd = [
            *self.cli_executable,
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd

    # Build the CLI command to get linter version
    def build_version_command(self):
        cmd = [
            *self.cli_executable_version,
            "-Command",
            "Write-Output $PsVersionTable.PsVersion;",
        ]
        return cmd
