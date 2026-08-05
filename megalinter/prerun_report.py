#!/usr/bin/env python3
"""
Prerun analysis mode: identify active linters and collected files, then suggest
configuration improvements (directory exclusions, flavor) without running any linter.
Activated with the MEGALINTER_PRERUN=true environment variable (mega-linter-runner --prerun)
"""

import json
import logging
import os

from megalinter import config, flavor_factory, utils
from megalinter.constants import ML_DOC_URL
from megalinter.utils_reporter import log_section_end, log_section_start

PRERUN_REPORT_FILE_NAME = "prerun-report.json"

# Directory names that usually contain generated or vendored content.
# When they still hold lintable files, suggest their exclusion but flag it
# as not safe: the user must confirm they are not sources
KNOWN_GENERATED_DIR_NAMES = [
    "_site",
    ".cache",
    ".docusaurus",
    ".gradle",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".tox",
    "build",
    "coverage",
    "DerivedData",
    "dist",
    "htmlcov",
    "out",
    "Pods",
    "site",
    "storybook-static",
    "target",
    "temp",
    "tmp",
    "vendor",
]

# Below this number of files, excluding a directory is not worth a suggestion
MIN_FILES_FOR_SUGGESTION = 20

# Do not list more than this number of directories in a single suggestion
MAX_SUGGESTED_DIRS = 10


def count_files_by_top_level_dir(files):
    counts: dict[str, int] = {}
    whole_ignored_dirs: set[str] = set()
    for file in files:
        file = file.replace("\\", "/")
        if "/" not in file:
            continue
        top_level_dir = file.split("/")[0]
        counts[top_level_dir] = counts.get(top_level_dir, 0) + 1
        # list_git_ignored_files() returns fully ignored directories as "dir/**"
        if file == top_level_dir + "/**":
            whole_ignored_dirs.add(top_level_dir)
    return counts, whole_ignored_dirs


def build_gitignored_dirs_suggestion(mega_linter, excluded_dirs, kept_by_dir):
    ignored_by_dir, whole_ignored_dirs = count_files_by_top_level_dir(
        mega_linter.ignored_files
    )
    candidates = []
    for directory, ignored_count in sorted(
        ignored_by_dir.items(), key=lambda item: item[1], reverse=True
    ):
        if directory in excluded_dirs:
            continue
        if kept_by_dir.get(directory, 0) > 0:
            # Some files of this directory are lintable: excluding it would
            # change the linting scope, so it can not be suggested safely
            continue
        if ignored_count >= MIN_FILES_FOR_SUGGESTION or directory in whole_ignored_dirs:
            candidates += [
                {
                    "directory": directory,
                    "gitignored_files": ignored_count,
                    "kept_files": 0,
                }
            ]
    if len(candidates) == 0:
        return None
    candidates = candidates[0:MAX_SUGGESTED_DIRS]
    dir_names = [candidate["directory"] for candidate in candidates]
    return {
        "variable": "ADDITIONAL_EXCLUDED_DIRECTORIES",
        "operation": "append",
        "values": dir_names,
        "safe": True,
        "reason": (
            "These top-level directories contain only .gitignored files, so excluding "
            "them does not change the linting scope. It speeds up file collection, and "
            "the exclusions are also forwarded to project-mode linters (checkov, "
            "trivy, grype, secret scanners...) that would otherwise scan these "
            f"folders entirely. See {ML_DOC_URL}/config-filtering/"
        ),
        "details": candidates,
    }


def build_generated_dirs_suggestion(mega_linter, excluded_dirs, kept_by_dir):
    candidates = []
    for dir_name in KNOWN_GENERATED_DIR_NAMES:
        if dir_name in excluded_dirs:
            continue
        kept_count = kept_by_dir.get(dir_name, 0)
        if kept_count < MIN_FILES_FOR_SUGGESTION:
            continue
        if not os.path.isdir(mega_linter.workspace + os.path.sep + dir_name):
            continue
        candidates += [{"directory": dir_name, "kept_files": kept_count}]
    if len(candidates) == 0:
        return None
    candidates = sorted(
        candidates, key=lambda candidate: candidate["kept_files"], reverse=True
    )[0:MAX_SUGGESTED_DIRS]
    dir_names = [candidate["directory"] for candidate in candidates]
    return {
        "variable": "ADDITIONAL_EXCLUDED_DIRECTORIES",
        "operation": "append",
        "values": dir_names,
        "safe": False,
        "reason": (
            "These directory names usually contain generated or vendored content, but "
            "they still hold files that MegaLinter would lint. If they are build "
            "outputs (not sources), excluding them speeds up linting and avoids "
            "false positives on generated files. Confirm before applying: excluding "
            "a directory containing sources would remove it from the linting scope. "
            f"See {ML_DOC_URL}/config-filtering/"
        ),
        "details": candidates,
    }


def build_flavor_suggestion(mega_linter):
    if (
        config.get(mega_linter.request_id, "FLAVOR_SUGGESTIONS", "true") != "true"
        or flavor_factory.is_custom_flavor()
    ):
        return None
    flavor_suggestions = flavor_factory.get_megalinter_flavor_suggestions(
        mega_linter.active_linters
    )
    matching_flavors = [
        {
            "flavor": suggestion["flavor"],
            "linters_number": suggestion["linters_number"],
        }
        for suggestion in flavor_suggestions
        if "flavor" in suggestion
    ]
    if len(matching_flavors) == 0:
        return None
    return {
        "variable": "MEGALINTER_FLAVOR",
        "operation": "set",
        "values": [matching_flavors[0]["flavor"]],
        "safe": False,
        "reason": (
            "All your active linters are available in smaller MegaLinter flavors, "
            "whose Docker images are faster to pull and start. Also update the "
            "Docker image or GitHub Action reference in your CI workflow files. "
            f"See {ML_DOC_URL}/flavors/"
        ),
        "details": matching_flavors,
    }


def build_prerun_report(mega_linter):
    request_id = mega_linter.request_id
    excluded_dirs = utils.get_excluded_directories(request_id)
    kept_by_dir, _ = count_files_by_top_level_dir(mega_linter.kept_files)
    suggestions = []
    for suggestion in [
        build_gitignored_dirs_suggestion(mega_linter, excluded_dirs, kept_by_dir),
        build_generated_dirs_suggestion(mega_linter, excluded_dirs, kept_by_dir),
        build_flavor_suggestion(mega_linter),
    ]:
        if suggestion is not None:
            suggestions += [suggestion]
    report = {
        "mode": "prerun",
        "flavor": mega_linter.megalinter_flavor,
        "files": {
            "found": mega_linter.found_files_count,
            "kept": len(mega_linter.kept_files),
            "gitignored": len(mega_linter.ignored_files),
        },
        "active_linters": [
            {
                "key": linter.name,
                "descriptor": linter.descriptor_id,
                "linter": linter.linter_name,
                "cli_lint_mode": linter.cli_lint_mode,
                "files_count": (
                    None if linter.cli_lint_mode == "project" else len(linter.files)
                ),
            }
            for linter in mega_linter.active_linters
        ],
        "suggestions": suggestions,
    }
    return report


def write_prerun_report(mega_linter, report):
    os.makedirs(mega_linter.report_folder, exist_ok=True)
    report_file = mega_linter.report_folder + os.path.sep + PRERUN_REPORT_FILE_NAME
    with open(report_file, "w", encoding="utf-8") as json_file:
        json.dump(report, json_file, indent=2, sort_keys=True)
    return report_file


def log_prerun_report(report, report_file):
    logging.info(
        log_section_start(
            "megalinter-prerun",
            "MegaLinter prerun analysis (no linter has been run)",
        )
    )
    files_info = report["files"]
    logging.info(
        f"- Active linters: {len(report['active_linters'])}"
        + f" | Files: kept {files_info['kept']} of {files_info['found']} found"
        + f" ({files_info['gitignored']} gitignored)"
    )
    if len(report["suggestions"]) == 0:
        logging.info(
            "No configuration improvement identified: "
            "your configuration looks efficient."
        )
    else:
        logging.info("Configuration suggestions to improve performances:")
        for suggestion in report["suggestions"]:
            operation = "add" if suggestion["operation"] == "append" else "set"
            safe_info = (
                ""
                if suggestion["safe"] is True
                else " (to confirm: may change the linting scope)"
            )
            logging.warning(
                f"- {suggestion['variable']}: {operation} "
                + f"[{', '.join(suggestion['values'])}]{safe_info}\n"
                + f"  {suggestion['reason']}"
            )
    logging.info(f"Prerun report written in [{report_file}]")
    logging.info(
        "Apply the relevant suggestions in .mega-linter.yml, "
        "then run MegaLinter again without MEGALINTER_PRERUN to lint."
    )
    logging.info(log_section_end("megalinter-prerun"))


def run_prerun(mega_linter):
    report = build_prerun_report(mega_linter)
    report_file = write_prerun_report(mega_linter, report)
    log_prerun_report(report, report_file)
    return report
