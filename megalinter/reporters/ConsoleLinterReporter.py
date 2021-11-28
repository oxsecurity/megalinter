#!/usr/bin/env python3
"""
Output results in console
"""
import logging

import chalk as c
from megalinter import Reporter, config, utils
from megalinter.constants import ML_DOC_URL

mega_linter_version = config.get("BUILD_VERSION", "latest")
DOCS_URL_DESCRIPTORS_ROOT = f"{ML_DOC_URL}/{mega_linter_version}/descriptors"


class ConsoleLinterReporter(Reporter):
    name = "CONSOLE"
    scope = "linter"
    print_all_files = False

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        self.report_type = "simple"
        if config.get("OUTPUT_DETAIL", "") == "detailed":
            self.report_type = "detailed"
        if config.get("PRINT_ALL_FILES", "") == "true":
            self.print_all_files = True
        super().__init__(params)

    def manage_activation(self):
        if config.get("CONSOLE_REPORTER", "true") == "false":
            self.is_active = False

    def produce_report(self):
        linter_version = self.master.get_linter_version()
        linter_doc_url = (
            f"{DOCS_URL_DESCRIPTORS_ROOT}/{self.master.descriptor_id.lower()}_"
            f"{self.master.linter_name.lower().replace('-', '_')}"
        )
        # Linter header prints
        msg = [
            "",
            c.bold(f"### Processed [{self.master.descriptor_id}] files"),
            f"- Using [{self.master.linter_name} v{linter_version}] {linter_doc_url}",
        ]
        if self.master.descriptor_id != self.master.name:
            msg += [f"- MegaLinter key: [{self.master.name}]"]
        if self.master.config_file is not None:
            msg += [f"- Rules config: [{self.master.config_file_label}]"]
        else:
            msg += [f"- Rules config: identified by [{self.master.linter_name}]"]
        if self.master.config_file_error is not None:
            logging.warning(self.master.config_file_error)
        if self.print_all_files is False and self.master.cli_lint_mode != "project":
            msg += [
                f"- Number of files analyzed: [{len(self.master.files_lint_results)}]"
            ]
        logging.info("\n".join(msg))
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
            if self.master.status != "success":
                logging.error(f"--Error detail:\n{self.master.stdout}")
            elif self.report_type == "detailed":
                logging.info(f"--Log detail:\n{self.master.stdout}")
        # Output linter status
        base_phrase = f"Linted [{self.master.descriptor_id}] files with [{self.master.linter_name}]"
        elapse = str(round(self.master.elapsed_time_s, 2)) + "s"
        total_errors = str(self.master.total_number_errors)
        if self.master.return_code == 0 and self.master.status == "success":
            logging.info(c.green(f"✅ {base_phrase} successfully - ({elapse})"))
        elif self.master.return_code == 0 and self.master.status != "success":
            logging.warning(
                c.yellow(
                    f"✅ {base_phrase}: Found {total_errors} non blocking error(s) - ({elapse})"
                )
            )
        elif self.master.return_code != 0 and self.master.status != "success":
            logging.error(
                c.red(f"❌ {base_phrase}: Found {total_errors} error(s) - ({elapse})")
            )
        else:
            logging.error(
                f"❌ There is a MegaLinter issue, please report it: {self.master.return_code} / {self.master.status}"
            )
