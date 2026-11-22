#!/usr/bin/env python3
"""
Class for lychee
"""

import os

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)


# ref: https://github.com/lycheeverse/lychee#commandline-parameters
class LycheeLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return lychee_json_to_sarif(return_stdout, self.workspace)

    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # `--no-progress` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--no-progress" in self.cli_lint_user_args:
            cmd.pop(cmd.index("--no-progress"))

        # `-n` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "-n" in self.cli_lint_user_args:
            cmd.pop(cmd.index("-n"))

        # `--format <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--format" in self.cli_lint_user_args:
            cmd.pop(cmd.index("--format") + 1)
            cmd.pop(cmd.index("--format"))

        # `-f <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "-f" in self.cli_lint_user_args:
            cmd.pop(cmd.index("-f") + 1)
            cmd.pop(cmd.index("-f"))

        # `--output <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "--output" in self.cli_lint_user_args:
            cmd.pop(cmd.index("--output") + 1)
            cmd.pop(cmd.index("--output"))

        # `--output <arg_value>` has been sent by user in SPELL_LYCHEE_ARGUMENTS
        # make sure that it's only once in the arguments list
        if "-o" in self.cli_lint_user_args:
            cmd.pop(cmd.index("-o") + 1)
            cmd.pop(cmd.index("-o"))

        # lychee accepts only one --format: the one of the SARIF arguments replaces the
        # default one of the descriptor
        if self.output_sarif is True:
            while cmd.count("--format") > 1:
                format_index = cmd.index("--format")
                cmd.pop(format_index + 1)
                cmd.pop(format_index)

        cmd += self.build_ignore_file_exclude_arguments()

        return cmd

    # Lychee only reads .lycheeignore from its working directory and has no CLI
    # option to pass another location: forward the resolved file as --exclude
    def build_ignore_file_exclude_arguments(self):
        if self.ignore_file is None or not os.path.isfile(self.ignore_file):
            return []
        # Lint commands run in the workspace, where lychee finds it by itself
        if os.path.abspath(self.ignore_file) == os.path.abspath(
            os.path.join(self.workspace, ".lycheeignore")
        ):
            return []
        exclude_args = []
        with open(self.ignore_file, encoding="utf-8", errors="ignore") as file:
            for line in file.read().splitlines():
                line = line.strip()
                if line != "" and not line.startswith("#"):
                    exclude_args.append("--exclude=" + line)
        return exclude_args


# The links that fail are grouped by the file that contains them, in error_map, and
# the ones that time out in timeout_map
def lychee_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple("lychee", url="https://lychee.cli.rs")
    for output in utils.find_json_values(
        stdout, dict, lambda value: isinstance(value.get("error_map"), dict)
    ):
        for map_name, rule_id in (
            ("error_map", "broken-link"),
            ("timeout_map", "link-timeout"),
        ):
            for source, links in (output.get(map_name) or {}).items():
                for link in links:
                    status = link.get("status") or {}
                    details = f" ({status['details']})" if status.get("details") else ""
                    span = link.get("span") or {}
                    run.add_result(
                        SarifResultBuilder().init_simple(
                            LEVEL_ERROR,
                            f"{link.get('url')}: {status.get('text')}{details}",
                            rule_id,
                            file_uri=to_sarif_uri(source, workspace),
                            start_line=to_one_based(span.get("line")),
                            start_column=to_one_based(span.get("column")),
                        )
                    )
    return SarifBuilder().add_run(run)
