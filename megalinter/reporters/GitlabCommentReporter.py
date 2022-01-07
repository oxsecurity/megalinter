#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging
from megalinter.utils_reporter import build_markdown_summary
import os

import gitlab
from megalinter import Reporter, config


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
            gitlab_merge_request_id = config.get("CI_MERGE_REQUEST_ID", None)
            logging.info("NICO: merge request id: " + gitlab_merge_request_id)
            if (
                gitlab_merge_request_id is None
                and config.get("CI_OPEN_MERGE_REQUESTS", None) is not None
            ):
                gitlab_merge_request_id = (
                    config.get("CI_OPEN_MERGE_REQUESTS").split(",")[0].split("!")[1]
                )
                logging.info("NICO: merge request id: " + gitlab_merge_request_id)
            gitlab_server_url = config.get("CI_SERVER_URL", self.gitlab_server_url)
            action_run_url = config.get("CI_JOB_URL", "")
            p_r_msg = build_markdown_summary(self, action_run_url)

            # Post comment on merge request if found
            gl = gitlab.Gitlab(gitlab_server_url, job_token=os.environ["CI_JOB_TOKEN"])
            logging.info("NICO: gitlab_project_id: " + gitlab_project_id)
            logging.info("NICO: gl: " + gl)
            project = gl.projects.get(gitlab_project_id)

            mr = project.mergerequests.get(gitlab_merge_request_id)
            if mr is None:
                logging.info(
                    "[Gitlab Comment Reporter] No merge request has been found, so no comment has been posted"
                )
                return

            # Ignore if PR is already merged
            if mr.state == "merged":
                return

            # Check if there is already a comment from Mega-Linter
            existing_comment = None
            existing_comments = mr.notes.list()
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
                    existing_comment.body = p_r_msg
                    existing_comment.save()
                # Or create a new PR comment
                else:
                    mr.notes.create({"body": "note content"})
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
