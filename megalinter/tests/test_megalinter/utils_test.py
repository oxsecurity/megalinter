#!/usr/bin/env python3
"""
Unit tests for utils class

"""

import os
import re
import subprocess
import tempfile
import unittest
import uuid
import warnings
from unittest.mock import MagicMock, patch

import git
from megalinter import config
from megalinter.logger import fetch_betterleaks_regexes, sanitize_string
from megalinter.utils import (
    fix_regex_pattern,
    get_excluded_directories,
    list_updated_files,
)


class utils_test(unittest.TestCase):
    def test_report_folder_excluded_even_when_excluded_directories_overridden(self):
        # MegaLinter writes its reports there while linters run, so analyzing it
        # makes project-mode linters fail on files created or deleted mid-run
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            None,
            {
                "EXCLUDED_DIRECTORIES": "custom_dir",
                "REPORT_OUTPUT_FOLDER": "my-reports",
            },
        )
        try:
            excluded = get_excluded_directories(request_id)
        finally:
            config.delete(request_id)
        self.assertIn("my-reports", excluded)
        self.assertIn("custom_dir", excluded)
        self.assertNotIn("node_modules", excluded)

    def test_sanitize_string(self):
        input_string = "AWS Key: AKIAIOSFODNN7EXAMPLE and GitHub Token: ghp_abcdEFGHijklMNOPqrstUVWXyz1234567890"
        sanitized = sanitize_string(input_string)

        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", sanitized)
        self.assertNotIn("ghp_abcdEFGHijklMNOPqrstUVWXyz1234567890", sanitized)
        self.assertIn("HIDDEN_BY_MEGALINTER", sanitized)

        # Optional: stricter check if needed
        self.assertEqual(
            sanitized.count("HIDDEN_BY_MEGALINTER"),
            2,
            "There should be exactly 2 HIDDEN_BY_MEGALINTER in the output",
        )

    def test_fetch_betterleaks_regexes(self):
        # Test loading betterleaks regexes from the vendored ruleset
        regexes = fetch_betterleaks_regexes()
        self.assertIsInstance(regexes, list, "Regexes should be a list")
        self.assertGreater(len(regexes), 0, "Regexes list should not be empty")

    def test_fix_regex_pattern_posix_character_classes(self):
        fixed = fix_regex_pattern(r"\b(pat[[:alnum:]]{14}\.[a-f0-9]{64})\b")
        self.assertEqual(fixed, r"\b(pat[a-zA-Z0-9]{14}\.[a-f0-9]{64})\b")
        # The translated pattern must match a real Airtable personal access token
        token = "patAbCdEf01234567." + "0123456789abcdef" * 4  # betterleaks:allow
        self.assertIsNotNone(re.search(fixed, f"token: {token} used"))

    def test_betterleaks_regexes_compile_without_warnings(self):
        regexes = fetch_betterleaks_regexes()
        re.purge()  # Clear the compile cache so warnings are re-emitted
        with warnings.catch_warnings():
            warnings.simplefilter("error", FutureWarning)
            for pattern in regexes:
                re.compile(pattern)

    def test_list_updated_files_lists_modified_files(self):
        # Nominal case: a file modified after the commit is reported.
        # The git configuration is neutralized for the whole test, not only for
        # the setup commands: list_updated_files runs git in this very process,
        # so the caller's global config (a content filter bound by
        # core.attributesFile, for instance) would otherwise apply to the diff
        git_env = {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_AUTHOR_NAME": "megalinter-test",
            "GIT_AUTHOR_EMAIL": "megalinter-test@invalid",
            "GIT_COMMITTER_NAME": "megalinter-test",
            "GIT_COMMITTER_EMAIL": "megalinter-test@invalid",
        }
        with patch.dict(os.environ, git_env), tempfile.TemporaryDirectory() as tmp_dir:

            def run(*args):
                subprocess.run(
                    ["git", *args],
                    cwd=tmp_dir,
                    check=True,
                    timeout=60,
                    capture_output=True,
                )

            run("init", "-q")
            with open(os.path.join(tmp_dir, "README.md"), "w", encoding="utf-8") as f:
                f.write("initial\n")
            run("add", "README.md")
            run("commit", "-q", "-m", "init")
            with open(os.path.join(tmp_dir, "README.md"), "w", encoding="utf-8") as f:
                f.write("updated\n")

            self.assertEqual(list_updated_files(tmp_dir), ["README.md"])

    def mock_repo_with_failing_diff(self, workspace, diff_err):
        # git_dir must stay inside the workspace, otherwise list_updated_files
        # returns on the working-copy-root check before reaching the diff
        mock_repo = MagicMock()
        mock_repo.git_dir = os.path.join(workspace, ".git")
        mock_repo.index.diff.side_effect = diff_err
        return patch("megalinter.utils.git.Repo", return_value=mock_repo)

    def test_list_updated_files_git_command_error_is_not_fatal(self):
        # Regression test for issue #8649: on a read-only workspace, a required
        # git content filter (git-lfs) can not write its temporary files, so the
        # diff exits 128. Listing updated files is best effort: the failure must
        # degrade to an empty list instead of crashing the whole MegaLinter run
        # from UpdatedSourcesReporter.produce_report()
        diff_err = git.GitCommandError(
            ["git", "diff", "--abbrev=40", "--full-index", "-M", "--raw", "-z"],
            128,
            # GitPython drains stderr before raising, so git's own message
            # ("clean filter 'lfs' failed") never reaches the exception
            b"",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.mock_repo_with_failing_diff(tmp_dir, diff_err):
                with self.assertLogs(level="WARNING") as log:
                    updated_files = list_updated_files(tmp_dir)

        self.assertEqual(updated_files, [])
        # The empty stderr makes the warning itself the only diagnosis material:
        # it must carry the workspace and the failed command
        message = "\n".join(log.output)
        self.assertIn(tmp_dir, message)
        self.assertIn("git diff", message)
        # Disabling UPDATED_SOURCES_REPORTER is not a remedy: Linter.py calls
        # list_updated_files whatever that variable is set to
        self.assertNotIn("UPDATED_SOURCES_REPORTER", message)

    def test_list_updated_files_git_error_warns_once_per_workspace(self):
        # Linter.update_files_lint_results calls list_updated_files once per
        # linted file in `file` lint mode, so a persistent git failure must not
        # repeat the same warning for every file of the run
        diff_err = git.GitCommandError(["git", "diff"], 128, b"")
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.mock_repo_with_failing_diff(tmp_dir, diff_err):
                with self.assertLogs(level="DEBUG") as log:
                    list_updated_files(tmp_dir)
                    list_updated_files(tmp_dir)

        warnings_logged = [line for line in log.output if line.startswith("WARNING")]
        self.assertEqual(len(warnings_logged), 1)

    def test_list_updated_files_without_git_repository(self):
        # Neither the workspace nor the default repo home is a git working copy
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch(
                "megalinter.utils.git.Repo",
                side_effect=git.InvalidGitRepositoryError(tmp_dir),
            ):
                with self.assertLogs(level="WARNING") as log:
                    updated_files = list_updated_files(tmp_dir)

        self.assertEqual(updated_files, [])
        self.assertIn("Unable to find git repository", "\n".join(log.output))

    def test_list_updated_files_when_workspace_is_not_the_working_copy_root(self):
        # The resolved git dir lies outside the workspace (e.g. the workspace is
        # inside a submodule), so the diff would not describe it
        with tempfile.TemporaryDirectory() as tmp_dir:
            mock_repo = MagicMock()
            mock_repo.git_dir = os.path.join(tmp_dir, "..", ".git")

            with patch("megalinter.utils.git.Repo", return_value=mock_repo):
                with self.assertLogs(level="WARNING") as log:
                    updated_files = list_updated_files(tmp_dir)

        self.assertEqual(updated_files, [])
        self.assertIn("not a Git working copy root", "\n".join(log.output))
        mock_repo.index.diff.assert_not_called()
