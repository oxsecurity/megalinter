#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import time
import unittest

from megalinter.tests.test_megalinter.helpers import utilstest


class MegalinterFixesTest(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_fixes"
            }
        )

    def test_1_apply_fixes_on_one_linter(self):
        super_linter, output = utilstest.call_super_linter(
            {
                "APPLY_FIXES": "JAVASCRIPT_STANDARD",
                "LOG_LEVEL": "DEBUG",
                "MULTI_STATUS": "false",
            }
        )
        self.assertTrue(
            len(super_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("Linting [JAVASCRIPT] files", output)
        time.sleep(5)
        utilstest.assert_file_has_been_updated("javascript_for_fixes_1.js", True, self)
        utilstest.assert_file_has_been_updated("env_for_fixes_1.env", False, self)

    def test_2_apply_fixes_on_all_linters(self):
        super_linter, output = utilstest.call_super_linter(
            {"APPLY_FIXES": "all", "LOG_LEVEL": "DEBUG", "MULTI_STATUS": "false"}
        )
        self.assertTrue(
            len(super_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("Linting [JAVASCRIPT] files", output)
        time.sleep(5)
        # Markdown lint fix
        utilstest.assert_file_has_been_updated("markdown_for_fixes_1.md", True, self)
        # eslint fix
        utilstest.assert_file_has_been_updated("javascript_for_fixes_1.js", True, self)
        # dotenv-linter fix
        utilstest.assert_file_has_been_updated("env_for_fixes_1.env", True, self)
        # ktlint fix (format)
        utilstest.assert_file_has_been_updated("kotlin_for_fixes_1.kt", True, self)
        # rubocop fix
        utilstest.assert_file_has_been_updated("ruby_for_fixes_1.rb", True, self)
        # black fix
        utilstest.assert_file_has_been_updated("python_for_fixes_1.py", True, self)
        # dotnet linter VB .NET fix
        utilstest.assert_file_has_been_updated("vbdotnet_for_fixes_1.vb", True, self)
        # dotnet linter C# fix
        utilstest.assert_file_has_been_updated("csharp_for_fixes_1.cs", True, self)
        # npm-groovy-lint fix
        utilstest.assert_file_has_been_updated("groovy_for_fixes_1.groovy", True, self)
