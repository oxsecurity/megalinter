import contextlib
import difflib
import io
import json
import logging
import os
import tempfile
import unittest
import warnings

from megalinter import Megalinter


# Define env variables before any test case
def linter_test_setup(params=None):
    if params is None:
        params = {}
    # Root to lint
    sub_lint_root = params['sub_lint_root'] if 'sub_lint_root' in params \
        else f'{os.path.sep}.automation{os.path.sep}test'
    # TAP Output deactivated by default
    os.environ['OUTPUT_FORMAT'] = 'text'
    os.environ['OUTPUT_DETAIL'] = 'detailed'
    # Root path of default rules
    root_dir = '/tmp/lint' if os.path.exists('/tmp/lint') else os.path.relpath(os.path.relpath(os.path.dirname(
        os.path.abspath(__file__))) + '/../../../..')

    os.environ['VALIDATE_ALL_CODEBASE'] = 'true'
    # Root path of files to lint
    os.environ["DEFAULT_WORKSPACE"] = os.environ["DEFAULT_WORKSPACE"] + sub_lint_root \
        if "DEFAULT_WORKSPACE" in os.environ and os.path.exists(
        os.environ["DEFAULT_WORKSPACE"] + sub_lint_root) else root_dir + sub_lint_root
    assert os.path.exists(os.environ["DEFAULT_WORKSPACE"]), 'DEFAULT_WORKSPACE ' + os.environ[
        "DEFAULT_WORKSPACE"] + ' is not a valid folder'


def print_output(output):
    if 'OUTPUT_DETAILS' in os.environ and os.environ['OUTPUT_DETAILS'] == 'detailed':
        for line in output.splitlines():
            print(line)


def call_super_linter(env_vars):
    prev_environ = os.environ.copy()
    usage_stdout = io.StringIO()
    with contextlib.redirect_stdout(usage_stdout):
        # Set env variables
        for env_var_key, env_var_value in env_vars.items():
            os.environ[env_var_key] = env_var_value
        # Call linter
        super_linter = Megalinter()
        super_linter.run()
        # Set back env variable previous values
        for env_var_key, env_var_value in env_vars.items():
            if env_var_key in prev_environ:
                os.environ[env_var_key] = prev_environ[env_var_key]
            else:
                del os.environ[env_var_key]
    output = usage_stdout.getvalue().strip()
    print_output(output)
    return super_linter, output


def test_linter_success(linter, test_self):
    test_folder = linter.test_folder
    workspace = os.environ["DEFAULT_WORKSPACE"] + os.path.sep + test_folder
    if os.path.exists(workspace + os.path.sep + 'good'):
        workspace = workspace + os.path.sep + 'good'
    linter_name = linter.linter_name
    env_vars = {'DEFAULT_WORKSPACE': workspace,
                'FILTER_REGEX_INCLUDE': "(.*_good_.*|.*\\/good\\/.*)",
                'LOG_LEVEL': 'DEBUG'}
    linter_key = "VALIDATE_" + linter.name
    env_vars[linter_key] = 'true'
    if linter.lint_all_other_linters_files is not False:
        env_vars['VALIDATE_JAVASCRIPT_ES'] = 'true'
    super_linter, output = call_super_linter(env_vars)
    test_self.assertTrue(len(super_linter.linters) > 0,
                         "Linters have been created and run")
    # Check console output
    if linter.cli_lint_mode == 'file':
        if len(linter.file_names) > 0 and len(linter.file_extensions) == 0:
            test_self.assertRegex(output, rf"\[{linter_name}\] .*{linter.file_names[0]}.* - SUCCESS")
        else:
            test_self.assertRegex(output, rf"\[{linter_name}\] .*good.* - SUCCESS")
    else:
        test_self.assertRegex(output, rf"Linted \[{linter.descriptor_id}\] files with \[{linter_name}\] successfully")


def test_linter_failure(linter, test_self):
    test_folder = linter.test_folder
    workspace = os.environ["DEFAULT_WORKSPACE"] + os.path.sep + test_folder
    if os.path.exists(workspace + os.path.sep + 'bad'):
        workspace = workspace + os.path.sep + 'bad'
    linter_name = linter.linter_name
    tmp_report_folder = tempfile.gettempdir()
    env_vars = {'DEFAULT_WORKSPACE': workspace,
                'FILTER_REGEX_INCLUDE': '(.*_bad_.*|.*\\/bad\\/.*)',
                'OUTPUT_FORMAT': 'text',
                'OUTPUT_DETAIL': 'detailed',
                'REPORT_OUTPUT_FOLDER': tmp_report_folder,
                'LOG_LEVEL': 'DEBUG'
                }
    linter_key = "VALIDATE_" + linter.name
    env_vars[linter_key] = 'true'
    if linter.lint_all_other_linters_files is not False:
        env_vars['VALIDATE_JAVASCRIPT_ES'] = 'true'
    super_linter, output = call_super_linter(env_vars)
    # Check linter run
    test_self.assertTrue(len(super_linter.linters) > 0,
                         "Linters have been created and run")
    # Check console output
    if linter.cli_lint_mode == 'file':
        if len(linter.file_names) > 0 and len(linter.file_extensions) == 0:
            test_self.assertRegex(output, rf"\[{linter_name}\] .*{linter.file_names[0]}.* - ERROR")
            test_self.assertNotRegex(output, rf"\[{linter_name}\] .*{linter.file_names[0]}.* - SUCCESS")
        else:
            test_self.assertRegex(output, rf"\[{linter_name}\] .*bad.* - ERROR")
            test_self.assertNotRegex(output, rf"\[{linter_name}\] .*bad.* - SUCCESS")
    else:
        test_self.assertRegex(output, rf"Linted \[{linter.descriptor_id}\] files with \[{linter_name}\]: Found error")
    # Check output log
    text_report_file_name = f"{tmp_report_folder}{os.path.sep}ERROR-mega-linter-{linter.name}.log"
    test_self.assertTrue(os.path.exists(text_report_file_name), f"Unable to find text report {text_report_file_name}")


def test_get_linter_version(linter, test_self):
    # Check linter version
    version = linter.get_linter_version()
    print('[' + linter.linter_name + '] version: ' + version)
    test_self.assertFalse(version == 'ERROR',
                          'Returned version invalid: [' + version + ']')
    # Check linter version cache
    version_cache = linter.get_linter_version()
    test_self.assertTrue(version == version_cache,
                         'Version not found in linter instance cache')
    # Write in linter-versions.json
    root_dir = '/tmp/lint' if os.path.exists('/tmp/lint') else os.path.relpath(os.path.relpath(os.path.dirname(
        os.path.abspath(__file__))) + '/../../../..')
    versions_file = root_dir + os.path.sep + '/linter-versions.json'
    data = {}
    if os.path.exists(versions_file):
        with open(versions_file) as json_file:
            data = json.load(json_file)
    if (linter.linter_name in data and data[linter.linter_name] != version) or linter.linter_name not in data:
        data[linter.linter_name] = version
        with open(versions_file, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)


def test_get_linter_help(linter, test_self):
    # Check linter help
    help_txt = linter.get_linter_help()
    print('[' + linter.linter_name + '] help: ' + help_txt)
    test_self.assertFalse(help_txt == 'ERROR',
                          'Returned help invalid: [' + help_txt + ']')
    # Write in linter-helps.json
    root_dir = '/tmp/lint' if os.path.exists('/tmp/lint') else os.path.relpath(os.path.relpath(os.path.dirname(
        os.path.abspath(__file__))) + '/../../../..')
    helps_file = root_dir + os.path.sep + '/linter-helps.json'
    data = {}
    help_lines = help_txt.split("\n")
    help_lines_clean = []
    for help_line in help_lines:
        line_clean = help_line \
            .replace('\\t', '  ') \
            .replace('\t', '  ') \
            .replace('\\r', '') \
            .replace('\r', '') \
            .replace(r"(\[..m)", '') \
            .replace(r"(\[.m)", '') \
            .rstrip()
        help_lines_clean += [line_clean]
    if os.path.exists(helps_file):
        with open(helps_file) as json_file:
            data = json.load(json_file)
    if (linter.linter_name in data and data[linter.linter_name] != help_lines_clean) or linter.linter_name not in data:
        data[linter.linter_name] = help_lines_clean
        with open(helps_file, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)


def test_linter_report_tap(linter, test_self):
    test_folder = linter.test_folder
    workspace = os.environ["DEFAULT_WORKSPACE"] + '/' + test_folder
    expected_file_name = ''
    # Identify expected report if defined
    reports_with_extension = []
    for ext in linter.file_extensions:
        reports_with_extension += [f"expected-{ext.upper()[1:]}.tap"]
    possible_reports = [f"expected-{linter.name}.tap",
                        f"expected-{linter.descriptor_id}.tap"] + reports_with_extension
    for file_nm in list(dict.fromkeys(possible_reports)):
        if os.path.exists(f"{workspace}{os.path.sep}reports{os.path.sep}{file_nm}"):
            expected_file_name = f"{workspace}{os.path.sep}reports{os.path.sep}{file_nm}"
    if expected_file_name == '':
        raise unittest.SkipTest(f'Expected report not defined in {workspace}{os.path.sep}reports')
    # Call linter
    tmp_report_folder = tempfile.gettempdir()
    env_vars = {'DEFAULT_WORKSPACE': workspace,
                'OUTPUT_FORMAT': 'tap',
                'OUTPUT_DETAIL': 'detailed',
                'REPORT_OUTPUT_FOLDER': tmp_report_folder
                }
    linter_key = "VALIDATE_" + linter.name
    env_vars[linter_key] = 'true'
    super_linter, _output = call_super_linter(env_vars)
    test_self.assertTrue(len(super_linter.linters) > 0,
                         "Linters have been created and run")
    # Check TAP file has been produced
    tmp_tap_file_name = f"{tmp_report_folder}{os.path.sep}mega-linter-{linter.name}.tap"
    test_self.assertTrue(os.path.exists(tmp_tap_file_name),
                         f"TAP report not found {tmp_tap_file_name}")
    # Compare file content
    with open(tmp_tap_file_name, 'r', encoding='utf-8') as f_produced:
        content_produced = f_produced.read()
        with open(expected_file_name, 'r', encoding='utf-8') as f_expected:
            content_expected = f_expected.read()
            diffs = [li for li in difflib.ndiff(content_expected, content_produced) if
                     li[0] != ' ' and li not in ['- \\n', '-  ', '+ \\n', '+  ']]
            if len(diffs) > 0:
                msg = ['Differences with expected TAP\n'
                       f"Produced:\n\n{content_produced}\n\n"
                       f"Expected:\n\n{content_expected}\n\n"
                       f"Diff: ({len(diffs)})\n\n {str(diffs) if len(diffs) < 20 else 'Too many diffs for display'}"]
                warnings.warn(msg[0])
                # Compare just the lines not containing 'message'
                expected_lines = content_expected.splitlines()
                produced_lines = content_produced.splitlines()
                identical_nb = 0
                for expected_idx, expected_line in enumerate(expected_lines):
                    produced_line = produced_lines[expected_idx] if expected_idx < len(
                        produced_lines) else ''
                    if produced_line.strip().startswith('message:'):
                        continue
                    test_self.assertEqual(produced_line, expected_line)
                    identical_nb = identical_nb + 1
                logging.warning('Produced and expected TAP files are different '
                                'only inside the content of [message:] YAML lines.'
                                f'{str(identical_nb)} TAP lines on the total {str(len(expected_lines))} '
                                f'remain perfectly identical :)')


def assert_is_skipped(skipped_item, output, test_self):
    test_self.assertRegex(output,
                          rf"(?<=Skipped linters:)*({skipped_item})(?=.*[\n])",
                          'No trace of skipped item ' + skipped_item + ' in log')
