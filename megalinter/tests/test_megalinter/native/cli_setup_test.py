import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import yaml

from megalinter import cli
from megalinter.native.context import NativeError

SUGGESTION = {
    "variable": "NATIVE_LINTERS",
    "operation": "set",
    "values": ["PYTHON_BLACK", "MARKDOWN_MARKDOWNLINT"],
    "safe": False,
    "reason": "fast linters",
    "details": [
        {
            "key": "PYTHON_BLACK",
            "recommended": True,
            "reason": "fast linter (speed 5/5)",
        },
        {
            "key": "MARKDOWN_MARKDOWNLINT",
            "recommended": True,
            "reason": "fast linter (speed 4/5)",
        },
        {
            "key": "SPELL_CSPELL",
            "recommended": False,
            "reason": "slow linter (speed 2/5)",
        },
    ],
}
KNOWN = ["PYTHON_BLACK", "MARKDOWN_MARKDOWNLINT", "SPELL_CSPELL", "YAML_YAMLLINT"]


def arguments(**extra):
    values = {"linters": None, "no_run": False, "input": None, "runtimes": None}
    values.update(extra)
    return SimpleNamespace(**values)


class SetupTest(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.config_file = os.path.join(self.workspace.name, ".mega-linter.yml")
        self.suggestions = [SUGGESTION]
        self.installed = []
        self.runs = []
        patches = [
            patch.object(cli, "prepare_environment", lambda _: self.workspace.name),
            patch.object(cli, "run_native_prerun", self.fake_prerun),
            patch.object(
                cli,
                "load_native_specs",
                lambda: [SimpleNamespace(key=key) for key in KNOWN],
            ),
            patch.object(
                cli,
                "install_explicit_linters",
                lambda args: self.installed.append(list(args.linters)),
            ),
            patch.object(cli, "command_run", lambda args: self.runs.append(args) or 0),
        ]
        for started in patches:
            started.start()
            self.addCleanup(started.stop)

    def fake_prerun(self):
        return SimpleNamespace(prerun_report={"suggestions": self.suggestions})

    def written(self):
        if not os.path.isfile(self.config_file):
            return None
        with open(self.config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def test_linters_option_writes_installs_and_runs(self):
        status = cli.command_setup(arguments(linters="python_black, SPELL_CSPELL"))
        self.assertEqual(status, 0)
        self.assertEqual(
            self.written(), {"NATIVE_LINTERS": ["PYTHON_BLACK", "SPELL_CSPELL"]}
        )
        self.assertEqual(self.installed, [["PYTHON_BLACK", "SPELL_CSPELL"]])
        self.assertEqual(len(self.runs), 1)

    def test_no_run_only_installs(self):
        cli.command_setup(arguments(linters="PYTHON_BLACK", no_run=True))
        self.assertEqual(self.installed, [["PYTHON_BLACK"]])
        self.assertEqual(self.runs, [])

    def test_unknown_linter_writes_nothing(self):
        with self.assertRaises(NativeError) as error:
            cli.command_setup(arguments(linters="PYTHON_NOPE"))
        self.assertIn("PYTHON_NOPE", str(error.exception))
        with self.assertRaises(NativeError):
            cli.command_setup(arguments(linters="all"))
        self.assertIsNone(self.written())
        self.assertEqual(self.installed, [])

    def test_without_a_terminal_the_suggestion_is_shown_and_nothing_is_written(self):
        with patch.object(cli.sys.stdin, "isatty", return_value=False):
            with self.assertRaises(NativeError) as error:
                cli.command_setup(arguments())
        self.assertIn(
            "--linters PYTHON_BLACK,MARKDOWN_MARKDOWNLINT", str(error.exception)
        )
        self.assertIsNone(self.written())
        self.assertEqual(self.installed, [])
        self.assertEqual(self.runs, [])

    def test_terminal_accepts_the_suggestion(self):
        with patch.object(cli.sys.stdin, "isatty", return_value=True):
            with patch("builtins.input", return_value=""):
                cli.command_setup(arguments())
        self.assertEqual(
            self.written(),
            {"NATIVE_LINTERS": ["PYTHON_BLACK", "MARKDOWN_MARKDOWNLINT"]},
        )
        self.assertEqual(self.installed, [["PYTHON_BLACK", "MARKDOWN_MARKDOWNLINT"]])

    def test_terminal_edits_the_list(self):
        answers = iter(["e", "yaml_yamllint, python_black"])
        with patch.object(cli.sys.stdin, "isatty", return_value=True):
            with patch("builtins.input", lambda _: next(answers)):
                cli.command_setup(arguments())
        self.assertEqual(
            self.written(), {"NATIVE_LINTERS": ["YAML_YAMLLINT", "PYTHON_BLACK"]}
        )

    def test_terminal_refusal_writes_nothing(self):
        with patch.object(cli.sys.stdin, "isatty", return_value=True):
            with patch("builtins.input", return_value="n"):
                with self.assertRaises(NativeError):
                    cli.command_setup(arguments())
        self.assertIsNone(self.written())
        self.assertEqual(self.installed, [])

    def test_no_answer_cancels_the_setup(self):
        def no_input(_):
            raise EOFError

        with patch.object(cli.sys.stdin, "isatty", return_value=True):
            with patch("builtins.input", no_input):
                with self.assertRaises(NativeError):
                    cli.command_setup(arguments())
        self.assertIsNone(self.written())

    def test_configured_linters_are_kept_when_nothing_better_is_suggested(self):
        with open(self.config_file, "w", encoding="utf-8") as file:
            file.write("NATIVE_LINTERS:\n  - PYTHON_BLACK\n")
        self.suggestions = []
        cli.command_setup(arguments())
        self.assertEqual(self.installed, [["PYTHON_BLACK"]])
        with open(self.config_file, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), "NATIVE_LINTERS:\n  - PYTHON_BLACK\n")
        self.assertEqual(len(self.runs), 1)

    def test_nothing_can_run_natively(self):
        self.suggestions = []
        with self.assertRaises(NativeError) as error:
            cli.command_setup(arguments())
        self.assertIn("Docker", str(error.exception))
        self.assertIsNone(self.written())
        self.assertEqual(self.installed, [])

    def test_other_settings_of_the_configuration_are_kept(self):
        with open(self.config_file, "w", encoding="utf-8") as file:
            file.write("APPLY_FIXES: all\n")
        cli.command_setup(arguments(linters="PYTHON_BLACK", no_run=True))
        self.assertEqual(
            self.written(), {"APPLY_FIXES": "all", "NATIVE_LINTERS": ["PYTHON_BLACK"]}
        )


class ParserTest(unittest.TestCase):
    def test_new_commands_and_report_options(self):
        parser = cli.build_parser()
        run = parser.parse_args(["run", "--json", "--sarif"])
        self.assertTrue(run.json and run.sarif)
        self.assertFalse(parser.parse_args(["run"]).json)
        setup = parser.parse_args(["setup", "--linters", "A,B", "--no-run", "--json"])
        self.assertEqual((setup.linters, setup.no_run, setup.json), ("A,B", True, True))
        self.assertEqual(parser.parse_args(["prerun"]).command, "prerun")

    def test_report_options_set_the_reporters(self):
        with patch.dict(os.environ, {}, clear=False):
            for name in ("JSON_REPORTER", "SARIF_REPORTER"):
                os.environ.pop(name, None)
            with patch.dict(os.environ, {"MEGALINTER_NATIVE": ""}):
                with patch.object(cli.config, "refresh_env_snapshot"):
                    cli.prepare_environment(
                        SimpleNamespace(input=None, json=True, sarif=True)
                    )
                    self.assertEqual(os.environ["JSON_REPORTER"], "true")
                    self.assertEqual(os.environ["SARIF_REPORTER"], "true")
                    for name in (
                        "JSON_REPORTER",
                        "SARIF_REPORTER",
                        "DEFAULT_WORKSPACE",
                    ):
                        os.environ.pop(name, None)


if __name__ == "__main__":
    unittest.main()
