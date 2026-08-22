#!/usr/bin/env python3
"""
Unit tests for CI providers Pull Request commit range resolution

"""

import json
import os
import tempfile
import unittest
import uuid
from unittest import mock

import git
from megalinter import ci_providers, config
from megalinter.ci_providers import (
    CiProvider,
    CiProviderAzurePipelines,
    CiProviderGithubActions,
    CiProviderGitlab,
)


class CiProvidersTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.init_config(self.request_id)

    def tearDown(self):
        config.delete(self.request_id)

    @staticmethod
    def init_repo(repo_dir, branch_name="main"):
        with git.Repo.init(repo_dir, initial_branch=branch_name) as repo:
            with repo.config_writer() as config_writer:
                config_writer.set_value("user", "name", "MegaLinter Test")
                config_writer.set_value("user", "email", "test@megalinter.io")
            readme = os.path.join(repo_dir, "README.md")
            with open(readme, "w", encoding="utf-8") as readme_file:
                readme_file.write("# test\n")
            repo.index.add(["README.md"])
            return repo.index.commit("Initial commit").hexsha

    def azure_provider(self, workspace):
        return CiProviderAzurePipelines(self.request_id, workspace)

    # Azure Pipelines shallow checkout has no origin/<branch> remote tracking
    # ref: the local branch must still be found instead of crashing the run
    def test_azure_target_sha_resolved_without_origin_remote(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            expected_sha = self.init_repo(repo_dir)
            provider = self.azure_provider(repo_dir)
            self.assertEqual(
                expected_sha, provider.resolve_target_branch_sha("refs/heads/main")
            )

    def test_azure_target_sha_resolved_from_bare_branch_name(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            expected_sha = self.init_repo(repo_dir)
            provider = self.azure_provider(repo_dir)
            self.assertEqual(expected_sha, provider.resolve_target_branch_sha("main"))

    # Regression test for https://github.com/oxsecurity/megalinter/issues/8732:
    # an unresolvable ref used to raise gitdb.exc.BadName from the constructor
    # of BetterleaksLinter, aborting the whole MegaLinter run
    def test_azure_target_sha_unresolvable_ref_returns_none(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            self.init_repo(repo_dir)
            provider = self.azure_provider(repo_dir)
            self.assertIsNone(
                provider.resolve_target_branch_sha("refs/heads/does-not-exist")
            )

    def test_azure_target_sha_not_a_git_repository_returns_none(self):
        with tempfile.TemporaryDirectory() as workspace:
            provider = self.azure_provider(workspace)
            self.assertIsNone(provider.resolve_target_branch_sha("refs/heads/main"))

    def test_azure_target_sha_missing_branch_variable_returns_none(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            self.init_repo(repo_dir)
            provider = self.azure_provider(repo_dir)
            self.assertIsNone(provider.resolve_target_branch_sha(None))

    def test_azure_commit_shas_on_shallow_checkout(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            self.init_repo(repo_dir, branch_name="feature/x")
            config.set_value(
                self.request_id, "SYSTEM_PULLREQUEST_SOURCECOMMITID", "deadbeef"
            )
            config.set_value(
                self.request_id, "SYSTEM_PULLREQUEST_TARGETBRANCH", "refs/heads/main"
            )
            provider = self.azure_provider(repo_dir)
            self.assertEqual(("deadbeef", None), provider.get_pr_commit_shas())

    def github_provider(self, workspace):
        return CiProviderGithubActions(self.request_id, workspace)

    def test_github_commit_shas_read_from_event_payload(self):
        with tempfile.TemporaryDirectory() as workspace:
            event_path = os.path.join(workspace, "event.json")
            with open(event_path, "w", encoding="utf-8") as event_file:
                json.dump(
                    {"pull_request": {"head": {"sha": "aaa"}, "base": {"sha": "bbb"}}},
                    event_file,
                )
            config.set_value(self.request_id, "GITHUB_EVENT_PATH", event_path)
            self.assertEqual(
                ("aaa", "bbb"), self.github_provider(workspace).get_pr_commit_shas()
            )

    def test_github_commit_shas_missing_event_path_returns_none(self):
        with tempfile.TemporaryDirectory() as workspace:
            self.assertEqual(
                (None, None), self.github_provider(workspace).get_pr_commit_shas()
            )

    def test_github_commit_shas_unreadable_event_payload_returns_none(self):
        with tempfile.TemporaryDirectory() as workspace:
            config.set_value(
                self.request_id,
                "GITHUB_EVENT_PATH",
                os.path.join(workspace, "missing-event.json"),
            )
            self.assertEqual(
                (None, None), self.github_provider(workspace).get_pr_commit_shas()
            )

    def test_github_commit_shas_payload_without_pull_request_returns_none(self):
        with tempfile.TemporaryDirectory() as workspace:
            event_path = os.path.join(workspace, "event.json")
            with open(event_path, "w", encoding="utf-8") as event_file:
                json.dump({"push": {}}, event_file)
            config.set_value(self.request_id, "GITHUB_EVENT_PATH", event_path)
            self.assertEqual(
                (None, None), self.github_provider(workspace).get_pr_commit_shas()
            )

    def gitlab_provider(self):
        return CiProviderGitlab(self.request_id, ".")

    def test_gitlab_merge_request_commit_shas(self):
        config.set_value(self.request_id, "CI_MERGE_REQUEST_SOURCE_BRANCH_SHA", "src")
        config.set_value(self.request_id, "CI_MERGE_REQUEST_TARGET_BRANCH_SHA", "tgt")
        with mock.patch("megalinter.utils.is_gitlab_premium", return_value=True):
            with mock.patch("megalinter.utils.is_gitlab_mr", return_value=True):
                self.assertEqual(
                    ("src", "tgt"), self.gitlab_provider().get_pr_commit_shas()
                )

    def test_gitlab_external_pull_request_commit_shas(self):
        config.set_value(
            self.request_id, "CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_SHA", "src"
        )
        config.set_value(
            self.request_id, "CI_EXTERNAL_PULL_REQUEST_TARGET_BRANCH_SHA", "tgt"
        )
        with mock.patch("megalinter.utils.is_gitlab_premium", return_value=True):
            with mock.patch("megalinter.utils.is_gitlab_mr", return_value=False):
                self.assertEqual(
                    ("src", "tgt"), self.gitlab_provider().get_pr_commit_shas()
                )

    # Without Premium/Ultimate GitLab does not expose the SHAs at all
    def test_gitlab_without_premium_returns_none(self):
        with mock.patch("megalinter.utils.is_gitlab_premium", return_value=False):
            self.assertEqual((None, None), self.gitlab_provider().get_pr_commit_shas())

    # The factory never returns None, so callers need no missing provider branch
    def test_factory_falls_back_to_neutral_provider(self):
        provider = ci_providers.get_pr_ci_provider(self.request_id, ".")
        self.assertIsInstance(provider, CiProvider)
        self.assertEqual((None, None), provider.get_pr_commit_shas())
        self.assertIn("not auto-detected", provider.get_pr_commit_shas_hint())

    def test_factory_detects_azure_pipelines(self):
        with mock.patch("megalinter.utils.is_azure_devops_pr", return_value=True):
            self.assertIsInstance(
                ci_providers.get_pr_ci_provider(self.request_id, "."),
                CiProviderAzurePipelines,
            )

    def test_factory_detects_github_actions(self):
        with mock.patch("megalinter.utils.is_github_pr", return_value=True):
            self.assertIsInstance(
                ci_providers.get_pr_ci_provider(self.request_id, "."),
                CiProviderGithubActions,
            )

    def test_factory_detects_gitlab(self):
        with mock.patch("megalinter.utils.is_gitlab_mr", return_value=True):
            self.assertIsInstance(
                ci_providers.get_pr_ci_provider(self.request_id, "."), CiProviderGitlab
            )

    # Every provider must offer actionable guidance when the range is missing
    def test_every_provider_exposes_a_hint(self):
        for provider_class in ci_providers.PROVIDER_CLASSES:
            hint = provider_class(self.request_id, ".").get_pr_commit_shas_hint()
            self.assertTrue(len(hint) > 0, f"{provider_class.__name__} has no hint")


if __name__ == "__main__":
    unittest.main()
