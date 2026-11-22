#!/usr/bin/env python3
"""
Use gherkin-lint to check Gherkin files
"""

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)


class GherkinLintLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return gherkin_lint_json_to_sarif(return_stdout, self.workspace)

    # Forward excluded directories through --ignore, which overrides the
    # .gherkin-lintignore file: its patterns are merged in. Without that file,
    # gherkin-lint ignores node_modules/** by default, which --ignore replaces
    def manage_excluded_directories_config(self, cmd):
        if any(arg in ("-i", "--ignore") for arg in cmd):
            return cmd
        patterns = self.read_workspace_file_lines(".gherkin-lintignore")
        if any("," in pattern for pattern in patterns):
            # gherkin-lint splits --ignore on commas, which would cut a brace
            # pattern (ex: {a,b}/**) in two: keep the user's ignore file alone
            self.log_project_exclude_forwarding(
                f"EXCLUDED_DIRECTORIES are not forwarded to {self.linter_name}: "
                ".gherkin-lintignore holds patterns with commas, that its --ignore "
                "argument can not receive"
            )
            return cmd
        if len(patterns) == 0:
            patterns = ["node_modules/**"]
        for excluded_dir in self.get_project_exclude_directories():
            pattern = f"**/{excluded_dir}/**"
            if pattern not in patterns:
                patterns += [pattern]
        cmd += ["--ignore", ",".join(patterns)]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through "
            f"--ignore, merged with .gherkin-lintignore patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd


# gherkin-lint prints its JSON array on stderr, with the absolute path of each file.
# The line is a string for some of the errors
def gherkin_lint_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "gherkin-lint", url="https://github.com/gherkin-lint/gherkin-lint"
    )
    for files in utils.find_json_values(stdout, list):
        for file_result in files:
            if not isinstance(file_result, dict) or "filePath" not in file_result:
                continue
            for error in file_result.get("errors", []):
                line = str(error.get("line", ""))
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_ERROR,
                        error.get("message"),
                        error.get("rule") or "gherkin-lint",
                        file_uri=to_sarif_uri(file_result["filePath"], workspace),
                        start_line=to_one_based(int(line)) if line.isdigit() else None,
                    )
                )
    return SarifBuilder().add_run(run)
