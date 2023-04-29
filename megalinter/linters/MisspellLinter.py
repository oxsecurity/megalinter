#!/usr/bin/env python3
"""
Use Misspell to fix commonly misspelled English words
https://github.com/client9/misspell
"""
from megalinter import Linter, config


class MisspellLinter(Linter):
    def pre_test(self):
        config.set_value(
            self.master.request_id, "SPELL_MISSPELL_FILE_EXTENSIONS", [".js", ".md"]
        )
