#!/usr/bin/env python3
"""
Use Eslint to check so many file formats :)
"""

import json
import logging
import os

from megalinter import Linter
from megalinter.utils_reporter import register_user_notification

LEGACY_ESLINTRC_FILES = (
    ".eslintrc",
    ".eslintrc.json",
    ".eslintrc.yml",
    ".eslintrc.yaml",
    ".eslintrc.js",
    ".eslintrc.cjs",
)

FLAT_ESLINT_FILES = (
    "eslint.config.js",
    "eslint.config.mjs",
    "eslint.config.cjs",
    "eslint.config.ts",
    "eslint.config.mts",
    "eslint.config.cts",
)

ESLINT_FLAT_CONFIG_MIGRATION_URL = (
    "https://eslint.org/docs/latest/use/configure/migration-guide"
)

ESLINT10_NOTIFICATION_KEY = "eslint10_flat_config_migration"
ESLINT10_NOTIFICATION_TEMPLATE = (
    "⚠️ **ESLint v10 flat-config migration required** — "
    "the following linters are disabled until you migrate: {values}. "
    "Only legacy `{legacy_config}` was detected; ESLint v10 dropped support "
    "for the `.eslintrc.*` format. Please migrate to `eslint.config.mjs`. "
    "See the [ESLint migration guide]({migration_url})."
)


class EslintLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super().__init__(params, linter_config)
        self._gate_on_eslint10_config(params)

    # ESLint v10 dropped support for the legacy ".eslintrc.*" format.
    # If only a legacy config is found, disable the linter and surface a
    # migration notice (also propagated to the master so PR reporters can
    # include it in their summary).
    def _gate_on_eslint10_config(self, params):
        workspace = params.get("workspace") if params else None
        if not workspace:
            return

        flat_found = next(
            (
                name
                for name in FLAT_ESLINT_FILES
                if os.path.isfile(os.path.join(workspace, name))
            ),
            None,
        )
        if flat_found is not None:
            return

        legacy_found = next(
            (
                name
                for name in LEGACY_ESLINTRC_FILES
                if os.path.isfile(os.path.join(workspace, name))
            ),
            None,
        )
        if legacy_found is None:
            package_json = os.path.join(workspace, "package.json")
            if os.path.isfile(package_json):
                try:
                    with open(package_json, "r", encoding="utf-8") as fh:
                        package_data = json.load(fh)
                except (OSError, ValueError):
                    package_data = None
                if isinstance(package_data, dict) and "eslintConfig" in package_data:
                    legacy_found = "package.json#eslintConfig"

        if legacy_found is None:
            return

        self.is_active = False
        self.disabled = True
        self.disabled_reason = (
            f"ESLint v10 requires the flat config format. "
            f"Only legacy `{legacy_found}` was found in this repository. "
            f"Migrate to `eslint.config.mjs` ({ESLINT_FLAT_CONFIG_MIGRATION_URL})."
        )
        logging.warning(
            f"[Activation] {self.name} has been disabled: ESLint v10 only supports "
            f"the flat config format (eslint.config.*). Detected legacy "
            f"`{legacy_found}` only. Please migrate. "
            f"See {ESLINT_FLAT_CONFIG_MIGRATION_URL}"
        )

        master = params.get("master") if params else None
        if master is not None:
            register_user_notification(
                master,
                key=ESLINT10_NOTIFICATION_KEY,
                template=ESLINT10_NOTIFICATION_TEMPLATE,
                value=self.name,
                extras={
                    "legacy_config": legacy_found,
                    "migration_url": ESLINT_FLAT_CONFIG_MIGRATION_URL,
                },
            )

    # Drop ESLint v8-only flags that v9 removed.
    # Keep --no-ignore stripping when an explicit ignore source is present.
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)
        cmd = [arg for arg in cmd if arg not in ("--no-eslintrc",)]
        if "--ignore-path" in cmd or "--ignore-pattern" in cmd:
            cmd = list(filter(lambda a: a != "--no-ignore", cmd))
        if self.cli_lint_mode == "project":
            cmd.append(".")
        return cmd
