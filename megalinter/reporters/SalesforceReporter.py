#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging
import os
import re
import urllib

from megalinter import Reporter, config

DOCS_URL_DESCRIPTORS_ROOT = "https://nvuillam.github.io/mega-linter/descriptors"

def log_link(label, url):
    if url == "":
        return label
    else:
        return f"[{label}]({url})"


class SalesforceReporter(Reporter):
    name = "SALESFORCE"
    scope = "mega-linter"

    issues_root = "https://github.com/nvuillam/mega-linter/issues"

    def manage_activation(self):
        if config.get("SALESFORCE_REPORTER", "false") == "true":
            self.is_active = True
        else:
            self.is_active = False

    def produce_report(self):
        # Post records in target Salesforce org where OrgCheck is installed
        github_repo = config.get("GITHUB_REPOSITORY")
        github_server_url = config.get("GITHUB_SERVER_URL", self.github_server_url)
        github_api_url = config.get("GITHUB_API_URL", self.github_api_url)
        run_id = config.get("GITHUB_RUN_ID")
        if run_id is not None:
            action_run_url = (
                f"{github_server_url}/{github_repo}/actions/runs/{run_id}"
            )
        else:
            action_run_url = ""
        table_header = ["Descriptor", "Linter", "Files", "Fixed", "Errors"]
        if self.master.show_elapsed_time is True:
            table_header += ["Elapsed time"]
        reportJson = {
            'CodeQualityReport__c': {
                "GitBranch__c": git_branch,
                "JobURL__c": action_run_url,
                "Origin__c": 'Mega-Linter'
            },
            'CodeQualityReportLinter__c': []
        }
        for linter in self.master.linters:
            if linter.is_active is True:
                reportLinterJson = {}
                reportLinterJson["Status__c"] = (
                    "Success"
                    if linter.status == "success" and linter.return_code == 0
                    else "Warning"
                    if linter.status != "success" and linter.return_code == 0
                    else "Error"
                )
                reportLinterJson["Descriptor__c"] = linter.descriptor_id 
                reportLinterJson["Linter__c"] = linter.linter_name
                lang_lower = linter.descriptor_id.lower()
                linter_name_lower = linter.linter_name.lower().replace("-", "_")
                reportLinterJson["LinterDocUrl__c"] = (
                    f"{DOCS_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
                )
                reportLinterJson["FixedNumber__c"] = (
                    str(linter.number_fixed) if linter.try_fix is True else ""
                )
                reportLinterJson["LintedFilesNumber__c"] = len(linter.files)
                reportLinterJson["ErrorNumber__c"] = linter.number_errors
                if self.master.show_elapsed_time is True:
                    reportLinterJson["ElapsedTimeMs__c"] += round(linter.elapsed_time_s, 2)
                reportJson["CodeQualityReportLinter__c"] += [reportLinterJson]

        status = (
            "✅"
            if self.master.return_code == 0 and self.master.status == "success"
            else ":warning:"
            if self.master.status == "warning"
            else "❌"
        )
        status_with_href = (
            status
            + " "
            + log_link(f"**{self.master.status.upper()}**", action_run_url)
        )
        p_r_msg = (
            f"## [Mega-Linter]({self.gh_url}) status: {status_with_href}"
            + os.linesep
            + os.linesep
        )
        if action_run_url != "":
            p_r_msg += (
                "See errors details in [**artifact Mega-Linter reports** on "
                f"GitHub Action page]({action_run_url})" + os.linesep
            )
        else:
            p_r_msg += "See errors details in Mega-Linter reports" + os.linesep
        if self.master.validate_all_code_base is False:
            p_r_msg += (
                "_Set `VALIDATE_ALL_CODEBASE: true` in mega-linter.yml to validate "
                + "all sources, not only the diff_"
                + os.linesep
            )

 