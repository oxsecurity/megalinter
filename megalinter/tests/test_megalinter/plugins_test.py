#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""

import os
import unittest
import uuid

from git import Repo
from megalinter import utilstest
from megalinter.constants import ML_REPO


def get_git_repo_info() -> tuple[str, str]:
    """
    Get the current git repository owner/name and branch name.
    Returns (repo_slug, branch) tuple.
    Falls back to (ML_REPO, "main") if git info cannot be determined.
    This allows tests to work correctly on forks and feature branches.
    """
    try:
        # Get the repository from the current file location
        repo = Repo(__file__, search_parent_directories=True)

        # Get current branch name
        branch = repo.active_branch.name

        # Get repository owner/name from remote URL
        # Try origin remote first, fallback to any remote
        remote_url = None
        if "origin" in repo.remotes:
            remote_url = repo.remotes.origin.url
        else:
            # Fallback to first available remote
            for remote in repo.remotes:
                remote_url = remote.url
                break

        if remote_url:
            # Parse GitHub URL to get owner/repo
            # Handles: git@github.com:owner/repo.git
            #         https://github.com/owner/repo.git
            if "github.com/" in remote_url:
                repo_slug = remote_url.split("github.com/")[-1]
                repo_slug = repo_slug.replace(".git", "")
                return repo_slug, branch

    except Exception:
        # If git detection fails, fall back to defaults
        pass

    return ML_REPO, "main"


class plugins_test(unittest.TestCase):
    def __init__(self, args) -> None:
        self.request_id = str(uuid.uuid1())
        super().__init__(args)

    def setUp(self):
        utilstest.linter_test_setup(
            {
                "request_id": self.request_id,
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}mega-linter-plugin-test",
            }
        )

    def test_load_plugin_success(self):
        # Get the current git repository and branch dynamically
        # This allows tests to work correctly on forks and feature branches
        repo_slug, local_branch = get_git_repo_info()
        mega_linter, output = utilstest.call_mega_linter(
            {
                "PLUGINS": f"https://raw.githubusercontent.com/{repo_slug}/"
                + local_branch
                + "/.automation/test/mega-linter-plugin-test/test.megalinter-descriptor.yml",
                "LOG_LEVEL": "DEBUG",
                "MULTI_STATUS": "false",
                "GITHUB_COMMENT_REPORTER": "false",
                "DISABLE": "REPOSITORY,SPELL",
                "request_id": self.request_id,
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("Linted [TEST] files", output)
        self.assertIn("[Plugins] Loaded plugin descriptor", output)
        self.assertIn("[Plugins] Successful initialization of TEST", output)

    def test_load_local_plugin_success(self):
        mega_linter, output = utilstest.call_mega_linter(
            {
                "PLUGINS": "file://.automation/test/mega-linter-plugin-test/test.megalinter-descriptor.yml",
                "LOG_LEVEL": "DEBUG",
                "MULTI_STATUS": "false",
                "GITHUB_COMMENT_REPORTER": "false",
                "DISABLE": "REPOSITORY,SPELL",
                "request_id": self.request_id,
            }
        )
        self.assertTrue(
            len(mega_linter.linters) > 0, "Linters have been created and run"
        )
        self.assertIn("Linted [TEST] files", output)
        self.assertIn("[Plugins] Loaded plugin descriptor", output)
        self.assertIn("[Plugins] Successful initialization of TEST", output)

    def test_load_local_plugin_fail(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": "file://.automation/test/mega-linter-plugin-test/test-fake.megalinter-descriptor.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                    "DISABLE": "REPOSITORY,SPELL",
                    "request_id": self.request_id,
                }
            )
        except Exception as e:
            self.assertIn(
                "[Plugins] Local plugin descriptor not found or not readable", str(e)
            )

    def test_load_local_plugin_read_fail(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": "file://.automation/test/mega-linter-plugin-test/test-empty.megalinter-descriptor.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                    "DISABLE": "REPOSITORY,SPELL",
                    "request_id": self.request_id,
                }
            )
        except Exception as e:
            self.assertIn("[Plugins] Plugin descriptor is empty:", str(e))

    def test_load_plugin_http_error(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": f"https://raw.githubus3ent.com/{ML_REPO}/"
                    "plugins/.automation/test/mega-linter-plugin-test/test.not.here.megalinter-descriptor.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                    "DISABLE": "REPOSITORY,SPELL",
                    "request_id": self.request_id,
                }
            )
        except Exception as e:
            self.assertIn("[Plugins] Unable to load remote plugin", str(e))

    def test_load_plugin_host_url_error_1(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": f"https://raw.githubusercontent.com/{ML_REPO}/"
                    "plugins/.automation/test/some_folder_name/test.megalinter-descriptor.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                    "DISABLE": "REPOSITORY,SPELL",
                    "request_id": self.request_id,
                }
            )
        except Exception as e:
            self.assertIn(
                "[Plugins] Plugin descriptor file must be hosted in"
                " a directory containing /mega-linter-plugin-",
                str(e),
            )

    def test_load_plugin_file_name_error(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": f"https://raw.githubusercontent.com/{ML_REPO}/"
                    "plugins/.automation/test/mega-linter-plugin-test/test.megalinter-wrong.yml",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                    "DISABLE": "REPOSITORY,SPELL",
                    "request_id": self.request_id,
                }
            )
        except Exception as e:
            self.assertIn(
                "[Plugins] Plugin descriptor file must end with .megalinter-descriptor.yml",
                str(e),
            )

    def test_load_plugin_format_error_2(self):
        try:
            utilstest.call_mega_linter(
                {
                    "PLUGINS": "hello",
                    "LOG_LEVEL": "DEBUG",
                    "MULTI_STATUS": "false",
                    "GITHUB_COMMENT_REPORTER": "false",
                    "DISABLE": "REPOSITORY,SPELL",
                    "request_id": self.request_id,
                }
            )
        except Exception as e:
            self.assertIn("[Plugins] Plugin descriptors must follow the format", str(e))
