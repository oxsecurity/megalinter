#!/usr/bin/env python3
"""
TAP reporter
https://testanything.org/
"""
import logging
import os

from megalinter import Reporter, config, utils


class TapReporter(Reporter):
    name = "TAP"
    scope = "linter"

    def __init__(self, params=None):
        # report_type is tap by default
        self.report_type = "tap"
        super().__init__(params)

    def manage_activation(self):
        # Super-Linter legacy variables
        if config.get(self.master.request_id, "OUTPUT_DETAIL", "") == "detailed":
            self.report_type = "detailed"
        if (
            config.get(self.master.request_id, "TAP_REPORTER_OUTPUT_DETAIL", "")
            == "detailed"
        ):
            self.report_type = "detailed"
        output_format = config.get(self.master.request_id, "OUTPUT_FORMAT", "")
        if output_format.startswith("tap"):
            self.is_active = True
        # MegaLinter vars (false by default)
        elif config.get(self.master.request_id, "TAP_REPORTER", "false") == "true":
            self.is_active = True
        else:
            self.is_active = False
        if not utils.can_write_report_files(self.master):
            self.is_active = False
        if self.is_active is True:
            # If TAP is active, we must lint file by file to have result file by file in TAP
            if self.master.cli_lint_mode == "list_of_files":
                self.master.cli_lint_mode = "file"
            elif self.master.cli_lint_mode == "project":
                self.is_active = False
                logging.warning(
                    f"Tap output is not available for {self.master.linter_name}"
                )

    def produce_report(self):
        if self.master.cli_lint_mode == "project":
            return
        tap_report_lines = ["TAP version 13", f"1..{str(len(self.master.files))}"]
        # Convert file results in TAP
        for index, file_result in enumerate(self.master.files_lint_results):
            file_nm = utils.normalize_log_string(file_result["file"])
            tap_status = "ok" if file_result["status_code"] == 0 else "not ok"
            file_tap_lines = [f"{tap_status} {str(index + 1)} - {file_nm}"]
            if (
                self.report_type == "detailed"
                and file_result["stdout"] != ""
                and file_result["status_code"] != 0
            ):
                std_out_tap = (
                    file_result["stdout"].rstrip(f" {os.linesep}") + os.linesep
                )
                std_out_tap = "\\n".join(std_out_tap.splitlines())
                std_out_tap = std_out_tap.replace(":", " ")
                detailed_lines = ["  ---", f"  message: {std_out_tap}", "  ..."]
                file_tap_lines += detailed_lines
            tap_report_lines += file_tap_lines
        # Write TAP file
        tap_report_sub_folder = config.get(
            self.master.request_id, "TAP_REPORTER_SUB_FOLDER", "tap"
        )
        tap_file_name = (
            f"{self.report_folder}{os.path.sep}"
            f"{tap_report_sub_folder}{os.path.sep}"
            f"mega-linter-{self.master.name}.tap"
        )
        if not os.path.isdir(os.path.dirname(tap_file_name)):
            os.makedirs(os.path.dirname(tap_file_name), exist_ok=True)
        with open(tap_file_name, "w", encoding="utf-8") as tap_file:
            tap_file_content = "\n".join(tap_report_lines) + "\n"
            tap_file.write(tap_file_content)
            logging.info(
                f"[Tap Reporter] Generated {self.name} report: {tap_file_name}"
            )
