#!/usr/bin/env python3
# Native mode results cache: the files that a linter found without any problem are
# not linted again by the next runs while they, the configuration and the linter
# stay the same. Only for the linters declaring native_results_cache in their
# descriptor: the ones whose result on a file depends only on its content and on
# the configuration files (none of them reads the other files of the repository)
import hashlib
import json
import logging
import os
import tempfile
import time

from megalinter import config
from megalinter.__about__ import __version__
from megalinter.native.context import cache_dir, megalinter_home

RESULTS_CACHE_FORMAT = 1
# A file modified this recently could be modified again with the same size and
# modification time (coarse file system timestamps): its content is checked next time
RACY_MODIFICATION_NS = 3 * 1_000_000_000


class ResultsCache:
    def __init__(self, linter):
        self.linter = linter
        self.workspace = os.path.abspath(linter.workspace)
        self.cache_file = os.path.join(
            cache_dir(megalinter_home(linter.request_id)),
            "results",
            linter.name,
            hashlib.sha256(self.workspace.encode("utf-8")).hexdigest()[:16] + ".json",
        )
        self.key = self.compute_key()
        self.entries = self.load_entries()
        self.unchanged_files = []
        self.stats_before_run = {}

    # Everything a result depends on, except the content of the linted file
    def compute_key(self):
        linter = self.linter
        install_dir = (
            linter.native_toolchain.install_dir
            if linter.native_toolchain is not None
            else None
        )
        variable_prefixes = (f"{linter.name}_", f"{linter.descriptor_id}_")
        variables = {
            name: value
            for name, value in config.get(linter.request_id).items()
            if name.startswith(variable_prefixes)
        }
        payload = {
            "format": RESULTS_CACHE_FORMAT,
            "megalinter": __version__,
            "linter": linter.name,
            "install_dir": install_dir,
            "linter_version": linter.get_linter_version(),
            "class": type(linter).__name__,
            "cli_lint_mode": linter.cli_lint_mode,
            "apply_fixes": linter.apply_fixes,
            "arguments": [
                linter.cli_executable,
                linter.cli_lint_extra_args,
                linter.cli_lint_user_args,
                linter.cli_config_extra_args,
                linter.cli_lint_extra_args_after,
                linter.cli_lint_mode_file_extra_args_after,
                linter.cli_lint_mode_list_of_files_extra_args_after,
                linter.cli_command_remove_args,
            ],
            "config_file": self.file_digest(linter.config_file),
            "ignore_file": self.file_digest(linter.ignore_file),
            "discovered_config_files": self.discovered_config_files(),
            "variables": variables,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

    # Configuration files the linter finds by itself, in the folder of a linted file
    # or in one of its parents up to the workspace root
    def discovered_config_files(self):
        names = (self.linter.native_results_cache or {}).get("config_files", [])
        if len(names) == 0:
            return []
        folders = {""}
        for file in self.linter.files:
            folder = os.path.dirname(file)
            while folder not in folders:
                folders.add(folder)
                folder = os.path.dirname(folder)
        found = []
        for folder in sorted(folders):
            for name in names:
                path = os.path.join(folder, name)
                if os.path.isfile(self.absolute(path)):
                    found.append([path, self.file_digest(path)])
        return found

    def absolute(self, path):
        return path if os.path.isabs(path) else os.path.join(self.workspace, path)

    def file_digest(self, path):
        if path is None:
            return None
        absolute_path = self.absolute(path)
        if not os.path.isfile(absolute_path):
            return [path, None]
        digest = hashlib.sha256()
        with open(absolute_path, "rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return [path, digest.hexdigest()]

    def file_stat(self, file):
        try:
            stat = os.stat(self.absolute(file))
        except OSError:
            return None
        return [stat.st_size, stat.st_mtime_ns]

    def load_entries(self):
        try:
            with open(self.cache_file, "r", encoding="utf-8") as file:
                content = json.load(file)
        except (OSError, ValueError):
            return {}
        if not isinstance(content, dict) or content.get("key") != self.key:
            return {}
        entries = content.get("files", {})
        return entries if isinstance(entries, dict) else {}

    # A file is unchanged when its size and modification time are the recorded
    # ones, or else when its content has the recorded digest
    def is_unchanged(self, file):
        entry = self.entries.get(file)
        if entry is None:
            return False
        stat = self.file_stat(file)
        if stat is None:
            return False
        if stat == entry[0:2]:
            return True
        digest = self.file_digest(file)[1]
        if digest != entry[2]:
            return False
        self.entries[file] = [*stat, digest]
        return True

    # Splits the files of the linter: the ones to lint, and the unchanged ones
    def select_files_to_lint(self, files):
        self.unchanged_files = [file for file in files if self.is_unchanged(file)]
        unchanged = set(self.unchanged_files)
        files_to_lint = [file for file in files if file not in unchanged]
        for file in files_to_lint:
            self.entries.pop(file, None)
            self.stats_before_run[file] = self.file_stat(file)
        if len(self.unchanged_files) > 0:
            logging.info(
                f"[Results cache] {self.linter.name}: {len(self.unchanged_files)} of "
                f"{len(files)} files are unchanged since they were linted without any "
                "problem: they are not linted again (disable with "
                f"{self.linter.name}_NATIVE_RESULTS_CACHE: false)"
            )
        return files_to_lint

    # Files modified during the run (fixed by a formatter...) are linted again next time
    def record_success(self, files):
        now_ns = time.time_ns()
        for file in files:
            stat = self.file_stat(file)
            if stat is None or stat != self.stats_before_run.get(file):
                continue
            digest = self.file_digest(file)[1]
            if now_ns - stat[1] < RACY_MODIFICATION_NS:
                stat = [stat[0], 0]
            self.entries[file] = [*stat, digest]

    # After a run with problems: when the linter checks every file and names each
    # file with a problem in its output (failed_files_in_output), the files it does
    # not name had none. An output naming no linted file (invalid configuration,
    # crash...) gives no information: nothing is recorded
    def record_files_absent_from_output(self, files, output):
        if self.linter.native_results_cache.get("failed_files_in_output") is not True:
            return
        output = output or ""
        mentioned = {file for file in files if self.is_in_output(file, output)}
        if len(mentioned) == 0:
            return
        self.record_success([file for file in files if file not in mentioned])

    def is_in_output(self, file, output):
        absolute_file = self.absolute(file)
        forms = {file, absolute_file, os.path.normpath(file)}
        forms |= {form.replace("\\", "/") for form in forms}
        forms |= {form.replace("/", "\\") for form in forms}
        return any(form in output for form in forms)

    def save(self):
        folder = os.path.dirname(self.cache_file)
        os.makedirs(folder, mode=0o700, exist_ok=True)
        file_descriptor, temp_file = tempfile.mkstemp(dir=folder, suffix=".tmp")
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as file:
            json.dump({"key": self.key, "files": self.entries}, file)
        os.replace(temp_file, self.cache_file)


def is_results_cache_enabled(linter):
    if (
        linter.native_results_cache is None
        or linter.native_toolchain is None
        or linter.cli_lint_mode not in ("file", "list_of_files")
        or linter.output_sarif is True
    ):
        return False
    linter_value = config.get(
        linter.request_id, f"{linter.name}_NATIVE_RESULTS_CACHE", ""
    )
    if linter_value != "":
        return linter_value == "true"
    return config.get(linter.request_id, "NATIVE_RESULTS_CACHE", "true") == "true"
