#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging

import terminaltables
from megalinter import Reporter


class ConsoleReporter(Reporter):
    name = "CONSOLE"
    scope = "mega-linter"

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        super().__init__(params)

    def produce_report(self):
        table_header = ["Descriptor", "Linter", "Found", "Fixed", "Errors"]
        if self.master.show_elapsed_time is True:
            table_header += ["Elapsed time"]
        table_data = [table_header]
        for linter in self.master.linters:
            if linter.is_active is True:
                nb_fixed_cell = (
                    str(linter.number_fixed) if linter.try_fix is True else ""
                )
                if linter.cli_lint_mode == "project":
                    found = "yes"
                    errors = "yes" if linter.number_errors > 0 else "no"
                    nb_fixed_cell = "yes" if nb_fixed_cell != "" else nb_fixed_cell
                else:
                    found = str(len(linter.files))
                    errors = str(linter.number_errors)
                table_line = [
                    linter.descriptor_id,
                    linter.linter_name,
                    found,
                    nb_fixed_cell,
                    errors,
                ]
                if self.master.show_elapsed_time is True:
                    table_line += [str(round(linter.elapsed_time_s, 2)) + "s"]
                table_data += [table_line]
        table = terminaltables.AsciiTable(table_data)
        table.title = "----SUMMARY"
        # Output table in console
        logging.info("")
        for table_line in table.table.splitlines():
            logging.info(table_line)
        logging.info("")
