#!/usr/bin/env python3
import os
import tempfile
import unittest
from unittest.mock import patch

from megalinter.Linter import Linter


def build_linter(files):
    linter = Linter.__new__(Linter)
    linter.name = "MARKDOWN_MARKDOWNLINT"
    linter.linter_name = "markdownlint"
    linter.cli_lint_mode = "list_of_files"
    linter.files = files
    linter.native_toolchain = None
    linter.tips = []
    linter.lint_command_log = ["C:\\bin\\tool.cmd --fix a.md"]
    return linter


def many_files(count):
    return [f"docs/some/long/folder/name/file-number-{i}.md" for i in range(count)]


class LinterWindowsCommandLimitTest(unittest.TestCase):
    def warn(self, linter, command, executable, posix_launcher=None, platform="win32"):
        with (
            patch("megalinter.Linter.sys.platform", platform),
            patch("megalinter.Linter.shutil.which", return_value=executable),
            patch.object(linter, "find_posix_launcher", return_value=posix_launcher),
        ):
            linter.warn_on_windows_command_limit(command)
        return len(linter.tips)

    def test_short_command_has_no_tip(self):
        files = many_files(2)
        linter = build_linter(files)
        self.assertEqual(self.warn(linter, ["tool", *files], "C:\\tool.cmd"), 0)

    def test_other_platforms_have_no_tip(self):
        files = many_files(2000)
        linter = build_linter(files)
        self.assertEqual(
            self.warn(linter, ["tool", *files], "/usr/bin/tool", platform="linux"), 0
        )

    def test_cmd_launcher_with_posix_launcher_fits(self):
        files = many_files(500)
        linter = build_linter(files)
        self.assertEqual(
            self.warn(linter, ["tool", *files], "C:\\tool.cmd", "C:\\tool"), 0
        )

    def test_cmd_launcher_alone_is_over_the_limit(self):
        files = many_files(500)
        linter = build_linter(files)
        self.assertEqual(self.warn(linter, ["tool", *files], "C:\\tool.CMD"), 1)
        self.assertEqual(linter.tips[0]["category"], "windows_command_line")
        self.assertEqual(linter.cli_lint_mode, "list_of_files")

    def test_executable_under_the_process_limit_fits(self):
        files = many_files(500)
        linter = build_linter(files)
        self.assertEqual(self.warn(linter, ["tool", *files], "C:\\tool.exe"), 0)

    def test_above_the_process_limit_keeps_one_command(self):
        files = many_files(2000)
        linter = build_linter(files)
        command = ["tool", *files]
        self.assertEqual(self.warn(linter, command, "C:\\tool.cmd", "C:\\tool"), 1)
        self.assertEqual(command, ["tool", *files])
        self.assertEqual(linter.cli_lint_mode, "list_of_files")

    def test_short_command_does_not_read_the_launcher(self):
        files = many_files(2)
        linter = build_linter(files)
        with (
            patch("megalinter.Linter.sys.platform", "win32"),
            patch.object(linter, "find_posix_launcher") as find_launcher,
        ):
            linter.warn_on_windows_command_limit(["tool", *files])
        find_launcher.assert_not_called()

    def test_posix_launcher_must_be_a_readable_script(self):
        linter = build_linter([])
        with tempfile.TemporaryDirectory() as folder:
            launcher = os.path.join(folder, "tool")
            executable = launcher + ".cmd"
            with patch("megalinter.Linter.find_git_bash", return_value="bash"):
                self.assertIsNone(linter.find_posix_launcher(executable))
                with open(launcher, "wb") as file:
                    file.write(b"MZ binary")
                self.assertIsNone(linter.find_posix_launcher(executable))
                with open(launcher, "wb") as file:
                    file.write(b"#!/bin/sh\n")
                self.assertEqual(linter.find_posix_launcher(executable), launcher)
                with patch("builtins.open", side_effect=PermissionError):
                    self.assertIsNone(linter.find_posix_launcher(executable))
            with patch("megalinter.Linter.find_git_bash", return_value=None):
                self.assertIsNone(linter.find_posix_launcher(executable))

    def test_git_bash_receives_the_arguments_in_a_file(self):
        linter = build_linter([])
        received = {}

        def read_arguments(command, kwargs):
            with open(command[4], "r", encoding="utf-8", newline="") as file:
                received["arguments"] = file.read()
            received["command"] = command
            received["env"] = kwargs["env"]
            return 0, "ok"

        with (
            patch("megalinter.Linter.find_git_bash", return_value="bash"),
            patch.object(linter, "_run_lint_subprocess", side_effect=read_arguments),
        ):
            result = linter.run_through_git_bash(
                ["C:\\bin\\tool.cmd", "--fix", "a b.md", "c.md"],
                {"PATH": "x"},
                "C:\\workspace",
                "C:\\bin\\tool",
            )
        self.assertEqual(result, (0, "ok"))
        self.assertEqual(received["arguments"], "--fix\0a b.md\0c.md\0")
        self.assertIn('< "$1" && exec "$2"', received["command"][2])
        self.assertEqual(received["command"][5], "C:/bin/tool")
        self.assertEqual(received["env"]["MSYS_NO_PATHCONV"], "1")
        self.assertEqual(linter.lint_command_log[-1], "C:\\bin\\tool --fix a b.md c.md")
