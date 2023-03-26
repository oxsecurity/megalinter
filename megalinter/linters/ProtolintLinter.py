#!/usr/bin/env python3
"""
Use Protolint to analyze protobuf files
"""

from megalinter import Linter


class ProtolintLinter(Linter):
    def process_linter(self, file=None):
        return_code, return_output = super().process_linter(file)

        # Although it fixes the errors, it returns exit code 1 instead of 0
        if self.apply_fixes is True and return_code == 1:
            return_code = 0

        return return_code, return_output
