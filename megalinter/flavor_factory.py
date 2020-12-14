import json
import logging
import os

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
        "dart": {"label": "Mega-Linter optimized for DART based projects"},
        "dotnet": {
            "label": "Mega-Linter optimized for C, C++, C# or VB based projects"
        },
        "go": {"label": "Mega-Linter optimized for GO based projects"},
        "java": {"label": "Mega-Linter optimized for JAVA based projects"},
        "javascript": {
            "label": "Mega-Linter optimized for JAVASCRIPT or TYPESCRIPT based projects"
        },
        "php": {"label": "Mega-Linter optimized for PHP based projects"},
        "python": {"label": "Mega-Linter optimized for PYTHON based projects"},
        "ruby": {"label": "Mega-Linter optimized for RUBY based projects"},
        "rust": {"label": "Mega-Linter optimized for RUST based projects"},
        "scala": {"label": "Mega-Linter optimized for SCALA based projects"},
        "terraform": {"label": "Mega-Linter optimized for TERRAFORM based projects"},
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
    if len(missing_linters) > 0:
        missing_linters_str = ",".join(missing_linters)
        logging.error(
            f"Mega-Linter flavor [{flavor}] does not contain linters {missing_linters_str}.\n"
            "To solve this problem, please either: \n"
            "- use default flavor nvuillam/mega-linter\n"
            "- add missing linters in DISABLE variable in your .mega-linter.yml config file "
            "located in your root directory"
        )
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
        return matching_flavors
    return None
