#!/usr/bin/env python3
"""
Bitbucket Comment reporter
Post a comment on Bitbucket Merge Requests
"""

import logging

import requests
from megalinter import Reporter, config
from megalinter.ci_providers import CiProviderBitbucket
from megalinter.utils_reporter import build_markdown_summary


class BitbucketCommentReporter(Reporter):
    name = "BITBUCKET_COMMENT"
    scope = "mega-linter"
    # Bitbucket Cloud markdown strips raw HTML; render sections as ### headings instead.
    markdown_supports_html_details = False

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

    def get_comment_marker(self):
        """Generate the comment marker

        This marker is used to find the same comment again so it can be updated.
        """
        repo_full_name = config.get(
            self.master.request_id, "BITBUCKET_REPO_FULL_NAME", ""
        )
        multirun_key = config.get(self.master.request_id, "MEGALINTER_MULTIRUN_KEY", "")

        repo_full_name = repo_full_name and f"repo={repo_full_name!r}"
        multirun_key = multirun_key and f"key={multirun_key!r}"
        identifier = " ".join(
            [
                "bitbucket-comment-reporter",
                *filter(None, (repo_full_name, multirun_key)),
            ]
        )
        return f"<!-- megalinter: {identifier} -->"

    def produce_report(self):
        # Post comment on Bitbucket pull request

        # The reporter instantiates the Bitbucket provider directly instead of
        # asking the factory: under Jenkins the platform is Jenkins, which maps
        # its variables onto the Bitbucket ones this reporter needs
        ci_provider = CiProviderBitbucket(self.master.request_id)
        bitbucket_repo_fullname = ci_provider.get_repo_slug()
        bitbucket_pr_id = ci_provider.get_pr_number()
        pipeline_step_run_url = ci_provider.get_job_url()

        if (
            ci_provider.get_auth_token() is None
            or bitbucket_repo_fullname is None
            or bitbucket_pr_id is None
            or pipeline_step_run_url == ""
            or config.get(self.master.request_id, "BITBUCKET_GIT_HTTP_ORIGIN", "") == ""
            or config.get(self.master.request_id, "BITBUCKET_BUILD_NUMBER", "") == ""
        ):
            logging.info(
                "[Bitbucket Comment Reporter] Required Bitbucket CI CD variables not found, so skipped post of PR "
                "comment"
            )
            return

        # add comment marker, with extra newlines in between.
        marker = self.get_comment_marker()
        p_r_msg = "\n".join(
            [build_markdown_summary(self, pipeline_step_run_url), "", marker, ""]
        )

        bitbucket_auth_header = ci_provider.get_api_headers()

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
                if marker in comment.get("content", {}).get("raw", ""):
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
