#!/usr/bin/env python3
"""
Produce MARKDOWN_SUMMARY report
"""
import logging
import os

from megalinter import Reporter, config, utils
from megalinter.constants import DEFAULT_MARKDOWN_SUMMARY_REPORT_FILE_NAME
from megalinter.utils_reporter import build_markdown_summary


class MarkdownSummaryReporter(Reporter):
    name = "MARKDOWN_SUMMARY"
    scope = "mega-linter"

    def manage_activation(self):
        if not utils.can_write_report_files(self.master):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "MARKDOWN_SUMMARY_REPORTER", "false")
            == "true"
        ):
            self.is_active = True
        else:
            self.is_active = False

    def produce_report(self):
        summary = build_markdown_summary(self)

        # Write output file
        summary_file_name = f"{self.report_folder}{os.path.sep}" + config.get(
            self.master.request_id,
            "MARKDOWN_SUMMARY_REPORTER_FILE_NAME",
            DEFAULT_MARKDOWN_SUMMARY_REPORT_FILE_NAME,
        )
        if os.path.isfile(summary_file_name):
            # Remove from previous run
            os.remove(summary_file_name)
        with open(summary_file_name, "w", encoding="utf-8") as sarif_file:
            sarif_file.write(summary)
        logging.info(
            f"[MARKDOWN_SUMMARY Reporter] Generated {self.name} report: {summary_file_name}"
        )
