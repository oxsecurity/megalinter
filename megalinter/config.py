#!/usr/bin/env python3
import json
import logging
import os

import yaml
from megalinter import utils


def get_config():
    runtime_config = os.environ.get("_MEGALINTER_CONFIG_RUNTIME", "{}")
    if runtime_config != "{}":
        return json.loads(runtime_config)
    env = os.environ.copy()
    config_file_name = os.environ.get("MEGALINTER_CONFIG", ".megalinter.yml")
    config_file = utils.REPO_HOME_DEFAULT + os.path.sep + config_file_name
    # if .megalinter.yml is found, merge its values with environment variables (with priority to env values)
    if os.path.isfile(config_file):
        with open(config_file, "r", encoding="utf-8") as config_file_stream:
            config_data = yaml.load(config_file_stream, Loader=yaml.FullLoader)
            runtime_config = {**config_data, **env}
            logging.info(
                f"Merged environment variables into config found in {config_file}"
            )
    else:
        logging.info(
            f"No {config_file} config file found: use only environment variables"
        )
    set_config(runtime_config)
    return runtime_config


def set_config(config):
    os.environ["_MEGALINTER_CONFIG_RUNTIME"] = json.dumps(config)


def get(config_var=None, default=None):
    if config_var is None:
        return get_config()
    return get_config().get(config_var, default)


def get_list(config_var, default=None):
    var = get(config_var, None)
    if var is not None:
        if isinstance(var, list):
            return var
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


def delete(key):
    config = get_config()
    del config[key]
    set_config(config)
