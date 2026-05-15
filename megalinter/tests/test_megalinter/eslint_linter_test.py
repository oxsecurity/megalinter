#!/usr/bin/env python3
"""
Unit tests for EslintLinter ESLint v10 activation gate
"""

import json
import os
import tempfile
import unittest

from megalinter.linters.EslintLinter import (
    ESLINT_FLAT_CONFIG_MIGRATION_URL,
    EslintLinter,
)


class _Master:
    def __init__(self):
        self.migration_warnings = []


def _make_linter(name="TEST_ESLINT"):
    linter = EslintLinter.__new__(EslintLinter)
    linter.name = name
    linter.is_active = True
    linter.disabled = False
    linter.disabled_reason = None
    return linter


class EslintLinterTest(unittest.TestCase):
    def test_gate_with_flat_config_keeps_linter_active(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, "eslint.config.mjs"), "w", encoding="utf-8"
            ) as fh:
                fh.write("export default [];\n")
            with open(
                os.path.join(workspace, ".eslintrc.json"), "w", encoding="utf-8"
            ) as fh:
                fh.write("{}\n")

            linter = _make_linter()
            master = _Master()
            linter._gate_on_eslint10_config(
                {"workspace": workspace, "master": master}
            )

            self.assertTrue(linter.is_active)
            self.assertFalse(linter.disabled)
            self.assertEqual(master.migration_warnings, [])

    def test_gate_with_legacy_eslintrc_disables_and_warns(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".eslintrc.json"), "w", encoding="utf-8"
            ) as fh:
                fh.write("{}\n")

            linter = _make_linter("JAVASCRIPT_ES")
            master = _Master()
            linter._gate_on_eslint10_config(
                {"workspace": workspace, "master": master}
            )

            self.assertFalse(linter.is_active)
            self.assertTrue(linter.disabled)
            self.assertIn(".eslintrc.json", linter.disabled_reason or "")
            self.assertEqual(len(master.migration_warnings), 1)
            self.assertIn("JAVASCRIPT_ES", master.migration_warnings[0])
            self.assertIn(
                ESLINT_FLAT_CONFIG_MIGRATION_URL, master.migration_warnings[0]
            )

    def test_gate_with_package_json_eslintconfig_disables_and_warns(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, "package.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump({"name": "demo", "eslintConfig": {"rules": {}}}, fh)

            linter = _make_linter("TYPESCRIPT_ES")
            master = _Master()
            linter._gate_on_eslint10_config(
                {"workspace": workspace, "master": master}
            )

            self.assertFalse(linter.is_active)
            self.assertTrue(linter.disabled)
            self.assertIn("package.json", linter.disabled_reason or "")

    def test_gate_with_no_config_files_is_noop(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = _make_linter()
            master = _Master()
            linter._gate_on_eslint10_config(
                {"workspace": workspace, "master": master}
            )

            self.assertTrue(linter.is_active)
            self.assertFalse(linter.disabled)
            self.assertEqual(master.migration_warnings, [])

    def test_gate_deduplicates_warnings(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".eslintrc.yml"), "w", encoding="utf-8"
            ) as fh:
                fh.write("rules: {}\n")

            master = _Master()
            for _ in range(3):
                linter = _make_linter("JAVASCRIPT_ES")
                linter._gate_on_eslint10_config(
                    {"workspace": workspace, "master": master}
                )

            self.assertEqual(len(master.migration_warnings), 1)


if __name__ == "__main__":
    unittest.main()
