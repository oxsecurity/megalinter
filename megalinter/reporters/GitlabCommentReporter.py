#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging

import gitlab
from megalinter import Reporter, config
from megalinter.utils_reporter import build_markdown_summary


class GitlabCommentReporter(Reporter):
    name = "GITLAB_COMMENT"
    scope = "mega-linter"

    gitlab_server_url = "https://gitlab.com"

    def manage_activation(self):
        if config.get("GITLAB_COMMENT_REPORTER", "true") != "true":
            self.is_active = False
        elif (
            config.get("POST_GITLAB_COMMENT", "true") == "true"
        ):  # Legacy - true by default
            self.is_active = True

    def produce_report(self):
        # Post comment on GitHub pull request
        if config.get("CI_JOB_TOKEN", "") != "":
            gitlab_repo = config.get("CI_PROJECT_NAME")
            gitlab_project_id = config.get("CI_PROJECT_ID")
            gitlab_merge_request_id = config.get("CI_MERGE_REQUEST_ID", "")
            if (
                gitlab_merge_request_id == ""
                and config.get("CI_OPEN_MERGE_REQUESTS", "") != ""
            ):
                gitlab_merge_request_id = (
                    config.get("CI_OPEN_MERGE_REQUESTS", "missing!missing")
                    .split(",")[0]
                    .split("!")[1]
                )
            gitlab_server_url = config.get("CI_SERVER_URL", self.gitlab_server_url)
            action_run_url = config.get("CI_JOB_URL", "")
            p_r_msg = build_markdown_summary(self, action_run_url)

            # Post comment on merge request if found
            if config.get("GITLAB_ACCESS_TOKEN_MEGALINTER", "") != "":
                gl = gitlab.Gitlab(
                    gitlab_server_url,
                    private_token=config.get("GITLAB_ACCESS_TOKEN_MEGALINTER"),
                )
            else:
                gl = gitlab.Gitlab(
                    gitlab_server_url, job_token=config.get("CI_JOB_TOKEN")
                )
            project = gl.projects.get(gitlab_project_id)
            try:
                mr = project.mergerequests.get(gitlab_merge_request_id)
            except gitlab.GitlabGetError as e:
                gitlab_merge_request_id = config.get("CI_MERGE_REQUEST_IID", "none")
                try:
                    mr = project.mergerequests.get(gitlab_merge_request_id)
                except gitlab.GitlabGetError as e:
                    logging.warning(
                        "[Gitlab Comment Reporter] No merge request has been found with "
                        f"id {gitlab_merge_request_id}, so no comment has been posted\n"
                        + str(e)
                    )
                    return

            # Ignore if PR is already merged
            if mr.state == "merged":
                return

            # List comments on merge request
            existing_comment = None
            try:
                existing_comments = mr.notes.list()
            except gitlab.GitlabAuthenticationError as e:
                logging.error(
                    "[Gitlab Comment Reporter] You need to define a masked Gitlab CI/CD variable "
                    "GITLAB_ACCESS_TOKEN_MEGALINTER containing a personal token with api access\n"
                    + str(e)
                )
                return
            except Exception as e:
                logging.error(
                    "[Gitlab Comment Reporter] You need to define a masked Gitlab CI/CD variable "
                    "MEGALINTER_ACCESS_TOKEN containing a personal token with scope 'api'\n"
                    + str(e)
                )
                return

            # Check if there is already a MegaLinter comment
            for comment in existing_comments:
                if (
                    "See errors details in [**artifact MegaLinter reports** on"
                    in comment.body
                ):
                    existing_comment = comment

            # Process comment
            try:
                # Edit if there is already a Mega-Linter comment
                if existing_comment is not None:
                    existing_comment.body = p_r_msg
                    existing_comment.save()
                # Or create a new PR comment
                else:
                    mr.notes.create({"body": p_r_msg})
                logging.debug(f"Posted Gitlab comment: {p_r_msg}")
                logging.info(
                    f"[Gitlab Comment Reporter] Posted summary as comment on {gitlab_repo} #MR{mr.id}"
                )
            except gitlab.GitlabError as e:
                logging.warning(
                    f"[GitHub Comment Reporter] Unable to post merge request comment: {str(e)}"
                )
            except Exception as e:
                logging.warning(
                    f"[Gitlab Comment Reporter] Error while posting comment: \n{str(e)}"
                )
        # Not in gitlab context
        else:
            logging.debug(
                "[Gitlab Comment Reporter] No Gitlab Token found, so skipped post of MR comment"
            )
