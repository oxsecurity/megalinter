#!/usr/bin/env python3
"""
Additional regression tests for the gommitlint linter implementation
"""

import uuid
from unittest import TestCase

from megalinter import config, utilstest
from megalinter.tests.test_megalinter.LinterTestRoot import LinterTestRoot


class repository_gommitlint_linter_test(TestCase, LinterTestRoot):
    descriptor_id = "REPOSITORY"
    linter_name = "gommitlint"

    @staticmethod
    def _extract_base_branch_args(command):
        base_branch_args = []
        for index, arg in enumerate(command):
            if arg == "--base-branch" and index + 1 < len(command):
                base_branch_args.extend([arg, command[index + 1]])
        return base_branch_args

    def test_single_base_branch_string_is_forwarded(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        config.set_value(self.request_id, "REPOSITORY_GOMMITLINT_BASE_BRANCH", "main")

        linter = self.get_linter_instance(self.request_id)
        command = linter.build_lint_command()

        self.assertEqual(
            ["--base-branch", "main"], self._extract_base_branch_args(command)
        )

    def test_multiple_base_branches_are_forwarded(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        config.set_value(
            self.request_id,
            "REPOSITORY_GOMMITLINT_BASE_BRANCH",
            ["main", "release/1.x"],
        )

        linter = self.get_linter_instance(self.request_id)
        command = linter.build_lint_command()

        self.assertEqual(
            ["--base-branch", "main,release/1.x"],
            self._extract_base_branch_args(command),
        )

    def test_base_branch_none_disables_ci_auto_detection(self):
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup({"request_id": self.request_id})
        config.set_value(self.request_id, "REPOSITORY_GOMMITLINT_BASE_BRANCH", "none")

        linter = self.get_linter_instance(self.request_id)
        command = linter.build_lint_command()

        self.assertNotIn("--base-branch", command)
        self.assertEqual("1", linter._cached_subprocess_env["GOMMITLINT_NO_CI_DETECT"])
