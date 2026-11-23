#!/usr/bin/env python3
# Checks on Windows what each native linter does with a list of files above the limit of
# the command line (.github/workflows/test-native-long-command.yml)
#
#   matrix   prints the GitHub Actions matrix of the linters running on a list of files
#   run      runs some linters on a generated workspace, and writes one result per linter
#   run-one  same for one linter, in its own process (MegaLinter keeps state per process)
#   summary  gathers the results in the job summary, and fails if a linter is broken
#
# The workspace holds a failing file first, many passing files, and a failing file last:
#   all_files  the linter reports the last file: it received the whole list
#   truncated  the linter reports the first file, and MegaLinter says what it skipped
#   unclear    the linter failed on the list, but its output names no file
#   broken     the linter did not start, or found nothing: a run that looks clean is a lie
import argparse
import glob
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_HOME)

from megalinter import linter_factory, utilstest  # noqa: E402
from megalinter.native import long_command  # noqa: E402
from megalinter.native.catalog import load_native_specs  # noqa: E402
from native_ci import build_matrix  # noqa: E402

TEST_ROOT = os.path.join(REPO_HOME, ".automation", "test")
FILES_FOLDER = "long-command-files"
FIRST_FILE_FOLDER = "aaa-first-file"
LAST_FILE_FOLDER = "zzz-last-file"
PASSING_FILES_FOLDER = "passing-files-with-a-long-folder-name-to-reach-the-limit"
# Above the 32767 characters of the Windows limit
LIST_MIN_CHARS = 36000
LINTER_TIMEOUT_SECONDS = 900
PROCESS_TIMEOUT_SECONDS = 1200
OUTPUT_SAMPLE_CHARS = 300
OUTCOMES = ["all_files", "truncated", "unclear", "skipped", "broken"]


def list_of_files_keys():
    return {
        spec.key
        for spec in load_native_specs()
        if spec.linter.get("disabled") is not True
        and spec.linter.get("cli_lint_mode", "file") == "list_of_files"
    }


def is_linted_file(linter, name):
    for regex in linter.file_names_regex or []:
        if re.fullmatch(regex, name):
            return True
    extensions = linter.file_extensions or []
    if len(extensions) == 0 and not linter.file_names_regex:
        return True
    return "*" in extensions or os.path.splitext(name)[1] in extensions


# A file named after its kind first: a good or bad folder also holds configuration
# files of the same type (ex: biome.json, .v8rrc.yml)
def find_fixture(linter, kind):
    source = os.path.join(TEST_ROOT, linter.test_folder)
    kind_folder = os.path.join(source, kind)
    has_kind_folder = os.path.isdir(kind_folder)
    candidates = []
    for folder, sub_folders, files in os.walk(
        kind_folder if has_kind_folder else source
    ):
        sub_folders[:] = [
            sub for sub in sub_folders if sub not in ("reports", "fix", ".wireit")
        ]
        for name in files:
            path = os.path.join(folder, name)
            relative = os.path.relpath(path, source).lower()
            if is_linted_file(linter, name) and (has_kind_folder or kind in relative):
                candidates.append(
                    (kind not in name.lower(), name.startswith("."), path)
                )
    return sorted(candidates)[0][2] if len(candidates) > 0 else None


def copy_configuration_files(linter, workspace):
    source = os.path.join(TEST_ROOT, linter.test_folder)
    bad_folder = os.path.join(source, "bad")
    ignored = shutil.ignore_patterns("reports", "fix", ".wireit")
    if not os.path.isdir(bad_folder):
        shutil.copytree(source, workspace, ignore=ignored, dirs_exist_ok=True)
        return
    # The configuration of the failing fixture (ex: the schema mapping of v8r), and
    # the one of the test folder that tools find by walking up (ex: biome.json)
    for name in os.listdir(source):
        path = os.path.join(source, name)
        if os.path.isfile(path):
            shutil.copy(path, os.path.join(workspace, name))
    shutil.copytree(bad_folder, workspace, ignore=ignored, dirs_exist_ok=True)
    # v8r matches fileMatch on the whole path, and the generated files are in sub-folders
    v8r_config = os.path.join(workspace, ".v8rrc.yml")
    if os.path.isfile(v8r_config):
        with open(v8r_config, "r", encoding="utf-8") as f:
            content = f.read()
        with open(v8r_config, "w", encoding="utf-8") as f:
            f.write(content.replace('fileMatch: ["', 'fileMatch: ["**/'))


# Copies keep the name of the fixture: some linters select files by their exact name
def build_workspace(linter, workspace, good_file, bad_file):
    copy_configuration_files(linter, workspace)
    sub_directory = linter.files_sub_directory or ""
    base = os.path.join(workspace, *sub_directory.split("/"), FILES_FOLDER)
    for folder in (FIRST_FILE_FOLDER, LAST_FILE_FOLDER):
        os.makedirs(os.path.join(base, folder))
        shutil.copy(bad_file, os.path.join(base, folder, os.path.basename(bad_file)))
    sample = os.path.join(
        sub_directory,
        FILES_FOLDER,
        PASSING_FILES_FOLDER,
        "0000",
        os.path.basename(good_file),
    )
    count = LIST_MIN_CHARS // (len(sample) + 1) + 1
    for index in range(count):
        folder = os.path.join(base, PASSING_FILES_FOLDER, f"{index:04d}")
        os.makedirs(folder)
        shutil.copy(good_file, os.path.join(folder, os.path.basename(good_file)))
    subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
    return count + 2


def activation_variables(linter):
    return {
        rule["variable"]: rule["expected_value"]
        for rule in linter.activation_rules or []
        if rule.get("type") == "variable" and "expected_value" in rule
    }


# Spelling linters lint the files of the other active linters, and there is none here
def file_extension_variables(linter, good_file, bad_file):
    if not linter.lint_all_other_linters_files or linter.file_extensions:
        return {}
    extensions = {os.path.splitext(path)[1] for path in (good_file, bad_file)}
    return {f"{linter.name}_FILE_EXTENSIONS": ",".join(sorted(extensions))}


def classify(linter):
    outcome, detail = classify_output(linter)
    if outcome in ("unclear", "broken"):
        sample = " ".join(str(linter.stdout or "").split())[-OUTPUT_SAMPLE_CHARS:]
        detail = f"{detail}. Output: {sample}"
    return outcome, detail


def classify_output(linter):
    output = f"{linter.stdout_human or ''}\n{linter.stdout or ''}".replace("\\", "/")
    not_linted = len(linter.windows_files_not_linted)
    categories = [tip.get("category") for tip in linter.tips]
    if long_command.is_launch_failure(output) or (
        not_linted == 0 and "windows_command_line" in categories
    ):
        return "broken", "the linter could not start"
    if not_linted > 0:
        if FIRST_FILE_FOLDER in output:
            return "truncated", f"{not_linted} files skipped and reported"
        if linter.number_errors > 0:
            return "unclear", f"{not_linted} files skipped, output names no file"
        return "broken", "truncated run found nothing in the failing first file"
    if LAST_FILE_FOLDER in output:
        return "all_files", "last file of the list reported"
    if linter.number_errors > 0:
        return "unclear", "the linter failed, but its output names no file"
    return "broken", "the linter found nothing in the failing files"


def run_one(key, output_file):
    result = {"key": key, "files": 0, "not_linted": 0}
    try:
        result.update(lint_generated_workspace(key))
    except unittest.SkipTest as e:
        result.update({"outcome": "skipped", "detail": str(e)})
    except Exception as e:  # pylint: disable=broad-except
        logging.exception(f"{key} failed")
        result.update({"outcome": "broken", "detail": f"{type(e).__name__}: {e}"})
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f)


def lint_generated_workspace(key):
    spec = next(spec for spec in load_native_specs(only={key}) if spec.key == key)
    request_id = str(uuid.uuid1())
    utilstest.linter_test_setup({"request_id": request_id})
    linter = utilstest.attach_native_toolchain(
        linter_factory.build_linter(
            spec.descriptor_id,
            spec.linter_name,
            {
                "default_linter_activation": True,
                "enable_descriptors": [],
                "enable_linters": [],
                "disable_descriptors": [],
                "disable_linters": [],
                "disable_errors_linters": [],
                "github_workspace": ".",
                "post_linter_status": True,
                "request_id": request_id,
            },
        )
    )
    good_file = find_fixture(linter, "good")
    bad_file = find_fixture(linter, "bad")
    if good_file is None or bad_file is None:
        raise unittest.SkipTest("no good and bad fixtures of its file type")
    # A server started by the linter (ex: npm-groovy-lint) can keep the folder open
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        workspace = os.path.join(folder, "w")
        os.makedirs(workspace)
        generated = build_workspace(linter, workspace, good_file, bad_file)
        mega_linter, _output = utilstest.call_mega_linter(
            {
                "DEFAULT_WORKSPACE": workspace,
                "FILTER_REGEX_INCLUDE": FILES_FOLDER,
                "TEXT_REPORTER": "true",
                "UPDATED_SOURCES_REPORTER": "false",
                "REPORT_OUTPUT_FOLDER": os.path.join(folder, "reports"),
                "ENABLE_LINTERS": linter.name,
                "LINTER_TIMEOUT_SECONDS": str(LINTER_TIMEOUT_SECONDS),
                "GITHUB_COMMENT_REPORTER": "false",
                "GITHUB_STATUS_REPORTER": "false",
                "request_id": request_id,
                **activation_variables(linter),
                **file_extension_variables(linter, good_file, bad_file),
                **linter.test_variables,
            }
        )
        if len(mega_linter.linters) == 0:
            raise unittest.SkipTest("not activated on the generated workspace")
        linted = mega_linter.linters[0]
        outcome, detail = classify(linted)
    return {
        "outcome": outcome,
        "detail": detail,
        "files": generated,
        "not_linted": len(linted.windows_files_not_linted),
    }


def run(keys, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for key in keys:
        output_file = os.path.join(output_folder, f"{key}.json")
        logging.info(f"::group::{key}")
        try:
            subprocess.run(
                [
                    sys.executable,
                    os.path.abspath(__file__),
                    "run-one",
                    key,
                    output_file,
                ],
                check=False,
                timeout=PROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            logging.error(f"{key} timed out")
        if not os.path.isfile(output_file):
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "key": key,
                        "outcome": "broken",
                        "detail": "the run did not complete",
                        "files": 0,
                        "not_linted": 0,
                    },
                    f,
                )
        logging.info("::endgroup::")
        with open(output_file, "r", encoding="utf-8") as f:
            result = json.load(f)
        logging.info(f"{key}: {result['outcome']} ({result.get('detail', '')})")


def summary(input_folder):
    results = []
    for path in glob.glob(os.path.join(input_folder, "**", "*.json"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            results.append(json.load(f))
    results.sort(key=lambda r: (OUTCOMES.index(r["outcome"]), r["key"]))
    counts = ", ".join(
        f"{outcome}: {sum(r['outcome'] == outcome for r in results)}"
        for outcome in OUTCOMES
    )
    lines = [
        "## Native linters above the Windows command line limit",
        "",
        counts,
        "",
        "| Linter | Outcome | Files | Skipped | Detail |",
        "|:--|:--|--:|--:|:--|",
    ]
    for r in results:
        detail = str(r.get("detail", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {r['key']} | {r['outcome']} | {r['files']} | {r['not_linted']} | {detail[:420]} |"
        )
    text = "\n".join(lines) + "\n"
    logging.info(text)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write(text)
    return 1 if any(r["outcome"] == "broken" for r in results) else 0


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    matrix = commands.add_parser("matrix")
    matrix.add_argument("--shard-size", type=int, default=8)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--linters", required=True)
    run_parser.add_argument("--output", required=True)
    run_one_parser = commands.add_parser("run-one")
    run_one_parser.add_argument("key")
    run_one_parser.add_argument("output")
    summary_parser = commands.add_parser("summary")
    summary_parser.add_argument("--input", required=True)
    arguments = parser.parse_args(argv)
    if arguments.command == "matrix":
        value = build_matrix(
            arguments.shard_size, "windows/amd64", only_keys=list_of_files_keys()
        )
        sys.stdout.write(json.dumps(value) + "\n")
    elif arguments.command == "run":
        run([key for key in arguments.linters.split(",") if key], arguments.output)
    elif arguments.command == "run-one":
        run_one(arguments.key, arguments.output)
    else:
        return summary(arguments.input)
    return 0


if __name__ == "__main__":
    sys.exit(main())
