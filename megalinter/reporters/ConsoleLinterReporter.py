#!/usr/bin/env python3
"""
Output results in console
"""
import logging

from megalinter import Reporter, utils


class ConsoleLinterReporter(Reporter):
    name = "CONSOLE"
    scope = "linter"

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        super().__init__(params)

    def initialize(self):
        linter_version = self.master.get_linter_version()
        # Linter header prints
        msg = [
            f"### Linting [{self.master.descriptor_id}] files",
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

    def produce_report(self):
        # Output results file by file
        for res in self.master.files_lint_results:
            file_nm = utils.normalize_log_string(res["file"])
            line = f"[{self.master.linter_name}] {file_nm} - {res['status'].upper()}"
            if res["fixed"] is True:
                line += " - FIXED"
            if res["status_code"] == 0:
                logging.info(line)
            else:
                logging.error(line)
                logging.error(f"--Error detail:\n{res['stdout']}")
        # Output linter status
        base_phrase = f"Linted [{self.master.descriptor_id}] files with [{self.master.linter_name}]"
        elapse = str(round(self.master.elapsed_time_s, 2)) + "s"
        if self.master.return_code == 0 and self.master.status == "success":
            logging.info(f"✅ {base_phrase} successfully - ({elapse})")
        elif self.master.return_code == 0 and self.master.status != "success":
            logging.warning(
                f"✅ {base_phrase}: Found non blocking error(s) - ({elapse})"
            )
        elif self.master.return_code != 0 and self.master.status != "success":
            logging.error(f"❌ {base_phrase}: Found error(s) - ({elapse})")
