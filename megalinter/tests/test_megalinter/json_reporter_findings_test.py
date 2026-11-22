#!/usr/bin/env python3
"""
Unit tests for the fields of the JSON report used by coding agents

"""

import json
import os
import tempfile
import unittest
import uuid
from types import SimpleNamespace

from megalinter import config
from megalinter.reporters.JsonReporter import JsonReporter


def fake_linter(name, **extra):
    attributes = {
        "name": name,
        "descriptor_id": name.split("_")[0],
        "linter_name": name.split("_")[1].lower(),
        "is_active": True,
        "status": "error",
        "return_code": 1,
        "number_errors": 1,
        "elapsed_time_s": 0.5,
        "disable_errors": False,
        "sarif_findings": None,
        "tips": [],
        "files": ["a.py"],
        "files_number": 1,
        "files_lint_results": [],
    }
    attributes.update(extra)
    return SimpleNamespace(**attributes)


class json_reporter_findings_test(unittest.TestCase):
    def produce(self, linters, tips=None, skipped=None, detail="simple"):
        request_id = str(uuid.uuid1())
        config.set_config(
            request_id, {"JSON_REPORTER": "true", "JSON_REPORTER_OUTPUT_DETAIL": detail}
        )
        with tempfile.TemporaryDirectory() as folder:
            master = SimpleNamespace(
                request_id=request_id,
                report_folder=folder,
                linters=linters,
                reporters=[],
                status="error",
                tips=tips or [],
                skipped_linters_details=skipped or [],
            )
            reporter = JsonReporter({"master": master, "report_folder": folder})
            self.assertTrue(reporter.is_active)
            reporter.produce_report()
            with open(
                os.path.join(folder, "mega-linter-report.json"), encoding="utf-8"
            ) as report_file:
                report = json.load(report_file)
        config.delete(request_id)
        return report

    def test_findings_and_blocking(self):
        findings = [{"level": "error", "rule": "E501", "file": "a.py", "line": 3}]
        report = self.produce(
            [
                fake_linter("PYTHON_FLAKE8", sarif_findings=findings),
                fake_linter("PYTHON_BLACK", disable_errors=True, return_code=0),
                # DISABLE_ERRORS_IF_LESS_THAN: errors, but the run does not fail
                fake_linter("PYTHON_RUFF", return_code=0),
                # No error: as configured
                fake_linter(
                    "PYTHON_ISORT", number_errors=0, status="success", return_code=0
                ),
                fake_linter(
                    "PYTHON_PYLINT",
                    number_errors=0,
                    status="success",
                    return_code=0,
                    disable_errors=True,
                ),
            ]
        )
        by_name = {linter["linter_name"]: linter for linter in report["linters"]}
        self.assertEqual(by_name["flake8"]["findings"], findings)
        self.assertIs(by_name["flake8"]["blocking"], True)
        self.assertNotIn("findings", by_name["black"])
        self.assertIs(by_name["black"]["blocking"], False)
        self.assertIs(by_name["ruff"]["blocking"], False)
        self.assertIs(by_name["isort"]["blocking"], True)
        self.assertIs(by_name["pylint"]["blocking"], False)

    def test_skipped_linters_and_tips(self):
        linter_tip = {"category": "timeout", "message": "Timed out"}
        report = self.produce(
            [
                fake_linter("PYTHON_FLAKE8", tips=[linter_tip]),
                fake_linter("PYTHON_BLACK", tips=[linter_tip]),
            ],
            tips=[{"category": "performance", "message": "Exclude folders"}],
            skipped=[{"key": "SPELL_CSPELL", "reason": "not listed in NATIVE_LINTERS"}],
        )
        self.assertEqual(
            report["skipped_linters"],
            [{"key": "SPELL_CSPELL", "reason": "not listed in NATIVE_LINTERS"}],
        )
        self.assertEqual(report["tips"][0]["category"], "performance")
        self.assertEqual(
            [tip.get("linter") for tip in report["tips"][1:]],
            ["PYTHON_FLAKE8", "PYTHON_BLACK"],
        )
        self.assertNotIn("skipped_linters_details", report)

    def test_existing_fields_are_unchanged(self):
        report = self.produce([fake_linter("PYTHON_FLAKE8")])
        linter = report["linters"][0]
        for field in (
            "descriptor_id",
            "linter_name",
            "status",
            "return_code",
            "number_errors",
            "elapsed_time_s",
            "files_lint_results",
        ):
            self.assertIn(field, linter)
        self.assertEqual(report["status"], "error")
        self.assertNotIn("tips", linter)
        self.assertNotIn("sarif_findings", linter)
