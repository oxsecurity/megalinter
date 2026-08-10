#!/usr/bin/env python3

from typing import Any

from megalinter.Linter import Linter

# Attributes touched by Linter.run() in project lint mode with SARIF output and
# no pre/post commands/reporters. Shared by linter_test.py and
# secretlint_linter_test.py so the two test files stop hand-maintaining two
# copies of the same knowledge of run()'s attribute surface.
_RUN_STUB_DEFAULTS: dict[str, Any] = {
    "linter_name": "test_linter",
    "name": "TEST_LINTER",
    "unsecured_env_variables": [],
    "reporters": [],
    "pre_commands": None,
    "post_commands": None,
    "master": None,
    "cli_lint_mode": "project",
    "output_sarif": True,
    "sarif_output_file": None,
    "sarif_default_output_file": None,
    "sarif_parse_failed": False,
    "cli_lint_errors_count": None,
    "cli_lint_warnings_count": None,
    "total_number_warnings": 0,
    "total_number_errors": 0,
    "number_errors": 0,
    "status": "success",
    "return_code": 0,
    "remote_config_file_to_delete": None,
    "remote_ignore_file_to_delete": None,
    "disable_errors": False,
    "disable_errors_if_less_than": None,
    "stdout": None,
}


def build_project_run_linter(request_id, linter=None, **overrides):
    if linter is None:
        linter = Linter.__new__(Linter)
    if not hasattr(linter, "request_id"):
        linter.request_id = request_id
    for key, value in _RUN_STUB_DEFAULTS.items():
        if not hasattr(linter, key):
            setattr(linter, key, value)
    for key, value in overrides.items():
        setattr(linter, key, value)
    return linter
