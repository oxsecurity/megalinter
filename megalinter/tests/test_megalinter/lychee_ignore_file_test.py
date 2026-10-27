#!/usr/bin/env python3
"""
Unit tests for the forwarding of .lycheeignore files found outside the workspace root
"""

import os
import tempfile
import unittest

from megalinter.linters.LycheeLinter import LycheeLinter


class lychee_ignore_file_test(unittest.TestCase):
    def build_linter(self, workspace, ignore_file):
        linter = LycheeLinter.__new__(LycheeLinter)
        linter.workspace = workspace
        linter.ignore_file = ignore_file
        return linter

    def write_file(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

    def test_rules_path_ignore_file_is_forwarded_as_exclude(self):
        with tempfile.TemporaryDirectory() as workspace:
            ignore_file = os.path.join(workspace, ".github", "linters", ".lycheeignore")
            self.write_file(
                ignore_file,
                "# comment\n\n^https://example\\.invalid/\n  (.*some_url_part)  \n",
            )
            linter = self.build_linter(workspace, ignore_file)
            self.assertEqual(
                linter.build_ignore_file_exclude_arguments(),
                [
                    "--exclude=^https://example\\.invalid/",
                    "--exclude=(.*some_url_part)",
                ],
            )

    def test_workspace_root_ignore_file_is_not_forwarded(self):
        with tempfile.TemporaryDirectory() as workspace:
            ignore_file = os.path.join(workspace, ".lycheeignore")
            self.write_file(ignore_file, "^https://example\\.invalid/\n")
            linter = self.build_linter(workspace, ignore_file)
            self.assertEqual(linter.build_ignore_file_exclude_arguments(), [])

    def test_no_ignore_file_is_not_forwarded(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_linter(workspace, None)
            self.assertEqual(linter.build_ignore_file_exclude_arguments(), [])
