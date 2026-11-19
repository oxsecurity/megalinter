#!/usr/bin/env python3
"""
Use Psalm to analyze PHP files
"""

from megalinter import Linter


class PsalmLinter(Linter):
    # Since Psalm 7 runs the security analysis by default, it exits with 0 even
    # when it found errors if it writes a report (--report) while the
    # GITHUB_WORKFLOW variable is set (GitHub Actions friendly behavior).
    # MegaLinter needs the real exit code to report the errors, so Psalm does
    # not see the variable
    def execute_lint_command(self, command):
        subprocess_env = getattr(self, "_cached_subprocess_env", None)
        if subprocess_env is not None:
            subprocess_env.pop("GITHUB_WORKFLOW", None)
        return super().execute_lint_command(command)
