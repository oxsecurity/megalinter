#!/usr/bin/env python3
"""
Web Hook linter reporter
Post linter lifecycle events to a Web Hook endpoint
"""
import logging

from megalinter import Reporter, config
from megalinter.utils_reporter import (
    build_linter_reporter_external_result,
    build_linter_reporter_start_message,
    post_webhook_message,
)


class WebHookLinterReporter(Reporter):
    name = "WEBHOOK_REPORTER"
    scope = "linter"

    hook_url: str | None = None
    web_hook_data: object | None = None

    def __init__(self, params=None):
        # Deactivate WebHook Linter Reporter by default
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

    # Send message when linter is about to start
    def initialize(self):
        start_message = build_linter_reporter_start_message(self)
        post_webhook_message(self.hook_url, start_message, self, "linter start event")

    # Send message when linter is completed
    def produce_report(self):
        self.web_hook_data = build_linter_reporter_external_result(self)
        post_webhook_message(
            self.hook_url, self.web_hook_data, self, "linter complete event"
        )
