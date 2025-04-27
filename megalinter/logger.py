#!/usr/bin/env python3
import logging
import os
import re
import sys
import tomllib

import chalk as c
import requests
from megalinter import config, utils
from megalinter.constants import ML_DOC_URL
from megalinter.utils_reporter import log_section_start


def initialize_logger(mega_linter):
    logging_level_key = config.get(mega_linter.request_id, "LOG_LEVEL", "INFO").upper()
    logging_level_list = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        # Previous values for v3 ascending compatibility
        "TRACE": logging.WARNING,
        "VERBOSE": logging.INFO,
    }
    logging_level = (
        logging_level_list[logging_level_key]
        if logging_level_key in logging_level_list
        else logging.INFO
    )

    handler_stream = logging.StreamHandler(sys.stdout)
    if config.get(
        mega_linter.request_id, "LOG_FILE", ""
    ) == "none" or not utils.can_write_report_files(mega_linter):
        # Don't log console output in a file
        logging.basicConfig(
            force=True,
            level=logging_level,
            format="%(message)s",
            handlers=[
                handler_stream,
            ],
        )
    else:
        log_file = (
            mega_linter.report_folder
            + os.path.sep
            + config.get(mega_linter.request_id, "LOG_FILE", "megalinter.log")
        )
        # Log console output in a file
        if not os.path.isdir(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handler_file = logging.FileHandler(log_file, "w", "utf-8")
        logging.basicConfig(
            force=True,
            level=logging_level,
            format="%(message)s",
            handlers=[
                handler_file,
                handler_stream,
            ],
        )


# Propose legacy versions users to upgrade
def manage_upgrade_message():
    mega_linter_version = config.get(None, "BUILD_VERSION", "No docker image")
    if (
        "insiders" in mega_linter_version
        or "v4" in mega_linter_version
        or "v5" in mega_linter_version
    ):
        logging.warning(
            c.yellow(
                "#######################################################################"
            )
        )
        logging.warning(
            c.yellow(
                "MEGA-LINTER HAS A NEW V7 VERSION at https://github.com/oxsecurity/megalinter .\n"
                + "Please upgrade your configuration by running the following command at the "
                + "root of your repository (requires node.js): \n"
                + c.green("npx mega-linter-runner --upgrade")
            )
        )
        logging.warning(
            c.yellow(
                "#######################################################################"
            )
        )


def display_header(mega_linter):
    # Header prints
    logging.info(utils.format_hyphens(""))
    logging.info(utils.format_hyphens("MegaLinter, by OX Security"))
    logging.info(utils.format_hyphens(""))
    logging.info(
        " - Image Creation Date: " + config.get(None, "BUILD_DATE", "No docker image")
    )
    logging.info(
        " - Image Revision: " + config.get(None, "BUILD_REVISION", "No docker image")
    )
    logging.info(
        " - Image Version: " + config.get(None, "BUILD_VERSION", "No docker image")
    )
    logging.info(utils.format_hyphens(""))
    logging.info("The MegaLinter documentation can be found at:")
    logging.info(" - " + ML_DOC_URL)
    logging.info(utils.format_hyphens(""))
    logging.info(log_section_start("megalinter-init", "MegaLinter initialization"))
    logging.info(f"MegaLinter will analyze workspace [{mega_linter.workspace}]")
    if config.get(None, "GITHUB_REPOSITORY", "") != "":
        logging.info("GITHUB_REPOSITORY: " + config.get(None, "GITHUB_REPOSITORY", ""))
        # logging.info("GITHUB_SHA: " + os.environ.get("GITHUB_SHA", ""))
        logging.info("GITHUB_REF: " + config.get(None, "GITHUB_REF", ""))
        # logging.info("GITHUB_TOKEN: " + os.environ.get("GITHUB_TOKEN", ""))
        logging.info("GITHUB_RUN_ID: " + config.get(None, "GITHUB_RUN_ID", ""))
        logging.info("PAT: " + "set" if config.get(None, "PAT", "") != "" else "")
        if config.exists(None, "PAT"):
            logging.warning(
                "You should not use PAT anymore, please use Github Permissions in your Github Actions job"
            )
            logging.warning(
                "Add permissions contents:write, issues: write and pull-requests: write"
            )
            logging.warning(
                "More details: https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs"
            )
    # Display config variables for debug mode
    secured_env_variables = config.list_secured_variables(mega_linter.request_id)
    secured_env_variables_regex = config.list_secured_variables_regexes(
        secured_env_variables
    )
    for name, value in sorted(config.get_config(mega_linter.request_id).items()):
        if name not in secured_env_variables and not config.match_variable_regexes(
            name, secured_env_variables_regex
        ):
            logging.debug("" + name + "=" + str(value))
        else:
            logging.debug("" + name + "=HIDDEN_BY_MEGALINTER")
    logging.debug(utils.format_hyphens(""))
    logging.info("")


GITLEAKS_REGEXES = None


def fetch_gitleaks_regexes(force_use_local_file=False):
    global GITLEAKS_REGEXES
    if GITLEAKS_REGEXES is not None:
        return GITLEAKS_REGEXES

    # Use local file for test cases to improve speed
    current_test_name = utils.get_current_test_name()
    if (
        current_test_name
        and "test_fetch_gitleaks_regexes_remote" not in current_test_name
    ):
        force_use_local_file = True

    config_data = None
    if not force_use_local_file:
        url = "https://raw.githubusercontent.com/gitleaks/gitleaks/refs/heads/master/config/gitleaks.toml"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                config_data = (
                    response.text
                )  # Fix: Pass string to tomllib.loads instead of bytes
            else:
                logging.warning(
                    f"Failed to fetch Gitleaks config from URL: {response.status_code}"
                )
        except Exception as e:
            logging.warning(f"Could not fetch Gitleaks config from URL. Error: {e}")

    if config_data is None:
        logging.info("Using local Gitleaks config file.")
        descriptors_dir = utils.get_descriptor_dir()
        with open(
            f"{descriptors_dir}/additional/gitleaks-default.toml", "r", encoding="utf-8"
        ) as file:
            config_data = file.read()

    config = tomllib.loads(config_data)
    regex_patterns = []
    for rule in config.get("rules", []):
        rule_id = rule.get("id")
        if rule_id == "generic-api-key":
            continue
        pattern = rule.get("regex")
        if pattern:
            regex_patterns.append(pattern)
    regex_patterns = utils.keep_only_valid_regex_patterns(regex_patterns)
    GITLEAKS_REGEXES = regex_patterns
    return regex_patterns


def sanitize_string(input_string):
    regex_patterns = fetch_gitleaks_regexes()
    sanitized_string = input_string
    for pattern in regex_patterns:
        while True:
            match = re.search(pattern, sanitized_string)
            if not match:
                break
            if sanitized_string[match.end() - 1] == '"':
                sanitized_string = re.sub(
                    pattern, 'HIDDEN_BY_MEGALINTER"', sanitized_string, count=1
                )
            else:
                sanitized_string = re.sub(
                    pattern, "HIDDEN_BY_MEGALINTER", sanitized_string, count=1
                )
    return sanitized_string
