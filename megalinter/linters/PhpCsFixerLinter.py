#!/usr/bin/env python3
"""
Use PHP CS Fixer to check PHP code formatting
"""

import re

from megalinter import Linter, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    strip_ansi,
    to_sarif_uri,
)


def _php_single_quoted(value):
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


PHP_CS_FIXER_HUNK_REGEX = re.compile(r"^@@ -(?P<line>\d+)", re.MULTILINE)
PHP_CS_FIXER_NOT_FIXED_REGEX = re.compile(
    r"^(?P<reason>Files that were not fixed due to errors.*?):?$"
    r"(?P<files>(?:\n\s+\d+\) .+)+)",
    re.MULTILINE,
)
PHP_CS_FIXER_NOT_FIXED_FILE_REGEX = re.compile(r"^\s+\d+\) (?P<path>.+)$", re.MULTILINE)


class PhpCsFixerLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return php_cs_fixer_json_to_sarif(return_stdout, self.workspace)

    # Forward excluded directories through a generated PHP config requiring
    # the resolved one and chaining Finder exclusions. Only applied when a
    # config is passed: php-cs-fixer configs are code, so there is no
    # resolved file to extend otherwise
    def manage_excluded_directories_config(self, cmd):
        config_index = self.find_cli_argument_value_index(cmd, ("--config",))
        if config_index is None:
            return cmd
        included_config = cmd[config_index].replace("\\", "/")
        exclude_dirs = ", ".join(
            _php_single_quoted(excluded_dir)
            for excluded_dir in self.get_project_exclude_directories()
        )
        generated_config = self.write_report_generated_file(
            "php-cs-fixer-config.php",
            [
                "<?php",
                "",
                f"$config = require {_php_single_quoted(included_config)};",
                # setFinder() also accepts plain iterables, which have no exclude()
                "$finder = $config->getFinder();",
                "if ($finder instanceof \\Symfony\\Component\\Finder\\Finder) {",
                f"    $finder->exclude([{exclude_dirs}]);",
                "}",
                "return $config;",
            ],
        )
        cmd[config_index] = generated_config
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} chaining {included_config} with "
            f"EXCLUDED_DIRECTORIES as Finder exclusions "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
        return cmd


# php-cs-fixer gives the fixers applied to each file and the diff of all of them: each
# fixer is a result, located at the first hunk of the diff. A file with a syntax error
# is not fixed, and only listed after the report
def php_cs_fixer_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple("php-cs-fixer", url="https://cs.symfony.com/")
    for output in utils.find_json_values(
        stdout, dict, lambda value: isinstance(value.get("files"), list)
    ):
        for file_result in output["files"]:
            hunk = PHP_CS_FIXER_HUNK_REGEX.search(file_result.get("diff") or "")
            for fixer in file_result.get("appliedFixers") or ["php-cs-fixer"]:
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_ERROR,
                        f"Found violation(s) of type: {fixer}",
                        fixer,
                        file_uri=to_sarif_uri(file_result["name"], workspace),
                        start_line=int(hunk.group("line")) if hunk else None,
                    )
                )
    for not_fixed in PHP_CS_FIXER_NOT_FIXED_REGEX.finditer(strip_ansi(stdout)):
        for file in PHP_CS_FIXER_NOT_FIXED_FILE_REGEX.finditer(
            not_fixed.group("files")
        ):
            run.add_result(
                SarifResultBuilder().init_simple(
                    LEVEL_ERROR,
                    not_fixed.group("reason"),
                    "php-cs-fixer-not-fixed",
                    file_uri=to_sarif_uri(file.group("path").strip(), workspace),
                )
            )
    return SarifBuilder().add_run(run)
