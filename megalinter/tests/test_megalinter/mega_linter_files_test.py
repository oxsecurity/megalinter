#!/usr/bin/env python3
"""Tests for MegaLinter file listing helpers."""

import os
import tempfile
import unittest
from unittest.mock import patch

from megalinter.MegaLinter import Megalinter


class MegaLinterFilesTest(unittest.TestCase):
    def test_list_files_all_skips_excluded_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Root file should always be listed
            with open(os.path.join(tmp_dir, "root.txt"), "w", encoding="utf-8"):
                pass

            # Excluded top-level directory
            os.makedirs(os.path.join(tmp_dir, "excluded"), exist_ok=True)
            with open(
                os.path.join(tmp_dir, "excluded", "should_skip.txt"),
                "w",
                encoding="utf-8",
            ):
                pass

            # Allowed directory with nested excluded child
            os.makedirs(os.path.join(tmp_dir, "keep", "nested_excluded"), exist_ok=True)
            with open(os.path.join(tmp_dir, "keep", "keep.txt"), "w", encoding="utf-8"):
                pass
            with open(
                os.path.join(tmp_dir, "keep", "nested_excluded", "skip_me.txt"),
                "w",
                encoding="utf-8",
            ):
                pass

            excluded = {"excluded", "keep/nested_excluded"}

            ml = Megalinter.__new__(Megalinter)
            ml.workspace = tmp_dir
            ml.request_id = "test"

            with patch(
                "megalinter.utils.get_excluded_directories", return_value=excluded
            ):
                files = ml.list_files_all()

            self.assertIn("root.txt", files)
            self.assertIn("keep/keep.txt", files)
            self.assertNotIn("excluded/should_skip.txt", files)
            self.assertNotIn("keep/nested_excluded/skip_me.txt", files)

    def test_list_files_all_skips_absolute_excluded_directory_inside_workspace(self):
        # Regression test for issue #7845: an absolute path inside the
        # workspace (e.g. REPORT_OUTPUT_FOLDER=/tmp/lint/megalinter-reports)
        # must be pruned from os.walk() the same as a relative entry.
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, "root.txt"), "w", encoding="utf-8"):
                pass

            report_dir = os.path.join(tmp_dir, "megalinter-reports")
            os.makedirs(os.path.join(report_dir, "updated_sources"), exist_ok=True)
            with open(
                os.path.join(report_dir, "updated_sources", "test.sh"),
                "w",
                encoding="utf-8",
            ):
                pass

            excluded = {report_dir}

            ml = Megalinter.__new__(Megalinter)
            ml.workspace = tmp_dir
            ml.request_id = "test"

            with patch(
                "megalinter.utils.get_excluded_directories", return_value=excluded
            ):
                files = ml.list_files_all()

            self.assertIn("root.txt", files)
            self.assertNotIn(
                "megalinter-reports/updated_sources/test.sh",
                [f.replace(os.sep, "/") for f in files],
            )


if __name__ == "__main__":
    unittest.main()
