#!/usr/bin/env python3
"""
Shared base for the Salesforce Code Analyzer engines (apex, aura, flow, lwc)
https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html
"""

from megalinter import Linter


class SalesforceCodeAnalyzerLinter(Linter):
    # sf code-analyzer infers its report format from the --output-file
    # extension, and that flag is already baked into cli_lint_extra_args
    # (not appended separately like most linters' cli_sarif_args), so a
    # second --output-file from the standard SARIF injection would collide
    # with it and get rejected by the CLI. Swap the extension in place
    # instead, and point sarif_default_output_file at the resulting file so
    # the base class picks it up after the run.
    def build_lint_command(self, file=None):
        if self.can_output_sarif is True and self.output_sarif is True:
            self.cli_lint_extra_args = [
                item[: -len(".csv")] + ".sarif" if item.endswith(".csv") else item
                for item in self.cli_lint_extra_args
            ]
            output_file_index = self.cli_lint_extra_args.index("--output-file") + 1
            self.sarif_default_output_file = self.cli_lint_extra_args[
                output_file_index
            ].replace("{{REPORT_FOLDER}}/", "")
        return super().build_lint_command(file)
