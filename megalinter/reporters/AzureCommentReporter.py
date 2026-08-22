#!/usr/bin/env python3
"""
Azure Comment reporter
Post a comment on Azure Pipelines Pull Requests
"""

import logging

import requests
from megalinter import Reporter, config
from megalinter.ci_providers import CiProviderAzurePipelines
from megalinter.utils_reporter import build_markdown_summary


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

    def get_comment_marker(self):
        """Generate the comment marker

        This marker is used to find the same comment again so it can be updated.
        """
        system_team_project = config.get(
            self.master.request_id, "SYSTEM_TEAMPROJECT", ""
        )
        build_repository_id = config.get(
            self.master.request_id, "BUILD_REPOSITORY_ID", ""
        )
        system_definition_id = config.get(
            self.master.request_id, "SYSTEM_DEFINITIONID", ""
        )
        multirun_key = config.get(self.master.request_id, "MEGALINTER_MULTIRUN_KEY", "")

        system_team_project = system_team_project and f"project={system_team_project!r}"
        build_repository_id = build_repository_id and f"repo_id={build_repository_id!r}"
        system_definition_id = (
            system_definition_id and f"pipeline_id={system_definition_id!r}"
        )
        multirun_key = multirun_key and f"key={multirun_key!r}"

        identifier = " ".join(
            [
                "azure-comment-reporter",
                *filter(
                    None,
                    (
                        system_team_project,
                        build_repository_id,
                        system_definition_id,
                        multirun_key,
                    ),
                ),
            ]
        )
        return f"<!-- megalinter: {identifier} -->"

    def produce_report(self):
        # The reporter instantiates the Azure provider directly instead of
        # asking the factory: under Jenkins the platform is Jenkins, which maps
        # its variables onto the Azure ones this reporter needs
        ci_provider = CiProviderAzurePipelines(self.master.request_id)
        # Post thread on Azure pull request
        if ci_provider.get_auth_token() is not None:
            pull_request_id = ci_provider.get_pr_number()
            if pull_request_id is None:
                logging.info(
                    "[Azure Comment Reporter] Missing value SYSTEM_PULLREQUEST_PULLREQUESTID\n"
                    + "You may need to configure a build validation policy to make it appear.\n"
                    + "See https://docs.microsoft.com/en-US/azure/devops/repos/git/"
                    + "branch-policies?view=azure-devops&tabs=browser#build-validation"
                )
                return

            # Build thread data
            if (
                config.get(
                    self.master.request_id,
                    "AZURE_COMMENT_REPORTER_LINKS_TYPE",
                    "artifacts",
                )
                == "artifacts"
            ):
                artifacts_url = ci_provider.get_artifacts_url()
            else:
                artifacts_url = ci_provider.get_job_url()

            # add comment marker, with extra newlines in between.
            marker = self.get_comment_marker()
            p_r_msg = "\n".join(
                [build_markdown_summary(self, artifacts_url), "", marker, ""]
            )

            comment_status = 2 if self.master.return_code == 0 else 1
            thread_data = {
                "comments": [
                    {"parentCommentId": 0, "content": p_r_msg, "commentType": 1}
                ],
                "status": comment_status,
            }

            headers = ci_provider.get_api_headers()
            repository_id = ci_provider.get_repository_id()
            threads_path = (
                f"/repositories/{repository_id}/pullRequests/{pull_request_id}/threads"
            )

            # Look for existing MegaLinter thread
            get_threads_response = requests.get(
                ci_provider.build_git_api_url(threads_path),
                headers=headers,
            )

            if get_threads_response.status_code != 200:
                get_threads_response.raise_for_status()

            threads = get_threads_response.json()

            existing_threads = threads["value"]
            existing_thread_id = None
            existing_thread_comment_id = None
            for existing_thread in existing_threads:
                for comment in existing_thread["comments"] or []:
                    if marker in (comment.get("content") or ""):
                        existing_thread_comment_id = existing_thread["comments"][0][
                            "id"
                        ]
                        existing_thread_id = existing_thread["id"]
                        break
                if existing_thread_id is not None:
                    break

            # Remove previous MegaLinter thread if existing
            if existing_thread_id is not None:
                deleted_comment_response = requests.delete(
                    ci_provider.build_git_api_url(
                        f"{threads_path}/{existing_thread_id}"
                        f"/comments/{existing_thread_comment_id}"
                    ),
                    headers=headers,
                )

                if deleted_comment_response.status_code != 200:
                    deleted_comment_response.raise_for_status()

                existing_thread_data = {
                    "status": 4,  # = Closed
                }

                update_pull_request_thread_response = requests.patch(
                    ci_provider.build_git_api_url(
                        f"{threads_path}/{existing_thread_id}"
                    ),
                    headers=headers,
                    json=existing_thread_data,
                )

                if update_pull_request_thread_response.status_code != 200:
                    update_pull_request_thread_response.raise_for_status()

            # Post thread
            create_pull_request_thread_response = requests.post(
                ci_provider.build_git_api_url(threads_path),
                headers=headers,
                json=thread_data,
            )

            if create_pull_request_thread_response.status_code != 200:
                create_pull_request_thread_response.raise_for_status()

            created_thread = create_pull_request_thread_response.json()

            if created_thread.get("id") is not None and created_thread["id"] > 0:
                logging.debug(f"Posted Azure Pipelines comment: {thread_data}")
                logging.info(
                    "[Azure Comment Reporter] Posted summary as comment on "
                    + f"{ci_provider.get_team_project()} #PR{pull_request_id}"
                )
            else:
                logging.warning(
                    "[Azure Comment Reporter] Error while posting comment:"
                    + str(created_thread)
                    + "\n"
                    + "See https://megalinter.io/latest/reporters/AzureCommentReporter/"
                )
        # Not in Azure context
        else:
            logging.debug(
                "[Azure Comment Reporter] No Azure Token found, so skipped post of PR comment"
            )
