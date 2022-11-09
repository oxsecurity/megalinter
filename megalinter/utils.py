#!/usr/bin/env python3

import importlib
import logging
import os
import re
from fnmatch import fnmatch
from typing import Any, Optional, Pattern, Sequence

import git
from megalinter import config
from megalinter.constants import DEFAULT_DOCKER_WORKSPACE_DIR

REPO_HOME_DEFAULT = (
    DEFAULT_DOCKER_WORKSPACE_DIR
    if os.path.isdir(DEFAULT_DOCKER_WORKSPACE_DIR)
    else os.environ.get("DEFAULT_WORKSPACE")
    if os.path.isdir(os.environ.get("DEFAULT_WORKSPACE", "null"))
    else os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
)

ANSI_ESCAPE_REGEX = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
LIST_OF_REPLACEMENTS = [
    # MegaLinter image
    [f"{DEFAULT_DOCKER_WORKSPACE_DIR}/", ""],
    ["tmp/lint/", ""],
    # GitHub Actions
    ["/github/workspace/", ""],
    ["github/workspace/", ""],
]
# GitLab CI
CI_PROJECT_DIR = os.environ.get("CI_PROJECT_DIR", "")
if CI_PROJECT_DIR != "":
    LIST_OF_REPLACEMENTS += [[f"/{CI_PROJECT_DIR}/", ""], [f"{CI_PROJECT_DIR}/", ""]]
# Other
DEFAULT_WORKSPACE = os.environ.get("DEFAULT_WORKSPACE", "")
if DEFAULT_WORKSPACE != "":
    LIST_OF_REPLACEMENTS += [
        [f"/{DEFAULT_WORKSPACE}/", ""],
        [f"{DEFAULT_WORKSPACE}/", ""],
    ]


def get_excluded_directories():
    default_excluded_dirs = [
        "__pycache__",
        ".git",
        ".jekyll-cache",
        ".pytest_cache",
        ".mypy_cache",
        ".rbenv",
        ".venv",
        ".terraform",
        ".terragrunt-cache",
        "node_modules",
        config.get("REPORT_OUTPUT_FOLDER", "megalinter-reports"),
    ]
    excluded_dirs = config.get_list("EXCLUDED_DIRECTORIES", default_excluded_dirs)
    excluded_dirs += config.get_list("ADDITIONAL_EXCLUDED_DIRECTORIES", [])
    return set(excluded_dirs)


def filter_files(
    all_files: Sequence[str],
    filter_regex_include: Optional[str],
    filter_regex_exclude: Optional[str],
    file_names_regex: Sequence[str],
    file_extensions: Any,
    ignored_files: Optional[Sequence[str]],
    ignore_generated_files: Optional[bool] = False,
    file_names_not_ends_with: Optional[Sequence[str]] = None,
    file_contains_regex: Optional[Sequence[str]] = None,
    files_sub_directory: Optional[str] = None,
    lint_all_other_linters_files: bool = False,
    prefix: Optional[str] = None,
) -> Sequence[str]:
    file_extensions = frozenset(file_extensions)
    filter_regex_include_object = (
        re.compile(filter_regex_include) if filter_regex_include else None
    )
    filter_regex_exclude_object = (
        re.compile(filter_regex_exclude) if filter_regex_exclude else None
    )
    file_names_regex_object = re.compile("|".join(file_names_regex))
    filtered_files = []
    file_contains_regex_object = (
        re.compile("|".join(file_contains_regex), flags=re.MULTILINE)
        if file_contains_regex
        else None
    )

    # if each file is check against every ignored_files (it can contain all the files), it's a O(n²) filtering
    # to reduce the execution time and complexity ignored_files is split
    ignored_patterns = list(filter(lambda x: "*" in x, ignored_files or []))
    ignored_fileset = frozenset(ignored_files or [])

    # Filter all files to keep only the ones matching with the current linter

    for file in all_files:
        file_with_prefix_and_sub_dir = os.path.normpath(file)
        file = file_with_prefix_and_sub_dir

        if prefix or files_sub_directory:
            prefix_and_sub_dir = os.path.normpath(
                os.path.join(prefix or "", files_sub_directory or "") + os.path.sep
            )

            if file.startswith(prefix_and_sub_dir):
                file = os.path.relpath(file_with_prefix_and_sub_dir, prefix_and_sub_dir)
            else:
                # Skip if file is not in defined files_sub_directory
                continue

        # Skip if file is in ignore list
        if file in ignored_fileset:
            continue
        # Skip if file is in ignored patterns
        if ignored_patterns and any(
            fnmatch(file, pattern) for pattern in ignored_patterns
        ):
            continue

        base_file_name = os.path.basename(file)
        _, file_extension = os.path.splitext(base_file_name)
        # Skip according to FILTER_REGEX_INCLUDE
        if filter_regex_include_object and not filter_regex_include_object.search(file):
            continue
        # Skip according to FILTER_REGEX_EXCLUDE
        if filter_regex_exclude_object and filter_regex_exclude_object.search(file):
            continue

        # Skip according to file extension (only if lint_all_other_linter_files is false or file_extensions is defined)
        if lint_all_other_linters_files is False or len(file_extensions) > 0:
            if file_extension in file_extensions:
                pass
            elif "*" in file_extensions:
                pass
            elif file_names_regex_object.fullmatch(base_file_name):
                pass
            else:
                continue
        # Skip according to end of file name
        if file_names_not_ends_with and file.endswith(tuple(file_names_not_ends_with)):
            continue
        # Skip according to file name regex
        if file_contains_regex and not file_contains(
            file_with_prefix_and_sub_dir, file_contains_regex_object
        ):
            continue
        # Skip according to IGNORE_GENERATED_FILES
        if (
            ignore_generated_files is not None
            and ignore_generated_files is True
            and file_is_generated(file_with_prefix_and_sub_dir)
        ):
            continue

        filtered_files.append(file_with_prefix_and_sub_dir)

    return filtered_files


# Center the string and complete blanks with hyphens (-)
def format_hyphens(str_in):
    if str_in != "":
        str_in = " " + str_in + " "
    return "{s:{c}^{n}}".format(s=str_in, n=100, c="-")


def list_active_reporters_for_scope(scope, reporter_init_params):
    reporters = []
    # List associated reporters
    reporters_dir = os.path.realpath(
        os.path.dirname(os.path.abspath(__file__)) + "/reporters"
    )
    scope_reporters = []
    for reporter_class_file in os.listdir(reporters_dir):
        if not reporter_class_file.endswith("Reporter.py"):
            continue
        reporter_class_nm = os.path.splitext(reporter_class_file)[0]
        reporter_module = importlib.import_module(
            ".reporters." + reporter_class_nm, package=__package__
        )
        reporter_class = getattr(reporter_module, reporter_class_nm)
        if reporter_class.scope == scope:
            reporter = reporter_class(reporter_init_params)
            scope_reporters += [reporter]
    # Keep only active reporters
    for reporter in scope_reporters:
        if reporter.is_active is False:
            continue
        reporters += [reporter]
    # Sort reporters by name
    reporters = sorted(reporters, key=lambda r: (r.processing_order, r.name))
    return reporters


def check_activation_rules(activation_rules, _linter):
    active = False
    for rule in activation_rules:
        if rule["type"] == "variable":
            value = config.get(rule["variable"], rule["default_value"])
            if value == rule["expected_value"]:
                active = True
            else:
                active = False
                break
    return active


def file_contains(file_name: str, regex_object: Optional[Pattern[str]]) -> bool:
    if not regex_object:
        return True
    with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    found_pattern = regex_object.search(content) is not None
    return found_pattern


def file_is_generated(file_name: str) -> bool:
    with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    is_generated = "@generated" in content and "@not-generated" not in content
    return is_generated


def decode_utf8(stdout):
    # noinspection PyBroadException
    try:
        res = stdout.decode("utf-8")
    except Exception:
        res = str(stdout)
    return res


def list_updated_files(repo_home):
    try:
        repo = git.Repo(repo_home)
    except git.InvalidGitRepositoryError:
        try:
            repo = git.Repo(REPO_HOME_DEFAULT)
        except git.InvalidGitRepositoryError:
            logging.warning("Unable to find git repository to list updated files")
            return []
    changed_files = [item.a_path for item in repo.index.diff(None)]
    return changed_files


def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.InvalidGitRepositoryError:
        return False


def check_updated_file(file, repo_home, changed_files=None):
    if changed_files is None:
        changed_files = list_updated_files(repo_home)
    file_absolute = os.path.abspath(file)
    for changed_file in changed_files:
        if changed_file in file_absolute:
            return True
    return False


def normalize_log_string(str_in):
    str_in = ANSI_ESCAPE_REGEX.sub("", str_in)
    for replacement in LIST_OF_REPLACEMENTS:
        str_in = str_in.replace(replacement[0], replacement[1])
    return str_in


def format_bullet_list(files):
    list_separator = "\n- "
    prefix = list_separator if any(files) is True else ""
    file_list = list_separator.join(files) if len(files) > 0 else ""
    return "{}{}".format(prefix, file_list)


def find_json_in_stdout(stdout: str):
    # Whole stdout is json
    if stdout.startswith("{"):
        return truncate_json_from_line(stdout)
    # Try to find a json line within stdout
    found_json = ""
    stdout_lines = stdout.splitlines()
    stdout_lines.reverse()  # start from last lines
    for line in stdout_lines:
        if line.startswith("{"):
            json_only = truncate_json_from_line(line)
            if json_only != "":
                found_json = json_only
                break
    return found_json


def truncate_json_from_line(line: str):
    start_pos = line.find("{")
    end_pos = line.rfind("}")
    if start_pos > -1 and end_pos > -1:
        return line[start_pos : end_pos + 1]  # noqa: E203
    return ""


def get_current_test_name(full_name=False):
    current_name = os.environ.get("PYTEST_CURRENT_TEST", None)
    if current_name is not None:
        if full_name is True:
            return current_name
        else:
            return current_name.split(":")[-1].split(" ")[0]
    return ""


def can_write_report_files(megalinter_instance) -> bool:
    if (
        megalinter_instance.report_folder == "none"
        or megalinter_instance.report_folder == "false"
    ):
        return False
    return True
