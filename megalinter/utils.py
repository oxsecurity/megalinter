#!/usr/bin/env python3

import importlib
import logging
import os
import re

import git
from megalinter import config

REPO_HOME_DEFAULT = (
    "/tmp/lint"
    if os.path.isdir("/tmp/lint")
    else os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
)

ANSI_ESCAPE_REGEX = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")


def get_excluded_directories():
    default_excluded_dirs = [
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".rbenv",
        ".venv",
        ".terragrunt-cache",
        "node_modules",
        "report",
    ]
    excluded_dirs = config.get_list("EXCLUDED_DIRECTORIES", default_excluded_dirs)
    excluded_dirs += config.get_list("ADDITIONAL_EXCLUDED_DIRECTORIES", [])
    return set(excluded_dirs)


def check_file_extension_or_name(file, file_extensions, file_names_regex):
    base_file_name = os.path.basename(file)
    filename, file_extension = os.path.splitext(base_file_name)
    if len(file_extensions) > 0 and file_extension in file_extensions:
        return True
    elif len(file_names_regex) > 0 and filename in file_names_regex:
        return True
    elif len(file_extensions) == 1 and file_extensions[0] == "*":
        return True
    return False


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


def file_contains(file_name, regex_list):
    if not regex_list:
        return True

    combined_regex = "|".join(regex_list)
    combined_regex_object = re.compile(combined_regex, flags=re.MULTILINE)

    with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    found_pattern = combined_regex_object.search(content) is not None
    return found_pattern


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


def check_updated_file(file, repo_home):
    changed_files = list_updated_files(repo_home)
    file_absolute = os.path.abspath(file)
    for changed_file in changed_files:
        if changed_file in file_absolute:
            return True
    return False


def normalize_log_string(str_in):
    return (
        ANSI_ESCAPE_REGEX.sub("", str_in)  # Remove ANSI escape sequences (ANSI colors)
        .replace("/tmp/lint/", "")
        .replace("tmp/lint/", "")
        .replace("/github/workspace/", "")
        .replace("github/workspace/", "")
    )
