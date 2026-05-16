#!/usr/bin/env python3
"""
Unit tests for EslintLinter ESLint v10 activation gate and the generic
user-notifications system on Megalinter.
"""

import json
import os
import tempfile
import unittest

from megalinter.linters.EslintLinter import (
    ESLINT10_NOTIFICATION_KEY,
    ESLINT_FLAT_CONFIG_MIGRATION_URL,
    EslintLinter,
)
from megalinter.utils_reporter import (
    build_user_notifications,
    register_user_notification,
)


class _Master:
    def __init__(self):
        self.user_notifications = {}


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
            linter._gate_on_eslint10_config({"workspace": workspace, "master": master})

            self.assertTrue(linter.is_active)
            self.assertFalse(linter.disabled)
            self.assertEqual(master.user_notifications, {})

    def test_gate_with_legacy_eslintrc_disables_and_registers_notification(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".eslintrc.json"), "w", encoding="utf-8"
            ) as fh:
                fh.write("{}\n")

            linter = _make_linter("JAVASCRIPT_ES")
            master = _Master()
            linter._gate_on_eslint10_config({"workspace": workspace, "master": master})

            self.assertFalse(linter.is_active)
            self.assertTrue(linter.disabled)
            self.assertIn(".eslintrc.json", linter.disabled_reason or "")
            self.assertIn(ESLINT10_NOTIFICATION_KEY, master.user_notifications)
            entry = master.user_notifications[ESLINT10_NOTIFICATION_KEY]
            self.assertEqual(entry["values"], ["JAVASCRIPT_ES"])
            self.assertEqual(entry["extras"]["legacy_config"], ".eslintrc.json")
            self.assertEqual(
                entry["extras"]["migration_url"], ESLINT_FLAT_CONFIG_MIGRATION_URL
            )

    def test_gate_with_package_json_eslintconfig_registers_notification(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, "package.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump({"name": "demo", "eslintConfig": {"rules": {}}}, fh)

            linter = _make_linter("TYPESCRIPT_ES")
            master = _Master()
            linter._gate_on_eslint10_config({"workspace": workspace, "master": master})

            self.assertFalse(linter.is_active)
            entry = master.user_notifications[ESLINT10_NOTIFICATION_KEY]
            self.assertEqual(entry["values"], ["TYPESCRIPT_ES"])
            self.assertEqual(
                entry["extras"]["legacy_config"], "package.json#eslintConfig"
            )

    def test_gate_with_no_config_files_is_noop(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = _make_linter()
            master = _Master()
            linter._gate_on_eslint10_config({"workspace": workspace, "master": master})

            self.assertTrue(linter.is_active)
            self.assertFalse(linter.disabled)
            self.assertEqual(master.user_notifications, {})

    def test_gate_collects_multiple_linters_into_single_notice(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".eslintrc.yml"), "w", encoding="utf-8"
            ) as fh:
                fh.write("rules: {}\n")

            master = _Master()
            for name in ("JAVASCRIPT_ES", "TYPESCRIPT_ES", "JSX_ESLINT"):
                linter = _make_linter(name)
                linter._gate_on_eslint10_config(
                    {"workspace": workspace, "master": master}
                )

            entry = master.user_notifications[ESLINT10_NOTIFICATION_KEY]
            self.assertEqual(
                sorted(entry["values"]),
                ["JAVASCRIPT_ES", "JSX_ESLINT", "TYPESCRIPT_ES"],
            )
            self.assertEqual(entry["extras"]["legacy_config"], ".eslintrc.yml")

            rendered = build_user_notifications(master)
            self.assertEqual(len(rendered), 1)
            notice = rendered[0]
            self.assertIn("`JAVASCRIPT_ES`, `JSX_ESLINT`, `TYPESCRIPT_ES`", notice)
            self.assertIn(".eslintrc.yml", notice)
            self.assertIn(ESLINT_FLAT_CONFIG_MIGRATION_URL, notice)

    def test_gate_deduplicates_linter_names(self):
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

            entry = master.user_notifications[ESLINT10_NOTIFICATION_KEY]
            self.assertEqual(entry["values"], ["JAVASCRIPT_ES"])


class UserNotificationsTest(unittest.TestCase):
    def test_register_creates_entry_and_collects_values(self):
        master = _Master()
        register_user_notification(
            master,
            key="demo",
            template="Items: {values} ({reason})",
            value="A",
            extras={"reason": "test"},
        )
        register_user_notification(
            master,
            key="demo",
            template="Items: {values} ({reason})",
            value="B",
        )

        self.assertEqual(master.user_notifications["demo"]["values"], ["A", "B"])
        rendered = build_user_notifications(master)
        self.assertEqual(rendered, ["Items: `A`, `B` (test)"])

    def test_extras_first_write_wins_for_same_key(self):
        master = _Master()
        register_user_notification(
            master,
            key="demo",
            template="{values} :: {detail}",
            value="x",
            extras={"detail": "first"},
        )
        register_user_notification(
            master,
            key="demo",
            template="{values} :: {detail}",
            value="y",
            extras={"detail": "second"},
        )
        self.assertEqual(master.user_notifications["demo"]["extras"]["detail"], "first")

    def test_empty_values_are_skipped(self):
        master = _Master()
        register_user_notification(master, key="demo", template="{values}", value=None)
        self.assertEqual(build_user_notifications(master), [])

    def test_build_returns_empty_when_no_notifications(self):
        master = _Master()
        self.assertEqual(build_user_notifications(master), [])

    def test_renders_multiple_independent_notifications(self):
        master = _Master()
        register_user_notification(master, key="a", template="A: {values}", value="1")
        register_user_notification(master, key="b", template="B: {values}", value="2")
        rendered = build_user_notifications(master)
        self.assertIn("A: `1`", rendered)
        self.assertIn("B: `2`", rendered)


if __name__ == "__main__":
    unittest.main()
