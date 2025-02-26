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


def list_flavor_linters(flavor_id):
    all_flavors = get_all_flavors()
    flavor_definition = all_flavors[flavor_id]
    return flavor_definition["linters"]


def list_megalinter_flavors():
    flavors = {
        "all": {"label": "MegaLinter for any type of project"},
        "ci_light": {
            "label": "Optimized for CI items (Dockerfile, Jenkinsfile, JSON/YAML schemas, XML)"
        },
        "cupcake": {"label": "MegaLinter for the most commonly used languages"},
        "c_cpp": {"label": "Optimized for pure C/C++ projects"},
        "documentation": {"label": "Optimized for documentation projects"},
        "dotnet": {"label": "Optimized for C, C++, C# or VB based projects"},
        "dotnetweb": {
            "label": "Optimized for C, C++, C# or VB based projects with JS/TS"
        },
        "formatters": {"label": "Contains only formatters"},
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
        "security": {"label": "Optimized for security", "strict": True},
        "swift": {"label": "Optimized for SWIFT based projects"},
        "terraform": {"label": "Optimized for TERRAFORM based projects"},
    }
    return flavors


def get_image_flavor():
    return config.get(None, "MEGALINTER_FLAVOR", "all")


# Compare linters active for the current repo, and linters available in the current MegaLinter image flavor
def check_active_linters_match_flavor(active_linters, request_id):
    flavor = get_image_flavor()
    if flavor == "all":
        logging.debug('MegaLinter flavor is "all", no need to check match with linters')
        return True
    elif flavor == "none":
        logging.debug(
            "MegaLinter image contains a single linter, no need to check match with linters"
        )
        return True
    all_flavors = get_all_flavors()
    flavor_linters = all_flavors[flavor]["linters"]
    missing_linters = []
    for active_linter in active_linters:
        if (
            active_linter.name not in flavor_linters
        ) and active_linter.is_plugin is False:
            missing_linters += [active_linter.name]
            active_linter.is_active = False
    # Manage cases where linters are missing in flavor
    if len(missing_linters) > 0:
        # Don't warn/stop if missing linters are repository ones (mostly OX.security related)
        if not are_all_repository_linters(missing_linters):
            missing_linters_str = ",".join(missing_linters)
            logging.warning(
                f"MegaLinter flavor [{flavor}] doesn't contain linters {missing_linters_str}.\n"
                "As they're not available in this docker image, they will not be processed\n"
                "To solve this problem, please either: \n"
                f"- use default flavor {ML_REPO}\n"
                "- add ignored linters in DISABLE or DISABLE_LINTERS variables in your .mega-linter.yml config file "
                "located in your root directory\n"
                "- ignore this message by setting config variable FLAVOR_SUGGESTIONS to false"
            )
            # Stop the process if user wanted so in case of missing linters
            if (
                config.get(
                    request_id,
                    "FAIL_IF_MISSING_LINTER_IN_FLAVOR",
                    "",
                )
                == "true"
            ):
                logging.error(
                    'Missing linter and FAIL_IF_MISSING_LINTER_IN_FLAVOR has been set to "true": Stop run'
                )
                sys.exit(84)
        return False
    # All good !
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
            if (
                active_linter.name not in flavor_info["linters"]
                and active_linter.ignore_for_flavor_suggestions is False
            ):
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

    new_flavor_linters = filter(
        lambda linter: linter.ignore_for_flavor_suggestions is False,
        active_linters,
    )
    new_flavor_linters_names = map(lambda linter: linter.name, new_flavor_linters)
    return ["new", new_flavor_linters_names]


def are_all_repository_linters(linter_names: list[str]) -> bool:
    if len(linter_names) == 0:
        return False
    result = True
    for linter_name in linter_names:
        if not linter_name.startswith("REPOSITORY"):
            result = False
    return result
