#!/usr/bin/env python3
"""
Web Hook linter reporter
Post linter results to a Web Hook
"""
import logging

import requests
from megalinter import Reporter, config
from megalinter.utils_reporter import build_linter_reporter_external_result


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
        self.web_hook_data = build_linter_reporter_external_result(self)
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        if config.exists(self.master.request_id, "WEBHOOK_REPORTER_BEARER_TOKEN"):
            headers["authorization"] = (
                f"Bearer {config.get(self.master.request_id, 'WEBHOOK_REPORTER_BEARER_TOKEN')}"
            )
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
