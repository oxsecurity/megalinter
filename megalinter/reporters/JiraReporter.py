#!/usr/bin/env python3
"""
Jira reporter
Post a comment on the Jira tickets referenced by labels of the current Pull Request
"""

import logging
import re

from atlassian import Jira
from megalinter import Reporter, ci_providers, config
from megalinter.utils_reporter import get_linter_summary_data

DEFAULT_LABEL_REGEX = r"^(?:jira[:/])?([A-Za-z][A-Za-z0-9_]+-\d+)$"


class JiraReporter(Reporter):
    name = "JIRA"
    scope = "mega-linter"

    def manage_activation(self):
        request_id = self.master.request_id
        if config.get(request_id, "JIRA_REPORTER", "true") != "true":
            self.is_active = False
        elif not config.exists(request_id, "JIRA_URL"):
            self.is_active = False
        elif not config.exists(request_id, "JIRA_API_TOKEN") and not config.exists(
            request_id, "JIRA_PERSONAL_ACCESS_TOKEN"
        ):
            self.is_active = False
        else:
            self.is_active = True

    def get_comment_marker(self):
        multirun_key = config.get(self.master.request_id, "MEGALINTER_MULTIRUN_KEY", "")
        suffix = f" key={multirun_key!r}" if multirun_key else ""
        return f"megalinter: jira-reporter{suffix}"

    def produce_report(self):
        request_id = self.master.request_id
        labels, job_url, pr_ref = self.get_pull_request_info()
        if labels is None:
            return
        issue_keys = self.extract_issue_keys(labels)
        if len(issue_keys) == 0:
            logging.info(
                f"[Jira Reporter] No label referencing a Jira ticket found on {pr_ref}, "
                "so no Jira comment has been posted"
            )
            return
        job_url = config.get(request_id, "REPORTERS_ACTION_RUN_URL", job_url)
        comment = self.build_comment(job_url, pr_ref)
        jira = self.build_jira_client()
        for issue_key in issue_keys:
            try:
                self.post_comment(jira, issue_key, comment)
            except Exception as e:
                logging.warning(
                    f"[Jira Reporter] Unable to post comment on {issue_key}: {e}\n"
                    "See https://megalinter.io/latest/reporters/JiraReporter/"
                )

    def extract_issue_keys(self, labels):
        regex = re.compile(
            config.get(
                self.master.request_id, "JIRA_REPORTER_LABEL_REGEX", DEFAULT_LABEL_REGEX
            )
        )
        issue_keys = []
        for label in labels:
            match = regex.match(label.strip())
            if match is None:
                continue
            issue_key = (match.group(1) if match.groups() else match.group(0)).upper()
            if issue_key not in issue_keys:
                issue_keys.append(issue_key)
        return issue_keys

    # Returns (labels, report url, pull request reference), labels being None
    # when the current platform exposes no Pull Request labels
    def get_pull_request_info(self):
        ci_provider = ci_providers.get_pr_ci_provider(self.master.request_id)
        labels = ci_provider.get_pr_labels()
        if labels is None:
            logging.info(
                f"[Jira Reporter] No Pull Request labels available on {ci_provider.name}, "
                "so no Jira comment has been posted"
            )
            return None, "", ""
        return labels, ci_provider.get_report_url(), ci_provider.get_pr_reference()

    def build_jira_client(self):
        request_id = self.master.request_id
        url = config.get(request_id, "JIRA_URL")
        username = config.get(request_id, "JIRA_USERNAME", "")
        api_token = config.get(request_id, "JIRA_API_TOKEN", "")
        if api_token != "":
            # Jira Cloud: basic authentication with e-mail and API token
            return Jira(url=url, username=username, password=api_token, cloud=True)
        # Jira Server / Data Center: Personal Access Token
        return Jira(
            url=url,
            token=config.get(request_id, "JIRA_PERSONAL_ACCESS_TOKEN"),
            cloud=False,
        )

    # Jira comments use the Jira wiki markup, not markdown
    def build_comment(self, job_url, pr_ref):
        master = self.master
        if master.status == "warning":
            status_line = "(!) *MegaLinter: success with warnings*"
        elif master.return_code == 0 and master.status == "success":
            status_line = "(/) *MegaLinter: success*"
        else:
            status_line = "(x) *MegaLinter: error*"
        lines = [status_line, ""]
        lines.append(f"Pull Request: {pr_ref}")
        lines.append("")
        lines.append("||Linter||Descriptor||Errors||Warnings||")
        for linter in master.linters:
            if linter.is_active is not True:
                continue
            data = get_linter_summary_data(linter)
            lines.append(
                f"|{linter.linter_name}|{data['descriptor_id']}|"
                f"{linter.total_number_errors}|{linter.total_number_warnings}|"
            )
        if job_url:
            lines.extend(["", f"[Detailed logs|{job_url}]"])
        lines.extend(["", f"{{noformat}}{self.get_comment_marker()}{{noformat}}"])
        return "\n".join(lines)

    def post_comment(self, jira, issue_key, comment):
        marker = self.get_comment_marker()
        overwrite = (
            config.get(
                self.master.request_id, "JIRA_REPORTER_OVERWRITE_COMMENT", "true"
            )
            == "true"
        )
        if overwrite:
            existing = jira.issue_get_comments(issue_key).get("comments", [])
            for existing_comment in existing:
                if marker in str(existing_comment.get("body", "")):
                    jira.issue_edit_comment(issue_key, existing_comment["id"], comment)
                    logging.info(
                        f"[Jira Reporter] Updated existing comment on {issue_key}"
                    )
                    return
        jira.issue_add_comment(issue_key, comment)
        logging.info(f"[Jira Reporter] Posted summary as comment on {issue_key}")
