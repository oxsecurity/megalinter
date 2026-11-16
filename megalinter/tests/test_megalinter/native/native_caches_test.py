import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from megalinter.Linter import Linter
from megalinter.native import runtimes
from megalinter.native.toolchain import Toolchain


# Only the version cache methods of Linter, without its descriptor-driven constructor
class FakeLinter:
    native_version_cache_file = Linter.native_version_cache_file
    native_version_cache_key = Linter.native_version_cache_key
    read_native_version_cache = Linter.read_native_version_cache
    write_native_version_cache = Linter.write_native_version_cache
    native_search_path = Linter.native_search_path

    def __init__(self, install_dir, host_tool=False):
        self.name = "PYTHON_FAKE"
        self.version_extract_regex = r"\d+(\.\d+)+"
        # The executable called by the version command: this Python interpreter
        self.native_toolchain = Toolchain(
            [os.path.dirname(sys.executable)], {}, install_dir, None, host_tool
        )

    def build_version_command(self):
        return [os.path.basename(sys.executable), "--version"]


class NativeVersionCacheTest(unittest.TestCase):
    def setUp(self):
        self.install_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.install_dir, ignore_errors=True)

    def test_version_is_reused(self):
        FakeLinter(self.install_dir).write_native_version_cache("1.2.3")
        self.assertEqual(
            FakeLinter(self.install_dir).read_native_version_cache(), "1.2.3"
        )

    def test_host_tools_are_never_cached(self):
        linter = FakeLinter(self.install_dir, host_tool=True)
        linter.write_native_version_cache("1.2.3")
        self.assertIsNone(linter.read_native_version_cache())
        self.assertEqual(os.listdir(self.install_dir), [])

    def test_changed_regex_invalidates(self):
        FakeLinter(self.install_dir).write_native_version_cache("1.2.3")
        linter = FakeLinter(self.install_dir)
        linter.version_extract_regex = r"v(\d+)"
        self.assertIsNone(linter.read_native_version_cache())

    def test_changed_executable_invalidates(self):
        FakeLinter(self.install_dir).write_native_version_cache("1.2.3")
        with mock.patch("os.path.getmtime", return_value=0.0):
            self.assertIsNone(FakeLinter(self.install_dir).read_native_version_cache())

    def test_without_native_toolchain_nothing_is_cached(self):
        linter = FakeLinter(self.install_dir)
        linter.native_toolchain = None
        linter.write_native_version_cache("1.2.3")
        self.assertIsNone(linter.read_native_version_cache())


class HostRuntimeCacheTest(unittest.TestCase):
    def setUp(self):
        runtimes.HOST_RUNTIME_CACHE.clear()

    def tearDown(self):
        runtimes.HOST_RUNTIME_CACHE.clear()

    def test_found_runtime_is_detected_once(self):
        found = runtimes.RuntimeInfo("node", "24.0.0", "host")
        with mock.patch.object(runtimes, "find_on_host", return_value=found) as finder:
            runtimes.detect_on_host("node", {}, "path")
            self.assertIs(runtimes.detect_on_host("node", {}, "path"), found)
        self.assertEqual(finder.call_count, 1)

    # A missing runtime can be installed later in the same process (native_ci.py)
    def test_missing_runtime_is_looked_for_again(self):
        with mock.patch.object(runtimes, "find_on_host", return_value=None) as finder:
            runtimes.detect_on_host("php", {}, "path")
            runtimes.detect_on_host("php", {}, "path")
        self.assertEqual(finder.call_count, 2)

    def test_catalog_copies_are_independent(self):
        catalog = runtimes.load_runtime_catalog()
        catalog["node"]["detect"] = None
        self.assertIsNotNone(runtimes.load_runtime_catalog()["node"]["detect"])
