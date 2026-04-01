#!/usr/bin/env python3
"""
Use zizmor to lint GitHub Actions files
https://zizmor.sh/
"""

import logging

import megalinter
from megalinter import config


class ZizmorLinter(megalinter.Linter):
    def pre_test(self, test_name):
        config.set_value(
            self.request_id, "ACTION_ZIZMOR_UNSECURED_ENV_VARIABLES", "GITHUB_TOKEN"
        )
