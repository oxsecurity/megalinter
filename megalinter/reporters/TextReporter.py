#!/usr/bin/env python3
"""
Text reporter
"""
import logging
import os

from megalinter import Reporter


class TextReporter(Reporter):
    name = "TEXT"
    report_type = "detailed"
    scope = "linter"

    def __init__(self, params=None):
        # report_type is simple by default
        self.report_type = "simple"
        super().__init__(params)

    def manage_activation(self):
        output_format = os.environ.get("OUTPUT_FORMAT", "text")
        if output_format.startswith("text"):
            self.is_active = True
            if os.environ.get("OUTPUT_DETAIL", "") == "detailed":
                self.report_type = "detailed"

    def add_report_item(self, file, status_code, stdout, index, fixed=False):
        status = "[SUCCESS]" if status_code == 0 else "[ERROR]"
        if file is not None:
            file_text_lines = [f"{status} {file}"]
        else:
            file_text_lines = [f"{status} {self.master.workspace}"]
        if fixed is True:
            file_text_lines[0] = file_text_lines[0] + " - FIXED"
        if self.report_type == "detailed" or status_code != 0:
            std_out_text = stdout.rstrip(f" {os.linesep}") + os.linesep
            std_out_text = "\n    ".join(std_out_text.split(os.linesep))
            detailed_lines = ["    " + std_out_text, ""]
            file_text_lines += detailed_lines
        self.report_items += file_text_lines

    def produce_report(self):
        # Doc URL
        lang_lower = self.master.descriptor_id.lower()
        linter_name_lower = self.master.linter_name.lower().replace("-", "_")
        doc_name = f"{lang_lower}_{linter_name_lower}"
        doc_url = f"https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/{doc_name}.md"
        # Finalize lines
        text_report_lines = [
            f"Results of {self.master.linter_name} linter (version {self.master.get_linter_version()})",
            f"See documentation on {doc_url}",
            "-----------------------------------------------",
            "",
        ]
        text_report_lines += self.report_items
        text_report_lines += self.master.complete_text_reporter_report(self)
        text_file_name = (
            f"{self.report_folder}{os.path.sep}"
            f"{self.master.status.upper()}-mega-linter-{self.master.name}.log"
        )
        if not os.path.isdir(os.path.dirname(text_file_name)):
            os.makedirs(os.path.dirname(text_file_name))
        with open(text_file_name, "w", encoding="utf-8") as text_file:
            text_file_content = "\n".join(text_report_lines) + "\n"
            text_file.write(text_file_content)
            logging.debug(f"Generated {self.name} report: {text_file_name}")
