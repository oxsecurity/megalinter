#!/usr/bin/env python3

import importlib
import json
import logging
import os
import re
import tempfile
import urllib.parse
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Optional, Pattern, Sequence

import git
import regex
from megalinter import config, logger
from megalinter.constants import DEFAULT_DOCKER_WORKSPACE_DIR

SIZE_MAX_SOURCEFILEHEADER = 1024

REPO_HOME_DEFAULT = (
    DEFAULT_DOCKER_WORKSPACE_DIR
    if os.path.isdir(DEFAULT_DOCKER_WORKSPACE_DIR)
    else (
        os.environ.get("DEFAULT_WORKSPACE")
        if os.path.isdir(os.environ.get("DEFAULT_WORKSPACE", "null"))
        else os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
    )
)

ANSI_ESCAPE_REGEX = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")

# Replacements for temp folder in case of MegaLinter server
LIST_OF_REPLACEMENTS_REGEX = []
if os.environ.get("MEGALINTER_SERVER", "") == "true":
    global_temp_dir = tempfile.gettempdir()
    path_seb_regex = os.path.sep.replace("\\", "\\\\")
    temp_megalinter_dir = (
        os.path.join(global_temp_dir, "ct-megalinter-x")
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        + f".*?({path_seb_regex}| |\\n|\\s)"
    )
    temp_megalinter_dir_2 = (
        os.path.join(global_temp_dir, "ct-megalinter-x")
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        + ".*"
    )
    temp_megalinter_dir_regex = rf"{temp_megalinter_dir}"
    temp_megalinter_dir_regex_2 = rf"{temp_megalinter_dir_2}"
    LIST_OF_REPLACEMENTS_REGEX = [
        temp_megalinter_dir_regex,
        temp_megalinter_dir_regex_2,
    ]
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


# Returns directory where all .yml language descriptors are defined
def get_descriptor_dir():
    # Compiled version (copied from DockerFile)
    if os.path.isdir("/megalinter-descriptors"):
        return "/megalinter-descriptors"
    # Dev / Test version
    else:
        descriptor_dir = os.path.realpath(
            os.path.dirname(os.path.abspath(__file__)) + "/descriptors"
        )
        assert os.path.isdir(
            descriptor_dir
        ), f"Descriptor dir {descriptor_dir} not found !"
        return descriptor_dir


def get_excluded_directories(request_id):
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
        config.get(request_id, "REPORT_OUTPUT_FOLDER", "megalinter-reports"),
    ]
    excluded_dirs = config.get_list(
        request_id, "EXCLUDED_DIRECTORIES", default_excluded_dirs
    )
    excluded_dirs += config.get_list(request_id, "ADDITIONAL_EXCLUDED_DIRECTORIES", [])
    return set(excluded_dirs)


def filter_files(
    all_files: Sequence[str],
    filter_regex_include: Optional[str],
    filter_regex_exclude: Sequence[str],
    file_names_regex: Sequence[str],
    file_extensions: Any,
    ignored_files: Optional[Sequence[str]],
    ignore_generated_files: Optional[bool] = False,
    file_names_not_ends_with: Optional[Sequence[str]] = None,
    file_contains_regex: Optional[Sequence[str]] = None,
    file_contains_regex_extensions: Optional[Sequence[str]] = None,
    files_sub_directory: Optional[str] = None,
    lint_all_other_linters_files: bool = False,
    workspace: str = "",
) -> Sequence[str]:
    file_extensions = frozenset(file_extensions)
    filter_regex_include_object = (
        re.compile(filter_regex_include) if filter_regex_include else None
    )
    filter_regex_exclude_objects = []
    for filter_regex_exclude_item in filter_regex_exclude:
        filter_regex_exclude_object = (
            re.compile(filter_regex_exclude_item) if filter_regex_exclude_item else None
        )
        filter_regex_exclude_objects += [filter_regex_exclude_object]
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
        file_with_prefix_and_sub_dir = os.path.normpath(file).replace(os.sep, "/")
        file_with_workspace = os.path.join(workspace, file_with_prefix_and_sub_dir)
        file = file_with_prefix_and_sub_dir

        # skip file if sub_directory necessary
        if files_sub_directory is not None:
            if not file.startswith(files_sub_directory):
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
        if filter_regex_include_object and (
            not filter_regex_include_object.search(file)
            # Compatibility with v6 regexes
            and not filter_regex_include_object.search(file_with_workspace)
        ):
            continue
        # Skip according to FILTER_REGEX_EXCLUDE list
        excluded_by_regex = False
        for filter_regex_exclude_object in filter_regex_exclude_objects:
            if filter_regex_exclude_object and (
                filter_regex_exclude_object.search(file)
                # Compatibility with v6 regexes
                or filter_regex_exclude_object.search(file_with_workspace)
            ):
                excluded_by_regex = True
                break
        if excluded_by_regex is True:
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
        # Skip according to file contains regex
        if (
            file_contains_regex
            and (
                (
                    # no defined file extension to check file content
                    file_contains_regex_extensions is None
                    or len(file_contains_regex_extensions) == 0
                )
                or (
                    # check file extension
                    file_extension
                    in file_contains_regex_extensions
                )
            )
            and not file_contains(file_with_workspace, file_contains_regex_object)
        ):
            continue
        # Skip according to IGNORE_GENERATED_FILES
        if (
            ignore_generated_files is not None
            and ignore_generated_files is True
            and file_is_generated(file_with_workspace)
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
    logging.debug(
        f"[Reporters] Available reporters for scope {scope}: "
        + ",".join([obj.name for obj in scope_reporters])
    )
    # Keep only active reporters
    for reporter in scope_reporters:
        if reporter.is_active is False:
            continue
        reporters += [reporter]
    # Sort reporters by name
    reporters = sorted(reporters, key=lambda r: r.processing_order)
    logging.debug(
        f"[Reporters] Active reporters for scope {scope}: "
        + ",".join([obj.name for obj in reporters])
    )
    return reporters


def check_activation_rules(activation_rules, linter):
    active = False
    for rule in activation_rules:
        if rule["type"] == "variable":
            value = config.get(
                linter.request_id, rule["variable"], rule["default_value"]
            )
            if value == rule["expected_value"]:
                active = True
            else:
                active = False
                break
    return active


def file_contains(file_name: str, regex_object: Optional[Pattern[str]]) -> bool:
    if not regex_object:
        return True
    try:
        with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        found_pattern = regex_object.search(content) is not None
        return found_pattern
    except Exception as e:
        logging.warning(f"Unable to check content of file {file_name}: " + str(e))
        return False


def file_is_generated(file_name: str) -> bool:
    with open(file_name, "rb") as f:
        content = f.read(SIZE_MAX_SOURCEFILEHEADER)
    return b"@generated" in content and b"@not-generated" not in content


def get_default_rules_location() -> str:
    default_rules_location = (
        "/action/lib/.automation"
        if os.path.isdir("/action/lib/.automation")
        else os.path.relpath(
            os.path.relpath(
                os.path.dirname(os.path.abspath(__file__)) + "/../TEMPLATES"
            )
        )
    )
    return default_rules_location


def clean_string(stdout, sanitize=True) -> str:
    # noinspection PyBroadException
    try:
        res = stdout.decode("utf-8")
        if sanitize is True:
            res = logger.sanitize_string(res)
    except Exception:
        res = str(stdout)
        if sanitize is True:
            res = logger.sanitize_string(res)
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
    if not Path(repo.git_dir).resolve().is_relative_to(Path(repo_home).resolve()):
        logging.warning(
            "Your workspace is not a Git working copy root (e.g., the workspace is inside a submodule)"
        )
        return []
    changed_files = [item.a_path for item in repo.index.diff(None)]
    return changed_files


def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.InvalidGitRepositoryError:
        return False


def get_git_context_info(request_id, path):
    # Repo name
    repo_name = config.get_first_var_set(
        request_id,
        [
            "GITHUB_REPOSITORY",
            "GIT_URL",
            "CI_PROJECT_NAME",
            "BITBUCKET_REPO_SLUG",
            "BUILD_REPOSITORYNAME",
        ],
        None,
    )
    if repo_name is not None:
        repo_name = repo_name.split("/")[-1]  # Get last portion
    # Branch name
    branch_name = config.get_first_var_set(
        request_id,
        [
            "GITHUB_HEAD_REF",
            "GITHUB_REF_NAME",
            "GIT_BRANCH",
            "CI_COMMIT_REF_NAME",
            "BITBUCKET_BRANCH",
            "BUILD_SOURCEBRANCHNAME",
        ],
        None,
    )
    if repo_name is None:
        try:
            repo = git.Repo(
                path,
                search_parent_directories=True,
            )
            repo_name = repo.working_tree_dir.split("/")[-1]
        except Exception:
            repo_name = "?"
    if branch_name is None:
        try:
            repo = git.Repo(
                path,
                search_parent_directories=True,
            )
            repo_name_1 = repo.working_tree_dir.split("/")[-1]
            branch = repo_name_1.active_branch
            branch_name = branch.name
        except Exception:
            branch_name = "?"
    # Job URL
    job_url = config.get_first_var_set(
        request_id,
        [
            "GITHUB_JOB_URL",
            "CI_JOB_URL",
        ],
        "",
    )
    # GitHub job url
    if job_url == "" and config.get(request_id, "GITHUB_REPOSITORY", "") != "":
        github_server_url = config.get(
            request_id, "GITHUB_SERVER_URL", "https://github.com"
        )
        github_repo = config.get(request_id, "GITHUB_REPOSITORY")
        run_id = config.get(request_id, "GITHUB_RUN_ID")
        job_url = f"{github_server_url}/{github_repo}/actions/runs/{run_id}"
    # Azure Job url
    elif job_url == "" and config.get(request_id, "SYSTEM_COLLECTIONURI", "") != "":
        SYSTEM_COLLECTIONURI = config.get(request_id, "SYSTEM_COLLECTIONURI")
        SYSTEM_TEAMPROJECT = urllib.parse.quote(
            config.get(request_id, "SYSTEM_TEAMPROJECT")
        )
        BUILD_BUILDID = config.get(
            request_id,
            "BUILD_BUILDID",
            config.get(request_id, "BUILD_BUILD_ID"),
        )
        job_url = f"{SYSTEM_COLLECTIONURI}{SYSTEM_TEAMPROJECT}/_build/results?buildId={BUILD_BUILDID}"
    # BitBucket job url
    elif job_url == "" and config.get(request_id, "BITBUCKET_STEP_UUID", "") != "":
        bitbucket_project_url = config.get(request_id, "BITBUCKET_GIT_HTTP_ORIGIN", "")
        bitbucket_pipeline_job_number = config.get(
            request_id, "BITBUCKET_BUILD_NUMBER", ""
        )
        pipeline_step_run_uuid = config.get(request_id, "BITBUCKET_STEP_UUID", "")
        pipeline_step_run_uuid = urllib.parse.quote(pipeline_step_run_uuid)
        job_url = (
            f"{bitbucket_project_url}/pipelines/results/"
            f"{bitbucket_pipeline_job_number}/steps/{pipeline_step_run_uuid}"
        )
    return {"repo_name": repo_name, "branch_name": branch_name, "job_url": job_url}


def check_updated_file(file, repo_home, changed_files=None):
    if changed_files is None:
        changed_files = list_updated_files(repo_home)
    file_absolute = os.path.abspath(file)
    for changed_file in changed_files:
        if changed_file in file_absolute:
            return True
    return False


def normalize_log_string(str_in):
    if str_in == "" or str_in is None:
        return ""
    str_in = ANSI_ESCAPE_REGEX.sub("", str_in)
    for replacement in LIST_OF_REPLACEMENTS:
        str_in = str_in.replace(replacement[0], replacement[1])
    for replacement_regex in LIST_OF_REPLACEMENTS_REGEX:
        str_in = re.sub(replacement_regex, "", str_in)
    return str_in


def format_bullet_list(files):
    list_separator = "\n- "
    prefix = list_separator if any(files) is True else ""
    file_list = list_separator.join(files) if len(files) > 0 else ""
    return "{}{}".format(prefix, file_list)


def find_json_in_stdout(stdout: str, sarif=True):
    # Try using full stdout
    found_json = truncate_json_from_string(stdout)
    if found_json != "":
        sarif_json = extract_sarif_json(found_json, sarif)
        if sarif_json != "":
            return sarif_json
    # Try to find a json single line within stdout
    stdout_lines = stdout.splitlines()
    stdout_lines.reverse()  # start from last lines
    for line in stdout_lines:
        if line.strip().startswith("{"):
            json_unique_line = truncate_json_from_string(line)
            sarif_json = extract_sarif_json(json_unique_line, sarif)
            if sarif_json != "":
                return sarif_json
    # Try using regex
    pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
    json_regex_results = pattern.findall(stdout)
    for json_regex_result in json_regex_results:
        sarif_json = extract_sarif_json(json_regex_result, sarif)
        if sarif_json != "":
            return sarif_json
    # SARIF json not found in stdout
    return ""


def truncate_json_from_string(string_with_json_inside: str):
    start_pos = string_with_json_inside.find("{")
    end_pos = string_with_json_inside.rfind("}")
    if start_pos > -1 and end_pos > -1:
        return string_with_json_inside[start_pos : end_pos + 1]  # noqa: E203
    return ""


def extract_sarif_json(json_text: str, sarif=True):
    try:
        json_obj = json.loads(json_text)
        if sarif is False:
            sarif_json = json.dumps(json_obj, indent=4)
        elif "runs" in json_obj:
            sarif_json = json.dumps(json_obj, indent=4)
        else:
            sarif_json = ""
    except json.decoder.JSONDecodeError:
        sarif_json = ""
    return sarif_json


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


# GitHub ref: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
def is_github_actions() -> bool:
    return config.get(None, "GITHUB_ACTIONS") is not None


def is_github_pr() -> bool:
    return config.get(None, "GITHUB_EVENT_NAME") == "pull_request"


# GitLab ref: https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
def is_gitlab_ci() -> bool:
    return config.get(None, "GITLAB_CI") == "true"


def is_gitlab_mr() -> bool:
    return config.get(None, "CI_PIPELINE_SOURCE") == "merge_request_event"


def is_gitlab_external_pr() -> bool:
    return config.get(None, "CI_PIPELINE_SOURCE") == "external_pull_request_event"


def is_gitlab_premium() -> bool:
    mr_event_type = config.get(None, "CI_MERGE_REQUEST_EVENT_TYPE")
    return (
        True
        if mr_event_type == "merged_result" or mr_event_type == "merge_train"
        else False
    )


# Azure DevOps ref: https://learn.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml
def is_azure_pipelines() -> bool:
    return config.get(None, "TF_BUILD") == "True"


def is_azure_devops_pr() -> bool:
    return config.get(None, "BUILD_REASON") == "PullRequest"


def is_ci() -> bool:
    return (
        True
        if (
            config.get(None, "CI") == "true"
            or is_github_actions()
            or is_gitlab_ci()
            or is_azure_pipelines()
        )
        else False
    )


def is_pr() -> bool:
    return (
        True
        if (
            config.get(None, "PULL_REQUEST") == "true"
            or is_github_pr()
            or is_gitlab_mr()
            or is_gitlab_external_pr()
            or is_azure_devops_pr()
        )
        else False
    )


def fix_regex_pattern(pattern):
    # 1. Fix global flags not at the start of the expression
    if "(?i)" in pattern:
        if pattern.find("(?i)") > 0:
            parts = pattern.split("(?i)")
            pattern = "(?i)" + "".join(parts[0:])
    # 2. Replace invalid escape sequences like `\z` with `$`
    pattern = re.sub(r"\\z", "$", pattern)
    return pattern


def keep_only_valid_regex_patterns(patterns, fail=False):
    fixed_patterns = []
    # Heuristic regex to detect nested quantifiers (potential ReDoS risk)
    nested_quantifier_regex = re.compile(
        r"\((?:[^()]*[+*][^()]*){2,}\)[+*?]"
    )
    for pattern in patterns:
        # First, attempt to fix the pattern
        fixed_pattern = fix_regex_pattern(pattern)
        try:
            # Try compiling the fixed pattern with regex module and a timeout (also checks validity)
            try:
                regex.compile(fixed_pattern, timeout=0.1)  # 100ms timeout
            except TimeoutError:
                logging.debug(
                    f"Skipped regex pattern due to timeout (possible ReDoS): {fixed_pattern}"
                )
                continue
            except Exception as e:
                logging.debug(
                    f"Skipped regex pattern due to error in regex module: {fixed_pattern}. Error: {e}"
                )
                continue
            # Skip if pattern has nested quantifiers (ReDoS risk)
            if nested_quantifier_regex.search(fixed_pattern):
                logging.debug(
                    f"Skipped potentially unsafe regex pattern (possible ReDoS): {fixed_pattern}"
                )
                continue
            fixed_patterns.append(fixed_pattern)  # Pattern is valid and safe, add it
        except re.error as e:
            if fail is True:
                raise
            else:
                logging.debug(
                    f"Invalid regex pattern after fix: {fixed_pattern}. Error: {e}"
                )

    return fixed_patterns
