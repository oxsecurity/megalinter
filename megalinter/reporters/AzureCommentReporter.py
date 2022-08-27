#!/usr/bin/env python3
"""
Azure Comment reporter
Post a comment on Azure Pipelines Pull Requests
"""
import logging
import os
import requests


from megalinter import Reporter, config
from megalinter.pre_post_factory import run_command
from megalinter.utils_reporter import build_markdown_summary


class GitlabCommentReporter(Reporter):
    name = "AZURE_COMMENT"
    scope = "mega-linter"

    gitlab_server_url = "https://gitlab.com"

    def manage_activation(self):
        if config.get("AZURE_COMMENT_REPORTER", "true") != "true":
            self.is_active = False
        elif (
            config.get("POST_AZURE_COMMENT", "true") == "true"
        ):  # True by default
            self.is_active = True

    def produce_report(self):
        # Post comment on GitHub pull request
        if config.get("CI_JOB_TOKEN", "") != "":
            SYSTEM_COLLECTIONURI = os.getenv('SYSTEM_COLLECTIONURI')
            SYSTEM_PULLREQUEST_PULLREQUESTID = os.getenv('SYSTEM_PULLREQUEST_PULLREQUESTID')
            SYSTEM_TEAMPROJECT = os.getenv('SYSTEM_TEAMPROJECT')
            BUILD_REPOSITORY_ID = os.getenv('BUILD_REPOSITORY_ID')
            url = f"{SYSTEM_COLLECTIONURI}{SYSTEM_TEAMPROJECT}/_apis/git/repositories/" \
                    f"{BUILD_REPOSITORY_ID}/pullRequests/{SYSTEM_PULLREQUEST_PULLREQUESTID}" \
                    "/threads?api-version=6.0"
            headers = {
                "content-type": "application/json",
                "Authorization": f"BEARER {os.getenv('SYSTEM_ACCESSTOKEN')}"
            }
            p_r_msg = build_markdown_summary(self, action_run_url)

            data = {
                "comments": [
                    {
                        "parentCommentId": 0,
                        "content": p_r_msg,
                        "commentType": 1
                    }
                ],
                "status": 1
            }
            r = requests.post(url=self.url, json=data, headers=self.headers)
        # Not in gitlab context
        else:
            logging.debug(
                "[Gitlab Comment Reporter] No Gitlab Token found, so skipped post of MR comment"
            )


