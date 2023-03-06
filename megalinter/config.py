#!/usr/bin/env python3
import json
import logging
import os
import shlex
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePath
from typing import AnyStr, cast
from urllib.parse import ParseResult, urlparse, urlunparse

import requests
import yaml

CONFIG_DATA = None
CONFIG_SOURCE = None

JsonValue = (
    None | bool | int | float | str | Sequence["JsonValue"] | Mapping[str, "JsonValue"]
)
JsonObject = dict[str, JsonValue]


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
    config_file = None
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
        combined_config: JsonObject = {}
        CONFIG_SOURCE = combine_config(
            workspace, runtime_config, combined_config, CONFIG_SOURCE
        )
        runtime_config = combined_config
    # Print & set config in cache
    print(f"[config] {CONFIG_SOURCE}")
    set_config(runtime_config)


def combine_config(
    workspace: str | None,
    config: JsonObject,
    combined_config: JsonObject,
    config_source: str,
    child_uri: ParseResult | None = None,
) -> str:
    workspace_path = Path(workspace) if workspace else None
    parsed_uri: ParseResult | None = None
    extends = cast(str | Sequence[str], config["EXTENDS"])
    if isinstance(extends, str):
        extends = extends.split(",")
    for extends_item in extends:
        if extends_item.startswith("http"):
            parsed_uri = urlparse(extends_item)
            extends_config_data = download_config(extends_item)
        else:
            path = PurePath(extends_item)
            if child_uri:
                parsed_uri = resolve_uri(child_uri, path)
                uri = urlunparse(parsed_uri)
                extends_config_data = download_config(uri)
            else:
                resolved_path = workspace_path / path if workspace_path else Path(path)
                with resolved_path.open("r", encoding="utf-8") as f:
                    extends_config_data = yaml.safe_load(f)
        combined_config.update(extends_config_data)
        config_source += f"\n[config] - extends from: {extends_item}"
        if "EXTENDS" in extends_config_data:
            combine_config(
                workspace,
                extends_config_data,
                combined_config,
                config_source,
                parsed_uri,
            )
    combined_config.update(config)
    return config_source


def download_config(uri: AnyStr) -> JsonObject:
    r = requests.get(uri, allow_redirects=True)
    assert r.status_code == 200, f"Unable to retrieve EXTENDS config file {uri!r}"
    return yaml.safe_load(r.content)


def resolve_uri(child_uri: ParseResult, relative_config_path: PurePath) -> ParseResult:
    match child_uri.netloc:
        case "cdn.jsdelivr.net" | "git.launchpad.net":
            repo_root_index = 3
        case "code.rhodecode.com" | "git.savannah.gnu.org" | "raw.githubusercontent.com" | "repo.or.cz":
            repo_root_index = 4
        case "bitbucket.org" | "git.sr.ht" | "gitee.com" | "pagure.io":
            repo_root_index = 5
        case "codeberg.org" | "gitea.com" | "gitlab.com" | "huggingface.co" | "p.phcdn.net" | "sourceforge.net":
            repo_root_index = 6
        case _:
            message = (
                f"Unsupported Git repo hosting service: {child_uri.netloc}. "
                "Request support be added to MegaLinter, or use absolute URLs "
                "with EXTENDS in inherited configs rather than relative paths."
            )
            raise ValueError(message)
    child_path = PurePath(child_uri.path)
    repo_root_path = child_path.parts[:repo_root_index]
    path = PurePath(*repo_root_path, str(relative_config_path))
    return child_uri._replace(path=str(path))


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
