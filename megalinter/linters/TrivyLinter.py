#!/usr/bin/env python3
"""
Use Trivy to check for vulnerabilities
"""

import logging
import os
import time

import yaml
from megalinter import Linter, config

# Errors returned by the registries hosting the trivy databases when they are
# rate-limiting us or temporarily unavailable. They are transient: retrying,
# or trying another mirror, can fix them
DB_DOWNLOAD_ERRORS = [
    "TOOMANYREQUESTS",
    "failed to download Java DB",
    "BLOB_UNKNOWN",
    "failed to download vulnerability DB",
]

# Only an aborted run is worth retrying: a registry error while fetching the
# optional misconfiguration checks bundle just makes trivy fall back to its
# embedded checks, and the scan results are complete
FATAL_ERROR_MARKER = "FATAL"

# Trivy tries these repositories in order and stops at the first one answering.
# Its own defaults are mirror.gcr.io + ghcr.io: public.ecr.aws is the third
# official mirror, added here because ghcr.io rate-limits per organization and
# a flag value REPLACES the trivy defaults instead of extending them
DEFAULT_DB_REPOSITORIES = [
    "mirror.gcr.io/aquasec/trivy-db:2",
    "ghcr.io/aquasecurity/trivy-db:2",
    "public.ecr.aws/aquasecurity/trivy-db:2",
]
DEFAULT_JAVA_DB_REPOSITORIES = [
    "mirror.gcr.io/aquasec/trivy-java-db:1",
    "ghcr.io/aquasecurity/trivy-java-db:1",
    "public.ecr.aws/aquasecurity/trivy-java-db:1",
]

DB_REPOSITORY_ARGS = [
    (
        "--db-repository",
        "DB_REPOSITORIES",
        "TRIVY_DB_REPOSITORY",
        "db.repository",
        DEFAULT_DB_REPOSITORIES,
    ),
    (
        "--java-db-repository",
        "JAVA_DB_REPOSITORIES",
        "TRIVY_JAVA_DB_REPOSITORY",
        "db.java-repository",
        DEFAULT_JAVA_DB_REPOSITORIES,
    ),
]

# Trivy refuses --skip-db-update when either of these files is missing from
# its cache directory: "the first run cannot skip downloading DB"
DB_REQUIRED_FILES = [
    os.path.join("db", "trivy.db"),
    os.path.join("db", "metadata.json"),
]

# Cache directory used to download the database while building the MegaLinter
# docker image (HOME is /root at build time). The runtime HOME can be
# different (GitHub Actions forces HOME=/github/home in container actions),
# which makes trivy ignore the database shipped within the image
IMAGE_CACHE_DIR = "/root/.cache/trivy"

DEFAULT_RETRY_ATTEMPTS = 5
DEFAULT_RETRY_INITIAL_DELAY = 10
DEFAULT_RETRY_MAX_DELAY = 60


class TrivyLinter(Linter):

    def build_lint_command(self, file=None) -> list:
        cmd = super().build_lint_command(file)
        return self.add_db_repository_arguments(cmd)

    # Send trivy to all known database mirrors, unless the user configured
    # their own repositories through arguments, environment or config file
    def add_db_repository_arguments(self, cmd):
        for (
            arg_name,
            config_key,
            trivy_env_var,
            config_file_key,
            default_repositories,
        ) in DB_REPOSITORY_ARGS:
            if arg_name in cmd:
                continue
            if config.get(self.request_id, trivy_env_var, "") != "":
                continue
            if self.get_config_file_value(config_file_key) is not None:
                continue
            repositories = config.get_list(
                self.request_id, f"{self.name}_{config_key}", default_repositories
            )
            if len(repositories) == 0:
                continue
            cmd += [arg_name, ",".join(repositories)]
        return cmd

    # Value of a dotted key path in the trivy configuration file, or None
    def get_config_file_value(self, config_file_key):
        if self.final_config_file is None or not os.path.isfile(self.final_config_file):
            return None
        with open(self.final_config_file, encoding="utf-8") as config_file:
            node = yaml.safe_load(config_file) or {}
        for key in config_file_key.split("."):
            if not isinstance(node, dict) or key not in node:
                return None
            node = node[key]
        return node

    # Cache directories where a previously downloaded database can be found,
    # the first one being the directory trivy uses for this run
    def get_trivy_cache_dirs(self, command):
        candidates = []
        if isinstance(command, list) and "--cache-dir" in command:
            candidates.append(command[command.index("--cache-dir") + 1])
        candidates.append(self.get_config_file_value("cache.dir"))
        candidates.append(config.get(self.request_id, "TRIVY_CACHE_DIR", ""))
        xdg_cache_home = config.get(self.request_id, "XDG_CACHE_HOME", "")
        if xdg_cache_home != "":
            candidates.append(os.path.join(xdg_cache_home, "trivy"))
        home_dir = config.get(self.request_id, "HOME", "")
        if home_dir != "":
            candidates.append(os.path.join(home_dir, ".cache", "trivy"))
        # Database shipped within the MegaLinter docker image
        candidates.append(IMAGE_CACHE_DIR)
        cache_dirs = []
        for candidate in candidates:
            if candidate and candidate not in cache_dirs:
                cache_dirs.append(candidate)
        return cache_dirs

    # Cache directory containing a database usable with --skip-db-update, or None
    def find_cached_db_dir(self, command):
        for cache_dir in self.get_trivy_cache_dirs(command):
            if all(
                os.path.isfile(os.path.join(cache_dir, db_file))
                for db_file in DB_REQUIRED_FILES
            ):
                return cache_dir
        return None

    # Registry rate limits are counted per minute: space the retries so they
    # do not all land within the same rate limit window
    def get_retry_delay(self, attempt):
        initial_delay = float(
            config.get(
                self.request_id,
                f"{self.name}_DB_RETRY_INITIAL_DELAY",
                DEFAULT_RETRY_INITIAL_DELAY,
            )
        )
        max_delay = float(
            config.get(
                self.request_id,
                f"{self.name}_DB_RETRY_MAX_DELAY",
                DEFAULT_RETRY_MAX_DELAY,
            )
        )
        return min(initial_delay * (2**attempt), max_delay)

    # Command running trivy against an already downloaded database
    def build_offline_command(self, command, cached_db_dir):
        offline_args = ["--skip-db-update", "--skip-check-update"]
        if cached_db_dir != self.get_trivy_cache_dirs(command)[0]:
            offline_args += ["--cache-dir", cached_db_dir]
        if isinstance(command, str):
            return command + " " + " ".join(offline_args)
        return command + offline_args

    def is_db_download_error(self, return_output):
        return_output = return_output or ""
        if FATAL_ERROR_MARKER not in return_output:
            return False
        return any(error in return_output for error in DB_DOWNLOAD_ERRORS)

    # Run trivy without letting the base class report the common linter errors:
    # their resolution guidance is only relevant once every attempt is over
    def execute_trivy_command(self, command):
        common_linter_errors = self.common_linter_errors
        self.common_linter_errors = []
        try:
            return super().execute_lint_command(command)
        finally:
            self.common_linter_errors = common_linter_errors

    def execute_lint_command(self, command):
        max_retries = int(
            config.get(
                self.request_id,
                f"{self.name}_DB_RETRY_ATTEMPTS",
                DEFAULT_RETRY_ATTEMPTS,
            )
        )
        return_code, return_output = self.execute_trivy_command(command)
        attempt = 0
        while attempt < max_retries - 1 and self.is_db_download_error(return_output):
            delay = self.get_retry_delay(attempt)
            logging.info(
                f"[{self.linter_name}] Vulnerability database download failed "
                "(registry rate limit or outage): waiting "
                f"{delay:.0f}s before attempt {attempt + 2}/{max_retries}"
            )
            time.sleep(delay)
            return_code, return_output = self.execute_trivy_command(command)
            attempt += 1
        if self.is_db_download_error(return_output):
            # Last chance: run against a database downloaded by a previous run
            # or shipped within the MegaLinter docker image
            cached_db_dir = self.find_cached_db_dir(command)
            if cached_db_dir is None:
                logging.error(
                    f"[{self.linter_name}] Unable to download the vulnerability "
                    f"database after {max_retries} attempts, and no previously "
                    "downloaded database is available to fall back on: trivy can not "
                    f"run offline on its first run. Raise {self.name}_DB_RETRY_ATTEMPTS,"
                    f" set {self.name}_DB_REPOSITORIES to a mirror you control, or "
                    "persist the trivy cache directory (TRIVY_CACHE_DIR) between your "
                    "CI runs."
                )
            else:
                logging.warning(
                    f"[{self.linter_name}] Unable to download the vulnerability "
                    f"database after {max_retries} attempts: running against the "
                    f"database cached in {cached_db_dir}, whose content may be outdated"
                )
                return_code, return_output = self.execute_trivy_command(
                    self.build_offline_command(command, cached_db_dir)
                )
        return self.apply_common_linter_errors(return_code, return_output)

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_TRIVY_FILE_NAMES_REGEX", ["package.*json"]
            )
