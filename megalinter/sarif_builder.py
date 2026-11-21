#!/usr/bin/env python3
"""
Build SARIF logs for the linters that can not output SARIF by themselves.
API inspired by https://github.com/nvuillam/node-sarif-builder
"""

import json
import os
import re
from urllib.parse import unquote, urlparse

from megalinter.constants import DEFAULT_SARIF_SCHEMA_URI, DEFAULT_SARIF_VERSION
from megalinter.utils import ANSI_ESCAPE_REGEX

LEVEL_ERROR = "error"
LEVEL_WARNING = "warning"
LEVEL_NOTE = "note"

WHOLE_OUTPUT_MAX_LENGTH = 4000

UNIFIED_DIFF_REGEX = re.compile(
    r"^--- (?P<path>[^\t\n]+)(?:\t[^\n]*)?\n\+\+\+ (?P<new_path>[^\n]*)\n@@ -(?P<line>\d+)",
    re.MULTILINE,
)
# isort names the sides of its diff "<file>:before" and "<file>:after"
DIFF_SIDE_SUFFIX_REGEX = re.compile(r":(?:before|after)$")


def to_sarif_uri(path, workspace=None):
    if path is None:
        return None
    uri = str(path).replace("\\", "/")
    if workspace:
        workspace_prefix = (
            os.path.abspath(workspace).replace("\\", "/").rstrip("/") + "/"
        )
        if uri.startswith(workspace_prefix):
            prefix_length = len(workspace_prefix)
            uri = uri[prefix_length:]
    while uri.startswith("./"):
        uri = uri[2:]
    return uri


# Result of a finding parsed by a regex with the named groups path, and optionally
# line and column
def result_from_match(match, workspace, level, message_text, rule_id):
    groups = match.groupdict()
    return SarifResultBuilder().init_simple(
        level,
        message_text,
        rule_id,
        file_uri=to_sarif_uri(groups["path"], workspace),
        start_line=int(groups["line"]) if groups.get("line") else None,
        start_column=int(groups["column"]) if groups.get("column") else None,
    )


def strip_ansi(text):
    return ANSI_ESCAPE_REGEX.sub("", text)


# Position (line, column) of a linter, as a SARIF 1-based number, or None when the
# linter did not give a valid one
def to_one_based(value, zero_based=False):
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    position = value + 1 if zero_based else value
    return position if position >= 1 else None


# Path of a file:// URI, as given by the linters that report their files that way
def file_uri_to_path(uri):
    path = unquote(urlparse(uri).path)
    return path[1:] if re.match(r"^/[A-Za-z]:/", path) else path


def sarif_from_results(tool_name, results, url=None):
    run = SarifRunBuilder().init_simple(tool_name, url=url)
    for result in results:
        run.add_result(result)
    return SarifBuilder().add_run(run)


# SARIF of a linter whose findings are lines of text matched by a regex with the
# named groups path, line, column, end_column, rule, severity, message and cell
def regex_output_to_sarif(
    stdout,
    workspace,
    tool_name,
    regex,
    default_rule_id,
    default_level=LEVEL_ERROR,
    levels=None,
    url=None,
    default_message=None,
    unified_diff=False,
):
    run = SarifRunBuilder().init_simple(tool_name, url=url)
    if regex:
        levels = levels or {}
        for match in re.finditer(regex, strip_ansi(stdout), re.MULTILINE):
            groups = match.groupdict()
            message_text = (groups.get("message") or default_message or "").strip()
            if groups.get("cell"):
                message_text = f"cell {groups['cell']}: {message_text}"
            level = levels.get(groups.get("severity"), default_level)
            run.add_result(
                SarifResultBuilder().init_simple(
                    level,
                    message_text,
                    (groups.get("rule") or "").strip() or default_rule_id,
                    file_uri=to_sarif_uri(groups["path"].strip(), workspace),
                    start_line=int(groups["line"]) if groups.get("line") else None,
                    start_column=(
                        int(groups["column"]) if groups.get("column") else None
                    ),
                    end_column=(
                        int(groups["end_column"]) if groups.get("end_column") else None
                    ),
                )
            )
    if unified_diff:
        for result in unified_diff_to_results(
            stdout,
            workspace,
            default_level,
            default_message or f"The file is not formatted as {tool_name} expects",
            default_rule_id,
        ):
            run.add_result(result)
    return SarifBuilder().add_run(run)


# A failed run whose output could not be converted still gives one result, without
# location, so that the failure is not lost
def add_whole_output_result(
    sarif_builder, stdout, return_code, rule_id, level=LEVEL_ERROR
):
    if any(len(run.results) > 0 for run in sarif_builder.runs):
        return
    message_text = strip_ansi(stdout or "").strip()
    if return_code in (0, None) or message_text == "" or len(sarif_builder.runs) == 0:
        return
    sarif_builder.runs[0].add_result(
        SarifResultBuilder().init_simple(
            level, message_text[:WHOLE_OUTPUT_MAX_LENGTH], rule_id
        )
    )


# One result per file in the unified diff printed by a linter that checks formatting,
# located at the first modified hunk
def unified_diff_to_results(stdout, workspace, level, message_text, rule_id):
    results = []
    for match in UNIFIED_DIFF_REGEX.finditer(strip_ansi(stdout)):
        path = DIFF_SIDE_SUFFIX_REGEX.sub("", match.group("path").strip())
        new_path = DIFF_SIDE_SUFFIX_REGEX.sub(
            "", match.group("new_path").split("\t")[0].strip()
        )
        # shfmt compares a "<file>.orig" copy with the file
        if path == new_path + ".orig":
            path = new_path
        # git style diffs prefix the paths with a/ and b/ (or old/ and new/)
        if path.startswith(("a/", "old/")) and new_path.startswith(("b/", "new/")):
            path = path.split("/", 1)[1]
            # Some tools remove the leading slash of an absolute path
            if workspace and ("/" + path).startswith(
                os.path.abspath(workspace).replace("\\", "/").rstrip("/") + "/"
            ):
                path = "/" + path
        results.append(
            SarifResultBuilder().init_simple(
                level,
                message_text,
                rule_id,
                file_uri=to_sarif_uri(path, workspace),
                start_line=int(match.group("line")),
            )
        )
    return results


class SarifRuleBuilder:
    def __init__(self):
        self.rule = {}

    def init_simple(
        self,
        rule_id,
        short_description_text=None,
        full_description_text=None,
        help_uri=None,
        name=None,
    ):
        self.rule = {"id": rule_id}
        if name:
            self.rule["name"] = name
        if short_description_text:
            self.rule["shortDescription"] = {"text": short_description_text}
        if full_description_text:
            self.rule["fullDescription"] = {"text": full_description_text}
        if help_uri:
            self.rule["helpUri"] = help_uri
        return self


class SarifResultBuilder:
    def __init__(self):
        self.result = {}

    # Line and column numbers lower than 1 are invalid in SARIF
    def init_simple(
        self,
        level,
        message_text,
        rule_id,
        file_uri=None,
        start_line=None,
        start_column=None,
        end_line=None,
        end_column=None,
    ):
        self.result = {
            "ruleId": rule_id,
            "level": level,
            "message": {"text": message_text or rule_id},
        }
        if file_uri:
            physical_location = {"artifactLocation": {"uri": file_uri}}
            if start_line is not None:
                region = {"startLine": max(start_line, 1)}
                if start_column is not None:
                    region["startColumn"] = max(start_column, 1)
                if end_line is not None:
                    region["endLine"] = max(end_line, region["startLine"])
                if end_column is not None:
                    region["endColumn"] = max(end_column, 1)
                    if (
                        region.get("endLine", region["startLine"])
                        == region["startLine"]
                        and "startColumn" in region
                    ):
                        region["endColumn"] = max(
                            region["endColumn"], region["startColumn"]
                        )
                physical_location["region"] = region
            self.result["locations"] = [{"physicalLocation": physical_location}]
        return self


class SarifRunBuilder:
    def __init__(self):
        self.driver = {}
        self.rules = []
        self.rule_indexes = {}
        self.results = []

    def init_simple(self, tool_driver_name, tool_driver_version=None, url=None):
        self.driver = {"name": tool_driver_name}
        if tool_driver_version:
            self.driver["version"] = tool_driver_version
        if url:
            self.driver["informationUri"] = url
        return self

    # Adding a rule twice keeps the first one. Returns the index of the rule
    def add_rule(self, rule_builder):
        rule_id = rule_builder.rule["id"]
        if rule_id not in self.rule_indexes:
            self.rule_indexes[rule_id] = len(self.rules)
            self.rules.append(rule_builder.rule)
        return self.rule_indexes[rule_id]

    # A result whose rule has not been added gets a rule with only its id
    def add_result(self, result_builder):
        result = dict(result_builder.result)
        result["ruleIndex"] = self.add_rule(
            SarifRuleBuilder().init_simple(result["ruleId"])
        )
        self.results.append(result)
        return self

    def build(self):
        return {
            "tool": {"driver": {**self.driver, "rules": self.rules}},
            "results": self.results,
        }


class SarifBuilder:
    def __init__(self):
        self.runs = []

    def add_run(self, run_builder):
        self.runs.append(run_builder)
        return self

    def build_sarif_output(self):
        return {
            "$schema": DEFAULT_SARIF_SCHEMA_URI,
            "version": DEFAULT_SARIF_VERSION,
            "runs": [run.build() for run in self.runs],
        }

    def build_sarif_json_string(self, indent=2):
        return json.dumps(self.build_sarif_output(), indent=indent)
