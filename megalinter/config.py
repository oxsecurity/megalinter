#!/usr/bin/env python3
import logging
import os

import megalinter

# Initialize runtime config
import yaml

RUNTIME_CONFIG = os.environ.copy()
config_file_name = os.environ.get("MEGALINTER_CONFIG", ".megalinter.yml")
config_file = megalinter.utils.REPO_HOME_DEFAULT + os.path.sep + config_file_name
# if .megalinter.yml is found, merge its values with environment variables (with priority to env values)
if os.path.isfile(config_file):
    with open(config_file, "r", encoding="utf-8") as config_file_stream:
        config_data = yaml.load(config_file_stream, Loader=yaml.FullLoader)
        RUNTIME_CONFIG = {**config_data, **RUNTIME_CONFIG}
        logging.info(f"Merged environment variables into config found in {config_file}")


def get(config_var=None, default=None):
    if config_var is None:
        return RUNTIME_CONFIG
    return RUNTIME_CONFIG.get(config_var, default)


def get_list(config_var, default=None):
    var = get(config_var, None)
    if var is not None:
        if isinstance(var, list):
            return var
        return var.split(",")
    return default


def set_value(config_var, val):
    RUNTIME_CONFIG[config_var] = val


def exists(config_var):
    return config_var in RUNTIME_CONFIG


def copy():
    return RUNTIME_CONFIG.copy()


def delete(key):
    del RUNTIME_CONFIG[key]
