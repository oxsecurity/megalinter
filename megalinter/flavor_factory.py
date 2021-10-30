import json
import logging
import os
import sys

from megalinter import config
from megalinter.constants import ML_REPO

ALL_FLAVORS_CACHE = None


def get_all_flavors():
    global ALL_FLAVORS_CACHE
    if ALL_FLAVORS_CACHE is not None:
        return ALL_FLAVORS_CACHE
    # Compiled version (copied from DockerFile)
    if os.path.isfile("/megalinter-descriptors/all_flavors.json"):
        flavors_file = "/megalinter-descriptors/all_flavors.json"
    # Dev / Test version
    else:
        flavors_file = os.path.realpath(
            os.path.dirname(os.path.abspath(__file__)) + "/descriptors/all_flavors.json"
        )
        assert os.path.isfile(
            flavors_file
        ), f"Descriptor dir {flavors_file} not found !"
    # Parse flavors file json , set cache and return result
    with open(flavors_file, "r", encoding="utf-8") as json_file:
        all_flavors = json.load(json_file)

    ALL_FLAVORS_CACHE = all_flavors
    return all_flavors


def list_megalinter_flavors():
    flavors = {
        "all": {"label": "Mega-Linter for any type of project"},
        "ci_light": {
            "label": "Optimized for CI items (Dockerfile, Jenkinsfile, JSON/YAML schemas, XML)"
        },
        "dart": {"label": "Optimized for DART based projects"},
        "documentation": {"label": "Optimized for documentation projects"},
        "dotnet": {"label": "Optimized for C, C++, C# or VB based projects"},
        "go": {"label": "Optimized for GO based projects"},
        "java": {"label": "Optimized for JAVA based projects"},
        "javascript": {
            "label": "Optimized for JAVASCRIPT or TYPESCRIPT based projects"
        },
        "php": {"label": "Optimized for PHP based projects"},
        "python": {"label": "Optimized for PYTHON based projects"},
        "ruby": {"label": "Optimized for RUBY based projects"},
        "rust": {"label": "Optimized for RUST based projects"},
        "salesforce": {"label": "Optimized for Salesforce based projects"},
        "scala": {"label": "Optimized for SCALA based projects"},
        "swift": {"label": "Optimized for SWIFT based projects"},
        "terraform": {"label": "Optimized for TERRAFORM based projects"},
    }
    return flavors


def get_image_flavor():
    return os.environ.get("MEGALINTER_FLAVOR", "all")


# Compare linters active for the current repo, and linters available in the current Mega-Linter image flavor
def check_active_linters_match_flavor(active_linters):
    flavor = get_image_flavor()
    if flavor == "all":
        logging.debug(
            'Mega-Linter flavor is "all", no need to check match with linters'
        )
        return True
    all_flavors = get_all_flavors()
    flavor_linters = all_flavors[flavor]["linters"]
    missing_linters = []
    for active_linter in active_linters:
        if active_linter.name not in flavor_linters:
            missing_linters += [active_linter.name]
            active_linter.is_active = False
    if len(missing_linters) > 0:
        missing_linters_str = ",".join(missing_linters)
        logging.warning(
            f"Mega-Linter flavor [{flavor}] does not contain linters {missing_linters_str}.\n"
            "As they are not available in this docker image, they will not be processed\n"
            "To solve this problem, please either: \n"
            f"- use default flavor {ML_REPO}\n"
            "- add ignored linters in DISABLE or DISABLE_LINTERS variables in your .mega-linter.yml config file "
            "located in your root directory\n"
            "- ignore this message by setting config variable FLAVOR_SUGGESTIONS to false"
        )
        if config.get("FAIL_IF_MISSING_LINTER_IN_FLAVOR", "") == "true":
            logging.error(
                'Missing linter and FAIL_IF_MISSING_LINTER_IN_FLAVOR has been set to "true": Stop run'
            )
            sys.exit(84)
        return False
    return True


# Compare active linters with available flavors to make suggestions to improve CI performances
def get_megalinter_flavor_suggestions(active_linters):
    flavor = get_image_flavor()
    if flavor != "all":
        return None
    all_flavors = get_all_flavors()
    matching_flavors = []
    for flavor_id, flavor_info in all_flavors.items():
        match = True
        for active_linter in active_linters:
            if active_linter.name not in flavor_info["linters"]:
                match = False
                break
        if match is True:
            matching_flavor = {
                "flavor": flavor_id,
                "flavor_info": flavor_info,
                "linters_number": len(flavor_info["linters"]),
            }
            matching_flavors += [matching_flavor]
    if len(matching_flavors) > 0:
        # There are matching flavors
        return sorted(
            matching_flavors, key=lambda i: (i["linters_number"], i["flavor"])
        )
    # Propose user to request a new flavor for the list of linters
    active_linter_names = map(lambda linter: linter.name, active_linters)
    return ["new", active_linter_names]
