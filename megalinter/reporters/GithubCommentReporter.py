#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging
from megalinter.utils_reporter import build_markdown_summary
import os
import re
import github
from megalinter import Reporter, config
from megalinter.constants import ML_DOC_URL, ML_REPO_URL
from pytablewriter import MarkdownTableWriter

mega_linter_version = config.get("BUILD_VERSION", "latest")
DOCS_URL_DESCRIPTORS_ROOT = f"{ML_DOC_URL}/{mega_linter_version}/descriptors"


class GithubCommentReporter(Reporter):
    name = "GITHUB_COMMENT"
    scope = "mega-linter"

    github_api_url = "https://api.github.com"
    github_server_url = "https://github.com"
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
            p_r_msg = build_markdown_summary(self, action_run_url)

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
                        "[GitHub Comment Reporter] No pull request has been found, so no comment has been posted"
                    )
                    return
            for pr in pr_list:
                # Ignore if PR is already merged
                if pr.is_merged():
                    continue
                # Check if there is already a comment from MegaLinter
                existing_comment = None
                existing_comments = pr.get_issue_comments()
                for comment in existing_comments:
                    if (
                        "See errors details in [**artifact MegaLinter reports** on"
                        in comment.body
                    ):
                        existing_comment = comment
                # Process comment
                try:
                    # Edit if there is already a MegaLinter comment
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
            logging.debug(
                "[GitHub Comment Reporter] No GitHub Token has been found, so skipped post of PR comment"
            )
