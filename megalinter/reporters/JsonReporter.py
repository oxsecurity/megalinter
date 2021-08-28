#!/usr/bin/env python3
"""
Output results in console
"""
import jsonpickle
import logging
import os

from megalinter import Reporter, config


class JsonReporter(Reporter):
    name = "JSON"
    scope = "mega-linter"

    def __init__(self, params=None):
        # Deactivate JSON output by default
        self.is_active = False
        self.processing_order = (
            9999  # Run at last so the output is on the last console line
        )
        super().__init__(params)

    def manage_activation(self):
        if config.get("JSON_REPORTER", "false") == "true":
            self.is_active = True

    def produce_report(self):
        resultJson = jsonpickle.encode(self.master,unpicklable =False,max_depth=3,indent=4)
        json_file_name = f"{self.report_folder}{os.path.sep}"+config.get("JSON_REPORTER_FILE_NAME", "mega-linter-report.json")
        with open(json_file_name, "w", encoding="utf-8") as tap_file:
            tap_file.write(resultJson)
            logging.info(
                f"[JSON Reporter] Generated {self.name} report: {json_file_name}"
            )
