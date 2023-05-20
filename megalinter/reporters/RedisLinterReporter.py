#!/usr/bin/env python3
"""
Web Hook linter reporter
Post linter results to a Web Hook
"""
import json
import logging
import os
from redis import Redis

import requests
from megalinter import Reporter, config
from megalinter.constants import ML_DOC_URL_DESCRIPTORS_ROOT
from megalinter.utils_reporter import build_linter_reporter_external_result


class RedisLinterReporter(Reporter):
    name = "REDIS_LINTER_REPORTER"
    scope = "linter"

    redis_host: str | None = None
    redis_port: int | None = None
    stream_key: str | None = None
    stream_data: object | None = None

    def __init__(self, params=None):
        # Deactivate Redis Linter Reporter by default
        self.is_active = False
        self.processing_order = 20  # Run after text reporter
        super().__init__(params)

    def manage_activation(self):
        if (
            config.get(self.master.request_id, "REDIS_LINTER_REPORTER", "false")
            == "true"
        ):
            if config.exists(self.master.request_id, "REDIS_LINTER_REPORTER_HOST"):
                self.is_active = True
                self.redis_host = config.get(
                    self.master.request_id, "REDIS_LINTER_REPORTER_HOST"
                )
                self.redis_port = int(
                    config.get(
                        self.master.request_id, "REDIS_LINTER_REPORTER_PORT", 6379
                    )
                )
                self.stream_key = config.get(
                    self.master.request_id,
                    "REDIS_LINTER_REPORTER_STREAM",
                    "megalinter:stream_linter_results",
                )
            else:
                logging.error(
                    "You need to define REDIS_LINTER_REPORTER_HOST to use RedisLinterReporter"
                )

    # Send message to Redis Stream
    def produce_report(self):
        self.stream_data = build_linter_reporter_external_result(self,redis=True)
        try:
            redis = Redis(host=self.redis_host, port=self.redis_port, db=0)
            logging.debug("REDIS Connection: " + str(redis.info()))
            resp = redis.xadd(self.stream_key, self.stream_data)
            logging.info("REDIS RESP"+str(resp))
        except ConnectionError as e:
            logging.warning(
                f"[Redis Linter Reporter] Error posting message for {self.master.descriptor_id}"
                f" with {self.master.linter_name}: Connection error {str(e)}"
            )
        except Exception as e:
            logging.warning(
                f"[Redis Linter Reporter] Error posting message for {self.master.descriptor_id}"
                f" with {self.master.linter_name}: Error {str(e)}"
            )
            logging.warning("[Redis Linter Reporter] Stream data: "+str(self.stream_data))
