#!/usr/bin/env python3
"""
Output results in console
"""
import logging

from megalinter import Reporter


class ConsoleLinterReporter(Reporter):
    name = 'CONSOLE'
    scope = 'linter'

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        super().__init__(params)

    def initialize(self):
        linter_version = self.master.get_linter_version()
        # Linter header prints
        msg = [f"### Linting [{self.master.descriptor_id}] files",
               f"- Using [{self.master.linter_name} v{linter_version}] {self.master.linter_url}"]
        if self.master.descriptor_id != self.master.name:
            msg += [f"- Mega-Linter key: [{self.master.name}]"]
        if self.master.config_file is not None:
            msg += [f"- Rules config: [{self.master.config_file}"]
        else:
            msg += [f"- Rules config: identified by [{self.master.linter_name}]"]
        logging.info("\n".join(msg))

    def produce_report(self):
        for res in self.master.files_lint_results:
            line = f"[{self.master.linter_name}] {res['file']} - {res['status'].upper()}"
            if res['status_code'] == 0:
                logging.info(line)
            else:
                logging.error(line)
                logging.error(f"--Error detail:\n{res['stdout']}")
