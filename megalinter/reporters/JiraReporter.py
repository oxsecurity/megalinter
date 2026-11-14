#!/usr/bin/env python3
"""
Jira reporter
Post a comment on the Jira tickets referenced by labels of the current Pull Request
"""

import logging
import re

from atlassian import Jira
from megalinter import Reporter, ci_providers, config
from megalinter.utils_reporter import build_markdown_summary

DEFAULT_LABEL_REGEX = r"^(?:jira[:/])?([A-Za-z][A-Za-z0-9_]+-\d+)$"

# Jira rejects comments over 32767 characters, wiki markup adds a bit to the markdown
MAX_MARKDOWN_CHARS = 30000

PLACEHOLDER = "\x00{}\x00"
FENCE_REGEX = re.compile(r"^\s*```")
HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.*)$")
TABLE_ROW_REGEX = re.compile(r"^\s*\|(.*)\|\s*$")
TABLE_SEPARATOR_REGEX = re.compile(r"^[\s|:-]+$")
BULLET_REGEX = re.compile(r"^(\s*)[-*+]\s+(.*)$")
NUMBERED_REGEX = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
HR_REGEX = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")


def escape_braces(text):
    return text.replace("{", "\\{").replace("}", "\\}")


# Converts the inline markdown subset produced by MegaLinter reports to Jira wiki markup
def convert_inline(text):
    protected = []

    def protect(value):
        protected.append(value)
        return PLACEHOLDER.format(len(protected) - 1)

    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(
        r"`([^`]+)`", lambda m: protect("{{" + escape_braces(m.group(1)) + "}}"), text
    )
    text = re.sub(
        r"!\[[^\]]*\]\(([^)\s]+)[^)]*\)", lambda m: protect(f"!{m.group(1)}!"), text
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)[^)]*\)",
        lambda m: protect(f"[{m.group(1)}|{m.group(2)}]"),
        text,
    )
    text = re.sub(r"</?[A-Za-z][^>]*>", "", text)
    text = re.sub(r"(\*\*|__)(.+?)\1", lambda m: protect(f"*{m.group(2)}*"), text)
    text = re.sub(r"~~(.+?)~~", lambda m: protect(f"-{m.group(1)}-"), text)
    # Braces start Jira macros
    text = escape_braces(text)
    # Restore, innermost last: placeholders may be nested in bold
    for _ in range(3):
        text = re.sub("\x00(\\d+)\x00", lambda m: protected[int(m.group(1))], text)
    return text


def convert_table_row(line, is_header):
    cells = [cell.strip() for cell in TABLE_ROW_REGEX.match(line).group(1).split("|")]
    cells = [convert_inline(cell) or " " for cell in cells]
    separator = "||" if is_header else "|"
    return separator + separator.join(cells) + separator


# Converts the markdown built by build_markdown_summary to Jira wiki markup
def markdown_to_jira(markdown):
    output = []
    in_code = False
    in_table = False
    for line in markdown.splitlines():
        if FENCE_REGEX.match(line):
            output.append("{code}")
            in_code = not in_code
            continue
        if in_code:
            output.append(line)
            continue
        table_match = TABLE_ROW_REGEX.match(line)
        if table_match:
            if TABLE_SEPARATOR_REGEX.match(table_match.group(1)):
                continue
            output.append(convert_table_row(line, not in_table))
            in_table = True
            continue
        in_table = False
        heading = HEADING_REGEX.match(line)
        bullet = BULLET_REGEX.match(line)
        numbered = NUMBERED_REGEX.match(line)
        if heading:
            output.append(
                f"h{len(heading.group(1))}. {convert_inline(heading.group(2))}"
            )
        elif HR_REGEX.match(line):
            output.append("----")
        elif bullet:
            depth = len(bullet.group(1).replace("\t", "  ")) // 2 + 1
            output.append("*" * depth + " " + convert_inline(bullet.group(2)))
        elif numbered:
            depth = len(numbered.group(1).replace("\t", "  ")) // 2 + 1
            output.append("#" * depth + " " + convert_inline(numbered.group(2)))
        elif line.startswith(">"):
            output.append("bq. " + convert_inline(line.lstrip("> ")))
        else:
            output.append(convert_inline(line))
    if in_code:
        output.append("{code}")
    return "\n".join(output)


class JiraReporter(Reporter):
    name = "JIRA"
    scope = "mega-linter"
    # Jira wiki markup has no collapsible section: render sections as headings
    markdown_supports_html_details = False

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

    # Jira comments use the Jira wiki markup, so the markdown summary is converted
    def build_comment(self, job_url, pr_ref):
        markdown = build_markdown_summary(self, job_url, MAX_MARKDOWN_CHARS)
        return "\n".join(
            [
                markdown_to_jira(markdown),
                "",
                f"Pull Request: {pr_ref}",
                "",
                f"{{noformat}}{self.get_comment_marker()}{{noformat}}",
            ]
        )

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
