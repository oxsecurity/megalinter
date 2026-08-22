#!/usr/bin/env python3
"""
Gitlab Comment reporter
Post a comment on Gitlab Merge Requests
"""

import logging

import gitlab
from megalinter import Reporter, config
from megalinter.ci_providers import CiProviderGitlab
from megalinter.pre_post_factory import run_command
from megalinter.utils_reporter import build_markdown_summary


class GitlabCommentReporter(Reporter):
    name = "GITLAB_COMMENT"
    scope = "mega-linter"

    def manage_activation(self):
        if not config.exists(
            self.master.request_id, "CI_JOB_TOKEN"
        ) and not config.exists(
            self.master.request_id, "GITLAB_ACCESS_TOKEN_MEGALINTER"
        ):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "GITLAB_COMMENT_REPORTER", "true")
            != "true"
        ):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "POST_GITLAB_COMMENT", "true") == "true"
        ):  # Legacy - true by default
            self.is_active = True

    def get_comment_marker(self):
        """Generate the comment marker

        This marker is used to find the same comment again so it can be updated.
        """
        pipeline_source = config.get(self.master.request_id, "CI_PIPELINE_SOURCE")
        job_name = config.get(self.master.request_id, "CI_JOB_NAME")
        multirun_key = config.get(self.master.request_id, "MEGALINTER_MULTIRUN_KEY")

        pipeline_source = pipeline_source and f"pipeline_source={pipeline_source!r}"
        job_name = job_name and f"job_name={job_name!r}"
        multirun_key = multirun_key and f"key={multirun_key!r}"

        identifier = " ".join(
            [
                "gitlab-comment-reporter",
                *filter(None, (pipeline_source, job_name, multirun_key)),
            ]
        )
        return f"<!-- megalinter: {identifier} -->"

    def produce_report(self):
        # Post comment on Gitlab pull request
        # The reporter instantiates the GitLab provider directly instead of
        # asking the factory: under Jenkins the platform is Jenkins, which maps
        # its variables onto the GitLab ones this reporter needs
        ci_provider = CiProviderGitlab(self.master.request_id)
        if (
            ci_provider.get_auth_token() is not None
            or ci_provider.get_user_auth_token() is not None
        ):
            gitlab_repo = config.get(self.master.request_id, "CI_PROJECT_NAME")
            gitlab_project_id = ci_provider.get_project_id()
            gitlab_merge_request_id = ci_provider.get_pr_number()
            if gitlab_merge_request_id is None:
                logging.info(
                    "[Gitlab Comment Reporter] No merge request has been found, so no comment has been posted"
                )
                return

            gitlab_server_url = ci_provider.get_server_url()
            action_run_url = ci_provider.get_job_url()

            # add comment marker, with extra newlines in between.
            marker = self.get_comment_marker()
            p_r_msg = "\n".join(
                [build_markdown_summary(self, action_run_url), "", marker, ""]
            )

            # Build gitlab options
            gitlab_options = ci_provider.get_api_auth_options()
            # Certificate management
            gitlab_certificate_path = config.get(
                self.master.request_id, "GITLAB_CERTIFICATE_PATH", ""
            )
            if (
                config.get(self.master.request_id, "GITLAB_CUSTOM_CERTIFICATE", "")
                != ""
            ):
                # Certificate value defined in an ENV variable
                cert_value = config.get(
                    self.master.request_id, "GITLAB_CUSTOM_CERTIFICATE"
                )
                gitlab_certificate_path = "/etc/ssl/certs/gitlab-cert.crt"
                with open(gitlab_certificate_path, "w", encoding="utf-8") as cert_file:
                    cert_file.write(cert_value)
                    logging.debug(
                        f"Updated {gitlab_certificate_path} with certificate value {cert_value}"
                    )
            if gitlab_certificate_path != "":
                # Update certificates and set cert path in gitlab options
                run_command(
                    {
                        "cwd": "root",
                        "command": "update-ca-certificates",
                        "secured_env": False,
                    },
                    "GitlabCommentReporter",
                    self.master,
                )
                gitlab_options["ssl_verify"] = gitlab_certificate_path
            # Create gitlab connection
            logging.debug(
                f"[GitlabCommentReporter] Logging to {gitlab_server_url} with {str(gitlab_options)}"
            )
            gl = gitlab.Gitlab(gitlab_server_url, **gitlab_options)
            # Get gitlab project
            try:
                project = gl.projects.get(gitlab_project_id)
            except gitlab.GitlabGetError as e:
                logging.warning(
                    "[Gitlab Comment Reporter] No project has been found with "
                    f"id {gitlab_project_id}, so no comment has been posted\n"
                )
                self.display_auth_error(e)
                return
            except Exception as e:
                self.display_auth_error(e)
                return

            # Get merge request
            try:
                mr = project.mergerequests.get(gitlab_merge_request_id)
            except gitlab.GitlabGetError:
                gitlab_merge_request_id = ci_provider.get_pr_number_fallback()
                try:
                    mr = project.mergerequests.get(gitlab_merge_request_id)
                except gitlab.GitlabGetError as e:
                    logging.warning(
                        "[Gitlab Comment Reporter] No merge request has been found with "
                        f"id {gitlab_merge_request_id}, so no comment has been posted\n"
                    )
                    self.display_auth_error(e)
                    return
                except Exception as e:
                    self.display_auth_error(e)
                    return

            # Ignore if PR is already merged
            if mr.state == "merged":
                return

            # List comments on merge request
            existing_comment = None
            if (
                config.get(
                    self.master.request_id,
                    "GITLAB_COMMENT_REPORTER_OVERWRITE_COMMENT",
                    "true",
                )
                == "true"
            ):
                try:
                    existing_comments = mr.notes.list(get_all=True)
                except gitlab.GitlabAuthenticationError as e:
                    self.display_auth_error(e)
                    return
                except Exception as e:
                    self.display_auth_error(e)
                    return
                # Check if there is already a MegaLinter comment
                for comment in existing_comments:
                    if marker in comment.body:
                        existing_comment = comment
                        break

            # Process comment
            try:
                # Edit if there is already a Mega-Linter comment
                if existing_comment is not None:
                    existing_comment.body = p_r_msg
                    existing_comment.save()
                    logging.debug(f"Updated Gitlab comment: {p_r_msg}")
                    logging.info(
                        f"[Gitlab Comment Reporter] Updated existing comment summary on {gitlab_repo} #MR{mr.id}"
                    )
                # Or create a new PR comment
                else:
                    mr.notes.create({"body": p_r_msg})
                    logging.debug(f"Posted Gitlab comment: {p_r_msg}")
                    logging.info(
                        f"[Gitlab Comment Reporter] Posted summary as comment on {gitlab_repo} #MR{mr.id}"
                    )
            except gitlab.GitlabError as e:
                logging.warning(
                    "[Gitlab Comment Reporter] Unable to post merge request comment"
                )
                self.display_auth_error(e)
            except Exception as e:
                logging.warning("[Gitlab Comment Reporter] Error while posting comment")
                self.display_auth_error(e)
        # Not in gitlab context
        else:
            logging.debug(
                "[Gitlab Comment Reporter] No Gitlab Token found "
                "(CI_JOB_TOKEN or GITLAB_ACCESS_TOKEN_MEGALINTER), "
                "so skipped post of MR comment"
            )

    def display_auth_error(self, e):
        logging.error(
            "[Gitlab Comment Reporter] You may need to define a masked Gitlab CI/CD variable "
            "GITLAB_ACCESS_TOKEN_MEGALINTER containing a personal token with scope 'api'\n"
            "(if already defined, your token is probably invalid)\n"
            "If you are using local certificate, you also may need to define variables "
            "GITLAB_CUSTOM_CERTIFICATE or GITLAB_CERTIFICATE_PATH" + str(e)
        )
