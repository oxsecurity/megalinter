#!/usr/bin/env python3
# Native mode: which of the linters activated by the repository to run on this machine.
# CI keeps running every active linter: NATIVE_LINTERS only scopes the local runs, where
# the slow linters and the ones scanning the whole repository are better left to CI
import json
import os
import shutil

from megalinter.native import selection as native_selection
from megalinter.native.installer import NativeInstaller
from megalinter.native.resolve import spec_from_linter

# A linter taking longer than this on the last run is left to CI
MAX_NATIVE_SECONDS = 10
# Descriptor linter_speed (1 very slow, 5 very fast) up to which a linter is left to CI
MAX_CI_ONLY_SPEED = 2
JSON_REPORT_FILE_NAME = "mega-linter-report.json"


def build_native_linters_suggestion(mega_linter):
    measured = read_measured_seconds(mega_linter.report_folder)
    installer = NativeInstaller(mega_linter.request_id)
    listed = {
        key
        for key in native_selection.configured_native_linters(mega_linter.request_id)
        if key.lower() != native_selection.ALL_KEYWORD
    }
    rows = [
        build_row(linter, installer, measured.get(linter.name), listed)
        for linter in mega_linter.active_linters
    ]
    recommended = sorted(row["key"] for row in rows if row["recommended"])
    if len(recommended) == 0 or recommended == sorted(listed):
        return None
    return {
        "variable": "NATIVE_LINTERS",
        "operation": "set",
        "values": recommended,
        "safe": False,
        "reason": (
            "Only the linters listed in NATIVE_LINTERS run without Docker. The fast linters "
            "are proposed for your machine, and the slow ones or the ones scanning the whole "
            "repository stay in CI, which still runs every active linter"
        ),
        "details": rows,
    }


def build_row(linter, installer, measured_seconds, listed):
    status, status_reason = installer.status(spec_from_linter(linter))
    recommended, reason = recommend(linter, status, status_reason, measured_seconds)
    row = {
        "key": linter.name,
        "recommended": recommended,
        "reason": reason,
        "listed": linter.name in listed,
        "cli_lint_mode": linter.cli_lint_mode,
        "linter_speed": linter.linter_speed,
        "is_formatter": linter.is_formatter,
        "native_status": status,
    }
    if measured_seconds is not None:
        row["measured_seconds"] = measured_seconds
    return row


def recommend(linter, status, status_reason, measured_seconds):
    if status == "unsupported":
        return False, status_reason
    if status == "host-provided" and shutil.which(linter.cli_executable[0]) is None:
        return False, f"{linter.cli_executable[0]} is not installed on this machine"
    if linter.cli_lint_mode == "project":
        return False, "scans the whole repository: better left to CI"
    if measured_seconds is not None:
        if measured_seconds >= MAX_NATIVE_SECONDS:
            return False, f"slow (measured {measured_seconds} s on the last run)"
        return True, f"fast (measured {measured_seconds} s on the last run)"
    if linter.linter_speed <= MAX_CI_ONLY_SPEED:
        return False, f"slow linter (speed {linter.linter_speed}/5)"
    return True, f"not a slow linter (speed {linter.linter_speed}/5)"


# Slowest time of each linter in the reports of the previous runs (full run, standalone runs)
def read_measured_seconds(report_folder):
    measured = {}
    if report_folder is None or not os.path.isdir(report_folder):
        return measured
    candidates = [os.path.join(report_folder, JSON_REPORT_FILE_NAME)] + [
        os.path.join(report_folder, entry, JSON_REPORT_FILE_NAME)
        for entry in sorted(os.listdir(report_folder))
    ]
    for candidate in candidates:
        if not os.path.isfile(candidate):
            continue
        try:
            with open(candidate, "r", encoding="utf-8") as report_file:
                report = json.load(report_file)
        except (OSError, ValueError):
            continue
        for linter in report.get("linters", []):
            key = linter.get("name")
            seconds = linter.get("elapsed_time_s")
            if (
                key is None
                or not isinstance(seconds, (int, float))
                # The first run of an installed linter is far slower than the next ones
                or linter.get("native_first_run") is True
            ):
                continue
            measured[key] = max(measured.get(key, 0), round(seconds, 1))
    return measured


def format_native_rows(details):
    lines = []
    for row in sorted(details, key=lambda item: (not item["recommended"], item["key"])):
        mark = "run natively" if row["recommended"] else "CI only"
        lines.append(f"  {row['key']:<40} {mark}: {row['reason']}")
    return lines


def is_native_suggestion(suggestion):
    return suggestion["variable"] == "NATIVE_LINTERS"
