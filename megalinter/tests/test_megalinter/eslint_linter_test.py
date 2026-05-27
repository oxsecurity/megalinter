#!/usr/bin/env python3
"""
Unit tests for EslintLinter ESLint v10 migration gate and the generic
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


def _make_linter(name="TEST_ESLINT", descriptor_id="JAVASCRIPT", is_active=True):
    linter = EslintLinter.__new__(EslintLinter)
    linter.name = name
    linter.descriptor_id = descriptor_id
    # is_active mirrors the descriptor's active_only_if_file_found result; the
    # gate only inspects the workspace when the linter is active.
    linter.is_active = is_active
    linter.disabled = False
    linter.disabled_reason = None
    linter.output_sarif = True
    linter.eslint10_legacy_config = None
    return linter


class EslintLinterTest(unittest.TestCase):
    def test_gate_with_flat_config_is_noop(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, "eslint.config.mjs"), "w", encoding="utf-8"
            ) as fh:
                fh.write("export default [];\n")
            # Legacy config also present — flat config wins, no migration gate.
            with open(
                os.path.join(workspace, ".eslintrc.json"), "w", encoding="utf-8"
            ) as fh:
                fh.write("{}\n")

            linter = _make_linter()  # active: flat config matched descriptor activation
            master = _Master()
            linter._detect_eslint10_legacy_config(
                {"workspace": workspace, "master": master}
            )

            self.assertTrue(linter.is_active)
            self.assertIsNone(linter.eslint10_legacy_config)
            self.assertTrue(linter.output_sarif)
            self.assertEqual(master.user_notifications, {})

    def test_gate_with_legacy_eslintrc_is_detected(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".eslintrc.json"), "w", encoding="utf-8"
            ) as fh:
                fh.write("{}\n")

            # Linter activated through the descriptor's legacy entry in
            # active_only_if_file_found.
            linter = _make_linter("JAVASCRIPT_ES")
            master = _Master()
            linter._detect_eslint10_legacy_config(
                {"workspace": workspace, "master": master}
            )

            self.assertEqual(linter.eslint10_legacy_config, ".eslintrc.json")
            # SARIF parsing is disabled for the synthetic failure output.
            self.assertFalse(linter.output_sarif)
            self.assertIn(ESLINT10_NOTIFICATION_KEY, master.user_notifications)
            entry = master.user_notifications[ESLINT10_NOTIFICATION_KEY]
            self.assertEqual(entry["values"], ["JAVASCRIPT_ES"])
            self.assertEqual(entry["extras"]["legacy_config"], ".eslintrc.json")
            self.assertEqual(
                entry["extras"]["migration_url"], ESLINT_FLAT_CONFIG_MIGRATION_URL
            )

    def test_gate_with_package_json_eslintconfig_is_detected(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, "package.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump({"name": "demo", "eslintConfig": {"rules": {}}}, fh)

            linter = _make_linter("TYPESCRIPT_ES", "TYPESCRIPT")
            master = _Master()
            linter._detect_eslint10_legacy_config(
                {"workspace": workspace, "master": master}
            )

            self.assertEqual(linter.eslint10_legacy_config, "package.json#eslintConfig")
            entry = master.user_notifications[ESLINT10_NOTIFICATION_KEY]
            self.assertEqual(entry["values"], ["TYPESCRIPT_ES"])

    def test_gate_with_no_config_files_is_noop(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = _make_linter()  # active, but workspace has no eslint config
            master = _Master()
            linter._detect_eslint10_legacy_config(
                {"workspace": workspace, "master": master}
            )

            self.assertIsNone(linter.eslint10_legacy_config)
            self.assertTrue(linter.output_sarif)
            self.assertEqual(master.user_notifications, {})

    def test_gate_is_noop_when_linter_inactive(self):
        # A non-activated or disabled linter (is_active False, e.g. via
        # DISABLE_LINTERS / DISABLE_DESCRIPTORS) is never inspected, even when a
        # legacy config is present.
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".eslintrc.json"), "w", encoding="utf-8"
            ) as fh:
                fh.write("{}\n")

            linter = _make_linter("JAVASCRIPT_ES", is_active=False)
            master = _Master()
            linter._detect_eslint10_legacy_config(
                {"workspace": workspace, "master": master}
            )

            self.assertFalse(linter.is_active)
            self.assertIsNone(linter.eslint10_legacy_config)
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
                linter._detect_eslint10_legacy_config(
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
            self.assertIn("fail until you migrate", notice)

    def test_process_linter_fails_when_legacy_detected(self):
        linter = _make_linter()
        linter.eslint10_legacy_config = ".eslintrc.json"
        return_code, stdout = linter.process_linter()
        self.assertEqual(return_code, 1)
        self.assertIn("migration required", stdout)
        self.assertIn(".eslintrc.json", stdout)
        self.assertIn("✖ 1 problem", stdout)
        self.assertIn(ESLINT_FLAT_CONFIG_MIGRATION_URL, stdout)


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

    def test_template_without_values_placeholder_renders_without_values(self):
        master = _Master()
        register_user_notification(
            master,
            key="announcement",
            template="📣 Read the announcement at https://example.com",
            value=None,
        )
        rendered = build_user_notifications(master)
        self.assertEqual(rendered, ["📣 Read the announcement at https://example.com"])

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
