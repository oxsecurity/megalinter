#!/usr/bin/env python3

import json
import os
import shutil
import tempfile
import types
import unittest
import uuid
from unittest import mock

from megalinter import Linter, Megalinter, config
from megalinter.linters.TyposLinter import TyposLinter
from megalinter.reporters.ApiReporter import ApiReporter


def build_typos_linter(
    request_id,
    workspace,
    report_folder,
    cli_lint_mode="list_of_files",
    apply_fixes=False,
    is_formatter=True,
):
    linter_config = {
        "descriptor_id": "SPELL",
        "descriptor_type": "other",
        "name": "SPELL_TYPOS",
        "linter_name": "typos",
        "linter_url": "https://github.com/crate-ci/typos",
        "is_formatter": is_formatter,
        "cli_lint_mode": cli_lint_mode,
        "supported_cli_lint_modes": ["file", "list_of_files", "project"],
        "cli_lint_extra_args": ["--format", "json"],
        "cli_lint_fix_arg_name": "--write-changes",
    }
    params = {
        "request_id": request_id,
        "default_linter_activation": True,
        "workspace": workspace,
        "github_workspace": workspace,
        "report_folder": report_folder,
        "post_linter_status": False,
        "apply_fixes": ["SPELL_TYPOS"] if apply_fixes else "none",
    }
    return TyposLinter(params, linter_config)


class TyposLinterTest(unittest.TestCase):
    def setUp(self):
        self.request_id = f"test-typos-{uuid.uuid4()}"
        config.set_config(self.request_id, {"REPORT_OUTPUT_FOLDER": "none"})
        self.addCleanup(config.delete, self.request_id)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.workspace = os.path.join(self.temp_dir.name, "workspace")
        self.report_folder = os.path.join(self.temp_dir.name, "report")
        os.makedirs(self.workspace, exist_ok=True)
        os.makedirs(self.report_folder, exist_ok=True)

    def test_get_total_number_errors_counts_typo_events(self):
        linter = build_typos_linter(self.request_id, self.workspace, self.report_folder)
        self.assertIsInstance(linter, Linter)
        ndjson = "\n".join(
            [
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./a.py",
                        "line_num": 1,
                        "byte_offset": 2,
                        "typo": "teh",
                        "corrections": ["the"],
                    }
                ),
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./b.md",
                        "line_num": 4,
                        "byte_offset": 10,
                        "typo": "recieve",
                        "corrections": ["receive"],
                    }
                ),
            ]
        )
        self.assertEqual(linter.get_total_number_errors(ndjson), 2)
        self.assertEqual(linter.get_total_number_errors(""), 0)

    def test_get_total_number_errors_ignores_non_typo_and_non_json_lines(self):
        linter = build_typos_linter(self.request_id, self.workspace, self.report_folder)
        mixed_output = "\n".join(
            [
                "",
                "   ",
                "warning: ignoring unreadable file foo.bin",
                "[1, 2, 3]",
                '"just a json string"',
                "42",
                "null",
                json.dumps({"type": "binary_file", "path": "./logo.png"}),
                json.dumps({"type": "other_event", "path": "./x.txt"}),
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./src/main.rs",
                        "line_num": 42,
                        "byte_offset": 15,
                        "typo": "retrive",
                        "corrections": ["retrieve"],
                    }
                ),
                "stderr: trailing non-json message",
            ]
        )
        self.assertEqual(linter.get_total_number_errors(mixed_output), 1)
        self.assertEqual(linter.get_total_number_errors(None), 0)
        self.assertEqual(linter.get_total_number_warnings(mixed_output), 0)

    def test_process_linter_populates_stdout_human_in_list_of_files_mode(self):
        linter = build_typos_linter(
            self.request_id,
            self.workspace,
            self.report_folder,
            cli_lint_mode="list_of_files",
        )
        linter.files = [os.path.join(self.workspace, "a.py")]
        ndjson = "\n".join(
            [
                "stderr warning: skipped hidden file",
                json.dumps({"type": "binary_file", "path": "./img.png"}),
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./a.py",
                        "line_num": 1,
                        "byte_offset": 4,
                        "typo": "teh",
                        "corrections": ["the"],
                    }
                ),
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./a.py",
                        "line_num": 3,
                        "byte_offset": 10,
                        "typo": "fo",
                        "corrections": ["for", "of"],
                    }
                ),
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./a.py",
                        "line_num": 8,
                        "byte_offset": 0,
                        "typo": "xyzzy",
                        "corrections": [],
                    }
                ),
            ]
        )
        with mock.patch.object(Linter, "process_linter", return_value=(2, ndjson)):
            rc, output = linter.process_linter()
        self.assertEqual(rc, 2)
        self.assertEqual(output, ndjson)
        self.assertEqual(
            linter.stdout_human,
            "\n".join(
                [
                    "./a.py:1:4: `teh` -> the",
                    "./a.py:3:10: `fo` -> for, of",
                    "./a.py:8:0: `xyzzy` -> (no suggestion)",
                ]
            ),
        )

        with mock.patch.object(Linter, "process_linter", return_value=(0, "")):
            rc_clean, _ = linter.process_linter()
        self.assertEqual(rc_clean, 0)
        self.assertIsNone(linter.stdout_human)

    def test_process_linter_accumulates_stdout_human_in_file_mode(self):
        linter = build_typos_linter(
            self.request_id,
            self.workspace,
            self.report_folder,
            cli_lint_mode="file",
        )
        file_one_ndjson = json.dumps(
            {
                "type": "typo",
                "path": "one.txt",
                "line_num": 1,
                "byte_offset": 0,
                "typo": "teh",
                "corrections": ["the"],
            }
        )
        file_three_ndjson = json.dumps(
            {
                "type": "typo",
                "path": "three.txt",
                "line_num": 2,
                "byte_offset": 5,
                "typo": "seperate",
                "corrections": ["separate"],
            }
        )
        with mock.patch.object(
            Linter,
            "process_linter",
            side_effect=[(2, file_one_ndjson), (0, ""), (2, file_three_ndjson)],
        ):
            rc1, _ = linter.process_linter("one.txt")
            rc2, _ = linter.process_linter("two.txt")
            rc3, _ = linter.process_linter("three.txt")

        self.assertEqual((rc1, rc2, rc3), (2, 0, 2))
        self.assertEqual(
            linter.stdout_human,
            "one.txt:1:0: `teh` -> the\nthree.txt:2:5: `seperate` -> separate",
        )

    def test_apply_fixes_exit_code_handling(self):
        linter_fix = build_typos_linter(
            self.request_id,
            self.workspace,
            self.report_folder,
            cli_lint_mode="list_of_files",
            apply_fixes=True,
        )
        with mock.patch.object(Linter, "process_linter", return_value=(0, "")):
            rc, _ = linter_fix.process_linter()
        self.assertEqual(rc, 0)
        self.assertIsNone(linter_fix.stdout_human)

        with mock.patch.object(
            Linter,
            "process_linter",
            return_value=(2, json.dumps({"type": "binary_file", "path": "./bin.dat"})),
        ):
            rc, _ = linter_fix.process_linter()
        self.assertEqual(rc, 2)
        self.assertIsNone(linter_fix.stdout_human)

        remaining_ndjson = json.dumps(
            {
                "type": "typo",
                "path": "./ambiguous.txt",
                "line_num": 1,
                "byte_offset": 0,
                "typo": "fo",
                "corrections": ["for", "of"],
            }
        )
        with mock.patch.object(
            Linter, "process_linter", return_value=(2, remaining_ndjson)
        ):
            rc, _ = linter_fix.process_linter()
        self.assertEqual(rc, 2)
        self.assertEqual(
            linter_fix.stdout_human, "./ambiguous.txt:1:0: `fo` -> for, of"
        )

        linter_no_fix = build_typos_linter(
            self.request_id,
            self.workspace,
            self.report_folder,
            cli_lint_mode="list_of_files",
            apply_fixes=False,
        )
        with mock.patch.object(
            Linter, "process_linter", return_value=(2, "fatal: bad config")
        ):
            rc, _ = linter_no_fix.process_linter()
        self.assertEqual(rc, 2)

    def _build_api_reporter(self, linter):
        master = types.SimpleNamespace(
            request_id=self.request_id,
            linters=[linter],
            show_elapsed_time=False,
            github_workspace=self.workspace,
            status=linter.status,
            return_code=linter.return_code,
        )
        reporter = ApiReporter.__new__(ApiReporter)
        reporter.master = master
        reporter.report_folder = self.report_folder
        reporter.is_active = True
        reporter.init_time = 0
        reporter.payload = {"linters": []}
        reporter.providers = []
        return reporter

    def _configure_reporters(self, formatters_disable_errors=None):
        reporter_config = {
            "REPORT_OUTPUT_FOLDER": self.report_folder,
            "TEXT_REPORTER": "true",
            "CONSOLE_REPORTER": "true",
        }
        if formatters_disable_errors is not None:
            reporter_config["FORMATTERS_DISABLE_ERRORS"] = formatters_disable_errors
        config.set_config(self.request_id, reporter_config)

    def _assert_reporter_outputs(
        self,
        linter,
        expected_human,
        expected_status,
        expected_return_code,
        expected_errors,
        expected_file_results_count,
    ):
        self.assertEqual(linter.status, expected_status)
        self.assertEqual(linter.return_code, expected_return_code)
        self.assertEqual(linter.total_number_errors, expected_errors)
        self.assertEqual(linter.total_number_warnings, 0)
        self.assertEqual(linter.stdout_human, expected_human)
        self.assertEqual(len(linter.files_lint_results), expected_file_results_count)

        text_log = os.path.join(
            self.report_folder,
            "linters_logs",
            f"SPELL_TYPOS-{expected_status.upper()}.log",
        )
        with open(text_log, "r", encoding="utf-8") as handle:
            text_content = handle.read()
        for line in expected_human.splitlines():
            self.assertIn(line, text_content)
        self.assertNotIn('"type":"typo"', text_content)
        self.assertNotIn('"type": "typo"', text_content)

        api_reporter = self._build_api_reporter(linter)
        api_reporter.build_payload()
        api_data = api_reporter.payload["linters"][0]["data"]
        self.assertEqual(api_data["numberErrorsFound"], expected_errors)
        self.assertEqual(api_data["output"], expected_human)

    def test_run_list_of_files_with_reporters(self):
        ndjson = "\n".join(
            [
                json.dumps({"type": "binary_file", "path": "./bin.dat"}),
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./a.py",
                        "line_num": 1,
                        "byte_offset": 2,
                        "typo": "teh",
                        "corrections": ["the"],
                    }
                ),
                json.dumps(
                    {
                        "type": "typo",
                        "path": "./a.py",
                        "line_num": 5,
                        "byte_offset": 0,
                        "typo": "recieve",
                        "corrections": ["receive"],
                    }
                ),
            ]
        )
        expected_human = "./a.py:1:2: `teh` -> the\n./a.py:5:0: `recieve` -> receive"
        file_a = os.path.join(self.workspace, "a.py")

        for formatters_disable_errors, expected_status, expected_rc in [
            (None, "warning", 0),
            ("false", "error", 1),
        ]:
            with self.subTest(formatters_disable_errors=formatters_disable_errors):
                self._configure_reporters(formatters_disable_errors)
                linter = build_typos_linter(
                    self.request_id,
                    self.workspace,
                    self.report_folder,
                    cli_lint_mode="list_of_files",
                )
                linter.files = [file_a]
                with mock.patch.object(
                    linter, "_run_lint_subprocess", return_value=(2, ndjson)
                ):
                    with self.assertLogs(level="INFO") as captured_logs:
                        linter.run()

                self.assertEqual(linter.stdout, ndjson)
                self.assertIn(expected_human, "\n".join(captured_logs.output))
                self._assert_reporter_outputs(
                    linter=linter,
                    expected_human=expected_human,
                    expected_status=expected_status,
                    expected_return_code=expected_rc,
                    expected_errors=2,
                    expected_file_results_count=1,
                )

    def test_run_file_mode_with_reporters(self):
        good_file = os.path.join(self.workspace, "good.txt")
        bad_file = os.path.join(self.workspace, "bad.txt")
        bad_ndjson = "\n".join(
            [
                json.dumps(
                    {
                        "type": "typo",
                        "path": bad_file,
                        "line_num": 1,
                        "byte_offset": 0,
                        "typo": "teh",
                        "corrections": ["the"],
                    }
                ),
                json.dumps(
                    {
                        "type": "typo",
                        "path": bad_file,
                        "line_num": 2,
                        "byte_offset": 4,
                        "typo": "seperate",
                        "corrections": ["separate"],
                    }
                ),
            ]
        )
        expected_human = (
            f"{bad_file}:1:0: `teh` -> the\n{bad_file}:2:4: `seperate` -> separate"
        )

        for formatters_disable_errors, expected_status, expected_rc in [
            (None, "warning", 0),
            ("false", "error", 1),
        ]:
            with self.subTest(formatters_disable_errors=formatters_disable_errors):
                self._configure_reporters(formatters_disable_errors)
                linter = build_typos_linter(
                    self.request_id,
                    self.workspace,
                    self.report_folder,
                    cli_lint_mode="file",
                )
                linter.files = [good_file, bad_file]
                with mock.patch.object(
                    linter,
                    "_run_lint_subprocess",
                    side_effect=[(0, ""), (2, bad_ndjson)],
                ):
                    linter.run()

                self.assertEqual(linter.files_lint_results[0]["status_code"], 0)
                self.assertEqual(linter.files_lint_results[1]["errors_number"], 2)
                self.assertEqual(linter.files_lint_results[1]["stdout"], expected_human)
                self._assert_reporter_outputs(
                    linter=linter,
                    expected_human=expected_human,
                    expected_status=expected_status,
                    expected_return_code=expected_rc,
                    expected_errors=2,
                    expected_file_results_count=2,
                )

    def test_run_project_mode_clean_and_failing(self):
        linter_clean = build_typos_linter(
            self.request_id,
            self.workspace,
            self.report_folder,
            cli_lint_mode="project",
        )
        with mock.patch.object(
            linter_clean, "_run_lint_subprocess", return_value=(0, "")
        ):
            linter_clean.run()
        self.assertEqual(linter_clean.status, "success")
        self.assertEqual(linter_clean.return_code, 0)
        self.assertEqual(linter_clean.total_number_errors, 0)
        self.assertIsNone(linter_clean.stdout_human)

        ndjson = json.dumps(
            {
                "type": "typo",
                "path": "./README.md",
                "line_num": 10,
                "byte_offset": 3,
                "typo": "adress",
                "corrections": ["address"],
            }
        )
        for formatters_disable_errors, expected_status, expected_rc in [
            (None, "warning", 0),
            ("false", "error", 1),
        ]:
            with self.subTest(formatters_disable_errors=formatters_disable_errors):
                cfg = {"REPORT_OUTPUT_FOLDER": "none"}
                if formatters_disable_errors is not None:
                    cfg["FORMATTERS_DISABLE_ERRORS"] = formatters_disable_errors
                config.set_config(self.request_id, cfg)
                linter_fail = build_typos_linter(
                    self.request_id,
                    self.workspace,
                    self.report_folder,
                    cli_lint_mode="project",
                )
                with mock.patch.object(
                    linter_fail, "_run_lint_subprocess", return_value=(2, ndjson)
                ):
                    linter_fail.run()
                self.assertEqual(linter_fail.status, expected_status)
                self.assertEqual(linter_fail.return_code, expected_rc)
                self.assertEqual(linter_fail.total_number_errors, 1)
                self.assertEqual(
                    linter_fail.stdout_human, "./README.md:10:3: `adress` -> address"
                )

    def test_pre_test_sets_file_extensions(self):
        linter = build_typos_linter(
            self.request_id,
            self.workspace,
            self.report_folder,
        )
        linter.pre_test("test_success_list_of_files_lint_mode")
        self.assertEqual(
            config.get_list(self.request_id, "SPELL_TYPOS_FILE_EXTENSIONS", []),
            [".md", ".py", ".txt"],
        )

    def test_apply_fixes_all_end_to_end(self):
        if shutil.which("typos") is None:
            self.skipTest("typos binary not available on PATH")

        target_file = os.path.join(self.workspace, "guide.md")
        with open(target_file, "w", encoding="utf-8") as handle:
            handle.write(
                "Follow teh checklist to recieve updates in a seperate environment.\n"
            )

        e2e_request_id = f"test-typos-e2e-{uuid.uuid4()}"
        self.addCleanup(
            lambda: (
                config.delete(e2e_request_id)
                if config.is_initialized_for(e2e_request_id)
                else None
            )
        )
        config.init_config(
            e2e_request_id,
            self.workspace,
            {
                "DEFAULT_WORKSPACE": self.workspace,
                "GITHUB_WORKSPACE": self.workspace,
                "ENABLE_LINTERS": "SPELL_TYPOS",
                "APPLY_FIXES": "all",
                "SPELL_TYPOS_FILE_EXTENSIONS": [".md"],
                "PARALLEL": "false",
                "IGNORE_GITIGNORED_FILES": "false",
                "VALIDATE_ALL_CODEBASE": "true",
                "REPORT_OUTPUT_FOLDER": "none",
                "TEXT_REPORTER": "false",
                "CONSOLE_REPORTER": "false",
                "GITHUB_COMMENT_REPORTER": "false",
                "GITHUB_STATUS_REPORTER": "false",
                "CONFIG_REPORTER": "false",
                "API_REPORTER": "false",
                "SARIF_REPORTER": "false",
                "UPDATED_SOURCES_REPORTER": "false",
                "FLAVOR_SUGGESTIONS": "false",
            },
        )
        mega_linter = Megalinter(
            {"request_id": e2e_request_id, "workspace": self.workspace}
        )
        mega_linter.run()

        self.assertEqual(mega_linter.return_code, 0)
        active_linters = [
            linter for linter in mega_linter.linters if linter.is_active is True
        ]
        self.assertEqual([linter.name for linter in active_linters], ["SPELL_TYPOS"])
        with open(target_file, "r", encoding="utf-8") as handle:
            self.assertEqual(
                handle.read(),
                "Follow the checklist to receive updates in a separate environment.\n",
            )
