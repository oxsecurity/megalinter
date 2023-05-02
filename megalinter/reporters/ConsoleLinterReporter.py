#!/usr/bin/env python3
"""
Output results in console
"""
import logging

import chalk as c
from megalinter import Reporter, config, utils
from megalinter.constants import ML_DOC_URL_DESCRIPTORS_ROOT
from megalinter.utils_reporter import log_section_end, log_section_start


class ConsoleLinterReporter(Reporter):
    name = "CONSOLE"
    scope = "linter"
    print_all_files = False

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        self.report_type = "simple"
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "OUTPUT_DETAIL", "") == "detailed":
            self.report_type = "detailed"
        if config.get(self.master.request_id, "PRINT_ALL_FILES", "") == "true":
            self.print_all_files = True
        if config.get(self.master.request_id, "CONSOLE_REPORTER", "true") == "false":
            self.is_active = False

    def produce_report(self):
        linter_version = self.master.get_linter_version()
        if self.master.is_plugin is True:
            linter_doc_url = (
                self.master.linter_url
                or self.master.linter_repo
                or "[linter_url should be defined on descriptor]"
            )
        else:
            linter_doc_url = (
                f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{self.master.descriptor_id.lower()}_"
                f"{self.master.linter_name.lower().replace('-', '_')}"
            )
        # Output linter status
        base_phrase = f"Linted [{self.master.descriptor_id}] files with [{self.master.linter_name}]"
        elapse = str(round(self.master.elapsed_time_s, 2)) + "s"
        total_errors = str(self.master.total_number_errors)
        if self.master.return_code == 0 and self.master.status == "success":
            logging.info(
                log_section_start(
                    f"processed-{self.master.name}",
                    c.green(f"✅ {base_phrase} successfully - ({elapse})"),
                )
            )
        elif self.master.return_code == 0 and self.master.status != "success":
            logging.warning(
                log_section_start(
                    f"processed-{self.master.name}",
                    c.yellow(
                        f"✅ {base_phrase}: Found {total_errors} non blocking error(s) - ({elapse})"
                    ),
                )
            )
        elif self.master.return_code != 0 and self.master.status != "success":
            logging.error(
                log_section_start(
                    f"processed-{self.master.name}",
                    c.red(
                        f"❌ {base_phrase}: Found {total_errors} error(s) - ({elapse})"
                    ),
                )
            )
        else:
            logging.error(
                log_section_start(
                    f"processed-{self.master.name}",
                    f"❌ There is a MegaLinter issue, please report it: {self.master.return_code}"
                    + " / {self.master.status}",
                )
            )
        # Linter header prints
        msg = [
            f"- Using [{self.master.linter_name} v{linter_version}] {linter_doc_url}",
        ]
        if self.master.descriptor_id != self.master.name:
            msg += [f"- MegaLinter key: [{self.master.name}]"]
        # Config info
        if self.master.config_file is not None:
            msg += [f"- Rules config: [{self.master.config_file_label}]"]
        else:
            msg += [f"- Rules config: identified by [{self.master.linter_name}]"]
        if self.master.config_file_error is not None:
            logging.warning(self.master.config_file_error)
        # Ignore file info
        if self.master.ignore_file_label is not None:
            msg += [f"- Ignore file: [{self.master.ignore_file_label}]"]
        if self.master.ignore_file_error is not None:
            logging.warning(self.master.ignore_file_error)
        # List of files
        if self.print_all_files is False and self.master.cli_lint_mode != "project":
            msg += [
                f"- Number of files analyzed: [{len(self.master.files_lint_results)}]"
            ]
        logging.info("\n".join(msg))
        # Pre-commands logs
        if len(self.master.log_lines_pre) > 0:
            logging.info("\n".join(self.master.log_lines_pre))
        # Output results
        for res in self.master.files_lint_results:
            file_nm = utils.normalize_log_string(res["file"])
            if self.master.cli_lint_mode == "file":
                file_errors = str(res.get("errors_number", 0))
                line = f"[{self.master.linter_name}] {file_nm} - {res['status'].upper()} - {file_errors} error(s)"
            else:
                line = f"[{self.master.linter_name}] {file_nm}"
            if res["fixed"] is True:
                line += " - FIXED"
                line = c.cyan(line)
            if res["status_code"] in [0, None]:  # file ok or file from list_of_files
                if self.print_all_files is True:
                    logging.info(line)
            else:
                logging.error(c.red(line))
                logging.error(c.red(f"--Error detail:\n{res['stdout']}"))
        # Output stdout if not file by file
        if self.master.cli_lint_mode in ["list_of_files", "project"]:
            stdout = (
                self.master.stdout_human
                if self.master.stdout_human is not None
                else self.master.stdout
            )
            if self.master.status != "success":
                logging.error(f"--Error detail:\n{stdout}")
            elif self.report_type == "detailed":
                logging.info(f"--Log detail:\n{stdout}")
        # Post-commands logs
        if len(self.master.log_lines_post) > 0:
            logging.info("\n".join(self.master.log_lines_post))
        # Close section
        logging.info(log_section_end(f"processed-{self.master.name}"))
