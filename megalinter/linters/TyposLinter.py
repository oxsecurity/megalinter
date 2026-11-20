#!/usr/bin/env python3

import json

from megalinter import Linter, config


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
