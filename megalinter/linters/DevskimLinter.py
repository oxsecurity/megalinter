#!/usr/bin/env python3
"""
Use Devskim to lint Infrastructure as Code
"""

from megalinter import Linter, config

# devskim -g replaces its default ignore globs, so they must be re-included
DEVSKIM_DEFAULT_IGNORE_GLOBS = ["**/.git/**", "**/bin/**"]


class DevskimLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not any(arg in ("-g", "--ignore-globs") for arg in cmd)
        ):
            ignore_globs = list(DEVSKIM_DEFAULT_IGNORE_GLOBS)
            for excluded_dir in self.get_project_exclude_directories():
                glob = f"**/{excluded_dir}/**"
                if glob not in ignore_globs:
                    ignore_globs += [glob]
            cmd += ["-g", ",".join(ignore_globs)]
            self.log_project_exclude_forwarding(
                f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through -g, "
                f"merged with devskim default ignore globs "
                f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
            )

        return cmd

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_DEVSKIM_FILE_EXTENSIONS", [".sh"]
            )
