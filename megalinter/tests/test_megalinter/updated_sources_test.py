#!/usr/bin/env python3
"""
Unit tests for the detection of updated sources and FAIL_IF_UPDATED_SOURCES

"""

import logging
import os
import tempfile
import unittest
import uuid
from types import SimpleNamespace
from unittest import mock

import git

from megalinter import MegaLinter, config, utils
from megalinter.reporters.EmailReporter import EmailReporter
from megalinter.reporters.FileIoReporter import FileIoReporter


def build_megalinter(request_id, linters=None, **attributes):
    mega_linter = object.__new__(MegaLinter.Megalinter)
    mega_linter.request_id = request_id
    mega_linter.linters = linters or []
    mega_linter.github_workspace = "."
    mega_linter.status = "success"
    mega_linter.return_code = 0
    mega_linter.result_message = ""
    mega_linter.has_updated_sources = 0
    mega_linter.updated_sources_baseline = None
    mega_linter.updated_sources_files = []
    mega_linter.updated_sources_failure = False
    mega_linter.fail_if_updated_sources = True
    mega_linter.cli = True
    for key, value in attributes.items():
        setattr(mega_linter, key, value)
    return mega_linter


class updated_sources_test(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.set_config(self.request_id, {"UPDATED_SOURCES_REPORTER": "true"})

    def tearDown(self):
        config.delete()

    def test_snapshot_diff_ignores_files_dirty_before_the_run(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            repo = git.Repo.init(repo_dir)
            for name in ["a.txt", "b.txt", "linter-helps.json"]:
                with open(os.path.join(repo_dir, name), "w", encoding="utf-8") as f:
                    f.write("initial")
            repo.index.add(["a.txt", "b.txt", "linter-helps.json"])
            with repo.config_writer() as writer:
                writer.set_value("user", "name", "test")
                writer.set_value("user", "email", "test@example.com")
            repo.index.commit("init")
            with open(os.path.join(repo_dir, "a.txt"), "w", encoding="utf-8") as f:
                f.write("dirty before the run")
            before = utils.snapshot_updated_files(repo_dir)
            self.assertEqual(["a.txt"], list(before.keys()))
            self.assertEqual([], utils.diff_updated_files_snapshots(before, before))
            with open(os.path.join(repo_dir, "a.txt"), "w", encoding="utf-8") as f:
                f.write("changed again by a fixer")
            with open(os.path.join(repo_dir, "b.txt"), "w", encoding="utf-8") as f:
                f.write("changed by a fixer")
            with open(
                os.path.join(repo_dir, "linter-helps.json"), "w", encoding="utf-8"
            ) as f:
                f.write("changed by MegaLinter")
            after = utils.snapshot_updated_files(repo_dir)
            self.assertEqual(
                ["a.txt", "b.txt"], utils.diff_updated_files_snapshots(before, after)
            )
            repo.close()

    def test_fail_if_updated_sources_names_the_fixing_linters(self):
        linters = [
            SimpleNamespace(name="C_CLANG_FORMAT", number_fixed=1),
            SimpleNamespace(name="C_CPPLINT", number_fixed=0),
        ]
        mega_linter = build_megalinter(self.request_id, linters)
        mega_linter.manage_updated_sources()
        self.assertEqual(1, mega_linter.has_updated_sources)
        self.assertEqual("error", mega_linter.status)
        self.assertEqual(1, mega_linter.return_code)
        self.assertIn("FAIL_IF_UPDATED_SOURCES=true", mega_linter.result_message)
        self.assertIn("C_CLANG_FORMAT", mega_linter.result_message)
        self.assertNotIn("C_CPPLINT", mega_linter.result_message)

    def test_fail_if_updated_sources_keeps_linter_return_code(self):
        linters = [SimpleNamespace(name="C_CLANG_FORMAT", number_fixed=1)]
        mega_linter = build_megalinter(
            self.request_id, linters, status="error", return_code=2
        )
        mega_linter.manage_updated_sources()
        self.assertEqual(2, mega_linter.return_code)
        self.assertIn("FAIL_IF_UPDATED_SOURCES=true", mega_linter.result_message)

    def test_updated_sources_without_the_option_do_not_fail(self):
        linters = [SimpleNamespace(name="C_CLANG_FORMAT", number_fixed=1)]
        mega_linter = build_megalinter(
            self.request_id, linters, fail_if_updated_sources=False
        )
        mega_linter.manage_updated_sources()
        self.assertEqual(1, mega_linter.has_updated_sources)
        self.assertEqual("success", mega_linter.status)
        self.assertEqual("", mega_linter.result_message)

    def test_updated_sources_detected_without_linter_counting_them(self):
        mega_linter = build_megalinter(
            self.request_id, updated_sources_baseline={"a.txt": "hash1"}
        )
        with mock.patch.object(
            utils, "snapshot_updated_files", return_value={"a.txt": "hash2"}
        ):
            mega_linter.manage_updated_sources()
        self.assertEqual(["a.txt"], mega_linter.updated_sources_files)
        self.assertEqual("error", mega_linter.status)
        self.assertIn("POST_COMMANDS", mega_linter.result_message)

    def test_disable_errors_does_not_hide_fail_if_updated_sources(self):
        config.set_value(self.request_id, "DISABLE_ERRORS", "true")
        mega_linter = build_megalinter(
            self.request_id,
            status="error",
            return_code=1,
            updated_sources_failure=True,
        )
        with mock.patch.object(MegaLinter, "get_ci_provider"):
            with self.assertRaises(SystemExit) as exit_context:
                mega_linter.check_results()
        self.assertEqual(1, exit_context.exception.code)

    def test_disable_errors_still_exits_0_without_updated_sources_failure(self):
        config.set_value(self.request_id, "DISABLE_ERRORS", "true")
        mega_linter = build_megalinter(self.request_id, status="error", return_code=1)
        with mock.patch.object(MegaLinter, "get_ci_provider"):
            with self.assertRaises(SystemExit) as exit_context:
                mega_linter.check_results()
        self.assertEqual(0, exit_context.exception.code)

    def test_unrecognized_option_value_is_reported(self):
        for value in ["True", ""]:
            config.set_value(self.request_id, "FAIL_IF_UPDATED_SOURCES", value)
            mega_linter = build_megalinter(self.request_id)
            with self.assertLogs(level=logging.WARNING) as logs:
                self.assertFalse(mega_linter.read_fail_if_updated_sources())
            self.assertIn("FAIL_IF_UPDATED_SOURCES value", "\n".join(logs.output))

    def test_diff_fetch_failure_explains_how_to_authenticate(self):
        mega_linter = build_megalinter(self.request_id, workspace=".")
        fetch_error = git.GitCommandError(
            "fetch", 128, stderr="could not read Username"
        )
        repo = mock.MagicMock()
        repo.refs = []
        repo.git.fetch.side_effect = fetch_error
        with mock.patch.object(MegaLinter.git, "Repo", return_value=repo):
            with self.assertLogs(level=logging.WARNING) as logs:
                with self.assertRaises(git.GitCommandError):
                    mega_linter.list_files_git_diff()
        self.assertIn("persist-credentials", " ".join(logs.output))

    def test_email_reporter_skips_clean_runs_by_default(self):
        self.assert_reporter_skip(EmailReporter, "EMAIL_REPORTER_SEND_SUCCESS")

    def test_fileio_reporter_skips_clean_runs_when_requested(self):
        self.assert_reporter_skip(
            FileIoReporter, "FILEIO_REPORTER_SEND_SUCCESS", skip_value="true"
        )

    def assert_reporter_skip(self, reporter_class, variable, skip_value=None):
        skipped_value = skip_value or "false"
        sent_value = "false" if skipped_value == "true" else "true"
        reporter = object.__new__(reporter_class)
        reporter.report_folder = tempfile.gettempdir() + os.path.sep + "no-report"
        for value, has_updated_sources, expect_skip in [
            (skipped_value, 0, True),
            (skipped_value, 1, False),
            (sent_value, 0, False),
        ]:
            config.set_value(self.request_id, variable, value)
            reporter.master = SimpleNamespace(
                request_id=self.request_id,
                status="success",
                has_updated_sources=has_updated_sources,
            )
            with mock.patch("requests.post") as post:
                with self.assertLogs(level=logging.INFO) as logs:
                    logging.info("sentinel")
                    reporter.produce_report()
            skipped = any(
                "No mail sent, as the MegaLinter status" in message
                or "No file sent" in message
                for message in logs.output
            )
            self.assertEqual(expect_skip, skipped, f"{variable}={value}")
            if reporter_class is FileIoReporter:
                self.assertEqual(not expect_skip, post.called)
