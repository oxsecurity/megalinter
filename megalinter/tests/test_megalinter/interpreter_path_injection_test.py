#!/usr/bin/env python3
"""
Unit tests: the name of a scanned file must never be
written in the R / PowerShell script built by the R, PowerShell and ARM
linters, otherwise a quote in the name runs as interpreter code.
"""

import os
import sys
import tempfile
import unittest
import uuid
from unittest import mock

from megalinter import config, linter_factory, utils
from megalinter.linters.PhpCsFixerLinter import _php_single_quoted

HOSTILE_NAMES = [
    "a'); system('id'); #.R",
    "x'; Start-Process calc; '.ps1",
    "x’; Start-Process calc; ‘.ps1",
    "x‛; Start-Process calc; ′.ps1",
    "$(id).json",
    "a b;c.json",
]

LINTERS = [
    ("R", "lintr"),
    ("POWERSHELL", "powershell"),
    ("POWERSHELL", "powershell_formatter"),
    ("ARM", "arm-ttk"),
]


def _build_linter(request_id, workspace, descriptor_id, linter_name):
    params = {
        "default_linter_activation": True,
        "enable_descriptors": [],
        "enable_linters": [],
        "disable_descriptors": [],
        "disable_linters": [],
        "disable_errors_linters": [],
        "github_workspace": workspace,
        "workspace": workspace,
        "linter_rules_path": workspace,
        "default_rules_location": utils.get_default_rules_location(),
        "post_linter_status": False,
        "request_id": request_id,
    }
    return linter_factory.build_linter(descriptor_id, linter_name, params)


def _script_of(cmd):
    return cmd[-1]


class InterpreterPathInjectionTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        self.workspace = tempfile.mkdtemp()
        config.set_config(self.request_id, {"default_workspace": self.workspace})

    def tearDown(self):
        config.delete(self.request_id)

    def _linter(self, descriptor_id, linter_name):
        return _build_linter(
            self.request_id, self.workspace, descriptor_id, linter_name
        )

    def test_file_name_is_not_written_in_script(self):
        for descriptor_id, linter_name in LINTERS:
            for name in HOSTILE_NAMES:
                with self.subTest(linter=linter_name, name=name):
                    linter = self._linter(descriptor_id, linter_name)
                    cmd = linter.build_lint_command(os.path.join("sub", name))
                    script = _script_of(cmd)
                    self.assertNotIn(name, script)
                    self.assertNotIn("Start-Process", script)
                    self.assertNotIn("system(", script)
                    self.assertIn(
                        name,
                        "".join(linter.lint_command_env.values()),
                    )

    def test_formatter_fix_mode_does_not_write_name_in_script(self):
        name = HOSTILE_NAMES[1]
        linter = self._linter("POWERSHELL", "powershell_formatter")
        linter.apply_fixes = True
        script = _script_of(linter.build_lint_command(name))
        self.assertNotIn(name, script)
        self.assertIn("Out-File -LiteralPath $env:MEGALINTER_LINT_FILE", script)
        self.assertEqual(linter.lint_command_env["MEGALINTER_LINT_FILE"], name)

    def test_invalid_formatter_encoding_falls_back_to_utf8(self):
        config.set_value(
            self.request_id,
            "POWERSHELL_POWERSHELL_FORMATTER_OUTPUT_ENCODING",
            "utf8; Start-Process calc",
        )
        linter = self._linter("POWERSHELL", "powershell_formatter")
        linter.apply_fixes = True
        with self.assertLogs(level="WARNING"):
            script = _script_of(linter.build_lint_command("a.ps1"))
        self.assertNotIn("Start-Process", script)
        self.assertIn("-Encoding utf8 ", script)

    def test_config_file_is_not_written_in_script(self):
        hostile_config = "/tmp/it's'; Start-Process calc; '.psd1"
        for descriptor_id, linter_name in LINTERS:
            with self.subTest(linter=linter_name):
                linter = self._linter(descriptor_id, linter_name)
                linter.config_file = hostile_config
                script = _script_of(linter.build_lint_command("a.file"))
                self.assertNotIn(hostile_config, script)
                self.assertEqual(
                    linter.lint_command_env["MEGALINTER_LINT_CONFIG_FILE"],
                    hostile_config,
                )

    def test_files_with_control_characters_are_skipped(self):
        for descriptor_id, linter_name in LINTERS:
            with self.subTest(linter=linter_name):
                linter = self._linter(descriptor_id, linter_name)
                linter.files = ["ok.file", "it's.file", "x’.file", "bad\nname"]
                with self.assertLogs(level="WARNING") as logs:
                    linter.drop_files_unsafe_for_interpreter()
                self.assertEqual(linter.files, ["ok.file", "it's.file", "x’.file"])
                self.assertEqual(linter.files_number, 3)
                self.assertEqual(len(logs.output), 1)

    def test_lint_command_env_reaches_the_subprocess(self):
        linter = self._linter("R", "lintr")
        linter._cached_subprocess_env = {"FORCE_COLOR": "0"}
        linter.lint_command_env = {"MEGALINTER_LINT_FILE_NAME": "it's.R"}
        with mock.patch.object(
            linter, "_run_lint_subprocess", return_value=(0, "")
        ) as run:
            linter.execute_lint_command([sys.executable, "-V"])
        env = run.call_args[0][1]["env"]
        self.assertEqual(env["MEGALINTER_LINT_FILE_NAME"], "it's.R")
        self.assertNotIn("MEGALINTER_LINT_FILE_NAME", linter._cached_subprocess_env)


class PhpCsFixerQuotingTest(unittest.TestCase):
    def test_php_single_quoted_escapes_quotes_and_backslashes(self):
        self.assertEqual(
            _php_single_quoted("x');system('id');//"), "'x\\');system(\\'id\\');//'"
        )
        self.assertEqual(_php_single_quoted("a\\"), "'a\\\\'")


if __name__ == "__main__":
    unittest.main()
