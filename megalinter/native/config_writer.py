#!/usr/bin/env python3
# Writes NATIVE_LINTERS in the MegaLinter configuration file of the analyzed repository.
# The file is edited as text, so its comments and layout are kept, then parsed again to
# check the result: when the value is not the expected one, the file is left untouched
import os
import re

import yaml

from megalinter import config
from megalinter.native.context import NativeError

DEFAULT_CONFIG_FILE_NAME = ".mega-linter.yml"
COMMENT = "# Linters run by native mode (without Docker). CI keeps running every active linter"
KEY_REGEX = re.compile(r"^NATIVE_LINTERS[ \t]*:.*$")


def find_config_file(workspace, request_id=None):
    configured = config.get(request_id, "MEGALINTER_CONFIG")
    if configured is not None:
        if configured.startswith("https://"):
            raise NativeError(
                "MEGALINTER_CONFIG is a remote file: add NATIVE_LINTERS to your "
                "local configuration yourself"
            )
        if os.path.isfile(configured):
            return configured
        return os.path.join(workspace, configured)
    for candidate in config.CONFIG_FILE_CANDIDATES:
        path = os.path.join(workspace, candidate)
        if os.path.isfile(path):
            return path
    return os.path.join(workspace, DEFAULT_CONFIG_FILE_NAME)


def build_block(keys, newline):
    return newline.join(["NATIVE_LINTERS:", *[f"  - {key}" for key in keys]])


# Lines of the existing NATIVE_LINTERS entry: the key line, then its block list
# (indented, or not indented as YAML allows) and the comments inside it
def find_entry(lines):
    start = next((i for i, line in enumerate(lines) if KEY_REGEX.match(line)), None)
    if start is None:
        return None
    end = start + 1
    last_content = start
    while end < len(lines):
        line = lines[end]
        if line.strip() == "":
            end += 1
            continue
        if line[0] in " \t" or line.startswith("- "):
            last_content = end
            end += 1
            continue
        break
    return start, last_content + 1


def replace_native_linters(content, keys):
    newline = "\r\n" if "\r\n" in content else "\n"
    lines = content.replace("\r\n", "\n").split("\n")
    block = build_block(keys, "\n")
    entry = find_entry(lines)
    if entry is not None:
        start, end = entry
        lines[start:end] = block.split("\n")
        return newline.join(lines)
    text = "\n".join(lines).rstrip("\n")
    separator = "\n\n" if text != "" else ""
    return newline.join((text + separator + COMMENT + "\n" + block + "\n").split("\n"))


def write_native_linters(config_file, keys):
    existing = ""
    if os.path.isfile(config_file):
        with open(config_file, "r", encoding="utf-8", newline="") as file:
            existing = file.read()
        try:
            yaml.safe_load(existing)
        except yaml.YAMLError as e:
            raise NativeError(f"{config_file} is not valid YAML: {e}") from e
    updated = replace_native_linters(existing, keys)
    try:
        parsed = yaml.safe_load(updated)
    except yaml.YAMLError:
        parsed = None
    if not isinstance(parsed, dict) or parsed.get("NATIVE_LINTERS") != list(keys):
        raise NativeError(
            f"Unable to edit {config_file} safely. Add this to it yourself:\n"
            + build_block(keys, "\n")
        )
    os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
    with open(config_file, "w", encoding="utf-8", newline="") as file:
        file.write(updated)


def read_configured_linters(config_file):
    if not os.path.isfile(config_file):
        return []
    with open(config_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    value = data.get("NATIVE_LINTERS") if isinstance(data, dict) else None
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).lower() != "all"]
