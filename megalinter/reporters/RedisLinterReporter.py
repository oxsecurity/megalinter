#!/usr/bin/env python3
"""
Web Hook linter reporter
Post linter results to a Web Hook
"""
import json
import logging

from megalinter import Reporter, config
from megalinter.utils_reporter import (
    build_linter_reporter_external_result,
    build_linter_reporter_start_message,
)
from redis import Redis


class RedisLinterReporter(Reporter):
    name = "REDIS_LINTER_REPORTER"
    scope = "linter"

    redis_host: str | None = None
    redis_port: int | None = None
    redis_method: str | None = None  # Stream or PubSub
    stream_key: str | None = None
    pubsub_channel: str | None = None
    message_data: object | None = None

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
                self.redis_method = config.get(
                    self.master.request_id, "REDIS_LINTER_REPORTER_METHOD", "STREAM"
                )
                # Use Redis Stream
                if self.redis_method == "STREAM":
                    self.stream_key = config.get(
                        self.master.request_id,
                        "REDIS_LINTER_REPORTER_STREAM",
                        "megalinter:stream:linter_results",
                    )
                else:
                    # Use redis PubSub
                    self.pubsub_channel = config.get(
                        self.master.request_id,
                        "REDIS_LINTER_REPORTER_PUBSUB_CHANNEL",
                        "megalinter:pubsub:linter_results:" + self.master.request_id,
                    )
            else:
                logging.error(
                    "You need to define REDIS_LINTER_REPORTER_HOST to use RedisLinterReporter"
                )

    # Send message when linter is about to start
    def initialize(self):
        start_message = build_linter_reporter_start_message(
            self, redis_stream=(self.redis_method == "STREAM")
        )
        self.send_redis_message(start_message)

    # Send message when linter is completed to Redis Stream
    def produce_report(self):
        self.message_data = build_linter_reporter_external_result(
            self, redis_stream=(self.redis_method == "STREAM")
        )
        self.send_redis_message(self.message_data)

    def send_redis_message(self, message_data):
        try:
            redis = Redis(host=self.redis_host, port=self.redis_port, db=0)
            logging.debug("REDIS Connection: " + str(redis.info()))
            if self.redis_method == "STREAM":
                resp = redis.xadd(self.stream_key, message_data)
            else:
                resp = redis.publish(self.pubsub_channel, json.dumps(message_data))
            logging.info("REDIS RESP" + str(resp))
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
            logging.warning(
                "[Redis Linter Reporter] Redis Message data: " + str(message_data)
            )
