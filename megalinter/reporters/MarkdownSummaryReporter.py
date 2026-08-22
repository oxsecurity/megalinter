#!/usr/bin/env python3
"""
Produce MARKDOWN_SUMMARY report
"""

import logging
import os

from megalinter import Reporter, ci_providers, config, utils
from megalinter.constants import DEFAULT_MARKDOWN_SUMMARY_REPORT_FILE_NAME
from megalinter.utils_reporter import build_markdown_summary


class MarkdownSummaryReporter(Reporter):
    name = "MARKDOWN_SUMMARY"
    scope = "mega-linter"

    def manage_activation(self):
        if not utils.can_write_report_files(self.master):
            self.is_active = False
        elif config.get(
            self.master.request_id, "MARKDOWN_SUMMARY_REPORTER", "false"
        ) == "true" or config.exists(self.master.request_id, "GITHUB_STEP_SUMMARY"):
            self.is_active = True
        else:
            self.is_active = False

    def produce_report(self):
        summary = build_markdown_summary(
            self, action_run_url="", max_total_chars=800000
        )

        # Write output file
        summary_file_name = f"{self.report_folder}{os.path.sep}" + config.get(
            self.master.request_id,
            "MARKDOWN_SUMMARY_REPORTER_FILE_NAME",
            DEFAULT_MARKDOWN_SUMMARY_REPORT_FILE_NAME,
        )
        if os.path.isfile(summary_file_name):
            # Remove from previous run
            os.remove(summary_file_name)
        with open(summary_file_name, "w", encoding="utf-8") as summary_file:
            summary_file.write(summary)
        # Publish on the CI job page when the platform supports it
        published = ci_providers.get_ci_provider(
            self.master.request_id
        ).publish_job_summary(summary)
        logging.info(
            f"[MARKDOWN_SUMMARY Reporter] Generated {self.name} report: {summary_file_name}"
        )
        if published is True:
            logging.info(
                "[MARKDOWN_SUMMARY Reporter] Also published on the CI job summary"
            )
