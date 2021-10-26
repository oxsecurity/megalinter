#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging
import os
import re
import urllib

import github
from megalinter import Reporter, config
from pytablewriter import MarkdownTableWriter

from megalinter.constants import ML_DOC_URL, ML_REPO, ML_REPO_URL

DOCS_URL_DESCRIPTORS_ROOT = ML_DOC_URL+"/descriptors"


def log_link(label, url):
    if url == "":
        return label
    else:
        return f"[{label}]({url})"


class GithubCommentReporter(Reporter):
    name = "GITHUB_COMMENT"
    scope = "mega-linter"

    github_api_url = "https://api.github.com"
    github_server_url = "https://github.com"
    gh_url = ML_DOC_URL
    issues_root = ML_REPO_URL + "/issues"

    def manage_activation(self):
        if config.get("GITHUB_COMMENT_REPORTER", "true") != "true":
            self.is_active = False
        elif (
            config.get("POST_GITHUB_COMMENT", "true") == "true"
        ):  # Legacy - true by default
            self.is_active = True

    def produce_report(self):
        # Post comment on GitHub pull request
        if config.get("GITHUB_TOKEN", "") != "":
            github_repo = config.get("GITHUB_REPOSITORY")
            github_server_url = config.get("GITHUB_SERVER_URL", self.github_server_url)
            github_api_url = config.get("GITHUB_API_URL", self.github_api_url)
            run_id = config.get("GITHUB_RUN_ID")
            sha = config.get("GITHUB_SHA")
            if run_id is not None:
                action_run_url = (
                    f"{github_server_url}/{github_repo}/actions/runs/{run_id}"
                )
            else:
                action_run_url = ""
            table_header = ["Descriptor", "Linter", "Files", "Fixed", "Errors"]
            if self.master.show_elapsed_time is True:
                table_header += ["Elapsed time"]
            table_data_raw = [table_header]
            for linter in self.master.linters:
                if linter.is_active is True:
                    status = (
                        "✅"
                        if linter.status == "success" and linter.return_code == 0
                        else ":warning:"
                        if linter.status != "success" and linter.return_code == 0
                        else "❌"
                    )
                    first_col = f"{status} {linter.descriptor_id}"
                    lang_lower = linter.descriptor_id.lower()
                    linter_name_lower = linter.linter_name.lower().replace("-", "_")
                    linter_doc_url = (
                        f"{DOCS_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
                    )
                    linter_link = f"[{linter.linter_name}]({linter_doc_url})"
                    nb_fixed_cell = (
                        str(linter.number_fixed) if linter.try_fix is True else ""
                    )
                    if linter.cli_lint_mode == "project":
                        found = "yes"
                        nb_fixed_cell = "yes" if nb_fixed_cell != "" else nb_fixed_cell
                        errors_cell = (
                            log_link(
                                f"**{linter.total_number_errors}**", action_run_url
                            )
                            if linter.number_errors > 0
                            else "no"
                        )
                    else:
                        found = str(len(linter.files))
                        errors_cell = (
                            log_link(
                                f"**{linter.total_number_errors}**", action_run_url
                            )
                            if linter.number_errors > 0
                            else linter.number_errors
                        )
                    table_line = [
                        first_col,
                        linter_link,
                        found,
                        nb_fixed_cell,
                        errors_cell,
                    ]
                    if self.master.show_elapsed_time is True:
                        table_line += [str(round(linter.elapsed_time_s, 2)) + "s"]
                    table_data_raw += [table_line]
            # Build markdown table
            table_data_raw.pop(0)
            writer = MarkdownTableWriter(
                headers=table_header, value_matrix=table_data_raw
            )
            table_content = str(writer) + os.linesep if len(table_data_raw) > 1 else ""
            status = (
                "✅"
                if self.master.return_code == 0 and self.master.status == "success"
                else ":warning:"
                if self.master.status == "warning"
                else "❌"
            )
            status_with_href = (
                status
                + " "
                + log_link(f"**{self.master.status.upper()}**", action_run_url)
            )
            p_r_msg = (
                f"## [Mega-Linter]({self.gh_url}) status: {status_with_href}"
                + os.linesep
                + os.linesep
            )
            p_r_msg += table_content + os.linesep
            if action_run_url != "":
                p_r_msg += (
                    "See errors details in [**artifact Mega-Linter reports** on "
                    f"GitHub Action page]({action_run_url})" + os.linesep
                )
            else:
                p_r_msg += "See errors details in Mega-Linter reports" + os.linesep
            if self.master.validate_all_code_base is False:
                p_r_msg += (
                    "_Set `VALIDATE_ALL_CODEBASE: true` in mega-linter.yml to validate "
                    + "all sources, not only the diff_"
                    + os.linesep
                )
            if self.master.flavor_suggestions is not None:
                if self.master.flavor_suggestions[0] == "new":
                    p_r_msg += (
                        os.linesep
                        + "You could have same capabilities but better runtime performances"
                        " if you request a new Mega-Linter flavor.\n"
                    )
                    body = (
                        "Mega-Linter would run faster on my project if I had a flavor containing the following "
                        "list of linters: \n\n - Add languages/linters list here\n\n"
                        "Would it be possible to create one ? Thanks :relaxed:"
                    )
                    new_flavor_url = (
                        f"{self.issues_root}/new?assignees=&labels=enhancement&template=feature_request.md"
                        f"&title={urllib.parse.quote('Request new Mega-Linter flavor')}"
                        f"&body={urllib.parse.quote(body)}"
                    )
                    p_r_msg += f"- [**Click here to request the new flavor**]({new_flavor_url})"
                else:
                    p_r_msg += (
                        os.linesep
                        + "You could have the same capabilities but better runtime performances"
                        " if you use a Mega-Linter flavor:" + os.linesep
                    )
                    for suggestion in self.master.flavor_suggestions:
                        build_version = os.environ.get("BUILD_VERSION", "v5")
                        action_version = (
                            "v5"
                            if len(build_version) > 20
                            else build_version
                        )
                        action_path = f"{ML_REPO}/flavors/{suggestion['flavor']}@{action_version}"
                        p_r_msg += (
                            f"- [**{action_path}**]({self.gh_url}/flavors/{suggestion['flavor']}/)"
                            f" ({suggestion['linters_number']} linters)"
                        )
            logging.debug("\n" + p_r_msg)
            # Post comment on pull request if found
            github_auth = (
                config.get("PAT")
                if config.get("PAT", "") != ""
                else config.get("GITHUB_TOKEN")
            )
            g = github.Github(base_url=github_api_url, login_or_token=github_auth)
            repo = g.get_repo(github_repo)

            # Try to get PR from GITHUB_REF
            pr_list = []
            ref = os.environ.get("GITHUB_REF", "")
            m = re.compile("refs/pull/(\\d+)/merge").match(ref)
            if m is not None:
                pr_id = m.group(1)
                logging.info(f"Identified PR#{pr_id} from environment")
                try:
                    pr_list = [repo.get_pull(int(pr_id))]
                except Exception as e:
                    logging.warning(f"Could not fetch PR#{pr_id}: {e}")
            if pr_list is None or len(pr_list) == 0:
                # If not found with GITHUB_REF, try to find PR from commit
                commit = repo.get_commit(sha=sha)
                pr_list = commit.get_pulls()
                if pr_list.totalCount == 0:
                    logging.info(
                        "[GitHub Comment Reporter] No pull request was found, so no comment has been posted"
                    )
                    return
            for pr in pr_list:
                # Ignore if PR is already merged
                if pr.is_merged():
                    continue
                # Check if there is already a comment from Mega-Linter
                existing_comment = None
                existing_comments = pr.get_issue_comments()
                for comment in existing_comments:
                    if (
                        "See errors details in [**artifact Mega-Linter reports** on"
                        in comment.body
                    ):
                        existing_comment = comment
                # Process comment
                try:
                    # Edit if there is already a Mega-Linter comment
                    if existing_comment is not None:
                        existing_comment.edit(p_r_msg)
                    # Or create a new PR comment
                    else:
                        pr.create_issue_comment(p_r_msg)
                    logging.debug(f"Posted Github comment: {p_r_msg}")
                    logging.info(
                        f"[GitHub Comment Reporter] Posted summary as comment on {github_repo} #PR{pr.number}"
                    )
                except github.GithubException as e:
                    logging.warning(
                        f"[GitHub Comment Reporter] Unable to post pull request comment: {str(e)}.\n"
                        "To enable this function, please :\n"
                        "1. Create a Personal Access Token (https://docs.github.com/en/free-pro-team@"
                        "latest/github/authenticating-to-github/creating-a-personal-access-token)\n"
                        "2. Create a secret named PAT with its value on your repository (https://docs."
                        "github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets#"
                        "creating-encrypted-secrets-for-a-repository)"
                        "3. Define PAT={{secrets.PAT}} in your GitHub action environment variables"
                    )
                except Exception as e:
                    logging.warning(
                        f"[GitHub Comment Reporter] Error while posting comment: \n{str(e)}"
                    )
        # Not in github context, or env var POST_GITHUB_COMMENT = false
        else:
            logging.info(
                "[GitHub Comment Reporter] No GitHub Token found, so skipped post of PR comment"
            )
