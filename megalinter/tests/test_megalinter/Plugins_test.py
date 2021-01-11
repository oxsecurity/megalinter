#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest

from megalinter.tests.test_megalinter.helpers import utilstest


class PluginsTest(unittest.TestCase):
    def setUp(self):
        utilstest.linter_test_setup(
            {
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}mega-linter-plugin-test"
            }
        )

    def test_load_plugin_success(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "PLUGINS": "https://raw.githubusercontent.com/nvuillam/mega-linter/"
                "master/.automation/test/mega-linter-plugin-test/test.megalinter-descriptor.yml",
                "LOG_LEVEL": "DEBUG",
                "MULTI_STATUS": "false",
                "GITHUB_COMMENT_REPORTER": "false",
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("### Processing [TEST] files", output)
        self.assertIn("[Plugins] Loaded plugin descriptor", output)
        self.assertIn("[Plugins] Successful initialization of TEST", output)

    def test_load_plugin_http_error(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": "https://raw.githubus3ent.com/nvuillam/mega-linter/"
                    "plugins/.automation/test/mega-linter-plugin-test/test.not.here.megalinter-descriptor.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                }
            )
        except Exception as e:
            self.assertIn("[Plugins] Unable to load plugin", str(e))

    def test_load_plugin_host_url_error_1(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": "https://raw.githubusercontent.com/nvuillam/mega-linter/"
                    "plugins/.automation/test/some_folder_name/test.megalinter-descriptor.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                }
            )
        except Exception as e:
            self.assertIn(
                "[Plugins] Plugin descriptor file must be hosted in"
                " a directory containing /mega-linter-plugin-",
                str(e),
            )

    def test_load_plugin_file_name_error(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": "https://raw.githubusercontent.com/nvuillam/mega-linter/"
                    "plugins/.automation/test/mega-linter-plugin-test/test.megalinter-wrong.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                }
            )
        except Exception as e:
            self.assertIn(
                "[Plugins] Plugin descriptor file must end with .megalinter-descriptor.yml",
                str(e),
            )

    def test_load_plugin_format_error_2(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": "hello",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                }
            )
        except Exception as e:
            self.assertIn("[Plugins] Plugin descriptors must follow the format", str(e))
