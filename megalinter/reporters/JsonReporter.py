#!/usr/bin/env python3
"""
Output results in console
"""
import copy
import json
import logging
import os

import jsonpickle
from megalinter import Reporter, config, utils


class JsonReporter(Reporter):
    name = "JSON"
    scope = "mega-linter"
    report_type = "simple"
    max_depth = 5
    megalinter_fields = [
        "linters",
        "reporters",
        "report_folder",
        "file_extensions",
        "file_names_regex",
        "status",
        "return_code",
        "has_updated_sources",
        "flavor_suggestions",
        "pre_commands_results",
        "post_commands_results",
    ]
    linter_fields = [
        "descriptor_id",
        "name",
        "linter_name",
        "descriptor_type",
        "is_active",
        "files",
        "files_number",
        "status",
        "return_code",
        "number_errors",
        "total_number_errors",
        "number_fixed",
        "files_lint_results",
        "elapsed_time_s",
    ]

    def __init__(self, params=None):
        # Deactivate JSON output by default
        self.is_active = False
        self.processing_order = (
            9999  # Run at last so the output is on the last console line
        )
        super().__init__(params)

    def manage_activation(self):
        if not utils.can_write_report_files(self.master):
            self.is_active = False
        elif config.get(self.master.request_id, "JSON_REPORTER", "false") == "true":
            self.is_active = True
            if (
                config.get(
                    self.master.request_id, "JSON_REPORTER_OUTPUT_DETAIL", "simple"
                )
                == "detailed"
            ):
                self.report_type = "detailed"

    def produce_report(self):
        result_obj = copy.deepcopy(self.master)
        # Remove output data if result is simple (except if we are in debug mode)
        if (
            self.report_type == "simple"
            and config.get(self.master.request_id, "LOG_LEVEL", "") != "DEBUG"
        ):
            result_obj = self.filter_fields(result_obj, self.megalinter_fields)
            result_obj.linters = filter(
                lambda x: x.is_active is True, result_obj.linters
            )
            result_obj.linters = list(
                map(
                    lambda x: self.filter_fields(x, self.linter_fields),
                    result_obj.linters,
                )
            )
            result_obj.reporters = list(
                map(lambda x: self.filter_fields(x, []), result_obj.reporters)
            )
            for reporter in result_obj.reporters:
                setattr(reporter, "name", reporter.name)

        # Generate JSON from object using jsonpickle
        result_json = jsonpickle.encode(
            result_obj, unpicklable=False, max_depth=self.max_depth, indent=4
        )
        # unserialize + serialize to sort object keys
        result_json_obj = json.loads(result_json)
        result_json = json.dumps(result_json_obj, sort_keys=True, indent=4)
        # Write output file
        json_file_name = f"{self.report_folder}{os.path.sep}" + config.get(
            self.master.request_id, "JSON_REPORTER_FILE_NAME", "mega-linter-report.json"
        )
        with open(json_file_name, "w", encoding="utf-8") as json_file:
            json_file.write(result_json)
            logging.info(
                f"[JSON Reporter] Generated {self.name} report: {json_file_name}"
            )

    def filter_fields(self, obj, fields_to_keep):
        for field in dir(obj):
            if (
                not field.startswith("__")
                and not callable(getattr(obj, field))
                and (
                    (len(fields_to_keep) > 0 and field not in fields_to_keep)
                    or getattr(obj, field, None) is None
                )
            ):
                try:
                    delattr(obj, field)
                except:  # noqa: E722
                    pass
        return obj
