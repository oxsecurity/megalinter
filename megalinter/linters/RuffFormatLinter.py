#!/usr/bin/env python3
"""
Use Ruff to  to format python files
https://github.com/astral-sh/ruff
"""

from megalinter import Linter, config


class RuffFormatLinter(Linter):
    def pre_test(self):
        config.set_value(self.request_id, "PYTHON_DEFAULT_STYLE", "ruff")
