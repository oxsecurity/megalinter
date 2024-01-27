#!/usr/bin/env python3
"""
Bitbucket Comment reporter
Post a comment on Bitbucket Merge Requests
"""
import logging
import urllib.parse

import requests
from megalinter import Reporter, config
from megalinter.utils_reporter import build_markdown_summary


class BitbucketCommentReporter(Reporter):
    name = "BITBUCKET_COMMENT"
    scope = "mega-linter"

    BITBUCKET_API = "https://api.bitbucket.org/2.0"

    def manage_activation(self):
        if not config.exists(self.master.request_id, "BITBUCKET_REPO_FULL_NAME"):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "BITBUCKET_COMMENT_REPORTER", "true")
            == "true"
        ):
            self.is_active = True
        else:
            self.is_active = False

    def produce_report(self):
        # Post comment on Bitbucket pull request

        BITBUCKET_REPO_ACCESS_TOKEN = config.get(
            self.master.request_id, "BITBUCKET_REPO_ACCESS_TOKEN", ""
        )
        bitbucket_repo_fullname = config.get(
            self.master.request_id, "BITBUCKET_REPO_FULL_NAME", ""
        )
        bitbucket_project_url = config.get(
            self.master.request_id, "BITBUCKET_GIT_HTTP_ORIGIN", ""
        )
        bitbucket_pipeline_job_number = config.get(
            self.master.request_id, "BITBUCKET_BUILD_NUMBER", ""
        )
        bitbucket_pr_id = config.get(self.master.request_id, "BITBUCKET_PR_ID", "")
        pipeline_step_run_uuid = config.get(
            self.master.request_id, "BITBUCKET_STEP_UUID", ""
        )

        if (
            BITBUCKET_REPO_ACCESS_TOKEN == ""
            or bitbucket_repo_fullname == ""
            or bitbucket_project_url == ""
            or bitbucket_pipeline_job_number == ""
            or bitbucket_pr_id == ""
            or pipeline_step_run_uuid == ""
        ):
            logging.info(
                "[Bitbucket Comment Reporter] Required Bitbucket CI CD variables not found, so skipped post of PR "
                "comment"
            )
            return

        pipeline_step_run_uuid = urllib.parse.quote(pipeline_step_run_uuid)
        pipeline_step_run_url = (
            f"{bitbucket_project_url}/pipelines/results/"
            f"{bitbucket_pipeline_job_number}/steps/{pipeline_step_run_uuid}"
        )

        p_r_msg = build_markdown_summary(self, pipeline_step_run_url)
        bitbucket_auth_header = {
            "Authorization": f"Bearer {BITBUCKET_REPO_ACCESS_TOKEN}"
        }

        # To-Do: Ignore if PR is already merged
        try:
            pr = requests.get(
                f"{self.BITBUCKET_API}/repositories/{bitbucket_repo_fullname}/pullrequests/{bitbucket_pr_id}",
                headers=bitbucket_auth_header,
            )
            if pr.status_code != 200:
                pr.raise_for_status()
            pr_state = pr.json().get("state", "")

            if pr_state.lower() != "open":
                logging.info(
                    "[Bitbucket Comment Reporter] PR is not in OPEN state, skipped posting comment"
                )
                return
        except Exception as e:
            logging.warning("[Bitbucket Comment Reporter] Unable to get PR details")
            self.display_auth_error(e)
            return

        # List comments on pull request
        comment_id = None
        if (
            config.get(
                self.master.request_id,
                "BITBUCKET_COMMENT_REPORTER_OVERWRITE_COMMENT",
                "true",
            )
            == "true"
        ):
            try:
                comments = requests.get(
                    f"{self.BITBUCKET_API}/repositories/{bitbucket_repo_fullname}/"
                    f"pullrequests/{bitbucket_pr_id}/comments?pagelen=100",
                    headers=bitbucket_auth_header,
                )
                if comments.status_code != 200:
                    pr.raise_for_status()
                existing_comments = comments.json().get("values", [])
            except Exception as e:
                logging.warning(
                    "[Bitbucket Comment Reporter] Unable to fetch existing comments on PR"
                    + str(e)
                )
                return
            # Check if there is already a MegaLinter comment
            for comment in existing_comments:
                if "MegaLinter is graciously provided by" in comment.get(
                    "content", {}
                ).get("raw", ""):
                    comment_id = comment.get("id", None)
                    break

        # Process comment
        try:
            data = {"content": {"raw": p_r_msg}}
            if comment_id is not None:
                # Existing comment
                logging.debug(f"Updated Bitbucket comment: {p_r_msg}")
                logging.info(
                    f"[Bitbucket Comment Reporter] Updated existing comment summary "
                    f"on {bitbucket_repo_fullname} #PR {bitbucket_pr_id}"
                )
                requests.put(
                    f"{self.BITBUCKET_API}/repositories/{bitbucket_repo_fullname}/pullrequests/"
                    f"{bitbucket_pr_id}/comments/{comment_id}",
                    headers=bitbucket_auth_header,
                    json=data,
                )
            else:
                # New comment
                requests.post(
                    f"{self.BITBUCKET_API}/repositories/{bitbucket_repo_fullname}/pullrequests/"
                    f"{bitbucket_pr_id}/comments",
                    headers=bitbucket_auth_header,
                    json=data,
                )
                logging.info(
                    f"[Bitbucket Comment Reporter] PR comment summary added on {bitbucket_repo_fullname} "
                    f"#PR {bitbucket_pr_id}"
                )

        except Exception as e:
            logging.warning("[Bitbucket Comment Reporter] Error while posting comment")
            self.display_auth_error(e)

    def display_auth_error(self, e):
        logging.error(
            "[Bitbucket Comment Reporter] You may need to define a masked "
            "Bitbucket CI/CD variable BITBUCKET_REPO_ACCESS_TOKEN containing "
            "a access token with scope 'Pull-requests: write' "
            "(if already defined, your access token is probably invalid): " + str(e)
        )
