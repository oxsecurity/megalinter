#!/usr/bin/env python3
"""
Use Vale to check spell in files
https://github.com/errata-ai/vale
"""

from megalinter import Linter, config


class ValeLinter(Linter):
    def pre_test(self):
        config.set_value(self.request_id, "SPELL_VALE_FILE_EXTENSIONS", [".js", ".md"])
