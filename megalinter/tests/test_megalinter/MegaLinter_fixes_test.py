#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import logging
import os
import unittest

from git import Repo

from megalinter.tests.test_megalinter.helpers import utilstest


class MegalinterFixesTest(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {'sub_lint_root': f'{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_fixes'})

    def test_apply_fixes_on_all_linters(self):
        utilstest.git_reset_updates()
        super_linter, output = utilstest.call_super_linter({
            'APPLY_FIXES': 'all',
            'MULTI_STATUS': 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        utilstest.assert_file_has_been_updated('groovy_for_fixes_1.groovy', True, self)
        utilstest.assert_file_has_been_updated('javascript_for_fixes_1.groovy', True, self)

    def test_apply_fixes_on_one_linter(self):
        utilstest.git_reset_updates()
        super_linter, output = utilstest.call_super_linter({
            'APPLY_FIXES': 'JAVASCRIPT_ES',
            'MULTI_STATUS': 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        utilstest.assert_file_has_been_updated('groovy_for_fixes_1.groovy', True, self)
        utilstest.assert_file_has_been_updated('javascript_for_fixes_1.groovy', False, self)

