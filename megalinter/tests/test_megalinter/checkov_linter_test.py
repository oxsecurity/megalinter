#!/usr/bin/env python3
"""
Unit tests for CheckovLinter automatic secrets framework delegation.

When another active linter of the run is a dedicated secret scanner
(betterleaks, kingfisher, secretlint, trufflehog), checkov must be called
with "--skip-framework secrets" to avoid duplicating the secrets scan,
unless the user already expressed a framework intent through
REPOSITORY_CHECKOV_ARGUMENTS or the checkov config file.
"""

import os
import tempfile
import unittest
import uuid
from types import SimpleNamespace

from megalinter import config, linter_factory, utils


def _build_checkov_linter(request_id, workspace, extra_config=None):
    runtime_config = {"default_workspace": workspace}
    if extra_config is not None:
        runtime_config.update(extra_config)
    config.set_config(request_id, runtime_config)
    base_params = {
        "default_linter_activation": True,
        "enable_descriptors": [],
        "enable_linters": [],
        "disable_descriptors": [],
        "disable_linters": [],
        "disable_errors_linters": [],
        "github_workspace": workspace,
        "workspace": workspace,
        "linter_rules_path": workspace,
        "default_rules_location": utils.get_default_rules_location(),
        "post_linter_status": False,
        "request_id": request_id,
    }
    return linter_factory.build_linter("REPOSITORY", "checkov", base_params)


def _master_with_active_linters(linter_names):
    return SimpleNamespace(
        active_linters=[SimpleNamespace(name=name) for name in linter_names]
    )


class CheckovLinterTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())

    def tearDown(self):
        config.delete(self.request_id)

    def _lint_command_with_betterleaks(self, checkov):
        checkov.master = _master_with_active_linters(
            ["REPOSITORY_CHECKOV", "REPOSITORY_BETTERLEAKS"]
        )
        return checkov.build_lint_command()

    def _assert_single_skip_framework(self, cmd, expected_value):
        self.assertEqual(cmd.count("--skip-framework"), 1)
        self.assertEqual(cmd[cmd.index("--skip-framework") + 1], expected_value)

    def test_skip_framework_added_when_secret_scanner_active(self):
        with tempfile.TemporaryDirectory() as workspace:
            checkov = _build_checkov_linter(self.request_id, workspace)
            cmd = self._lint_command_with_betterleaks(checkov)
            self._assert_single_skip_framework(cmd, "secrets")

    def test_skip_framework_added_for_each_dedicated_secret_scanner(self):
        for scanner in [
            "REPOSITORY_BETTERLEAKS",
            "REPOSITORY_KINGFISHER",
            "REPOSITORY_SECRETLINT",
            "REPOSITORY_TRUFFLEHOG",
        ]:
            with tempfile.TemporaryDirectory() as workspace:
                checkov = _build_checkov_linter(self.request_id, workspace)
                checkov.master = _master_with_active_linters(
                    ["REPOSITORY_CHECKOV", scanner]
                )
                cmd = checkov.build_lint_command()
                self.assertIn(
                    "--skip-framework",
                    cmd,
                    f"--skip-framework should be added when {scanner} is active",
                )

    def test_skip_framework_not_added_without_secret_scanner(self):
        with tempfile.TemporaryDirectory() as workspace:
            checkov = _build_checkov_linter(self.request_id, workspace)
            # Standalone run: checkov is the only active linter
            checkov.master = _master_with_active_linters(["REPOSITORY_CHECKOV"])
            cmd = checkov.build_lint_command()
            self.assertNotIn("--skip-framework", cmd)
            self.assertNotIn("secrets", cmd)

    def test_skip_framework_not_added_without_master(self):
        with tempfile.TemporaryDirectory() as workspace:
            checkov = _build_checkov_linter(self.request_id, workspace)
            # Linter instantiated without orchestrator: must not crash
            checkov.master = None
            cmd = checkov.build_lint_command()
            self.assertNotIn("--skip-framework", cmd)

    def test_user_skip_framework_argument_wins(self):
        with tempfile.TemporaryDirectory() as workspace:
            checkov = _build_checkov_linter(
                self.request_id,
                workspace,
                {"REPOSITORY_CHECKOV_ARGUMENTS": "--skip-framework dockerfile"},
            )
            cmd = self._lint_command_with_betterleaks(checkov)
            self._assert_single_skip_framework(cmd, "dockerfile")
            self.assertNotIn("secrets", cmd)

    def test_user_framework_argument_wins(self):
        with tempfile.TemporaryDirectory() as workspace:
            checkov = _build_checkov_linter(
                self.request_id,
                workspace,
                {"REPOSITORY_CHECKOV_ARGUMENTS": "--framework terraform"},
            )
            checkov.master = _master_with_active_linters(
                ["REPOSITORY_CHECKOV", "REPOSITORY_TRUFFLEHOG"]
            )
            cmd = checkov.build_lint_command()
            self.assertIn("--framework", cmd)
            self.assertNotIn("--skip-framework", cmd)

    def test_config_file_framework_key_wins(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".checkov.yml"), "w", encoding="utf-8"
            ) as config_file:
                config_file.write("framework:\n  - terraform\n")
            checkov = _build_checkov_linter(self.request_id, workspace)
            self.assertIsNotNone(
                checkov.config_file, ".checkov.yml should have been resolved"
            )
            checkov.master = _master_with_active_linters(
                ["REPOSITORY_CHECKOV", "REPOSITORY_BETTERLEAKS"]
            )
            cmd = checkov.build_lint_command()
            self.assertNotIn("--skip-framework", cmd)

    def test_config_file_skip_framework_key_wins(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".checkov.yml"), "w", encoding="utf-8"
            ) as config_file:
                config_file.write("skip-framework:\n  - dockerfile\n")
            checkov = _build_checkov_linter(self.request_id, workspace)
            checkov.master = _master_with_active_linters(
                ["REPOSITORY_CHECKOV", "REPOSITORY_BETTERLEAKS"]
            )
            cmd = checkov.build_lint_command()
            self.assertNotIn("--skip-framework", cmd)

    def test_config_file_without_framework_key_keeps_skip(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(
                os.path.join(workspace, ".checkov.yml"), "w", encoding="utf-8"
            ) as config_file:
                config_file.write("quiet: true\n")
            checkov = _build_checkov_linter(self.request_id, workspace)
            checkov.master = _master_with_active_linters(
                ["REPOSITORY_CHECKOV", "REPOSITORY_BETTERLEAKS"]
            )
            cmd = checkov.build_lint_command()
            self.assertEqual(cmd.count("--skip-framework"), 1)

    def test_build_lint_command_is_idempotent(self):
        with tempfile.TemporaryDirectory() as workspace:
            checkov = _build_checkov_linter(self.request_id, workspace)
            checkov.master = _master_with_active_linters(
                ["REPOSITORY_CHECKOV", "REPOSITORY_BETTERLEAKS"]
            )
            first_cmd = checkov.build_lint_command()
            second_cmd = checkov.build_lint_command()
            self.assertEqual(first_cmd.count("--skip-framework"), 1)
            self.assertEqual(second_cmd.count("--skip-framework"), 1)
            self.assertEqual(second_cmd.count("secrets"), 1)


if __name__ == "__main__":
    unittest.main()
