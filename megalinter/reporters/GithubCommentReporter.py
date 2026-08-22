#!/usr/bin/env python3
"""
GitHub Comment reporter
Post a comment on Github Pull Requests
"""

import logging

import github
from megalinter import Reporter, config
from megalinter.ci_providers import CiProviderGithubActions
from megalinter.constants import ML_REPO_URL
from megalinter.utils_reporter import build_markdown_summary


class GithubCommentReporter(Reporter):
    name = "GITHUB_COMMENT"
    scope = "mega-linter"

    issues_root = ML_REPO_URL + "/issues"

    def manage_activation(self):
        if not config.exists(self.master.request_id, "GITHUB_REPOSITORY"):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "GITHUB_COMMENT_REPORTER", "true")
            != "true"
        ):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "POST_GITHUB_COMMENT", "true") == "true"
        ):  # Legacy - true by default
            self.is_active = True

    def get_comment_marker(self):
        """Generate the comment marker

        This marker is used to find the same comment again so it can be updated.

        The marker includes the workflow name and jobid if available (via the
        GITHUB_WORKFLOW and GITHUB_JOB environment variables) to avoid clashes
        between multiple Mega-Linter jobs operating on the same PR:

          <!-- megalinter: github-comment-reporter workflow='…' jobid='…' -->

        """
        workflow = config.get(self.master.request_id, "GITHUB_WORKFLOW")
        jobid = config.get(self.master.request_id, "GITHUB_JOB")
        multirun_key = config.get(self.master.request_id, "MEGALINTER_MULTIRUN_KEY")

        workflow = workflow and f"workflow={workflow!r}"
        jobid = jobid and f"jobid={jobid!r}"
        multirun_key = multirun_key and f"key={multirun_key!r}"

        identifier = " ".join(
            ["github-comment-reporter", *filter(None, (workflow, jobid, multirun_key))]
        )
        return f"<!-- megalinter: {identifier} -->"

    def produce_report(self):
        # Post comment on GitHub pull request
        # The reporter instantiates the GitHub provider directly instead of
        # asking the factory: under Jenkins the platform is Jenkins, which maps
        # its variables onto the GitHub ones this reporter needs
        ci_provider = CiProviderGithubActions(self.master.request_id)
        if ci_provider.get_auth_token() is not None:
            github_repo = ci_provider.get_repo_slug()
            github_api_url = ci_provider.get_api_url()
            sha = ci_provider.get_commit_sha()

            if config.get(self.master.request_id, "CI_ACTION_RUN_URL", "") != "":
                action_run_url = config.get(
                    self.master.request_id, "CI_ACTION_RUN_URL", ""
                )
            elif config.get(self.master.request_id, "GITHUB_RUN_ID") is not None:
                action_run_url = ci_provider.get_job_url()
            else:
                action_run_url = ""

            # add comment marker, with extra newlines in between.
            marker = self.get_comment_marker()
            p_r_msg = "\n".join(
                [build_markdown_summary(self, action_run_url), "", marker, ""]
            )

            # Post comment on pull request if found. A user-provided PAT wins,
            # so the comment is attributed to the user rather than the bot
            github_auth = (
                ci_provider.get_user_auth_token() or ci_provider.get_auth_token()
            )
            g = github.Github(base_url=github_api_url, login_or_token=github_auth)
            try:
                repo = g.get_repo(github_repo)
            except github.GithubException as e:
                logging.warning(f"Unable to connect to GitHub repository: {e}")
                return
            except Exception as e:
                logging.warning(f"Unable to connect to GitHub repository: {e}")
                return
            # Try to get PR from GITHUB_REF
            pr_list = []
            pr_id = ci_provider.get_pr_number()
            if pr_id is not None:
                logging.debug(f"Identified PR#{pr_id} from environment")
                try:
                    pr_list = [repo.get_pull(int(pr_id))]
                except Exception as e:
                    logging.warning(f"Could not fetch PR#{pr_id}: {e}")
            if pr_list is None or len(pr_list) == 0:
                # If not found with GITHUB_REF, try to find PR from commit
                try:
                    commit = repo.get_commit(sha=sha)
                    pr_list = commit.get_pulls()
                    if pr_list.totalCount == 0:
                        logging.info(
                            "[GitHub Comment Reporter] No pull request has been found, so no comment has been posted"
                        )
                        return
                except Exception as e:
                    logging.warning(
                        f"[GitHub Comment Reporter] Unable to fetch pull requests for commit {sha}: {e}"
                    )
                    return
            for pr in pr_list:
                # Ignore if PR is already merged
                if pr.is_merged():
                    continue
                # Check if there is already a comment from MegaLinter
                # start searching from the most recent comment, backwards.
                existing_comment = None
                for comment in pr.get_issue_comments().reversed:
                    if marker in comment.body:
                        existing_comment = comment
                        break
                # Process comment
                try:
                    # Edit if there is already a MegaLinter comment
                    if existing_comment is not None:
                        existing_comment.edit(p_r_msg)
                    # Or create a new PR comment
                    else:
                        pr.create_issue_comment(p_r_msg)
                    logging.debug(f"Posted Github comment: {p_r_msg}")
                    logging.info(
                        f"[GitHub Comment Reporter] Posted summary as comment on {github_repo} #PR{pr.number}"
                    )
                except github.GithubException as e:
                    logging.warning(
                        f"[GitHub Comment Reporter] Unable to post pull request comment: {str(e)}.\n"
                        "To enable this function, please add permissions in your Github Actions Workflow:\n"
                        "permissions:\n"
                        "  issues: write\n"
                        "  pull-requests: write"
                    )
                except Exception as e:
                    logging.warning(
                        f"[GitHub Comment Reporter] Error while posting comment: \n{str(e)}"
                    )
        # Not in github context, or env var POST_GITHUB_COMMENT = false
        else:
            logging.debug(
                "[GitHub Comment Reporter] No GitHub Token has been found, so skipped post of PR comment"
            )
