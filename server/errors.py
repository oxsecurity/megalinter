import json
import logging

from megalinter import config
from megalinter.utils_reporter import manage_redis_stream
from redis import Redis


class MegalinterServerException(Exception):
    redis_host: str | None = None
    redis_port: int | None = None
    redis_method: str | None = None  # Stream or PubSub
    stream_key: str | None = None
    pubsub_channel: str | None = None
    message_data: object | None = None

    def __init__(self, message, error_code, request_id, error_details={}):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        # Now for your custom code...
        self.error_code = error_code
        self.message = message
        self.request_id = request_id
        self.error_details = error_details
        if config.get(None, "REDIS_REPORTER", "false") == "true" and config.exists(
            None, "REDIS_REPORTER_HOST"
        ):
            self.redis_host = config.get(None, "REDIS_REPORTER_HOST")
            self.redis_port = int(config.get(None, "REDIS_REPORTER_PORT", 6379))
            self.redis_method = config.get(
                None, "REDIS_ERRORS_REPORTER_METHOD", "PUBSUB"
            )
            # Use Redis Stream
            if self.redis_method == "STREAM":
                self.stream_key = config.get(
                    None,
                    "REDIS_ERRORS_REPORTER_STREAM",
                    "megalinter:stream:errors",
                )
            else:
                # Use redis PubSub
                self.pubsub_channel = config.get(
                    None,
                    "REDIS_ERRORS_REPORTER_PUBSUB_CHANNEL",
                    "megalinter:pubsub:" + request_id,
                )

    # Send redis message before raising exception
    def send_redis_message(self):
        self.message_data = {
            "messageType": "serverError",
            "message": self.message,
            "errorCode": self.error_code,
            "errorDetails": self.error_details,
            "requestId": self.request_id,
        }
        final_message = manage_redis_stream(
            self.message_data, (self.redis_method == "STREAM")
        )
        try:
            redis = Redis(host=self.redis_host, port=self.redis_port, db=0)
            logging.debug("REDIS Connection: " + str(redis.info()))
            if self.redis_method == "STREAM":
                resp = redis.xadd(self.stream_key, final_message)
            else:
                resp = redis.publish(self.pubsub_channel, json.dumps(final_message))
            logging.info("REDIS RESP" + str(resp))
        except ConnectionError as e:
            logging.warning(
                f"[Redis Server Reporter] Error posting message for MegaLinter: Connection error {str(e)}"
            )
        except Exception as e:
            logging.warning(
                f"[Redis Server Reporter] Error posting message for MegaLinter: Error {str(e)}"
            )
            logging.warning(
                "[Redis Server Reporter] Redis Message data: " + str(self.message_data)
            )
