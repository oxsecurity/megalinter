#!/usr/bin/env python3
"""
Use v8r to lint json files
"""

from megalinter import Linter


class V8rLinter(Linter):
    def build_lint_command(self, file=None) -> list:
        if self.cli_lint_mode == "project":
            self.cli_lint_extra_args_after.append(
                f"**/*{self.file_extensions[0]}" if len(self.file_extensions) == 1 else f"**/*.{{{self.file_extensions.join(",").replace(".", "")}}}"
            )

        return super().build_lint_command(file)
