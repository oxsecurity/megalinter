#!/usr/bin/env python3
"""
Unit tests for Linter class

"""

import os
import tempfile
import unittest
import uuid
from unittest import mock

from megalinter import config, utils
from megalinter.Linter import Linter
from megalinter.linters.StyleLintLinter import StyleLintLinter


class LinterTest(unittest.TestCase):
    @staticmethod
    def build_activation_params(enable_linters, disable_linters, priority):
        return {
            "default_linter_activation": len(enable_linters) == 0,
            "enable_linters": enable_linters,
            "disable_linters": disable_linters,
            "enable_descriptors": [],
            "disable_descriptors": [],
            "enable_disable_linters_priority": priority,
        }

    def run_activation(self, enable_linters, disable_linters, priority):
        linter = Linter.__new__(Linter)
        linter.name = "JAVASCRIPT_ES"
        linter.descriptor_id = "JAVASCRIPT"
        linter.request_id = str(uuid.uuid1())
        linter.activation_rules = []
        linter.manage_activation(
            self.build_activation_params(enable_linters, disable_linters, priority)
        )
        return linter.is_active

    def test_activation_overlap_default_priority_keeps_enabled(self):
        # Backward compatibility: ENABLE_LINTERS wins when a linter is in both lists
        self.assertTrue(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_ES"], "ENABLE")
        )

    def test_activation_overlap_disable_priority_skips(self):
        # New behavior: DISABLE_LINTERS overrides ENABLE_LINTERS when priority is DISABLE
        self.assertFalse(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_ES"], "DISABLE")
        )

    def test_activation_enable_only_with_disable_priority_stays_enabled(self):
        # Disable list must not over-reach when the linter is only in ENABLE_LINTERS
        self.assertTrue(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_STANDARD"], "DISABLE")
        )

    def test_activation_disable_only_is_skipped(self):
        self.assertFalse(self.run_activation([], ["JAVASCRIPT_ES"], "ENABLE"))

    def test_activation_unknown_priority_falls_back_to_enable(self):
        # Any value other than DISABLE preserves the default ENABLE-wins behavior
        self.assertTrue(
            self.run_activation(["JAVASCRIPT_ES"], ["JAVASCRIPT_ES"], "WHATEVER")
        )

    def build_exclude_forwarding_linter(self, workspace, config_values=None):
        linter = Linter.__new__(Linter)
        linter.name = "REPOSITORY_TRIVY"
        linter.request_id = str(uuid.uuid1())
        linter.filter_regex_exclude_descriptor = None
        linter.filter_regex_exclude_linter = None
        linter.workspace = workspace
        config.init_config(linter.request_id, None, config_values or {})
        return linter

    def get_forwarded_exclude_directories(
        self, existing_directories, config_values=None, return_paths=False
    ):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_exclude_forwarding_linter(workspace, config_values)
            try:
                for directory in existing_directories:
                    os.makedirs(os.path.join(workspace, directory))
                if return_paths is True:
                    return linter.get_project_exclude_directory_paths()
                return linter.get_project_exclude_directories()
            finally:
                config.delete(linter.request_id)

    def test_report_folder_is_forwarded_even_when_it_does_not_exist(self):
        # Reporters write in the report folder while linters run: a project-mode
        # linter must skip it even when it is not created yet at command build time
        excluded = self.get_forwarded_exclude_directories([])
        self.assertIn("megalinter-reports", excluded)

    def test_other_excluded_directories_are_forwarded_only_when_existing(self):
        excluded = self.get_forwarded_exclude_directories(["node_modules"])
        self.assertIn("node_modules", excluded)
        self.assertNotIn(".venv", excluded)

    def test_nested_excluded_directories_are_forwarded(self):
        # EXCLUDED_DIRECTORIES are basenames excluded at any nesting level:
        # a directory that only exists deeper in the tree must be forwarded too
        excluded = self.get_forwarded_exclude_directories(
            [os.path.join("infrastructure", "cdk.out")],
            {"ADDITIONAL_EXCLUDED_DIRECTORIES": "cdk.out"},
        )
        self.assertIn("cdk.out", excluded)

    def test_nested_excluded_directory_paths_are_collected(self):
        # {{WORKSPACE}} anchored exclusion arguments need real paths
        paths = self.get_forwarded_exclude_directories(
            [
                os.path.join("infrastructure", "cdk.out"),
                os.path.join("apps", "web", "cdk.out"),
            ],
            {"ADDITIONAL_EXCLUDED_DIRECTORIES": "cdk.out"},
            return_paths=True,
        )
        self.assertIn("infrastructure/cdk.out", paths)
        self.assertIn("apps/web/cdk.out", paths)
        self.assertNotIn("cdk.out", paths)

    def test_excluded_directories_walk_does_not_descend_into_matches(self):
        # A directory nested inside an already excluded one is not reported
        excluded = self.get_forwarded_exclude_directories(
            [os.path.join("node_modules", "some-package", ".venv")]
        )
        self.assertIn("node_modules", excluded)
        self.assertNotIn(".venv", excluded)

    def test_default_excluded_directories_are_pruned_when_list_is_overridden(self):
        # EXCLUDED_DIRECTORIES REPLACES the defaults, so overriding it with a
        # single entry must not turn the lookup into a full walk of node_modules
        walked = []
        real_walk = os.walk

        def counting_walk(top, *args, **kwargs):
            for dir_path, sub_dirs, files in real_walk(top, *args, **kwargs):
                walked.append(dir_path)
                yield dir_path, sub_dirs, files

        with tempfile.TemporaryDirectory() as workspace:
            os.makedirs(os.path.join(workspace, "node_modules", "pkg", "deep"))
            os.makedirs(os.path.join(workspace, "infrastructure", "cdk.out"))
            linter = self.build_exclude_forwarding_linter(
                workspace, {"EXCLUDED_DIRECTORIES": "cdk.out"}
            )
            try:
                with mock.patch("megalinter.utils.os.walk", counting_walk):
                    excluded = linter.get_project_exclude_directories()
            finally:
                config.delete(linter.request_id)

        self.assertIn("cdk.out", excluded)
        self.assertFalse(
            [path for path in walked if "node_modules" in path],
            "walk must not descend into node_modules",
        )

    def test_excluded_directories_caches_are_cleared_with_the_config(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_exclude_forwarding_linter(workspace)
            os.makedirs(os.path.join(workspace, "node_modules"))
            linter.get_project_exclude_directories()
            self.assertTrue(
                [
                    key
                    for key in utils._workspace_excluded_directories_cache
                    if key[0] == str(linter.request_id)
                ]
            )
            config.delete(linter.request_id)
            self.assertNotIn(str(linter.request_id), utils._excluded_directories_cache)
            self.assertFalse(
                [
                    key
                    for key in utils._workspace_excluded_directories_cache
                    if key[0] == str(linter.request_id)
                ]
            )

    def build_exclude_arguments(self, arg_value, existing_directories):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_exclude_forwarding_linter(
                workspace, {"ADDITIONAL_EXCLUDED_DIRECTORIES": "cdk.out"}
            )
            linter.cli_lint_mode_project_exclude_arg_name = "-x"
            linter.cli_lint_mode_project_exclude_arg_value = arg_value
            linter.cli_lint_mode_project_exclude_separator = None
            linter.cli_lint_mode_project_exclude_seed_values = []
            linter.cli_lint_mode_project_exclude_config_key = None
            linter.final_config_file = None
            linter.report_folder = os.path.join(workspace, "megalinter-reports")
            linter.sarif_output_file = None
            linter.linter_name = "trivy"
            try:
                for directory in existing_directories:
                    os.makedirs(os.path.join(workspace, directory))
                with mock.patch.object(Linter, "log_project_exclude_forwarding"):
                    return linter.build_project_exclude_arguments()
            finally:
                config.delete(linter.request_id)

    def test_dir_template_sends_bare_directory_names(self):
        args = self.build_exclude_arguments(
            "**/{{DIR}}/**", [os.path.join("infrastructure", "cdk.out")]
        )
        self.assertIn("**/cdk.out/**", args)

    def test_dir_path_template_sends_located_paths(self):
        # A root-anchored template can not match a nested directory by name:
        # {{DIR_PATH}} emits one value per location actually found
        args = self.build_exclude_arguments(
            "./{{DIR_PATH}}",
            [os.path.join("infrastructure", "cdk.out"), "cdk.out"],
        )
        self.assertIn("./infrastructure/cdk.out", args)
        self.assertIn("./cdk.out", args)

    def test_replace_vars_with_default_variables(self):
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = "test_sarif_output_file"
        linter.report_folder = "test_report_folder"
        linter.workspace = "test_workspace"

        args = ["{{SARIF_OUTPUT_FILE}}", "{{REPORT_FOLDER}}", "{{WORKSPACE}}"]
        additional_variables = None

        replaced_args = linter.replace_vars(args, additional_variables)

        self.assertEqual(
            ["test_sarif_output_file", "test_report_folder", "test_workspace"],
            replaced_args,
        )

    def test_replace_vars_with_unknown_variable(self):
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = "test_sarif_output_file"
        linter.report_folder = "test_report_folder"
        linter.workspace = "test_workspace"

        args = ["{{UNKNOWN_VAR}}"]
        additional_variables = None

        replaced_args = linter.replace_vars(args, additional_variables)

        self.assertEqual(["{{UNKNOWN_VAR}}"], replaced_args)

    def test_replace_vars_with_additional_variables(self):
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = "test_sarif_output_file"
        linter.report_folder = "test_report_folder"
        linter.workspace = "test_workspace"

        args = ["{{ADDITIONAL_VAR}}"]
        additional_variables = {"{{ADDITIONAL_VAR}}": "test_additional_var"}

        replaced_args = linter.replace_vars(args, additional_variables)

        self.assertEqual(["test_additional_var"], replaced_args)

    def test_remove_command_args_removes_existing_args(self):
        linter = Linter.__new__(Linter)
        linter.name = "CSS_STYLELINT"
        linter.cli_command_remove_args = ["--formatter", "json"]

        cmd = linter.remove_command_args(
            ["stylelint", "--formatter", "json", "--config", "conf.json"]
        )

        self.assertEqual(["stylelint", "--config", "conf.json"], cmd)

    def test_remove_command_args_ignores_missing_args(self):
        # Missing arguments must not raise ValueError: they can be conditionally
        # added by linter subclasses after the removal has been performed
        linter = Linter.__new__(Linter)
        linter.name = "CSS_STYLELINT"
        linter.cli_command_remove_args = ["--config-basedir"]

        cmd = linter.remove_command_args(["stylelint", "--config", "conf.json"])

        self.assertEqual(["stylelint", "--config", "conf.json"], cmd)

    def test_stylelint_skips_config_basedir_when_removed_by_user(self):
        linter = StyleLintLinter.__new__(StyleLintLinter)
        linter.name = "CSS_STYLELINT"
        linter.cli_lint_mode = "list_of_files"
        linter.cli_command_remove_args = ["--config-basedir"]

        with (
            mock.patch.object(Linter, "build_lint_command", return_value=["stylelint"]),
            mock.patch("os.path.isdir", return_value=True),
        ):
            cmd = linter.build_lint_command()

        self.assertEqual(["stylelint"], cmd)

    def test_stylelint_adds_config_basedir_by_default(self):
        linter = StyleLintLinter.__new__(StyleLintLinter)
        linter.name = "CSS_STYLELINT"
        linter.cli_lint_mode = "list_of_files"
        linter.cli_command_remove_args = []

        with (
            mock.patch.object(Linter, "build_lint_command", return_value=["stylelint"]),
            mock.patch("os.path.isdir", return_value=True),
        ):
            cmd = linter.build_lint_command()

        self.assertEqual(["stylelint", "--config-basedir", "/node-deps"], cmd)

    def test_stylelint_does_not_duplicate_user_defined_config_basedir(self):
        linter = StyleLintLinter.__new__(StyleLintLinter)
        linter.name = "CSS_STYLELINT"
        linter.cli_lint_mode = "list_of_files"
        linter.cli_command_remove_args = []

        with (
            mock.patch.object(
                Linter,
                "build_lint_command",
                return_value=["stylelint", "--config-basedir", "/tmp"],
            ),
            mock.patch("os.path.isdir", return_value=True),
        ):
            cmd = linter.build_lint_command()

        self.assertEqual(["stylelint", "--config-basedir", "/tmp"], cmd)

    def test_sarif_zero_results_is_not_a_warning(self):
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = None
        linter.sarif_default_output_file = None
        sarif = """\
runs:
  - tool:
      driver: {}
    results:
      - level: note
        locations:
          - physicalLocation: {}
"""

        with self.assertNoLogs(level="WARNING"):
            result = linter.get_sarif_result_count(sarif, "error")

        self.assertEqual(0, result)
