#!/usr/bin/env python3
"""
Output results in console
"""
import logging

from megalinter import Reporter, config, utils


class ConsoleLinterReporter(Reporter):
    name = "CONSOLE"
    scope = "linter"

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        self.report_type = "simple"
        if config.get("OUTPUT_DETAIL", "") == "detailed":
            self.report_type = "detailed"
        super().__init__(params)

    def produce_report(self):
        linter_version = self.master.get_linter_version()
        # Linter header prints
        msg = [
            "",
            f"### Processing [{self.master.descriptor_id}] files",
            f"- Using [{self.master.linter_name} v{linter_version}] {self.master.linter_url}",
        ]
        if self.master.descriptor_id != self.master.name:
            msg += [f"- Mega-Linter key: [{self.master.name}]"]
        if self.master.config_file is not None:
            msg += [f"- Rules config: [{self.master.config_file_label}]"]
        else:
            msg += [f"- Rules config: identified by [{self.master.linter_name}]"]
        if self.master.config_file_error is not None:
            logging.warning(self.master.config_file_error)
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
            if res["status_code"] in [0, None]:  # file ok or file from list_of_files
                logging.info(line)
            else:
                logging.error(line)
                logging.error(f"--Error detail:\n{res['stdout']}")
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
            logging.info(f"✅ {base_phrase} successfully - ({elapse})")
        elif self.master.return_code == 0 and self.master.status != "success":
            logging.warning(
                f"✅ {base_phrase}: Found {total_errors} non blocking error(s) - ({elapse})"
            )
        elif self.master.return_code != 0 and self.master.status != "success":
            logging.error(
                f"❌ {base_phrase}: Found {total_errors} error(s) - ({elapse})"
            )
        else:
            logging.error(
                f"❌ There is a Mega-Linter issue, please report it: {self.master.return_code} / {self.master.status}"
            )
