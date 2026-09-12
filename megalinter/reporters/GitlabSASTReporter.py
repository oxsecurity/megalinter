#!/usr/bin/env python3
"""
Produce Gitlab SAST report
"""
import datetime
import json
import logging
import os
import uuid
from json.decoder import JSONDecodeError

from megalinter import Reporter, config, utils
from megalinter.constants import (
    ML_DOC_URL,
    ML_VERSION,
)
from megalinter.flavor_factory import list_flavor_linters
from megalinter.utils import normalize_log_string


class GitlabSASTReporter(Reporter):
    name = "GITLAB_SAST"
    scope = "mega-linter"
    report_type = "simple"

    def __init__(self, params=None):
        # Deactivate JSON output by default
        self.is_active = False
        self.processing_order = -9998  # Run second after sarif reporter
        super().__init__(params)

    def manage_activation(self):
        if not utils.can_write_report_files(self.master):
            self.is_active = False
        elif config.get(self.master.request_id, "SAST_REPORTER", "false") == "true" and config.get(self.master.request_id, "SARIF_REPORTER", "false") == "true":
            self.is_active = True
        # TODO: currently requires sarif reporter. Does this need to change?

    def produce_report(self):
        sast_obj = {}
        sast_obj["version"] = "15.0.7"
        sast_obj["vulnerabilities"] = []
        sast_obj["scan"] = {
            "analyzer": {
                "id": "mega-linter",
                "name": "MegaLinter",
                "url": ML_DOC_URL,
                "vendor": {
                    "name": "OX Security"
                },
                "version": ML_VERSION
            },
            "scanner": {
                "id": "mega-linter",
                "name": "MegaLinter",
                "url": ML_DOC_URL,
                "vendor": {
                    "name": "MegaLinter"
                },
                "version": ML_VERSION
            },
            "type": "sast",
            "start_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), # GET PIPELINE TIME
            "end_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "success"
        }

        # Check delete linter SARIF file if LOG_FILE=none
        keep_sarif_logs = True
        if config.get(self.master.request_id, "LOG_FILE", "") == "none":
            keep_sarif_logs = False
        # Build unique SARIF file with all SARIF output files
        for linter in self.master.linters:
            if linter.name not in list_flavor_linters("security"):
                continue
            linter_sarif_obj = self.load_sarif_file(linter)
            # Delete linter SARIF file if LOG_FILE=none
            if keep_sarif_logs is False and os.path.isfile(
                linter.sarif_output_file
            ):
                os.remove(linter.sarif_output_file)
            if linter_sarif_obj:
                sast_obj["vulnerabilities"] += self.get_vulnerabilities(linter_sarif_obj)

        result_json = json.dumps(sast_obj, sort_keys=True, indent=4)
        # Remove workspace prefix from file names
        result_json = normalize_log_string(result_json)
        # Write output file
        sast_file_name = f"{self.report_folder}{os.path.sep}megalinter-sast.json"
        if os.path.isfile(sast_file_name):
            # Remove from previous run
            os.remove(sast_file_name)
        with open(sast_file_name, "w", encoding="utf-8") as sast_file:
            sast_file.write(result_json)
            logging.info(
                f"[Gitlab SAST Reporter] Generated {self.name} report: {sast_file_name}"
            )

    def load_sarif_file(self, linter):
        # TODO: move this to utils_sarif? same code as the sarif reporter.
        if linter.sarif_output_file is not None and os.path.isfile(
            linter.sarif_output_file
        ):
            # Read SARIF output file
            load_ok = False
            with open(
                linter.sarif_output_file, "r", encoding="utf-8"
            ) as linter_sarif_file:
                # parse sarif file
                try:
                    linter_sarif_obj = json.load(linter_sarif_file)
                    load_ok = True
                except JSONDecodeError as e:
                    # JSON decoding error
                    logging.error(
                        f"[SARIF reporter] ERROR: Unable to decode {linter.name} "
                        f"SARIF file {linter.sarif_output_file}"
                    )
                    logging.error(str(e))
                    logging.debug(
                        f"SARIF File content:\n{linter_sarif_file.read()}"
                    )
                except Exception as e:  # noqa: E722
                    # Other error
                    logging.error(
                        f"[SARIF reporter] ERROR: Unknown error with {linter.name} "
                        f"SARIF file {linter.sarif_output_file}"
                    )
                    logging.error(str(e))
            if load_ok is True:
                return linter_sarif_obj

    def get_vulnerabilities(self, linter_sarif_obj):
        # Initialize an empty list for gitlab vulnerabilities
        gitlab_vulnerabilities = []
        scanner = self.get_scanner(linter_sarif_obj)
        for run in linter_sarif_obj["runs"]:
            for result in run["results"]:
                # Create a dictionary for each gitlab vulnerability
                gitlab_vulnerability = {}
                gitlab_vulnerability["id"] = result.get("ruleId", str(uuid.uuid4()))
                rule = self._find_rule_for_id(gitlab_vulnerability["id"], run)
                if rule:
                    gitlab_vulnerability["description"] = rule.get("fullDescription", rule.get("shortDescription", {})).get("text", "")
                gitlab_vulnerability["category"] = "sast"
                gitlab_vulnerability["name"] = self._parse_message(result["message"].get("text", ""))[:254]
                gitlab_vulnerability["cve"] = ""
                gitlab_vulnerability["severity"] = self.get_severity(result, rule) # Create a mapping for this?
                gitlab_vulnerability["scanner"] = {
                    "id": scanner["id"],
                    "name": scanner["name"]
                }
                gitlab_vulnerability["location"] = self.get_location(result)
                # TODO identifiers?
                gitlab_vulnerability["identifiers"] = self._get_identifiers(gitlab_vulnerability, run)
                gitlab_vulnerabilities.append(gitlab_vulnerability)
        return gitlab_vulnerabilities

    def _get_identifiers(self, vulnerability, linter_sarif_run):
        rule = self._find_rule_for_id(vulnerability["id"], linter_sarif_run)
        identifier = {"type": "MegaLinter ID"}
        if rule:
            identifier["name"] = f"{vulnerability['scanner']['name']} - {rule['id']}"
            identifier["value"] = rule["id"]
            url = rule.get("helpUri", "")
            if url:
                identifier["url"] = url
        identifier["name"] = f"{vulnerability['scanner']['name']} - {vulnerability["id"]}"
        identifier["value"] = vulnerability["id"]
        return [identifier]

    def _find_rule_for_id(self, rule_id, linter_sarif_run):
        for rule in linter_sarif_run["tool"]["driver"].get("rules", []):
            if rule.get("id") == rule_id:
                return rule
        return None

    def _parse_message(self, message):
        if "Message:" in message:
            message = message.split("Message:", 1)[-1]
        return message

    def _map_severity(self, severity):
        if severity.lower() in ["info", "note", "1", "2"]:
            return "Info"
        if severity.lower() in ["low", "3", "4"]:
            return "Low"
        if severity.lower() in ["medium", "warning", "5", "6"]:
            return "Medium"
        if severity.lower() in ["high", "error", "7", "8"]:
            return "High"
        if severity.lower() in ["critical", "9", "10"]:
            return "Critical"
        return None

    def get_severity(self, result, rule):
        if not rule:
            rule = {}

        for possible_severity in [
            result.get("level", ""),
            result.get("properties", {}).get("issue_severity", ""),
            "LOW" if "LOW" in rule.get("properties", {}).get("tags", []) else "",
            "MEDIUM" if "MEDIUM" in rule.get("properties", {}).get("tags", []) else "",
            "HIGH" if "HIGH" in rule.get("properties", {}).get("tags", []) else "",
            rule.get("defaultConfiguration", {}).get("level", ""),
            rule.get("properties", {}).get("security-severity", "").split(".", 1)[0]
        ]:
            severity = self._map_severity(possible_severity)
            if severity:
                return severity
        return "Unknown"

    def get_location(self, result):
        # Only returns the first location.
        for location in result["locations"]:
            physical_location = location.get("physicalLocation", {})
            start_lint = physical_location.get("region", {}).get("startLine", 1)
            return {
                "file": physical_location.get("artifactLocation", {}).get("uri", ""),
                "start_line": start_lint,
                "end_line": physical_location.get("region", {}).get("endLine", start_lint)
            }
        return {}

    def get_scanner(self, linter_sarif_obj):
        # Does ML output more than one run per sarif report?
        for run in linter_sarif_obj["runs"]:
            ml_properties = run.get("properties", {}).get("megalinter", {})
            linter_key = ml_properties.get("linterKey", "")
            return {
                "id": linter_key,
                "name": f"MegaLinter ({linter_key})",
            }
