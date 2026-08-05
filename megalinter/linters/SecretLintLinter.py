#!/usr/bin/env python3
"""
Use secretlint to find secrets in sources
https://github.com/secretlint/secretlint
"""

import os

from megalinter import Linter, config


class SecretLintLinter(Linter):
    # Called before linting files
    def get_ignore_arguments(self, cmd):
        # Forward excluded directories in project mode: secretlint's walker
        # only resolves ignore files by base name inside the scanned tree, so
        # a merged ignore file is temporarily written at the workspace root
        # (removed after the run) and passed by base name
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and "--secretlintignore" not in self.cli_lint_user_args
        ):
            ignore_lines = self.read_workspace_file_lines(".secretlintignore")
            if len(ignore_lines) == 0:
                ignore_lines = self.read_workspace_file_lines(".gitignore")
            for excluded_dir in self.get_project_exclude_directories():
                ignore_line = f"{excluded_dir}/"
                if ignore_line not in ignore_lines:
                    ignore_lines += [ignore_line]
            self.write_workspace_generated_file(
                ".megalinter-secretlintignore", ignore_lines
            )
            return ["--secretlintignore", ".megalinter-secretlintignore"]
        ignore_args = super().get_ignore_arguments(cmd)
        # secretlint v13+ resolves the --secretlintignore value through its
        # ripgrep-style walker (@secretlint/walker), which matches ignore files
        # by base name against each scanned directory entry. The absolute path
        # MegaLinter builds by default never matches a base name, so the ignore
        # file is silently skipped and intentional test fixtures get flagged.
        # Pass the base name so the walker discovers the .secretlintignore that
        # sits at the workspace root (its patterns then apply from that root).
        if len(ignore_args) >= 2 and ignore_args[0] == "--secretlintignore":
            ignore_args = [
                "--secretlintignore",
                os.path.basename(ignore_args[1]),
                *ignore_args[2:],
            ]
        # Use .gitignore as .secretlintignore
        # only if --secretlintignore is not defined and .secretlintignore not found
        if (
            len(ignore_args) == 0
            and "--secretlintignore" not in self.cli_lint_user_args
            and (
                os.path.isfile(os.path.join(self.workspace, ".gitignore"))
                and (
                    not os.path.isfile(
                        os.path.join(self.workspace, ".secretlintignore")
                    )
                )
            )
        ):
            ignore_args = ["--secretlintignore", ".gitignore"]
        return ignore_args

    def execute_lint_command(self, command):
        try:
            return super().execute_lint_command(command)
        finally:
            self.cleanup_workspace_generated_files()

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_SECRETLINT_FILE_EXTENSIONS", [".ini"]
            )
