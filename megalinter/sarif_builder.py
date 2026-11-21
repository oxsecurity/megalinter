#!/usr/bin/env python3
"""
Build SARIF logs for the linters that can not output SARIF by themselves.
API inspired by https://github.com/nvuillam/node-sarif-builder
"""

import json
import os

from megalinter.constants import DEFAULT_SARIF_SCHEMA_URI, DEFAULT_SARIF_VERSION

LEVEL_ERROR = "error"
LEVEL_WARNING = "warning"
LEVEL_NOTE = "note"


def to_sarif_uri(path, workspace=None):
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
