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
    CiProviderBitbucket,
    CiProviderGithubActions,
    CiProviderGitlab,
    CiProviderJenkins,
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


class CiProvidersContextTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.init_config(self.request_id)

    def tearDown(self):
        config.delete(self.request_id)

    def provider(self, provider_class):
        return provider_class(self.request_id, ".")

    # ---------------- repo / branch / job url ----------------

    def test_github_context(self):
        config.set_value(self.request_id, "GITHUB_REPOSITORY", "oxsecurity/megalinter")
        config.set_value(self.request_id, "GITHUB_REF_NAME", "feature/x")
        config.set_value(self.request_id, "GITHUB_RUN_ID", "42")
        provider = self.provider(CiProviderGithubActions)
        self.assertEqual("megalinter", provider.get_repo_name())
        self.assertEqual("feature/x", provider.get_branch_name())
        self.assertEqual(
            "https://github.com/oxsecurity/megalinter/actions/runs/42",
            provider.get_job_url(),
        )

    def test_github_head_ref_wins_over_ref_name(self):
        config.set_value(self.request_id, "GITHUB_HEAD_REF", "pr-branch")
        config.set_value(self.request_id, "GITHUB_REF_NAME", "merge-ref")
        self.assertEqual(
            "pr-branch", self.provider(CiProviderGithubActions).get_branch_name()
        )

    def test_github_job_url_empty_without_repository(self):
        self.assertEqual("", self.provider(CiProviderGithubActions).get_job_url())

    def test_gitlab_context(self):
        config.set_value(self.request_id, "CI_PROJECT_NAME", "megalinter")
        config.set_value(self.request_id, "CI_COMMIT_REF_NAME", "main")
        config.set_value(self.request_id, "CI_JOB_URL", "https://gitlab.com/job/1")
        provider = self.provider(CiProviderGitlab)
        self.assertEqual("megalinter", provider.get_repo_name())
        self.assertEqual("main", provider.get_branch_name())
        self.assertEqual("https://gitlab.com/job/1", provider.get_job_url())

    def test_azure_context_and_build_id_fallback(self):
        config.set_value(self.request_id, "BUILD_REPOSITORYNAME", "org/megalinter")
        config.set_value(self.request_id, "BUILD_SOURCEBRANCHNAME", "main")
        config.set_value(
            self.request_id, "SYSTEM_COLLECTIONURI", "https://dev.azure.com/o/"
        )
        config.set_value(self.request_id, "SYSTEM_TEAMPROJECT", "My Project")
        config.set_value(self.request_id, "BUILD_BUILD_ID", "77")
        provider = self.provider(CiProviderAzurePipelines)
        self.assertEqual("megalinter", provider.get_repo_name())
        self.assertEqual("main", provider.get_branch_name())
        # BUILD_BUILDID is absent, so the BUILD_BUILD_ID spelling must be used,
        # and the project name must be url-encoded
        self.assertEqual(
            "https://dev.azure.com/o/My%20Project/_build/results?buildId=77",
            provider.get_job_url(),
        )

    def test_bitbucket_context(self):
        config.set_value(self.request_id, "BITBUCKET_REPO_SLUG", "megalinter")
        config.set_value(self.request_id, "BITBUCKET_BRANCH", "main")
        config.set_value(self.request_id, "BITBUCKET_STEP_UUID", "{uuid-1}")
        config.set_value(self.request_id, "BITBUCKET_BUILD_NUMBER", "12")
        config.set_value(
            self.request_id, "BITBUCKET_GIT_HTTP_ORIGIN", "https://bitbucket.org/o/r"
        )
        provider = self.provider(CiProviderBitbucket)
        self.assertEqual("megalinter", provider.get_repo_name())
        self.assertEqual("main", provider.get_branch_name())
        self.assertEqual(
            "https://bitbucket.org/o/r/pipelines/results/12/steps/%7Buuid-1%7D",
            provider.get_job_url(),
        )

    def test_neutral_provider_context_is_empty(self):
        provider = self.provider(CiProvider)
        self.assertIsNone(provider.get_repo_name())
        self.assertIsNone(provider.get_branch_name())
        self.assertEqual("", provider.get_job_url())

    # ---------------- log folding ----------------

    def test_github_log_sections(self):
        provider = self.provider(CiProviderGithubActions)
        self.assertTrue(
            provider.log_section_start("k", "Title").startswith("::group::")
        )
        self.assertEqual("::endgroup::", provider.log_section_end("k"))

    def test_azure_log_sections(self):
        provider = self.provider(CiProviderAzurePipelines)
        self.assertTrue(
            provider.log_section_start("k", "Title").startswith("##[group]")
        )
        self.assertEqual("##[endgroup]", provider.log_section_end("k"))

    def test_gitlab_log_sections_sanitize_the_key(self):
        provider = self.provider(CiProviderGitlab)
        started = provider.log_section_start("some key/with:chars", "Title")
        self.assertIn("some_key_with_chars", started)
        self.assertIn("[collapsed=true]", started)
        self.assertIn(
            "some_key_with_chars", provider.log_section_end("some key/with:chars")
        )

    def test_gitlab_section_key_never_empty(self):
        self.assertEqual("section", CiProviderGitlab.sanitize_section_key("///"))
        self.assertEqual(80, len(CiProviderGitlab.sanitize_section_key("a" * 200)))

    # Bitbucket and Jenkins have no folding syntax: plain title, empty end
    def test_providers_without_folding(self):
        for provider_class in (CiProviderBitbucket, CiProviderJenkins, CiProvider):
            provider = self.provider(provider_class)
            self.assertEqual("Title", provider.log_section_start("k", "Title"))
            self.assertEqual("", provider.log_section_end("k"))

    # ---------------- job outputs ----------------

    def test_github_set_output_and_job_summary(self):
        with tempfile.TemporaryDirectory() as workspace:
            output_file = os.path.join(workspace, "out.txt")
            summary_file = os.path.join(workspace, "summary.md")
            config.set_value(self.request_id, "GITHUB_OUTPUT", output_file)
            config.set_value(self.request_id, "GITHUB_STEP_SUMMARY", summary_file)
            provider = self.provider(CiProviderGithubActions)
            self.assertTrue(provider.set_output("has_updated_sources", "True"))
            self.assertTrue(provider.publish_job_summary("# Summary\n"))
            with open(output_file, encoding="utf-8") as f:
                self.assertEqual("has_updated_sources=True\n", f.read())
            with open(summary_file, encoding="utf-8") as f:
                self.assertEqual("# Summary\n", f.read())

    def test_github_outputs_noop_without_variables(self):
        provider = self.provider(CiProviderGithubActions)
        self.assertFalse(provider.set_output("k", "v"))
        self.assertFalse(provider.publish_job_summary("x"))

    # A runner-owned file that can not be written must not break the run
    def test_github_output_unwritable_path_returns_false(self):
        with tempfile.TemporaryDirectory() as workspace:
            config.set_value(
                self.request_id,
                "GITHUB_OUTPUT",
                os.path.join(workspace, "missing-dir", "out.txt"),
            )
            self.assertFalse(
                self.provider(CiProviderGithubActions).set_output("k", "v")
            )

    def test_other_providers_do_not_support_outputs(self):
        for provider_class in (CiProviderGitlab, CiProviderBitbucket, CiProvider):
            provider = self.provider(provider_class)
            self.assertFalse(provider.set_output("k", "v"))
            self.assertFalse(provider.publish_job_summary("x"))

    # ---------------- capabilities ----------------

    def test_bitbucket_does_not_support_html_details(self):
        self.assertFalse(CiProviderBitbucket.markdown_supports_html_details)
        self.assertTrue(CiProvider.markdown_supports_html_details)
        self.assertTrue(CiProviderGithubActions.markdown_supports_html_details)

    # ---------------- get_ci_provider factory ----------------

    def test_get_ci_provider_detects_each_platform(self):
        cases = [
            ("megalinter.utils.is_azure_pipelines", CiProviderAzurePipelines),
            ("megalinter.utils.is_github_actions", CiProviderGithubActions),
            ("megalinter.utils.is_gitlab_ci", CiProviderGitlab),
            ("megalinter.utils.is_bitbucket", CiProviderBitbucket),
            ("megalinter.utils.is_jenkins", CiProviderJenkins),
        ]
        for target, expected_class in cases:
            with mock.patch(target, return_value=True):
                self.assertIsInstance(
                    ci_providers.get_ci_provider(self.request_id), expected_class
                )

    def test_get_ci_provider_falls_back_to_neutral_provider(self):
        provider = ci_providers.get_ci_provider(self.request_id)
        self.assertIs(type(provider), CiProvider)


if __name__ == "__main__":
    unittest.main()
