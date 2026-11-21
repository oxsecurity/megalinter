#!/usr/bin/env python3
"""
Use PowerShell to lint Powershell files
https://github.com/PowerShell/PSScriptAnalyzer
"""

import logging
import re
from shutil import get_terminal_size

from megalinter import Linter, config, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_NOTE,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)

POWERSHELL_LEVELS = {
    "Error": LEVEL_ERROR,
    "ParseError": LEVEL_ERROR,
    "Warning": LEVEL_WARNING,
}
POWERSHELL_RULES_URL = (
    "https://github.com/PowerShell/PSScriptAnalyzer/blob/main/docs/Rules"
)
# Findings as JSON, instead of the table that is displayed to the user
POWERSHELL_JSON_OUTPUT = (
    " | Select-Object RuleName,"
    " @{Name='Severity'; Expression={$_.Severity.ToString()}},"
    " ScriptPath, Line, Column,"
    " @{Name='EndLine'; Expression={$_.Extent.EndLineNumber}},"
    " @{Name='EndColumn'; Expression={$_.Extent.EndColumnNumber}},"
    " Message | ConvertTo-Json -Compress -AsArray"
)


class PowershellLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super().__init__(params, linter_config)
        self.cli_executable = ["pwsh"]
        self.cli_executable_help = [*self.cli_executable]
        self.cli_executable_version = [*self.cli_executable]

    def collect_files(self, all_files):
        super().collect_files(all_files)
        self.drop_files_unsafe_for_interpreter()

    def convert_output_to_sarif(self, return_stdout):
        return powershell_json_to_sarif(return_stdout, self.workspace)

    # Build the CLI command to call to lint a file with a powershell script
    def build_lint_command(self, file=None):
        # This command does not use the default command builder, which
        # resolves the SARIF output file
        self.get_sarif_arguments()
        # Paths are passed through environment variables: writing them in the
        # script would let a quote in a file name run as PowerShell code
        self.lint_command_env = {
            "MEGALINTER_LINT_FILE": str(file),
            "MEGALINTER_LINT_WORKSPACE": str(self.workspace),
        }
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
            self.lint_command_env["MEGALINTER_LINT_CONFIG_FILE"] = str(self.config_file)
            pwsh_script[0] += " -Settings $env:MEGALINTER_LINT_CONFIG_FILE"

        if self.linter_name == "powershell":
            if self.cli_lint_mode == "file":
                pwsh_script[0] += " -Path $env:MEGALINTER_LINT_FILE"
            elif self.cli_lint_mode == "project":
                pwsh_script[0] += " -Path $env:MEGALINTER_LINT_WORKSPACE -Recurse"
        elif self.linter_name == "powershell_formatter":
            pwsh_script[0] += (
                " -ScriptDefinition"
                " (Get-Content -LiteralPath $env:MEGALINTER_LINT_FILE -Raw)"
            )

            if self.apply_fixes is True:
                self.try_fix = True
                file_encoding = config.get(
                    self.request_id,
                    "POWERSHELL_POWERSHELL_FORMATTER_OUTPUT_ENCODING",
                    "utf8",
                )
                if not re.fullmatch(r"[A-Za-z0-9_-]+", file_encoding):
                    logging.warning(
                        f"Invalid POWERSHELL_POWERSHELL_FORMATTER_OUTPUT_ENCODING "
                        f"{file_encoding!r}, using utf8"
                    )
                    file_encoding = "utf8"

                pwsh_script[0] += (
                    " | Out-File -LiteralPath $env:MEGALINTER_LINT_FILE"
                    f" -Encoding {file_encoding} -NoNewline"
                )

        if (
            self.linter_name == "powershell"
            and self.apply_fixes is True
            and self.cli_lint_fix_arg_name is not None
        ):
            pwsh_script[0] += f" {self.cli_lint_fix_arg_name}"
            self.try_fix = True

        if self.linter_name == "powershell":
            if self.output_sarif is True:
                pwsh_script[0] += POWERSHELL_JSON_OUTPUT
            else:
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


# SARIF is built from the JSON findings of Invoke-ScriptAnalyzer
def powershell_json_to_sarif(stdout, workspace=None):
    findings = utils.find_json_value(
        stdout,
        list,
        lambda value: all(
            isinstance(item, dict) and "RuleName" in item for item in value
        ),
    )
    if findings is None and stdout.strip() != "":
        logging.warning("[powershell] No JSON output found to build SARIF from")
    run = SarifRunBuilder().init_simple(
        "PSScriptAnalyzer", url="https://github.com/PowerShell/PSScriptAnalyzer"
    )
    for finding in findings or []:
        rule_id = finding.get("RuleName") or "ParseError"
        run.add_rule(
            SarifRuleBuilder().init_simple(
                rule_id,
                help_uri=(
                    f"{POWERSHELL_RULES_URL}/{rule_id[2:]}.md"
                    if rule_id.startswith("PS")
                    else None
                ),
            )
        )
        run.add_result(
            SarifResultBuilder().init_simple(
                POWERSHELL_LEVELS.get(finding.get("Severity"), LEVEL_NOTE),
                finding.get("Message"),
                rule_id,
                file_uri=to_sarif_uri(finding.get("ScriptPath") or "", workspace),
                start_line=finding.get("Line"),
                start_column=finding.get("Column"),
                end_line=finding.get("EndLine"),
                end_column=finding.get("EndColumn"),
            )
        )
    return SarifBuilder().add_run(run)
