import os
import shutil
import tempfile
import unittest

from megalinter import config
from megalinter.Linter import Linter

CACHE_ARGS = [
    "--cache",
    "--cache-location",
    "{{LINTER_CACHE_DIR}}/eslintcache",
    "--cache-strategy",
    "content",
]


def build_linter(request_id, workspace, cache_args=None, user_args=None):
    linter = Linter.__new__(Linter)
    linter.request_id = request_id
    linter.name = "JAVASCRIPT_ES"
    linter.workspace = workspace
    linter.cli_lint_cache_args = CACHE_ARGS if cache_args is None else cache_args
    linter.cli_lint_user_args = user_args or []
    return linter


class NativeLinterCacheArgsTest(unittest.TestCase):
    def setUp(self):
        self.request_id = "test-native-linter-cache-args"
        self.home = tempfile.mkdtemp()
        os.chmod(self.home, 0o700)
        self.workspace = tempfile.mkdtemp()
        config.set_config(
            self.request_id,
            {"MEGALINTER_NATIVE": "true", "MEGALINTER_HOME": self.home},
        )
        self.addCleanup(config.delete, self.request_id)
        self.addCleanup(shutil.rmtree, self.home, True)
        self.addCleanup(shutil.rmtree, self.workspace, True)

    def test_cache_folder_is_outside_the_workspace(self):
        linter = build_linter(self.request_id, self.workspace)
        args = linter.get_native_cache_arguments()
        cache_file = args[2]
        self.assertEqual(args[:2], ["--cache", "--cache-location"])
        self.assertTrue(cache_file.startswith(os.path.join(self.home, "cache")))
        self.assertFalse(cache_file.startswith(self.workspace))
        self.assertIn(os.path.join("linters", "JAVASCRIPT_ES"), cache_file)
        self.assertTrue(os.path.isdir(os.path.dirname(cache_file)))

    def test_one_folder_per_workspace(self):
        other_workspace = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, other_workspace, True)
        first = build_linter(self.request_id, self.workspace).get_native_cache_dir()
        second = build_linter(self.request_id, other_workspace).get_native_cache_dir()
        self.assertNotEqual(first, second)

    def test_not_sent_in_docker(self):
        config.set(self.request_id, "MEGALINTER_NATIVE", "false")
        linter = build_linter(self.request_id, self.workspace)
        self.assertEqual(linter.get_native_cache_arguments(), [])

    def test_not_sent_without_cache_args(self):
        linter = build_linter(self.request_id, self.workspace, cache_args=[])
        self.assertEqual(linter.get_native_cache_arguments(), [])

    def test_disabled_globally(self):
        config.set(self.request_id, "NATIVE_LINTER_CACHE", "false")
        linter = build_linter(self.request_id, self.workspace)
        self.assertEqual(linter.get_native_cache_arguments(), [])

    def test_disabled_for_one_linter(self):
        config.set(self.request_id, "JAVASCRIPT_ES_NATIVE_CACHE", "false")
        linter = build_linter(self.request_id, self.workspace)
        self.assertEqual(linter.get_native_cache_arguments(), [])

    def test_linter_value_wins_over_global_value(self):
        config.set(self.request_id, "NATIVE_LINTER_CACHE", "false")
        config.set(self.request_id, "JAVASCRIPT_ES_NATIVE_CACHE", "true")
        linter = build_linter(self.request_id, self.workspace)
        self.assertEqual(len(linter.get_native_cache_arguments()), 5)

    def test_user_cache_arguments_win(self):
        for user_args in (["--no-cache"], ["--cache-location=/tmp/x"], ["--cache"]):
            linter = build_linter(self.request_id, self.workspace, user_args=user_args)
            self.assertEqual(linter.get_native_cache_arguments(), [], user_args)


if __name__ == "__main__":
    unittest.main()
