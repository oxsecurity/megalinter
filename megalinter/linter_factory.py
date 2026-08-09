import glob
import importlib
import logging
import os

import yaml
from megalinter import Linter, flavor_factory
from megalinter.utils import get_descriptor_dir


# List all defined linters
def list_all_linters(linters_init_params=None):
    descriptor_files = list_descriptor_files()
    linters = []
    for descriptor_file in descriptor_files:
        descriptor_linters = build_descriptor_linters(
            descriptor_file, linters_init_params
        )
        linters += descriptor_linters
    return linters


# List flavor linters
def list_flavor_linters(linters_init_params=None, flavor_id="all"):
    all_linters = list_all_linters(linters_init_params)
    flavor_linter_ids = flavor_factory.list_flavor_linters(flavor_id)
    linters = []
    for linter in all_linters:
        if linter.name in flavor_linter_ids or linter.is_plugin is True:
            linters += [linter]
        else:
            del linter
    return linters


# List unique linter
def list_linters_by_name(linters_init_params=None, linter_names=[]):
    # Only parse descriptors that can contain the requested linters: a linter name
    # always starts with its descriptor id (convention also relied upon by
    # build_linter), so instantiating the 100+ other linters would be wasted time
    descriptor_files = [
        descriptor_file
        for descriptor_file in list_descriptor_files()
        if any(
            linter_name.startswith(
                os.path.basename(descriptor_file)
                .replace(".megalinter-descriptor.yml", "")
                .upper()
                + "_"
            )
            for linter_name in linter_names
        )
    ]
    if len(descriptor_files) == 0:
        descriptor_files = list_descriptor_files()
    linters = []
    for descriptor_file in descriptor_files:
        for linter in build_descriptor_linters(descriptor_file, linters_init_params):
            if linter.name in linter_names:
                linters += [linter]
    return linters


SHARED_LINTER_FILE_SUFFIX = ".megalinter-linter.yml"
shared_linter_definitions_cache: dict[str, dict] = {}


def resolve_linter_extends(linter_descriptor):
    if "extends" not in linter_descriptor:
        return linter_descriptor
    shared_name = linter_descriptor["extends"]
    shared_file = os.path.join(
        get_descriptor_dir(), "shared", shared_name + SHARED_LINTER_FILE_SUFFIX
    )
    if shared_file not in shared_linter_definitions_cache:
        assert os.path.isfile(shared_file), (
            f"Unable to find shared linter definition {shared_file} "
            f"(referenced by extends: {shared_name})"
        )
        with open(shared_file, "r", encoding="utf-8") as f:
            shared_linter_definitions_cache[shared_file] = yaml.safe_load(f)
    shared_definition = shared_linter_definitions_cache[shared_file]
    resolved = {
        **shared_definition,
        **{key: value for key, value in linter_descriptor.items() if key != "extends"},
    }
    for required_key in ["linter_name", "linter_url", "examples"]:
        assert required_key in resolved, (
            f"Missing {required_key} in linter extending {shared_name} "
            f"(not defined in {shared_file} nor in the descriptor entry)"
        )
    return resolved


# List all descriptor files (one by language)
def list_descriptor_files():
    descriptors_dir = get_descriptor_dir()
    linters_glob_pattern = descriptors_dir + "/*.megalinter-descriptor.yml"
    descriptor_files = []
    for descriptor_file in sorted(glob.glob(linters_glob_pattern)):
        descriptor_files += [descriptor_file]
    return descriptor_files


# Extract descriptor info from descriptor file
def build_descriptor_info(file):
    with open(file, "r", encoding="utf-8") as f:
        language_descriptor = yaml.safe_load(f)
    language_descriptor["linters"] = [
        resolve_linter_extends(linter_descriptor)
        for linter_descriptor in language_descriptor.get("linters", [])
    ]
    return language_descriptor


# Build linter instances from a descriptor file name, and initialize them
def build_descriptor_linters(file, linter_init_params=None, linter_names=None):
    if linter_names is None:
        linter_names = []
    linters = []
    # Dynamic generation from yaml
    with open(file, "r", encoding="utf-8") as f:
        language_descriptor = yaml.safe_load(f)

        # Build common attributes
        common_attributes = {}
        for attr_key, attr_value in language_descriptor.items():
            if attr_key not in ["linters", "install"]:
                common_attributes[attr_key] = attr_value
            elif attr_key == "install":
                common_attributes["descriptor_install"] = attr_value

        # Browse linters defined for language
        for linter_descriptor in language_descriptor.get("linters", []):
            if (
                len(linter_names) > 0
                and linter_descriptor["linter_name"] not in linter_names
            ):
                continue
            linter_descriptor = resolve_linter_extends(linter_descriptor)

            # Use custom class if defined in file
            linter_class = Linter
            if linter_descriptor.get("class"):
                linter_class_file_name = os.path.splitext(
                    os.path.basename(linter_descriptor.get("class"))
                )[0]
                try:
                    linter_module = importlib.import_module(
                        ".linters." + linter_class_file_name, package=__package__
                    )
                except ModuleNotFoundError as e:
                    # Descriptors baked in a docker image can reference a linter
                    # class that no longer exists in the code, for example when a
                    # linter has been removed in a major version. Skip the linter
                    # instead of crashing, but let unrelated import errors raised
                    # from within the class module propagate.
                    if e.name != f"{__package__}.linters.{linter_class_file_name}":
                        raise
                    logging.warning(
                        f"Linter class {linter_class_file_name} not found: skipping "
                        f"{linter_descriptor.get('linter_name')}, as it has been "
                        "removed from this version of MegaLinter"
                    )
                    continue
                linter_class = getattr(linter_module, linter_class_file_name)

            # Create a Linter class instance by linter
            instance_attributes = {**common_attributes, **linter_descriptor}
            linter_instance = linter_class(linter_init_params, instance_attributes)
            linters += [linter_instance]

    return linters


# Build a single linter instance from language and linter name
def build_linter(language, linter_name, linter_init_params=None):
    language_descriptor_file = (
        get_descriptor_dir()
        + os.path.sep
        + language.lower()
        + ".megalinter-descriptor.yml"
    )
    assert os.path.isfile(
        language_descriptor_file
    ), f"Unable to find {language_descriptor_file}"
    linters = build_descriptor_linters(
        language_descriptor_file, linter_init_params, [linter_name]
    )
    assert (
        len(linters) == 1
    ), f"Unable to find linter {linter_name} in {language_descriptor_file}"
    return linters[0]


# Sort groups of linters by speed
def sort_linters_groups_by_speed(linters_groups):
    # Calculate sum of linter speeds in the group
    linter_groups_speed_points = list(
        map(lambda x: [sum(i.linter_speed for i in x), x], linters_groups)
    )
    # Sort by slower to faster
    linter_groups_speed_points.sort(key=lambda x: x[0])
    linters_groups = list(map(lambda x: x[1], linter_groups_speed_points))
    return linters_groups
