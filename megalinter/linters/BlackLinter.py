#!/usr/bin/env python3
"""
Use black to check Python files formatting
black ignores its cache when --diff is set, so the check runs without --diff (served
from black's cache for the unchanged files), and the diff is only computed for the files
black would reformat
"""

import re

from megalinter import Linter

BLACK_WOULD_REFORMAT_REGEX = re.compile(r"^would reformat (.+)$", re.MULTILINE)
BLACK_SUMMARY_REGEX = re.compile(
    r"^(Oh no!|All done!|\d+ files? (would be|would fail|reformatted|left unchanged))"
)


class BlackLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        cmd = super().build_lint_command(file)
        self.black_diff_on_failure = False
        self.black_lint_targets = None
        if self.try_fix is not True and "--check" in cmd and "--diff" in cmd:
            cmd.remove("--diff")
            self.black_diff_on_failure = True
            self.black_lint_targets = self.get_black_lint_targets(cmd, file)
        return cmd

    # The arguments ending the command line that designate what black analyzes
    def get_black_lint_targets(self, cmd, file):
        if file is not None:
            targets = [file]
        elif self.cli_lint_mode == "list_of_files":
            targets = list(self.files)
        else:
            targets = list(self.cli_lint_mode_project_extra_args_after)
        targets_count = len(targets)
        if targets_count > 0 and cmd[-targets_count:] == targets:
            return targets
        return None

    def execute_lint_command(self, command):
        return_code, return_stdout = super().execute_lint_command(command)
        if (
            getattr(self, "black_diff_on_failure", False) is not True
            or return_code == 0
        ):
            return return_code, return_stdout
        diff_command = self.build_black_diff_command(
            command, return_code, return_stdout
        )
        if diff_command is None:
            return return_code, return_stdout
        _diff_return_code, diff_stdout = super().execute_lint_command(diff_command)
        return return_code, merge_black_outputs(diff_stdout, return_stdout)

    def build_black_diff_command(self, command, check_return_code, check_stdout):
        after_check = command.index("--check") + 1
        with_diff = [*command[:after_check], "--diff", *command[after_check:]]
        if self.black_lint_targets is None:
            # Unknown layout of the command line: compute the diff of the whole command
            return with_diff
        to_reformat = BLACK_WOULD_REFORMAT_REGEX.findall(check_stdout)
        if len(to_reformat) == 0:
            # --quiet hides the files to reformat (exit code 1), but not their diff
            if check_return_code == 1 or any(
                arg in ("-q", "--quiet") for arg in command
            ):
                return with_diff
            # Only parse errors: there is no diff to show
            return None
        return [
            *with_diff[: len(with_diff) - len(self.black_lint_targets)],
            *[path.strip() for path in to_reformat],
        ]


# The diff, then the messages of the check run (reformat list, parse errors and summary
# of every analyzed file), without the summary of the diff run that only knows the
# files to reformat
def merge_black_outputs(diff_stdout, check_stdout):
    diff_lines = [
        line
        for line in diff_stdout.splitlines()
        if BLACK_SUMMARY_REGEX.match(line) is None
        and BLACK_WOULD_REFORMAT_REGEX.match(line) is None
    ]
    return "\n".join([*diff_lines, check_stdout.strip()]).strip() + "\n"
