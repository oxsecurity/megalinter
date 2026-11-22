#!/usr/bin/env python3
import os
import tempfile
import unittest
from unittest.mock import patch

from megalinter.Linter import Linter


def build_linter(files, modes=("list_of_files", "project")):
    linter = Linter.__new__(Linter)
    linter.name = "MARKDOWN_MARKDOWNLINT"
    linter.linter_name = "markdownlint"
    linter.cli_lint_mode = "list_of_files"
    linter.supported_cli_lint_modes = list(modes)
    linter.files = files
    linter.native_toolchain = None
    return linter


def many_files(count):
    return [f"docs/some/long/folder/name/file-number-{i}.md" for i in range(count)]


class LinterWindowsCommandLimitTest(unittest.TestCase):
    def fit(self, linter, command, executable, posix_launcher=None, platform="win32"):
        project_command = ["tool", "."]
        with (
            patch("megalinter.Linter.sys.platform", platform),
            patch("megalinter.Linter.shutil.which", return_value=executable),
            patch.object(linter, "find_posix_launcher", return_value=posix_launcher),
            patch.object(linter, "build_lint_command", return_value=project_command),
        ):
            return linter.fit_command_in_windows_limit(command)

    def test_short_command_is_unchanged(self):
        files = many_files(2)
        linter = build_linter(files)
        command = ["tool", *files]
        self.assertEqual(self.fit(linter, command, "C:\\tool.cmd"), command)
        self.assertEqual(linter.cli_lint_mode, "list_of_files")

    def test_other_platforms_are_unchanged(self):
        files = many_files(2000)
        linter = build_linter(files)
        command = ["tool", *files]
        self.assertEqual(
            self.fit(linter, command, "/usr/bin/tool", platform="linux"), command
        )
        self.assertEqual(linter.cli_lint_mode, "list_of_files")

    def test_cmd_launcher_with_posix_launcher_keeps_the_files(self):
        files = many_files(500)
        linter = build_linter(files)
        command = ["tool", *files]
        self.assertEqual(self.fit(linter, command, "C:\\tool.cmd", "C:\\tool"), command)
        self.assertEqual(linter.cli_lint_mode, "list_of_files")

    def test_cmd_launcher_alone_switches_to_project_mode(self):
        files = many_files(500)
        linter = build_linter(files)
        self.assertEqual(
            self.fit(linter, ["tool", *files], "C:\\tool.CMD"), ["tool", "."]
        )
        self.assertEqual(linter.cli_lint_mode, "project")

    def test_executable_under_the_process_limit_keeps_the_files(self):
        files = many_files(500)
        linter = build_linter(files)
        command = ["tool", *files]
        self.assertEqual(self.fit(linter, command, "C:\\tool.exe"), command)
        self.assertEqual(linter.cli_lint_mode, "list_of_files")

    def test_above_the_process_limit_switches_to_project_mode(self):
        files = many_files(2000)
        linter = build_linter(files)
        self.assertEqual(
            self.fit(linter, ["tool", *files], "C:\\tool.cmd", "C:\\tool"),
            ["tool", "."],
        )
        self.assertEqual(linter.cli_lint_mode, "project")

    def test_without_project_mode_the_command_is_kept(self):
        files = many_files(2000)
        linter = build_linter(files, modes=("file", "list_of_files"))
        command = ["tool", *files]
        self.assertEqual(self.fit(linter, command, "C:\\tool.exe"), command)
        self.assertEqual(linter.cli_lint_mode, "list_of_files")

    def test_posix_launcher_must_be_a_script(self):
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
        self.assertEqual(received["command"][5], "C:/bin/tool")
        self.assertEqual(received["env"]["MSYS_NO_PATHCONV"], "1")
