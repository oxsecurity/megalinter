#!/usr/bin/env python3
import logging
import os

import yaml

CONFIG_DATA = None
CONFIG_SOURCE = None


def init_config(workspace):
    global CONFIG_DATA, CONFIG_SOURCE
    if CONFIG_DATA is not None:
        logging.debug(f"[config] Already initialized: {CONFIG_SOURCE}")
        return
    env = os.environ.copy()
    if workspace is None:
        set_config(env)
        CONFIG_SOURCE = "Environment variables only (no workspace)"
        print(f"[config] {CONFIG_SOURCE}")
        return
    # Search for config file
    if "MEGALINTER_CONFIG" in os.environ:
        config_file_name = os.environ.get("MEGALINTER_CONFIG")
        config_file = workspace + os.path.sep + config_file_name
    else:
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
            config_data = yaml.load(config_file_stream, Loader=yaml.FullLoader)
            if config_data is None:  # .mega-linter.yml existing but empty
                runtime_config = env
            else:
                runtime_config = {**config_data, **env}  # .mega-linter.yml not empty
            CONFIG_SOURCE = f"{config_file} + Environment variables"
    else:
        runtime_config = env
        CONFIG_SOURCE = (
            f"Environment variables only (no config file found in {workspace})"
        )
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


def get_list(config_var, default=None):
    var = get(config_var, None)
    if var is not None:
        if isinstance(var, list):
            return var
        if var == "":
            return []
        return var.split(",")
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
        logging.debug("Cleared Mega-Linter runtime config")
        return
    config = get_config()
    if key in config:
        del config[key]
    set_config(config)
