#!/usr/bin/env python3
"""
Web Hook linter reporter
Post linter results to a Web Hook
"""
import json
import logging
import os

import requests
from megalinter import Reporter, config
from megalinter.constants import ML_DOC_URL_DESCRIPTORS_ROOT


class WebHookLinterReporter(Reporter):
    name = "WEBHOOK_REPORTER"
    scope = "linter"

    hook_url: str | None = None
    web_hook_data: object | None = None

    def __init__(self, params=None):
        # Deactivate GitHub Status by default
        self.is_active = False
        self.processing_order = 20  # Run after text reporter
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "WEBHOOK_REPORTER", "false") == "true":
            if config.exists(self.master.request_id, "WEBHOOK_REPORTER_URL"):
                self.is_active = True
                self.hook_url = config.get(
                    self.master.request_id, "WEBHOOK_REPORTER_URL"
                )
            else:
                logging.error(
                    "You need to define WEBHOOK_REPORTER_URL to use WebHookReporter"
                )

    # Snd webHook to remote server
    def produce_report(self):
        success_msg = "No errors were found in the linting process"
        error_not_blocking = "Errors were detected but are considered not blocking"
        error_msg = f"Found {self.master.total_number_errors} errors"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        if config.exists(self.master.request_id, "WEBHOOK_REPORTER_BEARER_TOKEN"):
            headers[
                "authorization"
            ] = f"Bearer {config.get(self.master.request_id,'WEBHOOK_REPORTER_BEARER_TOKEN')}"
        status_message = (
            success_msg
            if self.master.status == "success" and self.master.return_code == 0
            else error_not_blocking
            if self.master.status == "error" and self.master.return_code == 0
            else error_msg
        )
        lang_lower = self.master.descriptor_id.lower()
        linter_name_lower = self.master.linter_name.lower().replace("-", "_")
        linter_doc_url = (
            f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
        )
        self.web_hook_data = {
            "status": "success" if self.master.return_code == 0 else "error",
            "errorNumber": self.master.total_number_errors,
            "statusMessage": status_message,
            "elapsedTime": round(self.master.elapsed_time_s, 2),
            "descriptorId": self.master.descriptor_id,
            "linterId": self.master.linter_name,
            "linterKey": self.master.name,
            "linterVersion": self.master.get_linter_version(),
            "requestId": self.master.master.request_id,
            "docUrl": linter_doc_url,
            "isFormatter": self.master.is_formatter,
        }
        if (
            self.master.sarif_output_file is not None
            and os.path.isfile(self.master.sarif_output_file)
            and os.path.getsize(self.master.sarif_output_file) > 0
        ):
            with open(
                self.master.sarif_output_file, "r", encoding="utf-8"
            ) as linter_sarif_file:
                self.web_hook_data["outputSarif"] = json.load(linter_sarif_file)
        else:
            text_report_sub_folder = config.get(
                self.master.request_id, "TEXT_REPORTER_SUB_FOLDER", "linters_logs"
            )
            text_file_name = (
                f"{self.report_folder}{os.path.sep}"
                f"{text_report_sub_folder}{os.path.sep}"
                f"{self.master.status.upper()}-{self.master.name}.log"
            )
            if os.path.isfile(text_file_name):
                with open(text_file_name, "r", encoding="utf-8") as text_file:
                    self.web_hook_data["outputText"] = text_file.read()
        try:
            response = requests.post(
                self.hook_url, headers=headers, json=self.web_hook_data
            )
            if 200 <= response.status_code < 299:
                logging.debug(
                    f"[WebHook Reporter] Successfully posted Web Hook for {self.master.descriptor_id}"
                    f" with {self.master.linter_name}"
                )
            else:
                logging.warning(
                    f"[WebHook Reporter] Error posting Status for {self.master.descriptor_id}"
                    f" with {self.master.linter_name}: {response.status_code}\n"
                    f"API response: {response.text}"
                )
        except ConnectionError as e:
            logging.warning(
                f"[WebHook Reporter] Error posting Web Hook for {self.master.descriptor_id}"
                f" with {self.master.linter_name}: Connection error {str(e)}"
            )
        except Exception as e:
            logging.warning(
                f"[WebHook Reporter] Error posting Web Hook for {self.master.descriptor_id}"
                f" with {self.master.linter_name}: Error {str(e)}"
            )
