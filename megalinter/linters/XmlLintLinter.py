#!/usr/bin/env python3
"""
Use XmlLint to lint xml files
http://xmlsoft.org/xmllint.html
"""
import os

from megalinter import Linter, config


class XmlLintLinter(Linter):
    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        if (
            self.apply_fixes is True
            and self.cli_lint_fix_arg_name is not None
            and config.get("XML_XMLLINT_AUTOFORMAT", "false") == "true"
        ):
            if self.cli_lint_mode == "file":
                os.environ["XMLLINT_INDENT"] = config.get("XML_XMLLINT_INDENT", "  ")

                cmd += ["--output", f"{file}"]
            else:
                raise KeyError(
                    f"You can not apply_fixes with cli_lint_mode {self.cli_lint_mode}"
                )
        return cmd
