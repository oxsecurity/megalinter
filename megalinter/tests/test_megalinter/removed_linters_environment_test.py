import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from megalinter import config
from megalinter.MegaLinter import Megalinter


class removed_linters_environment_test(unittest.TestCase):
    def notifications(self, environment=None, files=None, params=None, workspace=True):
        request_id = str(uuid4())
        with tempfile.TemporaryDirectory() as directory:
            for name, content in (files or {}).items():
                Path(directory, name).write_text(content, encoding="utf-8")
            with patch.dict(os.environ, environment or {}, clear=True):
                config.init_config(
                    request_id, directory if workspace else None, params or {}
                )
                master = Megalinter.__new__(Megalinter)
                master.request_id = request_id
                master.enable_linters = config.get_list(
                    request_id, "ENABLE_LINTERS", []
                )
                master.disable_linters = config.get_list(
                    request_id, "DISABLE_LINTERS", []
                )
                master.enable_descriptors = config.get_list(request_id, "ENABLE", [])
                master.disable_descriptors = config.get_list(request_id, "DISABLE", [])
                try:
                    with patch(
                        "megalinter.MegaLinter.register_user_notification"
                    ) as register:
                        master.check_removed_linters_references()
                    return [call.kwargs["value"] for call in register.call_args_list]
                finally:
                    config.delete(request_id)

    def test_unrelated_environment_prefixes_do_not_warn(self):
        for name in (
            "GIT_STRATEGY",
            "GIT_DEPTH",
            "GIT_SUBMODULE_STRATEGY",
            "GIT_DIR",
            "GIT_WORK_TREE",
            "GIT_CONFIG_COUNT",
            "CREDENTIALS_PROFILE",
            "MAKEFILE_HOME",
            "OPENAPI_AUTH",
            "PUPPET_ENVIRONMENT",
        ):
            with self.subTest(variable=name):
                self.assertEqual(self.notifications({name: "value"}), [])

    def test_removed_environment_options_still_warn(self):
        for name, removed in (
            ("GIT_FILTER_REGEX_INCLUDE", "GIT"),
            ("GIT_PRE_COMMANDS", "GIT"),
            ("MAKEFILE_FILTER_REGEX_INCLUDE", "MAKEFILE"),
            ("GIT_GIT_DIFF_ARGUMENTS", "GIT_GIT_DIFF"),
            ("REPOSITORY_GITLEAKS_ARGUMENTS", "REPOSITORY_GITLEAKS"),
        ):
            with self.subTest(variable=name):
                self.assertEqual(self.notifications({name: "value"}), [removed])

    def test_explicit_yaml_key_still_warns_when_also_in_environment(self):
        self.assertEqual(
            self.notifications(
                {"GIT_STRATEGY": "clone"},
                {".mega-linter.yml": "GIT_STRATEGY: fetch\n"},
            ),
            ["GIT"],
        )

    def test_nested_extends_key_still_warns_when_also_in_environment(self):
        self.assertEqual(
            self.notifications(
                {"GIT_CUSTOM_OPTION": "value"},
                {
                    ".mega-linter.yml": "EXTENDS: base.yml\n",
                    "base.yml": "EXTENDS: nested.yml\n",
                    "nested.yml": "GIT_CUSTOM_OPTION: configured\n",
                },
            ),
            ["GIT"],
        )

    def test_explicit_parameters_still_warn(self):
        self.assertEqual(
            self.notifications(params={"GIT_CUSTOM_OPTION": "configured"}), ["GIT"]
        )

    def test_removed_selections_still_warn(self):
        self.assertEqual(
            self.notifications(
                files={
                    ".mega-linter.yml": (
                        "ENABLE: [GIT]\nDISABLE_LINTERS: [REPOSITORY_GITLEAKS]\n"
                    )
                }
            ),
            ["GIT", "REPOSITORY_GITLEAKS"],
        )

    def test_environment_only_without_workspace_does_not_warn(self):
        self.assertEqual(
            self.notifications({"GIT_STRATEGY": "clone"}, workspace=False), []
        )

    def test_explicit_keys_do_not_leak_between_requests(self):
        self.assertEqual(
            self.notifications(params={"GIT_CUSTOM_OPTION": "configured"}), ["GIT"]
        )
        self.assertEqual(self.notifications({"GIT_CUSTOM_OPTION": "value"}), [])
