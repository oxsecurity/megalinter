#!/usr/bin/env python3
"""
Unit tests for TrivyLinter vulnerability database download resilience:
mirror repositories, spaced retries, and offline fallback only when a
database has already been downloaded.
"""

import os
import tempfile
import unittest
import uuid
from unittest import mock

from megalinter import Linter, config
from megalinter.linters.TrivyLinter import (
    DEFAULT_DB_REPOSITORIES,
    DEFAULT_JAVA_DB_REPOSITORIES,
    DEFAULT_RETRY_ATTEMPTS,
    TrivyLinter,
)

RATE_LIMITED_OUTPUT = (
    "FATAL Fatal error init error: DB error: failed to download vulnerability DB: "
    "OCI repository error: 1 error occurred: failed to fetch the layer: "
    "GET https://ghcr.io/v2/aquasecurity/trivy-db/manifests/2: TOOMANYREQUESTS"
)
SUCCESS_OUTPUT = "Total: 0 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0)"
# The misconfiguration checks bundle is optional: trivy logs the registry error
# then falls back to its embedded checks and completes the scan
CHECKS_BUNDLE_ERROR_OUTPUT = (
    "ERROR [misconf] Falling back to embedded checks err=failed to download "
    "checks bundle: TOOMANYREQUESTS\n"
    "Total: 1 (UNKNOWN: 0, LOW: 1, MEDIUM: 0, HIGH: 0, CRITICAL: 0)"
)


def make_linter(request_id, name="REPOSITORY_TRIVY", config_file=None):
    linter = TrivyLinter.__new__(TrivyLinter)
    linter.request_id = request_id
    linter.name = name
    linter.linter_name = "trivy"
    linter.final_config_file = config_file
    linter.common_linter_errors = []
    return linter


def cache_dir_with_db(root):
    db_dir = os.path.join(root, "db")
    os.makedirs(db_dir, exist_ok=True)
    for db_file in ["trivy.db", "metadata.json"]:
        with open(os.path.join(db_dir, db_file), "w", encoding="utf-8") as file_handler:
            file_handler.write("{}")
    return root


class TrivyLinterDbRepositoriesTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.set_config(self.request_id, {})

    def tearDown(self):
        config.delete(self.request_id)

    def test_mirrors_added_by_default(self):
        linter = make_linter(self.request_id)
        cmd = linter.add_db_repository_arguments(["trivy", "fs", "."])
        self.assertEqual(
            cmd[cmd.index("--db-repository") + 1], ",".join(DEFAULT_DB_REPOSITORIES)
        )
        self.assertEqual(
            cmd[cmd.index("--java-db-repository") + 1],
            ",".join(DEFAULT_JAVA_DB_REPOSITORIES),
        )
        # Setting the flag replaces the trivy defaults: they must be kept
        self.assertIn("ghcr.io/aquasecurity/trivy-db:2", DEFAULT_DB_REPOSITORIES)
        self.assertIn("mirror.gcr.io/aquasec/trivy-db:2", DEFAULT_DB_REPOSITORIES)

    def test_mirrors_not_added_when_user_defined_in_arguments(self):
        linter = make_linter(self.request_id)
        cmd = linter.add_db_repository_arguments(
            ["trivy", "fs", "--db-repository", "my.registry/trivy-db:2", "."]
        )
        self.assertEqual(cmd.count("--db-repository"), 1)
        self.assertEqual(
            cmd[cmd.index("--db-repository") + 1], "my.registry/trivy-db:2"
        )

    def test_mirrors_not_added_when_trivy_env_var_is_set(self):
        config.set_value(
            self.request_id, "TRIVY_DB_REPOSITORY", "my.registry/trivy-db:2"
        )
        linter = make_linter(self.request_id)
        cmd = linter.add_db_repository_arguments(["trivy", "fs", "."])
        self.assertNotIn("--db-repository", cmd)
        # The java database repository is still defaulted to the mirrors
        self.assertIn("--java-db-repository", cmd)

    def test_mirrors_not_added_when_defined_in_trivy_config_file(self):
        with tempfile.TemporaryDirectory() as workspace:
            config_file = os.path.join(workspace, "trivy.yaml")
            with open(config_file, "w", encoding="utf-8") as file_handler:
                file_handler.write("db:\n  repository:\n    - my.registry/trivy-db:2\n")
            linter = make_linter(self.request_id, config_file=config_file)
            cmd = linter.add_db_repository_arguments(["trivy", "fs", "."])
            self.assertNotIn("--db-repository", cmd)
            self.assertIn("--java-db-repository", cmd)

    def test_mirrors_can_be_disabled(self):
        config.set_value(self.request_id, "REPOSITORY_TRIVY_DB_REPOSITORIES", "")
        config.set_value(self.request_id, "REPOSITORY_TRIVY_JAVA_DB_REPOSITORIES", "")
        linter = make_linter(self.request_id)
        cmd = linter.add_db_repository_arguments(["trivy", "fs", "."])
        self.assertEqual(cmd, ["trivy", "fs", "."])

    def test_mirrors_can_be_overridden(self):
        config.set_value(
            self.request_id,
            "REPOSITORY_TRIVY_DB_REPOSITORIES",
            ["registry1/trivy-db:2", "registry2/trivy-db:2"],
        )
        linter = make_linter(self.request_id)
        cmd = linter.add_db_repository_arguments(["trivy", "fs", "."])
        self.assertEqual(
            cmd[cmd.index("--db-repository") + 1],
            "registry1/trivy-db:2,registry2/trivy-db:2",
        )

    def test_sbom_linter_uses_its_own_configuration_keys(self):
        config.set_value(
            self.request_id, "REPOSITORY_TRIVY_SBOM_DB_REPOSITORIES", "sbom/trivy-db:2"
        )
        linter = make_linter(self.request_id, name="REPOSITORY_TRIVY_SBOM")
        cmd = linter.add_db_repository_arguments(["trivy", "fs", "."])
        self.assertEqual(cmd[cmd.index("--db-repository") + 1], "sbom/trivy-db:2")


class TrivyLinterCacheTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.set_config(self.request_id, {})

    def tearDown(self):
        config.delete(self.request_id)

    def test_cached_db_found_in_trivy_cache_dir(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            cache_dir_with_db(cache_dir)
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", cache_dir)
            linter = make_linter(self.request_id)
            self.assertEqual(linter.find_cached_db_dir(["trivy", "fs", "."]), cache_dir)

    def test_cached_db_found_from_cache_dir_argument(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            cache_dir_with_db(cache_dir)
            linter = make_linter(self.request_id)
            command = ["trivy", "fs", "--cache-dir", cache_dir, "."]
            self.assertEqual(linter.find_cached_db_dir(command), cache_dir)

    def test_cached_db_found_in_home_cache_dir(self):
        with tempfile.TemporaryDirectory() as home_dir:
            cache_dir_with_db(os.path.join(home_dir, ".cache", "trivy"))
            config.set_value(self.request_id, "HOME", home_dir)
            linter = make_linter(self.request_id)
            self.assertEqual(
                linter.find_cached_db_dir(["trivy", "fs", "."]),
                os.path.join(home_dir, ".cache", "trivy"),
            )

    def test_no_cached_db_when_metadata_is_missing(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            cache_dir_with_db(cache_dir)
            os.remove(os.path.join(cache_dir, "db", "metadata.json"))
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", cache_dir)
            config.set_value(self.request_id, "HOME", cache_dir)
            config.set_value(self.request_id, "XDG_CACHE_HOME", cache_dir)
            linter = make_linter(self.request_id)
            # /root/.cache/trivy is the last candidate and does not exist here
            self.assertIsNone(linter.find_cached_db_dir(["trivy", "fs", "."]))

    def test_offline_command_adds_skip_arguments(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            cache_dir_with_db(cache_dir)
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", cache_dir)
            linter = make_linter(self.request_id)
            cmd = linter.build_offline_command(["trivy", "fs", "."], cache_dir)
            self.assertEqual(
                cmd, ["trivy", "fs", ".", "--skip-db-update", "--skip-check-update"]
            )

    def test_offline_command_points_to_the_cache_dir_of_the_found_database(self):
        with tempfile.TemporaryDirectory() as workspace:
            image_cache_dir = cache_dir_with_db(os.path.join(workspace, "image-cache"))
            config.set_value(
                self.request_id, "TRIVY_CACHE_DIR", os.path.join(workspace, "empty")
            )
            linter = make_linter(self.request_id)
            cmd = linter.build_offline_command(["trivy", "fs", "."], image_cache_dir)
            self.assertEqual(cmd[-2:], ["--cache-dir", image_cache_dir])


class TrivyLinterRetryTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.set_config(self.request_id, {})

    def tearDown(self):
        config.delete(self.request_id)

    # Replace Linter.execute_lint_command, which spawns a real process, by a
    # stub returning the given outputs, and neutralize the retry waits
    def run_lint(self, outputs, command=None, common_linter_errors=None):
        if command is None:
            command = ["trivy", "fs", "."]
        results = list(outputs)
        executed_commands = []

        def fake_execute(_self, cmd):
            executed_commands.append(cmd)
            return 1, results.pop(0) if len(results) > 1 else results[0]

        linter = make_linter(self.request_id)
        linter.common_linter_errors = common_linter_errors or []
        with (
            mock.patch.object(Linter, "execute_lint_command", fake_execute),
            mock.patch("megalinter.linters.TrivyLinter.time.sleep") as sleep_mock,
        ):
            return_code, return_output = linter.execute_lint_command(command)
        delays = [call.args[0] for call in sleep_mock.call_args_list]
        return executed_commands, delays, return_code, return_output

    def test_no_retry_and_no_wait_when_command_succeeds(self):
        executed_commands, delays, _, _ = self.run_lint([SUCCESS_OUTPUT])
        self.assertEqual(len(executed_commands), 1)
        self.assertEqual(delays, [])

    def test_no_retry_on_a_regular_vulnerability_finding(self):
        executed_commands, delays, _, _ = self.run_lint(
            ["Total: 3 (UNKNOWN: 0, LOW: 1, MEDIUM: 2, HIGH: 0, CRITICAL: 0)"]
        )
        self.assertEqual(len(executed_commands), 1)
        self.assertEqual(delays, [])

    def test_no_retry_when_only_the_checks_bundle_download_failed(self):
        # The scan completed: retrying would waste minutes for nothing
        executed_commands, delays, _, _ = self.run_lint([CHECKS_BUNDLE_ERROR_OUTPUT])
        self.assertEqual(len(executed_commands), 1)
        self.assertEqual(delays, [])

    def test_retries_then_succeeds(self):
        executed_commands, delays, _, return_output = self.run_lint(
            [RATE_LIMITED_OUTPUT, SUCCESS_OUTPUT]
        )
        self.assertEqual(len(executed_commands), 2)
        self.assertEqual(delays, [10.0])
        self.assertNotIn("TOOMANYREQUESTS", return_output)

    def test_retries_are_spaced_over_more_than_one_rate_limit_window(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", empty_dir)
            config.set_value(self.request_id, "HOME", empty_dir)
            _, delays, _, _ = self.run_lint([RATE_LIMITED_OUTPUT])
        self.assertEqual(delays, [10.0, 20.0, 40.0, 60.0])
        self.assertGreater(sum(delays), 60)

    def test_retry_delays_are_configurable(self):
        config.set_value(self.request_id, "REPOSITORY_TRIVY_DB_RETRY_ATTEMPTS", "3")
        config.set_value(
            self.request_id, "REPOSITORY_TRIVY_DB_RETRY_INITIAL_DELAY", "2"
        )
        config.set_value(self.request_id, "REPOSITORY_TRIVY_DB_RETRY_MAX_DELAY", "3")
        with tempfile.TemporaryDirectory() as empty_dir:
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", empty_dir)
            config.set_value(self.request_id, "HOME", empty_dir)
            executed_commands, delays, _, _ = self.run_lint([RATE_LIMITED_OUTPUT])
        self.assertEqual(len(executed_commands), 3)
        self.assertEqual(delays, [2.0, 3.0])

    def test_offline_fallback_when_a_database_is_cached(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            cache_dir_with_db(cache_dir)
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", cache_dir)
            executed_commands, _, _, _ = self.run_lint([RATE_LIMITED_OUTPUT])
        self.assertEqual(len(executed_commands), DEFAULT_RETRY_ATTEMPTS + 1)
        self.assertIn("--skip-db-update", executed_commands[-1])
        self.assertIn("--skip-check-update", executed_commands[-1])

    def test_resolution_guidance_is_reported_only_once(self):
        common_linter_errors = [
            {
                "identifier": "REPOSITORY_TRIVY_ERROR_TOOMANYREQUESTS",
                "regex": "TOOMANYREQUESTS",
                "message": "Rate limited by the registry",
            }
        ]
        with tempfile.TemporaryDirectory() as empty_dir:
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", empty_dir)
            config.set_value(self.request_id, "HOME", empty_dir)
            _, _, _, return_output = self.run_lint(
                [RATE_LIMITED_OUTPUT], common_linter_errors=common_linter_errors
            )
        self.assertEqual(return_output.count("Rate limited by the registry"), 1)

    def test_no_offline_fallback_on_a_first_run(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            config.set_value(self.request_id, "TRIVY_CACHE_DIR", empty_dir)
            config.set_value(self.request_id, "HOME", empty_dir)
            config.set_value(self.request_id, "XDG_CACHE_HOME", empty_dir)
            executed_commands, _, _, return_output = self.run_lint(
                [RATE_LIMITED_OUTPUT]
            )
        # An extra --skip-db-update run would be fatal without a database
        self.assertEqual(len(executed_commands), DEFAULT_RETRY_ATTEMPTS)
        for command in executed_commands:
            self.assertNotIn("--skip-db-update", command)
        self.assertIn("TOOMANYREQUESTS", return_output)


if __name__ == "__main__":
    unittest.main()
