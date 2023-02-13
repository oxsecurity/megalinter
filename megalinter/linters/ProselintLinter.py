#!/usr/bin/env python3
"""
Use Proselint to check spell in files
https://github.com/amperser/proselint
"""
from megalinter import config, Linter


class ProselintLinter(Linter):
    def pre_test(self):
        config.set_value("SPELL_PROSELINT_FILE_EXTENSIONS", [".js", ".md"])
