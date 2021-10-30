#!/usr/bin/env python3
"""
Output results in console
"""
import logging
import os
import urllib

import chalk as c
import terminaltables
from megalinter import Reporter, config
from megalinter.constants import ML_DOC_URL, ML_REPO, ML_REPO_URL


class ConsoleReporter(Reporter):
    name = "CONSOLE"
    scope = "mega-linter"
    gh_url = ML_DOC_URL
    issues_root = ML_REPO_URL+"/issues"

    def __init__(self, params=None):
        # Activate console output by default
        self.is_active = True
        self.processing_order = -9
        super().__init__(params)

    def manage_activation(self):
        if config.get("CONSOLE_REPORTER", "true") == "false":
            self.is_active = False

    def initialize(self):
        # Display collection summary in log
        table_data = [
            ["Descriptor", "Linter", "Criteria", "Matching files", "Format/Fix"]
        ]
        for linter in self.master.linters:
            if linter.is_active is True:
                all_criteria = linter.file_extensions + linter.file_names_regex
                if linter.cli_lint_mode == "project":
                    files_col = "project"
                else:
                    files_col = str(len(linter.files))
                fixes_col = "yes" if linter.apply_fixes is True else "no"
                table_data += [
                    [
                        linter.descriptor_id,
                        linter.linter_name,
                        "|".join(all_criteria),
                        files_col,
                        fixes_col,
                    ]
                ]
        table = terminaltables.AsciiTable(table_data)
        table.title = "----MATCHING LINTERS"
        logging.info("")
        for table_line in table.table.splitlines():
            logging.info(table_line)
        logging.info("")

    def produce_report(self):
        table_header = ["Descriptor", "Linter", "Mode", "Files", "Fixed", "Errors"]
        if self.master.show_elapsed_time is True:
            table_header += ["Elapsed time"]
        table_data = [table_header]
        for linter in self.master.linters:
            if linter.is_active is True:
                nb_fixed_cell = (
                    str(linter.number_fixed) if linter.try_fix is True else ""
                )
                status = (
                    "✅"
                    if linter.status == "success" and linter.return_code == 0
                    else "◬"
                    if linter.status != "success" and linter.return_code == 0
                    else "❌"
                )
                errors = str(linter.total_number_errors)
                if linter.cli_lint_mode == "project":
                    found = "n/a"
                    nb_fixed_cell = "yes" if nb_fixed_cell != "" else nb_fixed_cell
                else:
                    found = str(len(linter.files))

                table_line = [
                    status + " " + linter.descriptor_id,
                    linter.linter_name,
                    linter.cli_lint_mode,
                    found,
                    nb_fixed_cell,
                    errors,
                ]
                if self.master.show_elapsed_time is True:
                    table_line += [str(round(linter.elapsed_time_s, 2)) + "s"]
                table_data += [table_line]
        table = terminaltables.AsciiTable(table_data)
        table.title = "----SUMMARY"
        table.justify_columns = {
            0: "left",
            1: "left",
            2: "left",
            3: "right",
            4: "right",
            5: "right",
            6: "right",
        }
        # Output table in console
        logging.info("")
        for table_line in table.table.splitlines():
            logging.info(table_line)
        logging.info("")
        if self.master.flavor_suggestions is not None:
            if self.master.flavor_suggestions[0] == "new":
                logging.warning(
                    "[flavors] You could have same capabilities but better runtime performances"
                    " if you request a new Mega-Linter flavor."
                )
                linters_list_formatted = ", ".join(self.master.flavor_suggestions[1])
                body = (
                    "Mega-Linter would run faster on my project if I had a flavor containing the following "
                    f"list of linters:\n\n{linters_list_formatted}\n\n"
                    "Would it be possible to create one ? Thanks :relaxed:"
                )
                new_flavor_url = (
                    f"{self.issues_root}/new?assignees=&labels=enhancement&template=feature_request.md"
                    f"&title={urllib.parse.quote('Request new Mega-Linter flavor')}"
                    f"&body={urllib.parse.quote(body)}"
                )
                logging.warning(
                    f"[flavors] Use the following link to request the new flavor: {new_flavor_url}"
                )
            else:
                build_version = os.environ.get("BUILD_VERSION", "v5")
                action_version = (
                    "v5"
                    if "v5" in build_version
                    else "beta"
                    if build_version == "latest"
                    else build_version
                )
                logging.warning(
                    c.blue(
                        "You could have same capabilities but better runtime performances"
                        " if you use a Mega-Linter flavor:"
                    )
                )
                for suggestion in self.master.flavor_suggestions:
                    action_path = f"{ML_REPO}/flavors/{suggestion['flavor']}@{action_version}"
                    flavor_msg = (
                        f"- [{suggestion['flavor']}] {action_path} ({suggestion['linters_number']} linters) "
                        f"{self.gh_url}/flavors/{suggestion['flavor']}/"
                    )
                    logging.warning(flavor_msg)
            logging.info("")
