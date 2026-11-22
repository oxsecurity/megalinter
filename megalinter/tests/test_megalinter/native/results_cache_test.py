import os
import shutil
import tempfile
import time
import unittest

from megalinter import config
from megalinter.native.results_cache import ResultsCache, is_results_cache_enabled


class FakeToolchain:
    install_dir = "/home/user/.megalinter/linters/PYTHON_FAKE/abc"


class FakeLinter:
    def __init__(self, request_id, workspace, files, results_cache=None):
        self.request_id = request_id
        self.name = "PYTHON_FAKE"
        self.descriptor_id = "PYTHON"
        self.workspace = workspace
        self.files = files
        self.native_toolchain = FakeToolchain()
        self.native_results_cache = (
            {"config_files": ["setup.cfg"], "failed_files_in_output": True}
            if results_cache is None
            else results_cache
        )
        self.cli_lint_mode = "list_of_files"
        self.output_sarif = False
        self.apply_fixes = False
        self.cli_executable = ["fake"]
        self.cli_lint_extra_args = ["--check"]
        self.cli_lint_user_args = []
        self.cli_config_extra_args = []
        self.cli_lint_extra_args_after = []
        self.cli_lint_mode_file_extra_args_after = []
        self.cli_lint_mode_list_of_files_extra_args_after = []
        self.cli_command_remove_args = []
        self.config_file = None
        self.ignore_file = None
        self.linter_version = "1.0.0"

    def get_linter_version(self):
        return self.linter_version


class ResultsCacheTest(unittest.TestCase):
    def setUp(self):
        self.request_id = "test-native-results-cache"
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
        os.makedirs(os.path.join(self.workspace, "src"))
        self.files = ["a.py", "src/b.py", "src/c.py"]
        for file in self.files:
            self.write(file, f"# {file}\n")

    def write(self, file, content):
        with open(os.path.join(self.workspace, file), "w", encoding="utf-8") as f:
            f.write(content)

    def linter(self, **kwargs):
        return FakeLinter(self.request_id, self.workspace, list(self.files), **kwargs)

    # Simulates a successful run of the linter on the files it selects
    def run_success(self, linter):
        cache = ResultsCache(linter)
        files_to_lint = cache.select_files_to_lint(linter.files)
        cache.record_success(files_to_lint)
        cache.save()
        return files_to_lint

    def files_to_lint(self, linter):
        return ResultsCache(linter).select_files_to_lint(linter.files)

    def test_unchanged_files_are_not_linted_again(self):
        self.assertEqual(self.run_success(self.linter()), self.files)
        self.assertEqual(self.files_to_lint(self.linter()), [])

    def test_modified_file_is_linted_again(self):
        self.run_success(self.linter())
        self.write("src/b.py", "x = 1  # longer content\n")
        self.assertEqual(self.files_to_lint(self.linter()), ["src/b.py"])

    def test_same_content_with_new_modification_time_is_unchanged(self):
        self.run_success(self.linter())
        path = os.path.join(self.workspace, "a.py")
        later = time.time() + 100
        os.utime(path, (later, later))
        self.assertEqual(self.files_to_lint(self.linter()), [])

    def test_same_size_and_new_content_is_linted_again(self):
        self.run_success(self.linter())
        self.write("a.py", "# A.PY\n")
        self.assertEqual(self.files_to_lint(self.linter()), ["a.py"])

    def test_recent_modification_is_checked_by_content(self):
        # Coarse file system timestamps: same size and same modification time
        path = os.path.join(self.workspace, "a.py")
        self.run_success(self.linter())
        stat = os.stat(path)
        self.write("a.py", "# A.PY\n")
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(self.files_to_lint(self.linter()), ["a.py"])

    def test_old_files_are_trusted_by_size_and_modification_time(self):
        path = os.path.join(self.workspace, "a.py")
        past = time.time() - 3600
        os.utime(path, (past, past))
        self.run_success(self.linter())
        cache = ResultsCache(self.linter())
        self.assertEqual(cache.entries["a.py"][1], os.stat(path).st_mtime_ns)

    def test_linter_version_invalidates(self):
        self.run_success(self.linter())
        linter = self.linter()
        linter.linter_version = "2.0.0"
        self.assertEqual(self.files_to_lint(linter), self.files)

    def test_arguments_invalidate(self):
        self.run_success(self.linter())
        linter = self.linter()
        linter.cli_lint_user_args = ["--strict"]
        self.assertEqual(self.files_to_lint(linter), self.files)

    def test_linter_variables_invalidate(self):
        self.run_success(self.linter())
        config.set(self.request_id, "PYTHON_FAKE_FILTER_REGEX_EXCLUDE", "x")
        self.assertEqual(self.files_to_lint(self.linter()), self.files)

    def test_other_linters_variables_do_not_invalidate(self):
        self.run_success(self.linter())
        config.set(self.request_id, "MARKDOWN_MARKDOWNLINT_ARGUMENTS", "--fix")
        self.assertEqual(self.files_to_lint(self.linter()), [])

    def test_config_file_content_invalidates(self):
        self.write("config.toml", "a = 1\n")
        linter = self.linter()
        linter.config_file = "config.toml"
        self.run_success(linter)
        self.write("config.toml", "a = 2\n")
        linter = self.linter()
        linter.config_file = "config.toml"
        self.assertEqual(self.files_to_lint(linter), self.files)

    def test_discovered_config_file_in_parent_folder_invalidates(self):
        self.run_success(self.linter())
        self.write("src/setup.cfg", "[flake8]\n")
        self.assertEqual(self.files_to_lint(self.linter()), self.files)

    def test_files_modified_during_the_run_are_not_recorded(self):
        linter = self.linter()
        cache = ResultsCache(linter)
        files_to_lint = cache.select_files_to_lint(linter.files)
        self.write("a.py", "fixed = True  # by a formatter\n")
        cache.record_success(files_to_lint)
        cache.save()
        self.assertEqual(self.files_to_lint(self.linter()), ["a.py"])

    def test_files_absent_from_output_of_a_failed_run_are_recorded(self):
        linter = self.linter()
        cache = ResultsCache(linter)
        files_to_lint = cache.select_files_to_lint(linter.files)
        cache.record_files_absent_from_output(
            files_to_lint, "src/b.py:1:1: E999 problem\n"
        )
        cache.save()
        self.assertEqual(self.files_to_lint(self.linter()), ["src/b.py"])

    def test_absolute_paths_in_output_are_found(self):
        linter = self.linter()
        cache = ResultsCache(linter)
        files_to_lint = cache.select_files_to_lint(linter.files)
        output = f"would reformat {os.path.join(self.workspace, 'src', 'c.py')}\n"
        cache.record_files_absent_from_output(files_to_lint, output)
        cache.save()
        self.assertEqual(self.files_to_lint(self.linter()), ["src/c.py"])

    def test_output_naming_no_file_records_nothing(self):
        linter = self.linter()
        cache = ResultsCache(linter)
        files_to_lint = cache.select_files_to_lint(linter.files)
        cache.record_files_absent_from_output(files_to_lint, "Invalid configuration")
        cache.save()
        self.assertEqual(self.files_to_lint(self.linter()), self.files)

    def test_failed_run_records_nothing_without_failed_files_in_output(self):
        linter = self.linter(results_cache={})
        cache = ResultsCache(linter)
        files_to_lint = cache.select_files_to_lint(linter.files)
        cache.record_files_absent_from_output(files_to_lint, "src/b.py: problem")
        cache.save()
        self.assertEqual(self.files_to_lint(self.linter(results_cache={})), self.files)

    def test_cache_is_stored_outside_the_workspace(self):
        cache = ResultsCache(self.linter())
        self.assertTrue(cache.cache_file.startswith(self.home))

    def test_activation(self):
        self.assertTrue(is_results_cache_enabled(self.linter()))
        self.assertTrue(is_results_cache_enabled(self.linter(results_cache={})))
        linter = self.linter()
        linter.native_results_cache = None
        self.assertFalse(is_results_cache_enabled(linter))
        linter = self.linter()
        linter.native_toolchain = None
        self.assertFalse(is_results_cache_enabled(linter), "Docker")
        linter = self.linter()
        linter.cli_lint_mode = "project"
        self.assertFalse(is_results_cache_enabled(linter))
        linter = self.linter()
        linter.output_sarif = True
        self.assertFalse(is_results_cache_enabled(linter))
        config.set(self.request_id, "NATIVE_RESULTS_CACHE", "false")
        self.assertFalse(is_results_cache_enabled(self.linter()))
        config.set(self.request_id, "PYTHON_FAKE_NATIVE_RESULTS_CACHE", "true")
        self.assertTrue(is_results_cache_enabled(self.linter()))


if __name__ == "__main__":
    unittest.main()
