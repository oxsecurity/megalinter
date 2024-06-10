import contextlib
import difflib
import glob
import io
import json
import logging
import os
import re
import shutil
import tempfile
import unittest
import uuid
from datetime import datetime
from shutil import copytree

from git import Repo
from megalinter import Megalinter, config, utils
from megalinter.constants import (
    DEFAULT_DOCKER_WORKSPACE_DIR,
    DEFAULT_REPORT_FOLDER_NAME,
)

REPO_HOME = (
    DEFAULT_DOCKER_WORKSPACE_DIR
    if os.path.isdir(DEFAULT_DOCKER_WORKSPACE_DIR)
    else os.path.dirname(os.path.abspath(__file__))
    + os.path.sep
    + ".."
    + os.path.sep
    + ".."
    + os.path.sep
    + ".."
    + os.path.sep
    + ".."
)


# Returns root dir depending we are locally or in CI
def get_root_dir():
    root_dir = (
        DEFAULT_DOCKER_WORKSPACE_DIR
        if os.path.isdir(DEFAULT_DOCKER_WORKSPACE_DIR)
        else Repo(__file__, search_parent_directories=True).git.rev_parse(
            "--show-toplevel"
        )
    )
    return root_dir


# Define env variables before any test case
def linter_test_setup(params=None):
    config.delete()
    # Workarounds to avoid wrong test classes to be called
    test_name = os.environ.get("PYTEST_CURRENT_TEST", "")
    test_keywords = os.environ.get("TEST_KEYWORDS", "")
    if (test_keywords == "api_spectral" and "openapi_spectral" in test_name) or (
        test_keywords == "php_phpcs" and "php_phpcsfixer" in test_name
    ):
        raise unittest.SkipTest("This test class should not be run in this campaign")
    if params is None:
        params = {"request_id": str(uuid.uuid1())}
    request_id = params["request_id"]
    # Root to lint
    sub_lint_root = (
        params["sub_lint_root"]
        if "sub_lint_root" in params
        else f"{os.path.sep}.automation{os.path.sep}test"
    )
    # Root path of default rules
    root_dir = get_root_dir()

    workspace = None
    config_file_path = root_dir + sub_lint_root + os.path.sep + ".mega-linter.yml"
    if os.path.isfile(config_file_path):
        workspace = root_dir + sub_lint_root
    elif params.get("required_config_file", False) is True:
        raise Exception(
            f"[test] There should be a .mega-linter.yml file in test folder {config_file_path}"
        )
    config.init_config(request_id, workspace)
    # Ignore report folder
    config.set_value(request_id, "FILTER_REGEX_EXCLUDE", r"\/megalinter-reports\/")
    # TAP Output deactivated by default
    config.set_value(request_id, "OUTPUT_FORMAT", "text")
    config.set_value(request_id, "OUTPUT_DETAIL", "detailed")
    config.set_value(request_id, "PLUGINS", "")
    config.set_value(request_id, "GITHUB_STATUS_REPORTER", "false")
    config.set_value(request_id, "GITHUB_COMMENT_REPORTER", "false")
    config.set_value(request_id, "CONFIG_REPORTER", "false")
    config.set_value(request_id, "FLAVOR_SUGGESTIONS", "false")
    config.set_value(request_id, "IGNORE_GITIGNORED_FILES", "true")
    config.set_value(request_id, "VALIDATE_ALL_CODEBASE", "true")
    config.set_value(request_id, "CLEAR_REPORT_FOLDER", "true")
    config.set_value(request_id, "SARIF_REPORTER", "false")
    if params.get("additional_test_variables"):
        for env_var_key, env_var_value in params.get(
            "additional_test_variables"
        ).items():
            config.set_value(request_id, env_var_key, env_var_value)
    # Root path of files to lint
    config.set_value(
        request_id,
        "DEFAULT_WORKSPACE",
        (
            config.get(request_id, "DEFAULT_WORKSPACE") + sub_lint_root
            if config.exists(request_id, "DEFAULT_WORKSPACE")
            and os.path.isdir(
                config.get(request_id, "DEFAULT_WORKSPACE") + sub_lint_root
            )
            else root_dir + sub_lint_root
        ),
    )
    assert os.path.isdir(config.get(request_id, "DEFAULT_WORKSPACE")), (
        "DEFAULT_WORKSPACE "
        + config.get(request_id, "DEFAULT_WORKSPACE")
        + " is not a valid folder"
    )


def print_output(output):
    if (
        config.exists(None, "OUTPUT_DETAIL")
        and config.get(None, "OUTPUT_DETAIL") == "detailed"
    ):
        for line in output.splitlines():
            print(line)


def call_mega_linter(env_vars):
    usage_stdout = io.StringIO()
    request_id = env_vars["request_id"]
    with contextlib.redirect_stdout(usage_stdout):
        # Set env variables
        for env_var_key, env_var_value in env_vars.items():
            config.set_value(request_id, env_var_key, env_var_value)
        # Call linter
        mega_linter = Megalinter({"request_id": request_id})
        mega_linter.run()
    output = usage_stdout.getvalue().strip()
    print_output(output)
    return mega_linter, output


def test_linter_success(linter, test_self):
    if (
        linter.disabled is True
        or "all" in getattr(linter, "descriptor_flavors_exclude", [])
        # todo: remove when bug is fixed https://github.com/tenable/terrascan/issues/1036
        or linter.linter_name == "terrascan"
    ):
        raise unittest.SkipTest("Linter has been disabled")
    test_folder = linter.test_folder
    workspace = (
        config.get(linter.request_id, "DEFAULT_WORKSPACE") + os.path.sep + test_folder
    )
    # Special cases when files must be copied in a temp directory before being linted
    if os.path.isdir(workspace + os.path.sep + "good"):
        workspace = workspace + os.path.sep + "good"
    workspace = manage_copy_sources(workspace)
    tmp_report_folder = tempfile.gettempdir() + os.path.sep + str(uuid.uuid4())
    assert os.path.isdir(workspace), f"Test folder {workspace} is not existing"
    linter_name = linter.linter_name
    env_vars = {
        "DEFAULT_WORKSPACE": workspace,
        "FILTER_REGEX_INCLUDE": r"(good)",
        "TEXT_REPORTER": "true",
        "UPDATED_SOURCES_REPORTER": "false",
        "REPORT_OUTPUT_FOLDER": tmp_report_folder,
        "LOG_LEVEL": "DEBUG",
        "ENABLE_LINTERS": linter.name,
        "PRINT_ALL_FILES": "true",
        "GITHUB_COMMENT_REPORTER": "false",
        "GITHUB_STATUS_REPORTER": "false",
        "request_id": test_self.request_id,
    }
    env_vars.update(linter.test_variables)
    mega_linter, output = call_mega_linter(env_vars)
    test_self.assertTrue(
        len(mega_linter.linters) > 0, "Linters have been created and run"
    )
    # Check console output
    if linter.cli_lint_mode == "file":
        if len(linter.file_names_regex) > 0 and len(linter.file_extensions) == 0:
            test_self.assertRegex(
                output, rf"\[{linter_name}\] .*{linter.file_names_regex[0]}.* - SUCCESS"
            )
        else:
            test_self.assertRegex(output, rf"\[{linter_name}\] .*good.* - SUCCESS")
    elif (linter.descriptor_id != "SPELL") and (
        linter.linter_name != "php-cs-fixer"
    ):  # This log doesn't appear in SPELL linters
        test_self.assertRegex(
            output,
            rf"Linted \[{linter.descriptor_id}\] files with \[{linter_name}\] successfully",
        )
    # Check text reporter output log
    report_file_name = f"SUCCESS-{linter.name}.log"
    text_report_file = (
        f"{tmp_report_folder}{os.path.sep}linters_logs"
        f"{os.path.sep}{report_file_name}"
    )
    if (
        linter.linter_name != "php-cs-fixer"
    ):  # This log doesn't appear in PHP_PHPCSFIXER linter
        test_self.assertTrue(
            os.path.isfile(text_report_file),
            f"Unable to find text report {text_report_file}",
        )
        copy_logs_for_doc(text_report_file, test_folder, report_file_name)


def test_linter_failure(linter, test_self):
    if (
        (linter.disabled is True)
        or (linter.linter_name in ["dustilock", "syft"])  # ugly
        or ("all" in getattr(linter, "descriptor_flavors_exclude", []))
    ):
        raise unittest.SkipTest("Linter or test has been disabled")
    test_folder = linter.test_folder
    workspace = (
        config.get(linter.request_id, "DEFAULT_WORKSPACE") + os.path.sep + test_folder
    )
    if os.path.isdir(workspace + os.path.sep + "bad"):
        workspace = workspace + os.path.sep + "bad"
    workspace = manage_copy_sources(workspace)
    tmp_report_folder = tempfile.gettempdir() + os.path.sep + str(uuid.uuid4())
    assert os.path.isdir(workspace), f"Test folder {workspace} is not existing"
    if os.path.isfile(workspace + os.path.sep + "no_test_failure"):
        raise unittest.SkipTest(
            f"Skip failure test for {linter}: no_test_failure found in test folder"
        )
    linter_name = linter.linter_name
    env_vars_failure = {
        "DEFAULT_WORKSPACE": workspace,
        "FILTER_REGEX_INCLUDE": r"(bad)",
        "OUTPUT_FORMAT": "text",
        "OUTPUT_DETAIL": "detailed",
        "UPDATED_SOURCES_REPORTER": "false",
        "REPORT_OUTPUT_FOLDER": tmp_report_folder,
        "LOG_LEVEL": "DEBUG",
        "ENABLE_LINTERS": linter.name,
        "GITHUB_COMMENT_REPORTER": "false",
        "GITHUB_STATUS_REPORTER": "false",
        "request_id": test_self.request_id,
    }
    env_vars_failure.update(linter.test_variables)
    mega_linter, output = call_mega_linter(env_vars_failure)
    # Check linter run
    test_self.assertTrue(
        len(mega_linter.linters) > 0, "Linters have been created and run"
    )
    # Check console output
    if linter.cli_lint_mode == "file":
        if len(linter.file_names_regex) > 0 and len(linter.file_extensions) == 0:
            test_self.assertRegex(
                output, rf"\[{linter_name}\] .*{linter.file_names_regex[0]}.* - ERROR"
            )
            test_self.assertNotRegex(
                output, rf"\[{linter_name}\] .*{linter.file_names_regex[0]}.* - SUCCESS"
            )
        else:
            test_self.assertRegex(output, rf"\[{linter_name}\] .*bad.* - ERROR")
            test_self.assertNotRegex(output, rf"\[{linter_name}\] .*bad.* - SUCCESS")
    elif linter.descriptor_id != "SPELL":  # This log doesn't appear in SPELL linters
        test_self.assertRegex(
            output,
            rf"Linted \[{linter.descriptor_id}\] files with \[{linter_name}\]: Found",
        )

    mega_linter_linter = mega_linter.linters[0]

    # Check text reporter output log
    if mega_linter_linter.disable_errors is True:
        report_file_name = f"WARNING-{linter.name}.log"
    else:
        report_file_name = f"ERROR-{linter.name}.log"
    text_report_file = (
        f"{tmp_report_folder}{os.path.sep}linters_logs"
        f"{os.path.sep}{report_file_name}"
    )
    test_self.assertTrue(
        os.path.isfile(text_report_file),
        f"Unable to find text report {text_report_file}",
    )

    # Check if number of errors is correctly generated
    if (
        mega_linter_linter.cli_lint_errors_count is not None
        and mega_linter_linter.linter_name != "mypy"  # ugly
    ):
        test_self.assertTrue(
            mega_linter_linter.total_number_errors > 1,
            "Unable to count number of errors from logs with count method "
            + f"{mega_linter_linter.cli_lint_errors_count} and "
            + f"regex {mega_linter_linter.cli_lint_errors_regex}",
        )

    # Copy error logs in documentation
    copy_logs_for_doc(text_report_file, test_folder, report_file_name)


def manage_copy_sources(workspace):
    if os.path.isfile(workspace + os.path.sep + "test_copy_in_tmp_folder"):
        tmp_sources_folder = tempfile.gettempdir() + os.path.sep + str(uuid.uuid4())
        copytree(workspace, tmp_sources_folder)
        workspace = tmp_sources_folder
    return workspace


# Copy logs for documentation
def copy_logs_for_doc(text_report_file, test_folder, report_file_name):
    updated_sources_dir = (
        f"{REPO_HOME}{os.path.sep}{DEFAULT_REPORT_FOLDER_NAME}{os.path.sep}updated_dev_sources{os.path.sep}"
        f".automation{os.path.sep}test{os.path.sep}{test_folder}{os.path.sep}{DEFAULT_REPORT_FOLDER_NAME}"
    )
    target_file = f"{updated_sources_dir}{os.path.sep}{report_file_name}".replace(
        ".log", ".txt"
    )
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    shutil.copy(text_report_file, target_file)


def test_get_linter_version(linter, test_self):
    if linter.disabled is True or "all" in getattr(
        linter, "descriptor_flavors_exclude", []
    ):
        raise unittest.SkipTest("Linter has been disabled")
    # Check linter version
    version = linter.get_linter_version()
    print("[" + linter.linter_name + "] version: " + version)
    # Ugly workaround to avoid instability of get sql_tsqllint_test version
    if version == "ERROR" and test_self.__class__.__name__ == "sql_tsqllint_test":
        raise unittest.SkipTest("Ugly workaround to avoid sql_tsqllint_test failure")
    # Check version is returned
    test_self.assertFalse(
        version == "ERROR", "Returned version invalid: [" + version + "]"
    )
    # Check linter version cache
    version_cache = linter.get_linter_version()
    test_self.assertTrue(
        version == version_cache, "Version not found in linter instance cache"
    )
    # Write in linter-versions.json
    root_dir = get_root_dir()
    versions_file = (
        root_dir + os.path.sep + "/.automation/generated/linter-versions.json"
    )
    data = {}
    if os.path.isfile(versions_file):
        with open(versions_file, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    if (
        linter.linter_name in data and data[linter.linter_name] != version
    ) or linter.linter_name not in data:
        prev_version = None
        if linter.linter_name in data and data[linter.linter_name] != version:
            prev_version = data[linter.linter_name]
        data[linter.linter_name] = version
        with open(versions_file, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
        # Upgrade version in changelog
        if prev_version is not None:
            changelog_file = root_dir + os.path.sep + "/CHANGELOG.md"
            with open(changelog_file, "r", encoding="utf-8") as md_file:
                changelog_content = md_file.read()
            start = "- Linter versions upgrades"
            end = "<!-- linter-versions-end -->"
            regex = rf"{start}([\s\S]*?){end}"
            existing_text_find = re.findall(regex, changelog_content, re.DOTALL)
            if existing_text_find is None:
                raise Exception(
                    f"CHANGELOG.md must contain a single block scoped by '{start}' and '{end}'"
                )
            versions_text = existing_text_find[0]
            versions_text += (
                f"  - [{linter.linter_name}]({linter.linter_url}) from {prev_version} to **{version}**"
                f" on {datetime.today().strftime('%Y-%m-%d')}\n"
            )
            versions_block = f"{start}{versions_text}{end}"
            changelog_content = re.sub(
                regex, versions_block, changelog_content, re.DOTALL
            )
            with open(changelog_file, "w", encoding="utf-8") as md_file:
                md_file.write(changelog_content)
            logging.info(f"Updated {linter.linter_name} in CHANGELOG.md")


def test_get_linter_help(linter, test_self):
    if linter.disabled is True or "all" in getattr(
        linter, "descriptor_flavors_exclude", []
    ):
        raise unittest.SkipTest("Linter has been disabled")
    # Check linter help
    help_txt = linter.get_linter_help()
    print("[" + linter.linter_name + "] help: " + help_txt)
    # Ugly workaround to avoid instability of get sql_tsqllint_test version
    if help_txt == "ERROR" and test_self.__class__.__name__ == "sql_tsqllint_test":
        raise unittest.SkipTest("Ugly workaround to avoid sql_tsqllint_test failure")
    test_self.assertFalse(
        help_txt == "ERROR", "Returned help invalid: [" + help_txt + "]"
    )
    # Write in linter-helps.json
    root_dir = get_root_dir()
    helps_file = root_dir + os.path.sep + "/.automation/generated/linter-helps.json"
    data = {}
    help_lines = help_txt.splitlines()
    help_lines_clean = []
    for help_line in help_lines:
        line_clean = (
            help_line.replace("\\t", "  ")
            .replace("\t", "  ")
            .replace("\\r", "")
            .replace("\r", "")
            .replace(r"(\[..m)", "")  # pylint: disable=invalid-character-esc
            .replace(r"(\[.m)", "")  # pylint: disable=invalid-character-esc
            .rstrip()
        )
        line_clean = utils.normalize_log_string(line_clean)
        help_lines_clean += [line_clean]
    if os.path.isfile(helps_file):
        with open(helps_file, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    if (
        linter.linter_name in data and data[linter.linter_name] != help_lines_clean
    ) or linter.linter_name not in data:
        data[linter.linter_name] = help_lines_clean
        with open(helps_file, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)


def test_linter_report_tap(linter, test_self):
    if linter.disabled is True or "all" in getattr(
        linter, "descriptor_flavors_exclude", []
    ):
        raise unittest.SkipTest("Linter has been disabled")
    test_folder = linter.test_folder
    workspace = (
        config.get(linter.request_id, "DEFAULT_WORKSPACE") + os.path.sep + test_folder
    )
    assert os.path.isdir(workspace), f"Test folder {workspace} is not existing"
    expected_file_name = ""
    # Identify expected report if defined
    reports_with_extension = []
    for ext in linter.file_extensions:
        reports_with_extension += [f"expected-{ext.upper()[1:]}.tap"]
    possible_reports = [
        f"expected-{linter.name}.tap",
        f"expected-{linter.descriptor_id}.tap",
    ] + reports_with_extension
    for file_nm in list(dict.fromkeys(possible_reports)):
        if os.path.isfile(
            f"{workspace}{os.path.sep}{DEFAULT_REPORT_FOLDER_NAME}{os.path.sep}{file_nm}"
        ):
            expected_file_name = f"{workspace}{os.path.sep}{DEFAULT_REPORT_FOLDER_NAME}{os.path.sep}{file_nm}"
    if expected_file_name == "":
        raise unittest.SkipTest(
            f"Expected report not defined in {workspace}{os.path.sep}{DEFAULT_REPORT_FOLDER_NAME}"
        )
    # Call linter
    tmp_report_folder = tempfile.gettempdir() + os.path.sep + str(uuid.uuid4())
    env_vars = {
        "DEFAULT_WORKSPACE": workspace,
        "OUTPUT_FORMAT": "tap",
        "OUTPUT_DETAIL": "detailed",
        "REPORT_OUTPUT_FOLDER": tmp_report_folder,
        "ENABLE_LINTERS": linter.name,
        "GITHUB_COMMENT_REPORTER": "false",
        "GITHUB_STATUS_REPORTER": "false",
        "request_id": test_self.request_id,
    }
    env_vars.update(linter.test_variables)
    mega_linter, _output = call_mega_linter(env_vars)
    test_self.assertTrue(
        len(mega_linter.linters) > 0, "Linters have been created and run"
    )
    # Check TAP file has been produced
    tmp_tap_file_name = (
        f"{tmp_report_folder}{os.path.sep}tap{os.path.sep}mega-linter-{linter.name}.tap"
    )
    test_self.assertTrue(
        os.path.isfile(tmp_tap_file_name), f"TAP report not found {tmp_tap_file_name}"
    )
    # Compare file content
    with open(tmp_tap_file_name, "r", encoding="utf-8") as f_produced:
        content_produced = f_produced.read()
        with open(expected_file_name, "r", encoding="utf-8") as f_expected:
            content_expected = f_expected.read()
            diffs = [
                li
                for li in difflib.ndiff(content_expected, content_produced)
                if li[0] != " " and li not in ["- \\n", "-  ", "+ \\n", "+  "]
            ]
            if len(diffs) > 0:
                # Compare just the lines not containing 'message'
                expected_lines = content_expected.splitlines()
                produced_lines = content_produced.splitlines()
                identical_nb = 0
                for expected_idx, expected_line in enumerate(expected_lines):
                    produced_line = (
                        produced_lines[expected_idx]
                        if expected_idx < len(produced_lines)
                        else ""
                    )
                    if produced_line.strip().startswith("message:"):
                        continue
                    if "ok " in produced_line:
                        test_self.assertEqual(
                            produced_line.split("-")[0],
                            utils.normalize_log_string(expected_line).split("-")[0],
                        )
                    else:
                        test_self.assertEqual(
                            produced_line, utils.normalize_log_string(expected_line)
                        )
                    identical_nb = identical_nb + 1
                logging.warning(
                    "Produced and expected TAP files are different "
                    "only inside the content of [message:] YAML lines."
                    f"{str(identical_nb)} TAP lines on the total {str(len(expected_lines))} "
                    f"remain perfectly identical :)"
                )


# Test that the linter provides a SARIF output if it's configured like that
def test_linter_report_sarif(linter, test_self):
    if (
        linter.disabled is True
        or "all" in getattr(linter, "descriptor_flavors_exclude", [])
        or linter.can_output_sarif is False
    ):
        raise unittest.SkipTest("SARIF is not configured for this linter")
    test_folder = linter.test_folder
    workspace = (
        config.get(linter.request_id, "DEFAULT_WORKSPACE") + os.path.sep + test_folder
    )
    if linter.cli_lint_mode == "project" and os.path.isdir(
        workspace + os.path.sep + "bad"
    ):
        workspace += os.path.sep + "bad"
    assert os.path.isdir(workspace), f"Test folder {workspace} is not existing"
    # Call linter
    tmp_report_folder = tempfile.gettempdir() + os.path.sep + str(uuid.uuid4())
    env_vars = {
        "DEFAULT_WORKSPACE": workspace,
        "SARIF_REPORTER": "true",
        "REPORT_OUTPUT_FOLDER": tmp_report_folder,
        "ENABLE_LINTERS": linter.name,
        "LOG_LEVEL": "DEBUG",
        "LOG_FILE": "megalinter.log",
        "GITHUB_COMMENT_REPORTER": "false",
        "GITHUB_STATUS_REPORTER": "false",
        "request_id": test_self.request_id,
    }
    env_vars.update(linter.test_variables)
    mega_linter, _output = call_mega_linter(env_vars)
    test_self.assertTrue(
        len(mega_linter.linters) > 0, "Linters have been created and run"
    )
    # Check SARIF file has been produced
    tmp_sarif_file_name = (
        f"{tmp_report_folder}{os.path.sep}sarif{os.path.sep}{linter.name}.sarif"
    )
    test_self.assertTrue(
        os.path.isfile(tmp_sarif_file_name),
        f"SARIF report not found {tmp_sarif_file_name}",
    )
    # Check SARIF file contains appropriate format and runs
    with open(tmp_sarif_file_name, "r", encoding="utf-8") as json_file:
        sarif_content = json.load(json_file)
    test_self.assertTrue(
        "runs" in sarif_content,
        f'Missing property "runs" in {tmp_sarif_file_name}',
    )
    test_self.assertTrue(
        len(sarif_content["runs"]) > 0,
        f"Empty runs list in {tmp_sarif_file_name}",
    )
    # Check number of errors is ok
    for linter in mega_linter.linters:
        if (
            linter.output_sarif is True
            and linter.cli_lint_mode != "file"
            and linter.name
            not in [
                "REPOSITORY_DUSTILOCK",
                "REPOSITORY_SYFT",
            ]
        ):
            test_self.assertTrue(
                linter.total_number_errors > 1,
                f"Missing multiple sarif errors in {linter.name}"
                + f" ({linter.total_number_errors})\n"
                + f"SARIF:{str(sarif_content)}",
            )


def assert_is_skipped(skipped_item, output, test_self):
    test_self.assertRegex(
        output,
        rf"(?<=Skipped linters:)*({skipped_item})(?=.*[\n])",
        "No trace of skipped item " + skipped_item + " in log",
    )


def assert_file_has_been_updated(file_name, bool_val, test_self):
    repo = Repo(os.path.realpath(REPO_HOME))
    changed_files = [item.a_path for item in repo.index.diff(None)]
    logging.info("Updated files (git):\n" + "\n".join(changed_files))
    updated = False
    for changed_file in changed_files:
        if file_name in changed_file:
            updated = True
    if bool_val is True:
        test_self.assertTrue(updated, f"{file_name} has been updated")
    else:
        test_self.assertFalse(updated, f"{file_name} has not been updated")


def test_linter_format_fix(linter, test_self):
    if (
        linter.disabled is True
        or "all" in getattr(linter, "descriptor_flavors_exclude", [])
        or (linter.is_formatter is False and linter.cli_lint_fix_arg_name is None)
    ):
        raise unittest.SkipTest("Linter doesn't format and can't apply fixes")
    test_folder = linter.test_folder
    workspace = (
        config.get(linter.request_id, "DEFAULT_WORKSPACE") + os.path.sep + test_folder
    )
    # Special cases when files must be copied in a temp directory before being linted
    if os.path.isdir(workspace + os.path.sep + "fix"):
        workspace = workspace + os.path.sep + "fix"
    tmp_report_folder = tempfile.gettempdir() + os.path.sep + str(uuid.uuid4())
    assert os.path.isdir(workspace), f"Test folder {workspace} is not existing"

    file_map = {}

    search_glob_pattern = workspace.replace("\\", "/") + "/**/*"

    files = glob.glob(search_glob_pattern, recursive=True)

    filter_regex_exclude = []

    if linter.test_format_fix_regex_exclude is not None:
        filter_regex_exclude = [linter.test_format_fix_regex_exclude]

    file_extensions = linter.file_extensions

    if len(linter.test_format_fix_file_extensions) > 0:
        file_extensions = linter.test_format_fix_file_extensions

    filtered_files = utils.filter_files(
        all_files=files,
        filter_regex_include="_fix_",
        filter_regex_exclude=filter_regex_exclude,
        file_names_regex=[],
        file_extensions=file_extensions,
        ignored_files=[],
        ignore_generated_files=False,
    )

    for file in filtered_files:
        with open(file, "r", encoding="utf-8") as f_expected:
            content_expected = f_expected.read()
            file_map[file] = content_expected

    if len(file_map) == 0:
        raise Exception(f"[test] No files found in: {workspace}")

    linter_name = linter.linter_name
    env_vars = {
        "APPLY_FIXES": linter.name,
        "DEFAULT_WORKSPACE": workspace,
        "FILTER_REGEX_INCLUDE": r"(fix)",
        "TEXT_REPORTER": "true",
        "UPDATED_SOURCES_REPORTER": "false",
        "REPORT_OUTPUT_FOLDER": tmp_report_folder,
        "LOG_LEVEL": "DEBUG",
        "ENABLE_LINTERS": linter.name,
        "PRINT_ALL_FILES": "true",
        "GITHUB_COMMENT_REPORTER": "false",
        "GITHUB_STATUS_REPORTER": "false",
        "SARIF_REPORTER": "false",
        "request_id": test_self.request_id,
    }
    env_vars.update(linter.test_variables)
    mega_linter, output = call_mega_linter(env_vars)
    test_self.assertTrue(
        len(mega_linter.linters) > 0, "Linters have been created and run"
    )
    # Check console output
    if linter.cli_lint_mode == "file":
        if (
            len(linter.file_names_regex) > 0
            and len(linter.test_format_fix_file_extensions) == 0
            and len(linter.file_extensions) == 0
        ):
            test_self.assertRegex(
                output, rf"\[{linter_name}\] .*{linter.file_names_regex[0]}.* - SUCCESS"
            )
        else:
            test_self.assertRegex(output, rf"\[{linter_name}\] .*fix.* - SUCCESS")
    else:
        test_self.assertRegex(
            output,
            rf"Linted \[{linter.descriptor_id}\] files with \[{linter_name}\] successfully",
        )
    # Check text reporter output log
    report_file_name = f"SUCCESS-{linter.name}.log"
    text_report_file = (
        f"{tmp_report_folder}{os.path.sep}linters_logs"
        f"{os.path.sep}{report_file_name}"
    )
    test_self.assertTrue(
        os.path.isfile(text_report_file),
        f"Unable to find text report {text_report_file}",
    )
    copy_logs_for_doc(text_report_file, test_folder, report_file_name)

    repo = Repo(os.path.realpath(REPO_HOME))

    # Check files content
    for file in file_map:
        with open(file, "r", encoding="utf-8") as f_produced:
            content_expected = file_map[file]
            content_produced = f_produced.read()
            diffs = [
                li
                for li in difflib.ndiff(content_expected, content_produced)
                if li[0] != " "
            ]
            assert (len(list(diffs))) > 0, f"No changes in the {file} file"

        repo.index.checkout(
            [os.path.join(os.path.realpath(REPO_HOME), file)], force=True
        )


def write_eslintignore():
    # The file must be in the root of the repository so we create it temporarily for the test.
    # By default eslint ignores files starting with "." so we override this behavior
    # to work with the .automation folder
    with open(
        os.path.join(os.getcwd(), ".eslintignore"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write("!.automation")


def delete_eslintignore():
    os.remove(os.path.join(os.getcwd(), ".eslintignore"))
