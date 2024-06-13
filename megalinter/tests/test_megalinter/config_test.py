#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import contextlib
import glob
import io
import os
import re
import unittest
import uuid
from unittest.mock import patch

from git import Repo
from megalinter import config, utilstest
from megalinter.constants import ML_REPO
from megalinter.MegaLinter import Megalinter
from megalinter.utils import REPO_HOME_DEFAULT


class config_test(unittest.TestCase):
    repository = None
    branch = None
    test_folder = None

    def __init__(self, *args, **kwargs):
        super(config_test, self).__init__(*args, **kwargs)

        self.repository = self.get_repository()
        self.branch = self.get_branch()

        self.test_folder = (
            f"https://raw.githubusercontent.com/{self.repository}/"
            f"{self.branch}/.automation/test/mega-linter-config-test/"
        )

    def setUp(self):
        for key in [
            "MEGALINTER_CONFIG",
            "EXTENDS",
            "FILTER_REGEX_INCLUDE",
            "FILTER_REGEX_EXCLUDE",
            "SHOW_ELAPSED_TIME",
            "PRE_COMMANDS",
        ]:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        config.delete()

    def test_remote_config_success(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = self.test_folder + "remote/custom.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(request_id, None, {"MEGALINTER_CONFIG": remote_config})
        self.assertEqual("(custom)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.restore_branch_in_input_files(changed_files)

    def test_remote_config_error(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = self.test_folder + "custom.mega-linter-not-existing.yml"
        request_id = str(uuid.uuid1())
        try:
            config.init_config(request_id, None, {"MEGALINTER_CONFIG": remote_config})
        except Exception as e:
            self.assertRegex(
                str(e),
                (
                    "Unable to retrieve config file "
                    r"https://.*/\.automation/test/mega-linter-config-test/"
                    r"custom\.mega-linter-not-existing\.yml"
                ),
            )
        finally:
            self.restore_branch_in_input_files(changed_files)

    def test_local_config_extends_success(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "local.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_extends",
            {"MEGALINTER_CONFIG": local_config},
        )
        self.assertEqual("(local)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.assertEqual("false", config.get(request_id, "SHOW_ELAPSED_TIME"))
        self.restore_branch_in_input_files(changed_files)

    def test_local_config_extends_list_merge_replace_success(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "local.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_extends_list_merge_replace",
            {"MEGALINTER_CONFIG": local_config},
        )
        self.assertEqual(
            ["LINTER_2"],
            config.get(request_id, "ENABLE_LINTERS"),
        )
        self.assertEqual("(local)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.restore_branch_in_input_files(changed_files)

    def test_local_config_extends_list_merge_append_success(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "local.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_extends_list_merge_append",
            {"MEGALINTER_CONFIG": local_config},
        )
        self.assertEqual(
            ["LINTER_1", "LINTER_3", "LINTER_2"],
            config.get(request_id, "ENABLE_LINTERS"),
        )
        self.assertEqual("(local)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.restore_branch_in_input_files(changed_files)

    def test_local_config_extends_recurse_success(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "recurse.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_extends_recurse",
            {"MEGALINTER_CONFIG": local_config},
        )
        self.assertEqual("(local)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.assertEqual("false", config.get(request_id, "SHOW_ELAPSED_TIME"))
        self.assertEqual("dev", config.get(request_id, "DEFAULT_BRANCH"))
        self.assertEqual("DEBUG", config.get(request_id, "LOG_LEVEL"))
        self.restore_branch_in_input_files(changed_files)

    def test_local_config_extends_error(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "local-error.mega-linter.yml"
        request_id = str(uuid.uuid1())
        try:
            config.init_config(
                request_id,
                REPO_HOME_DEFAULT
                + os.path.sep
                + ".automation"
                + os.path.sep
                + "test"
                + os.path.sep
                + "mega-linter-config-test",
                {"MEGALINTER_CONFIG": local_config},
            )
        except Exception as e:
            self.assertIn("No such file or directory", str(e))
        finally:
            self.restore_branch_in_input_files(changed_files)

    def test_remote_config_extends_success(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = self.test_folder + "remote_extends/base.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(request_id, None, {"MEGALINTER_CONFIG": remote_config})
        self.assertEqual("(base)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get(request_id, "FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get(request_id, "SHOW_ELAPSED_TIME"))
        self.restore_branch_in_input_files(changed_files)

    def test_remote_config_extends_success_2(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = self.test_folder + "remote_extends_2/base2.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(request_id, None, {"MEGALINTER_CONFIG": remote_config})
        self.assertEqual("(base)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get(request_id, "FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get(request_id, "SHOW_ELAPSED_TIME"))
        self.restore_branch_in_input_files(changed_files)

    def test_remote_config_extends_error(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = (
            self.test_folder + "remote_extends_error/base-error.mega-linter.yml"
        )
        request_id = str(uuid.uuid1())
        try:
            config.init_config(request_id, None, {"MEGALINTER_CONFIG": remote_config})
        except Exception as e:
            self.assertRegex(
                str(e),
                (
                    "Unable to retrieve EXTENDS config file "
                    r"https://.*/\.automation/test/mega-linter-config-test/"
                    r"extension3\.mega-linter\.yml"
                ),
            )
        finally:
            self.restore_branch_in_input_files(changed_files)

    def test_local_remote_config_extends_recurse_success(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "local.remote.mega-linter.yml"
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_remote_extends_recurse",
            {"MEGALINTER_CONFIG": local_config},
        )
        self.assertEqual("(base)", config.get(request_id, "FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get(request_id, "FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get(request_id, "SHOW_ELAPSED_TIME"))
        self.assertEqual("dev", config.get(request_id, "DEFAULT_BRANCH"))
        self.assertEqual("DEBUG", config.get(request_id, "LOG_LEVEL"))
        self.restore_branch_in_input_files(changed_files)

    def test_list_of_obj_as_env_var(self):
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            None,
            {
                "PRE_COMMANDS": '[{"cwd": "workspace", "command:": "echo \\"hello world\\""}]'
            },
        )
        pre_commands = config.get_list(request_id, "PRE_COMMANDS", [])
        self.assertTrue(len(pre_commands) > 0, "PRE_COMMANDS not loaded from ENV var")

    def test_config_secure_env_vars_default(self):
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            None,
            {
                "VISIBLE_VAR": "VALUE",
                "GITHUB_TOKEN": "GITHUB_TOKEN_VALUE",
                "GITLAB_ACCESS_TOKEN_MEGALINTER": "GITLAB_ACCESS_TOKEN_MEGALINTER_VALUE",
                "LOG_LEVEL": "DEBUG",
            },
        )
        cli_env = config.build_env(request_id)
        self.assertTrue(cli_env["VISIBLE_VAR"] == "VALUE", "VISIBLE_VAR is visible")
        self.assertTrue(
            cli_env["GITHUB_TOKEN"] == "HIDDEN_BY_MEGALINTER",
            "GITHUB_TOKEN is not visible",
        )
        self.assertTrue(
            cli_env["GITLAB_ACCESS_TOKEN_MEGALINTER"] == "HIDDEN_BY_MEGALINTER",
            "GITLAB_ACCESS_TOKEN_MEGALINTER is not visible",
        )
        usage_stdout = io.StringIO()
        with contextlib.redirect_stdout(usage_stdout):
            Megalinter(
                {
                    "cli": True,
                    "request_id": request_id,
                    "workspace": ".",
                    "LOG_LEVEL": "DEBUG",
                }
            )
        output = usage_stdout.getvalue().strip()
        self.assertTrue("VISIBLE_VAR=VALUE" in output, "VISIBLE_VAR is visible")
        self.assertTrue(
            "GITHUB_TOKEN=HIDDEN_BY_MEGALINTER" in output, "GITHUB_TOKEN is not visible"
        )
        self.assertTrue(
            "GITLAB_ACCESS_TOKEN_MEGALINTER=HIDDEN_BY_MEGALINTER" in output,
            "GITLAB_ACCESS_TOKEN_MEGALINTER is not visible",
        )

    def test_config_secure_env_vars_custom(self):
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            None,
            {
                "VISIBLE_VAR": "VALUE",
                "GITHUB_TOKEN": "GITHUB_TOKEN_VALUE",
                "GITLAB_ACCESS_TOKEN_MEGALINTER": "GITLAB_ACCESS_TOKEN_MEGALINTER_VALUE",
                "SECRET_VAR": "SECRET_VALUE",
                "OX_API_KEY": "1234",
                "SECURED_ENV_VARIABLES": "SECRET_VAR,OX_API_KEY,(VAR_.*_REGEX),UNSECURED_VAR",
                "workspace": ".",
                "LOG_LEVEL": "DEBUG",
                "VAR_WITH_REGEX": "aXw32",
                "UNSECURED_VAR": "visible",
            },
        )
        cli_env = config.build_env(request_id, True, ["UNSECURED_VAR"])
        self.assertTrue(cli_env["VISIBLE_VAR"] == "VALUE", "VISIBLE_VAR is visible")
        self.assertTrue(
            cli_env["GITHUB_TOKEN"] == "HIDDEN_BY_MEGALINTER",
            "GITHUB_TOKEN is not visible",
        )
        self.assertTrue(
            cli_env["SECRET_VAR"] == "HIDDEN_BY_MEGALINTER", "SECRET_VAR is not visible"
        )
        self.assertTrue(
            cli_env["OX_API_KEY"] == "HIDDEN_BY_MEGALINTER", "OX_API_KEY is not visible"
        )
        self.assertTrue(
            cli_env["VAR_WITH_REGEX"] == "HIDDEN_BY_MEGALINTER",
            "VAR_WITH_REGEX is not visible",
        )
        self.assertTrue(
            cli_env["GITLAB_ACCESS_TOKEN_MEGALINTER"] == "HIDDEN_BY_MEGALINTER",
            "GITLAB_ACCESS_TOKEN_MEGALINTER is not visible",
        )
        self.assertTrue(
            cli_env["UNSECURED_VAR"] == "visible", "UNSECURED_VAR is visible"
        )
        usage_stdout = io.StringIO()
        with contextlib.redirect_stdout(usage_stdout):
            Megalinter(
                {
                    "cli": True,
                    "request_id": request_id,
                    "workspace": ".",
                    "LOG_LEVEL": "DEBUG",
                }
            )
        output = usage_stdout.getvalue().strip()
        self.assertTrue("VISIBLE_VAR=VALUE" in output, "VISIBLE_VAR is visible")
        self.assertTrue(
            "GITHUB_TOKEN=HIDDEN_BY_MEGALINTER" in output, "GITHUB_TOKEN is not visible"
        )
        self.assertTrue(
            "SECRET_VAR=HIDDEN_BY_MEGALINTER" in output,
            "SECRET_VAR is not visible",
        )
        self.assertTrue(
            "OX_API_KEY=HIDDEN_BY_MEGALINTER" in output,
            "OX_API_KEY is not visible",
        )

    def test_config_secure_env_vars_override_default(self):
        request_id = str(uuid.uuid1())
        config.init_config(
            request_id,
            None,
            {
                "VISIBLE_VAR": "VALUE",
                "GITHUB_TOKEN": "GITHUB_TOKEN_VALUE",
                "SECRET_VAR": "SECRET_VALUE",
                "OX_API_KEY": "1234",
                "SECURED_ENV_VARIABLES_DEFAULT": "SECRET_VAR,(VAR_.*_REGEX)",
                "SECURED_ENV_VARIABLES": "OX_API_KEY",
                "workspace": ".",
                "LOG_LEVEL": "DEBUG",
                "VAR_WITH_REGEX": "aXw32",
            },
        )
        cli_env = config.build_env(request_id)
        self.assertTrue(cli_env["VISIBLE_VAR"] == "VALUE", "VISIBLE_VAR is visible")
        self.assertTrue(
            cli_env["GITHUB_TOKEN"] == "GITHUB_TOKEN_VALUE", "GITHUB_TOKEN is visible"
        )
        self.assertTrue(
            cli_env["SECRET_VAR"] == "HIDDEN_BY_MEGALINTER", "SECRET_VAR is not visible"
        )
        self.assertTrue(
            cli_env["VAR_WITH_REGEX"] == "HIDDEN_BY_MEGALINTER",
            "VAR_WITH_REGEX is not visible",
        )
        self.assertTrue(
            cli_env["OX_API_KEY"] == "HIDDEN_BY_MEGALINTER", "OX_API_KEY is not visible"
        )
        usage_stdout = io.StringIO()
        with contextlib.redirect_stdout(usage_stdout):
            Megalinter(
                {
                    "cli": True,
                    "request_id": request_id,
                    "workspace": ".",
                    "LOG_LEVEL": "DEBUG",
                }
            )
        output = usage_stdout.getvalue().strip()
        self.assertTrue("VISIBLE_VAR=VALUE" in output, "VISIBLE_VAR is visible")
        self.assertTrue(
            "GITHUB_TOKEN=GITHUB_TOKEN_VALUE" in output, "GITHUB_TOKEN is visible"
        )
        self.assertTrue(
            "SECRET_VAR=HIDDEN_BY_MEGALINTER" in output,
            "SECRET_VAR is not visible",
        )
        self.assertTrue(
            "OX_API_KEY=HIDDEN_BY_MEGALINTER" in output,
            "OX_API_KEY is not visible",
        )

    def replace_branch_in_input_files(self):
        root = (
            ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
        )

        search_glob_pattern = root.replace("\\", "/") + "/**/*"

        regex = r"(/oxsecurity/megalinter/main)(/\.automation)"

        list = []

        for file in glob.iglob(search_glob_pattern, recursive=True):
            file_name = os.path.basename(file)

            if ".yml" not in file_name:
                continue

            match = False

            with open(file, "r", encoding="utf-8") as f:
                file_content = f.read()

                if re.search(regex, file_content):
                    file_content = re.sub(
                        regex, rf"/{self.repository}/{self.branch}\2", file_content
                    )

                    match = True

            if match:
                with open(file, "w") as f:
                    f.write(file_content)

                list.append(file)

        return list

    def restore_branch_in_input_files(self, files):
        repo = Repo(os.path.realpath(utilstest.REPO_HOME))

        for file in files:
            repo.index.checkout(
                [os.path.join(os.path.realpath(utilstest.REPO_HOME), file)], force=True
            )

    def get_repository(self):
        return os.environ.get("GITHUB_REPOSITORY", ML_REPO)

    def get_branch(self):
        return os.environ.get("GITHUB_BRANCH", "main")

    def test_get_list_args(self):
        # This is a test to check the functionality of the get_list_args method.
        # It mocks the behavior of the get method within this method and asserts the expected output.
        scenarios = [
            ("01", "none_value", None, None),
            ("02", "single_boolean_true", True, ["True"]),
            ("03", "single_boolean_false", False, ["False"]),
            ("04", "integer_value", 42, ["42"]),
            ("05", "float_value", 3.14, ["3.14"]),
            ("06", "empty_list", [], []),
            ("07", "empty_string", "", []),
            ("08", "single_space", " ", []),
            ("09", "double_space", "  ", []),
            ("10", "empty_quoted_string", '""', ['""']),
            ("11", "non_empty_list", ["item1", "item2"], ["item1", "item2"]),
            (
                "12",
                "single_quoted_string",
                "'single_quoted_string'",
                ["'single_quoted_string'"],
            ),
            ("13", "space_separated_items", "item1 item2", ["item1", "item2"]),
            (
                "14",
                "multiple_single_quoted_strings",
                "'string1' 'string2' 'string3'",
                ["string1", "string2", "string3"],
            ),
            (
                "15",
                "mixed_single_and_double_quotes",
                "\"double quoted\" 'single quoted'",
                ["double quoted", "single quoted"],
            ),
            (
                "16",
                "three_space_separated_items",
                "item1 item2 item3",
                ["item1", "item2", "item3"],
            ),
            (
                "17",
                "four_space_separated_items",
                "item1 item2 item3 item4",
                ["item1", "item2", "item3", "item4"],
            ),
            (
                "18",
                "five_space_separated_items",
                "item1 item2 item3 item4 item5",
                ["item1", "item2", "item3", "item4", "item5"],
            ),
            (
                "19",
                "single_quoted_with_spaces",
                "' single quoted with spaces '",
                [" single quoted with spaces "],
            ),
            (
                "20",
                " quoted_with_leading_space",
                '" leading space"',
                [" leading space"],
            ),
            (
                "21",
                "quoted_with_trailing_space",
                '"trailing space "',
                ["trailing space "],
            ),
            (
                "22",
                "quoted_with_leading_and_trailing_spaces",
                '" leading and trailing spaces "',
                [" leading and trailing spaces "],
            ),
            (
                "23",
                "multiple_quoted_strings_with_spaces",
                '" string1 " "string2 " " string3 "',
                [" string1 ", "string2 ", " string3 "],
            ),
            (
                "24",
                "paths_with_nested_folders",
                "./nested/folder/file.txt",
                ["./nested/folder/file.txt"],
            ),
            (
                "25",
                "paths_with_parent_directory",
                "../parent/file.txt",
                ["../parent/file.txt"],
            ),
            (
                "26",
                "paths_with_tilde_home",
                "~/home/user/file.txt",
                ["~/home/user/file.txt"],
            ),
            (
                "27",
                "paths_with_url_files",
                "http://example.com/file.txt",
                ["http://example.com/file.txt"],
            ),
            ("28", "multiple_spaces_between_paths", "path1  path2", ["path1", "path2"]),
            (
                "29",
                "relative_paths",
                "./relative/path ./another/relative/path",
                ["./relative/path", "./another/relative/path"],
            ),
            (
                "30",
                "paths_with_file_extensions",
                "./file.txt ./folder/file.py",
                ["./file.txt", "./folder/file.py"],
            ),
            (
                "31",
                "paths_with_hidden_files",
                "./folder/.file.sln ./folder/.hidden",
                ["./folder/.file.sln", "./folder/.hidden"],
            ),
            (
                "32",
                "absolute_unix_paths",
                "/root/path /another/root/path",
                ["/root/path", "/another/root/path"],
            ),
            (
                "33",
                "quoted_paths_with_spaces",
                '"quoted path/with spaces" "another/quoted path"',
                ["quoted path/with spaces", "another/quoted path"],
            ),
            (
                "34",
                "paths_with_url_and_local_files",
                "http://example.com/file.txt ./local/file.txt",
                ["http://example.com/file.txt", "./local/file.txt"],
            ),
            (
                "35",
                "mixed_quotes_and_spaces",
                "\"quoted item1\" item2 'quoted item3' item4",
                ["quoted item1", "item2", "quoted item3", "item4"],
            ),
            (
                "36",
                "command_with_options",
                'command --option="value with spaces" --flag',
                ["command", "--option=value with spaces", "--flag"],
            ),
            (
                "37",
                "list_with_spaces_in_elements",
                ["item 1", "item 2"],
                ["item 1", "item 2"],
            ),
            ("38", "list_with_single_element", ["single_item"], ["single_item"]),
            (
                "39",
                "list_with_single_element_with_spaces",
                ["single item"],
                ["single item"],
            ),
            (
                "40",
                "list_with_spaces_and_quotes",
                ['"item 1"', "'item 2'"],
                ['"item 1"', "'item 2'"],
            ),
            (
                "41",
                "list_with_single_quoted_element_with_spaces",
                ['"single item"'],
                ['"single item"'],
            ),
            (
                "42",
                "list_with_single_element_and_spaces",
                [" single item "],
                [" single item "],
            ),
            (
                "43",
                "list_with_single_quoted_element_and_spaces",
                [' "single item" '],
                [' "single item" '],
            ),
            (
                "44",
                "list_with_comma_separated_items",
                "item1,item2,item3",
                ["item1,item2,item3"],
            ),
            (
                "45",
                "list_with_comma_and_space_separated_items",
                "item1, item2, item3",
                ["item1,", "item2,", "item3"],
            ),
            (
                "46",
                "list_with_semicolon_separated_items",
                "item1;item2;item3",
                ["item1;item2;item3"],
            ),
            (
                "47",
                "list_with_semicolon_and_space_separated_items",
                "item1; item2; item3",
                ["item1;", "item2;", "item3"],
            ),
            (
                "48",
                "list_with_multiple_elements",
                ["item1", "item2", "item3", "item4"],
                ["item1", "item2", "item3", "item4"],
            ),
            (
                "49",
                "list_with_multiple_elements_with_spaces",
                ["item 1", "item 2", "item 3", "item 4"],
                ["item 1", "item 2", "item 3", "item 4"],
            ),
            (
                "50",
                "list_with_multiple_quoted_elements_with_spaces",
                ['"item 1"', '"item 2"', '"item 3"', '"item 4"'],
                ['"item 1"', '"item 2"', '"item 3"', '"item 4"'],
            ),
            (
                "51",
                "list_with_multiple_elements_and_spaces",
                [" item1 ", " item2 ", " item3 ", " item4 "],
                [" item1 ", " item2 ", " item3 ", " item4 "],
            ),
            (
                "52",
                "list_with_multiple_quoted_elements_and_spaces",
                [' "item1" ', ' "item2" ', ' "item3" ', ' "item4" '],
                [' "item1" ', ' "item2" ', ' "item3" ', ' "item4" '],
            ),
            (
                "53",
                "list_with_comma_separated_multiple_items",
                "item1,item2;item3,item4",
                ["item1,item2;item3,item4"],
            ),
            (
                "54",
                "list_with_comma_and_space_separated_multiple_items",
                "item1, item2, item3, item4",
                ["item1,", "item2,", "item3,", "item4"],
            ),
            (
                "55",
                "list_with_semicolon_separated_multiple_items",
                "item1;item2,item3;item4",
                ["item1;item2,item3;item4"],
            ),
            (
                "56",
                "list_with_semicolon_and_space_separated_multiple_items",
                "item1; item2; item3; item4",
                ["item1;", "item2;", "item3;", "item4"],
            ),
            (
                "57",
                "single_windows_path",
                "C:\\path\\to\\file.txt",
                ["C:\\path\\to\\file.txt"],
            ),
            (
                "58",
                "windows_path_with_spaces",
                '"C:\\path to\\file.txt"',
                ["C:\\path to\\file.txt"],
            ),
            (
                "59",
                "list_of_two_windows_paths",
                ["C:\\path\\to\\file1.txt", "C:\\path\\to\\file2.txt"],
                ["C:\\path\\to\\file1.txt", "C:\\path\\to\\file2.txt"],
            ),
            (
                "60",
                "list_of_two_windows_paths_with_spaces",
                ['"C:\\path to\\file1.txt"', '"C:\\path to\\file2.txt"'],
                ['"C:\\path to\\file1.txt"', '"C:\\path to\\file2.txt"'],
            ),
            ("61", "network_share", "\\\\server\\share", ["\\\\server\\share"]),
            (
                "62",
                "network_share_with_spaces",
                "'\\\\server\\share\\path with spaces\\file.txt'",
                ["\\\\server\\share\\path with spaces\\file.txt"],
            ),
            ("63", "relative_path", ".\\path\\to\\file.txt", [".\\path\\to\\file.txt"]),
            (
                "64",
                "relative_path_with_spaces",
                '".\\path to\\file.txt"',
                [".\\path to\\file.txt"],
            ),
            (
                "65",
                "list_of_two_network_shares",
                ["\\\\server1\\share\\file1.txt", "\\\\server2\\share\\file2.txt"],
                ["\\\\server1\\share\\file1.txt", "\\\\server2\\share\\file2.txt"],
            ),
            (
                "66",
                "list_of_two_relative_paths",
                [".\\path1\\file1.txt", ".\\path2\\file2.txt"],
                [".\\path1\\file1.txt", ".\\path2\\file2.txt"],
            ),
            # Commented out cases due to shlex.split removing the /
            # ("67", "absolute_windows_paths", "C:\\absolute\\path C:\\another\\absolute\\path",
            #   ['C:\\absolute\\path', 'C:\\another\\absolute\\path']),
            # ("68", "paths_with_environment_variables", "$HOME/file.txt $USERPROFILE\\file1.txt",
            #   ['$HOME/file.txt', '$USERPROFILE\\file1.txt']),
            # ("69", "path_with_mixed_separators", "path/to/file path\\to\\another\\file",
            #   ['path/to/file', 'path\\to\\another\\file']),
            # ("70", "complex_paths_and_files", 'file1 "complex path/file2" file3\\with\\backslashes',
            #   ['file1', 'complex path/file2', 'file3\\with\\backslashes'])
        ]

        for scenario_number, scenario_name, return_value, expected_result in scenarios:
            with self.subTest(
                scenario_number=scenario_number, scenario_name=scenario_name
            ):
                with patch.object(config, "get", return_value=return_value):
                    result = config.get_list_args("dummy_request_id", scenario_name)
                    self.assertEqual(
                        result,
                        expected_result,
                        f"Failed on result scenario {scenario_number}: {scenario_name}",
                    )
