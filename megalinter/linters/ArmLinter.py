#!/usr/bin/env python3
"""
Use Azure Resource Manager Template Toolkit to lint ARM files
https://github.com/Azure/arm-ttk
"""

import sys

from megalinter import Linter, config


class ArmLinter(Linter):
    arm_ttk_psd1 = ""

    def collect_files(self, all_files):
        super().collect_files(all_files)
        self.drop_files_unsafe_for_interpreter()

    # Build the CLI command to call to lint a file with a powershell script
    def build_lint_command(self, file=None):
        self.arm_ttk_psd1 = config.get(
            self.request_id, "ARM_TTK_PSD1", "/usr/bin/arm-ttk"
        )
        # Paths are passed through environment variables: writing them in the
        # script would let a quote in a file name run as PowerShell code
        self.lint_command_env = {"MEGALINTER_LINT_FILE": str(file)}
        pwsh_script = ["Import-Module " + self.arm_ttk_psd1 + " ;"]
        if self.config_file is not None:
            self.lint_command_env["MEGALINTER_LINT_CONFIG_FILE"] = str(self.config_file)
            pwsh_script += [
                "${config} = $(Import-PowerShellDataFile"
                " -LiteralPath $env:MEGALINTER_LINT_CONFIG_FILE) ;",
                "Test-AzTemplate @config -TemplatePath $env:MEGALINTER_LINT_FILE ;",
            ]
        else:
            pwsh_script += ["Test-AzTemplate -TemplatePath $env:MEGALINTER_LINT_FILE ;"]
        pwsh_script += ["if (${Error}.Count) {exit 1}"]
        cmd = [
            ("powershell" if sys.platform == "win32" else "pwsh"),
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd

    # Build the CLI command to get linter version
    def build_version_command(self):
        pwsh_script = [
            "Import-Module " + self.arm_ttk_psd1 + " ;",
            "$TAZ_V = (Test-AzTemplate -version);",
            "Write-Output $TAZ_V;",
        ]
        cmd = [
            ("powershell" if sys.platform == "win32" else "pwsh"),
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd

    # Build the CLI command to get linter help
    def build_help_command(self):
        pwsh_script = [
            "Import-Module " + self.arm_ttk_psd1 + " ;",
            "$TAZ_V = (Test-AzTemplate -help);",
            "Write-Output $TAZ_V;",
        ]
        cmd = [
            ("powershell" if sys.platform == "win32" else "pwsh"),
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd
