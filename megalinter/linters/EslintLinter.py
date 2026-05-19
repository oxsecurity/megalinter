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
    "⛔ **ESLint v10 flat-config migration required** — "
    "the following linters fail until you migrate: {values}. "
    "Legacy `{legacy_config}` was detected; ESLint v10 dropped support "
    "for the `.eslintrc.*` format. Please migrate to `eslint.config.js`. "
    "See the [ESLint migration guide]({migration_url})."
)


class EslintLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        super().__init__(params, linter_config)
        # Independent scan: descriptor's active_only_if_file_found only lists
        # flat configs (v10-native). When a legacy .eslintrc.* is found we
        # force-activate the linter and synthesize a hard error in
        # process_linter() so users are forced to migrate.
        self.eslint10_legacy_config = None
        self._apply_eslint10_migration_gate(params)

    def _apply_eslint10_migration_gate(self, params):
        if params is None:
            return
        workspace = params.get("workspace")
        if not workspace:
            return

        # Respect explicit user disables; never override.
        if self.disabled:
            return
        if self.name in (params.get("disable_linters") or []):
            return
        if self.descriptor_id in (params.get("disable_descriptors") or []):
            return

        # If flat config exists, nothing to do — normal flow.
        if any(
            os.path.isfile(os.path.join(workspace, name))
            for name in FLAT_ESLINT_FILES
        ):
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

        # Force-activate so process_linter() runs and emits a failure.
        self.eslint10_legacy_config = legacy_found
        self.is_active = True
        # No real ESLint is invoked, so don't try to parse SARIF from the synthetic stdout.
        self.output_sarif = False

        logging.warning(
            f"[{self.name}] ESLint v10 only supports flat config. "
            f"Legacy `{legacy_found}` detected — the linter will fail until "
            f"the config is migrated to eslint.config.js. "
            f"See {ESLINT_FLAT_CONFIG_MIGRATION_URL}"
        )

        master = params.get("master")
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

    # When a legacy config is the only one present, short-circuit the
    # real ESLint call and synthesize a single hard error so MegaLinter
    # exits non-zero. The "✖ 1 problem" line matches the descriptor's
    # cli_lint_errors_regex so the error is counted by the normal path.
    def process_linter(self, file=None):
        if self.eslint10_legacy_config:
            message = (
                "ESLint v10 migration required\n"
                "\n"
                f"Legacy `{self.eslint10_legacy_config}` was found but ESLint v10\n"
                "dropped support for the .eslintrc.* format.\n"
                "Migrate to eslint.config.js (flat config):\n"
                f"  {ESLINT_FLAT_CONFIG_MIGRATION_URL}\n"
                "\n"
                "✖ 1 problem (1 error, 0 warnings)\n"
            )
            return 1, message
        return super().process_linter(file)

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
