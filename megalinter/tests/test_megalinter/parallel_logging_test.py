#!/usr/bin/env python3
"""
Unit tests for the logging of linters run in parallel worker processes

"""

import logging
import multiprocessing as mp
import unittest
from logging.handlers import QueueHandler, QueueListener

from megalinter.MegaLinter import init_worker

WORKER_INFO_MESSAGE = "info message sent by a worker process"
WORKER_WARNING_MESSAGE = "warning message sent by a worker process"


# Must be at module level to be picklable by the "spawn" and "forkserver" start methods
def emit_worker_log_records():
    logging.info(WORKER_INFO_MESSAGE)
    logging.warning(WORKER_WARNING_MESSAGE)
    return True


class CollectHandler(logging.Handler):
    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def emit(self, record):
        self.messages.append(record.getMessage())


class parallel_logging_test(unittest.TestCase):
    def setUp(self):
        root_logger = logging.getLogger()
        self.initial_handlers = root_logger.handlers[:]
        self.initial_level = root_logger.level

    def tearDown(self):
        root_logger = logging.getLogger()
        root_logger.handlers = self.initial_handlers
        root_logger.setLevel(self.initial_level)

    # Reproduce what Megalinter.process_linters_parallel does, with a single worker
    def collect_worker_messages(self, start_method):
        context = mp.get_context(start_method)
        messages = []
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.handlers = [CollectHandler(messages)]
        initial_handlers = root_logger.handlers[:]
        log_queue = context.Queue()
        log_queue_listener = QueueListener(
            log_queue, *initial_handlers, respect_handler_level=True
        )
        root_logger.handlers = [QueueHandler(log_queue)]
        log_queue_listener.start()
        pool = context.Pool(
            1,
            initializer=init_worker,
            initargs=({}, log_queue, logging.INFO),
        )
        try:
            pool.apply_async(emit_worker_log_records).get(timeout=120)
        finally:
            pool.close()
            pool.join()
            log_queue_listener.stop()
            root_logger.handlers = initial_handlers
        return messages

    def test_worker_log_records_reach_main_process(self):
        # "forkserver" is the default on Linux since Python 3.14, and "spawn" on
        # Windows and macOS: a worker started that way inherits no logging handler
        for start_method in mp.get_all_start_methods():
            with self.subTest(start_method=start_method):
                messages = self.collect_worker_messages(start_method)
                self.assertIn(
                    WORKER_INFO_MESSAGE,
                    messages,
                    f"INFO logs of workers started with [{start_method}] must be "
                    "sent to the main process",
                )
                self.assertIn(
                    WORKER_WARNING_MESSAGE,
                    messages,
                    f"WARNING logs of workers started with [{start_method}] must be "
                    "sent to the main process",
                )
