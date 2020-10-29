#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import logging
import os
import unittest

from git import Repo

from megalinter.tests.test_megalinter.helpers import utilstest

REPO_HOME = '/tmp/lint' if os.path.exists('/tmp/lint') else os.path.dirname(
    os.path.abspath(__file__)) + os.path.sep + '..' + os.path.sep + '..' + os.path.sep + '..'


class MegalinterFixesTest(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {'sub_lint_root': f'{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_fixes'})

    def test_apply_fixes_on_all_linters(self):
        super_linter, output = utilstest.call_super_linter({
            'APPLY_FIXES': 'all',
            'MULTI_STATUS': 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        repo = Repo(REPO_HOME)
        changed_files = [item.a_path for item in repo.index.diff(None)]
        logging.info('Updated files:\n'+"\n".join(changed_files))
        self.assertTrue(len(changed_files) > 0)

    def test_apply_fixes_on_one_linter(self):
        super_linter, output = utilstest.call_super_linter({
            'APPLY_FIXES': 'JAVASCRIPT_ES',
            'MULTI_STATUS': 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        repo = Repo(REPO_HOME)
        changed_files = [item.a_path for item in repo.index.diff(None)]
        logging.info('Updated files:\n'+"\n".join(changed_files))
