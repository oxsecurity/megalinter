import json
import os
import tempfile
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from megalinter import config
from megalinter.native import suggest


class FakeInstaller:
    statuses = {}

    def __init__(self, request_id=None):
        self.request_id = request_id

    def status(self, spec):
        return self.statuses.get(spec, ("installed", None))


def fake_linter(key, speed=3, mode="list_of_files", executable="tool"):
    return SimpleNamespace(
        name=key,
        linter_speed=speed,
        cli_lint_mode=mode,
        cli_executable=[executable],
        is_formatter=False,
    )


@patch("megalinter.native.suggest.NativeInstaller", FakeInstaller)
@patch("megalinter.native.suggest.spec_from_linter", lambda linter: linter.name)
class SuggestTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        FakeInstaller.statuses = {}
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.addCleanup(config.delete, self.request_id)

    def master(self, linters, native_linters=None):
        config.set_config(self.request_id, {"NATIVE_LINTERS": native_linters or []})
        return SimpleNamespace(
            request_id=self.request_id,
            active_linters=linters,
            report_folder=self.folder.name,
        )

    def write_report(self, linters, sub_folder=None, first_run=()):
        folder = self.folder.name
        if sub_folder is not None:
            folder = os.path.join(folder, sub_folder)
            os.makedirs(folder)
        with open(
            os.path.join(folder, suggest.JSON_REPORT_FILE_NAME), "w", encoding="utf-8"
        ) as report_file:
            json.dump(
                {
                    "linters": [
                        {
                            "name": name,
                            "elapsed_time_s": seconds,
                            **({"native_first_run": True} if name in first_run else {}),
                        }
                        for name, seconds in linters.items()
                    ]
                },
                report_file,
            )

    def rows(self, suggestion):
        return {row["key"]: row for row in suggestion["details"]}

    def test_rules(self):
        FakeInstaller.statuses = {
            "PYTHON_UNSUPPORTED": ("unsupported", "No Windows build. Use Docker."),
            "PYTHON_HOSTTOOL": ("host-provided", None),
        }
        master = self.master(
            [
                fake_linter("PYTHON_BLACK", speed=5),
                fake_linter("PYTHON_PYLINT", speed=2),
                fake_linter("REPOSITORY_TRIVY", speed=4, mode="project"),
                fake_linter("PYTHON_UNSUPPORTED"),
                fake_linter("PYTHON_HOSTTOOL", executable="hosttool"),
            ]
        )
        with patch("megalinter.native.suggest.shutil.which", return_value=None):
            suggestion = suggest.build_native_linters_suggestion(master)
        rows = self.rows(suggestion)
        self.assertEqual(suggestion["variable"], "NATIVE_LINTERS")
        self.assertEqual(suggestion["values"], ["PYTHON_BLACK"])
        self.assertTrue(rows["PYTHON_BLACK"]["recommended"])
        self.assertIn("speed 2/5", rows["PYTHON_PYLINT"]["reason"])
        self.assertIn("whole repository", rows["REPOSITORY_TRIVY"]["reason"])
        self.assertEqual(
            rows["PYTHON_UNSUPPORTED"]["reason"], "No Windows build. Use Docker."
        )
        self.assertEqual(rows["PYTHON_UNSUPPORTED"]["native_status"], "unsupported")
        self.assertIn("hosttool is not installed", rows["PYTHON_HOSTTOOL"]["reason"])
        self.assertFalse(any(rows[key]["recommended"] for key in list(rows)[1:]))

    def test_host_tool_found_on_the_machine_is_recommended(self):
        FakeInstaller.statuses = {"PYTHON_HOSTTOOL": ("host-provided", None)}
        master = self.master([fake_linter("PYTHON_HOSTTOOL")])
        with patch("megalinter.native.suggest.shutil.which", return_value="/bin/tool"):
            suggestion = suggest.build_native_linters_suggestion(master)
        self.assertEqual(suggestion["values"], ["PYTHON_HOSTTOOL"])

    def test_measured_time_wins_over_the_static_speed(self):
        self.write_report({"PYTHON_PYLINT": 0.4, "SPELL_CSPELL": 12.5})
        master = self.master(
            [
                fake_linter("PYTHON_PYLINT", speed=1),
                fake_linter("SPELL_CSPELL", speed=5),
            ]
        )
        suggestion = suggest.build_native_linters_suggestion(master)
        rows = self.rows(suggestion)
        self.assertEqual(suggestion["values"], ["PYTHON_PYLINT"])
        self.assertEqual(rows["PYTHON_PYLINT"]["measured_seconds"], 0.4)
        self.assertIn("measured 0.4 s", rows["PYTHON_PYLINT"]["reason"])
        self.assertIn("slow (measured 12.5 s", rows["SPELL_CSPELL"]["reason"])

    def test_first_run_of_an_installed_linter_is_not_a_measure(self):
        # 48 s measured on Windows for linters that take 1 s from the second run
        self.write_report(
            {"PYTHON_BLACK": 48.9, "PYTHON_FLAKE8": 47.8},
            first_run={"PYTHON_BLACK"},
        )
        master = self.master(
            [
                fake_linter("PYTHON_BLACK", speed=5),
                fake_linter("PYTHON_FLAKE8", speed=5),
            ]
        )
        rows = self.rows(suggest.build_native_linters_suggestion(master))
        self.assertTrue(rows["PYTHON_BLACK"]["recommended"])
        self.assertNotIn("measured_seconds", rows["PYTHON_BLACK"])
        self.assertFalse(rows["PYTHON_FLAKE8"]["recommended"])

    def test_slowest_measure_of_the_reports_is_used(self):
        self.write_report({"PYTHON_BLACK": 0.4})
        self.write_report({"PYTHON_BLACK": 11.0}, sub_folder="python_black")
        master = self.master([fake_linter("PYTHON_BLACK", speed=5)])
        self.assertIsNone(suggest.build_native_linters_suggestion(master))

    def test_unreadable_reports_are_ignored(self):
        with open(
            os.path.join(self.folder.name, suggest.JSON_REPORT_FILE_NAME),
            "w",
            encoding="utf-8",
        ) as report_file:
            report_file.write("{not json")
        master = self.master([fake_linter("PYTHON_BLACK", speed=5)])
        suggestion = suggest.build_native_linters_suggestion(master)
        self.assertNotIn("measured_seconds", self.rows(suggestion)["PYTHON_BLACK"])

    def test_no_suggestion_when_the_configuration_is_already_the_recommendation(self):
        master = self.master(
            [
                fake_linter("PYTHON_BLACK", speed=5),
                fake_linter("PYTHON_PYLINT", speed=1),
            ],
            native_linters=["PYTHON_BLACK"],
        )
        self.assertIsNone(suggest.build_native_linters_suggestion(master))

    def test_listed_linters_are_flagged(self):
        master = self.master(
            [fake_linter("PYTHON_BLACK", speed=5), fake_linter("PYTHON_RUFF", speed=5)],
            native_linters=["PYTHON_BLACK", "all"],
        )
        rows = self.rows(suggest.build_native_linters_suggestion(master))
        self.assertTrue(rows["PYTHON_BLACK"]["listed"])
        self.assertFalse(rows["PYTHON_RUFF"]["listed"])

    def test_no_suggestion_without_a_recommended_linter(self):
        master = self.master([fake_linter("REPOSITORY_TRIVY", mode="project")])
        self.assertIsNone(suggest.build_native_linters_suggestion(master))

    def test_rows_are_listed_with_the_recommended_ones_first(self):
        master = self.master(
            [fake_linter("A_SLOW", speed=1), fake_linter("B_FAST", speed=5)]
        )
        lines = suggest.format_native_rows(
            suggest.build_native_linters_suggestion(master)["details"]
        )
        self.assertIn("B_FAST", lines[0])
        self.assertIn("run natively", lines[0])
        self.assertIn("A_SLOW", lines[1])
        self.assertIn("CI only", lines[1])


if __name__ == "__main__":
    unittest.main()
