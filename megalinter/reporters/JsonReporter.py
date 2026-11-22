#!/usr/bin/env python3
"""
Output results in console
"""

import copy
import json
import logging
import os

from megalinter import Reporter, config, utils


class JsonReporter(Reporter):
    name = "JSON"
    scope = "mega-linter"
    report_type = "simple"
    max_depth = 5
    megalinter_fields = [
        "request_id",
        "linters",
        "reporters",
        "report_folder",
        "file_extensions",
        "file_names_regex",
        "status",
        "return_code",
        "has_updated_sources",
        "flavor_suggestions",
        "native_suggestion",
        "skipped_linters",
        "tips",
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
        "total_number_warnings",
        "number_fixed",
        "files_lint_results",
        "elapsed_time_s",
        "blocking",
        "findings",
        "native_first_run",
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
        # Imported on use: loading this library at startup slows down every run
        import jsonpickle

        result_obj = copy.deepcopy(self.master)
        self.add_computed_fields(result_obj)
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

    # Fields built from several attributes of the run, for both simple and detailed reports
    def add_computed_fields(self, result_obj):
        result_obj.skipped_linters = result_obj.skipped_linters_details
        tips = list(result_obj.tips)
        for linter in result_obj.linters:
            # A linter with errors is blocking when it fails the run (not with DISABLE_ERRORS,
            # nor under <LINTER>_DISABLE_ERRORS_IF_LESS_THAN). Without errors, as configured
            linter.blocking = (
                linter.return_code != 0
                if linter.number_errors > 0
                else linter.disable_errors is not True
            )
            linter.findings = linter.sarif_findings
            for tip in linter.tips:
                linter_tip = {**tip, "linter": linter.name}
                if linter_tip not in tips:
                    tips.append(linter_tip)
        result_obj.tips = tips

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
