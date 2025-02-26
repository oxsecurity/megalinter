#!/usr/bin/env python3
"""
Use PowerShell to lint Powershell files
https://github.com/PowerShell/PSScriptAnalyzer
"""
import sys
from shutil import get_terminal_size

from megalinter import Linter, config, utils


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
            # Prevent Out-String (piped later) to strip ANSI escape sequences
            # and start forming a call to Invoke-ScriptAnalyzer
            pwsh_script = [
                "$PSStyle.OutputRendering = 'Ansi'; Invoke-ScriptAnalyzer -EnableExit"
            ]
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

        if self.linter_name == "powershell":
            pwsh_script[0] = self.format_powershell_output(pwsh_script[0])

        cmd = [
            *self.cli_executable,
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd

    def format_powershell_output(self, pwsh_script):
        if utils.is_ci():
            width = (
                150  # Use a default width in CI environments to prevent output cutoff
            )
        else:
            width = get_terminal_size().columns  # Use the terminal width when not in CI

        # Format the output to a table with specific columns
        pwsh_script += (
            " | Format-Table -AutoSize -Wrap -Property "
            "@{Name='Severity'; Expression={$_.Severity}; Alignment='left'},"
            " @{Name='RuleName'; Expression={$_.RuleName}; Alignment='left'},"
            " @{Name='ScriptName'; Expression={$_.ScriptName}; Alignment='left'},"
            " @{Name='Line'; Expression={$_.Line}; Alignment='right'},"
            " @{Name='Message'; Expression={$_.Message}; Alignment='left'}"
        )

        # Ensure the output string fits within the specified width
        pwsh_script += f" | Out-String -Width {width}"
        return pwsh_script

    # Build the CLI command to get linter version
    def build_version_command(self):
        cmd = [
            *self.cli_executable_version,
            "-Command",
            "Write-Output $PsVersionTable.PsVersion;",
        ]
        return cmd
