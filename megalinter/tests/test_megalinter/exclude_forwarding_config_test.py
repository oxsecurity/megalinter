#!/usr/bin/env python3
"""
Unit tests for the preservation of the user's own exclusions (config files,
ignore files, tool defaults, ARGUMENTS) when MegaLinter forwards excluded
directories to project-mode linters (issue #8955)
"""

import os
import re
import tempfile
import unittest
import uuid
from unittest import mock

import yaml
from megalinter import config, utils
from megalinter.Linter import Linter
from megalinter.linters.GherkinLintLinter import GherkinLintLinter
from megalinter.linters.PhpstanLinter import PhpstanLinter
from megalinter.linters.StyLuaLinter import StyLuaLinter
from megalinter.linters.YamllintLinter import YamllintLinter
from megalinter.MegaLinter import Megalinter


class ExcludeForwardingConfigTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name
        self.request_ids = []

    def tearDown(self):
        for request_id in self.request_ids:
            config.delete(request_id)
        self.temp_dir.cleanup()

    def write_workspace_file(self, file_name, content):
        file_path = os.path.join(self.workspace, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(content)
        return file_path

    def build_linter(self, linter_class=Linter, **attributes):
        linter = linter_class.__new__(linter_class)
        linter.name = "TEST_LINTER"
        linter.linter_name = "test-linter"
        linter.request_id = str(uuid.uuid1())
        self.request_ids.append(linter.request_id)
        config.init_config(linter.request_id, None, {})
        linter.workspace = self.workspace
        linter.report_folder = os.path.join(self.workspace, "megalinter-reports")
        linter.sarif_output_file = None
        linter.log_lines_pre = []
        linter.final_config_file = None
        linter.cli_config_arg_name = "-c"
        linter.project_gitignored_directories = []
        linter.project_gitignored_name_directories = []
        linter.cli_lint_mode_project_exclude_arg_name = None
        linter.cli_lint_mode_project_exclude_arg_value = "{{DIR}}"
        linter.cli_lint_mode_project_exclude_separator = None
        linter.cli_lint_mode_project_exclude_seed_values = []
        linter.cli_lint_mode_project_exclude_config_key = None
        linter.cli_lint_mode_project_exclude_config_files = []
        linter.cli_lint_mode_project_exclude_conflicting_args = []
        linter.cli_lint_mode_project_exclude_ignore_file_arg_name = None
        linter.cli_lint_mode_project_exclude_ignore_file_seed_files = []
        linter.cli_lint_mode_project_exclude_ignore_file_merge_all_seeds = False
        linter.cli_lint_mode_project_exclude_ignore_file_pass_existing = []
        for key, value in attributes.items():
            setattr(linter, key, value)
        return linter

    def build_exclude_arguments(self, linter, cmd=None, excluded=("node_modules",)):
        with (
            mock.patch.object(
                Linter, "get_project_exclude_directories", return_value=list(excluded)
            ),
            mock.patch.object(
                Linter,
                "get_project_exclude_directory_paths",
                return_value=list(excluded),
            ),
        ):
            return linter.build_project_exclude_arguments(cmd)

    # Config file formats

    def test_load_config_file_content_formats(self):
        toml_file = self.write_workspace_file(
            "pyproject.toml", '[tool.black]\nextend-exclude = "/build/"\n'
        )
        json_file = self.write_workspace_file(
            ".groovylintrc.json",
            '{\n  // comment\n  "ignorepattern": "**/gen/**,**/tmp/**", // trailing\n}\n',
        )
        ini_file = self.write_workspace_file(
            ".flake8", "# flake8 config\n[flake8]\nextend-exclude = a,\n  b\n"
        )
        yaml_file = self.write_workspace_file(".phplint.yml", "exclude:\n  - vendor\n")
        invalid_file = self.write_workspace_file("broken.toml", "[tool\n")
        self.assertEqual(
            "/build/",
            utils.load_config_file_content(toml_file)["tool"]["black"][
                "extend-exclude"
            ],
        )
        self.assertEqual(
            "**/gen/**,**/tmp/**",
            utils.load_config_file_content(json_file)["ignorepattern"],
        )
        self.assertEqual(
            "a,\nb",
            utils.load_config_file_content(ini_file)["flake8"]["extend-exclude"],
        )
        self.assertEqual(
            ["vendor"], utils.load_config_file_content(yaml_file)["exclude"]
        )
        self.assertEqual({}, utils.load_config_file_content(invalid_file))

    def test_find_config_key_value_wildcard_section(self):
        content = {"MASTER": {"ignore": "CVS,legacy"}, "REPORTS": {}}
        self.assertEqual(
            "CVS,legacy", utils.find_config_key_value(content, ["*", "ignore"])
        )
        self.assertIsNone(utils.find_config_key_value(content, ["MAIN", "ignore"]))

    # Native CLI argument mechanism

    def test_phplint_keeps_config_exclusions(self):
        # Issue #8955: phplint --exclude replaces the exclude list of its
        # config file, so the user's examples/fixtures/ was linted again
        config_file = self.write_workspace_file(
            ".github/linters/.phplint.yml",
            "path: .\nexclude:\n  - vendor\n  - examples/fixtures/\n",
        )
        linter = self.build_linter(
            final_config_file=config_file,
            cli_lint_mode_project_exclude_arg_name="--exclude",
            cli_lint_mode_project_exclude_config_key="exclude",
        )
        self.assertEqual(
            [
                "--exclude",
                "vendor",
                "--exclude",
                "examples/fixtures/",
                "--exclude",
                "node_modules",
            ],
            self.build_exclude_arguments(linter),
        )

    def test_ini_comma_string_is_split_and_joined(self):
        config_file = self.write_workspace_file(
            ".flake8", "[flake8]\nextend_exclude = legacy,\n    generated\n"
        )
        linter = self.build_linter(
            final_config_file=config_file,
            cli_lint_mode_project_exclude_arg_name="--extend-exclude=",
            cli_lint_mode_project_exclude_separator=",",
            cli_lint_mode_project_exclude_config_key=[
                "flake8.extend-exclude",
                "flake8.extend_exclude",
            ],
        )
        self.assertEqual(
            ["--extend-exclude=legacy,generated,node_modules"],
            self.build_exclude_arguments(linter),
        )

    def test_pylint_ignore_found_in_any_section_with_default_seed(self):
        config_file = self.write_workspace_file(
            ".pylintrc", "[MASTER]\nignore=legacy\n"
        )
        linter = self.build_linter(
            final_config_file=config_file,
            cli_lint_mode_project_exclude_arg_name="--ignore=",
            cli_lint_mode_project_exclude_separator=",",
            cli_lint_mode_project_exclude_seed_values=["CVS"],
            cli_lint_mode_project_exclude_config_key=[
                "*.ignore",
                "tool.pylint.*.ignore",
            ],
        )
        self.assertEqual(
            ["--ignore=legacy,CVS,node_modules"], self.build_exclude_arguments(linter)
        )

    def test_regex_string_kept_whole(self):
        config_file = self.write_workspace_file(
            "pyproject.toml", '[tool.black]\nextend-exclude = "(a|b)/legacy"\n'
        )
        linter = self.build_linter(
            final_config_file=config_file,
            cli_lint_mode_project_exclude_arg_name="--extend-exclude",
            cli_lint_mode_project_exclude_arg_value="/{{DIR}}/",
            cli_lint_mode_project_exclude_separator="|",
            cli_lint_mode_project_exclude_config_key=["tool.black.extend-exclude"],
        )
        self.assertEqual(
            ["--extend-exclude", "(a|b)/legacy|/node_modules/"],
            self.build_exclude_arguments(linter),
        )

    def test_multiline_verbose_regex_is_grouped(self):
        config_file = self.write_workspace_file(
            "pyproject.toml",
            "[tool.black]\nextend-exclude = '''\n/(\n  legacy  # old code\n)/\n'''\n",
        )
        linter = self.build_linter(
            final_config_file=config_file,
            cli_lint_mode_project_exclude_arg_name="--extend-exclude",
            cli_lint_mode_project_exclude_arg_value="/{{DIR}}/",
            cli_lint_mode_project_exclude_separator="|",
            cli_lint_mode_project_exclude_config_key=["tool.black.extend-exclude"],
        )
        joined = self.build_exclude_arguments(linter)[1]
        self.assertTrue(joined.startswith("(?:/(\n  legacy  # old code\n)/\n)|"))
        self.assertTrue(joined.endswith("|/node_modules/"))

    def test_config_passed_in_user_arguments_is_read(self):
        config_file = self.write_workspace_file(
            "custom/phplint.yml", "exclude:\n  - legacy\n"
        )
        linter = self.build_linter(
            cli_config_arg_name="--configuration",
            cli_lint_mode_project_exclude_arg_name="--exclude",
            cli_lint_mode_project_exclude_config_key="exclude",
        )
        self.assertEqual(
            ["--exclude", "legacy", "--exclude", "node_modules"],
            self.build_exclude_arguments(
                linter, ["phplint", f"--configuration={config_file}"]
            ),
        )
        self.assertEqual(
            ["--exclude", "legacy", "--exclude", "node_modules"],
            self.build_exclude_arguments(
                linter, ["phplint", "--configuration", "custom/phplint.yml"]
            ),
        )

    def test_discovered_config_files_are_searched(self):
        self.write_workspace_file(
            "pyproject.toml", '[tool.djlint]\nextend_exclude = "legacy, build"\n'
        )
        linter = self.build_linter(
            cli_config_arg_name="",
            cli_lint_mode_project_exclude_arg_name="--extend-exclude",
            cli_lint_mode_project_exclude_separator=",",
            cli_lint_mode_project_exclude_config_key=[
                "tool.djlint.extend_exclude",
                "extend_exclude",
            ],
            cli_lint_mode_project_exclude_config_files=[
                "pyproject.toml",
                ".djlintrc",
            ],
        )
        self.assertEqual(
            ["--extend-exclude", "legacy,build,node_modules"],
            self.build_exclude_arguments(linter, ["djlint"]),
        )

    def test_user_single_occurrence_argument_is_merged(self):
        linter = self.build_linter(
            cli_lint_mode_project_exclude_arg_name="--ignore=",
            cli_lint_mode_project_exclude_arg_value="*/{{DIR}}/*",
            cli_lint_mode_project_exclude_separator=",",
        )
        cmd = ["phpcs", "--ignore=*/legacy/*", "--ignore-annotations"]
        exclude_args = self.build_exclude_arguments(linter, cmd)
        self.assertEqual(["phpcs", "--ignore-annotations"], cmd)
        self.assertEqual(["--ignore=*/legacy/*,*/node_modules/*"], exclude_args)

    def test_user_separated_argument_is_merged(self):
        linter = self.build_linter(
            cli_lint_mode_project_exclude_arg_name="--skip",
            cli_lint_mode_project_exclude_separator=",",
        )
        cmd = ["codespell", "--skip", "*.lock", "--skip-hidden"]
        exclude_args = self.build_exclude_arguments(linter, cmd)
        self.assertEqual(["codespell", "--skip-hidden"], cmd)
        self.assertEqual(["--skip", "*.lock,node_modules"], exclude_args)

    def test_user_argument_without_value_is_not_consumed(self):
        linter = self.build_linter(
            cli_lint_mode_project_exclude_arg_name="--skip",
            cli_lint_mode_project_exclude_separator=",",
        )
        cmd = ["codespell", "--skip", "--count"]
        exclude_args = self.build_exclude_arguments(linter, cmd)
        self.assertEqual(["codespell", "--skip", "--count"], cmd)
        self.assertEqual(["--skip", "node_modules"], exclude_args)

    def test_regex_with_global_flags_stays_first(self):
        config_file = self.write_workspace_file(
            "pyproject.toml",
            "[tool.black]\nextend-exclude = '''\n(?x)/(\n  legacy\n)/\n'''\n",
        )
        linter = self.build_linter(
            final_config_file=config_file,
            cli_lint_mode_project_exclude_arg_name="--extend-exclude",
            cli_lint_mode_project_exclude_arg_value="/{{DIR}}/",
            cli_lint_mode_project_exclude_separator="|",
            cli_lint_mode_project_exclude_config_key=["tool.black.extend-exclude"],
        )
        cmd = ["black", "--extend-exclude", "/tmp/"]
        joined = self.build_exclude_arguments(linter, cmd)[1]
        self.assertTrue(joined.startswith("(?x)/(\n  legacy\n)/\n|/tmp/|"))
        self.assertTrue(re.compile(joined).search("/node_modules/a.py"))

    def test_conflicting_argument_disables_forwarding(self):
        linter = self.build_linter(
            cli_lint_mode_project_exclude_conflicting_args=["--no-ignore"]
        )
        self.assertTrue(
            linter.has_project_exclude_conflicting_args(["v8r", "--no-ignore"])
        )
        self.assertFalse(linter.has_project_exclude_conflicting_args(["v8r"]))
        self.assertIn("--no-ignore", linter.log_lines_pre[0])

    # Generated ignore file mechanism

    def test_all_seed_files_are_merged(self):
        self.write_workspace_file(".gitignore", "bin/\n*.g.cs\n")
        self.write_workspace_file(".csharpierignore", "legacy/\n!keep.g.cs\n")
        linter = self.build_linter(
            cli_lint_mode_project_exclude_ignore_file_arg_name="--ignore-path",
            cli_lint_mode_project_exclude_ignore_file_seed_files=[
                ".gitignore",
                ".csharpierignore",
            ],
            cli_lint_mode_project_exclude_ignore_file_merge_all_seeds=True,
        )
        with mock.patch.object(
            Linter, "get_project_exclude_directories", return_value=["node_modules"]
        ):
            args = linter.build_project_exclude_ignore_file_arguments(["csharpier"])
        with open(os.path.join(self.workspace, args[1]), encoding="utf-8") as file:
            lines = file.read().splitlines()
        self.assertEqual(
            ["bin/", "*.g.cs", "legacy/", "!keep.g.cs", "node_modules"], lines
        )

    def test_config_ignore_files_replace_default_ones(self):
        self.write_workspace_file(".v8rrc.yml", "ignorePatternFiles:\n  - .myignore\n")
        self.write_workspace_file(".myignore", "fixtures/**\n")
        self.write_workspace_file(".gitignore", "build/\n")
        linter = self.build_linter(
            cli_config_arg_name="",
            cli_lint_mode_project_exclude_arg_value="{{DIR_PATH}}/**",
            cli_lint_mode_project_exclude_ignore_file_arg_name="--ignore-pattern-files=",
            cli_lint_mode_project_exclude_ignore_file_pass_existing=[
                ".v8rignore",
                ".gitignore",
            ],
            cli_lint_mode_project_exclude_config_key="ignorePatternFiles",
            cli_lint_mode_project_exclude_config_files=[".v8rrc.yml"],
        )
        with (
            mock.patch.object(
                Linter,
                "get_project_exclude_directory_paths",
                return_value=["node_modules"],
            ),
            mock.patch.object(
                Linter, "get_project_exclude_directories", return_value=["node_modules"]
            ),
        ):
            args = linter.build_project_exclude_ignore_file_arguments(["v8r"])
        self.assertEqual("--ignore-pattern-files=.myignore", args[0])
        self.assertEqual(2, len(args))

    # Custom linter classes

    def test_phpstan_excludes_from_analysis_only(self):
        config_file = self.write_workspace_file(
            "phpstan.neon.dist",
            "parameters:\n    scanDirectories:\n        - vendor-bin/\n",
        )
        linter = self.build_linter(PhpstanLinter, name="PHP_PHPSTAN")
        with mock.patch.object(
            PhpstanLinter, "get_project_exclude_directories", return_value=["vendor"]
        ):
            cmd = linter.manage_excluded_directories_config(
                ["phpstan", "analyse", "-c", config_file]
            )
        with open(cmd[3], encoding="utf-8") as file_handler:
            generated = file_handler.read().splitlines()
        self.assertEqual(
            [
                "includes:",
                f"    - {config_file.replace(chr(92), '/')}",
                "parameters:",
                "    excludePaths:",
                "        analyse:",
                "            - */vendor/*",
            ],
            generated,
        )

    def build_yamllint_generated_config(self, config_content):
        config_file = self.write_workspace_file(".yamllint.yml", config_content)
        linter = self.build_linter(YamllintLinter, name="YAML_YAMLLINT")
        with mock.patch.object(
            YamllintLinter, "get_project_exclude_directories", return_value=["vendor"]
        ):
            cmd = linter.manage_excluded_directories_config(
                ["yamllint", "-c", config_file]
            )
        with open(cmd[2], encoding="utf-8") as file_handler:
            return yaml.safe_load(file_handler)

    def test_yamllint_keeps_ignore_inherited_through_extends(self):
        self.write_workspace_file("base.yml", "ignore: |\n  fixtures/\n")
        generated = self.build_yamllint_generated_config("extends: base.yml\n")
        self.assertEqual(["fixtures/", "vendor/"], generated["ignore"])

    def test_yamllint_reads_relative_config_from_the_workspace(self):
        self.write_workspace_file(".yamllint.yml", "ignore:\n  - fixtures/\n")
        linter = self.build_linter(YamllintLinter, name="YAML_YAMLLINT")
        self.assertEqual(
            (["fixtures/"], []), linter.find_effective_ignore(".yamllint.yml")
        )
        self.write_workspace_file(".yamllint.yml", "ignore:\n")
        self.assertEqual(([], []), linter.find_effective_ignore(".yamllint.yml"))

    def test_yamllint_forwards_with_ignore_from_file(self):
        generated = self.build_yamllint_generated_config(
            "ignore-from-file: .gitignore\n"
        )
        self.assertNotIn("ignore", generated)
        self.assertEqual(".gitignore", generated["ignore-from-file"][0])
        with open(generated["ignore-from-file"][1], encoding="utf-8") as file_handler:
            self.assertEqual("vendor/", file_handler.read().strip())

    def test_gherkin_lint_keeps_default_ignore(self):
        linter = self.build_linter(GherkinLintLinter, name="GHERKIN_GHERKIN_LINT")
        with mock.patch.object(
            GherkinLintLinter, "get_project_exclude_directories", return_value=["dist"]
        ):
            cmd = linter.manage_excluded_directories_config(["gherkin-lint"])
        self.assertEqual(
            ["gherkin-lint", "--ignore", "node_modules/**,**/dist/**"], cmd
        )

    def test_stylua_restates_defaults_and_ignored_files(self):
        self.write_workspace_file(".styluaignore", "# generated\nsrc/gen.lua\n")
        # An allowlist can not be restated as overrides: it is left out
        self.write_workspace_file(".gitignore", "/*\n!/src/\n")
        linter = self.build_linter(StyLuaLinter, name="LUA_STYLUA")
        with mock.patch.object(
            StyLuaLinter, "get_project_exclude_directories", return_value=["vendor"]
        ):
            cmd = linter.manage_excluded_directories_config(["stylua", "--check"])
        self.assertEqual(
            [
                "stylua",
                "--check",
                "-g",
                "**/*.lua",
                "-g",
                "**/*.luau",
                "-g",
                "!src/gen.lua",
                "-g",
                "!**/vendor/**",
            ],
            cmd,
        )

    # Parallel processes

    def get_parallel_process_number(self, is_ci, cpu_count, config_values=None):
        megalinter = Megalinter.__new__(Megalinter)
        megalinter.request_id = str(uuid.uuid1())
        self.request_ids.append(megalinter.request_id)
        config.init_config(megalinter.request_id, None, config_values or {})
        with (
            mock.patch.object(utils, "is_ci", return_value=is_ci),
            mock.patch("megalinter.MegaLinter.mp.cpu_count", return_value=cpu_count),
        ):
            return megalinter.get_parallel_process_number()

    def test_parallel_process_number_keeps_a_core_free_outside_ci(self):
        self.assertEqual(11, self.get_parallel_process_number(False, 12))
        self.assertEqual(1, self.get_parallel_process_number(False, 1))

    def test_parallel_process_number_uses_all_cores_in_ci(self):
        self.assertEqual(12, self.get_parallel_process_number(True, 12))

    def test_parallel_process_number_variable_wins(self):
        self.assertEqual(
            4,
            self.get_parallel_process_number(
                False, 12, {"PARALLEL_PROCESS_NUMBER": "4"}
            ),
        )
