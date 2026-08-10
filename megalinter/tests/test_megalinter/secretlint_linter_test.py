#!/usr/bin/env python3
"""
Unit tests for the secretlint ignore file MegaLinter generates.

secretlint resolves --secretlintignore as path.join(cwd, value) and silently skips
the file when that path does not exist, so the value must be relative to the
workspace. The file itself lives in MegaLinter's report folder so MegaLinter never
creates or deletes files inside the sources being scanned (issue #3979).
"""

import builtins
import errno
import os
import shutil
import tempfile
from unittest.mock import patch

from megalinter import config
from megalinter.Linter import Linter
from megalinter.linters.SecretLintLinter import (
    MEGALINTER_IGNORE_FILE_NAME,
    SecretLintLinter,
)
from megalinter.tests.test_megalinter.isolated_config_test_case import (
    IsolatedConfigTestCase,
)
from megalinter.tests.test_megalinter.linter_run_stub import build_project_run_linter


class _Master:
    def __init__(self, report_folder):
        self.report_folder = report_folder


def _make_linter(
    workspace, report_folder, request_id, ignore_file=None, user_args=None
):
    linter = SecretLintLinter.__new__(SecretLintLinter)
    linter.linter_name = "secretlint"
    linter.name = "REPOSITORY_SECRETLINT"
    linter.workspace = workspace
    linter.report_folder = report_folder
    linter.request_id = request_id
    linter.ignore_file = ignore_file
    linter.cli_lint_user_args = user_args if user_args is not None else []
    linter.master = _Master(report_folder)
    linter.megalinter_ignore_file = None
    linter.ignore_tmp_folder = None
    # Read by Linter.get_project_exclude_directories and only set by the real
    # constructor, which these tests bypass
    linter.filter_regex_exclude_descriptor = None
    linter.filter_regex_exclude_linter = None
    linter.log_lines_pre = []
    return linter


class SecretLintLinterTest(IsolatedConfigTestCase):
    def test_setup_isolates_ambient_megalinter_config(self):
        # Without the patch.dict(..., clear=True) guard in setUp, an ambient
        # MEGALINTER_CONFIG pointing at a non-existent file reaches
        # workspace + os.path.sep + config_file_name with workspace=None, raising
        # TypeError before config.get is ever reached.
        with patch.dict(os.environ, {"MEGALINTER_CONFIG": "no-such-config.yml"}):
            self.setUp()

        self.assertNotEqual(
            config.get(self.request_id, "MEGALINTER_CONFIG", None),
            "no-such-config.yml",
        )

    def _build_ignore_file(self, workspace, report_folder=None, **linter_kwargs):
        # Returns both halves of the contract: what secretlint receives on the
        # command line (the relative path) and what it reads from it (the file
        # content). Reading the file back is also what proves the relative path
        # points at a file that was really created.
        if report_folder is None:
            report_folder = os.path.join(workspace, "megalinter-reports")
        linter = _make_linter(
            workspace, report_folder, self.request_id, **linter_kwargs
        )
        relative_path = linter.build_megalinter_ignore_file()
        with open(
            os.path.join(report_folder, MEGALINTER_IGNORE_FILE_NAME),
            "r",
            encoding="utf-8",
        ) as fh:
            return relative_path, fh.read()

    def test_ignore_file_written_with_relative_path(self):
        with tempfile.TemporaryDirectory() as workspace:
            relative_path, _ = self._build_ignore_file(workspace)

            self.assertEqual(
                relative_path, f"megalinter-reports/{MEGALINTER_IGNORE_FILE_NAME}"
            )
            self.assertFalse(os.path.isabs(relative_path))

    def test_report_folder_is_excluded(self):
        with tempfile.TemporaryDirectory() as workspace:
            _, content = self._build_ignore_file(workspace)

            # Bare pattern, not megalinter-reports/** : node-ignore prunes the
            # directory outright rather than testing each child
            self.assertIn("\nmegalinter-reports\n", content)
            self.assertNotIn("megalinter-reports/**", content)
            # Excluded directories are forwarded like for every other project mode
            # linter, but only those that exist at the workspace root: this
            # workspace is empty, so the defaults contribute nothing
            self.assertNotIn(".terraform", content)
            self.assertNotIn(".terragrunt-cache", content)

    def test_excluded_directories_are_forwarded(self):
        # Same contract as the generic cli_lint_mode_project_exclude_ignore_file_*
        # forwarding, applied through the generated file so nothing is written to
        # the linted sources
        with tempfile.TemporaryDirectory() as workspace:
            os.makedirs(os.path.join(workspace, "build-artifacts"))
            config.set_value(
                self.request_id, "EXCLUDED_DIRECTORIES", ["build-artifacts"]
            )

            _, content = self._build_ignore_file(workspace)

            self.assertIn("\nbuild-artifacts\n", content)
            # The report folder stays last: last match wins, so it cannot be
            # cancelled by anything forwarded before it
            self.assertLess(
                content.index("\nbuild-artifacts\n"),
                content.index("\nmegalinter-reports\n"),
            )

    def test_excluded_directories_not_forwarded_when_disabled(self):
        with tempfile.TemporaryDirectory() as workspace:
            os.makedirs(os.path.join(workspace, "build-artifacts"))
            config.set_value(
                self.request_id, "EXCLUDED_DIRECTORIES", ["build-artifacts"]
            )
            config.set_value(
                self.request_id,
                "REPOSITORY_SECRETLINT_FORWARD_EXCLUDED_DIRECTORIES",
                "false",
            )

            _, content = self._build_ignore_file(workspace)

            self.assertNotIn("build-artifacts", content)
            # Opting out of forwarding must not opt out of the report folder
            # exclusion, which exists to keep MegaLinter's own output unscanned
            self.assertIn("\nmegalinter-reports\n", content)

    def test_excluded_directory_absent_from_workspace_is_not_forwarded(self):
        # get_project_exclude_directories keeps only directories that exist at the
        # workspace root, so the generated file never lists phantom entries
        with tempfile.TemporaryDirectory() as workspace:
            config.set_value(self.request_id, "EXCLUDED_DIRECTORIES", ["never-created"])

            _, content = self._build_ignore_file(workspace)

            self.assertNotIn("never-created", content)

    def test_user_patterns_are_merged_before_megalinter_patterns(self):
        with tempfile.TemporaryDirectory() as workspace:
            user_ignore = os.path.join(workspace, ".secretlintignore")
            with open(user_ignore, "w", encoding="utf-8") as fh:
                fh.write("my/fixtures\n!megalinter-reports/keep.json\n")

            _, content = self._build_ignore_file(workspace, ignore_file=user_ignore)

            self.assertIn("my/fixtures", content)
            # gitignore semantics are last match wins, so MegaLinter's patterns must
            # come after the user's negation to stay authoritative
            self.assertLess(
                content.index("!megalinter-reports/keep.json"),
                content.index("\nmegalinter-reports\n"),
            )

    def test_unreadable_source_ignore_file_degrades(self):
        # before_lint_files is called from Linter.run with no exception boundary up
        # to megalinter/run.py, so raising here would abort every linter, not just
        # secretlint. A non-UTF-8 .gitignore must therefore degrade, never raise.
        with tempfile.TemporaryDirectory() as workspace:
            with open(os.path.join(workspace, ".gitignore"), "wb") as fh:
                fh.write(b"\xff\xfe invalid\n")

            relative_path, content = self._build_ignore_file(workspace)

            self.assertEqual(
                relative_path, f"megalinter-reports/{MEGALINTER_IGNORE_FILE_NAME}"
            )
            self.assertIn("\nmegalinter-reports\n", content)

    def test_write_failure_logs_warning_with_strerror_and_returns_none(self):
        # A real write failure, not the megalinter_ignore_file = None shortcut used
        # by test_get_ignore_arguments_falls_back_to_ignore_file_base_name, so this
        # actually exercises the except OSError branch of
        # build_megalinter_ignore_file rather than assuming its postcondition.
        # The denial is injected instead of produced with os.chmod(0o500) because
        # MegaLinter's test image runs as root, and root bypasses directory
        # permissions: the write would succeed and the branch never run. The error
        # carries an errno, a strerror and a filename like a kernel-raised one, as a
        # bare PermissionError("denied") has strerror None and would satisfy the
        # "(None)" assertion below for the wrong reason.
        with tempfile.TemporaryDirectory() as workspace:
            report_folder = os.path.join(workspace, "megalinter-reports")
            os.makedirs(report_folder)
            linter = _make_linter(workspace, report_folder, self.request_id)
            ignore_file_path = os.path.join(report_folder, MEGALINTER_IGNORE_FILE_NAME)
            real_open = builtins.open

            # Only the generated ignore file is denied: every other open, such as
            # the source ignore file this method also reads, must behave normally
            def deny_ignore_file_write(file, *args, **kwargs):
                if file == ignore_file_path:
                    raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), file)
                return real_open(file, *args, **kwargs)

            with patch("builtins.open", deny_ignore_file_write):
                with self.assertLogs(level="WARNING") as logs:
                    relative_path = linter.build_megalinter_ignore_file()

            self.assertIsNone(relative_path)
            self.assertFalse(os.path.exists(ignore_file_path))
            warning_messages = [
                message for message in logs.output if "Unable to write" in message
            ]
            self.assertEqual(len(warning_messages), 1)
            self.assertNotIn("(None)", warning_messages[0])
            self.assertIn(os.strerror(errno.EACCES), warning_messages[0])

    def test_gitignore_used_when_no_secretlintignore(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".gitignore"), "w", encoding="utf-8"
            ) as fh:
                fh.write("dist\n")

            _, content = self._build_ignore_file(workspace)

            self.assertIn("dist", content)

    def _generated_content_for_user_ignore_arg(self, workspace, user_args):
        with open(
            os.path.join(workspace, "custom-ignore"), "w", encoding="utf-8"
        ) as fh:
            fh.write("vendor\n")

        _, content = self._build_ignore_file(workspace, user_args=user_args)

        return content

    def test_user_supplied_ignore_arg_is_merged(self):
        # secretlint takes the last --secretlintignore and drops the earlier one, so
        # a user file that is not merged would stop being applied entirely
        with tempfile.TemporaryDirectory() as workspace:
            content = self._generated_content_for_user_ignore_arg(
                workspace, ["--secretlintignore", "custom-ignore"]
            )
            self.assertIn("vendor", content)

    def test_custom_report_folder_is_excluded(self):
        with tempfile.TemporaryDirectory() as workspace:
            relative_path, content = self._build_ignore_file(
                workspace, report_folder=os.path.join(workspace, "build", "ml-reports")
            )

            self.assertEqual(
                relative_path, f"build/ml-reports/{MEGALINTER_IGNORE_FILE_NAME}"
            )
            self.assertIn("build/ml-reports", content)

    def test_get_ignore_arguments_uses_generated_file(self):
        with tempfile.TemporaryDirectory() as workspace:
            report_folder = os.path.join(workspace, "megalinter-reports")
            linter = _make_linter(workspace, report_folder, self.request_id)
            linter.megalinter_ignore_file = (
                f"megalinter-reports/{MEGALINTER_IGNORE_FILE_NAME}"
            )

            self.assertEqual(
                linter.get_ignore_arguments([]),
                [
                    "--secretlintignore",
                    f"megalinter-reports/{MEGALINTER_IGNORE_FILE_NAME}",
                ],
            )

    def test_report_folder_outside_workspace_adds_no_parent_pattern(self):
        with tempfile.TemporaryDirectory() as root:
            workspace = os.path.join(root, "workspace")
            os.makedirs(workspace)

            relative_path, content = self._build_ignore_file(
                workspace, report_folder=os.path.join(root, "reports")
            )

            # secretlint resolves this with path.join, which normalizes "..", so the
            # generated file is still found
            self.assertEqual(relative_path, f"../reports/{MEGALINTER_IGNORE_FILE_NAME}")
            # "../reports" is not a valid gitignore pattern, and a report folder
            # outside the workspace is never scanned anyway
            self.assertNotIn("..", content)

    def test_get_ignore_arguments_falls_back_to_ignore_file_base_name(self):
        # secretlint resolves --secretlintignore as path.join(cwd, value) and
        # silently drops an absolute path, so the fallback used when MegaLinter
        # cannot write its own ignore file must pass the base name
        with tempfile.TemporaryDirectory() as workspace:
            report_folder = os.path.join(workspace, "megalinter-reports")
            ignore_file = os.path.join(
                workspace, ".github", "linters", ".secretlintignore"
            )
            linter = _make_linter(
                workspace, report_folder, self.request_id, ignore_file=ignore_file
            )
            linter.cli_lint_ignore_arg_name = "--secretlintignore"
            linter.cli_lint_extra_args_after = []

            self.assertIsNone(linter.megalinter_ignore_file)
            self.assertEqual(
                linter.get_ignore_arguments([]),
                ["--secretlintignore", ".secretlintignore"],
            )

    def _resolve_ignore_path_and_register_cleanup(self, workspace, relative_path):
        # secretlint resolves --secretlintignore as path.join(cwd, value) with cwd
        # being the workspace, so this is the contract that actually matters at
        # runtime: the returned value must combine with the workspace to reach the
        # file secretlint will actually read.
        resolved_path = os.path.normpath(os.path.join(workspace, relative_path))
        self.addCleanup(
            shutil.rmtree, os.path.dirname(resolved_path), ignore_errors=True
        )
        return resolved_path

    def _make_reports_disabled_linter_with_user_ignore(self, workspace):
        user_ignore = os.path.join(workspace, ".secretlintignore")
        with open(user_ignore, "w", encoding="utf-8") as fh:
            fh.write("my/fixtures\n")
        return _make_linter(workspace, "none", self.request_id, ignore_file=user_ignore)

    def _generated_content_at(self, workspace, relative_path):
        resolved_path = self._resolve_ignore_path_and_register_cleanup(
            workspace, relative_path
        )
        with open(resolved_path, "r", encoding="utf-8") as fh:
            return fh.read()

    def test_reports_disabled_writes_to_temp_folder(self):
        # _make_linter already wires master.report_folder to "none", which is
        # what can_write_report_files checks. A .secretlintignore living in
        # LINTER_RULES_PATH must still be applied even though there is no report
        # folder to write the generated file into (issue #3979 review finding).
        with tempfile.TemporaryDirectory() as workspace:
            linter = _make_linter(workspace, "none", self.request_id)

            relative_path = linter.build_megalinter_ignore_file()

            self.assertIsNotNone(relative_path)
            self.assertFalse(os.path.isabs(relative_path))
            resolved_path = self._resolve_ignore_path_and_register_cleanup(
                workspace, relative_path
            )
            self.assertTrue(os.path.isfile(resolved_path))

    def test_reports_disabled_merges_user_patterns(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self._make_reports_disabled_linter_with_user_ignore(workspace)

            relative_path = linter.build_megalinter_ignore_file()

            self.assertIn(
                "my/fixtures", self._generated_content_at(workspace, relative_path)
            )

    def test_reports_disabled_adds_no_report_folder_pattern(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self._make_reports_disabled_linter_with_user_ignore(workspace)

            content = self._generated_content_at(
                workspace, linter.build_megalinter_ignore_file()
            )

            self.assertIn("my/fixtures", content)
            self.assertNotIn(
                "Added by MegaLinter: never lint MegaLinter's own output", content
            )

    def test_reports_disabled_logs_warning_naming_report_output_folder(self):
        # The warning only fires when reports being disabled actually put
        # something at risk: a user ignore file must be present
        with tempfile.TemporaryDirectory() as workspace:
            linter = self._make_reports_disabled_linter_with_user_ignore(workspace)

            with self.assertLogs(level="WARNING") as logs:
                relative_path = linter.build_megalinter_ignore_file()

            self.assertTrue(
                any("REPORT_OUTPUT_FOLDER" in message for message in logs.output)
            )
            self._resolve_ignore_path_and_register_cleanup(workspace, relative_path)

    def test_reports_disabled_no_source_ignore_file_logs_no_warning(self):
        # No ignore file anywhere means nothing was ever at risk of being
        # dropped, so the noisy REPORT_OUTPUT_FOLDER warning must not fire
        with tempfile.TemporaryDirectory() as workspace:
            linter = _make_linter(workspace, "none", self.request_id)

            with self.assertNoLogs(level="WARNING"):
                relative_path = linter.build_megalinter_ignore_file()

            self._resolve_ignore_path_and_register_cleanup(workspace, relative_path)

    def test_reports_disabled_uses_gitignore_when_no_secretlintignore(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".gitignore"), "w", encoding="utf-8"
            ) as fh:
                fh.write("dist\n")
            linter = _make_linter(workspace, "none", self.request_id)

            relative_path = linter.build_megalinter_ignore_file()

            self.assertIn("dist", self._generated_content_at(workspace, relative_path))

    def _make_run_ready_linter(self, workspace):
        linter = _make_linter(workspace, "none", self.request_id)
        build_project_run_linter(
            self.request_id,
            linter,
            name="TEST_SECRETLINT",
            output_sarif=False,
        )
        return linter

    def _assert_ignore_tmp_folder_cleaned(self, linter, workspace):
        self.assertIsNone(linter.ignore_tmp_folder)
        resolved_path = os.path.normpath(
            os.path.join(workspace, linter.megalinter_ignore_file)
        )
        self.assertFalse(os.path.isdir(os.path.dirname(resolved_path)))

    def test_run_cleans_up_ignore_tmp_folder(self):
        # A leaked temp directory is worth removing on every invocation regardless
        # of process lifetime: nothing else ever cleans up the folder created by
        # build_megalinter_ignore_file when REPORT_OUTPUT_FOLDER is disabled
        with tempfile.TemporaryDirectory() as workspace:
            linter = self._make_run_ready_linter(workspace)

            with patch.object(Linter, "process_linter", return_value=(0, "")):
                linter.run()

            self._assert_ignore_tmp_folder_cleaned(linter, workspace)

    def test_run_cleans_up_ignore_tmp_folder_when_process_linter_raises(self):
        # Proves the "finally" in SecretLintLinter.run() matters: a plain
        # self.remove_ignore_tmp_folder() placed after super().run() with no
        # try/finally would pass the happy-path test above just as well, but
        # would leak the temp folder whenever process_linter raises
        with tempfile.TemporaryDirectory() as workspace:
            linter = self._make_run_ready_linter(workspace)

            with patch.object(
                Linter, "process_linter", side_effect=RuntimeError("boom")
            ):
                with self.assertRaises(RuntimeError):
                    linter.run()

            self._assert_ignore_tmp_folder_cleaned(linter, workspace)

    def test_user_supplied_ignore_arg_with_equals_form_is_merged(self):
        with tempfile.TemporaryDirectory() as workspace:
            content = self._generated_content_for_user_ignore_arg(
                workspace, ["--secretlintignore=custom-ignore"]
            )
            self.assertIn("vendor", content)

    def test_user_supplied_ignore_arg_not_a_file_logs_warning_and_degrades(self):
        with tempfile.TemporaryDirectory() as workspace:
            report_folder = os.path.join(workspace, "megalinter-reports")
            linter = _make_linter(
                workspace,
                report_folder,
                self.request_id,
                user_args=["--secretlintignore", "does-not-exist"],
            )

            with self.assertLogs(level="WARNING") as logs:
                source_ignore_file = linter.get_source_ignore_file()

            self.assertIsNone(source_ignore_file)
            self.assertTrue(
                any(
                    "does-not-exist" in message and "not" in message
                    for message in logs.output
                )
            )

    def test_unresolvable_user_ignore_arg_does_not_fall_back_to_gitignore(self):
        # A .gitignore in a real repository routinely lists exactly what a secrets
        # scanner exists to find (.env, *.pem, credentials.json, secrets/). An
        # unresolvable --secretlintignore must not silently promote those patterns
        # to authoritative status via the fallback chain.
        with tempfile.TemporaryDirectory() as workspace:
            report_folder = os.path.join(workspace, "megalinter-reports")
            with open(
                os.path.join(workspace, ".gitignore"), "w", encoding="utf-8"
            ) as fh:
                fh.write(".env\n")
            linter = _make_linter(
                workspace,
                report_folder,
                self.request_id,
                user_args=["--secretlintignore", "does-not-exist"],
            )

            with self.assertLogs(level="WARNING"):
                source_ignore_file = linter.get_source_ignore_file()

            self.assertIsNone(source_ignore_file)
