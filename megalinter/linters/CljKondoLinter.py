#!/usr/bin/env python3
"""
Use clj-kondo to check Clojure files
"""

import re

from megalinter import Linter


class CljKondoLinter(Linter):
    # Forward excluded directories through an inline EDN config. clj-kondo
    # deep-merges every --config in order on top of the project config, and
    # concatenates vectors: unlike the top-level :exclude-files regex string,
    # which would replace the user one, :output :exclude-files keeps the user
    # patterns. It filters the findings (and the exit code) of the files
    # located in excluded directories, which are still analyzed
    def manage_excluded_directories_config(self, cmd):
        # The directory name is a literal, not a pattern: escape it so that the
        # dot of a name like "cdk.out" stays a dot instead of matching any
        # character. The backslashes are doubled because the regex travels
        # inside an EDN string, whose reader only accepts a short list of
        # escape sequences
        exclude_regexes = " ".join(
            '"(^|/)' + re.escape(excluded_dir).replace("\\", "\\\\") + '/"'
            for excluded_dir in self.get_project_exclude_directories()
        )
        cmd += ["--config", "{:output {:exclude-files [" + exclude_regexes + "]}}"]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through an "
            f"inline merged --config :output :exclude-files entry "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd
