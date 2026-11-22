#!/usr/bin/env python3
# Tests of the thread pool running the linters in parallel
import logging
import os
import sys
import threading
import unittest

from megalinter import config
from megalinter.MegaLinter import Megalinter

FAKE_LINTER_MESSAGE = "fake linter ran"


class FakeLinter:
    def __init__(self, name, descriptor_id="FAKE"):
        self.name = name
        self.descriptor_id = descriptor_id
        self.linter_speed = 1
        self.apply_fixes = False
        self.ran_in_pid = None
        self.ran_in_thread = None
        self.version_read = False
        self.fail = False

    def run(self, **kwargs):
        if self.fail:
            raise RuntimeError(f"{self.name} failed")
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
            megalinter = build_megalinter(self.request_id, native_mode)
            linters = list(megalinter.linters)
            self.run_parallel(megalinter)
            # The linters run in place: the same objects hold the results
            self.assertEqual(megalinter.linters, linters)
            for linter in megalinter.linters:
                self.assertEqual(linter.ran_in_pid, os.getpid(), linter.name)
                self.assertNotEqual(linter.ran_in_thread, "MainThread", linter.name)
                self.assertTrue(linter.version_read, linter.name)
                self.assertIn(f"{FAKE_LINTER_MESSAGE}: {linter.name}", self.messages)
        self.assertEqual(logging.getLogger().handlers[0].messages, self.messages)

    def test_single_group_runs_in_a_thread(self):
        megalinter = build_megalinter(self.request_id, native_mode=False)
        megalinter.linters = megalinter.linters[:1]
        self.run_parallel(megalinter)
        self.assertNotEqual(megalinter.linters[0].ran_in_thread, "MainThread")

    def test_failed_group_raises(self):
        megalinter = build_megalinter(self.request_id, native_mode=False)
        megalinter.linters[1].fail = True
        with self.assertRaises(RuntimeError):
            self.run_parallel(megalinter)

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


if __name__ == "__main__":
    unittest.main()
