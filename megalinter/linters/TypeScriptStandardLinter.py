#!/usr/bin/env python3
"""
Use Standard to lint js files
https://github.com/standard/standard
"""
import os

from megalinter import Linter


class TypeScriptStandardLinter(Linter):
    def pre_test(self):
        # The file must be in the root of the repository so we create it temporarily for the test.
        # By default eslint ignores files starting with "." so we override this behavior
        # to work with the .automation folder
        with open(
            os.path.join(os.getcwd(), ".eslintignore"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write("!.automation")

    def post_test(self):
        os.remove(os.path.join(os.getcwd(), ".eslintignore"))
