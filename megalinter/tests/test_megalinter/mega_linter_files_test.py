#!/usr/bin/env python3
"""Tests for MegaLinter file listing helpers."""

import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import git
from megalinter import config
from megalinter.MegaLinter import GIT_LS_FILES_TIMEOUT_SECONDS, Megalinter


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

    def test_list_git_ignored_files_collapses_fully_ignored_directories(self):
        # Regression test: a fully-ignored directory (e.g. node_modules) must
        # be reported as a single collapsed entry ("dirname/**"), not as one
        # entry per file. Without `--directory`, git ls-files enumerates every
        # individual file under a large ignored tree, which is what made
        # list_git_ignored_files pathologically slow on real-world repos.
        with tempfile.TemporaryDirectory() as tmp_dir:
            run = lambda *args: subprocess.run(  # noqa: E731
                ["git", *args], cwd=tmp_dir, check=True, capture_output=True
            )
            run("init", "-q")
            run("config", "user.email", "test@example.com")
            run("config", "user.name", "Test")

            with open(os.path.join(tmp_dir, ".gitignore"), "w", encoding="utf-8") as f:
                f.write("node_modules/\nbuild/only_ignored.log\n")

            # Fully-ignored directory: no tracked file anywhere inside it.
            modules_dir = os.path.join(tmp_dir, "node_modules", "pkg")
            os.makedirs(modules_dir, exist_ok=True)
            for i in range(20):
                with open(
                    os.path.join(modules_dir, f"file{i}.js"), "w", encoding="utf-8"
                ):
                    pass

            # Partially-ignored directory: one tracked file, one ignored file.
            build_dir = os.path.join(tmp_dir, "build")
            os.makedirs(build_dir, exist_ok=True)
            with open(os.path.join(build_dir, "keep.txt"), "w", encoding="utf-8"):
                pass
            with open(
                os.path.join(build_dir, "only_ignored.log"), "w", encoding="utf-8"
            ):
                pass

            with open(os.path.join(tmp_dir, "README.md"), "w", encoding="utf-8"):
                pass

            run("add", "README.md", ".gitignore", "build/keep.txt")
            run("commit", "-q", "-m", "init")

            ml = Megalinter.__new__(Megalinter)
            ml.workspace = tmp_dir
            ml.github_workspace = tmp_dir
            ml.request_id = "test"

            config.set_config(ml.request_id, {})
            self.addCleanup(config.delete, ml.request_id)

            with patch("megalinter.utils.get_excluded_directories", return_value=set()):
                ignored_files = ml.list_git_ignored_files()

            # Collapsed into a single directory entry, not one per file.
            self.assertIn("node_modules/**", ignored_files)
            self.assertNotIn("node_modules/pkg/file0.js", ignored_files)

            # A directory that is only partially ignored keeps listing its
            # individual ignored files instead of being collapsed.
            self.assertIn("build/only_ignored.log", ignored_files)
            self.assertNotIn("build/**", ignored_files)
            self.assertNotIn("build/keep.txt", ignored_files)

    def test_list_git_ignored_files_timeout_raises_actionable_error(self):
        # Regression test: the git ls-files call is bounded by kill_after_timeout
        # because it can stall indefinitely on I/O when the workspace is
        # bind-mounted from Windows into a WSL2-backed container. When GitPython
        # kills the stalled process it raises GitCommandError with
        # "did not complete in N secs." in stderr; list_git_ignored_files must
        # convert it into an actionable RuntimeError. The caller in run()
        # catches any Exception and degrades to an empty ignored files list, so
        # raising (instead of returning partial output) is the safe behavior.
        timeout_err = git.GitCommandError(
            ["git", "ls-files"],
            -9,
            'Timeout: the command "git ls-files" did not complete in 120 secs.',
        )
        mock_repo = MagicMock()
        mock_repo.git.execute.side_effect = timeout_err

        ml = Megalinter.__new__(Megalinter)
        ml.workspace = "."
        ml.github_workspace = "."
        ml.request_id = "test"

        with (
            patch("megalinter.MegaLinter.git.Repo", return_value=mock_repo),
            patch("megalinter.utils.get_excluded_directories", return_value=set()),
        ):
            with self.assertRaises(RuntimeError) as raised:
                ml.list_git_ignored_files()

        message = str(raised.exception)
        self.assertIn(str(GIT_LS_FILES_TIMEOUT_SECONDS), message)
        self.assertIn("WSL2", message)
        self.assertIn("ADDITIONAL_EXCLUDED_DIRECTORIES", message)

    def test_list_git_ignored_files_non_timeout_git_error_is_reraised(self):
        # A GitCommandError unrelated to the timeout must keep its original
        # type so existing handling (and error messages) stay unchanged.
        other_err = git.GitCommandError(["git", "ls-files"], 128, "fatal: boom")
        mock_repo = MagicMock()
        mock_repo.git.execute.side_effect = other_err

        ml = Megalinter.__new__(Megalinter)
        ml.workspace = "."
        ml.github_workspace = "."
        ml.request_id = "test"

        with (
            patch("megalinter.MegaLinter.git.Repo", return_value=mock_repo),
            patch("megalinter.utils.get_excluded_directories", return_value=set()),
        ):
            with self.assertRaises(git.GitCommandError):
                ml.list_git_ignored_files()

    def test_list_git_ignored_files_passes_timeout_on_non_windows(self):
        # On non-Windows platforms (i.e. inside the MegaLinter Docker images),
        # the git ls-files call must be invoked with kill_after_timeout so it
        # cannot hang forever. On Windows, GitPython does not support
        # kill_after_timeout, so the kwarg must be omitted there.
        mock_repo = MagicMock()
        mock_repo.git.execute.return_value = ""

        ml = Megalinter.__new__(Megalinter)
        ml.workspace = "."
        ml.github_workspace = "."
        ml.request_id = "test"

        with (
            patch("megalinter.MegaLinter.git.Repo", return_value=mock_repo),
            patch("megalinter.utils.get_excluded_directories", return_value=set()),
            patch("megalinter.MegaLinter.sys.platform", "linux"),
        ):
            ml.list_git_ignored_files()

        kwargs = mock_repo.git.execute.call_args.kwargs
        self.assertEqual(kwargs.get("kill_after_timeout"), GIT_LS_FILES_TIMEOUT_SECONDS)

        mock_repo.git.execute.reset_mock()
        with (
            patch("megalinter.MegaLinter.git.Repo", return_value=mock_repo),
            patch("megalinter.utils.get_excluded_directories", return_value=set()),
            patch("megalinter.MegaLinter.sys.platform", "win32"),
        ):
            ml.list_git_ignored_files()

        kwargs = mock_repo.git.execute.call_args.kwargs
        self.assertNotIn("kill_after_timeout", kwargs)


if __name__ == "__main__":
    unittest.main()
