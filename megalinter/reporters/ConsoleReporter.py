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
        table_header = ["Descriptor", "Linter", "Found", "Fixed", "Errors"]
        table_data = [table_header]
        for linter in self.master.linters:
            if linter.is_active is True:
                nb_fixed_cell = str(linter.number_fixed) if linter.try_fix is True else ''
                table_data += [
                    [linter.descriptor_id, linter.linter_name, str(len(linter.files)), nb_fixed_cell,
                     str(linter.number_errors)]]
        table = terminaltables.AsciiTable(table_data)
        table.title = "----SUMMARY"
        # Output table in console
        logging.info("")
        for table_line in table.table.splitlines():
            logging.info(table_line)
        logging.info("")
