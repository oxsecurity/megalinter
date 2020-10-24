#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging
import os

import github
from pytablewriter import MarkdownTableWriter

from megalinter import Reporter

BRANCH = 'master'
URL_ROOT = "https://github.com/nvuillam/mega-linter/tree/" + BRANCH
DOCS_URL_ROOT = URL_ROOT + "/docs"
DOCS_URL_DESCRIPTORS_ROOT = DOCS_URL_ROOT + "/descriptors"


class GithubCommentReporter(Reporter):
    name = 'GITHUB_COMMENT'
    scope = 'mega-linter'

    github_api_url = 'https://api.github.com'
    gh_url = 'https://github.com/nvuillam/mega-linter#readme'

    def manage_activation(self):
        if os.environ.get('POST_GITHUB_COMMENT', 'true') == 'true':
            self.is_active = True

    def produce_report(self):
        # Post comment on GitHub pull request
        if os.environ.get('GITHUB_TOKEN', '') != '':
            github_repo = os.environ['GITHUB_REPOSITORY']
            run_id = os.environ['GITHUB_RUN_ID']
            sha = os.environ.get('GITHUB_SHA')
            action_run_url = f"https://github.com/{github_repo}/actions/runs/{run_id}"
            table_header = ["Descriptor", "Linter", "Found", "Errors"]
            table_data_raw = [table_header]
            for linter in self.master.linters:
                if linter.is_active is True:
                    emoji = ':green_circle:' if linter.status == 'success' and linter.return_code == 0 \
                        else 'orange_circle' if linter.status != 'success' and linter.return_code == 0 \
                        else ':red_circle:'
                    first_col = f"{emoji} {linter.descriptor_id}"
                    lang_lower = linter.descriptor_id.lower()
                    linter_name_lower = linter.linter_name.lower().replace('-', '_')
                    linter_doc_url = f"{DOCS_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}.md"
                    linter_link = f"[{linter.linter_name}]({linter_doc_url})"
                    errors_cell = f"[**{linter.number_errors}**]({action_run_url})" if linter.number_errors > 0 \
                        else linter.number_errors
                    table_data_raw += [
                        [first_col, linter_link, len(linter.files), errors_cell]]
            # Build markdown table
            table_data_raw.pop(0)
            writer = MarkdownTableWriter(
                headers=table_header,
                value_matrix=table_data_raw
            )
            table_content = str(writer) + os.linesep if len(table_data_raw) > 1 else ""
            emoji = ':green_circle:' if self.master.return_code == 0 else ':red_circle:'
            status_with_href = f"[**{self.master.status.upper()}**]({action_run_url}) {emoji}"
            p_r_msg = f"## [Mega-Linter]({self.gh_url}) status: {status_with_href}" + os.linesep + os.linesep
            p_r_msg += table_content + os.linesep
            p_r_msg += f"See errors details in [**artifact Mega-Linter reports** on " \
                       f"GitHub Action page]({action_run_url})" + \
                       os.linesep
            if self.master.validate_all_code_base is False:
                p_r_msg += "_Set `VALIDATE_ALL_CODEBASE: true` in mega-linter.yml to validate " + \
                           "all sources, not only the diff_" + os.linesep
            logging.debug("\n" + p_r_msg)
            # Post comment on pull request if found
            github_auth = os.environ['PAT'] if os.environ.get(
                'PAT', '') != '' else os.environ['GITHUB_TOKEN']
            g = github.Github(github_auth)
            repo = g.get_repo(github_repo)
            commit = repo.get_commit(sha=sha)
            pr_list = commit.get_pulls()
            for pr in pr_list:
                if pr.is_merged():
                    continue
                try:
                    pr.create_issue_comment(p_r_msg)
                    logging.debug(f'Posted Github comment: {p_r_msg}')
                    logging.info(f'Posted summary as comment on {github_repo} #PR{pr.number}')
                except github.GithubException as e:
                    logging.warning(f"Unable to post pull request comment: {str(e)}.\n"
                                    "To enable this function, please :\n"
                                    "1. Create a Personal Access Token (https://docs.github.com/en/free-pro-team@"
                                    "latest/github/authenticating-to-github/creating-a-personal-access-token)\n"
                                    "2. Create a secret named PAT with its value on your repository (https://docs."
                                    "github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets#"
                                    "creating-encrypted-secrets-for-a-repository)"
                                    "3. Define PAT={{secrets.PAT}} in your GitHub action environment variables")
        # Not in github contest, or env var POST_GITHUB_COMMENT = false
        else:
            logging.debug("Skipped post of pull request comment")
