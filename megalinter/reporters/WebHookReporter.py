#!/usr/bin/env python3
"""
Web Hook reporter
Post MegaLinter lifecycle events to a Web Hook endpoint
"""
import logging

from megalinter import Reporter, config
from megalinter.utils_reporter import (
    build_reporter_external_result,
    build_reporter_start_message,
    post_webhook_message,
)


class WebHookReporter(Reporter):
    name = "WEBHOOK_REPORTER"
    scope = "mega-linter"

    hook_url: str | None = None
    web_hook_data: object | None = None

    def __init__(self, params=None):
        # Deactivate WebHook reporter by default
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

    # Send message when MegaLinter is about to start
    def initialize(self):
        start_message = build_reporter_start_message(self)
        post_webhook_message(self.hook_url, start_message, self, "MegaLinter start event")

    # Send message when MegaLinter is completed
    def produce_report(self):
        self.web_hook_data = build_reporter_external_result(self)
        post_webhook_message(self.hook_url, self.web_hook_data, self, "MegaLinter complete event")