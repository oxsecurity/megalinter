#!/usr/bin/env python3
"""
Use cljstyle to check Clojure code formatting
"""

import os

from megalinter import Linter


class CljstyleLinter(Linter):
    # Forward excluded directories: cljstyle only discovers .cljstyle files
    # hierarchically in the scanned tree, so one is temporarily written at the
    # workspace root when the repository has none (removed after the run).
    # Ignore entries are exact name matches
    def manage_excluded_directories_config(self, cmd):
        if not os.path.isfile(os.path.join(self.workspace, ".cljstyle")):
            ignore_names = " ".join(
                f'"{excluded_dir}"'
                for excluded_dir in self.get_project_exclude_directories()
            )
            self.write_workspace_generated_file(
                ".cljstyle", ["{:files {:ignore #{" + ignore_names + "}}}"]
            )
        return cmd
