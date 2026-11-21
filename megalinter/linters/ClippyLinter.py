#!/usr/bin/env python3
"""
Use Clippy to lint rust files
SARIF is built from the JSON messages of cargo
"""

import json
import logging
import os

import megalinter
from megalinter import config
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)

CLIPPY_LINTS_URL = "https://rust-lang.github.io/rust-clippy/stable/index.html"
RUSTC_ERROR_CODES_URL = "https://doc.rust-lang.org/error_codes"
CLIPPY_LEVELS = {"error": LEVEL_ERROR, "warning": LEVEL_WARNING}


class ClippyLinter(megalinter.Linter):
    def convert_output_to_sarif(self, return_stdout):
        return clippy_json_to_sarif(return_stdout, self.workspace)

    # To execute before linting files
    def before_lint_files(self):
        # Native mode: never change the default toolchain of the user's rustup
        if self.native_toolchain is not None:
            return
        # The image installs a single pinned toolchain and makes it the default
        # in RUSTUP_HOME: switching to "stable" there would download a second one
        rustup_home = config.get(
            self.request_id,
            "RUSTUP_HOME",
            os.path.expandvars("${HOME}/.rustup"),
        )
        rustup_settings = os.path.join(rustup_home, "settings.toml")
        if not os.path.isfile(rustup_settings):
            rustup_init_command = 'echo "Init RUST toolkit" && rustup default stable'
            if self.pre_commands is None:
                self.pre_commands = []
            # Add to pre-commands
            logging.debug("clippy before_lint_files: " + rustup_init_command)
            self.pre_commands.append(
                {"command": rustup_init_command, "cwd": self.workspace}
            )
        else:
            logging.debug("RUST settings found: " + rustup_settings)


def clippy_rule_help_uri(code):
    if code.startswith("clippy::"):
        return f"{CLIPPY_LINTS_URL}#{code[len('clippy::'):]}"
    if len(code) == 5 and code[0] == "E" and code[1:].isdigit():
        return f"{RUSTC_ERROR_CODES_URL}/{code}.html"
    return None


# Diagnostics of cargo --message-format=json, one JSON message per line
def clippy_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "clippy", url="https://github.com/rust-lang/rust-clippy"
    )
    already_reported = set()
    for line in stdout.splitlines():
        if not line.startswith("{"):
            continue
        try:
            cargo_message = json.loads(line)
        except ValueError:
            continue
        if cargo_message.get("reason") != "compiler-message":
            continue
        diagnostic = cargo_message.get("message", {})
        level = CLIPPY_LEVELS.get(diagnostic.get("level"))
        primary_spans = [
            span for span in diagnostic.get("spans", []) if span.get("is_primary")
        ]
        # Summaries (ex: "3 warnings emitted") have no location
        if level is None or len(primary_spans) == 0:
            continue
        span = primary_spans[0]
        code = (diagnostic.get("code") or {}).get("code") or "rustc"
        text = diagnostic.get("message")
        helps = [
            child["message"]
            for child in diagnostic.get("children", [])
            if child.get("level") == "help" and child.get("message")
        ]
        if helps:
            text += f" ({helps[0]})"
        file_uri = to_sarif_uri(span.get("file_name", ""), workspace)
        report_key = (
            code,
            file_uri,
            span.get("line_start"),
            span.get("column_start"),
            text,
        )
        # The same diagnostic is reported for each target (lib, tests...)
        if report_key in already_reported:
            continue
        already_reported.add(report_key)
        run.add_rule(
            SarifRuleBuilder().init_simple(code, help_uri=clippy_rule_help_uri(code))
        )
        run.add_result(
            SarifResultBuilder().init_simple(
                level,
                text,
                code,
                file_uri=file_uri,
                start_line=span.get("line_start"),
                start_column=span.get("column_start"),
                end_line=span.get("line_end"),
                end_column=span.get("column_end"),
            )
        )
    return SarifBuilder().add_run(run)
