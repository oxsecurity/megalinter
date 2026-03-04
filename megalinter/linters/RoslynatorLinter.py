#!/usr/bin/env python3
"""
Use roslynator to lint CSharp files and convert its JSON/XML report to SARIF
so MegaLinter can consume diagnostics from roslynator reports.
"""

import json
import logging
import os
from xml.etree import ElementTree as ET

from megalinter import Linter, utils


class RoslynatorLinter(Linter):
    def process_linter(self, file=None):
        # Ensure project restore is attempted (keeps legacy behavior)
        if file is not None:
            command = f"dotnet restore {file}"
            logging.debug(f"[{self.linter_name}] command: {str(command)}")
            return_code, return_output = self.execute_lint_command(command)
            logging.debug(
                f"[{self.linter_name}] restore result: {str(return_code)} {return_output}"
            )

        # Let base class run the configured linter command (descriptor driven)
        result = super().process_linter(file)

        # After the linter run, try to find roslynator JSON or XML reports
        try:
            report_files = []
            # Common places: report_folder, workspace root
            candidates = []
            if hasattr(self, "report_folder") and self.report_folder:
                candidates.append(self.report_folder)
            if hasattr(self, "workspace") and self.workspace:
                candidates.append(self.workspace)

            for base in candidates:
                try:
                    for f in os.listdir(base):
                        lf = f.lower()
                        if "roslynator" in lf and (
                            lf.endswith(".json") or lf.endswith(".xml")
                        ):
                            report_files.append(os.path.join(base, f))
                except Exception:
                    continue

            # Also scan report_folder subdir
            if hasattr(self, "report_folder") and self.report_folder:
                for root, _, files in os.walk(self.report_folder):
                    for f in files:
                        lf = f.lower()
                        if "roslynator" in lf and (
                            lf.endswith(".json") or lf.endswith(".xml")
                        ):
                            report_files.append(os.path.join(root, f))

            # If any report found, convert the first one to SARIF
            if len(report_files) > 0:
                report = report_files[0]
                logging.info(f"[{self.linter_name}] Found roslynator report: {report}")
                sarif_obj = self._convert_report_to_sarif(report)
                if sarif_obj is not None:
                    # Ensure sarif_output_file path exists (fallback if not set)
                    if self.sarif_output_file is None:
                        self.sarif_output_file = os.path.join(
                            self.report_folder or ".", "sarif", f"{self.name}.sarif"
                        )
                        os.makedirs(
                            os.path.dirname(self.sarif_output_file), exist_ok=True
                        )

                    with open(self.sarif_output_file, "w", encoding="utf-8") as fh:
                        json.dump(sarif_obj, fh, indent=2, sort_keys=True)
                    logging.info(
                        f"[{self.linter_name}] Wrote SARIF: {self.sarif_output_file}"
                    )

        except Exception as e:
            logging.exception(
                f"[{self.linter_name}] Error while converting roslynator report: {e}"
            )

        return result

    def _convert_report_to_sarif(self, report_path):
        """Try to parse roslynator JSON or XML report and build a minimal SARIF object."""
        try:
            if report_path.lower().endswith(".json"):
                with open(report_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                return self._json_to_sarif(data)
            elif report_path.lower().endswith(".xml"):
                tree = ET.parse(report_path)
                root = tree.getroot()
                return self._xml_to_sarif(root)
        except Exception as e:
            logging.exception(
                f"[{self.linter_name}] Failed to parse report {report_path}: {e}"
            )
        return None

    def _json_to_sarif(self, data):
        # Best-effort mapping from roslynator JSON to SARIF
        diagnostics = []
        if isinstance(data, dict):
            # common candidates
            if "diagnostics" in data and isinstance(data["diagnostics"], list):
                diagnostics = data["diagnostics"]
            elif "items" in data and isinstance(data["items"], list):
                diagnostics = data["items"]
            else:
                # maybe top-level is a list
                for v in data.values():
                    if isinstance(v, list):
                        diagnostics = v
                        break
        elif isinstance(data, list):
            diagnostics = data

        results = []
        rules = {}
        for diag in diagnostics:
            try:
                rule_id = (
                    diag.get("id") or diag.get("ruleId") or diag.get("diagnosticId")
                )
                message = (
                    diag.get("message")
                    or diag.get("messageText")
                    or diag.get("title")
                    or str(diag)
                )
                file_path = diag.get("file") or diag.get("filePath") or diag.get("path")
                line = diag.get("line") or diag.get("startLine") or None

                if rule_id:
                    rules.setdefault(
                        rule_id, {"id": rule_id, "shortDescription": {"text": rule_id}}
                    )

                location = None
                if file_path:
                    region = {"startLine": int(line) if line is not None else 1}
                    location = {
                        "physicalLocation": {
                            "artifactLocation": {"uri": file_path},
                            "region": region,
                        }
                    }

                res = {"ruleId": rule_id or "roslynator", "message": {"text": message}}
                if location:
                    res["locations"] = [location]

                results.append(res)
            except Exception:
                continue

        sarif = {
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "roslynator",
                            "version": self.get_linter_version(),
                            "informationUri": getattr(
                                self,
                                "linter_url",
                                "https://github.com/dotnet/Roslynator",
                            ),
                            "rules": list(rules.values()),
                        }
                    },
                    "results": results,
                }
            ],
        }
        return sarif

    def _xml_to_sarif(self, root):
        # Best-effort mapping from XML structure to SARIF. Try to find diagnostic elements.
        diagnostics = []
        for diag in root.iter():
            if diag.tag.lower().endswith("diagnostic") or diag.tag.lower().endswith(
                "issue"
            ):
                diagnostics.append(diag)

        results = []
        rules = {}
        for diag in diagnostics:
            try:
                rule_id = (
                    diag.findtext("id") or diag.findtext("ruleId") or diag.get("id")
                )
                message = (
                    diag.findtext("message")
                    or diag.findtext("messageText")
                    or ET.tostring(diag, encoding="unicode")
                )
                file_path = diag.findtext("file") or diag.findtext("path") or None
                line = diag.findtext("line") or diag.findtext("startLine") or None

                if rule_id:
                    rules.setdefault(
                        rule_id, {"id": rule_id, "shortDescription": {"text": rule_id}}
                    )

                location = None
                if file_path:
                    region = {"startLine": int(line) if line is not None else 1}
                    location = {
                        "physicalLocation": {
                            "artifactLocation": {"uri": file_path},
                            "region": region,
                        }
                    }

                res = {"ruleId": rule_id or "roslynator", "message": {"text": message}}
                if location:
                    res["locations"] = [location]

                results.append(res)
            except Exception:
                continue

        sarif = {
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "roslynator",
                            "version": self.get_linter_version(),
                            "informationUri": getattr(
                                self,
                                "linter_url",
                                "https://github.com/dotnet/Roslynator",
                            ),
                            "rules": list(rules.values()),
                        }
                    },
                    "results": results,
                }
            ],
        }
        return sarif

    # Provide original roslynator report content in the standard TextReporter
    # This method is called by reporters to append extra human-readable lines
    def complete_text_reporter_report(self, reporter_self):
        if self.stdout is None or not utils.can_write_report_files(self.master):
            return []

        # Find the same report files as in process_linter
        report_files = []
        candidates = []
        if hasattr(self, "report_folder") and self.report_folder:
            candidates.append(self.report_folder)
        if hasattr(self, "workspace") and self.workspace:
            candidates.append(self.workspace)

        for base in candidates:
            try:
                for f in os.listdir(base):
                    lf = f.lower()
                    if "roslynator" in lf and (lf.endswith(".json") or lf.endswith(".xml")):
                        report_files.append(os.path.join(base, f))
            except Exception:
                continue

        if hasattr(self, "report_folder") and self.report_folder:
            for root, _, files in os.walk(self.report_folder):
                for f in files:
                    lf = f.lower()
                    if "roslynator" in lf and (lf.endswith(".json") or lf.endswith(".xml")):
                        report_files.append(os.path.join(root, f))

        if len(report_files) == 0:
            return []

        # Use the first found report
        report_path = report_files[0]
        try:
            with open(report_path, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except Exception:
            return []

        additional_report = [
            "\n--- Roslynator original report ---",
            f"Source: {utils.normalize_log_string(report_path)}",
        ]

        try:
            if report_path.lower().endswith(".json"):
                parsed = json.loads(raw)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                additional_report += pretty.splitlines()
            else:
                # XML: show raw (or pretty if feasible)
                additional_report += raw.splitlines()
        except Exception:
            additional_report += raw.splitlines()

        additional_report += ["--- End Roslynator report ---\n"]
        return additional_report
