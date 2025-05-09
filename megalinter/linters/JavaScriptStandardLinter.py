#!/usr/bin/env python3
"""
Use Standard to lint js files
https://github.com/standard/standard
"""
from megalinter import Linter, utilstest


class JavaScriptStandardLinter(Linter):
    def pre_test(self, test_name):
        utilstest.write_eslintignore()

    def post_test(self, test_name):
        utilstest.delete_eslintignore()
