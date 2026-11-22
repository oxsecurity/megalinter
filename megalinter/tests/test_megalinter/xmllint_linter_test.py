#!/usr/bin/env python3
# Tests of XmlLintLinter: the indentation of the autoformat is given to the xmllint
# command only, the configuration shared with the other linters is not changed
import unittest
from unittest.mock import patch

from megalinter import config
from megalinter.Linter import Linter
from megalinter.linters.XmlLintLinter import XmlLintLinter


class XmlLintLinterTest(unittest.TestCase):
    def setUp(self):
        self.request_id = "test-xmllint-linter"
        config.set_config(
            self.request_id,
            {"XML_XMLLINT_AUTOFORMAT": "true", "XML_XMLLINT_INDENT": "    "},
        )
        self.addCleanup(config.delete, self.request_id)

    def test_indent_is_given_to_the_command_only(self):
        linter = XmlLintLinter.__new__(XmlLintLinter)
        linter.request_id = self.request_id
        linter.apply_fixes = True
        linter.cli_lint_fix_arg_name = "--format"
        linter.cli_lint_mode = "file"
        linter.lint_command_env = None
        with patch.object(
            Linter, "build_lint_command", return_value=["xmllint", "--format"]
        ), patch.object(config, "clear_registered_caches") as clear_caches:
            command = linter.build_lint_command("a.xml")
        self.assertEqual(command, ["xmllint", "--format", "--output", "a.xml"])
        self.assertEqual(linter.lint_command_env, {"XMLLINT_INDENT": "    "})
        self.assertFalse(config.exists(self.request_id, "XMLLINT_INDENT"))
        clear_caches.assert_not_called()


if __name__ == "__main__":
    unittest.main()
