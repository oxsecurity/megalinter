#!/usr/bin/env python3
# Tests of BlackLinter: the check runs without --diff (black only uses its cache
# without it), and the diff is computed afterwards for the files to reformat only
import unittest
from unittest.mock import patch

from megalinter.Linter import Linter
from megalinter.linters.BlackLinter import BlackLinter, merge_black_outputs

CHECK_FAILED_OUTPUT = (
    "would reformat /ws/src/b.py\n"
    "error: cannot parse for target version Python 3.15: /ws/src/c.py:1:4\n"
    "\nOh no! 💥 💔 💥\n"
    "1 file would be reformatted, 1 file would be left unchanged, "
    "1 file would fail to reformat.\n"
)
DIFF_OUTPUT = (
    "--- /ws/src/b.py\n+++ /ws/src/b.py\n@@ -1 +1 @@\n-x=1\n+x = 1\n"
    "would reformat /ws/src/b.py\n\nOh no! 💥 💔 💥\n1 file would be reformatted.\n"
)


def build_black_linter(cli_lint_mode="list_of_files", try_fix=False):
    linter = BlackLinter.__new__(BlackLinter)
    linter.cli_lint_mode = cli_lint_mode
    linter.files = ["src/a.py", "src/b.py", "src/c.py"]
    linter.cli_lint_mode_project_extra_args_after = ["."]
    linter.try_fix = try_fix
    return linter


def base_command(linter, file=None):
    options = ["black", "--diff", "--check", "--config", "pyproject.toml"]
    if file is not None:
        return [*options, file]
    if linter.cli_lint_mode == "list_of_files":
        return [*options, *linter.files]
    return [*options, "."]


class BlackLinterTest(unittest.TestCase):
    def build_command(self, linter, file=None):
        with patch.object(
            Linter, "build_lint_command", return_value=base_command(linter, file)
        ):
            return linter.build_lint_command(file)

    # Runs the check (failing with check_output) then the diff: returns the result
    # and the command line of the diff
    def run_check_then_diff(self, linter, command, check_output):
        with patch.object(
            Linter,
            "execute_lint_command",
            side_effect=[(1, check_output), (1, DIFF_OUTPUT)],
        ) as execute:
            result = linter.execute_lint_command(command)
        return result, execute.call_args_list[1].args[0]

    def test_check_runs_without_diff(self):
        linter = build_black_linter()
        command = self.build_command(linter)
        self.assertNotIn("--diff", command)
        self.assertIn("--check", command)
        self.assertEqual(linter.black_lint_targets, linter.files)

    def test_fix_mode_is_untouched(self):
        linter = build_black_linter(try_fix=True)
        with patch.object(
            Linter, "build_lint_command", return_value=["black", "--config", "x"]
        ):
            command = linter.build_lint_command()
        self.assertEqual(command, ["black", "--config", "x"])
        self.assertFalse(linter.black_diff_on_failure)

    def test_success_runs_once(self):
        linter = build_black_linter()
        command = self.build_command(linter)
        with patch.object(
            Linter, "execute_lint_command", return_value=(0, "All done!")
        ) as execute:
            self.assertEqual(linter.execute_lint_command(command), (0, "All done!"))
        execute.assert_called_once()

    def test_diff_only_for_files_to_reformat(self):
        linter = build_black_linter()
        command = self.build_command(linter)
        (return_code, stdout), diff_command = self.run_check_then_diff(
            linter, command, CHECK_FAILED_OUTPUT
        )
        self.assertEqual(
            diff_command,
            [
                "black",
                "--check",
                "--diff",
                "--config",
                "pyproject.toml",
                "/ws/src/b.py",
            ],
        )
        self.assertEqual(return_code, 1)
        self.assertIn("+x = 1", stdout)
        self.assertIn("error: cannot parse", stdout)
        self.assertIn("1 file would be left unchanged", stdout)
        self.assertNotIn("1 file would be reformatted.\n", stdout)
        self.assertEqual(stdout.count("would reformat /ws/src/b.py"), 1)

    def test_file_mode_target_is_replaced(self):
        linter = build_black_linter(cli_lint_mode="file")
        command = self.build_command(linter, "src/b.py")
        _result, diff_command = self.run_check_then_diff(
            linter, command, "would reformat /ws/src/b.py\n"
        )
        self.assertEqual(diff_command[-1], "/ws/src/b.py")
        self.assertNotIn("src/b.py", diff_command)

    def test_project_mode_target_is_replaced(self):
        linter = build_black_linter(cli_lint_mode="project")
        command = self.build_command(linter)
        self.assertEqual(linter.black_lint_targets, ["."])
        _result, diff_command = self.run_check_then_diff(
            linter, command, "would reformat /ws/src/b.py\n"
        )
        self.assertEqual(diff_command[-2:], ["pyproject.toml", "/ws/src/b.py"])
        self.assertNotIn(".", diff_command)

    def test_unknown_layout_reruns_whole_command_with_diff(self):
        linter = build_black_linter()
        with patch.object(
            Linter,
            "build_lint_command",
            return_value=["black", "--diff", "--check", "--config", "x", "extra"],
        ):
            command = linter.build_lint_command()
        self.assertIsNone(linter.black_lint_targets)
        _result, diff_command = self.run_check_then_diff(
            linter, command, CHECK_FAILED_OUTPUT
        )
        self.assertEqual(
            diff_command, ["black", "--check", "--diff", "--config", "x", "extra"]
        )

    def test_parse_errors_only_need_no_diff(self):
        linter = build_black_linter()
        command = self.build_command(linter)
        parse_error = "error: cannot parse for target version: /ws/src/c.py:1:4\n"
        with patch.object(
            Linter, "execute_lint_command", return_value=(123, parse_error)
        ) as execute:
            self.assertEqual(linter.execute_lint_command(command), (123, parse_error))
        execute.assert_called_once()

    def test_merge_keeps_check_summary(self):
        merged = merge_black_outputs(DIFF_OUTPUT, CHECK_FAILED_OUTPUT)
        self.assertTrue(merged.startswith("--- /ws/src/b.py"))
        self.assertTrue(merged.rstrip().endswith("1 file would fail to reformat."))


if __name__ == "__main__":
    unittest.main()
