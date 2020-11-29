#!/usr/bin/env python3
import json
import logging
import os

import yaml

ENV_RUNTIME_KEY = "_MEGALINTER_RUNTIME_CONFIG"


def init_config(workspace):
    if os.environ.get(ENV_RUNTIME_KEY, "") != "":
        logging.info("Init config: Runtime config already initialized")
        return
    env = os.environ.copy()
    if workspace is None:
        set_config(env)
        print("Mega-Linter init config: Environment variables only (no workspace)")
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
            print(f"Mega-Linter init config: {config_file} + Environment variables")
    else:
        runtime_config = env
        print("Mega-Linter init config: Environment variables")
    set_config(runtime_config)


def get_config():
    runtime_config_str = os.environ.get(ENV_RUNTIME_KEY, "")
    if runtime_config_str != "":
        return json.loads(runtime_config_str)
    else:
        return os.environ.copy()


def set_config(config):
    os.environ[ENV_RUNTIME_KEY] = json.dumps(config)


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


def delete(key=None):
    if key is None:
        del os.environ[ENV_RUNTIME_KEY]
        logging.info("Cleared Mega-Linter runtime config")
        return
    config = get_config()
    if key in config:
        del config[key]
    set_config(config)
