#!/usr/bin/env python3
"""
Unit tests for Linter class

"""

import contextlib
import json
import os
import tempfile
import unittest
import uuid
from unittest import mock

from megalinter import config, utils
from megalinter.Linter import MAX_PROJECT_EXCLUDE_ARG_BYTES, Linter
from megalinter.linters.JsCpdLinter import JsCpdLinter
from megalinter.linters.StyleLintLinter import StyleLintLinter
from megalinter.MegaLinter import Megalinter

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
)


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

    def build_exclude_forwarding_linter(
        self, workspace, config_values=None, filter_regex_exclude=None
    ):
        linter = Linter.__new__(Linter)
        linter.name = "REPOSITORY_TRIVY"
        linter.request_id = str(uuid.uuid1())
        linter.filter_regex_exclude_descriptor = None
        linter.filter_regex_exclude_linter = filter_regex_exclude
        linter.workspace = workspace
        linter.project_gitignored_directories = []
        linter.project_gitignored_name_directories = []
        config.init_config(linter.request_id, None, config_values or {})
        return linter

    def get_forwarded_exclude_directories(
        self,
        existing_directories,
        config_values=None,
        return_paths=False,
        filter_regex_exclude=None,
    ):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_exclude_forwarding_linter(
                workspace, config_values, filter_regex_exclude
            )
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

    def test_root_anchored_filter_regex_exclude_stays_root_level(self):
        # "^docs/" excludes the ROOT docs directory only: forwarding its
        # candidate at any nesting level would silence findings in
        # packages/a/docs, which the user regex does not exclude
        paths = self.get_forwarded_exclude_directories(
            ["docs", os.path.join("packages", "a", "docs")],
            return_paths=True,
            filter_regex_exclude="^docs/",
        )
        self.assertIn("docs", paths)
        self.assertNotIn("packages/a/docs", paths)

    def test_root_anchored_filter_regex_exclude_dropped_when_absent_at_root(self):
        excluded = self.get_forwarded_exclude_directories(
            [os.path.join("packages", "a", "docs")],
            filter_regex_exclude="^docs/",
        )
        self.assertNotIn("docs", excluded)

    def test_unanchored_filter_regex_exclude_matches_any_nesting_level(self):
        paths = self.get_forwarded_exclude_directories(
            ["docs", os.path.join("packages", "a", "docs")],
            return_paths=True,
            filter_regex_exclude="(^|/)docs/",
        )
        self.assertIn("docs", paths)
        self.assertIn("packages/a/docs", paths)

    def test_walk_never_descends_into_a_known_excluded_directory(self):
        # Excluded directories are not linted, so nothing inside them has to be
        # forwarded: the walk must skip them wherever they are, not only at the
        # workspace root
        visited = []
        real_walk = os.walk

        def counting_walk(top, *args, **kwargs):
            for dir_path, sub_dirs, files in real_walk(top, *args, **kwargs):
                visited.append(dir_path)
                yield dir_path, sub_dirs, files

        with tempfile.TemporaryDirectory() as workspace:
            for directory in [
                ("node_modules", "pkg", "deep"),
                ("src", "node_modules", "pkg", "deep"),
                ("src", ".venv", "lib"),
                ("src", "keep"),
            ]:
                os.makedirs(os.path.join(workspace, *directory))
            linter = self.build_exclude_forwarding_linter(workspace)
            try:
                with mock.patch("megalinter.utils.os.walk", counting_walk):
                    paths = linter.get_project_exclude_directory_paths()
            finally:
                config.delete(linter.request_id)

        self.assertIn("node_modules", paths)
        self.assertIn("src/node_modules", paths)
        self.assertIn("src/.venv", paths)
        descended = [
            path
            for path in visited
            for excluded in ("node_modules", ".venv")
            if excluded in path.replace("\\", "/").split("/")
        ]
        self.assertFalse(descended, f"walk descended into excluded dirs: {descended}")

    def init_exclude_workspace(self, workspace, directories, config_values=None):
        for directory in directories:
            os.makedirs(os.path.join(workspace, *directory))
        request_id = str(uuid.uuid1())
        config.init_config(request_id, None, config_values or {})
        return request_id

    def build_mega_linter_with_project_linters(self, request_id, workspace, regexes):
        linters = []
        for index, regex in enumerate(regexes):
            linter = Linter.__new__(Linter)
            linter.name = f"LINTER_{index}"
            linter.request_id = request_id
            linter.workspace = workspace
            linter.filter_regex_exclude_descriptor = None
            linter.filter_regex_exclude_linter = regex
            linter.project_gitignored_directories = []
            linter.project_gitignored_name_directories = []
            linter.cli_lint_mode = "project"
            linter.cli_lint_mode_project_exclude_arg_name = "-x"
            linter.cli_lint_mode_project_exclude_ignore_file_arg_name = None
            linters += [linter]
        mega_linter = Megalinter.__new__(Megalinter)
        mega_linter.request_id = request_id
        mega_linter.workspace = workspace
        mega_linter.active_linters = linters
        return mega_linter, linters

    @contextlib.contextmanager
    def count_workspace_walks(self):
        walks = []
        real_walk = utils.walk_workspace_excluded_directories

        def counting_walk(*args, **kwargs):
            walks.append(args)
            return real_walk(*args, **kwargs)

        with mock.patch.object(
            utils, "walk_workspace_excluded_directories", counting_walk
        ):
            yield walks

    def test_workspace_is_walked_only_once_for_the_whole_run(self):
        # The walk is cached per process, and worker processes do not share it:
        # the main process primes it for every linter before the pool is created
        with tempfile.TemporaryDirectory() as workspace:
            os.makedirs(os.path.join(workspace, "a", "node_modules"))
            os.makedirs(os.path.join(workspace, "b", "docs"))
            request_id = str(uuid.uuid1())
            config.init_config(request_id, None, {})
            mega_linter, linters = self.build_mega_linter_with_project_linters(
                request_id, workspace, [None, "docs/", "build/", None, "(^|/)d/"]
            )
            try:
                with self.count_workspace_walks() as walks:
                    mega_linter.prepare_project_exclude_directories()
                    for linter in linters:
                        linter.get_project_exclude_directories()
            finally:
                config.delete(request_id)

        self.assertEqual(len(walks), 1, "the workspace must be walked exactly once")
        # Each linter still only receives what its own configuration excludes
        self.assertIn("docs", linters[1].project_exclude_directories)
        self.assertNotIn("docs", linters[0].project_exclude_directories)

    def test_shared_walk_keeps_every_matching_entry_for_every_linter(self):
        # The run-wide walk is done for the UNION of what the linters search, so
        # a located directory must be filed under each entry it matches: here
        # one linter excludes "docs" and the other the exact nested path
        with tempfile.TemporaryDirectory() as workspace:
            os.makedirs(os.path.join(workspace, "packages", "a", "docs"))
            request_id = str(uuid.uuid1())
            config.init_config(
                request_id, None, {"ADDITIONAL_EXCLUDED_DIRECTORIES": "docs"}
            )
            mega_linter, linters = self.build_mega_linter_with_project_linters(
                request_id, workspace, [None, "packages/a/docs/"]
            )
            try:
                mega_linter.prepare_project_exclude_directories()
                paths = [
                    linter.get_project_exclude_directory_paths() for linter in linters
                ]
            finally:
                config.delete(request_id)
        for linter_paths in paths:
            self.assertIn("packages/a/docs", linter_paths)

    def test_file_listing_walk_feeds_the_forwarding_lookup(self):
        # In full-codebase mode MegaLinter already walks the workspace to list
        # the files, pruning the very same directories: the forwarding lookup
        # rides on it instead of walking a second time
        with tempfile.TemporaryDirectory() as workspace:
            request_id = self.init_exclude_workspace(
                workspace,
                [("src", "node_modules"), ("infrastructure", "cdk.out"), ("src", "k")],
                {"ADDITIONAL_EXCLUDED_DIRECTORIES": "cdk.out"},
            )
            mega_linter, linters = self.build_mega_linter_with_project_linters(
                request_id, workspace, [None]
            )
            try:
                mega_linter.list_files_all()
                with self.count_workspace_walks() as walks:
                    mega_linter.prepare_project_exclude_directories()
                    paths = linters[0].get_project_exclude_directory_paths()
            finally:
                config.delete(request_id)

        self.assertFalse(walks, "the workspace must not be walked a second time")
        self.assertIn("src/node_modules", paths)
        self.assertIn("infrastructure/cdk.out", paths)

    def test_file_listing_harvest_matches_the_standalone_walk(self):
        with tempfile.TemporaryDirectory() as workspace:
            request_id = self.init_exclude_workspace(
                workspace,
                [
                    ("src", "node_modules", "pkg"),
                    ("infrastructure", "cdk.out"),
                    ("packages", "a", ".venv"),
                    ("src", "keep"),
                ],
                {"ADDITIONAL_EXCLUDED_DIRECTORIES": "cdk.out"},
            )
            excluded = utils.get_excluded_directories(request_id)
            try:
                utils.clear_excluded_directories_caches(request_id)
                walked = utils.find_workspace_excluded_directories(
                    request_id, workspace, excluded
                )
                utils.clear_excluded_directories_caches(request_id)
                mega_linter = Megalinter.__new__(Megalinter)
                mega_linter.request_id = request_id
                mega_linter.workspace = workspace
                mega_linter.list_files_all()
                harvested = utils.find_workspace_excluded_directories(
                    request_id, workspace, excluded
                )
            finally:
                config.delete(request_id)
        self.assertEqual(walked, harvested)

    def test_linter_without_forwarding_mechanism_skips_the_lookup(self):
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_exclude_forwarding_linter(workspace)
            linter.cli_lint_mode_project_exclude_arg_name = None
            linter.cli_lint_mode_project_exclude_ignore_file_arg_name = None
            try:
                self.assertFalse(linter.has_project_exclude_forwarding())
                linter.cli_lint_mode_project_exclude_arg_name = "-x"
                self.assertTrue(linter.has_project_exclude_forwarding())
            finally:
                config.delete(linter.request_id)
        # A custom linter class always hooks into the forwarding somewhere
        style_lint = StyleLintLinter.__new__(StyleLintLinter)
        style_lint.cli_lint_mode_project_exclude_arg_name = None
        style_lint.cli_lint_mode_project_exclude_ignore_file_arg_name = None
        self.assertTrue(style_lint.has_project_exclude_forwarding())

    def test_exclude_arguments_stay_below_the_system_argument_limit(self):
        # One value per located directory can exceed MAX_ARG_STRLEN on a large
        # monorepo, and execve then fails with E2BIG instead of running the linter
        values = [f"./packages/pkg{index:05d}/src/__pycache__" for index in range(4000)]
        linter = Linter.__new__(Linter)
        linter.linter_name = "bandit"
        linter.log_lines_pre = []
        kept = linter.limit_project_exclude_values(values)
        self.assertLess(len(kept), len(values))
        self.assertLessEqual(
            len(",".join(kept).encode("utf-8")), MAX_PROJECT_EXCLUDE_ARG_BYTES
        )
        # Shallowest paths are the ones kept: they cover the most files
        self.assertIn(values[0], kept)
        self.assertTrue(
            any("were sent to bandit" in line for line in linter.log_lines_pre)
        )

    def test_workspace_template_uses_paths_in_generated_ignore_files(self):
        # build_project_exclude_arguments and build_project_exclude_ignore_file
        # share one predicate, so a {{WORKSPACE}} template gets paths in both
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_exclude_forwarding_linter(
                workspace, {"ADDITIONAL_EXCLUDED_DIRECTORIES": "cdk.out"}
            )
            linter.report_folder = os.path.join(workspace, "megalinter-reports")
            linter.linter_name = "trivy"
            linter.sarif_output_file = None
            linter.final_config_file = None
            linter.log_lines_pre = []
            try:
                os.makedirs(os.path.join(workspace, "infrastructure", "cdk.out"))
                ignore_file = linter.build_project_exclude_ignore_file(
                    "test-ignore.txt", line_template="{{WORKSPACE}}/{{DIR}}"
                )
                with open(ignore_file, encoding="utf-8") as file_handler:
                    lines = [line.strip().replace("\\", "/") for line in file_handler]
            finally:
                config.delete(linter.request_id)
        expected = os.path.join(workspace, "infrastructure/cdk.out").replace("\\", "/")
        self.assertIn(expected, lines)
        self.assertTrue(all("{{" not in line for line in lines), lines)

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

    def test_sarif_suppressed_results_are_not_counted(self):
        # A result silenced in source (ex: # nosemgrep) is not a warning (#9373)
        linter = Linter.__new__(Linter)
        linter.sarif_output_file = os.path.join(
            REPO_ROOT,
            ".automation",
            "test",
            "sarif_reports",
            "REPOSITORY_SEMGREP.sarif",
        )
        linter.sarif_default_output_file = None

        self.assertEqual(1, linter.get_sarif_result_count("", "warning"))
        self.assertEqual(0, linter.get_sarif_result_count("", "error"))

    def test_sarif_count_mode_skips_suppressed_results(self):
        # cli_lint_errors_count: sarif (devskim) parses the SARIF from stdout
        linter = Linter.__new__(Linter)
        linter.output_sarif = False
        linter.cli_lint_errors_count = "sarif"
        stdout = json.dumps(
            {
                "runs": [
                    {
                        "results": [
                            {"level": "error"},
                            {"level": "error", "suppressions": [{"kind": "inSource"}]},
                            {
                                "level": "error",
                                "suppressions": [
                                    {"kind": "external", "status": "underReview"}
                                ],
                            },
                        ]
                    }
                ]
            }
        )

        result = linter.get_result_count(
            stdout, "error", "cli_lint_errors_count", "cli_lint_errors_regex"
        )

        self.assertEqual(2, result)

    def test_gitignored_directories_are_forwarded_by_path(self):
        # With IGNORE_GITIGNORED_FILES, the folders git ignores (ex: vendor/)
        # are not linted, so project-mode linters must skip them too (#8955)
        with tempfile.TemporaryDirectory() as workspace:
            linter = self.build_exclude_forwarding_linter(workspace)
            linter.project_gitignored_directories = ["lib", "tools/a/vendor", "vendor"]
            # A tracked src/lib exists: "lib" is only sent as a path
            linter.project_gitignored_name_directories = ["tools/a/vendor", "vendor"]
            try:
                excluded = linter.get_project_exclude_directories()
                paths = linter.get_project_exclude_directory_paths()
            finally:
                config.delete(linter.request_id)
        self.assertIn("vendor", excluded)
        self.assertIn("tools/a/vendor", excluded)
        self.assertNotIn("lib", excluded)
        self.assertIn("lib", paths)
        self.assertIn("tools/a/vendor", paths)

    def build_project_paths_linter(self, config_content, regex):
        linter = Linter.__new__(Linter)
        linter.cli_lint_mode_project_config_paths_regex = regex
        linter.cli_lint_mode_project_extra_args_after = ["."]
        linter.config_file = None
        if config_content is not None:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".xml", delete=False, encoding="utf-8"
            ) as config_file:
                config_file.write(config_content)
            linter.config_file = config_file.name
        return linter

    def assert_project_paths_defined_in_config(self, config_content, regex, expected):
        linter = self.build_project_paths_linter(config_content, regex)
        try:
            self.assertEqual(expected, linter.is_project_paths_defined_in_config())
        finally:
            if linter.config_file is not None:
                os.remove(linter.config_file)

    def test_project_paths_defined_in_config_skip_project_args(self):
        # "." would override the paths of phpcs.xml and analyze vendor/ (#8955)
        self.assert_project_paths_defined_in_config(
            "<ruleset><file>src</file></ruleset>", "<file>", True
        )

    def test_project_args_kept_when_config_defines_no_paths(self):
        self.assert_project_paths_defined_in_config(
            "<ruleset><rule ref='PSR12'/></ruleset>", "<file>", False
        )

    def test_project_args_kept_without_config_file(self):
        self.assert_project_paths_defined_in_config(None, "<file>", False)

    def test_project_args_kept_without_config_paths_regex(self):
        self.assert_project_paths_defined_in_config(
            "<ruleset><file>src</file></ruleset>", None, False
        )

    def build_gitignored_mega_linter(self, repo_root):
        mega_linter = Megalinter.__new__(Megalinter)
        mega_linter.request_id = str(uuid.uuid1())
        mega_linter.github_workspace = repo_root
        mega_linter.workspace = repo_root
        config.init_config(mega_linter.request_id, None, {})
        return mega_linter

    def test_gitignored_directories_are_relative_to_the_workspace(self):
        with tempfile.TemporaryDirectory() as repo_root:
            mega_linter = self.build_gitignored_mega_linter(repo_root)
            try:
                self.assertEqual(
                    ["packages/a/build", "vendor"],
                    mega_linter.get_gitignored_directories(
                        ["vendor/**", "stub.php", "packages/a/build/**"]
                    ),
                )
                # Workspace in a sub-folder of the repository: paths are rebased,
                # and directories outside of the workspace are dropped
                mega_linter.workspace = os.path.join(repo_root, "packages")
                self.assertEqual(
                    ["a/build"],
                    mega_linter.get_gitignored_directories(
                        ["vendor/**", "packages/a/build/**"]
                    ),
                )
            finally:
                config.delete(mega_linter.request_id)

    def test_gitignored_directories_inside_excluded_ones_are_skipped(self):
        # Nested node_modules escape the git pathspec exclusions, but they are
        # already forwarded through the excluded directory name
        with tempfile.TemporaryDirectory() as repo_root:
            mega_linter = self.build_gitignored_mega_linter(repo_root)
            try:
                gitignored = mega_linter.get_gitignored_directories(
                    ["packages/a/node_modules/**", "packages/a/dist/**"]
                )
            finally:
                config.delete(mega_linter.request_id)
        self.assertEqual(["packages/a/dist"], gitignored)

    def test_gitignored_directories_sharing_a_tracked_name_are_path_only(self):
        # A gitignored /lib/ forwarded as **/lib/** would also skip src/lib
        mega_linter = Megalinter.__new__(Megalinter)
        self.assertEqual(
            ["tools/vendor", "vendor"],
            mega_linter.get_unambiguous_gitignored_directories(
                ["lib", "tools/vendor", "vendor"],
                [
                    "src/lib/main.py",
                    "lib/generated.py",
                    "vendor/pkg/lib/file.php",
                    "README.md",
                ],
            ),
        )

    def test_jscpd_generated_config_keeps_configured_paths(self):
        # Without "." in project mode, jscpd analyzes the paths of its config,
        # resolved against the config directory: the generated config lives in
        # the report folder, so they must be rebased on the original one
        with tempfile.TemporaryDirectory() as workspace:
            config_file = os.path.join(workspace, ".jscpd.json")
            with open(config_file, "w", encoding="utf-8") as file_handler:
                file_handler.write('{"path": ["src"], "ignore": ["**/*.md"]}')
            linter = JsCpdLinter.__new__(JsCpdLinter)
            linter.name = "COPYPASTE_JSCPD"
            linter.report_folder = os.path.join(workspace, "megalinter-reports")
            linter.log_lines_pre = []
            with mock.patch.object(
                JsCpdLinter, "get_project_exclude_directories", return_value=["vendor"]
            ):
                cmd = linter.manage_excluded_directories_config(
                    ["jscpd", "-c", config_file]
                )
            with open(cmd[2], encoding="utf-8") as file_handler:
                generated = json.load(file_handler)
        self.assertEqual([os.path.join(workspace, "src")], generated["path"])
        self.assertEqual(["**/*.md", "**/vendor/**"], generated["ignore"])
