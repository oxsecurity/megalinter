#!/usr/bin/env python3
"""
Use StyLua to check Lua code formatting
"""

import json

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)


class StyLuaLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return stylua_json_to_sarif(return_stdout, self.workspace)

    # Forward excluded directories through negated glob patterns. Any -g value
    # replaces stylua's default "**/*.lua" + "**/*.luau" includes, so they must
    # be restated before the negations. -g globs are overrides, taking
    # precedence over the ignore files for files: the file patterns of the root
    # .styluaignore and .gitignore are restated as negations so they still apply
    def manage_excluded_directories_config(self, cmd):
        if any(arg in ("-g", "--glob") for arg in cmd):
            return cmd
        cmd += ["-g", "**/*.lua", "-g", "**/*.luau"]
        for ignore_file in [".gitignore", ".styluaignore"]:
            patterns = [
                pattern
                for pattern in self.read_workspace_file_lines(ignore_file)
                if not pattern.startswith("#")
            ]
            if any(pattern.startswith("!") for pattern in patterns):
                # A negation can not be restated as an override: an allowlist
                # (ex: "/*" then "!/src/") would turn into "ignore everything"
                self.log_project_exclude_forwarding(
                    f"The file patterns of {ignore_file} are not restated for "
                    f"{self.linter_name}, as it holds negated (!) patterns"
                )
                continue
            for pattern in patterns:
                cmd += ["-g", f"!{pattern}"]
        for excluded_dir in self.get_project_exclude_directories():
            cmd += ["-g", f"!**/{excluded_dir}/**"]
        self.log_project_exclude_forwarding(
            f"Forwarded EXCLUDED_DIRECTORIES to {self.linter_name} through "
            f"-g negated globs, with the root .styluaignore and .gitignore patterns "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd


# With --output-format json, stylua prints one JSON object per file to format, with
# 0-based lines, and a JSON array of the files that can not be parsed
def stylua_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "stylua", url="https://github.com/JohnnyMorganz/StyLua"
    )
    for line in stdout.splitlines():
        if not line.strip().startswith("{"):
            continue
        try:
            file_result = json.loads(line)
        except ValueError:
            continue
        if not isinstance(file_result, dict) or "mismatches" not in file_result:
            continue
        for mismatch in file_result["mismatches"]:
            run.add_result(
                SarifResultBuilder().init_simple(
                    LEVEL_ERROR,
                    "The code is not formatted as StyLua expects",
                    "formatting",
                    file_uri=to_sarif_uri(file_result["file"], workspace),
                    start_line=to_one_based(
                        mismatch.get("original_start_line"), zero_based=True
                    ),
                    end_line=to_one_based(
                        mismatch.get("original_end_line"), zero_based=True
                    ),
                )
            )
    for errors in utils.find_json_values(stdout, list):
        for error in errors:
            if not isinstance(error, dict) or error.get("type") != "parse_error":
                continue
            location = error.get("location") or {}
            run.add_result(
                SarifResultBuilder().init_simple(
                    LEVEL_ERROR,
                    error.get("message"),
                    "parse-error",
                    file_uri=to_sarif_uri(error.get("filename"), workspace),
                    start_line=to_one_based(location.get("start_line")),
                    start_column=to_one_based(location.get("start_column")),
                    end_line=to_one_based(location.get("end_line")),
                    end_column=to_one_based(location.get("end_column")),
                )
            )
    return SarifBuilder().add_run(run)
