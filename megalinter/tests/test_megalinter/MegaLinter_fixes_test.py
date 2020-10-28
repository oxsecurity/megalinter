#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest

from megalinter.tests.test_megalinter.helpers import utilstest


class MegalinterTest(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {'sub_lint_root': f'{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_fixes'})

    def apply_fixes_on_all_linters(self):
        super_linter, output = utilstest.call_super_linter({
            'APPLY_FIXES': 'all',
            'MULTI_STATUS': 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)

    def apply_fixes_on_one_linter(self):
        super_linter, output = utilstest.call_super_linter({
            'APPLY_FIXES': 'JAVASCRIPT_ES',
            'MULTI_STATUS': 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
