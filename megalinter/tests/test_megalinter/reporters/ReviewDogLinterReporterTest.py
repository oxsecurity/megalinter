import unittest
from unittest.mock import patch, mock_open, MagicMock

from megalinter.reporters.ReviewdogLinterReporter import ReviewdogLinterReporter


def mock_linter(name=""):
    mock = MagicMock()
    mock.complete_text_reporter_report.return_value = []
    mock.cli_lint_mode = "project"
    mock.status = "ERROR"
    mock.name = name
    return mock


class ReviewdogLinterReporterRegexConvertorTestCase(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    @patch('megalinter.Linter', new_callable=mock_linter, name="PYTHON_PYLINT")
    def test_regex_convertor(self, linter, mock_report_file):
        linter.reviewdog_processor = {
            "class_name": "Regex",
            "init_params": {
                "regex": r"^(?P<path>[^:]+):(?P<line>\d+):(?P<column>\d+):(?P<message>.+)$"
            }
        }
        linter.stdout = "\n".join([
            "/some/path.py:12:3:Something is wrong with this file",
            "/a/path/file.py:2:1:A linting error!"
        ])

        self.produce_report(linter)

        mock_report_file.assert_called_once_with(
            "/tmp/reports/reviewdog/ERROR-PYTHON_PYLINT.log", "w", encoding="utf-8"
        )
        mock_report_file().write.assert_called_once_with("\n".join([
            r'{"message": "Something is wrong with this file",'
            + ' "location": {"range": {"start": {"line": 12, "column": 3}, "end": null}, '
            + '"path": "/some/path.py"}, '
            + '"severity": "ERROR", "suggestions": []}',
            r'{"message": "A linting error!", '
            + '"location": {"range": {"start": {"line": 2, "column": 1}, "end": null}, '
            + '"path": "/a/path/file.py"}, '
            + '"severity": "ERROR", "suggestions": []}']) + "\n"
        )

    @patch('builtins.open', new_callable=mock_open)
    @patch('megalinter.Linter', new_callable=mock_linter, name="PYTHON_PYLINT")
    def test_regex_convertor_with_unparsable_lines(self, linter, mock_report_file):
        linter.reviewdog_processor = {
            "class_name": "Regex",
            "init_params": {
                "regex": r"^(?P<path>[^:]+):(?P<line>\d+):(?P<column>\d+):(?P<message>.+)$"
            }
        }
        linter.stdout = "\n".join([
            "/some/path.py:12:3:Something is wrong with this file",
            "This line cannot have information extracted from it and should be skipped",
            "/a/path/file.py:2:1:Why would you do that?"
        ])

        self.produce_report(linter)

        mock_report_file.assert_called_once_with(
            "/tmp/reports/reviewdog/ERROR-PYTHON_PYLINT.log", "w", encoding="utf-8"
        )
        mock_report_file().write.assert_called_once_with("\n".join([
            r'{"message": "Something is wrong with this file", '
            + '"location": {"range": {"start": {"line": 12, "column": 3}, "end": null}, '
            + '"path": "/some/path.py"}, '
            + '"severity": "ERROR", "suggestions": []}',
            r'{"message": "Why would you do that?", '
            + '"location": {"range": {"start": {"line": 2, "column": 1}, "end": null}, '
            + '"path": "/a/path/file.py"}, '
            + '"severity": "ERROR", "suggestions": []}']) + "\n"
        )

    def produce_report(self, linter):
        reporter = ReviewdogLinterReporter({"master": linter, "report_folder": "/tmp/reports"})
        reporter.produce_report()


class ReviewdogLinterReporterUnifiedDiffConvertorTestCase(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    @patch('megalinter.Linter', new_callable=mock_linter, name="LINTER")
    def test_unifieddiff_convertor(self, linter, mock_report_file):
        linter.reviewdog_processor = {
            "class_name": "UnifiedDiffs",
            "init_params": {
                "file_header_regex": r"^\s*(?:[A-Z]+:) (?P<path>\S+)\s",
                "message_include_file_header": True
            }
        }
        linter.stdout = """
[ERROR] .automation/test/python/python_bad_1.py
ERROR: .automation/test/python/python_bad_1.py Imports are incorrectly sorted and/or formatted.
--- .automation/test/python/python_bad_1.py:before	2020-12-05 12:08:47.707389
+++ .automation/test/python/python_bad_1.py:after	2020-12-05 12:34:28.504872
@@ -1,11 +1,11 @@
 import json
+import sys
 from os import getenv, path
 from pprint import pprint
-import sys

-import click # pylint: disable=import-error
-from dotenv import load_dotenv # pylint: disable=import-error
-import requests # pylint: disable=import-error
+import click  # pylint: disable=import-error
+import requests  # pylint: disable=import-error
+from dotenv import load_dotenv  # pylint: disable=import-error

 env = load_dotenv()
 api_url = getenv(API_URL, default='https://api.github.com/graphql' )
"""

        reporter = ReviewdogLinterReporter({"master": linter, "report_folder": "/tmp/reports"})
        reporter.produce_report()

        mock_report_file.assert_called_once_with("/tmp/reports/reviewdog/ERROR-LINTER.log", "w", encoding="utf-8")
        mock_report_file().write.assert_called_once_with(
            '{"message": "ERROR: .automation/test/python/python_bad_1.py '
            + 'Imports are incorrectly sorted and/or formatted.", '
            + '"location": {"range": {"start": {"line": 1, "column": 0}, "end": {"line": 12, "column": 69}}, '
            + '"path": ".automation/test/python/python_bad_1.py"}, '
            + '"severity": "ERROR", '
            + '"suggestions": [{"text": "import json\\nimport sys\\nfrom os import getenv, path'
            + '\\nfrom pprint import pprint\\n\\nimport click  # pylint: disable=import-error'
            + '\\nimport requests  # pylint: disable=import-error'
            + '\\nfrom dotenv import load_dotenv  # pylint: disable=import-error'
            + '\\n\\nenv = load_dotenv()\\napi_url = getenv(API_URL, default=\'https://api.github.com/graphql\' )", '
            + '"range": {"start": {"line": 1, "column": 0}, "end": {"line": 12, "column": 69}}}]}\n'
        )
