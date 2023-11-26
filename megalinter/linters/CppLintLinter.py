#!/usr/bin/env python3
"""
Class for cpplint
"""

import pathlib

from megalinter import Linter


class CppLintLinter(Linter):
    def build_lint_command(self, file=None):
        # Dynamically add the list of extensions from list of files
        if (
            self.cli_lint_mode == "list_of_files"
            and self.files is not None
            and len(self.files) > 0
        ):
            extensions = []
            for file_to_lint in self.files:
                extension = pathlib.Path(file_to_lint).suffix.replace(".", "")
                if extension not in extensions:
                    extensions += [extension]
            self.cli_lint_extra_args += ["--extensions=" + ",".join(extensions)]
        cmd = super().build_lint_command(file)
        return cmd
