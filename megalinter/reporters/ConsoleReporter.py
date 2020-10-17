#!/usr/bin/env python3
"""
GitHub Status reporter
Post a GitHub status for each linter
"""
import logging

import terminaltables

from megalinter import Reporter


class ConsoleReporter(Reporter):
    name = 'CONSOLE'
    scope = 'mega-linter'

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        super().__init__(params)

    def produce_report(self):
        table_header = ["Descriptor", "Linter",
                        "Files with error(s)", "Total files"]
        table_data = [table_header]
        for linter in self.master.linters:
            if linter.is_active is True:
                table_data += [
                    [linter.descriptor_id, linter.linter_name, str(linter.number_errors), str(len(linter.files))]]
        table = terminaltables.AsciiTable(table_data)
        table.title = "----SUMMARY"
        # Output table in console
        logging.info("")
        for table_line in table.table.splitlines():
            logging.info(table_line)
        logging.info("")
