#!/usr/bin/env python3
"""Tests for per-linter timeout support (<LINTER_KEY>_TIMEOUT_SECONDS /
LINTER_TIMEOUT_SECONDS): a stalled linter sub-process must be killed,
reported as an error with return code 124 (GNU timeout convention), and the
run must continue instead of hanging forever."""

import os
import signal
import subprocess
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

from megalinter import config
from megalinter.Linter import DEFAULT_LINTER_TIMEOUT_SECONDS, Linter


def build_linter(request_id, workspace="."):
    """Minimal Linter fixture: enough attributes for load_timeout_config()
    and execute_lint_command(), without a full MegaLinter orchestrator."""
    linter = Linter.__new__(Linter)
    linter.request_id = request_id
    linter.name = "REPOSITORY_CHECKOV"
    linter.descriptor_id = "REPOSITORY"
    linter.linter_name = "checkov"
    linter.is_formatter = False
    linter.workspace = workspace
    linter.lint_command_log = []
    linter.lint_cwd_log = None
    linter.common_linter_errors = []
    linter.can_output_sarif = False
    linter.output_sarif = False
    linter.sarif_output_file = None
    linter.sarif_default_output_file = None
    linter.unsecured_env_variables = []
    linter.timeout_seconds = None
    linter.timeout_config_var = None
    # Pre-computed env so execute_lint_command doesn't call config.build_env
    linter._cached_subprocess_env = {**os.environ, "FORCE_COLOR": "0"}
    return linter


class LinterTimeoutConfigTest(unittest.TestCase):
    def setUp(self):
        self.request_id = "test-linter-timeout-config"
        config.set_config(self.request_id, {})
        self.addCleanup(config.delete, self.request_id)

    def test_default_timeout_when_nothing_configured(self):
        linter = build_linter(self.request_id)
        linter.load_timeout_config()
        self.assertEqual(linter.timeout_seconds, DEFAULT_LINTER_TIMEOUT_SECONDS)
        self.assertEqual(linter.timeout_config_var, "LINTER_TIMEOUT_SECONDS (default)")

    def test_zero_disables_timeout_globally(self):
        config.set(self.request_id, "LINTER_TIMEOUT_SECONDS", "0")
        linter = build_linter(self.request_id)
        linter.load_timeout_config()
        self.assertIsNone(linter.timeout_seconds)
        self.assertEqual(linter.timeout_config_var, "LINTER_TIMEOUT_SECONDS")

    def test_zero_per_linter_wins_over_positive_global(self):
        config.set(self.request_id, "LINTER_TIMEOUT_SECONDS", "3600")
        config.set(self.request_id, "REPOSITORY_CHECKOV_TIMEOUT_SECONDS", "0")
        linter = build_linter(self.request_id)
        linter.load_timeout_config()
        self.assertIsNone(linter.timeout_seconds)
        self.assertEqual(
            linter.timeout_config_var, "REPOSITORY_CHECKOV_TIMEOUT_SECONDS"
        )

    def test_global_timeout_used_when_no_linter_value(self):
        config.set(self.request_id, "LINTER_TIMEOUT_SECONDS", "3600")
        linter = build_linter(self.request_id)
        linter.load_timeout_config()
        self.assertEqual(linter.timeout_seconds, 3600)
        self.assertEqual(linter.timeout_config_var, "LINTER_TIMEOUT_SECONDS")

    def test_linter_timeout_overrides_global(self):
        config.set(self.request_id, "LINTER_TIMEOUT_SECONDS", "3600")
        config.set(self.request_id, "REPOSITORY_CHECKOV_TIMEOUT_SECONDS", "600")
        linter = build_linter(self.request_id)
        linter.load_timeout_config()
        self.assertEqual(linter.timeout_seconds, 600)
        self.assertEqual(
            linter.timeout_config_var, "REPOSITORY_CHECKOV_TIMEOUT_SECONDS"
        )

    def test_invalid_timeout_value_logs_warning_and_falls_back_to_default(self):
        for invalid_value in ["abc", "-5", ""]:
            with self.subTest(invalid_value=invalid_value):
                config.set(
                    self.request_id,
                    "REPOSITORY_CHECKOV_TIMEOUT_SECONDS",
                    invalid_value,
                )
                linter = build_linter(self.request_id)
                with self.assertLogs(level="WARNING") as captured:
                    linter.load_timeout_config()
                self.assertEqual(linter.timeout_seconds, DEFAULT_LINTER_TIMEOUT_SECONDS)
                self.assertEqual(
                    linter.timeout_config_var, "LINTER_TIMEOUT_SECONDS (default)"
                )
                self.assertTrue(
                    any(
                        "REPOSITORY_CHECKOV_TIMEOUT_SECONDS" in line
                        for line in captured.output
                    )
                )
            config.delete(self.request_id, "REPOSITORY_CHECKOV_TIMEOUT_SECONDS")

    def test_invalid_linter_value_falls_back_to_valid_global(self):
        config.set(self.request_id, "REPOSITORY_CHECKOV_TIMEOUT_SECONDS", "abc")
        config.set(self.request_id, "LINTER_TIMEOUT_SECONDS", "120")
        linter = build_linter(self.request_id)
        with self.assertLogs(level="WARNING"):
            linter.load_timeout_config()
        self.assertEqual(linter.timeout_seconds, 120)
        self.assertEqual(linter.timeout_config_var, "LINTER_TIMEOUT_SECONDS")


class LinterTimeoutExecutionTest(unittest.TestCase):
    def setUp(self):
        self.request_id = "test-linter-timeout-exec"
        config.set_config(self.request_id, {})
        self.addCleanup(config.delete, self.request_id)

    def test_stalled_linter_is_killed_and_reported_as_error(self):
        # A command sleeping longer than the timeout must be killed close to
        # the timeout (not after the full sleep) and reported with return
        # code 124 and an actionable message including partial output
        linter = build_linter(self.request_id)
        linter.timeout_seconds = 1
        linter.timeout_config_var = "REPOSITORY_CHECKOV_TIMEOUT_SECONDS"
        command = [
            sys.executable,
            "-c",
            "import sys, time; print('partial-marker'); sys.stdout.flush(); "
            "time.sleep(20)",
        ]
        start = time.monotonic()
        return_code, return_stdout = linter.execute_lint_command(command)
        elapsed = time.monotonic() - start
        self.assertEqual(return_code, 124)
        self.assertLess(elapsed, 10, "process must be killed near the timeout")
        self.assertIn("Timed out after 1 seconds and was killed", return_stdout)
        self.assertIn("REPOSITORY_CHECKOV_TIMEOUT_SECONDS=1", return_stdout)
        self.assertIn("I/O stall", return_stdout)
        self.assertIn("partial-marker", return_stdout)

    def test_disabled_timeout_runs_subprocess_without_timeout(self):
        # Timeout disabled (explicit 0 -> timeout_seconds None) must keep the
        # historical subprocess.run call, without any timeout argument
        linter = build_linter(self.request_id)
        completed = MagicMock()
        completed.returncode = 0
        completed.stdout = b"all good"
        with (
            patch(
                "megalinter.Linter.subprocess.run", return_value=completed
            ) as run_mock,
            patch("megalinter.Linter.subprocess.Popen") as popen_mock,
        ):
            return_code, return_stdout = linter.execute_lint_command(
                [sys.executable, "-c", "print('all good')"]
            )
        self.assertEqual(return_code, 0)
        self.assertIn("all good", return_stdout)
        run_mock.assert_called_once()
        self.assertNotIn("timeout", run_mock.call_args.kwargs)
        popen_mock.assert_not_called()

    def test_fast_linter_is_not_impacted_by_timeout(self):
        linter = build_linter(self.request_id)
        linter.timeout_seconds = 60
        linter.timeout_config_var = "LINTER_TIMEOUT_SECONDS"
        return_code, return_stdout = linter.execute_lint_command(
            [sys.executable, "-c", "print('quick run ok')"]
        )
        self.assertEqual(return_code, 0)
        self.assertIn("quick run ok", return_stdout)

    def _fake_timed_out_process(self, second_communicate_result):
        fake_process = MagicMock()
        fake_process.pid = 4242
        fake_process.communicate.side_effect = [
            subprocess.TimeoutExpired(cmd="checkov", timeout=1),
            second_communicate_result,
        ]
        return fake_process

    def _run_timed_out_subprocess(self, linter, fake_process, os_name):
        with (
            patch("megalinter.Linter.os.name", os_name),
            patch(
                "megalinter.Linter.subprocess.Popen", return_value=fake_process
            ) as popen_mock,
            # create=True: os.killpg doesn't exist on Windows dev machines
            patch("megalinter.Linter.os.killpg", create=True) as killpg_mock,
        ):
            return_code, return_stdout = linter._run_lint_subprocess(
                ["checkov", "-d", "."], {"cwd": ".", "env": {}}
            )
        self.assertEqual(return_code, 124)
        return return_stdout, popen_mock, killpg_mock

    def test_posix_kills_whole_process_group(self):
        # On POSIX, the child must be started in its own process group
        # (start_new_session=True) and the whole group must be killed with
        # SIGKILL on timeout, so linter worker sub-processes can't survive
        linter = build_linter(self.request_id)
        linter.timeout_seconds = 1
        linter.timeout_config_var = "LINTER_TIMEOUT_SECONDS"
        fake_process = self._fake_timed_out_process(
            (b"partial output before kill", None)
        )
        return_stdout, popen_mock, killpg_mock = self._run_timed_out_subprocess(
            linter, fake_process, "posix"
        )
        self.assertTrue(popen_mock.call_args.kwargs.get("start_new_session"))
        # 9 == SIGKILL (signal.SIGKILL doesn't exist on Windows dev machines)
        killpg_mock.assert_called_once_with(4242, getattr(signal, "SIGKILL", 9))
        fake_process.kill.assert_not_called()
        self.assertIn("partial output before kill", return_stdout)
        self.assertIn("Timed out after 1 seconds and was killed", return_stdout)

    def test_non_posix_kills_direct_child_only(self):
        # Fallback outside POSIX: no process group, direct child kill only
        linter = build_linter(self.request_id)
        linter.timeout_seconds = 1
        fake_process = self._fake_timed_out_process((None, None))
        return_stdout, popen_mock, killpg_mock = self._run_timed_out_subprocess(
            linter, fake_process, "nt"
        )
        self.assertNotIn("start_new_session", popen_mock.call_args.kwargs)
        killpg_mock.assert_not_called()
        fake_process.kill.assert_called_once()
        self.assertIn("Timed out after 1 seconds and was killed", return_stdout)


if __name__ == "__main__":
    unittest.main()
