#!/usr/bin/env python3
"""
Azure Comment reporter
Post a comment on Azure Pipelines Pull Requests

Requires the following vars sent to docker run:
- SYSTEM_ACCESSTOKEN
- SYSTEM_COLLECTIONURI
- SYSTEM_PULLREQUEST_PULLREQUESTID
- SYSTEM_TEAMPROJECT
- BUILD_BUILD_ID
- BUILD_REPOSITORY_ID
"""
import logging

import requests
from megalinter import Reporter, config
from megalinter.utils_reporter import build_markdown_summary


class AzureCommentReporter(Reporter):
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
                "SYSTEM_PULLREQUEST_PULLREQUESTID", ""
            )
            if SYSTEM_PULLREQUEST_PULLREQUESTID == "":
                logging.warning(
                    "[Azure Comment Reporter] Missing value SYSTEM_PULLREQUEST_PULLREQUESTID\n"
                    + "You may need to configure a build validation policy to make it appear.\n"
                    + "See https://docs.microsoft.com/en-US/azure/devops/repos/git/"
                    + "branch-policies?view=azure-devops&tabs=browser#build-validation"
                )
            SYSTEM_TEAMPROJECT = config.get("SYSTEM_TEAMPROJECT")
            BUILD_REPOSITORY_ID = config.get("BUILD_REPOSITORY_ID")
            BUILD_BUILD_ID = config.get("BUILD_BUILD_ID")
            artifacts_url = (
                f"{SYSTEM_COLLECTIONURI}{SYSTEM_TEAMPROJECT}/_build/results?buildId="
                f"{BUILD_BUILD_ID}&view=artifacts&pathAsName=false&type=publishedArtifacts"
            )
            url = (
                f"{SYSTEM_COLLECTIONURI}{SYSTEM_TEAMPROJECT}/_apis/git/repositories/"
                f"{BUILD_REPOSITORY_ID}/pullRequests/{SYSTEM_PULLREQUEST_PULLREQUESTID}"
                "/threads?api-version=6.0"
            )
            headers = {
                "content-type": "application/json",
                "Authorization": f"BEARER {config.get('SYSTEM_ACCESSTOKEN')}",
            }
            p_r_msg = build_markdown_summary(self, artifacts_url)
            comment_status = "fixed" if self.master.return_code == 0 else 1
            data = {
                "comments": [
                    {"parentCommentId": 0, "content": p_r_msg, "commentType": 1}
                ],
                "status": comment_status,
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
                    "[Azure Comment Reporter] Error while posting comment:"
                    + r.reason
                    + "\n"
                    + "See https://oxsecurity.github.io/megalinter/latest/reporters/AzureCommentReporter/"
                )
        # Not in Azure context
        else:
            logging.debug(
                "[Azure Comment Reporter] No Azure Token found, so skipped post of PR comment"
            )
