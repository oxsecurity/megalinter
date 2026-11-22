#!/usr/bin/env python3
"""
Unit tests for the findings read from a SARIF file (JSON report)

"""

import json
import os
import tempfile
import unittest

from megalinter import utils_sarif


def write_sarif(folder, results):
    sarif_file = os.path.join(folder, "linter.sarif")
    with open(sarif_file, "w", encoding="utf-8") as file:
        json.dump({"runs": [{"results": results}]}, file)
    return sarif_file


def result(uri="src/a.py", line=3, **extra):
    return {
        "ruleId": "E501",
        "level": "error",
        "message": {"text": "line too long"},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": uri},
                    "region": {"startLine": line, "startColumn": 5, "endLine": line},
                }
            }
        ],
        **extra,
    }


class utils_sarif_findings_test(unittest.TestCase):
    def test_flat_finding(self):
        with tempfile.TemporaryDirectory() as folder:
            findings = utils_sarif.extract_findings(write_sarif(folder, [result()]))
        self.assertEqual(
            findings,
            [
                {
                    "level": "error",
                    "rule": "E501",
                    "message": "line too long",
                    "file": "src/a.py",
                    "line": 3,
                    "column": 5,
                    "end_line": 3,
                }
            ],
        )

    def test_missing_fields_are_omitted(self):
        with tempfile.TemporaryDirectory() as folder:
            findings = utils_sarif.extract_findings(
                write_sarif(folder, [{"message": {"markdown": "Something wrong"}}])
            )
        self.assertEqual(findings, [{"level": "warning", "message": "Something wrong"}])

    def test_suppressed_results_are_skipped(self):
        suppressed = result(suppressions=[{"status": "accepted"}])
        with tempfile.TemporaryDirectory() as folder:
            findings = utils_sarif.extract_findings(
                write_sarif(folder, [suppressed, result(line=9)])
            )
        self.assertEqual([finding["line"] for finding in findings], [9])

    def test_workspace_prefix_is_removed(self):
        with tempfile.TemporaryDirectory() as folder:
            sarif_file = write_sarif(
                folder,
                [
                    result(uri="file:///C:/work/src/a.py"),
                    result(uri="C:\\work\\src\\b.py"),
                    result(uri="/work/src/c.py"),
                    result(uri="d/e.py"),
                ],
            )
            files = [
                finding["file"]
                for finding in utils_sarif.extract_findings(sarif_file, "C:\\work")
            ]
            posix_files = [
                finding["file"]
                for finding in utils_sarif.extract_findings(sarif_file, "/work")
            ]
        self.assertEqual(files, ["src/a.py", "src/b.py", "/work/src/c.py", "d/e.py"])
        self.assertEqual(posix_files[2], "src/c.py")

    def test_no_file_or_invalid_file(self):
        self.assertIsNone(utils_sarif.extract_findings(None))
        self.assertIsNone(utils_sarif.extract_findings("/does/not/exist.sarif"))
        with tempfile.TemporaryDirectory() as folder:
            invalid = os.path.join(folder, "invalid.sarif")
            with open(invalid, "w", encoding="utf-8") as file:
                file.write("not json")
            self.assertIsNone(utils_sarif.extract_findings(invalid))
