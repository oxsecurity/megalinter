import json
import logging
import os
import random
import re
from json.decoder import JSONDecodeError
from os import fdopen
from shutil import move
from tempfile import mkstemp

from megalinter import config
from megalinter.utils_reporter import get_linter_doc_url


def normalize_sarif_files(linter):
    if (
        linter.sarif_output_file is not None
        and os.path.isfile(linter.sarif_output_file)
        and os.path.getsize(linter.sarif_output_file) > 0
    ):
        # Read SARIF output file

        load_ok = False
        # utf-8-sig: some linters (ex: roslynator, on .NET) write a BOM
        with open(
            linter.sarif_output_file, "r", encoding="utf-8-sig"
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
                logging.debug(f"SARIF File content:\n{linter_sarif_file.read()}")
            except Exception as e:  # noqa: E722
                # Other error
                logging.error(
                    f"[SARIF reporter] ERROR: Unknown error with {linter.name} "
                    f"SARIF file {linter.sarif_output_file}"
                )
                logging.error(str(e))
        if load_ok is True:
            linter_sarif_obj = fix_sarif(linter_sarif_obj, linter)

            result_json = json.dumps(linter_sarif_obj, sort_keys=True, indent=2)

            with open(linter.sarif_output_file, "w", encoding="utf-8") as sarif_file:
                sarif_file.write(result_json)
                logging.info(
                    f"[SARIF Reporter] Generated {linter.name} report: {linter.sarif_output_file}"
                )

            # In case SARIF is active, and default workspace is set, clear that from sarif files
            default_workspace = config.get(linter.request_id, "DEFAULT_WORKSPACE")
            if (
                config.get(
                    linter.request_id, "SARIF_REPORTER_NORMALIZE_LINTERS_OUTPUT", True
                )
                == "true"
                and default_workspace
            ):
                clear_default_workspace_prefix(
                    linter.sarif_output_file, default_workspace
                )


# Add the runs of the source SARIF log to the target one. The rules of a run are
# merged by id, and the rule indexes of the added results follow
def merge_sarif_logs(target: dict, source: dict):
    target_runs = target.setdefault("runs", [])
    for run_index, source_run in enumerate(source.get("runs", [])):
        if run_index >= len(target_runs):
            target_runs.append(source_run)
            continue
        target_run = target_runs[run_index]
        rules = (
            target_run.setdefault("tool", {})
            .setdefault("driver", {})
            .setdefault("rules", [])
        )
        rule_indexes = {rule.get("id"): index for index, rule in enumerate(rules)}
        index_map = {}
        source_rules = source_run.get("tool", {}).get("driver", {}).get("rules", [])
        for source_index, rule in enumerate(source_rules):
            if rule.get("id") not in rule_indexes:
                rule_indexes[rule.get("id")] = len(rules)
                rules.append(rule)
            index_map[source_index] = rule_indexes[rule.get("id")]
        results = target_run.setdefault("results", [])
        for result in source_run.get("results", []):
            if "ruleIndex" in result:
                result["ruleIndex"] = index_map.get(
                    result["ruleIndex"], result["ruleIndex"]
                )
            results.append(result)
        if "artifacts" in source_run:
            target_run["artifacts"] = (
                target_run.get("artifacts", []) + source_run["artifacts"]
            )


def clear_default_workspace_prefix(file_path, default_workspace):
    # The workspace is matched literally. On Windows (native mode) it can appear
    # with forward slashes (URIs) or with JSON-escaped backslashes
    workspace_patterns = []
    for variant, separator in (
        (default_workspace, "/"),
        (default_workspace.replace("\\", "/"), "/"),
        (default_workspace.replace("\\", "\\\\"), "\\\\"),
    ):
        pattern = re.escape(variant) + re.escape(separator)
        if pattern not in workspace_patterns:
            workspace_patterns.append(pattern)
    patterns = []
    for workspace_pattern in workspace_patterns:
        patterns += [
            r'(?P<def_ws_context>\s+"uri"\:\s")' + workspace_pattern,
            r'(?P<def_ws_context>\s+"uri"\:\s"file://)' + workspace_pattern,
            r'(?P<def_ws_context>\s+")' + workspace_pattern,
        ]

    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, "w") as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_line = line
                matched = False
                for p in patterns:
                    match = re.match(p, line)

                    if match:
                        matched = True
                        replaced = re.sub(p, match.group("def_ws_context"), line)
                        new_file.write(replaced)

                if not matched:
                    new_file.write(new_line)
    move(abs_path, file_path)


# Some SARIF linter output contain errors (like references to line 0)
# We must correct them so SARIF is valid
def fix_sarif(linter_sarif_obj, linter):
    # browse runs
    if "runs" in linter_sarif_obj:
        for id_run, run in enumerate(linter_sarif_obj["runs"]):
            # Add MegaLinter info
            run_properties = run["properties"] if "properties" in run else {}
            run_properties["megalinter"] = {
                "linterKey": linter.name,
                "docUrl": get_linter_doc_url(linter),
                "linterVersion": linter.get_linter_version(),
            }
            run["properties"] = run_properties

            # Update linter name in case there are duplicates
            if (
                "tool" in run
                and "driver" in run["tool"]
                and "name" in run["tool"]["driver"]
                and linter.master.megalinter_flavor
                != "none"  # single linter image case
            ):
                run["tool"]["driver"]["name"] = (
                    run["tool"]["driver"]["name"] + " (MegaLinter " + linter.name + ")"
                )

            # fix missing informationUri
            if (
                "tool" in run
                and "driver" in run["tool"]
                and "informationUri" not in run["tool"]["driver"]
            ):
                run["tool"]["driver"]["informationUri"] = get_linter_doc_url(linter)

            # fix missing version
            if (
                "tool" in run
                and "driver" in run["tool"]
                and "version" not in run["tool"]["driver"]
            ):
                run["tool"]["driver"]["version"] = linter.get_linter_version()

            # fix duplicate rules property
            if (
                "tool" in run
                and "driver" in run["tool"]
                and "rules" in run["tool"]["driver"]
            ):
                rules = run["tool"]["driver"]["rules"]
                rules_updated: list = []
                for rule in rules:
                    # If duplicate id, update duplicate items ids with a random value
                    if "id" in rule and any(
                        "id" in rule_item and rule_item["id"] == rule["id"]
                        for rule_item in rules_updated
                    ):
                        rule["id"] = (
                            rule["id"] + "_DUPLICATE_" + str(random.randint(1, 99999))
                        )
                    rules_updated += [rule]
                run["tool"]["driver"]["rules"] = rules_updated

            # fix results property
            if "results" in run:
                # browse run results
                for id_result, result in enumerate(run["results"]):
                    if "fixes" in result:
                        result["fixes"] = [
                            fix for fix in result["fixes"] if fix.get("artifactChanges")
                        ]
                        if not result["fixes"]:
                            del result["fixes"]
                    if "locations" in result:
                        # browse result locations
                        for id_location, location in enumerate(result["locations"]):
                            if "physicalLocation" in location:
                                location["physicalLocation"] = (
                                    fix_sarif_physical_location(
                                        location["physicalLocation"]
                                    )
                                )
                            result["locations"][id_location] = location

                    run["results"][id_result] = result
            else:
                # make sure that there is a results entry so GitHub's SARIF validator doesn't cry
                run["results"] = []

            # Update run in full list
            linter_sarif_obj["runs"][id_run] = run
    return linter_sarif_obj


# A result is suppressed (ex: # nosemgrep) when all its suppressions are accepted:
# it must be excluded from counts and human-readable details (SARIF 2.1.0 §3.27.23)
# A suppression without status is accepted, "underReview" and "rejected" are not (§3.35.3)
def is_suppressed(result: dict) -> bool:
    suppressions = result.get("suppressions") or []
    return len(suppressions) > 0 and all(
        suppression.get("status", "accepted") == "accepted"
        for suppression in suppressions
    )


# Returns a copy of the SARIF without its suppressed results. The SARIF report
# itself keeps them, so SARIF consumers still see the suppressions
def remove_suppressed_results(sarif_obj: dict) -> dict:
    runs = []
    for run in sarif_obj.get("runs") or []:
        results = run.get("results")
        if isinstance(results, list):
            run = {
                **run,
                "results": [result for result in results if not is_suppressed(result)],
            }
        runs.append(run)
    return {**sarif_obj, "runs": runs}


def remove_suppressed_results_from_text(sarif_text: str) -> str:
    try:
        sarif_obj = json.loads(sarif_text)
    except JSONDecodeError:
        # Invalid SARIF has already been reported by normalize_sarif_files
        return sarif_text
    if not isinstance(sarif_obj, dict):
        return sarif_text
    return json.dumps(remove_suppressed_results(sarif_obj), indent=2)


# Replace startLine and endLine in region or contextRegion
def fix_sarif_physical_location(physical_location):
    for location_key in physical_location.keys():
        location_item = physical_location[location_key]
        if "startLine" in location_item and location_item["startLine"] == 0:
            location_item["startLine"] = 1
        if "endLine" in location_item and location_item["endLine"] == 0:
            location_item["endLine"] = 1
        if "startColumn" in location_item and location_item["startColumn"] == 0:
            location_item["startColumn"] = 1
        if "endColumn" in location_item and location_item["endColumn"] == 0:
            location_item["endColumn"] = 1
        physical_location[location_key] = location_item
    return physical_location


# Findings of a SARIF file (after normalization), as flat records for the JSON report
def extract_findings(sarif_file, workspace=None):
    if sarif_file is None or not os.path.isfile(sarif_file):
        return None
    with open(sarif_file, "r", encoding="utf-8-sig") as file:
        try:
            sarif_obj = json.load(file)
        except JSONDecodeError:
            return None
    findings = []
    for run in sarif_obj.get("runs") or []:
        for result in run.get("results") or []:
            if is_suppressed(result):
                continue
            findings.append(build_finding(result, workspace))
    return findings


def build_finding(result: dict, workspace=None) -> dict:
    finding = {"level": result.get("level") or "warning"}
    rule_id = result.get("ruleId") or (result.get("rule") or {}).get("id")
    if rule_id:
        finding["rule"] = rule_id
    message = result.get("message") or {}
    text = message.get("text") or message.get("markdown")
    if text:
        finding["message"] = text
    locations = result.get("locations") or []
    physical = (locations[0].get("physicalLocation") or {}) if locations else {}
    uri = (physical.get("artifactLocation") or {}).get("uri")
    if uri:
        finding["file"] = relative_finding_path(uri, workspace)
    region = physical.get("region") or {}
    for sarif_key, key in (
        ("startLine", "line"),
        ("startColumn", "column"),
        ("endLine", "end_line"),
    ):
        if sarif_key in region:
            finding[key] = region[sarif_key]
    return finding


def relative_finding_path(uri: str, workspace=None) -> str:
    path = uri.removeprefix("file://").replace("\\", "/")
    if workspace:
        prefix = workspace.replace("\\", "/").rstrip("/") + "/"
        # file:///C:/... on Windows leaves a leading slash before the drive
        for candidate in (path, path.removeprefix("/")):
            if candidate.startswith(prefix):
                return candidate.removeprefix(prefix)
    return path
