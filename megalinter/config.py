#!/usr/bin/env python3
import json
import logging
import os
import shlex
import tempfile

import requests
import yaml

CONFIG_DATA = None
CONFIG_SOURCE = None


def init_config(workspace=None):
    global CONFIG_DATA, CONFIG_SOURCE
    if CONFIG_DATA is not None:
        logging.debug(f"[config] Already initialized: {CONFIG_SOURCE}")
        return
    env = os.environ.copy()
    if workspace is None and "MEGALINTER_CONFIG" not in os.environ:
        set_config(env)
        CONFIG_SOURCE = "Environment variables only (no workspace)"
        print(f"[config] {CONFIG_SOURCE}")
        return
    # Search for config file
    if "MEGALINTER_CONFIG" in os.environ:
        config_file_name = os.environ.get("MEGALINTER_CONFIG")
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
                runtime_config = env
            else:
                # append config file variables to env variables, with priority to env variables
                runtime_config = config_data | env
            CONFIG_SOURCE = f"{config_file} + Environment variables"
    else:
        runtime_config = env
        CONFIG_SOURCE = (
            f"Environment variables only (no config file found in {workspace})"
        )
    # manage EXTENDS in configuration
    if "EXTENDS" in runtime_config:
        combined_config = {}
        extends = runtime_config["EXTENDS"]
        if isinstance(extends, str):
            extends = extends.split(",")
        for extends_item in extends:
            r = requests.get(extends_item, allow_redirects=True)
            assert (
                r.status_code == 200
            ), f"Unable to retrieve EXTENDS config file {config_file_name}"
            extends_config_data = yaml.safe_load(r.content)
            combined_config.update(extends_config_data)
            CONFIG_SOURCE += f"\n[config] - extends from: {extends_item}"
        combined_config.update(runtime_config)
        runtime_config = combined_config
    # Print & set config in cache
    print(f"[config] {CONFIG_SOURCE}")
    set_config(runtime_config)


def get_config():
    global CONFIG_DATA
    if CONFIG_DATA is not None:
        return CONFIG_DATA
    else:
        return os.environ.copy()


def set_config(runtime_config):
    global CONFIG_DATA
    CONFIG_DATA = runtime_config


def get(config_var=None, default=None):
    if config_var is None:
        return get_config()
    val = get_config().get(config_var, default)
    # IF boolean, convert to "true" or "false"
    if isinstance(val, bool):
        if val is True:
            val = "true"
        elif val is False:
            val = "false"
    return val


def set(config_var, value):
    global CONFIG_DATA
    assert CONFIG_DATA is not None, "Config has not been initialized yet !"
    CONFIG_DATA[config_var] = value


# Get list of elements from configuration. It can be list of strings or objects
def get_list(config_var, default=None):
    var = get(config_var, None)
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


def get_list_args(config_var, default=None):
    var = get(config_var, None)
    if var is not None:
        if isinstance(var, list):
            return var
        if var == "":
            return []
        return shlex.split(var)
    return default


def set_value(config_var, val):
    config = get_config()
    config[config_var] = val
    set_config(config)


def exists(config_var):
    return config_var in get_config()


def copy():
    return get_config().copy()


def delete(key=None):
    global CONFIG_DATA, CONFIG_SOURCE
    if key is None:
        CONFIG_DATA = None
        CONFIG_SOURCE = None
        logging.debug("Cleared MegaLinter runtime config")
        return
    config = get_config()
    if key in config:
        del config[key]
    set_config(config)
