#!/usr/bin/env python3
"""
Use cljstyle to check Clojure code formatting
"""

import os

from megalinter import Linter


class CljstyleLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode: cljstyle only discovers
        # .cljstyle files hierarchically in the scanned tree, so one is
        # temporarily written at the workspace root when the repository has
        # none (removed after the run). Ignore entries are exact name matches
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not os.path.isfile(os.path.join(self.workspace, ".cljstyle"))
        ):
            ignore_names = " ".join(
                f'"{excluded_dir}"'
                for excluded_dir in self.get_project_exclude_directories()
            )
            self.write_workspace_generated_file(
                ".cljstyle", ["{:files {:ignore #{" + ignore_names + "}}}"]
            )

        return cmd
