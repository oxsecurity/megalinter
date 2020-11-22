#!/usr/bin/env python3
"""
Use PowerShell to lint Powershell files
https://github.com/PowerShell/PSScriptAnalyzer
"""
import sys

from megalinter import Linter


class PowershellLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super(PowershellLinter, self).__init__(params, linter_config)
        self.cli_executable = "powershell" if sys.platform == "win32" else "pwsh"
        self.cli_executable_help = self.cli_executable
        self.cli_executable_version = self.cli_executable

    # Build the CLI command to call to lint a file with a powershell script
    def build_lint_command(self, file=None):
        pwsh_script = ["Invoke-ScriptAnalyzer -EnableExit"]
        if self.config_file is not None:
            pwsh_script[0] += " -Settings " + self.config_file
        pwsh_script[0] += " -Path " + file
        cmd = [
            self.cli_executable,
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd

    # Build the CLI command to get linter version
    def build_version_command(self):
        cmd = [
            self.cli_executable_version,
            "-Command",
            "Write-Output $PsVersionTable.PsVersion;",
        ]
        return cmd
