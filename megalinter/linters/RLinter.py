#!/usr/bin/env python3
"""
Use lintr to lint R files
https://github.com/r-lib/lintr
"""

import os
import shutil
from pathlib import Path

from megalinter import Linter


class RLinter(Linter):
    _r_sarif_report = None

    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        # Build command in R format
        r_commands = [
            # Change the working directory to match the file
            f"setwd('{Path(file).parent}')",
            # Instruct lintr to walk up the directory tree
            f"lintr:::read_settings('{self.config_file_name}')",
            f"lints <- lintr::lint('{Path(file).name}')",
        ]

        if self.config_file:
            # Instruct lintr to load an absolute filepath
            r_commands.insert(0, f"options('lintr.linter_file' = '{self.config_file}')")

        # RLinter builds its own R -e command instead of going through
        # complete_command_line(), so it bypasses the standard SARIF argument
        # injection (get_sarif_arguments() is called here for its side effect
        # of resolving self.sarif_output_file, not for its cli_sarif_args return)
        self._r_sarif_report = None
        if self.can_output_sarif is True and self.output_sarif is True:
            self.get_sarif_arguments()
            # sarif_output() aborts with "Package path needs to be a
            # relative path" whenever attr(lints, "path") is NULL — which it
            # always is for plain lint() results (that attribute is only
            # ever set by lint_dir()/lint_package()). Set it ourselves;
            # the value only feeds the SARIF ROOTPATH URI, not file I/O, so
            # any non-NULL path works. The filename itself must stay a bare
            # name relative to the R process's own cwd, so write it there
            # and move it into place ourselves once the command has run
            # (see execute_lint_command below)
            r_cwd = os.path.abspath(os.path.join(self.workspace, Path(file).parent))
            self._r_sarif_report = os.path.join(r_cwd, "lintr-report.sarif")
            r_commands.append("attr(lints, 'path') <- '.'")
            r_commands.append(
                "lintr::sarif_output(lints, filename = 'lintr-report.sarif')"
            )

        r_commands += [
            "print(lints)",
            "quit(save = 'no', status = if (length(lints) > 0) 1 else 0)",
        ]

        # Build shell command
        cmd = ["R", "--slave", "-e", ";".join(r_commands)]
        return cmd

    def execute_lint_command(self, command):
        return_code, return_output = super().execute_lint_command(command)
        if self._r_sarif_report is not None and os.path.isfile(self._r_sarif_report):
            shutil.move(self._r_sarif_report, self.sarif_output_file)
        return return_code, return_output

    # Build the CLI command to request lintr version
    def build_version_command(self):
        # Build command in R format
        r_commands = ['packageVersion("lintr");']
        # Build shell command
        cmd = ["R", "--slave", "-e", "".join(r_commands)]
        return cmd

    # Build the CLI command to request lintr help
    def build_help_command(self):
        # Build command in R format
        r_commands = ['help("lintr");']
        # Build shell command
        cmd = ["R", "--slave", "-e", "".join(r_commands)]
        return cmd
