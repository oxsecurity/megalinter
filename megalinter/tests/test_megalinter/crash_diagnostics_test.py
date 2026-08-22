#!/usr/bin/env python3
"""
Unit tests for crash diagnostics setup

"""

import faulthandler
import threading
import unittest

from megalinter.run import enable_crash_diagnostics

# CPython 3.14.7 raised the musl thread stack size to this value, so anything
# below it is known to segfault on Alpine instead of raising RecursionError
MIN_SAFE_THREAD_STACK_SIZE = 1024 * 1024


class crash_diagnostics_test(unittest.TestCase):
    def setUp(self):
        self.initial_stack_size = threading.stack_size()
        self.initial_faulthandler_enabled = faulthandler.is_enabled()

    def tearDown(self):
        threading.stack_size(self.initial_stack_size)
        if self.initial_faulthandler_enabled is False:
            faulthandler.disable()

    def test_faulthandler_is_enabled(self):
        faulthandler.disable()
        enable_crash_diagnostics()
        self.assertTrue(
            faulthandler.is_enabled(),
            "faulthandler must be enabled so a fatal signal prints a traceback",
        )

    def test_thread_stack_size_is_large_enough(self):
        threading.stack_size(0)
        enable_crash_diagnostics()
        self.assertGreaterEqual(
            threading.stack_size(),
            MIN_SAFE_THREAD_STACK_SIZE,
            "threads must not run with musl's 128 KiB default stack",
        )
