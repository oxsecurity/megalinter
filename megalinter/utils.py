#!/usr/bin/env python3

import importlib
import json
import logging
import os
import re
import tempfile
import warnings
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Optional, Pattern, Sequence, Union

import git
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

# Workspaces whose "git diff" already failed: list_updated_files runs once per
# linted file, and a workspace that fails once keeps failing for the whole run
UPDATED_FILES_FAILED_WORKSPACES: set[str] = set()

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


PREBUILT_LINTER_VERSIONS = {"loaded": False, "versions": {}}


# Returns the linter versions collected at Docker build time
# (/megalinter-descriptors/linter-versions.json), empty dict outside Docker
def get_prebuilt_linter_versions():
    if PREBUILT_LINTER_VERSIONS["loaded"] is False:
        versions_file = os.path.join(get_descriptor_dir(), "linter-versions.json")
        if os.path.isfile(versions_file):
            try:
                with open(versions_file, "r", encoding="utf-8") as json_file:
                    PREBUILT_LINTER_VERSIONS["versions"] = json.load(json_file)
            except json.JSONDecodeError as e:
                logging.warning(f"Unable to load {versions_file}: {str(e)}")
        PREBUILT_LINTER_VERSIONS["loaded"] = True
    return PREBUILT_LINTER_VERSIONS["versions"]


def get_prebuilt_linter_version(linter_name):
    version = get_prebuilt_linter_versions().get(linter_name)
    if version and version != "0.0.0" and version != "ERROR":
        return version
    return None


# Directories excluded by default. Kept as a module constant because
# find_workspace_excluded_directories() prunes them from its walk even when
# EXCLUDED_DIRECTORIES overrides the list: config.get_list() REPLACES the
# defaults, so a user setting EXCLUDED_DIRECTORIES: ["cdk.out"] would otherwise
# make the walk enumerate every node_modules, .venv and .terraform tree in full
DEFAULT_EXCLUDED_DIRECTORIES = [
    "__pycache__",
    ".angular",
    ".git",
    ".jekyll-cache",
    ".nx",
    ".parcel-cache",
    ".pnpm-store",
    ".pytest_cache",
    ".mypy_cache",
    ".rbenv",
    ".sf",
    ".sfdx",
    ".turbo",
    ".venv",
    ".terraform",
    ".terragrunt-cache",
    ".wireit",
    ".yarn/cache",
    "node_modules",
]

_excluded_directories_cache: dict[str, set[str]] = {}


# MegaLinter writes its own files there while linters run, so it must never be
# analyzed: a report file created or deleted mid-run makes project-mode linters
# walking the workspace fail
def get_report_output_folder_name(request_id):
    return config.get(request_id, "REPORT_OUTPUT_FOLDER", "megalinter-reports")


def get_excluded_directories(request_id):
    cache_key = str(request_id)
    cached = _excluded_directories_cache.get(cache_key)
    if cached is not None:
        return cached
    excluded_dirs = config.get_list(
        request_id, "EXCLUDED_DIRECTORIES", list(DEFAULT_EXCLUDED_DIRECTORIES)
    )
    excluded_dirs += config.get_list(request_id, "ADDITIONAL_EXCLUDED_DIRECTORIES", [])
    # Always excluded, even when EXCLUDED_DIRECTORIES is overridden
    excluded_dirs += [get_report_output_folder_name(request_id)]
    result = set(excluded_dirs)
    _excluded_directories_cache[cache_key] = result
    return result


# Convert absolute paths located inside the workspace into workspace-relative
# paths so they match the values produced by os.walk(). Workspace-relative
# entries are kept unchanged; absolute paths outside the workspace are dropped
# (they can never match)
def normalize_excluded_directories(workspace, excluded_directories) -> set[str]:
    workspace_abs = os.path.abspath(workspace)
    normalized = set()
    for excluded_dir in excluded_directories:
        if not excluded_dir:
            continue
        if os.path.isabs(excluded_dir):
            try:
                rel = os.path.relpath(excluded_dir, workspace_abs)
            except ValueError:
                continue
            if rel == "." or rel.startswith(".."):
                continue
            normalized.add(rel.replace("\\", "/"))
        else:
            # Strip before testing emptiness: a bare "/" would otherwise add an
            # empty entry, which matches nothing but is a trap for callers
            relative = excluded_dir.replace("\\", "/").strip("/")
            if relative != "":
                normalized.add(relative)
    return normalized


# Single source of truth for directory-exclusion matching, shared by
# full-codebase (os.walk), changed-files (git diff) and project lint mode
# exclusions forwarding: a directory matches by its basename at any nesting
# level, or by its workspace-relative path. Returns the matched entry, so
# callers can group found directories by the excluded entry they come from
def match_excluded_dir(rel_dir_path, excluded_directories) -> Optional[str]:
    rel_dir_path = rel_dir_path.replace("\\", "/").strip("/")
    if rel_dir_path in excluded_directories:
        return rel_dir_path
    basename = rel_dir_path.rsplit("/", 1)[-1]
    if basename in excluded_directories:
        return basename
    return None


def is_excluded_dir(rel_dir_path, excluded_directories) -> bool:
    return match_excluded_dir(rel_dir_path, excluded_directories) is not None


# Every entry the directory matches, not only the first one. The workspace walk
# is shared by all the linters of a run, so a located directory must be filed
# under each entry it matches: a linter excluding "docs" and another excluding
# "packages/a/docs" both have to find packages/a/docs in the result
def match_excluded_dir_entries(rel_dir_path, excluded_directories) -> set[str]:
    rel_dir_path = rel_dir_path.replace("\\", "/").strip("/")
    matched = set()
    if rel_dir_path in excluded_directories:
        matched.add(rel_dir_path)
    basename = rel_dir_path.rsplit("/", 1)[-1]
    if basename in excluded_directories:
        matched.add(basename)
    return matched


# Cache of the workspace walk, keyed by (request_id, workspace). The value is
# a (searched entries, found map) couple: a later call whose entries are a
# subset of the ones already searched is served from it, so a whole MegaLinter
# run needs a single walk. Cleared with the config (server mode is long-lived)
_workspace_excluded_directories_cache: dict = {}


# Directories the walk must never descend into: the run's excluded directories
# plus the built-in defaults. The defaults are added even when
# EXCLUDED_DIRECTORIES replaced them (config.get_list REPLACES the defaults),
# so a custom exclusion list can not turn the walk into a full enumeration of
# every node_modules, .venv or .terraform tree. Deliberately independent of
# what is being searched, so every linter of a run walks the same shape
def get_walk_pruned_directories(request_id, workspace) -> set[str]:
    return normalize_excluded_directories(
        workspace,
        list(DEFAULT_EXCLUDED_DIRECTORIES) + list(get_excluded_directories(request_id)),
    )


def walk_workspace_excluded_directories(
    request_id, workspace, searched_directories
) -> dict:
    pruned_directories = get_walk_pruned_directories(request_id, workspace)
    found: dict[str, list[str]] = {}
    for dir_path, sub_dirs, _files in os.walk(
        workspace, topdown=True, followlinks=False
    ):
        rel_dir_path = os.path.relpath(dir_path, workspace).replace("\\", "/")
        prefix = "" if rel_dir_path == "." else rel_dir_path + "/"
        kept_sub_dirs = []
        for sub_dir in sub_dirs:
            rel_sub_dir = prefix + sub_dir
            for matched in match_excluded_dir_entries(
                rel_sub_dir, searched_directories
            ):
                found.setdefault(matched, []).append(rel_sub_dir)
            # Never descend into a directory that is excluded from the analysis:
            # its content is not linted, so nothing inside it has to be
            # forwarded, and enumerating it is pure cost
            if not is_excluded_dir(rel_sub_dir, pruned_directories):
                kept_sub_dirs.append(sub_dir)
        sub_dirs[:] = kept_sub_dirs
    return {matched: sorted(paths) for matched, paths in found.items()}


# Seed the cache with excluded directories already located by another walk of
# the workspace. MegaLinter's own file listing (Megalinter.list_files_all)
# prunes the very same directories, so in full-codebase mode the forwarding
# lookup costs nothing at all. Finding a directory in MORE places than the
# standalone walk would is never wrong: its own pruning is only a cost
# optimization, and every reported path is genuinely an excluded directory
def prime_workspace_excluded_directories(
    request_id, workspace, searched_directories, found
) -> None:
    searched = normalize_excluded_directories(workspace, searched_directories)
    cache_key = (str(request_id), os.path.abspath(workspace))
    cached = _workspace_excluded_directories_cache.get(cache_key)
    if cached is not None and searched <= cached[0]:
        return
    _workspace_excluded_directories_cache[cache_key] = (
        searched,
        {matched: sorted(set(paths)) for matched, paths in found.items()},
    )


# Locate every excluded directory in the workspace, at any nesting level:
# EXCLUDED_DIRECTORIES and ADDITIONAL_EXCLUDED_DIRECTORIES are basenames
# excluded wherever they are found, so a lookup limited to the workspace root
# would miss directories like infrastructure/cdk.out. Returns a dict mapping
# each searched entry to the workspace-relative paths where it exists
def find_workspace_excluded_directories(
    request_id, workspace, excluded_directories
) -> dict:
    searched = normalize_excluded_directories(workspace, excluded_directories)
    cache_key = (str(request_id), os.path.abspath(workspace))
    cached = _workspace_excluded_directories_cache.get(cache_key)
    if cached is None or not searched <= cached[0]:
        # Walk once for the union of everything searched so far: linters only
        # differ by the candidates extracted from their FILTER_REGEX_EXCLUDE,
        # and the walk shape does not depend on what is searched
        all_searched = searched if cached is None else searched | cached[0]
        cached = (
            all_searched,
            walk_workspace_excluded_directories(request_id, workspace, all_searched),
        )
        _workspace_excluded_directories_cache[cache_key] = cached
    return {name: paths for name, paths in cached[1].items() if name in searched}


# Drop the cached excluded-directories of one request (or of every request when
# request_id is None). Registered into config so that config.delete() and
# config.set() clear them: in server mode the process is long-lived and handles
# many analyses, and a configuration change invalidates both caches
def clear_excluded_directories_caches(request_id=None):
    if request_id is None:
        _excluded_directories_cache.clear()
        _workspace_excluded_directories_cache.clear()
        return
    _excluded_directories_cache.pop(str(request_id), None)
    for cache_key in [
        key
        for key in _workspace_excluded_directories_cache
        if key[0] == str(request_id)
    ]:
        del _workspace_excluded_directories_cache[cache_key]


config.register_cache_cleaner(clear_excluded_directories_caches)


# Remove comments and trailing commas from JSONC content so it can be parsed
# with json.loads (string contents are preserved untouched)
def strip_jsonc(content: str) -> str:
    result = []
    in_string = False
    escaped = False
    index = 0
    while index < len(content):
        char = content[index]
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            result.append(char)
            index += 1
        elif content.startswith("//", index):
            while index < len(content) and content[index] != "\n":
                index += 1
        elif content.startswith("/*", index):
            comment_end = content.find("*/", index + 2)
            index = len(content) if comment_end == -1 else comment_end + 2
        else:
            result.append(char)
            index += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(result))


_REGEX_METACHARACTERS = set(".^$*+?()[]{}|\\")
_REGEX_QUANTIFIERS = set("*+?{")


# A regex starting with ^ is anchored on the workspace root: the directories it
# excludes are only the root-level ones, so its candidates must not be matched
# at any nesting level like EXCLUDED_DIRECTORIES entries are
def is_root_anchored_regex(regex) -> bool:
    return str(regex).strip().startswith("^")


# Extract literal directory candidates from an exclusion regex, without any
# filesystem walk: strip anchors, expand a simple leading alternation group,
# then keep the literal prefix of each alternative. "." is kept as a literal
# realization since callers verify the candidate's existence on disk anyway.
def extract_dir_candidates_from_regex(regex: str) -> list[str]:
    regex = str(regex).strip()
    if regex.startswith("^"):
        regex = regex[1:]
    alternatives = []
    if regex.startswith("(") and ")" in regex:
        group, remainder = regex[1:].split(")", 1)
        if group.startswith("?:"):
            group = group[2:]
        # Expand the alternatives: the literal-prefix trimming below drops the
        # non-literal ones (escapes like \. are handled there)
        if "(" not in group and "[" not in group:
            alternatives = [alt + remainder for alt in group.split("|") if alt]
    if len(alternatives) == 0:
        if "(" not in regex and "[" not in regex and "|" in regex:
            alternatives = [alt for alt in regex.split("|") if alt]
        else:
            alternatives = [regex]
    candidates = []
    for alternative in alternatives:
        literal = ""
        pos = 0
        while pos < len(alternative):
            char = alternative[pos]
            next_char = alternative[pos + 1] if pos + 1 < len(alternative) else ""
            if char == "\\" and next_char in _REGEX_METACHARACTERS | {"/"}:
                char = next_char
                pos += 1
                next_char = alternative[pos + 1] if pos + 1 < len(alternative) else ""
            elif char == "\\":
                break  # \d, \w, ... are not literals
            elif char in _REGEX_METACHARACTERS and char != ".":
                break
            if next_char in _REGEX_QUANTIFIERS:
                break  # the quantifier applies to this char: drop it and stop
            literal += char
            pos += 1
        literal = literal.strip("/")
        if literal != "" and literal not in candidates:
            candidates.append(literal)
    return candidates


# Flatten None, a single regex string, or a (possibly nested) list of regex strings
# into a flat list of non-empty regex strings.
def normalize_regex_filter(value) -> Sequence[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value != "" else []
    result: list = []
    for item in value:
        result += normalize_regex_filter(item)
    return result


def filter_files(
    all_files: Sequence[str],
    filter_regex_include: Optional[Union[str, Sequence[str]]],
    filter_regex_exclude: Optional[Union[str, Sequence[str]]],
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
    filter_regex_include_objects = [
        re.compile(item) for item in normalize_regex_filter(filter_regex_include)
    ]
    filter_regex_exclude_objects = [
        re.compile(item) for item in normalize_regex_filter(filter_regex_exclude)
    ]
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
        # Skip according to FILTER_REGEX_INCLUDE list (kept if matching any, logical OR)
        if filter_regex_include_objects and not any(
            filter_regex_include_object.search(file)
            # Compatibility with v6 regexes
            or filter_regex_include_object.search(file_with_workspace)
            for filter_regex_include_object in filter_regex_include_objects
        ):
            continue
        # Skip according to FILTER_REGEX_EXCLUDE list (excluded if matching any, logical OR)
        excluded_by_regex = False
        for filter_regex_exclude_object in filter_regex_exclude_objects:
            if filter_regex_exclude_object.search(
                file
            ) or filter_regex_exclude_object.search(
                # Compatibility with v6 regexes
                file_with_workspace
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
    reason = None
    for rule in activation_rules:
        if rule["type"] == "variable":
            value = config.get(
                linter.request_id, rule["variable"], rule["default_value"]
            )
            if value == rule["expected_value"]:
                active = True
            else:
                active = False
                reason = (
                    f"{rule['variable']}={value} "
                    f"(set {rule['variable']}={rule['expected_value']} to activate)"
                )
                break
        # For linters requiring a credential or a connection string, the value
        # can not be known in advance: activate as soon as the variable is set
        elif rule["type"] == "variable_is_set":
            value = config.get(linter.request_id, rule["variable"], "")
            if value != "":
                active = True
            else:
                active = False
                reason = (
                    f"{rule['variable']} is not set "
                    f"(define {rule['variable']} to activate)"
                )
                break
    return active, reason


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
    # Closing the repo releases the persistent "git cat-file" child process and its
    # file descriptors: this function runs once per fixer linter, so leaking them
    # can exhaust the file descriptor limit on a large run
    with repo:
        if not Path(repo.git_dir).resolve().is_relative_to(Path(repo_home).resolve()):
            logging.warning(
                "Your workspace is not a Git working copy root (e.g., the workspace is inside a submodule)"
            )
            return []
        try:
            changed_files = [item.a_path for item in repo.index.diff(None)]
        except git.GitCommandError as git_err:
            # Listing updated files is best effort: a git failure must not end a
            # run whose linters all passed. Known case (issue #8649): on a
            # read-only workspace, a required content filter such as git-lfs
            # can not write its temporary files and the diff exits 128.
            # GitPython drains stderr before raising, so git's own message is
            # usually lost: name the workspace and the command instead.
            message = (
                f"Unable to list updated files in {repo_home}: {str(git_err)}\n"
                "If your workspace is mounted read-only, a required git filter "
                "(e.g. git-lfs) can not write its temporary files: mount .git "
                "as writable to let MegaLinter detect the files fixed by linters"
            )
            if repo_home in UPDATED_FILES_FAILED_WORKSPACES:
                logging.debug(message)
            else:
                UPDATED_FILES_FAILED_WORKSPACES.add(repo_home)
                logging.warning(message)
            return []
    return changed_files


def is_git_repo(path):
    try:
        with git.Repo(path) as repo:
            _ = repo.git_dir
        return True
    except git.InvalidGitRepositoryError:
        return False


def get_git_context_info(request_id, path):
    # Import here: ci_providers imports utils, so a module level import cycles
    from megalinter import ci_providers

    ci_provider = ci_providers.get_ci_provider(request_id)
    repo_name = ci_provider.get_repo_name()
    branch_name = ci_provider.get_branch_name()
    # Explicit overrides win over whatever the provider computes
    job_url = config.get_first_var_set(request_id, ["GITHUB_JOB_URL", "CI_JOB_URL"], "")
    if job_url == "":
        job_url = ci_provider.get_job_url()
    # Keep honoring the platform variables even when the platform itself is not
    # detected (MegaLinter run from a CI it does not recognize)
    if repo_name is None:
        repo_name = ci_providers.CiProvider.split_repo_name(
            config.get_first_var_set(
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
        )
    if branch_name is None:
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
    # Fall back to the local git repository for whatever the platform did not
    # provide (also covers running outside any CI)
    if repo_name is None:
        try:
            repo = git.Repo(
                path,
                search_parent_directories=True,
            )
            repo_name = repo.working_tree_dir.split("/")[-1]
            if branch_name is None:
                try:
                    branch = repo.active_branch
                    branch_name = branch.name
                except Exception:
                    branch_name = "?"
        except Exception:
            repo_name = "?"
    if branch_name is None:
        try:
            repo = git.Repo(
                path,
                search_parent_directories=True,
            )
            branch = repo.active_branch
            branch_name = branch.name
        except Exception:
            branch_name = "?"
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
    # Try balanced {...} blocks found anywhere in stdout
    for json_block in extract_json_blocks(stdout):
        sarif_json = extract_sarif_json(json_block, sarif)
        if sarif_json != "":
            return sarif_json
    # SARIF json not found in stdout
    return ""


# Return outermost balanced {...} blocks, ignoring braces within JSON strings.
# Balanced blocks nested under a never-closed "{" are also returned, as the JSON
# searched for may be preceded by log text containing unmatched braces
def extract_json_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    open_positions: list[int] = []
    open_children: list[list[str]] = []
    in_string = False
    escaped = False
    for pos, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"' and open_positions:
            in_string = True
        elif char == "{":
            open_positions.append(pos)
            open_children.append([])
        elif char == "}" and open_positions:
            start = open_positions.pop()
            # children are dropped: they are contained in this bigger balanced block
            open_children.pop()
            block = text[start : pos + 1]  # noqa: E203
            if open_positions:
                open_children[-1].append(block)
            else:
                blocks.append(block)
    # Balanced blocks whose parent braces were never closed are candidates too
    for children in open_children:
        blocks.extend(children)
    return blocks


# Parse JSON tolerating comments and trailing commas (jsonc, like .vscode config files)
def parse_jsonc(jsonc_text: str):
    chars: list[str] = []
    index = 0
    length = len(jsonc_text)
    in_string = False
    escaped = False
    while index < length:
        char = jsonc_text[index]
        if in_string:
            chars.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
            chars.append(char)
        elif char == "/" and index + 1 < length and jsonc_text[index + 1] == "/":
            while index + 1 < length and jsonc_text[index + 1] != "\n":
                index += 1
        elif char == "/" and index + 1 < length and jsonc_text[index + 1] == "*":
            index += 3
            while index < length and not (
                jsonc_text[index - 1] == "*" and jsonc_text[index] == "/"
            ):
                index += 1
        elif char in "}]":
            tail = len(chars) - 1
            while tail >= 0 and chars[tail] in " \t\r\n":
                tail -= 1
            if tail >= 0 and chars[tail] == ",":
                chars.pop(tail)
            chars.append(char)
        else:
            chars.append(char)
        index += 1
    return json.loads("".join(chars))


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


# Bitbucket Pipelines ref: https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
def is_bitbucket() -> bool:
    return config.get(None, "BITBUCKET_BUILD_NUMBER") is not None


def is_bitbucket_pr() -> bool:
    return is_bitbucket() and config.get(None, "BITBUCKET_PR_ID") is not None


# Jenkins ref: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables
def is_jenkins() -> bool:
    return (
        config.get(None, "JENKINS_URL") is not None
        or config.get(None, "JENKINS_HOME") is not None
    )


def is_jenkins_pr() -> bool:
    return is_jenkins() and config.get(None, "CHANGE_ID") is not None


def is_ci() -> bool:
    return (
        True
        if (
            config.get(None, "CI") == "true"
            or is_github_actions()
            or is_gitlab_ci()
            or is_azure_pipelines()
            or is_bitbucket()
            or is_jenkins()
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
            or is_bitbucket_pr()
            or is_jenkins_pr()
        )
        else False
    )


# POSIX character classes (supported by Go regexp, used in gitleaks rules) and their
# Python re equivalents. Python parses [[:alnum:]] as a literal character set and
# emits "FutureWarning: Possible nested set", so they must be translated.
POSIX_CHARACTER_CLASSES = {
    "[:alnum:]": "a-zA-Z0-9",
    "[:alpha:]": "a-zA-Z",
    "[:ascii:]": "\\x00-\\x7f",
    "[:blank:]": " \\t",
    "[:cntrl:]": "\\x00-\\x1f\\x7f",
    "[:digit:]": "0-9",
    "[:graph:]": "\\x21-\\x7e",
    "[:lower:]": "a-z",
    "[:print:]": "\\x20-\\x7e",
    "[:punct:]": "!-/:-@\\[-`{-~",
    "[:space:]": "\\s",
    "[:upper:]": "A-Z",
    "[:word:]": "\\w",
    "[:xdigit:]": "0-9a-fA-F",
}


def fix_regex_pattern(pattern):
    # 1. Fix global flags not at the start of the expression
    if "(?i)" in pattern:
        if pattern.find("(?i)") > 0:
            parts = pattern.split("(?i)")
            pattern = "(?i)" + "".join(parts[0:])
    # 2. Replace invalid escape sequences like `\z` with `$`
    pattern = re.sub(r"\\z", "$", pattern)
    # 3. Translate POSIX character classes unsupported by Python re
    for posix_class, python_equivalent in POSIX_CHARACTER_CLASSES.items():
        pattern = pattern.replace(posix_class, python_equivalent)
    return pattern


def keep_only_valid_regex_patterns(patterns, fail=False):
    fixed_patterns = []
    # Heuristic regex to detect nested quantifiers (potential ReDoS risk)
    nested_quantifier_regex = re.compile(r"\((?:[^()]*[+*][^()]*){2,}\)[+*?]")
    for pattern in patterns:
        # First, attempt to fix the pattern
        fixed_pattern = fix_regex_pattern(pattern)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                re.compile(fixed_pattern)  # Check if the pattern is valid
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


def yellow(text):
    return f"\033[33m{text}\033[0m"


def green(text):
    return f"\033[32m{text}\033[0m"


def red(text):
    return f"\033[31m{text}\033[0m"


def blue(text):
    return f"\033[34m{text}\033[0m"


def cyan(text):
    return f"\033[36m{text}\033[0m"
