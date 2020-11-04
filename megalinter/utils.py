#!/usr/bin/env python3

# Center the string and complete blanks with hyphens (-)
import glob
import importlib
import logging
import os
import re

import yaml
from git import Repo

from megalinter.Linter import Linter


def list_excluded_directories():
    excluded_dirs = ["node_modules", ".git", ".rbenv", ".venv", ".terragrunt-cache"]
    return excluded_dirs


# Returns directory where all .yml language descriptors are defined
def get_descriptor_dir():
    # Compiled version (copied from DockerFile)
    if os.path.isdir("/megalinter-descriptors"):
        return "/megalinter-descriptors"
    # Dev / Test version
    else:
        descriptor_dir = os.path.realpath(
            os.path.dirname(os.path.abspath(__file__)) + "/descriptors"
        )
        assert os.path.isdir(
            descriptor_dir
        ), f"Descriptor dir {descriptor_dir} not found !"
        return descriptor_dir


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


# List all descriptor files (one by language)
def list_descriptor_files():
    descriptors_dir = get_descriptor_dir()
    linters_glob_pattern = descriptors_dir + "/*.yml"
    descriptor_files = []
    for descriptor_file in sorted(glob.glob(linters_glob_pattern)):
        descriptor_files += [descriptor_file]
    return descriptor_files


# Extract descriptor info from descriptor file
def build_descriptor_info(file):
    with open(file) as f:
        language_descriptor = yaml.load(f, Loader=yaml.FullLoader)
    return language_descriptor


# Build linter instances from a descriptor file name, and initialize them
def build_descriptor_linters(file, linter_init_params=None, linter_names=None):
    if linter_names is None:
        linter_names = []
    linters = []
    # Dynamic generation from yaml
    with open(file) as f:
        language_descriptor = yaml.load(f, Loader=yaml.FullLoader)

        # Build common attributes
        common_attributes = {}
        for attr_key, attr_value in language_descriptor.items():
            if attr_key not in ["linters", "install"]:
                common_attributes[attr_key] = attr_value
            elif attr_key == "install":
                common_attributes["descriptor_install"] = attr_value

        # Browse linters defined for language
        for linter_descriptor in language_descriptor.get("linters"):
            if (
                len(linter_names) > 0
                and linter_descriptor["linter_name"] not in linter_names
            ):
                continue

            # Use custom class if defined in file
            linter_class = Linter
            if linter_descriptor.get("class"):
                linter_class_file_name = os.path.splitext(
                    os.path.basename(linter_descriptor.get("class"))
                )[0]
                linter_module = importlib.import_module(
                    ".linters." + linter_class_file_name, package=__package__
                )
                linter_class = getattr(linter_module, linter_class_file_name)

            # Create a Linter class instance by linter
            instance_attributes = {**common_attributes, **linter_descriptor}
            linter_instance = linter_class(linter_init_params, instance_attributes)
            linters += [linter_instance]

    return linters


# Build a single linter instance from language and linter name
def build_linter(language, linter_name):
    language_descriptor_file = (
        get_descriptor_dir() + os.path.sep + language.lower() + ".yml"
    )
    assert os.path.isfile(
        language_descriptor_file
    ), f"Unable to find {language_descriptor_file}"
    linters = build_descriptor_linters(language_descriptor_file, None, [linter_name])
    assert (
        len(linters) == 1
    ), f"Unable to find linter {linter_name} in {language_descriptor_file}"
    return linters[0]


def check_file_extension_or_name(file, file_extensions, file_names):
    base_file_name = os.path.basename(file)
    filename, file_extension = os.path.splitext(base_file_name)
    if len(file_extensions) > 0 and file_extension in file_extensions:
        return True
    elif len(file_names) > 0 and filename in file_names:
        return True
    elif len(file_extensions) == 1 and file_extensions[0] == "*":
        return True
    return False


# Center the string and complete blanks with hyphens (-)
def format_hyphens(str_in):
    if str_in != "":
        str_in = " " + str_in + " "
    return "{s:{c}^{n}}".format(s=str_in, n=100, c="-")


def list_active_reporters_for_scope(scope, reporter_init_params):
    reporters = []
    # List associated reporters
    reporters_dir = os.path.realpath(
        os.path.dirname(os.path.abspath(__file__)) + "/reporters"
    )
    scope_reporters = []
    for reporter_class_file in os.listdir(reporters_dir):
        if not reporter_class_file.endswith("Reporter.py"):
            continue
        reporter_class_nm = os.path.splitext(reporter_class_file)[0]
        reporter_module = importlib.import_module(
            ".reporters." + reporter_class_nm, package=__package__
        )
        reporter_class = getattr(reporter_module, reporter_class_nm)
        if reporter_class.scope == scope:
            reporter = reporter_class(reporter_init_params)
            scope_reporters += [reporter]
    # Keep only active reporters
    skipped_reporters = []
    for reporter in scope_reporters:
        if reporter.is_active is False:
            skipped_reporters += [reporter.name]
            continue
        reporters += [reporter]
    # Display skipped reporters in log
    if len(skipped_reporters) > 0:
        skipped_reporters.sort()
        logging.debug("Skipped reporters:  " + ", ".join(skipped_reporters))
    # Sort reporters by name
    reporters.sort(key=lambda x: x.name)
    return reporters


# Can receive a list of strings, regexes, or even mixed :).
# Regexes must start with '(' to be identified are regex
def file_contains(file_name, regex_or_str_list):
    with open(file_name) as f:
        content = f.read()
        for regex_or_str in regex_or_str_list:
            if regex_or_str[0] == "(":
                regex = re.compile(regex_or_str)
                if regex.search(content, re.MULTILINE) is not None:
                    return True
            else:
                if regex_or_str in content:
                    return True
    return False


def get_dict_string_list(dict_obj, key, default):
    if key in dict_obj:
        return dict_obj[key].split(",")
    return default


def decode_utf8(stdout):
    # noinspection PyBroadException
    try:
        res = stdout.decode("utf-8")
    except Exception:
        res = str(stdout)
    return res


def check_updated_file(file, repo_home):
    repo = Repo(repo_home)
    changed_files = [item.a_path for item in repo.index.diff(None)]
    file_absolute = os.path.abspath(file)
    for changed_file in changed_files:
        if changed_file in file_absolute:
            return True
    return False
