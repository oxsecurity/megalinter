#!/usr/bin/env python3
"""
Azure Comment reporter
Post a comment on Azure Pipelines Pull Requests

Requires the following vars sent to docker run:
- SYSTEM_ACCESSTOKEN
- SYSTEM_COLLECTIONURI
- SYSTEM_PULLREQUEST_PULLREQUESTID
- SYSTEM_TEAMPROJECT
- BUILD_REPOSITORY_ID
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

    def manage_activation(self):
        if config.get("AZURE_COMMENT_REPORTER", "true") != "true":
            self.is_active = False
        elif config.get("POST_AZURE_COMMENT", "true") == "true":  # True by default
            self.is_active = True

    def produce_report(self):
        # Post comment on GitHub pull request
        if config.get("SYSTEM_ACCESSTOKEN", "") != "":
            SYSTEM_COLLECTIONURI = config.get("SYSTEM_COLLECTIONURI")
            SYSTEM_PULLREQUEST_PULLREQUESTID = config.get(
                "SYSTEM_PULLREQUEST_PULLREQUESTID"
            )
            SYSTEM_TEAMPROJECT = config.get("SYSTEM_TEAMPROJECT")
            BUILD_REPOSITORY_ID = config.get("BUILD_REPOSITORY_ID")
            url = (
                f"{SYSTEM_COLLECTIONURI}{SYSTEM_TEAMPROJECT}/_apis/git/repositories/"
                f"{BUILD_REPOSITORY_ID}/pullRequests/{SYSTEM_PULLREQUEST_PULLREQUESTID}"
                "/threads?api-version=6.0"
            )
            headers = {
                "content-type": "application/json",
                "Authorization": f"BEARER {config.get('SYSTEM_ACCESSTOKEN')}",
            }
            p_r_msg = build_markdown_summary(self, url)

            data = {
                "comments": [
                    {"parentCommentId": 0, "content": p_r_msg, "commentType": 1}
                ],
                "status": 1,
            }
            r = requests.post(url=url, json=data, headers=headers)
            if r.status_code == 200:
                logging.debug(f"Posted Azure Pipelines comment: {p_r_msg}")
                logging.info(
                    "[Azure Comment Reporter] Posted summary as comment on "
                    + f"{SYSTEM_TEAMPROJECT} #PR{SYSTEM_PULLREQUEST_PULLREQUESTID}"
                )
            else:
                logging.warning(
                    "[Azure Comment Reporter] Error while posting comment\n" + r.reason
                )
        # Not in Azure context
        else:
            logging.debug(
                "[Azure Comment Reporter] No Azure Token found, so skipped post of PR comment"
            )
