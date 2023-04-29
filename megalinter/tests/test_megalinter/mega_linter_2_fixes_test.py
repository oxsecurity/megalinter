#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import os
import unittest
import uuid

from megalinter import utilstest


class mega_linter_2_fixes_test(unittest.TestCase):
    def __init__(self) -> None:
        self.request_id = str(uuid.uuid1())

    def setUp(self):
        utilstest.linter_test_setup(
            {
                "request_id": self.request_id,
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project_fixes",
            }
        )
