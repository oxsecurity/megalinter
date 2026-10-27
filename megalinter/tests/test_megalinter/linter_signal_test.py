#!/usr/bin/env python3
"""A sub-process stopped by a signal has a negative return code in Python.
It must count as a failure, not as a success."""

import subprocess
import tempfile
import unittest
import uuid
from types import SimpleNamespace
from unittest import mock

from megalinter import config, linter_factory, pre_post_factory, utils

KILLED = -9


def build_file_mode_linter(request_id, workspace, disable_errors=False):
    config.set_config(request_id, {"default_workspace": workspace})
    params = {
        "default_linter_activation": True,
        "enable_descriptors": [],
        "enable_linters": [],
        "disable_descriptors": [],
        "disable_linters": [],
        "disable_errors_linters": ["BICEP_BICEP_LINTER"] if disable_errors else [],
        "github_workspace": workspace,
        "workspace": workspace,
        "linter_rules_path": workspace,
        "default_rules_location": utils.get_default_rules_location(),
        "post_linter_status": False,
        "request_id": request_id,
    }
    linter = linter_factory.build_linter("BICEP", "bicep_linter", params)
    linter.master = SimpleNamespace(active_linters=[linter], all_diff_files=[])
    linter.reporters = []
    linter.files = [f"{workspace}/main.bicep"]
    return linter


class LinterSignalTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.set_config(self.request_id, {})
        self.addCleanup(config.delete, self.request_id)

    def test_file_killed_by_signal_is_an_error(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = build_file_mode_linter(self.request_id, workspace)
            self.assertEqual(linter.cli_lint_mode, "file")
            output = "main.bicep(1,7) : Error no-unused-params: unused"
            with mock.patch.object(
                linter, "process_linter", return_value=(KILLED, output)
            ):
                linter.run()
        self.assertEqual(linter.status, "error")
        self.assertEqual(linter.return_code, 1)
        self.assertEqual(linter.number_errors, 1)

    def test_file_killed_by_signal_is_a_warning_when_errors_are_disabled(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = build_file_mode_linter(
                self.request_id, workspace, disable_errors=True
            )
            with mock.patch.object(linter, "process_linter", return_value=(KILLED, "")):
                linter.run()
        self.assertEqual(linter.status, "warning")
        self.assertEqual(linter.return_code, 0)
        self.assertEqual(linter.number_errors, 1)

    def test_command_killed_by_signal_stops_when_continue_if_failed_is_false(self):
        killed = subprocess.CompletedProcess("exit 0", KILLED, stdout=b"")
        command = {"command": "exit 0", "continue_if_failed": False}
        mega_linter = SimpleNamespace(workspace=".", request_id=self.request_id)
        with (
            mock.patch.object(
                pre_post_factory, "complete_command", side_effect=lambda c: c
            ),
            mock.patch.object(pre_post_factory, "build_command_env", return_value={}),
            mock.patch.object(pre_post_factory.subprocess, "run", return_value=killed),
        ):
            with self.assertRaisesRegex(Exception, "User command failed"):
                pre_post_factory.run_command(command, "[Pre]", mega_linter)


if __name__ == "__main__":
    unittest.main()
