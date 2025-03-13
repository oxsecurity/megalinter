#!/usr/bin/env python3
"""
Use PMD to lint java files
"""

import os.path
import tempfile
import uuid

from megalinter import Linter


class JavaPmdLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        # Base command
        cmd = [*self.cli_executable, "check"]
        # Add other lint cli arguments if defined
        self.cli_lint_extra_args = self.replace_vars(self.cli_lint_extra_args)
        cmd += self.cli_lint_extra_args
        # Add user-defined extra arguments if defined
        self.cli_lint_user_args = self.replace_vars(self.cli_lint_user_args)
        cmd += self.cli_lint_user_args
        if self.config_file is not None:
            cmd += [self.cli_config_arg_name, self.config_file]
        # Manage ignore arguments if necessary
        cmd += self.get_ignore_arguments(cmd)

        # Manage SARIF arguments if necessary
        cmd += self.get_sarif_arguments()

        # Add other lint cli arguments after other arguments if defined
        self.cli_lint_extra_args_after = self.replace_vars(
            self.cli_lint_extra_args_after
        )
        cmd += self.cli_lint_extra_args_after
        # Add dir/file arguments
        # single file
        if self.cli_lint_mode == "file":
            file_args = ["-dir", file]
        # lint the whole directory
        elif self.cli_lint_mode == "project":
            file_args = ["-dir", self.workspace]
        # lint a list of files
        else:  # self.cli_lint_mode == "list_of_files":
            temp_list_of_files_for_pmd = (
                tempfile.gettempdir()
                + os.path.sep
                + str(uuid.uuid4())
                + "-pmd-files.txt"
            )
            with open(temp_list_of_files_for_pmd, "w", encoding="utf-8") as f:
                f.write("\n".join(self.files))
            file_args = ["--file-list", temp_list_of_files_for_pmd]
        cmd += file_args
        return cmd
