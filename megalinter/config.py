#!/usr/bin/env python3
import json
import logging
import os
import re
import shlex
import tempfile

import requests
import yaml

RUN_CONFIGS = {}  # type: ignore[var-annotated]


def init_config(request_id, workspace=None, params={}):
    global RUN_CONFIGS
    if request_id in RUN_CONFIGS:
        existing_config = get_config(request_id)
        new_config = existing_config | params
        set_config(request_id, new_config)
        logging.debug(
            f"[config] Already initialized: {RUN_CONFIGS[request_id]['CONFIG_SOURCE']}"
        )
        return
    env = os.environ.copy()
    env_plus_params = env | params
    if workspace is None and "MEGALINTER_CONFIG" not in env_plus_params:
        set_config(request_id, env_plus_params)
        RUN_CONFIGS[request_id][
            "CONFIG_SOURCE"
        ] = "Environment variables only (no workspace)"
        print(f"[config] {RUN_CONFIGS[request_id]['CONFIG_SOURCE']}")
        return
    else:
        set_config(request_id, env_plus_params)
        RUN_CONFIGS[request_id][
            "CONFIG_SOURCE"
        ] = "TEMPORARY VAL THAT SHOULD NOT REMAIN"
    # Search for config file
    config_file = None
    if "MEGALINTER_CONFIG" in env_plus_params:
        config_file_name = env_plus_params.get("MEGALINTER_CONFIG")
        if config_file_name.startswith("https://"):
            # Remote configuration file
            config_file = (
                tempfile.gettempdir()
                + os.path.sep
                + config_file_name.rsplit("/", 1)[-1]
            )
            r = requests.get(config_file_name, allow_redirects=True)
            assert (
                r.status_code == 200
            ), f"Unable to retrieve config file {config_file_name}"
            with open(config_file, "wb") as f:
                f.write(r.content)
        # Hardcoded path to config file
        elif os.path.isfile(config_file_name):
            config_file = config_file_name
        else:
            # Local configuration file with name forced by user
            config_file = workspace + os.path.sep + config_file_name
    else:
        # Local configuration file found with default name
        config_file = workspace + os.path.sep + ".mega-linter.yml"
        for candidate in [
            ".mega-linter.yml",
            ".megalinter.yml",
            ".mega-linter.yaml",
            ".megalinter.yaml",
        ]:
            if os.path.isfile(workspace + os.path.sep + candidate):
                config_file = workspace + os.path.sep + candidate
                break
    # if config file is found, merge its values with environment variables (with priority to env values)
    if os.path.isfile(config_file):
        with open(config_file, "r", encoding="utf-8") as config_file_stream:
            config_data = yaml.safe_load(config_file_stream)
            if config_data is None:  # .mega-linter.yml existing but empty
                runtime_config = env_plus_params
            else:
                # append config file variables to env variables, with priority to env variables
                runtime_config = config_data | env_plus_params
            RUN_CONFIGS[request_id][
                "CONFIG_SOURCE"
            ] = f"{config_file} + Environment variables"
    else:
        runtime_config = env_plus_params
        RUN_CONFIGS[request_id][
            "CONFIG_SOURCE"
        ] = f"Environment variables only (no config file found in {workspace})"
    # manage EXTENDS in configuration
    if "EXTENDS" in runtime_config:
        combined_config = {}
        RUN_CONFIGS[request_id]["CONFIG_SOURCE"] = combine_config(
            workspace,
            runtime_config,
            combined_config,
            RUN_CONFIGS[request_id]["CONFIG_SOURCE"],
        )
        runtime_config = combined_config
    # Print & set config in cache
    print(f"[config] {RUN_CONFIGS[request_id]['CONFIG_SOURCE']}")
    set_config(request_id, runtime_config)


def combine_config(workspace, config, combined_config, config_source):
    config_properties_to_append = []

    if "CONFIG_PROPERTIES_TO_APPEND" in config:
        config_properties_to_append = config["CONFIG_PROPERTIES_TO_APPEND"]

    extends = config["EXTENDS"]
    if isinstance(extends, str):
        extends = extends.split(",")
    for extends_item in extends:
        if extends_item.startswith("http"):
            headers = {}
            if (
                extends_item.startswith("https://raw.githubusercontent.com")
                and "GITHUB_TOKEN" in os.environ
            ):
                github_token = os.environ["GITHUB_TOKEN"]
                headers["Authorization"] = f"token {github_token}"
            r = requests.get(extends_item, allow_redirects=True, headers=headers)
            assert (
                r.status_code == 200
            ), f"Unable to retrieve EXTENDS config file {extends_item}"
            extends_config_data = yaml.safe_load(r.content)
        else:
            with open(
                workspace + os.path.sep + extends_item, "r", encoding="utf-8"
            ) as f:
                extends_config_data = yaml.safe_load(f)
        merge_dicts(combined_config, extends_config_data, config_properties_to_append)
        config_source += f"\n[config] - extends from: {extends_item}"
        if "EXTENDS" in extends_config_data:
            combine_config(
                workspace,
                extends_config_data,
                combined_config,
                config_source,
            )
    merge_dicts(combined_config, config, config_properties_to_append)
    return config_source


def merge_dicts(first, second, config_properties_to_append):
    for k, v in second.items():
        if k not in first:
            first[k] = v
        else:
            if (
                isinstance(first[k], list)
                and isinstance(v, list)
                and k in config_properties_to_append
            ):
                first[k] = first[k] + v
            else:
                first[k] = v


def is_initialized_for(request_id):
    global RUN_CONFIGS
    if request_id in RUN_CONFIGS:
        return True
    return False


def get_config(request_id=None):
    global RUN_CONFIGS
    if request_id is not None and request_id in RUN_CONFIGS:
        # Return request config
        return RUN_CONFIGS[request_id]
    elif request_id is not None:
        raise Exception(
            f"Internal error: there should be a config for request_id {request_id}"
        )
    else:
        # Return ENV
        return os.environ.copy()


def set_config(request_id, runtime_config):
    global RUN_CONFIGS
    RUN_CONFIGS[request_id] = runtime_config


def get(request_id, config_var=None, default=None):
    if config_var is None:
        return get_config(request_id)
    val = get_config(request_id).get(config_var, default)
    # IF boolean, convert to "true" or "false"
    if isinstance(val, bool):
        if val is True:
            val = "true"
        elif val is False:
            val = "false"
    return val


def set(request_id, config_var, value):
    global RUN_CONFIGS
    assert request_id in RUN_CONFIGS, "Config has not been initialized yet !"
    RUN_CONFIGS[request_id][config_var] = value


# Get list of elements from configuration. It can be list of strings or objects
def get_list(request_id, config_var, default=None):
    var = get(request_id, config_var, None)
    if var is not None:
        # List format
        if isinstance(var, list):
            return var
        # Empty var: return empty list
        if var == "":
            return []
        # Serialized JSON
        if var.startswith("["):
            return json.loads(var)
        # String with comma-separated elements
        return var.split(",")
    return default


# Retrieve a configuration variable as a list of arguments, handling various input formats.
def get_list_args(request_id, config_var, default=None):
    # Retrieve the variable from the configuration
    var = get(request_id, config_var, None)

    match var:
        # None return the default value
        case None:
            return default
        # Blank or whitespace-only strings return empty list
        case "" | str() if var.strip() == "":
            return []
        # Integer or a Decimal return it as a list
        case int() | float():
            return [str(var)]
        # If already a list just return it
        case list():
            return var
        # If string does not contain spaces, return it as a list
        case str() if " " not in var.strip():
            return [var]
        # Otherwise, split the string using shlex and return the result
        case _:
            return shlex.split(var)


def set_value(request_id, config_var, val):
    config = get_config(request_id)
    config[config_var] = val
    set_config(request_id, config)


def exists(request_id, config_var):
    return config_var in get_config(request_id)


def copy(request_id):
    return get_config(request_id).copy()


def delete(request_id=None, key=None):
    global RUN_CONFIGS
    # Global delete (used for tests)
    if request_id is None:
        RUN_CONFIGS = {}
        return
    if key is None:
        del RUN_CONFIGS[request_id]
        logging.debug("Cleared MegaLinter runtime config for request " + request_id)
        return
    config = get_config(request_id)
    if key in config:
        del config[key]
    set_config(request_id, config)


def build_env(request_id, secured=True, allow_list=[]):
    secured_env_variables = []
    secured_env_variables_regex = []
    if secured is True:
        secured_env_variables = list_secured_variables(request_id)
        secured_env_variables_regex = list_secured_variables_regexes(
            secured_env_variables
        )
    env_dict = {}
    for key, value in get_config(request_id).items():
        if (
            key in secured_env_variables
            or match_variable_regexes(key, secured_env_variables_regex)
        ) and key not in allow_list:
            env_dict[key] = "HIDDEN_BY_MEGALINTER"
        elif not isinstance(value, str):
            env_dict[key] = str(value)
        else:
            env_dict[key] = value
    return env_dict


def list_secured_variables(request_id) -> list[str]:
    secured_env_variables_default = get_list(
        request_id,
        "SECURED_ENV_VARIABLES_DEFAULT",
        [
            "GITHUB_TOKEN",
            "PAT",
            "SYSTEM_ACCESSTOKEN",
            "GIT_AUTHORIZATION_BEARER",
            "CI_JOB_TOKEN",
            "GITLAB_ACCESS_TOKEN_MEGALINTER",
            "GITLAB_CUSTOM_CERTIFICATE",
            "WEBHOOK_REPORTER_BEARER_TOKEN",
            "NODE_TOKEN",
            "NPM_TOKEN",
            "DOCKER_USERNAME",
            "DOCKER_PASSWORD",
            "CODECOV_TOKEN",
            "GCR_USERNAME",
            "GCR_PASSWORD",
            "SMTP_PASSWORD",
            "CI_SFDX_HARDIS_GITLAB_TOKEN" "(SFDX_CLIENT_ID_.*)",
            "(SFDX_CLIENT_KEY_.*)",
        ],
    )
    secured_env_variables = get_list(
        request_id,
        "SECURED_ENV_VARIABLES",
        [],
    )
    return secured_env_variables_default + secured_env_variables


def list_secured_variables_regexes(secured_env_variables: list[str]):
    regexes = []
    for variable_expression in secured_env_variables:
        if variable_expression.startswith("("):
            regexes += [re.compile(variable_expression)]
    return regexes


def match_variable_regexes(
    variable_name, secured_env_variable_regexes: list[re.Pattern]
):
    for regex in secured_env_variable_regexes:
        if regex.search(variable_name):
            return True
    return False
