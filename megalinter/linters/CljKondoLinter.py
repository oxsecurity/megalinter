#!/usr/bin/env python3
"""
Use clj-kondo to check Clojure files
"""

import re

from megalinter import Linter


class CljKondoLinter(Linter):
    # Forward excluded directories through an inline EDN config, which
    # clj-kondo deep-merges on top of the project config. Skipped when a
    # --config file is already passed, as repeated --config flags are not a
    # documented merge path
    def manage_excluded_directories_config(self, cmd):
        if "--config" in cmd:
            return cmd
        # The directory name is a literal, not a pattern: escape it so that the
        # dot of a name like "cdk.out" stays a dot instead of matching any
        # character. The backslashes are doubled because the regex travels
        # inside an EDN string, whose reader only accepts a short list of
        # escape sequences
        exclude_regexes = " ".join(
            '"(^|/)' + re.escape(excluded_dir).replace("\\", "\\\\") + '/"'
            for excluded_dir in self.get_project_exclude_directories()
        )
        cmd += ["--config", "{:exclude-files [" + exclude_regexes + "]}"]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through an "
            f"inline merged --config exclude-files entry "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
