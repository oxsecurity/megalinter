#!/usr/bin/env python3
"""
Use Standard to lint js files
https://github.com/standard/ts-standard
"""
from megalinter import Linter, utilstest


class TypeScriptStandardLinter(Linter):
    def pre_test(self):
        utilstest.write_eslintignore()

    def post_test(self):
        utilstest.delete_eslintignore()
