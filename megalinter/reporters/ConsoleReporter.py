#!/usr/bin/env python3
"""
Output results in console
"""
import logging
import os

import terminaltables
from megalinter import Reporter


class ConsoleReporter(Reporter):
    name = "CONSOLE"
    scope = "mega-linter"
    gh_url = "https://nvuillam.github.io/mega-linter"

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        self.processing_order = -9
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
        if self.master.flavor_suggestions is not None:
            build_version = os.environ.get("BUILD_VERSION", "v4")
            action_version = (
                "v4"
                if "v4" in build_version
                else "insiders"
                if build_version == "latest"
                else build_version
            )
            docker_version = (
                "latest" if action_version == "insiders" else action_version
            )
            logging.warning(
                "You could have same capabilities but better runtime performances"
                " if you use a Mega-Linter flavor:"
            )
            for suggestion in self.master.flavor_suggestions:
                action_path = f"nvuillam/mega-linter/flavors/{suggestion['flavor']}@{action_version}"
                image_name = (
                    f"nvuillam/mega-linter-{suggestion['flavor']}:{docker_version}"
                )
                flavor_msg = (
                    f"- [{suggestion['flavor']}] {action_path} |"
                    f" {image_name} ({suggestion['linters_number']} linters)"
                )
                logging.warning(flavor_msg)
            logging.warning(f"More info at {self.gh_url}/flavors/")
            logging.info("")
