#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from megalinter.Linter import Linter
from megalinter.native import long_command


def build_linter(files):
    linter = Linter.__new__(Linter)
    linter.name = "MARKDOWN_MARKDOWNLINT"
    linter.linter_name = "markdownlint"
    linter.cli_lint_mode = "list_of_files"
    linter.files = files
    linter.native_toolchain = None
    linter.tips = []
    linter.disable_errors = True
    linter.disable_errors_if_less_than = 5
    return linter


def many_files(count):
    return [f"docs/some/long/folder/name/file-number-{i}.md" for i in range(count)]


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as file:
        file.write(content)


NPM_LAUNCHER = b'#!/bin/sh\nif [ -x "$basedir/node" ]; then\n  exec "$basedir/node" "x.js" "$@"\nfi\n'


class LongCommandRouteTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.folder = self.temp_dir.name

    def python_tool(self, name, entry_point=True):
        venv = os.path.join(self.folder, "venv")
        write_file(os.path.join(venv, "pyvenv.cfg"), b"home = x\n")
        executable = os.path.join(venv, "Scripts", f"{name}.exe")
        write_file(executable, b"MZ")
        if entry_point:
            write_file(
                os.path.join(
                    venv, "Lib", "site-packages", "tool.dist-info", "entry_points.txt"
                ),
                f"[console_scripts]\n{name} = tool:main\n".encode(),
            )
        return executable

    def test_short_commands_are_direct(self):
        for executable in ("tool.cmd", "tool.exe"):
            self.assertEqual(
                long_command.find_route([executable, *many_files(2)]),
                long_command.ROUTE_DIRECT,
            )

    def test_executable_below_the_process_limit_is_direct(self):
        self.assertEqual(
            long_command.find_route(["tool.exe", *many_files(500)]),
            long_command.ROUTE_DIRECT,
        )

    def test_node_launcher_has_no_limit(self):
        executable = os.path.join(self.folder, "tool.cmd")
        write_file(os.path.join(self.folder, "tool"), NPM_LAUNCHER)
        self.assertEqual(
            long_command.find_route([executable, *many_files(5000)]),
            long_command.ROUTE_NODE,
        )

    def test_python_console_script_has_no_limit(self):
        executable = self.python_tool("black")
        self.assertEqual(
            long_command.find_route([executable, *many_files(5000)]),
            long_command.ROUTE_PYTHON,
        )

    def test_native_binary_in_a_venv_is_too_long(self):
        executable = self.python_tool("ruff", entry_point=False)
        self.assertEqual(
            long_command.find_route([executable, *many_files(5000)]),
            long_command.ROUTE_TOO_LONG,
        )

    def test_other_script_uses_git_bash_up_to_the_process_limit(self):
        executable = os.path.join(self.folder, "tool.cmd")
        write_file(
            os.path.join(self.folder, "tool"), b'#!/bin/sh\nexec java -jar x "$@"\n'
        )
        with patch.object(long_command, "find_git_bash", return_value="bash"):
            self.assertEqual(
                long_command.find_route([executable, *many_files(500)]),
                long_command.ROUTE_GIT_BASH,
            )
            self.assertEqual(
                long_command.find_route([executable, *many_files(2000)]),
                long_command.ROUTE_TOO_LONG,
            )
        with patch.object(long_command, "find_git_bash", return_value=None):
            self.assertEqual(
                long_command.find_route([executable, *many_files(500)]),
                long_command.ROUTE_TOO_LONG,
            )

    def test_unreadable_launcher_is_ignored(self):
        with patch("builtins.open", side_effect=PermissionError):
            self.assertEqual(long_command.read_posix_launcher("tool.cmd"), (None, None))

    def test_node_launch_keeps_existing_node_options(self):
        launch, env = long_command.build_launch(
            long_command.ROUTE_NODE,
            ["tool.cmd", "--fix", "a b.md"],
            {"NODE_OPTIONS": "--max-old-space-size=4096"},
            self.folder,
        )
        self.assertEqual(launch, ["tool.cmd"])
        self.assertTrue(env["NODE_OPTIONS"].startswith('--require "'))
        self.assertTrue(env["NODE_OPTIONS"].endswith("--max-old-space-size=4096"))
        self.assertEqual(env["MEGALINTER_NODE_OPTIONS"], "--max-old-space-size=4096")
        with open(
            env["MEGALINTER_ARGUMENTS_FILE"], encoding="utf-8", newline=""
        ) as file:
            self.assertEqual(file.read(), "--fix\0a b.md\0")

    def test_python_launch_reads_the_arguments_file(self):
        executable = self.python_tool("black")
        launch, _env = long_command.build_launch(
            long_command.ROUTE_PYTHON, [executable, "--check", "a.py"], {}, self.folder
        )
        self.assertEqual(os.path.basename(launch[0]), "python.exe")
        self.assertEqual(launch[1], "-c")
        self.assertEqual(launch[3:5], ["black", executable])
        with open(launch[5], encoding="utf-8", newline="") as file:
            self.assertEqual(file.read(), "--check\0a.py\0")

    def test_python_bootstrap_runs_the_entry_point(self):
        site_packages = os.path.join(self.folder, "site")
        write_file(
            os.path.join(site_packages, "demo_tool.py"),
            b"import sys\ndef main():\n    print(len(sys.argv) - 1, sys.argv[-1])\n",
        )
        write_file(
            os.path.join(site_packages, "demo_tool-1.0.dist-info", "METADATA"),
            b"Metadata-Version: 2.1\nName: demo-tool\nVersion: 1.0\n",
        )
        write_file(
            os.path.join(site_packages, "demo_tool-1.0.dist-info", "entry_points.txt"),
            b"[console_scripts]\ndemo-tool = demo_tool:main\n",
        )
        arguments_file = os.path.join(self.folder, "arguments")
        write_file(arguments_file, "a b.py\0é.py\0".encode())
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                long_command.PYTHON_BOOTSTRAP,
                "demo-tool",
                "demo-tool",
                arguments_file,
            ],
            env={**os.environ, "PYTHONPATH": site_packages, "PYTHONUTF8": "1"},
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "2 é.py")

    def test_git_bash_launch_stops_when_the_file_can_not_be_read(self):
        executable = os.path.join(self.folder, "tool.cmd")
        write_file(os.path.join(self.folder, "tool"), b"#!/bin/sh\n")
        with patch.object(long_command, "find_git_bash", return_value="bash"):
            launch, env = long_command.build_launch(
                long_command.ROUTE_GIT_BASH, [executable, "a.md"], {}, self.folder
            )
        self.assertIn('< "$1" && exec "$2"', launch[2])
        self.assertEqual(env["MSYS_NO_PATHCONV"], "1")


class LinterWindowsCommandLimitTest(unittest.TestCase):
    def check(self, linter, command, route, platform="win32"):
        with (
            patch("megalinter.Linter.sys.platform", platform),
            patch("megalinter.Linter.shutil.which", return_value=command[0]),
            patch.object(long_command, "find_route", return_value=route),
        ):
            linter.check_windows_command_limit(command)

    def test_linter_that_can_not_run_blocks_the_run(self):
        files = many_files(2000)
        linter = build_linter(files)
        self.check(linter, ["tool.exe", *files], long_command.ROUTE_TOO_LONG)
        self.assertEqual(linter.tips[0]["category"], "windows_command_line")
        self.assertFalse(linter.disable_errors)
        self.assertIsNone(linter.disable_errors_if_less_than)

    def test_linter_with_a_route_stays_non_blocking(self):
        files = many_files(2000)
        linter = build_linter(files)
        self.check(linter, ["tool.cmd", *files], long_command.ROUTE_NODE)
        self.assertEqual(linter.tips, [])
        self.assertTrue(linter.disable_errors)

    def test_other_platforms_are_not_checked(self):
        files = many_files(2000)
        linter = build_linter(files)
        self.check(linter, ["tool", *files], long_command.ROUTE_TOO_LONG, "linux")
        self.assertEqual(linter.tips, [])

    def run_long_command(self, return_code, output):
        files = many_files(2000)
        linter = build_linter(files)
        with (
            patch.object(
                long_command, "find_route", return_value=long_command.ROUTE_NODE
            ),
            patch.object(long_command, "build_launch", return_value=(["tool.cmd"], {})),
            patch.object(
                linter, "_run_lint_subprocess", return_value=(return_code, output)
            ),
        ):
            result = linter.run_windows_lint_subprocess(
                ["tool.cmd", *files], {}, "workspace"
            )
        self.assertEqual(result, (return_code, output))
        return linter

    def test_wrapped_program_that_can_not_start_blocks_the_run(self):
        for output in (
            "Error: spawnSync biome.exe ENAMETOOLONG",
            "CreateProcess error=206, The filename or extension is too long",
            "OSError: [WinError 206] Nom de fichier trop long",
            "bash: /c/tool: Argument list too long",
        ):
            linter = self.run_long_command(1, output)
            self.assertEqual(len(linter.tips), 1, output)
            self.assertFalse(linter.disable_errors)

    def test_lint_errors_stay_non_blocking(self):
        linter = self.run_long_command(1, "a.md:1 error MD025 Multiple headings")
        self.assertEqual(linter.tips, [])
        self.assertTrue(linter.disable_errors)
