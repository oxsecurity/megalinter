#!/usr/bin/env python3
"""Use Eslint to check so many file formats :)"""

import os

from megalinter import Linter, config


class EslintLinter(Linter):
    FLAT_CONFIG_FILES = (
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
    )

    ESLINTRC_FILES = (
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.cjs",
        ".eslintrc.mjs",
        ".eslintrc.json",
        ".eslintrc.yml",
        ".eslintrc.yaml",
    )

    def _parse_bool(self, value, default=False) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        value_str = str(value).strip().lower()
        if value_str in ("1", "true", "yes", "y", "on"):
            return True
        if value_str in ("0", "false", "no", "n", "off"):
            return False
        return default

    def _workspace_has_any_file(self, filenames) -> bool:
        for filename in filenames:
            if os.path.isfile(os.path.join(self.workspace, filename)):
                return True
        return False

    def _eslint_major_version(self):
        version = self.get_linter_version()
        if version in (None, "", "ERROR"):
            return None
        try:
            return int(str(version).split(".")[0])
        except Exception:
            return None

    def _eslint_has_abandoned_eslintrc_support(self) -> bool:
        help_txt = self.get_linter_help()
        if help_txt in (None, "", "ERROR"):
            return False
        help_lower = str(help_txt).lower()
        # Heuristic: if the CLI no longer mentions legacy config, assume eslintrc is gone.
        return (
            "--no-eslintrc" not in help_lower
            and ".eslintrc" not in help_lower
            and "eslintrc" not in help_lower
        )

    def _user_set_config_file_variable(self) -> bool:
        # Mirrors Linter.load_config_vars resolution order.
        return (
            config.exists(self.request_id, f"{self.name}_CONFIG_FILE")
            or config.exists(self.request_id, f"{self.descriptor_id}_CONFIG_FILE")
            or config.exists(self.request_id, f"{self.name}_FILE_NAME")
            or config.exists(self.request_id, f"{self.descriptor_id}_FILE_NAME")
        )

    def _config_file_name_is_flat(self) -> bool:
        return self.config_file_name in self.FLAT_CONFIG_FILES

    def is_flat_config(self) -> bool:
        """Decide whether to use ESLint flat config (eslint.config.*) or legacy eslintrc.
        Implements the decision tree described in the user-provided flowchart.
        """

        # q0: Has the current ESLint version abandoned eslintrc support?
        if self._eslint_has_abandoned_eslintrc_support():
            return True

        # q1: Is the 'JAVASCRIPT_ES_USE_FLAT_CONFIG' configuration variable set?
        if config.exists(self.request_id, "JAVASCRIPT_ES_USE_FLAT_CONFIG"):
            return self._parse_bool(
                config.get(self.request_id, "JAVASCRIPT_ES_USE_FLAT_CONFIG"),
                default=False,
            )

        # q2: Is the environment variable 'ESLINT_USE_FLAT_CONFIG' set?
        if "ESLINT_USE_FLAT_CONFIG" in os.environ:
            return self._parse_bool(
                os.environ.get("ESLINT_USE_FLAT_CONFIG"), default=False
            )

        eslint_major = self._eslint_major_version()

        # q3: Is the configuration variable 'JAVASCRIPT_ES_CONFIG_FILE' set?
        if self._user_set_config_file_variable():
            # y3q1: Is it eslint.config.{js, cjs, mjs}?
            if self._config_file_name_is_flat():
                return True
            # y3n1q1: Are we using ESLint 9+?
            return bool(eslint_major is not None and eslint_major >= 9)

        # q4: Is eslint.config.{js, cjs, mjs} in the project root?
        if self._workspace_has_any_file(self.FLAT_CONFIG_FILES):
            return True

        # q5: Is .eslintrc* in the project root?
        if self._workspace_has_any_file(self.ESLINTRC_FILES):
            return False

        # Fallback: y3n1q1: Are we using ESLint 9+?
        return bool(eslint_major is not None and eslint_major >= 9)

    def _strip_megalinter_config_arg_if_any(self, cmd):
        """Remove the config arg added by MegaLinter (not user-provided), if present."""
        if not isinstance(cmd, list) or not cmd:
            return cmd
        if not getattr(self, "final_config_file", None):
            return cmd

        # Case 1: arg is like "--config=" or "--config:"
        if self.cli_config_arg_name.endswith("=") or self.cli_config_arg_name.endswith(
            ":"
        ):
            needle = f"{self.cli_config_arg_name}{self.final_config_file}"
            cmd = [a for a in cmd if a != needle]
            return cmd

        # Case 2: arg is separate token like "-c <file>"
        i = 0
        while i < len(cmd):
            if cmd[i] == self.cli_config_arg_name and i + 1 < len(cmd):
                if cmd[i + 1] == self.final_config_file:
                    cmd.pop(i)  # remove arg
                    cmd.pop(i)  # remove value (same index after pop)
                    continue
            i += 1
        return cmd

    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Handle flat config vs eslintrc
        if self.is_flat_config():
            # If flat config is selected but we're not explicitly pointing ESLint at a flat config file,
            # avoid forcing a legacy config file (usually coming from MegaLinter default rules).
            if not self._config_file_name_is_flat():
                cmd = self._strip_megalinter_config_arg_if_any(cmd)

            # Remove flags that are incompatible with flat config
            cmd = list(filter(lambda a: a not in ["--no-eslintrc", "--no-ignore"], cmd))
            # Remove --ignore-path and its value
            if "--ignore-path" in cmd:
                idx = cmd.index("--ignore-path")
                # Remove both --ignore-path and the following path argument
                cmd.pop(idx)
                if idx < len(cmd):
                    cmd.pop(idx)
        else:
            # eslintrc format: Remove --no-ignore if there are arguments about ignoring stuff
            if "--ignore-path" in cmd or "--ignore-pattern" in cmd:
                cmd = list(filter(lambda a: a != "--no-ignore", cmd))

        if self.cli_lint_mode == "project":
            cmd.append(".")

        return cmd
