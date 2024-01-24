#!/usr/bin/env python3
"""
Azure Comment reporter
Post a comment on Azure Pipelines Pull Requests

Requires the following vars sent to docker run:
- SYSTEM_ACCESSTOKEN
- SYSTEM_COLLECTIONURI
- SYSTEM_PULLREQUEST_PULLREQUESTID
- SYSTEM_TEAMPROJECT
- BUILD_BUILDID
- BUILD_REPOSITORY_ID
"""
import logging
import urllib.parse

from azure.devops.connection import Connection
from azure.devops.released.git.git_client import GitClient
from megalinter import Reporter, config
from megalinter.utils_reporter import build_markdown_summary
from msrest.authentication import BasicTokenAuthentication


class AzureCommentReporter(Reporter):
    name = "AZURE_COMMENT"
    scope = "mega-linter"

    def manage_activation(self):
        if not config.exists(self.master.request_id, "SYSTEM_COLLECTIONURI"):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "AZURE_COMMENT_REPORTER", "true")
            != "true"
        ):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "POST_AZURE_COMMENT", "true") == "true"
        ):  # True by default
            self.is_active = True

    def produce_report(self):
        # Post thread on Azure pull request
        if config.get(self.master.request_id, "SYSTEM_ACCESSTOKEN", "") != "":
            # Collect variables
            SYSTEM_COLLECTIONURI = config.get(
                self.master.request_id, "SYSTEM_COLLECTIONURI"
            )
            SYSTEM_PULLREQUEST_PULLREQUESTID = config.get(
                self.master.request_id, "SYSTEM_PULLREQUEST_PULLREQUESTID", ""
            )
            if SYSTEM_PULLREQUEST_PULLREQUESTID == "":
                logging.info(
                    "[Azure Comment Reporter] Missing value SYSTEM_PULLREQUEST_PULLREQUESTID\n"
                    + "You may need to configure a build validation policy to make it appear.\n"
                    + "See https://docs.microsoft.com/en-US/azure/devops/repos/git/"
                    + "branch-policies?view=azure-devops&tabs=browser#build-validation"
                )
                return
            SYSTEM_TEAMPROJECT = urllib.parse.quote(
                config.get(self.master.request_id, "SYSTEM_TEAMPROJECT")
            )
            BUILD_REPOSITORY_ID = config.get(
                self.master.request_id, "BUILD_REPOSITORY_ID"
            )
            BUILD_BUILDID = config.get(
                self.master.request_id,
                "BUILD_BUILDID",
                config.get(self.master.request_id, "BUILD_BUILD_ID"),
            )

            # Build thread data
            AZURE_COMMENT_REPORTER_LINKS_TYPE = config.get(
                self.master.request_id, "AZURE_COMMENT_REPORTER_LINKS_TYPE", "artifacts"
            )
            if AZURE_COMMENT_REPORTER_LINKS_TYPE == "artifacts":
                artifacts_url = (
                    f"{SYSTEM_COLLECTIONURI}{SYSTEM_TEAMPROJECT}/_build/results?buildId="
                    f"{BUILD_BUILDID}&view=artifacts&pathAsName=false&type=publishedArtifacts"
                )
            else:
                artifacts_url = f"{SYSTEM_COLLECTIONURI}{SYSTEM_TEAMPROJECT}/_build/results?buildId={BUILD_BUILDID}"
            p_r_msg = build_markdown_summary(self, artifacts_url)
            comment_status = "fixed" if self.master.return_code == 0 else 1
            thread_data = {
                "comments": [
                    {"parentCommentId": 0, "content": p_r_msg, "commentType": 1}
                ],
                "status": comment_status,
            }

            # Create connection to Azure API
            access_token = config.get(self.master.request_id, "SYSTEM_ACCESSTOKEN")
            credentials = BasicTokenAuthentication({"access_token": access_token})
            connection = Connection(
                base_url=f"{SYSTEM_COLLECTIONURI}",
                creds=credentials,
            )
            git_client: GitClient = connection.clients.get_git_client()

            # Look for existing MegaLinter thread
            existing_threads = git_client.get_threads(
                BUILD_REPOSITORY_ID, SYSTEM_PULLREQUEST_PULLREQUESTID
            )
            existing_thread_id = None
            existing_thread_comment = None
            existing_thread_comment_id = None
            for existing_thread in existing_threads:
                for comment in existing_thread.comments or []:
                    if "MegaLinter is graciously provided by" in (
                        comment.content or ""
                    ):
                        existing_thread_comment = existing_thread
                        existing_thread_comment_id = existing_thread.comments[0].id
                        existing_thread_id = existing_thread.id
                        break
                if existing_thread_id is not None:
                    break

            # Remove previous MegaLinter thread if existing
            if existing_thread_id is not None:
                git_client.delete_comment(
                    BUILD_REPOSITORY_ID,
                    SYSTEM_PULLREQUEST_PULLREQUESTID,
                    existing_thread_id,
                    existing_thread_comment_id,
                )
                existing_thread_comment = git_client.get_pull_request_thread(
                    BUILD_REPOSITORY_ID,
                    SYSTEM_PULLREQUEST_PULLREQUESTID,
                    existing_thread_id,
                )
                existing_thread_comment = {
                    "id": existing_thread_comment.id,
                    "status": 4,  # = Closed
                }
                git_client.update_thread(
                    existing_thread_comment,
                    BUILD_REPOSITORY_ID,
                    SYSTEM_PULLREQUEST_PULLREQUESTID,
                    existing_thread_id,
                )

            # Post thread
            new_thread_result = git_client.create_thread(
                thread_data, BUILD_REPOSITORY_ID, SYSTEM_PULLREQUEST_PULLREQUESTID
            )
            if new_thread_result.id is not None and new_thread_result.id > 0:
                logging.debug(f"Posted Azure Pipelines comment: {thread_data}")
                logging.info(
                    "[Azure Comment Reporter] Posted summary as comment on "
                    + f"{SYSTEM_TEAMPROJECT} #PR{SYSTEM_PULLREQUEST_PULLREQUESTID}"
                )
            else:
                logging.warning(
                    "[Azure Comment Reporter] Error while posting comment:"
                    + str(new_thread_result)
                    + "\n"
                    + "See https://megalinter.io/latest/reporters/AzureCommentReporter/"
                )
        # Not in Azure context
        else:
            logging.debug(
                "[Azure Comment Reporter] No Azure Token found, so skipped post of PR comment"
            )
