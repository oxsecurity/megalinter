#!/usr/bin/env python3
"""
Unit tests for Megalinter class

"""

import os
import unittest
import uuid
from urllib.parse import quote

from git import Repo
from megalinter import utilstest
from megalinter.constants import ML_REPO


def _get_branch_from_ci_env() -> str | None:
    """
    Get branch name from GitHub Actions environment variables.
    Returns None if no GitHub CI environment variable is set.
    Note: GITHUB_REF contains full ref path (refs/heads/main), not just branch name.
    """
    return (
        os.environ.get("GITHUB_HEAD_REF")
        or os.environ.get("GITHUB_REF_NAME")
    )


def _parse_github_remote_url(remote_url: str) -> str | None:
    """
    Parse GitHub remote URL to extract owner/repo slug.
    Handles both SSH and HTTPS formats.
    Returns None if not a GitHub URL.

    Examples:
        git@github.com:owner/repo.git -> owner/repo
        https://github.com/owner/repo.git -> owner/repo
        git@gitlab.com:owner/repo.git -> None
    """
    if "github.com/" in remote_url:
        # HTTPS format: https://github.com/owner/repo.git
        return remote_url.split("github.com/")[-1]
    elif "github.com:" in remote_url:
        # SSH format: git@github.com:owner/repo.git
        return remote_url.split("github.com:")[-1]
    return None


def _parse_fork_pr_ref(head_ref: str) -> tuple[str, str] | None:
    """
    Parse GITHUB_HEAD_REF in fork PR format (owner:branch).

    Args:
        head_ref: The GITHUB_HEAD_REF value (e.g., "owner:fix/plugin-test")

    Returns:
        (fork_owner, fork_branch) tuple if valid fork PR format, None otherwise

    Examples:
        "owner:fix/plugin-test" -> ("owner", "fix/plugin-test")
        "user:feature:part:1" -> ("user", "feature:part:1")  # branch with colons
        "main" -> None
    """
    if ":" in head_ref:
        # Split only on first colon to handle branch names containing colons
        fork_owner, fork_branch = head_ref.split(":", 1)
        return fork_owner, fork_branch
    return None


def get_git_repo_info() -> tuple[str, str]:
    """
    Get the current git repository owner/name and branch name.

    Returns:
        (repo_slug, branch) tuple
        Falls back to (ML_REPO, "main") if git info cannot be determined

    This allows tests to work correctly on forks and feature branches.
    Uses GitHub Actions environment variables for CI detection.
    """
    try:
        repo = Repo(__file__, search_parent_directories=True)

        # Get current branch name
        try:
            branch = repo.active_branch.name
        except TypeError:
            # Detached HEAD state (common in CI)
            branch = repo.git.rev_parse("--abbrev-ref", "HEAD")

            # If branch is "HEAD", check CI environment variables
            if branch == "HEAD":
                branch = _get_branch_from_ci_env()
                if not branch:
                    return ML_REPO, "main"

        # Get repository owner/name from remote URL
        remote_url = None
        if "origin" in repo.remotes:
            remote_url = repo.remotes.origin.url
        else:
            for remote in repo.remotes:
                remote_url = remote.url
                break

        if remote_url:
            repo_slug = _parse_github_remote_url(remote_url)
            if repo_slug:
                # Handle fork PRs: check GITHUB_HEAD_REF for fork owner
                head_ref = os.environ.get("GITHUB_HEAD_REF")
                if head_ref and head_ref == branch:
                    fork_info = _parse_fork_pr_ref(head_ref)
                    if fork_info:
                        fork_owner, fork_branch = fork_info
                        # Replace owner part with fork owner
                        repo_name = repo_slug.split("/")[-1]
                        repo_slug = f"{fork_owner}/{repo_name}"
                        branch = fork_branch

                # Remove .git suffix only (not all occurrences)
                repo_slug = repo_slug.removesuffix(".git")
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
        # URL-encode branch name, preserving slashes (common in branch names)
        encoded_branch = quote(local_branch, safe="/")
        mega_linter, output = utilstest.call_mega_linter(
            {
                "PLUGINS": f"https://raw.githubusercontent.com/{repo_slug}/"
                + encoded_branch
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
