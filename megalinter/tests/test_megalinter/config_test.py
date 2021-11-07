#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest

from megalinter import config
from megalinter.constants import ML_REPO


class config_test(unittest.TestCase):
    test_folder = (
        f"https://raw.githubusercontent.com/{ML_REPO}/"
        "main/.automation/test/mega-linter-config-test/"
    )

    def setUp(self):
        for key in [
            "MEGALINTER_CONFIG",
            "EXTENDS",
            "FILTER_REGEX_INCLUDE",
            "FILTER_REGEX_EXCLUDE",
            "SHOW_ELAPSED_TIME",
        ]:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        config.delete()

    def test_remote_config_success(self):
        remote_config = self.test_folder + "custom.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = remote_config
        config.init_config()
        self.assertEqual("(custom)", config.get("FILTER_REGEX_INCLUDE"))

    def test_remote_config_error(self):
        remote_config = self.test_folder + "custom.mega-linter-not-existing.yml"
        try:
            os.environ["MEGALINTER_CONFIG"] = remote_config
            config.init_config()
        except Exception as e:
            self.assertIn("http", str(e))

    def test_remote_config_extends_success(self):
        remote_config = self.test_folder + "base.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = remote_config
        config.init_config()
        self.assertEqual("(extension1)", config.get("FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get("FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get("SHOW_ELAPSED_TIME"))

    def test_remote_config_extends_success_2(self):
        remote_config = self.test_folder + "base2.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = remote_config
        config.init_config()
        self.assertEqual("(base)", config.get("FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get("FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get("SHOW_ELAPSED_TIME"))

    def test_remote_config_extends_error(self):
        remote_config = self.test_folder + "base-error.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = remote_config
        try:
            os.environ["MEGALINTER_CONFIG"] = remote_config
            config.init_config()
        except Exception as e:
            self.assertIn("http", str(e))
