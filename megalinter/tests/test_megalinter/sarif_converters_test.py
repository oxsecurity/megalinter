#!/usr/bin/env python3
"""
Unit tests for the SARIF builder and for the converters of the linters
that can not output SARIF by themselves

"""

import json
import os
import tempfile
import unittest

from megalinter import utils, utils_sarif
from megalinter.Linter import Linter
from megalinter.linters.ClippyLinter import clippy_json_to_sarif
from megalinter.linters.CodespellLinter import codespell_output_to_sarif
from megalinter.linters.CppLintLinter import cpplint_output_to_sarif
from megalinter.linters.DartAnalyzerLinter import dart_json_to_sarif
from megalinter.linters.Flake8Linter import flake8_output_to_sarif
from megalinter.linters.MarkdownlintLinter import markdownlint_json_to_sarif
from megalinter.linters.PowershellLinter import powershell_json_to_sarif
from megalinter.linters.PylintLinter import pylint_json2_to_sarif
from megalinter.linters.StyleLintLinter import stylelint_json_to_sarif
from megalinter.linters.YamllintLinter import yamllint_parsable_to_sarif
from megalinter.sarif_builder import (
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)

WORKSPACE = os.path.abspath("lint-workspace")


def first_run(sarif_builder):
    return sarif_builder.build_sarif_output()["runs"][0]


def location(result):
    return result["locations"][0]["physicalLocation"]


class SarifBuilderTest(unittest.TestCase):
    def test_result_regions_are_valid(self):
        result = (
            SarifResultBuilder()
            .init_simple("error", "msg", "R1", "a.py", 0, 0, 0, 0)
            .result
        )
        region = location(result)["region"]
        self.assertEqual(
            region, {"startLine": 1, "startColumn": 1, "endLine": 1, "endColumn": 1}
        )

    def test_result_without_location(self):
        result = SarifResultBuilder().init_simple("error", None, "R1").result
        self.assertNotIn("locations", result)
        self.assertEqual(result["message"]["text"], "R1")

    def test_result_end_column_is_not_before_start_column(self):
        result = (
            SarifResultBuilder()
            .init_simple("note", "msg", "R1", "a.py", 3, 10, 3, 4)
            .result
        )
        self.assertEqual(location(result)["region"]["endColumn"], 10)

    def test_rules_are_deduplicated_and_indexed(self):
        run = SarifRunBuilder().init_simple("tool", "1.0", "https://tool")
        run.add_rule(SarifRuleBuilder().init_simple("R2", help_uri="https://r2"))
        for rule_id in ["R1", "R2", "R1"]:
            run.add_result(
                SarifResultBuilder().init_simple("error", "msg", rule_id, "a.py", 1)
            )
        built = SarifBuilder().add_run(run).build_sarif_output()
        driver = built["runs"][0]["tool"]["driver"]
        self.assertEqual([rule["id"] for rule in driver["rules"]], ["R2", "R1"])
        self.assertEqual(driver["rules"][0]["helpUri"], "https://r2")
        self.assertEqual(
            [result["ruleIndex"] for result in built["runs"][0]["results"]], [1, 0, 1]
        )
        self.assertEqual(built["version"], "2.1.0")
        self.assertEqual(
            json.loads(SarifBuilder().add_run(run).build_sarif_json_string()), built
        )

    def test_to_sarif_uri(self):
        self.assertEqual(to_sarif_uri("./a/b.py"), "a/b.py")
        self.assertEqual(to_sarif_uri("a\\b.py"), "a/b.py")
        absolute = os.path.join(WORKSPACE, "src", "a.py")
        self.assertEqual(to_sarif_uri(absolute, WORKSPACE), "src/a.py")
        self.assertEqual(to_sarif_uri("other/a.py", WORKSPACE), "other/a.py")


class FindJsonValueTest(unittest.TestCase):
    def test_finds_array_among_log_lines(self):
        text = '[INFO] starting\nwarning {not json\n[\n  {"a": 1}\n]\ndone'
        self.assertEqual(utils.find_json_value(text, list), [{"a": 1}])

    def test_uses_predicate_and_type(self):
        text = '[1, 2]\n{"messages": []}'
        self.assertEqual(
            utils.find_json_value(text, dict, lambda value: "messages" in value),
            {"messages": []},
        )
        self.assertIsNone(utils.find_json_value("no json here", (dict, list)))


class ConvertersTest(unittest.TestCase):
    def test_pylint_json2(self):
        output = {
            "messages": [
                {
                    "type": "convention",
                    "symbol": "line-too-long",
                    "message": "Line too long (120/100)",
                    "messageId": "C0301",
                    "module": "a",
                    "obj": "",
                    "line": 3,
                    "column": 0,
                    "endLine": 3,
                    "endColumn": 120,
                    "path": "src/a.py",
                    "absolutePath": "/tmp/lint/src/a.py",
                },
                {
                    "type": "error",
                    "symbol": "undefined-variable",
                    "message": "Undefined variable 'x'",
                    "messageId": "E0602",
                    "module": "a",
                    "obj": "",
                    "line": 5,
                    "column": 4,
                    "endLine": None,
                    "endColumn": None,
                    "path": "src/a.py",
                    "absolutePath": "/tmp/lint/src/a.py",
                },
            ],
            "statistics": {"messageTypeCount": {}, "score": 5},
        }
        run = first_run(pylint_json2_to_sarif("noise\n" + json.dumps(output, indent=4)))
        self.assertEqual([r["level"] for r in run["results"]], ["note", "error"])
        self.assertEqual(
            location(run["results"][0])["region"],
            {"startLine": 3, "startColumn": 1, "endLine": 3, "endColumn": 121},
        )
        self.assertEqual(
            location(run["results"][1])["region"], {"startLine": 5, "startColumn": 5}
        )
        rule = run["tool"]["driver"]["rules"][0]
        self.assertEqual(rule["id"], "line-too-long")
        self.assertTrue(rule["helpUri"].endswith("/convention/line-too-long.html"))
        self.assertEqual(
            location(run["results"][0])["artifactLocation"]["uri"], "src/a.py"
        )

    def test_pylint_without_json_gives_empty_run(self):
        run = first_run(pylint_json2_to_sarif("pylint crashed"))
        self.assertEqual(run["results"], [])

    def test_flake8(self):
        stdout = (
            f"{WORKSPACE}/src/a.py:10:80: E501 line too long (95 > 79 characters)\n"
            "./b.py:1:1: F401 'os' imported but unused\n"
            "not a finding\n"
        )
        run = first_run(flake8_output_to_sarif(stdout, WORKSPACE))
        self.assertEqual([r["ruleId"] for r in run["results"]], ["E501", "F401"])
        self.assertEqual({r["level"] for r in run["results"]}, {"error"})
        self.assertEqual(
            location(run["results"][0])["artifactLocation"]["uri"], "src/a.py"
        )
        self.assertEqual(location(run["results"][1])["artifactLocation"]["uri"], "b.py")
        self.assertEqual(
            location(run["results"][0])["region"], {"startLine": 10, "startColumn": 80}
        )

    def test_codespell(self):
        stdout = (
            "docs/a.md:12: teh ==> the\n"
            "docs/b.md:3: recieve ==> receive, deceive\n"
            "docs/teh.md: teh ==> the\n"
        )
        run = first_run(codespell_output_to_sarif(stdout, WORKSPACE))
        self.assertEqual(len(run["results"]), 3)
        self.assertEqual(
            run["results"][1]["message"]["text"],
            '"recieve" is a misspelling of "receive, deceive"',
        )
        self.assertEqual(location(run["results"][0])["region"], {"startLine": 12})
        self.assertNotIn("region", location(run["results"][2]))

    def test_yamllint(self):
        stdout = (
            'a.yml:1:1: [warning] missing document start "---" (document-start)\n'
            "a.yml:3:81: [error] line too long (100 > 80 characters) (line-length)\n"
            "b.yml:2:5: [error] syntax error: mapping values are not allowed here (syntax)\n"
        )
        run = first_run(yamllint_parsable_to_sarif(stdout, WORKSPACE))
        self.assertEqual(
            [(r["ruleId"], r["level"]) for r in run["results"]],
            [
                ("document-start", "warning"),
                ("line-length", "error"),
                ("syntax", "error"),
            ],
        )
        self.assertEqual(
            run["results"][1]["message"]["text"],
            "line too long (100 > 80 characters)",
        )
        self.assertTrue(
            run["tool"]["driver"]["rules"][1]["helpUri"].endswith(
                "#module-yamllint.rules.line_length"
            )
        )

    def test_stylelint_json(self):
        output = [
            {
                "source": f"{WORKSPACE}/css/a.css",
                "errored": True,
                "warnings": [
                    {
                        "line": 2,
                        "column": 3,
                        "endLine": 2,
                        "endColumn": 8,
                        "rule": "color-no-invalid-hex",
                        "severity": "error",
                        "text": "Unexpected invalid hex color (color-no-invalid-hex)",
                    },
                    {
                        "line": 4,
                        "column": 1,
                        "rule": "scss/at-rule-no-unknown",
                        "severity": "warning",
                        "text": "Unexpected unknown at-rule",
                    },
                ],
                "invalidOptionWarnings": [{"text": "Unknown rule foo"}],
            }
        ]
        run = first_run(stylelint_json_to_sarif(json.dumps(output), WORKSPACE))
        self.assertEqual(
            [r["level"] for r in run["results"]], ["error", "warning", "error"]
        )
        self.assertEqual(
            location(run["results"][0])["artifactLocation"]["uri"], "css/a.css"
        )
        self.assertEqual(
            location(run["results"][0])["region"],
            {"startLine": 2, "startColumn": 3, "endLine": 2, "endColumn": 8},
        )
        rules = {rule["id"]: rule for rule in run["tool"]["driver"]["rules"]}
        self.assertIn("helpUri", rules["color-no-invalid-hex"])
        self.assertNotIn("helpUri", rules["scss/at-rule-no-unknown"])
        self.assertNotIn("locations", run["results"][2])

    def test_markdownlint_json(self):
        findings = [
            {
                "fileName": "docs/a.md",
                "lineNumber": 7,
                "ruleNames": ["MD013", "line-length"],
                "ruleDescription": "Line length",
                "ruleInformation": "https://github.com/DavidAnson/markdownlint/blob/main/doc/md013.md",
                "errorDetail": "Expected: 80; Actual: 95",
                "errorContext": "A very long line",
                "errorRange": [81, 15],
                "fixInfo": None,
                "severity": "error",
            },
            {
                "fileName": "docs/a.md",
                "lineNumber": 9,
                "ruleNames": ["MD041", "first-line-heading"],
                "ruleDescription": "First line in a file should be a top-level heading",
                "ruleInformation": "https://example.org/md041",
                "errorDetail": None,
                "errorContext": None,
                "errorRange": None,
                "severity": "warning",
            },
        ]
        run = first_run(
            markdownlint_json_to_sarif(json.dumps(findings, indent=2), WORKSPACE)
        )
        self.assertEqual([r["level"] for r in run["results"]], ["error", "warning"])
        self.assertEqual(
            run["results"][0]["message"]["text"],
            'Line length [Expected: 80; Actual: 95] [Context: "A very long line"]',
        )
        self.assertEqual(
            location(run["results"][0])["region"],
            {"startLine": 7, "startColumn": 81, "endLine": 7, "endColumn": 96},
        )
        self.assertEqual(location(run["results"][1])["region"], {"startLine": 9})
        self.assertEqual(run["tool"]["driver"]["rules"][0]["name"], "line-length")

    def test_markdownlint_without_finding(self):
        run = first_run(markdownlint_json_to_sarif("", WORKSPACE))
        self.assertEqual(run["results"], [])

    def test_dart_json(self):
        output = {
            "version": 1,
            "diagnostics": [
                {
                    "code": "unused_import",
                    "severity": "WARNING",
                    "type": "STATIC_WARNING",
                    "location": {
                        "file": f"{WORKSPACE}/lib/a.dart",
                        "range": {
                            "start": {"offset": 7, "line": 1, "column": 8},
                            "end": {"offset": 20, "line": 1, "column": 21},
                        },
                    },
                    "problemMessage": "Unused import.",
                    "correctionMessage": "Try removing the import.",
                    "documentation": "https://dart.dev/diagnostics/unused_import",
                },
                {
                    "code": "prefer_const_declarations",
                    "severity": "INFO",
                    "type": "LINT",
                    "location": {
                        "file": f"{WORKSPACE}/lib/a.dart",
                        "range": {
                            "start": {"offset": 30, "line": 3, "column": 1},
                            "end": {"offset": 40, "line": 3, "column": 11},
                        },
                    },
                    "problemMessage": "Use const.",
                },
            ],
        }
        run = first_run(dart_json_to_sarif(json.dumps(output), WORKSPACE))
        self.assertEqual([r["level"] for r in run["results"]], ["warning", "note"])
        self.assertEqual(
            run["results"][0]["message"]["text"],
            "Unused import. Try removing the import.",
        )
        self.assertEqual(
            location(run["results"][0])["artifactLocation"]["uri"], "lib/a.dart"
        )
        self.assertEqual(
            run["tool"]["driver"]["rules"][0]["helpUri"],
            "https://dart.dev/diagnostics/unused_import",
        )

    def test_cpplint(self):
        stdout = (
            "Done processing src/a.cc\n"
            "src/a.cc:0:  No copyright message found.  [legal/copyright] [5]\n"
            "src/a.cc:12:  Missing space after ,  [whitespace/comma] [3]\n"
            "Total errors found: 2\n"
        )
        run = first_run(cpplint_output_to_sarif(stdout, WORKSPACE))
        self.assertEqual(
            [r["ruleId"] for r in run["results"]],
            ["legal/copyright", "whitespace/comma"],
        )
        self.assertEqual(location(run["results"][0])["region"], {"startLine": 1})
        self.assertEqual(run["results"][1]["message"]["text"], "Missing space after ,")
        self.assertEqual({r["level"] for r in run["results"]}, {"error"})

    def test_clippy_cargo_json(self):
        diagnostic = {
            "reason": "compiler-message",
            "package_id": "demo 0.1.0",
            "message": {
                "code": {"code": "clippy::needless_return", "explanation": None},
                "level": "warning",
                "message": "unneeded `return` statement",
                "children": [
                    {"level": "help", "message": "remove `return`", "spans": []}
                ],
                "spans": [
                    {
                        "file_name": "src/main.rs",
                        "is_primary": True,
                        "line_start": 4,
                        "line_end": 4,
                        "column_start": 5,
                        "column_end": 13,
                    }
                ],
            },
        }
        error = json.loads(json.dumps(diagnostic))
        error["message"]["level"] = "error"
        error["message"]["code"] = {"code": "E0308"}
        error["message"]["message"] = "mismatched types"
        error["message"]["children"] = []
        summary = {
            "reason": "compiler-message",
            "message": {
                "level": "warning",
                "message": "1 warning emitted",
                "code": None,
                "spans": [],
                "children": [],
            },
        }
        stdout = "\n".join(
            [
                "    Checking demo v0.1.0 (/tmp/lint)",
                json.dumps({"reason": "compiler-artifact"}),
                json.dumps(diagnostic),
                json.dumps(diagnostic),
                json.dumps(error),
                json.dumps(summary),
                json.dumps({"reason": "build-finished", "success": False}),
            ]
        )
        run = first_run(clippy_json_to_sarif(stdout, WORKSPACE))
        self.assertEqual([r["level"] for r in run["results"]], ["warning", "error"])
        self.assertEqual(
            run["results"][0]["message"]["text"],
            "unneeded `return` statement (remove `return`)",
        )
        self.assertEqual(
            location(run["results"][0])["region"],
            {"startLine": 4, "startColumn": 5, "endLine": 4, "endColumn": 13},
        )
        rules = run["tool"]["driver"]["rules"]
        self.assertTrue(rules[0]["helpUri"].endswith("#needless_return"))
        self.assertTrue(rules[1]["helpUri"].endswith("/E0308.html"))

    def test_powershell_json(self):
        findings = [
            {
                "RuleName": "PSAvoidUsingWriteHost",
                "Severity": "Warning",
                "ScriptPath": f"{WORKSPACE}/scripts/a.ps1",
                "Line": 4,
                "Column": 1,
                "EndLine": 4,
                "EndColumn": 20,
                "Message": "File 'a.ps1' uses Write-Host.",
            },
            {
                "RuleName": "",
                "Severity": "ParseError",
                "ScriptPath": f"{WORKSPACE}/scripts/b.ps1",
                "Line": 1,
                "Column": 2,
                "EndLine": None,
                "EndColumn": None,
                "Message": "Unexpected token.",
            },
        ]
        run = first_run(powershell_json_to_sarif(json.dumps(findings), WORKSPACE))
        self.assertEqual([r["level"] for r in run["results"]], ["warning", "error"])
        self.assertEqual(run["results"][1]["ruleId"], "ParseError")
        rules = run["tool"]["driver"]["rules"]
        self.assertTrue(rules[0]["helpUri"].endswith("/AvoidUsingWriteHost.md"))
        self.assertNotIn("helpUri", rules[1])
        self.assertEqual(
            location(run["results"][0])["artifactLocation"]["uri"], "scripts/a.ps1"
        )


class MergeSarifTest(unittest.TestCase):
    @staticmethod
    def build_log(results):
        run = SarifRunBuilder().init_simple("tool")
        for rule_id, uri in results:
            run.add_result(
                SarifResultBuilder().init_simple("error", "m", rule_id, uri, 1)
            )
        return SarifBuilder().add_run(run).build_sarif_output()

    def test_rules_are_merged_and_indexes_follow(self):
        target = self.build_log([("R1", "a.py"), ("R2", "a.py")])
        source = self.build_log([("R3", "b.py"), ("R2", "b.py")])
        source["runs"][0]["artifacts"] = [{"location": {"uri": "b.py"}}]
        utils_sarif.merge_sarif_logs(target, source)
        run = target["runs"][0]
        rules = [rule["id"] for rule in run["tool"]["driver"]["rules"]]
        self.assertEqual(rules, ["R1", "R2", "R3"])
        self.assertEqual(len(run["results"]), 4)
        for result in run["results"]:
            self.assertEqual(rules[result["ruleIndex"]], result["ruleId"])
        self.assertEqual(len(run["artifacts"]), 1)

    def test_file_mode_sarif_of_each_file_is_gathered(self):
        with tempfile.TemporaryDirectory() as report_folder:
            linter = object.__new__(Linter)
            linter.merged_sarif = None
            linter.sarif_output_file = os.path.join(report_folder, "LINT.sarif")
            for rule_id, uri in [("R1", "a.py"), ("R2", "b.py")]:
                log = self.build_log([(rule_id, uri)])
                # linters of the .NET family write a BOM
                with open(linter.sarif_output_file, "w", encoding="utf-8-sig") as file:
                    json.dump(log, file)
                linter.merge_file_sarif()
            linter.after_lint_files()
            with open(linter.sarif_output_file, encoding="utf-8") as file:
                merged = json.load(file)
        run = merged["runs"][0]
        self.assertEqual([r["ruleId"] for r in run["results"]], ["R1", "R2"])
        self.assertEqual(
            [rule["id"] for rule in run["tool"]["driver"]["rules"]], ["R1", "R2"]
        )

    def test_invalid_file_sarif_is_ignored(self):
        with tempfile.TemporaryDirectory() as report_folder:
            linter = object.__new__(Linter)
            linter.merged_sarif = None
            linter.sarif_output_file = os.path.join(report_folder, "LINT.sarif")
            with open(linter.sarif_output_file, "w", encoding="utf-8") as file:
                file.write("{not json")
            linter.merge_file_sarif()
            self.assertIsNone(linter.merged_sarif)
