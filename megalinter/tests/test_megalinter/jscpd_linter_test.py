#!/usr/bin/env python3
"""
Unit tests for JsCpdLinter report materialization.

jscpd used to write its report directly into the workspace and MegaLinter deleted
it again on success, which raced with project mode linters still scanning the same
tree (issue #3979).
"""

import os
import shutil
import stat
import tempfile
import unittest
from unittest.mock import patch

from megalinter import Linter
from megalinter.linters.JsCpdLinter import JsCpdLinter


def _make_linter(
    report_folder, report_tmp_folder, is_active=True, name="COPYPASTE_JSCPD"
):
    linter = JsCpdLinter.__new__(JsCpdLinter)
    linter.report_folder = report_folder
    linter.report_tmp_folder = report_tmp_folder
    linter.is_active = is_active
    linter.name = name
    return linter


# Reproduce the state left by a jscpd run: a report sitting in the temp folder
# outside the workspace, waiting to be materialized or discarded. jscpd's HTML
# reporter nests its output under an "html" folder (see the real crash stdout
# reproduced in linter_test.py: megalinter-reports/copy-paste/html/jscpd-report.json
# and EmailReporter.py, which filters on "copy-paste/html"), so the fixture must
# reproduce that nesting rather than a flat file.
def _linter_with_generated_report(root):
    report_folder = os.path.join(root, "megalinter-reports")
    tmp_folder = os.path.join(root, "tmp-jscpd")
    os.makedirs(report_folder)
    os.makedirs(os.path.join(tmp_folder, "html"))
    with open(
        os.path.join(tmp_folder, "html", "jscpd-report.html"), "w", encoding="utf-8"
    ) as fh:
        fh.write("<html></html>")
    # tempfile.mkdtemp always creates its directory 0700 regardless of umask;
    # reproduce that here since this fixture builds tmp_folder with os.makedirs
    os.chmod(tmp_folder, 0o700)
    return _make_linter(report_folder, tmp_folder), report_folder, tmp_folder


# Whether a report left behind by a previous run survives
# remove_stale_copy_paste_report when MegaLinter runs under the given image flavor
def _stale_report_survives_flavor(flavor, flavor_linters):
    with tempfile.TemporaryDirectory() as root:
        report_folder = os.path.join(root, "megalinter-reports")
        stale_folder = os.path.join(report_folder, "copy-paste")
        os.makedirs(stale_folder)
        linter = _make_linter(report_folder, None)

        with (
            patch(
                "megalinter.flavor_factory.get_image_flavor",
                return_value=flavor,
            ),
            patch(
                "megalinter.flavor_factory.list_flavor_linters",
                return_value=flavor_linters,
            ),
        ):
            linter.remove_stale_copy_paste_report()

        return os.path.isdir(stale_folder)


class JsCpdLinterTest(unittest.TestCase):
    def test_report_materialized_when_clones_found(self):
        with tempfile.TemporaryDirectory() as root:
            linter, report_folder, tmp_folder = _linter_with_generated_report(root)

            linter.materialize_copy_paste_report(1)

            published_folder = os.path.join(report_folder, "copy-paste")
            self.assertTrue(
                os.path.isfile(
                    os.path.join(published_folder, "html", "jscpd-report.html")
                )
            )
            self.assertFalse(os.path.isdir(tmp_folder))
            self.assertIsNone(linter.report_tmp_folder)
            # shutil.copytree's final copystat(src, dst) would otherwise leave the
            # published folder at mkdtemp's 0700, unreadable to a non-root consumer
            # such as a later actions/upload-artifact step
            self.assertEqual(stat.S_IMODE(os.stat(published_folder).st_mode), 0o755)

    def test_report_discarded_when_no_clones_found(self):
        with tempfile.TemporaryDirectory() as root:
            linter, report_folder, tmp_folder = _linter_with_generated_report(root)

            linter.materialize_copy_paste_report(0)

            # Nothing is created inside the report folder, and nothing is deleted
            # from it either: the copy-paste folder simply never appears
            self.assertFalse(os.path.isdir(os.path.join(report_folder, "copy-paste")))
            self.assertFalse(os.path.isdir(tmp_folder))
            self.assertIsNone(linter.report_tmp_folder)

    def test_report_copy_failure_is_logged_and_temp_folder_still_removed(self):
        with tempfile.TemporaryDirectory() as root:
            linter, report_folder, tmp_folder = _linter_with_generated_report(root)

            with patch.object(
                shutil, "copytree", side_effect=PermissionError("denied")
            ):
                with self.assertLogs(level="WARNING") as logs:
                    linter.materialize_copy_paste_report(1)

            self.assertTrue(any("Unable to copy" in message for message in logs.output))
            self.assertFalse(os.path.isdir(tmp_folder))
            self.assertIsNone(linter.report_tmp_folder)

    def test_no_temp_folder_is_a_noop(self):
        with tempfile.TemporaryDirectory() as root:
            report_folder = os.path.join(root, "megalinter-reports")
            os.makedirs(report_folder)

            linter = _make_linter(report_folder, None)
            linter.materialize_copy_paste_report(1)

            self.assertFalse(os.path.isdir(os.path.join(report_folder, "copy-paste")))

    def test_stale_report_of_previous_run_is_removed(self):
        # CLEAR_REPORT_FOLDER defaults to false, so a report kept from a previous
        # run would contradict the text reporter stating that no copy-paste report
        # has been generated
        with tempfile.TemporaryDirectory() as root:
            report_folder = os.path.join(root, "megalinter-reports")
            stale_folder = os.path.join(report_folder, "copy-paste")
            os.makedirs(stale_folder)
            with open(
                os.path.join(stale_folder, "jscpd-report.html"), "w", encoding="utf-8"
            ) as fh:
                fh.write("<html>previous run</html>")
            linter = _make_linter(report_folder, None)

            linter.remove_stale_copy_paste_report()
            linter.materialize_copy_paste_report(0)

            self.assertFalse(os.path.isdir(stale_folder))
            self.assertTrue(os.path.isdir(report_folder))

    def test_stale_report_kept_when_linter_is_disabled(self):
        # The linter object is still constructed when COPYPASTE_JSCPD is disabled, so
        # a disabled jscpd must not discard the report a previous run left behind
        with tempfile.TemporaryDirectory() as root:
            report_folder = os.path.join(root, "megalinter-reports")
            stale_folder = os.path.join(report_folder, "copy-paste")
            os.makedirs(stale_folder)
            linter = _make_linter(report_folder, None, is_active=False)

            linter.remove_stale_copy_paste_report()

            self.assertTrue(os.path.isdir(stale_folder))

    def test_stale_report_kept_when_absent_from_image_flavor(self):
        # formatters/security don't ship COPYPASTE_JSCPD, but check_active_linters_
        # match_flavor only flips is_active to False after every linter, including
        # this one, has already been constructed (MegaLinter.py:227 vs :262)
        self.assertTrue(_stale_report_survives_flavor("formatters", ["SPELL_CSPELL"]))

    def test_stale_report_removed_when_present_in_image_flavor(self):
        self.assertFalse(_stale_report_survives_flavor("python", ["COPYPASTE_JSCPD"]))

    def test_stale_report_removal_skipped_when_reports_disabled(self):
        with tempfile.TemporaryDirectory() as cwd:
            os.makedirs(os.path.join(cwd, "copy-paste"))
            # A folder that would actually be deleted if report_folder == "none"
            # were ever joined with "copy-paste" and resolved against cwd, unlike
            # the sibling "copy-paste" folder above which the "" case would delete
            os.makedirs(os.path.join(cwd, "none", "copy-paste"))
            initial_cwd = os.getcwd()
            os.chdir(cwd)
            try:
                # "none" must never be joined with "copy-paste" and resolved
                # against the current directory
                _make_linter("none", None).remove_stale_copy_paste_report()
                _make_linter("", None).remove_stale_copy_paste_report()
            finally:
                os.chdir(initial_cwd)

            self.assertTrue(os.path.isdir(os.path.join(cwd, "copy-paste")))
            self.assertTrue(os.path.isdir(os.path.join(cwd, "none", "copy-paste")))

    def test_clean_run_explains_the_missing_report(self):
        linter = _make_linter("megalinter-reports", None)
        linter.status = "success"
        linter.master = _make_linter("megalinter-reports", None)

        self.assertIn(
            "no copy-paste report has been generated",
            " ".join(linter.complete_text_reporter_report(None)),
        )

    def test_no_report_explanation_when_report_files_are_disabled(self):
        # jscpd then runs with the console reporter alone and writes no report
        # whatever it finds, so blaming the absence on a clean run would be wrong
        linter = _make_linter("none", None)
        linter.status = "success"
        linter.master = _make_linter("none", None)

        self.assertEqual(linter.complete_text_reporter_report(None), [])

    def test_no_report_explanation_when_copy_paste_was_found(self):
        linter = _make_linter("megalinter-reports", None)
        linter.status = "error"
        linter.master = _make_linter("megalinter-reports", None)

        self.assertEqual(linter.complete_text_reporter_report(None), [])

    def test_build_lint_command_redirects_output_outside_workspace(self):
        # This is the actual #3979 fix: jscpd's report must land outside the
        # workspace/report folder other linters are still scanning, not back at
        # f"{self.report_folder}/copy-paste/"
        with tempfile.TemporaryDirectory() as root:
            report_folder = os.path.join(root, "megalinter-reports")
            os.makedirs(report_folder)
            linter = _make_linter(report_folder, None)
            linter.master = linter
            linter.cli_lint_extra_args = []

            with patch.object(Linter, "build_lint_command", return_value=["jscpd"]):
                cmd = linter.build_lint_command()

            try:
                self.assertIsNotNone(linter.report_tmp_folder)
                self.assertTrue(os.path.isdir(linter.report_tmp_folder))
                self.assertFalse(linter.report_tmp_folder.startswith(root + os.sep))
                self.assertFalse(
                    linter.report_tmp_folder.startswith(report_folder + os.sep)
                )
                self.assertIn("--output", linter.cli_lint_extra_args)
                output_index = linter.cli_lint_extra_args.index("--output")
                self.assertEqual(
                    linter.cli_lint_extra_args[output_index + 1],
                    linter.report_tmp_folder,
                )
                self.assertEqual(cmd, ["jscpd"])
            finally:
                if linter.report_tmp_folder and os.path.isdir(linter.report_tmp_folder):
                    shutil.rmtree(linter.report_tmp_folder)

    def test_build_lint_command_falls_back_to_console_when_reports_disabled(self):
        linter = _make_linter("none", None)
        linter.master = linter
        linter.cli_lint_extra_args = []

        with patch.object(
            Linter,
            "build_lint_command",
            return_value=["jscpd", "--reporters", "console,html"],
        ):
            cmd = linter.build_lint_command()

        self.assertIsNone(linter.report_tmp_folder)
        self.assertEqual(linter.cli_lint_extra_args, [])
        self.assertEqual(cmd, ["jscpd", "--reporters", "console"])

    def test_process_linter_materializes_report_on_failure(self):
        with tempfile.TemporaryDirectory() as root:
            linter, report_folder, tmp_folder = _linter_with_generated_report(root)

            with patch.object(
                Linter, "process_linter", return_value=(1, "some stdout")
            ):
                return_code, stdout = linter.process_linter()

            self.assertEqual((return_code, stdout), (1, "some stdout"))
            self.assertTrue(
                os.path.isfile(
                    os.path.join(
                        report_folder, "copy-paste", "html", "jscpd-report.html"
                    )
                )
            )
            self.assertFalse(os.path.isdir(tmp_folder))
            self.assertIsNone(linter.report_tmp_folder)

    def test_process_linter_leaks_no_temp_folder_when_base_raises(self):
        # Proves the "finally" matters: a plain self.materialize_copy_paste_report()
        # placed after super().process_linter() with no try/finally would pass the
        # happy-path tests above just as well, but would leak the temp folder created
        # by build_lint_command whenever process_linter raises (e.g. Linter.py's
        # os.remove of a stale SARIF file before the command is even run)
        with tempfile.TemporaryDirectory() as root:
            linter, report_folder, tmp_folder = _linter_with_generated_report(root)

            with patch.object(
                Linter, "process_linter", side_effect=RuntimeError("boom")
            ):
                with self.assertRaises(RuntimeError):
                    linter.process_linter()

            # A crash is not "clones were found": the report must not be published
            self.assertFalse(os.path.isdir(os.path.join(report_folder, "copy-paste")))
            self.assertFalse(os.path.isdir(tmp_folder))
            self.assertIsNone(linter.report_tmp_folder)

    def test_process_linter_discards_report_on_success(self):
        with tempfile.TemporaryDirectory() as root:
            linter, report_folder, tmp_folder = _linter_with_generated_report(root)

            with patch.object(Linter, "process_linter", return_value=(0, "")):
                return_code, stdout = linter.process_linter()

            self.assertEqual((return_code, stdout), (0, ""))
            self.assertFalse(os.path.isdir(os.path.join(report_folder, "copy-paste")))
            self.assertFalse(os.path.isdir(tmp_folder))
            self.assertIsNone(linter.report_tmp_folder)
