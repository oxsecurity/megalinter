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
                "SECURED_ENV_VARIABLES": "SECRET_VAR,OX_API_KEY",
                "workspace": ".",
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
            cli_env["SECRET_VAR"] == "HIDDEN_BY_MEGALINTER", "SECRET_VAR is not visible"
        )
        self.assertTrue(
            cli_env["OX_API_KEY"] == "HIDDEN_BY_MEGALINTER", "OX_API_KEY is not visible"
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
                "SECURED_ENV_VARIABLES_DEFAULT": "SECRET_VAR",
                "SECURED_ENV_VARIABLES": "OX_API_KEY",
                "workspace": ".",
                "LOG_LEVEL": "DEBUG",
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
