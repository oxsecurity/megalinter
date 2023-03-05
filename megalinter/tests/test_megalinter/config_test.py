#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""
import glob
import os
import re
import unittest

from git import Repo
from megalinter import config, utilstest
from megalinter.constants import ML_REPO
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
        os.environ["MEGALINTER_CONFIG"] = remote_config
        config.init_config()
        self.assertEqual("(custom)", config.get("FILTER_REGEX_INCLUDE"))
        self.restore_branch_in_input_files(changed_files)

    def test_remote_config_error(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = self.test_folder + "custom.mega-linter-not-existing.yml"
        try:
            os.environ["MEGALINTER_CONFIG"] = remote_config
            config.init_config()
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
        os.environ["MEGALINTER_CONFIG"] = local_config
        config.init_config(
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_extends"
        )
        self.assertEqual("(local)", config.get("FILTER_REGEX_INCLUDE"))
        self.assertEqual("false", config.get("SHOW_ELAPSED_TIME"))
        self.restore_branch_in_input_files(changed_files)

    def test_local_config_extends_recurse_success(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "recurse.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = local_config
        config.init_config(
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_extends_recurse"
        )
        self.assertEqual("(local)", config.get("FILTER_REGEX_INCLUDE"))
        self.assertEqual("false", config.get("SHOW_ELAPSED_TIME"))
        self.assertEqual("dev", config.get("DEFAULT_BRANCH"))
        self.assertEqual("DEBUG", config.get("LOG_LEVEL"))
        self.restore_branch_in_input_files(changed_files)

    def test_local_config_extends_error(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "local-error.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = local_config
        try:
            config.init_config(
                REPO_HOME_DEFAULT
                + os.path.sep
                + ".automation"
                + os.path.sep
                + "test"
                + os.path.sep
                + "mega-linter-config-test"
            )
        except Exception as e:
            self.assertIn("No such file or directory", str(e))
        finally:
            self.restore_branch_in_input_files(changed_files)

    def test_remote_config_extends_success(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = self.test_folder + "remote_extends/base.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = remote_config
        config.init_config()
        self.assertEqual("(base)", config.get("FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get("FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get("SHOW_ELAPSED_TIME"))
        self.restore_branch_in_input_files(changed_files)

    def test_remote_config_extends_success_2(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = self.test_folder + "remote_extends_2/base2.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = remote_config
        config.init_config()
        self.assertEqual("(base)", config.get("FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get("FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get("SHOW_ELAPSED_TIME"))
        self.restore_branch_in_input_files(changed_files)

    def test_remote_config_extends_error(self):
        changed_files = self.replace_branch_in_input_files()
        remote_config = (
            self.test_folder + "remote_extends_error/base-error.mega-linter.yml"
        )
        os.environ["MEGALINTER_CONFIG"] = remote_config
        try:
            os.environ["MEGALINTER_CONFIG"] = remote_config
            config.init_config()
        except Exception as e:
            self.assertIn("Unable to retrieve EXTENDS config file", str(e)),
        finally:
            self.restore_branch_in_input_files(changed_files)

    def test_local_remote_config_extends_recurse_success(self):
        changed_files = self.replace_branch_in_input_files()
        local_config = "local.remote.mega-linter.yml"
        os.environ["MEGALINTER_CONFIG"] = local_config
        config.init_config(
            REPO_HOME_DEFAULT
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + "mega-linter-config-test"
            + os.path.sep
            + "local_remote_extends_recurse"
        )
        self.assertEqual("(base)", config.get("FILTER_REGEX_INCLUDE"))
        self.assertEqual("(extension2)", config.get("FILTER_REGEX_EXCLUDE"))
        self.assertEqual("true", config.get("SHOW_ELAPSED_TIME"))
        self.assertEqual("dev", config.get("DEFAULT_BRANCH"))
        self.assertEqual("DEBUG", config.get("LOG_LEVEL"))
        self.restore_branch_in_input_files(changed_files)

    def test_list_of_obj_as_env_var(self):
        os.environ[
            "PRE_COMMANDS"
        ] = '[{"cwd": "workspace", "command:": "echo \\"hello world\\""}]'
        config.init_config()
        pre_commands = config.get_list("PRE_COMMANDS", [])
        del os.environ["PRE_COMMANDS"]
        self.assertTrue(len(pre_commands) > 0, "PRE_COMMANDS not loaded from ENV var")

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
