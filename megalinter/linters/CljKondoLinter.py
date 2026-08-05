#!/usr/bin/env python3
"""
Use clj-kondo to check Clojure files
"""

from megalinter import Linter


class CljKondoLinter(Linter):
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Forward excluded directories in project mode through an inline EDN
        # config, which clj-kondo deep-merges on top of the project config.
        # Skipped when a --config file is already passed, as repeated --config
        # flags are not a documented merge path
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and "--config" not in cmd
        ):
            exclude_regexes = " ".join(
                f'"(^|/){excluded_dir}/"'
                for excluded_dir in self.get_project_exclude_directories()
            )
            cmd += ["--config", "{:exclude-files [" + exclude_regexes + "]}"]
            self.log_project_exclude_forwarding(
                f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through an "
                f"inline merged --config exclude-files entry "
                f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
            )

        return cmd
