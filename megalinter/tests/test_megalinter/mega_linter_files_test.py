#!/usr/bin/env python3
"""Tests for MegaLinter file listing helpers."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from megalinter import config
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

            # "excluded_backup" shares a prefix with the excluded "excluded"
            # directory but is a distinct name; it must be kept. Guards against
            # regressing exact-segment matching into prefix/substring matching.
            os.makedirs(os.path.join(tmp_dir, "excluded_backup"), exist_ok=True)
            with open(
                os.path.join(tmp_dir, "excluded_backup", "keep.txt"),
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
            self.assertIn("excluded_backup/keep.txt", files)
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

    def test_list_files_git_diff_skips_excluded_directories(self):
        # Regression test for issue #8360: files inside excluded directories
        # must be pruned in changed-files mode (VALIDATE_ALL_CODEBASE=false),
        # the same way they are in full-codebase mode (list_files_all).
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Files referenced by the mocked git diff must exist on disk
            # because list_files_git_diff() keeps only real, non-symlink files.
            for rel_path in [
                "README.md",
                "src/app.py",
                "excluded_backup/keep.py",
                "excluded/skip.py",
                "pkg/excluded/deep.py",
                "keep/nested_excluded/skip.py",
            ]:
                abs_path = os.path.join(tmp_dir, rel_path)
                os.makedirs(os.path.dirname(abs_path) or tmp_dir, exist_ok=True)
                with open(abs_path, "w", encoding="utf-8"):
                    pass

            # "excluded" matches by basename at any nesting level;
            # "keep/nested_excluded" matches by workspace-relative path.
            excluded = {"excluded", "keep/nested_excluded"}
            diff_output = (
                "README.md\n"
                "src/app.py\n"
                "excluded_backup/keep.py\n"
                "excluded/skip.py\n"
                "pkg/excluded/deep.py\n"
                "keep/nested_excluded/skip.py\n"
            )

            ml = Megalinter.__new__(Megalinter)
            ml.workspace = tmp_dir
            ml.github_workspace = tmp_dir
            ml.request_id = "test"
            ml.has_git_extraheader = False

            config.set_config(ml.request_id, {})
            self.addCleanup(config.delete, ml.request_id)

            head_ref = MagicMock()
            head_ref.name = "origin/HEAD"
            mock_repo = MagicMock()
            mock_repo.refs = [head_ref]
            mock_repo.git.diff.return_value = diff_output

            with (
                patch("megalinter.MegaLinter.git.Repo", return_value=mock_repo),
                patch(
                    "megalinter.utils.get_excluded_directories", return_value=excluded
                ),
            ):
                files = ml.list_files_git_diff()

            # Root-level file has no ancestor directory, so it is never excluded
            self.assertIn("README.md", files)
            self.assertIn("src/app.py", files)
            # Prefix of an excluded name must not be pruned (exact-segment match)
            self.assertIn("excluded_backup/keep.py", files)
            self.assertNotIn("excluded/skip.py", files)
            self.assertNotIn("pkg/excluded/deep.py", files)
            self.assertNotIn("keep/nested_excluded/skip.py", files)


if __name__ == "__main__":
    unittest.main()
