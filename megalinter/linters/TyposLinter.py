#!/usr/bin/env python3

import json

from megalinter import Linter, config
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRuleBuilder,
    SarifRunBuilder,
    to_one_based,
    to_sarif_uri,
)

TYPOS_RULE_ID = "typo"
TYPOS_URL = "https://github.com/crate-ci/typos"


class TyposLinter(Linter):
    @staticmethod
    def _parse_typo_events(stdout: str | None) -> list[dict]:
        if not stdout:
            return []
        events = []
        for line in stdout.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and obj.get("type") == "typo":
                events.append(obj)
        return events

    @staticmethod
    def _format_typo_event(event: dict) -> str:
        path = "" if event.get("path") is None else event.get("path")
        line_num = "" if event.get("line_num") is None else event.get("line_num")
        byte_offset = (
            "" if event.get("byte_offset") is None else event.get("byte_offset")
        )
        typo = "" if event.get("typo") is None else event.get("typo")
        corrections = event.get("corrections")
        if isinstance(corrections, list) and len(corrections) > 0:
            corrections_text = ", ".join(str(item) for item in corrections)
        else:
            corrections_text = "(no suggestion)"
        return f"{path}:{line_num}:{byte_offset}: `{typo}` -> {corrections_text}"

    def _format_typo_events(self, typos: list[dict]) -> str:
        return "\n".join(self._format_typo_event(event) for event in typos)

    def _parse_and_format_typos(self, stdout: str) -> tuple[list[dict], str]:
        typos = self._parse_typo_events(stdout)
        return typos, self._format_typo_events(typos)

    def process_linter(self, file: str | None = None) -> tuple[int, str]:
        return_code, return_output = super().process_linter(file)
        _, formatted = self._parse_and_format_typos(return_output)
        if file is not None or self.cli_lint_mode == "file":
            if formatted:
                self.stdout_human = (
                    f"{self.stdout_human}\n{formatted}"
                    if self.stdout_human
                    else formatted
                )
        else:
            self.stdout_human = formatted if formatted else None
        return return_code, return_output

    def update_files_lint_results(
        self,
        linted_files: list[str],
        return_code: int | None,
        file_status: str | None,
        stdout: str | None,
        file_errors_number: int | None,
        file_warnings_number: int | None,
    ) -> None:
        if stdout:
            _, formatted = self._parse_and_format_typos(stdout)
            if formatted:
                stdout = formatted
        super().update_files_lint_results(
            linted_files,
            return_code,
            file_status,
            stdout,
            file_errors_number,
            file_warnings_number,
        )

    def get_total_number_errors(self, stdout: str | None) -> int:
        return len(self._parse_typo_events(stdout))

    def get_total_number_warnings(self, stdout: str | None) -> int:
        return 0

    def pre_test(self, test_name: str) -> None:
        config.set_value(
            self.request_id, "SPELL_TYPOS_FILE_EXTENSIONS", [".md", ".py", ".txt"]
        )

    def convert_output_to_sarif(self, return_stdout):
        return typos_output_to_sarif(return_stdout, self.workspace)


# typos has no severity: every finding is an error. byte_offset is 0-based
def typos_output_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple("typos", url=TYPOS_URL)
    run.add_rule(
        SarifRuleBuilder().init_simple(
            TYPOS_RULE_ID,
            short_description_text="Source code spelling mistake",
            help_uri=TYPOS_URL,
        )
    )
    for event in TyposLinter._parse_typo_events(stdout):
        corrections = event.get("corrections")
        suggestion = (
            ", ".join(str(item) for item in corrections)
            if isinstance(corrections, list) and len(corrections) > 0
            else None
        )
        message = f'"{event.get("typo")}" is a typo'
        if suggestion:
            message += f', should be "{suggestion}"'
        run.add_result(
            SarifResultBuilder().init_simple(
                LEVEL_ERROR,
                message,
                TYPOS_RULE_ID,
                file_uri=to_sarif_uri(event.get("path"), workspace),
                start_line=to_one_based(event.get("line_num")),
                start_column=to_one_based(event.get("byte_offset"), zero_based=True),
            )
        )
    return SarifBuilder().add_run(run)
