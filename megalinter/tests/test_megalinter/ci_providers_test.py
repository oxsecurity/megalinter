#!/usr/bin/env python3
"""
Unit tests for CI providers Pull Request commit range resolution

"""

import base64
import json
import os
import tempfile
import unittest
import uuid
from contextlib import ExitStack
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

# Platform variables that must not leak into the tests from the environment
# actually running them: this suite runs inside GitHub Actions, where
# GITHUB_ACTIONS, GITHUB_REPOSITORY, GITHUB_RUN_ID and friends are really set
CI_VAR_PREFIXES = (
    "GITHUB_",
    "CI_",
    "BITBUCKET_",
    "SYSTEM_",
    "BUILD_",
    "JENKINS_",
    "GITLAB_",
)
CI_VAR_NAMES = (
    "TF_BUILD",
    "CI",
    "PAT",
    "PULL_REQUEST",
    "GIT_URL",
    "GIT_BRANCH",
    "CHANGE_ID",
    "CHANGE_URL",
    "MEGALINTER_MULTIRUN_KEY",
)


class CiProviderTestCase(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.init_config(self.request_id)
        # Start from a platform-neutral configuration, whatever CI runs this
        for key in list(config.copy(self.request_id).keys()):
            if key.startswith(CI_VAR_PREFIXES) or key in CI_VAR_NAMES:
                config.delete(self.request_id, key)

    def tearDown(self):
        config.delete(self.request_id)

    # The is_* detectors read the global configuration, not the request one, so
    # clearing the request config is not enough: activate exactly one provider
    def activate_only(self, stack, provider_class, method):
        for candidate in ci_providers.PROVIDER_CLASSES:
            stack.enter_context(
                mock.patch.object(
                    candidate, method, return_value=candidate is provider_class
                )
            )


class CiProvidersTest(CiProviderTestCase):

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
        with ExitStack() as stack:
            self.activate_only(stack, None, "is_pr_context")
            provider = ci_providers.get_pr_ci_provider(self.request_id, ".")
        self.assertIs(type(provider), CiProvider)
        self.assertEqual((None, None), provider.get_pr_commit_shas())
        self.assertIn("not auto-detected", provider.get_pr_commit_shas_hint())

    def test_factory_detects_each_pull_request_platform(self):
        for provider_class in ci_providers.PROVIDER_CLASSES:
            with ExitStack() as stack:
                self.activate_only(stack, provider_class, "is_pr_context")
                self.assertIsInstance(
                    ci_providers.get_pr_ci_provider(self.request_id, "."),
                    provider_class,
                )

    # Every provider must offer actionable guidance when the range is missing
    def test_every_provider_exposes_a_hint(self):
        for provider_class in ci_providers.PROVIDER_CLASSES:
            hint = provider_class(self.request_id, ".").get_pr_commit_shas_hint()
            self.assertTrue(len(hint) > 0, f"{provider_class.__name__} has no hint")


class CiProvidersContextTest(CiProviderTestCase):

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
        for provider_class in ci_providers.PROVIDER_CLASSES:
            with ExitStack() as stack:
                self.activate_only(stack, provider_class, "is_current")
                self.assertIsInstance(
                    ci_providers.get_ci_provider(self.request_id), provider_class
                )

    def test_get_ci_provider_falls_back_to_neutral_provider(self):
        with ExitStack() as stack:
            self.activate_only(stack, None, "is_current")
            self.assertIs(
                type(ci_providers.get_ci_provider(self.request_id)), CiProvider
            )


# The four comment reporters used to read these variables themselves. The
# values they now get from the providers must stay identical, in particular
# the API urls and the auth headers
class CiProvidersReporterContextTest(CiProviderTestCase):

    def set_values(self, values):
        for key, value in values.items():
            config.set_value(self.request_id, key, value)

    # ---------------- Azure ----------------

    def azure_provider(self):
        self.set_values(
            {
                "SYSTEM_COLLECTIONURI": "https://dev.azure.com/myorg/",
                "SYSTEM_TEAMPROJECT": "My Project",
                "SYSTEM_PULLREQUEST_PULLREQUESTID": "123",
                "BUILD_BUILDID": "456",
                "BUILD_REPOSITORY_ID": "repo-guid",
                "SYSTEM_ACCESSTOKEN": "tok",
            }
        )
        return CiProviderAzurePipelines(self.request_id)

    def test_azure_git_api_url_matches_previous_format(self):
        provider = self.azure_provider()
        self.assertEqual(
            "https://dev.azure.com/myorg/My%20Project/_apis/git"
            "/repositories/repo-guid/pullRequests/123/threads?api-version=7.1",
            provider.build_git_api_url(
                "/repositories/repo-guid/pullRequests/123/threads"
            ),
        )

    def test_azure_api_headers_are_basic_auth_with_empty_user(self):
        header = self.azure_provider().get_api_headers()["Authorization"]
        scheme, _, encoded = header.partition(" ")
        self.assertEqual("Basic", scheme)
        # The ADO REST API expects an empty user name before the token
        self.assertEqual(b":tok", base64.b64decode(encoded))

    def test_azure_artifacts_url(self):
        self.assertEqual(
            "https://dev.azure.com/myorg/My%20Project/_build/results?buildId=456"
            "&view=artifacts&pathAsName=false&type=publishedArtifacts",
            self.azure_provider().get_artifacts_url(),
        )

    def test_azure_pr_number_and_token(self):
        provider = self.azure_provider()
        self.assertEqual("123", provider.get_pr_number())
        self.assertEqual("tok", provider.get_auth_token())

    def test_azure_repository_id_falls_back_without_source_uri(self):
        # No SYSTEM_PULLREQUEST_SOURCEREPOSITORYURI: BUILD_REPOSITORY_ID is used
        # and no API call is attempted
        self.assertEqual("repo-guid", self.azure_provider().get_repository_id())

    def test_azure_repository_id_falls_back_when_lookup_fails(self):
        provider = self.azure_provider()
        config.set_value(
            self.request_id,
            "SYSTEM_PULLREQUEST_SOURCEREPOSITORYURI",
            "https://dev.azure.com/myorg/_git/My%20Repo",
        )
        with mock.patch("requests.get", side_effect=Exception("boom")):
            self.assertEqual("repo-guid", provider.get_repository_id())

    def test_azure_repository_id_from_source_repository_uri(self):
        provider = self.azure_provider()
        config.set_value(
            self.request_id,
            "SYSTEM_PULLREQUEST_SOURCEREPOSITORYURI",
            "https://dev.azure.com/myorg/_git/My%20Repo",
        )
        response = mock.Mock(status_code=200)
        response.json.return_value = {"id": "resolved-guid"}
        with mock.patch("requests.get", return_value=response) as requests_get:
            self.assertEqual("resolved-guid", provider.get_repository_id())
        # %20 is turned into a space before the lookup, as the reporter did
        self.assertIn("/repositories/My Repo?", requests_get.call_args[0][0])

    # ---------------- GitHub ----------------

    def test_github_pr_number_from_ref(self):
        config.set_value(self.request_id, "GITHUB_REF", "refs/pull/42/merge")
        self.assertEqual("42", CiProviderGithubActions(self.request_id).get_pr_number())

    def test_github_pr_number_none_on_other_refs(self):
        config.set_value(self.request_id, "GITHUB_REF", "refs/heads/main")
        self.assertIsNone(CiProviderGithubActions(self.request_id).get_pr_number())

    # PAT must NOT replace GITHUB_TOKEN: commit statuses need statuses:write,
    # which the documented fine-grained PAT (Contents only) does not carry
    def test_github_runner_token_and_user_token_stay_distinct(self):
        self.set_values({"GITHUB_TOKEN": "runner", "PAT": "user"})
        provider = CiProviderGithubActions(self.request_id)
        self.assertEqual("runner", provider.get_auth_token())
        self.assertEqual("user", provider.get_user_auth_token())

    def test_github_user_token_absent(self):
        config.set_value(self.request_id, "GITHUB_TOKEN", "runner")
        provider = CiProviderGithubActions(self.request_id)
        self.assertIsNone(provider.get_user_auth_token())
        self.assertEqual(
            "runner", provider.get_user_auth_token() or provider.get_auth_token()
        )

    def test_github_api_url_default(self):
        self.assertEqual(
            "https://api.github.com",
            CiProviderGithubActions(self.request_id).get_api_url(),
        )

    # ---------------- GitLab ----------------

    def test_gitlab_auth_options_prefer_the_user_token(self):
        self.set_values(
            {
                "CI_JOB_TOKEN": "job",
                "GITLAB_ACCESS_TOKEN_MEGALINTER": "user",
            }
        )
        self.assertEqual(
            {"private_token": "user"},
            CiProviderGitlab(self.request_id).get_api_auth_options(),
        )

    def test_gitlab_auth_options_fall_back_to_the_job_token(self):
        config.set_value(self.request_id, "CI_JOB_TOKEN", "job")
        self.assertEqual(
            {"job_token": "job"},
            CiProviderGitlab(self.request_id).get_api_auth_options(),
        )

    def test_gitlab_merge_request_id_from_open_merge_requests(self):
        config.set_value(
            self.request_id, "CI_OPEN_MERGE_REQUESTS", "group/proj!17,group/proj!18"
        )
        self.assertEqual("17", CiProviderGitlab(self.request_id).get_pr_number())

    def test_gitlab_merge_request_id_prefers_the_explicit_variable(self):
        self.set_values(
            {
                "CI_MERGE_REQUEST_ID": "99",
                "CI_OPEN_MERGE_REQUESTS": "group/proj!17",
            }
        )
        self.assertEqual("99", CiProviderGitlab(self.request_id).get_pr_number())

    def test_gitlab_merge_request_id_none_when_nothing_is_set(self):
        self.assertIsNone(CiProviderGitlab(self.request_id).get_pr_number())

    # ---------------- Bitbucket ----------------

    def test_bitbucket_reporter_context(self):
        self.set_values(
            {
                "BITBUCKET_REPO_FULL_NAME": "org/repo",
                "BITBUCKET_PR_ID": "8",
                "BITBUCKET_REPO_ACCESS_TOKEN": "tok",
            }
        )
        provider = CiProviderBitbucket(self.request_id)
        self.assertEqual("org/repo", provider.get_repo_slug())
        self.assertEqual("8", provider.get_pr_number())
        self.assertEqual({"Authorization": "Bearer tok"}, provider.get_api_headers())

    def test_bitbucket_context_none_when_unset(self):
        provider = CiProviderBitbucket(self.request_id)
        self.assertIsNone(provider.get_repo_slug())
        self.assertIsNone(provider.get_pr_number())
        self.assertIsNone(provider.get_auth_token())


if __name__ == "__main__":
    unittest.main()
