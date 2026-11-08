#!/usr/bin/env python3
import unittest
import uuid
from unittest import mock

from megalinter import config
from megalinter.ci_providers import CiProviderAzurePipelines, CiProviderGithubActions
from megalinter.reporters.JiraReporter import JiraReporter


class FakeMaster:
    def __init__(self, request_id):
        self.request_id = request_id
        self.status = "error"
        self.return_code = 1
        self.linters = []


class JiraReporterTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.init_config(self.request_id)
        for key in list(config.copy(self.request_id).keys()):
            if key.startswith("JIRA_") or key == "REPORTERS_ACTION_RUN_URL":
                config.delete(self.request_id, key)
        config.set_value(self.request_id, "JIRA_URL", "https://jira.example.com")
        config.set_value(self.request_id, "JIRA_API_TOKEN", "tok")
        config.set_value(self.request_id, "JIRA_USERNAME", "me@example.com")

    def tearDown(self):
        config.delete(self.request_id)

    def build_reporter(self):
        return JiraReporter(
            {"master": FakeMaster(self.request_id), "report_folder": "."}
        )

    def mock_provider(self, provider_class, labels, reference, url):
        provider = mock.create_autospec(provider_class, instance=True)
        provider.name = provider_class.name
        provider.get_pr_labels.return_value = labels
        provider.get_pr_reference.return_value = reference
        provider.get_report_url.return_value = url
        return mock.patch(
            "megalinter.ci_providers.get_pr_ci_provider", return_value=provider
        )

    def run_reporter(self, provider_patch, existing_comments=None):
        with (
            provider_patch,
            mock.patch("megalinter.reporters.JiraReporter.Jira") as jira_class,
        ):
            jira = jira_class.return_value
            jira.issue_get_comments.return_value = {"comments": existing_comments or []}
            self.build_reporter().produce_report()
        return jira_class, jira

    def test_activation(self):
        self.assertTrue(self.build_reporter().is_active)
        config.set_value(self.request_id, "JIRA_REPORTER", "false")
        self.assertFalse(self.build_reporter().is_active)
        config.set_value(self.request_id, "JIRA_REPORTER", "true")
        config.delete(self.request_id, "JIRA_URL")
        self.assertFalse(self.build_reporter().is_active)

    def test_github_posts_comment_on_labelled_ticket(self):
        patch = self.mock_provider(
            CiProviderGithubActions,
            ["bug", "PROJ-12", "jira:OTHER-3"],
            "org/repo #PR5",
            "https://github.com/org/repo/actions/runs/1",
        )
        jira_class, jira = self.run_reporter(patch)
        jira_class.assert_called_once_with(
            url="https://jira.example.com",
            username="me@example.com",
            password="tok",
            cloud=True,
        )
        self.assertEqual(
            ["PROJ-12", "OTHER-3"],
            [call.args[0] for call in jira.issue_add_comment.call_args_list],
        )
        body = jira.issue_add_comment.call_args_list[0].args[1]
        self.assertIn("org/repo #PR5", body)
        self.assertIn("https://github.com/org/repo/actions/runs/1", body)

    def test_azure_uses_report_url_and_updates_existing_comment(self):
        patch = self.mock_provider(
            CiProviderAzurePipelines,
            ["PROJ-7"],
            "proj #PR9",
            "https://dev.azure.com/org/proj/_build/results?buildId=1&view=artifacts",
        )
        existing = [
            {"id": "55", "body": "x {noformat}megalinter: jira-reporter{noformat}"}
        ]
        _, jira = self.run_reporter(patch, existing)
        jira.issue_add_comment.assert_not_called()
        key, comment_id, body = jira.issue_edit_comment.call_args.args
        self.assertEqual(("PROJ-7", "55"), (key, comment_id))
        self.assertIn("view=artifacts", body)

    def test_no_overwrite_always_adds_comment(self):
        config.set_value(self.request_id, "JIRA_REPORTER_OVERWRITE_COMMENT", "false")
        patch = self.mock_provider(CiProviderGithubActions, ["PROJ-1"], "r #PR1", "")
        _, jira = self.run_reporter(patch)
        jira.issue_get_comments.assert_not_called()
        jira.issue_add_comment.assert_called_once()

    def test_personal_access_token_for_server(self):
        config.delete(self.request_id, "JIRA_API_TOKEN")
        config.set_value(self.request_id, "JIRA_PERSONAL_ACCESS_TOKEN", "pat")
        patch = self.mock_provider(CiProviderGithubActions, ["PROJ-1"], "r #PR1", "")
        jira_class, _ = self.run_reporter(patch)
        jira_class.assert_called_once_with(
            url="https://jira.example.com", token="pat", cloud=False
        )

    def test_nothing_posted_without_labels_or_ticket_label(self):
        for labels in (None, [], ["bug", "enhancement"]):
            patch = self.mock_provider(CiProviderGithubActions, labels, "r #PR1", "")
            jira_class, jira = self.run_reporter(patch)
            jira.issue_add_comment.assert_not_called()
            jira.issue_edit_comment.assert_not_called()

    def test_jira_error_does_not_raise(self):
        patch = self.mock_provider(CiProviderGithubActions, ["PROJ-1"], "r #PR1", "")
        with patch, mock.patch("megalinter.reporters.JiraReporter.Jira") as jira_class:
            jira_class.return_value.issue_get_comments.side_effect = Exception("boom")
            self.build_reporter().produce_report()


if __name__ == "__main__":
    unittest.main()
