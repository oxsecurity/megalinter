#!/usr/bin/env python3
# Tests of the pool running the linters in parallel: threads by default, or
# processes with PARALLEL_POOL: processes
import logging
import os
import sys
import threading
import unittest

from megalinter import config
from megalinter.MegaLinter import Megalinter

FAKE_LINTER_MESSAGE = "fake linter ran"


# Must be at module level to be picklable by the worker processes
class FakeLinter:
    def __init__(self, name, descriptor_id="FAKE"):
        self.name = name
        self.descriptor_id = descriptor_id
        self.linter_speed = 1
        self.apply_fixes = False
        self.ran_in_pid = None
        self.ran_in_thread = None
        self.version_read = False

    def run(self, **kwargs):
        self.ran_in_pid = os.getpid()
        self.ran_in_thread = threading.current_thread().name
        logging.info(f"{FAKE_LINTER_MESSAGE}: {self.name}")
        return self

    def get_linter_version(self):
        self.version_read = True
        return "1.0.0"


class CollectHandler(logging.Handler):
    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def emit(self, record):
        self.messages.append(record.getMessage())


def build_megalinter(request_id, native_mode):
    megalinter = Megalinter.__new__(Megalinter)
    megalinter.request_id = request_id
    megalinter.native_mode = native_mode
    megalinter.linters = [FakeLinter(f"FAKE_LINTER_{index}") for index in range(4)]
    return megalinter


class ParallelPoolTest(unittest.TestCase):
    def setUp(self):
        self.request_id = "test-parallel-pool"
        config.set_config(self.request_id, {"PARALLEL_PROCESS_NUMBER": "2"})
        self.addCleanup(config.delete, self.request_id)
        root_logger = logging.getLogger()
        self.initial_handlers = root_logger.handlers[:]
        self.initial_level = root_logger.level
        self.messages = []
        root_logger.handlers = [CollectHandler(self.messages)]
        root_logger.setLevel(logging.INFO)

    def tearDown(self):
        root_logger = logging.getLogger()
        root_logger.handlers = self.initial_handlers
        root_logger.setLevel(self.initial_level)

    def run_parallel(self, megalinter):
        megalinter.process_linters_parallel(list(megalinter.linters), False)

    def test_linters_run_in_threads(self):
        for native_mode in (True, False):
            self.assertEqual(
                build_megalinter(self.request_id, native_mode).get_parallel_pool_type(),
                "threads",
            )
        megalinter = build_megalinter(self.request_id, native_mode=True)
        self.run_parallel(megalinter)
        for linter in megalinter.linters:
            self.assertEqual(linter.ran_in_pid, os.getpid(), linter.name)
            self.assertNotEqual(linter.ran_in_thread, "MainThread", linter.name)
            self.assertTrue(linter.version_read, linter.name)
            self.assertIn(f"{FAKE_LINTER_MESSAGE}: {linter.name}", self.messages)
        self.assertEqual(logging.getLogger().handlers[0].messages, self.messages)

    def test_processes_on_request(self):
        config.set(self.request_id, "PARALLEL_POOL", "processes")
        megalinter = build_megalinter(self.request_id, native_mode=False)
        self.assertEqual(megalinter.get_parallel_pool_type(), "processes")
        self.run_parallel(megalinter)
        for linter in megalinter.linters:
            # The linters returned by the worker processes replace the initial ones
            self.assertIsNotNone(linter.ran_in_pid, linter.name)
            self.assertNotEqual(linter.ran_in_pid, os.getpid(), linter.name)
            self.assertIn(f"{FAKE_LINTER_MESSAGE}: {linter.name}", self.messages)

    # Linters running in threads share the configuration: building the environment of
    # a linter must not fail while another linter sets a variable
    def test_build_env_while_other_threads_set_variables(self):
        request_id = "test-parallel-pool-concurrent-config"
        config.set_config(request_id, {f"VAR_{index}": "x" for index in range(300)})
        self.addCleanup(config.delete, request_id)
        writing = threading.Event()
        writing.set()
        errors = []

        def set_variables():
            for index in range(30000):
                config.set_value(request_id, f"NEW_{index}", "y")
            writing.clear()

        def build_envs():
            try:
                while writing.is_set():
                    config.build_env(request_id)
            except RuntimeError as e:
                errors.append(e)

        threads = [threading.Thread(target=set_variables)] + [
            threading.Thread(target=build_envs) for _ in range(2)
        ]
        # Switch threads as often as possible, so they interleave inside build_env
        switch_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)
        try:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        finally:
            sys.setswitchinterval(switch_interval)
        self.assertEqual(errors, [])

    def test_invalid_value_uses_threads(self):
        config.set(self.request_id, "PARALLEL_POOL", "fibers")
        self.assertEqual(
            build_megalinter(self.request_id, False).get_parallel_pool_type(),
            "threads",
        )


if __name__ == "__main__":
    unittest.main()
