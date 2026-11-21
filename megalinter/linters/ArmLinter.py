#!/usr/bin/env python3
"""
Use Azure Resource Manager Template Toolkit to lint ARM files
https://github.com/Azure/arm-ttk
"""

from megalinter import Linter, config, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)

# Keeps what the SARIF needs of the results of Test-AzTemplate, that are too deep to be
# converted to JSON as they are
ARM_TTK_JSON_PROJECTION = (
    "| ForEach-Object { [pscustomobject]@{ Name = $_.Name; Group = $_.Group;"
    ' Passed = $_.Passed; File = "$($_.File.FullPath)";'
    ' Errors = @($_.Errors | ForEach-Object { [pscustomobject]@{ Message = "$_";'
    ' Id = "$($_.FullyQualifiedErrorId)"; Line = $_.Location.Line;'
    " Column = $_.Location.Column } });"
    ' Warnings = @($_.Warnings | ForEach-Object { "$_" }) } }'
    " | ConvertTo-Json -Depth 5 -Compress -AsArray"
)


class ArmLinter(Linter):
    arm_ttk_psd1 = ""

    def collect_files(self, all_files):
        super().collect_files(all_files)
        self.drop_files_unsafe_for_interpreter()

    def get_arm_ttk_psd1(self):
        if self.native_toolchain is not None:
            return self.native_toolchain.env["ARM_TTK_PSD1"]
        return config.get(self.request_id, "ARM_TTK_PSD1", "/usr/bin/arm-ttk")

    def convert_output_to_sarif(self, return_stdout):
        return arm_ttk_json_to_sarif(return_stdout, self.workspace)

    # Build the CLI command to call to lint a file with a powershell script
    def build_lint_command(self, file=None):
        self.arm_ttk_psd1 = self.get_arm_ttk_psd1()
        self.get_sarif_arguments()
        json_output = " " + ARM_TTK_JSON_PROJECTION if self.output_sarif else ""
        # Paths are passed through environment variables: writing them in the
        # script would let a quote in a file name run as PowerShell code
        self.lint_command_env = {"MEGALINTER_LINT_FILE": str(file)}
        pwsh_script = ["Import-Module " + self.arm_ttk_psd1 + " ;"]
        if self.config_file is not None:
            self.lint_command_env["MEGALINTER_LINT_CONFIG_FILE"] = str(self.config_file)
            pwsh_script += [
                "${config} = $(Import-PowerShellDataFile"
                " -LiteralPath $env:MEGALINTER_LINT_CONFIG_FILE) ;",
                "Test-AzTemplate @config -TemplatePath $env:MEGALINTER_LINT_FILE"
                + json_output
                + " ;",
            ]
        else:
            pwsh_script += [
                "Test-AzTemplate -TemplatePath $env:MEGALINTER_LINT_FILE"
                + json_output
                + " ;"
            ]
        pwsh_script += ["if (${Error}.Count) {exit 1}"]
        cmd = [
            "pwsh",
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd

    # Build the CLI command to get linter version
    def build_version_command(self):
        self.arm_ttk_psd1 = self.get_arm_ttk_psd1()
        pwsh_script = [
            "Import-Module " + self.arm_ttk_psd1 + " ;",
            "$TAZ_V = (Test-AzTemplate -version);",
            "Write-Output $TAZ_V;",
        ]
        cmd = [
            "pwsh",
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd

    # Build the CLI command to get linter help
    def build_help_command(self):
        self.arm_ttk_psd1 = self.get_arm_ttk_psd1()
        pwsh_script = [
            "Import-Module " + self.arm_ttk_psd1 + " ;",
            "$TAZ_V = (Test-AzTemplate -help);",
            "Write-Output $TAZ_V;",
        ]
        cmd = [
            "pwsh",
            "-NoProfile",
            "-NoLogo",
            "-Command",
            "\n".join(pwsh_script),
        ]
        return cmd


# One result per error or warning of each test of arm-ttk, located when the test
# gives a position
def arm_ttk_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "arm-ttk", url="https://github.com/Azure/arm-ttk"
    )
    for tests in utils.find_json_values(stdout, list):
        for test in tests:
            if not isinstance(test, dict) or "Name" not in test:
                continue
            file_uri = (
                to_sarif_uri(test["File"], workspace) if test.get("File") else None
            )
            for error in test.get("Errors") or []:
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_ERROR,
                        error.get("Message"),
                        test["Name"],
                        file_uri=file_uri,
                        start_line=to_one_based(error.get("Line")),
                        start_column=to_one_based(error.get("Column")),
                    )
                )
            for warning in test.get("Warnings") or []:
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_WARNING, warning, test["Name"], file_uri=file_uri
                    )
                )
    return SarifBuilder().add_run(run)
