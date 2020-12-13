import json
import logging
import os


ALL_FLAVOURS_CACHE = None


def get_all_flavours():
    global ALL_FLAVOURS_CACHE
    if ALL_FLAVOURS_CACHE is not None:
        return ALL_FLAVOURS_CACHE
    # Compiled version (copied from DockerFile)
    if os.path.isfile("/megalinter-descriptors/flavours.json"):
        flavours_file = "/megalinter-descriptors/flavours.json"
    # Dev / Test version
    else:
        flavours_file = os.path.realpath(
            os.path.dirname(os.path.abspath(__file__)) + "/flavours.json"
        )
        assert os.path.isfile(
            flavours_file
        ), f"Descriptor dir {flavours_file} not found !"
    # Parse flavours file json , set cache and return result
    with open(flavours_file, "r", encoding="utf-8") as json_file:
        all_flavours = json.load(json_file)

    ALL_FLAVOURS_CACHE = all_flavours
    return all_flavours


def list_megalinter_flavours():
    flavours = {
        "all": {"label": "Mega-Linter for any type of project"},
        "dart": {"label": "Mega-Linter optimized for DART based projects"},
        "go": {"label": "Mega-Linter optimized for GO based projects"},
        "java": {"label": "Mega-Linter optimized for JAVA based projects"},
        "javascript": {"label": "Mega-Linter optimized for JAVASCRIPT based projects"},
        "microsoft": {"label": "Mega-Linter optimized for MICROSOFT based projects"},
        "php": {"label": "Mega-Linter optimized for PHP based projects"},
        "python": {"label": "Mega-Linter optimized for PYTHON based projects"},
        "ruby": {"label": "Mega-Linter optimized for RUBY based projects"},
        "rust": {"label": "Mega-Linter optimized for RUST based projects"},
        "scala": {"label": "Mega-Linter optimized for SCALA based projects"},
    }
    return flavours


def get_image_flavour():
    return os.environ.get("MEGALINTER_FLAVOUR", "all")


# Compare linters active for the current repo, and linters available in the current Mega-Linter image flavour
def check_active_linters_match_flavour(active_linters):
    flavour = get_image_flavour()
    if flavour == "all":
        logging.debug("Mega-Linter flavour is \"all\", no need to check match with linters")
        return True
    all_flavours = get_all_flavours()
    flavour_linters = all_flavours[flavour]["linters"]
    missing_linters = []
    for active_linter in active_linters:
        if active_linter not in flavour_linters:
            missing_linters += [active_linter.name]
    if len(missing_linters) > 0:
        missing_linters_str = ",".join(missing_linters)
        logging.error(f"Mega-Linter flavour [{flavour}] does not contain linters {missing_linters_str}.\n"
                      "To solve this problem, please either: \n"
                      "- use default flavour nvuillam/mega-linter\n"
                      "- add missing linters in DISABLE variable in your .mega-linter.yml config file "
                      "located in your root directory")
        return False
    return True
