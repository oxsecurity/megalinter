#!/usr/bin/env python3
"""
Text reporter
"""
import logging
import os

from megalinter import Reporter, config, utils
from megalinter.constants import ML_DOC_URL_DESCRIPTORS_ROOT


class TextReporter(Reporter):
    name = "TEXT"
    report_type = "detailed"
    scope = "linter"

    def __init__(self, params=None):
        # report_type is simple by default
        self.report_type = "simple"
        self.processing_order = -5
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "OUTPUT_DETAIL", "") == "detailed":
            self.report_type = "detailed"
        output_format = config.get(self.master.request_id, "OUTPUT_FORMAT", "")
        if not utils.can_write_report_files(self.master):
            self.is_active = False
        elif output_format.startswith("text"):
            # Super-Linter legacy variable
            self.is_active = True
        # MegaLinter vars (true by default)
        elif config.get(self.master.request_id, "TEXT_REPORTER", "true") != "true":
            self.is_active = False
        else:
            self.is_active = True

    def produce_report(self):
        # Doc URL
        if self.master.is_plugin is True:
            doc_url = (
                self.master.linter_url
                or self.master.linter_repo
                or "[linter_url should be defined on descriptor]"
            )
        else:
            lang_lower = self.master.descriptor_id.lower()
            linter_name_lower = self.master.linter_name.lower().replace("-", "_")
            doc_name = f"{lang_lower}_{linter_name_lower}"
            doc_url = f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{doc_name}/"
        # Header lines
        text_report_lines = [
            f"Results of {self.master.linter_name} linter (version {self.master.get_linter_version()})",
            f"See documentation on {doc_url}",
            "-----------------------------------------------",
            "",
        ]
        # Files lines
        if self.master.cli_lint_mode == "file":
            for file_result in self.master.files_lint_results:
                status = (
                    "✅ [SUCCESS]" if file_result["status_code"] == 0 else "❌ [ERROR]"
                )
                file_text_lines = []
                if file_result["file"] is not None:
                    file_nm = utils.normalize_log_string(file_result["file"])
                    file_text_lines = [f"{status} {file_nm}"]
                if file_result["fixed"] is True:
                    file_text_lines[0] = file_text_lines[0] + " - FIXED"
                if self.report_type == "detailed" or file_result["status_code"] != 0:
                    std_out_text = (
                        file_result["stdout"].rstrip(f" {os.linesep}") + os.linesep
                    )
                    std_out_text = "\n    ".join(std_out_text.splitlines())
                    std_out_text = utils.normalize_log_string(std_out_text)
                    detailed_lines = ["    " + std_out_text, ""]
                    file_text_lines += detailed_lines
                text_report_lines += file_text_lines
        # Bulk output as linter has run all project or files in one call
        elif self.master.cli_lint_mode in ["project", "list_of_files"]:
            workspace_nm = utils.normalize_log_string(self.master.workspace)
            status = "✅ [SUCCESS]" if self.master.status == "success" else "❌ [ERROR]"
            text_report_lines += [f"{status} for workspace {workspace_nm}"]
            if self.report_type == "detailed" or self.master.status != "success":
                stdout = utils.normalize_log_string(
                    self.master.stdout_human
                    if self.master.stdout_human is not None
                    else self.master.stdout
                )
                text_report_lines += [f"Linter raw log:\n{stdout}"]
        # Complete lines
        text_report_lines += self.master.complete_text_reporter_report(self)
        # Write to file
        text_report_sub_folder = config.get(
            self.master.request_id, "TEXT_REPORTER_SUB_FOLDER", "linters_logs"
        )
        text_file_name = (
            f"{self.report_folder}{os.path.sep}"
            f"{text_report_sub_folder}{os.path.sep}"
            f"{self.master.status.upper()}-{self.master.name}.log"
        )
        if not os.path.isdir(os.path.dirname(text_file_name)):
            os.makedirs(os.path.dirname(text_file_name), exist_ok=True)
        with open(text_file_name, "w", encoding="utf-8") as text_file:
            text_file_content = "\n".join(text_report_lines) + "\n"
            text_file.write(text_file_content)
            logging.debug(
                f"[Text Reporter] Generated {self.name} report: {text_file_name}"
            )
