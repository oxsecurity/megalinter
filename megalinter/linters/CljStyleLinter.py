#!/usr/bin/env python3
"""
Use cljstyle to check the formatting of Clojure files
SARIF is built from the diff printed for each file to format
https://github.com/greglook/cljstyle
"""

from megalinter import Linter
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    sarif_from_results,
    unified_diff_to_results,
)


class CljStyleLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return cljstyle_diff_to_sarif(return_stdout, self.workspace)


# cljstyle has no rule or position: one result per file, at its first modified hunk
def cljstyle_diff_to_sarif(stdout, workspace=None):
    return sarif_from_results(
        "cljstyle",
        unified_diff_to_results(
            stdout,
            workspace,
            LEVEL_ERROR,
            "The file is not formatted as cljstyle expects",
            "cljstyle",
        ),
        "https://github.com/greglook/cljstyle",
    )
