#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest

import megalinter
from megalinter.tests.test_megalinter.helpers import utilstest


class MegalinterTest(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {'sub_lint_root': f'{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project'})

    def test_logging_level_info(self):
        super_linter, output = utilstest.call_super_linter(
            {"LOG_LEVEL": 'INFO'})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn("[INFO]", output)
        self.assertNotIn("[DEBUG]", output)

    def test_logging_level_debug(self):
        super_linter, output = utilstest.call_super_linter(
            {"LOG_LEVEL": 'DEBUG'})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn("[INFO]", output)
        self.assertIn("[DEBUG]", output)

    def test_disable_language(self):
        super_linter, output = utilstest.call_super_linter(
            {"DISABLE": 'GROOVY'})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        utilstest.assert_is_skipped('GROOVY', output, self)

    def test_disable_language_legacy(self):
        super_linter, output = utilstest.call_super_linter(
            {"VALIDATE_GROOVY": 'false'})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        utilstest.assert_is_skipped('GROOVY', output, self)

    def test_disable_linter(self):
        super_linter, output = utilstest.call_super_linter(
            {"DISABLE_LINTERS": "JAVASCRIPT_ES"})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        utilstest.assert_is_skipped('JAVASCRIPT_ES', output, self)
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('Using [standard', output)

    def test_disable_linter_legacy(self):
        super_linter, output = utilstest.call_super_linter(
            {"VALIDATE_JAVASCRIPT_ES": 'false'})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        utilstest.assert_is_skipped('JAVASCRIPT_ES', output, self)
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('Using [standard', output)

    def test_enable_only_one_linter(self):
        super_linter, output = utilstest.call_super_linter(
            {"ENABLE_LINTERS": "JAVASCRIPT_ES"})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('Using [eslint', output)
        utilstest.assert_is_skipped('JAVASCRIPT_STANDARD', output, self)
        utilstest.assert_is_skipped('GROOVY', output, self)

    def test_enable_only_one_linter_legacy(self):
        super_linter, output = utilstest.call_super_linter(
            {"VALIDATE_JAVASCRIPT_ES": 'true'})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('Using [eslint', output)
        utilstest.assert_is_skipped('JAVASCRIPT_STANDARD', output, self)
        utilstest.assert_is_skipped('GROOVY', output, self)

    def test_enable_only_one_language(self):
        super_linter, output = utilstest.call_super_linter(
            {"ENABLE": "JAVASCRIPT"})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('Using [eslint', output)
        self.assertIn('Using [standard', output)
        utilstest.assert_is_skipped('GROOVY', output, self)

    def test_enable_only_one_language_legacy(self):
        super_linter, output = utilstest.call_super_linter(
            {"VALIDATE_JAVASCRIPT": 'true'})
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('Using [eslint', output)
        self.assertIn('Using [standard', output)
        utilstest.assert_is_skipped('GROOVY', output, self)

    def test_validate_all_code_base_false(self):
        os.environ["GITHUB_WORKSPACE"] = '/tmp/lint' if os.path.exists('/tmp/lint') else os.path.relpath(
            os.path.relpath(os.path.dirname(
                os.path.abspath(__file__))) + '/../../..')
        super_linter, output = utilstest.call_super_linter({
            'ENABLE_LINTERS': 'PYTHON_PYLINT',
            "VALIDATE_ALL_CODEBASE": 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")

    def test_override_linter_rules_path(self):
        super_linter, output = utilstest.call_super_linter({
            'ENABLE_LINTERS': 'JAVASCRIPT_ES',
            'LINTER_RULES_PATH': '.',
            "JAVASCRIPT_ES_FILE_NAME": '.eslintrc-custom.yml',
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('Using [eslint', output)
        self.assertIn('.eslintrc-custom.yml', output)

    def test_custom_config_on_language(self):
        super_linter, output = utilstest.call_super_linter({
            'ENABLE_LINTERS': 'JAVASCRIPT_ES',
            'JAVASCRIPT_LINTER_RULES_PATH': '.',
            "JAVASCRIPT_FILE_NAME": '.eslintrc-custom.yml',
            "JAVASCRIPT_FILTER_REGEX_INCLUDE": '(.*_good_.*|.*\\/good\\/.*)',
            "JAVASCRIPT_FILTER_REGEX_EXCLUDE": '(.*_bad_.*|.*\\/bad\\/.*)'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('.eslintrc-custom.yml', output)

    def test_general_include_exclude(self):
        super_linter, output = utilstest.call_super_linter({
            'ENABLE_LINTERS': 'JAVASCRIPT_ES',
            "FILTER_REGEX_INCLUDE": '(.*_good_.*|.*\\/good\\/.*)',
            "FILTER_REGEX_EXCLUDE": '(.*_bad_.*|.*\\/bad\\/.*)'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)

    def test_custom_config_on_linter(self):
        super_linter, output = utilstest.call_super_linter({
            'ENABLE_LINTERS': 'JAVASCRIPT_ES',
            'JAVASCRIPT_ES_LINTER_RULES_PATH': '.',
            "JAVASCRIPT_ES_FILE_NAME": '.eslintrc-custom.yml',
            "JAVASCRIPT_FILTER_REGEX_INCLUDE": '(.*_good_.*|.*\\/good\\/.*)',
            "JAVASCRIPT_FILTER_REGEX_EXCLUDE": '(.*_bad_.*|.*\\/bad\\/.*)',
            'MULTI_STATUS': 'false'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)

    def test_user_arguments_on_linter(self):
        super_linter, output = utilstest.call_super_linter({
            'ENABLE_LINTERS': 'JAVASCRIPT_ES',
            "JAVASCRIPT_ES_FILTER_REGEX_INCLUDE": '(.*_good_.*|.*\\/good\\/.*)',
            "JAVASCRIPT_ES_FILTER_REGEX_EXCLUDE": '(.*_bad_.*|.*\\/bad\\/.*)',
            "JAVASCRIPT_ES_ARGUMENTS": '--debug --env-info',
            'MULTI_STATUS': 'false',
            "LOG_LEVEL": 'DEBUG'
        })
        self.assertTrue(len(super_linter.linters) > 0,
                        "Linters have been created and run")
        self.assertIn('Linting [JAVASCRIPT] files', output)
        self.assertIn('--debug --env-info', output)

    def test_alpaca(self):
        res = megalinter.alpaca()
        self.assertTrue(res is True)
