#!/usr/bin/env python3
"""
Unit tests for SqlFluffLinter excluded directories forwarding

"""

import os
import tempfile
import unittest
import uuid

from megalinter.linters.SqlFluffLinter import SqlFluffLinter


class sqlfluff_linter_test(unittest.TestCase):
    def build_linter(self, workspace, report_folder, user_config_content=None):
        linter = SqlFluffLinter.__new__(SqlFluffLinter)
        linter.name = "SQL_SQLFLUFF"
        linter.linter_name = "sqlfluff"
        linter.request_id = str(uuid.uuid1())
        linter.workspace = workspace
        linter.report_folder = report_folder
        linter.log_lines_pre = []
        linter.project_exclude_directories = ["megalinter-reports", "node_modules"]
        linter.final_config_file = None
        if user_config_content is not None:
            user_config_file = os.path.join(workspace, ".sqlfluff")
            with open(user_config_file, "w", encoding="utf-8") as file_handler:
                file_handler.write(user_config_content)
            linter.final_config_file = user_config_file
        return linter

    def run_forwarding(self, user_config_content=None):
        with tempfile.TemporaryDirectory() as workspace:
            report_folder = os.path.join(workspace, "megalinter-reports")
            linter = self.build_linter(workspace, report_folder, user_config_content)
            cmd = linter.manage_excluded_directories_config(
                ["sqlfluff", "lint", "--config", ".sqlfluff", "."]
            )
            generated_file = os.path.join(report_folder, "sqlfluff-megalinter.cfg")
            with open(generated_file, encoding="utf-8") as file_handler:
                generated_content = file_handler.read()
            workspace_entries = sorted(os.listdir(workspace))
            return cmd, generated_content, workspace_entries

    def test_excluded_directories_are_added_to_ignore_paths(self):
        cmd, generated_content, _ = self.run_forwarding("[sqlfluff]\ndialect = ansi\n")
        self.assertIn(
            "ignore_paths = megalinter-reports/,node_modules/", generated_content
        )
        # The user configuration is preserved in the generated copy
        self.assertIn("dialect = ansi", generated_content)
        self.assertIn("--config", cmd)
        self.assertTrue(
            cmd[cmd.index("--config") + 1].endswith("sqlfluff-megalinter.cfg")
        )

    def test_user_ignore_paths_are_kept(self):
        _, generated_content, _ = self.run_forwarding(
            "[sqlfluff]\ndialect = ansi\nignore_paths = target/\n"
        )
        self.assertIn(
            "ignore_paths = target/,megalinter-reports/,node_modules/",
            generated_content,
        )

    def test_nothing_is_written_in_the_workspace(self):
        # MegaLinter must never create files in the analyzed sources: a file
        # appearing there crashes the project-mode linters walking the tree
        _, _, workspace_entries = self.run_forwarding("[sqlfluff]\ndialect = ansi\n")
        self.assertEqual([".sqlfluff", "megalinter-reports"], workspace_entries)

    def test_generated_config_without_user_config(self):
        cmd, generated_content, workspace_entries = self.run_forwarding()
        self.assertIn("[sqlfluff]", generated_content)
        self.assertIn(
            "ignore_paths = megalinter-reports/,node_modules/", generated_content
        )
        self.assertEqual(["megalinter-reports"], workspace_entries)
