#!/usr/bin/env python3
"""
Use Misspell to fix ommonly misspelled English words
https://github.com/client9/misspell
"""
from megalinter import config, Linter


class MisspellLinter(Linter):
    def pre_test(self):
        config.set_value("SPELL_MISSPELL_FILE_EXTENSIONS", [".js", ".md"])
