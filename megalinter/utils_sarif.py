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
        with open(linter.sarif_output_file, "r", encoding="utf-8") as linter_sarif_file:
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


def clear_default_workspace_prefix(file_path, default_workspace):
    def_ws_pattern = r'(?P<def_ws_context>\s+"uri"\:\s")' + default_workspace + "/"
    def_ws_pattern2 = (
        r'(?P<def_ws_context>\s+"uri"\:\s"file://)' + default_workspace + "/"
    )
    def_ws_pattern3 = r'(?P<def_ws_context>\s+")' + default_workspace + "/"

    patterns = [def_ws_pattern, def_ws_pattern2, def_ws_pattern3]

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
