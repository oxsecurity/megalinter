# Class to manage MegaLinter plugins
import logging
import os
import shutil
import subprocess
import sys

import requests
import yaml
from megalinter import config, linter_factory, utils


def list_plugins(request_id):
    plugins = config.get_list(request_id, "PLUGINS", [])
    return plugins


# Load & install plugins from external URLs
def initialize_plugins(request_id):
    plugins = list_plugins(request_id)
    for plugin in plugins:
        descriptor_file = load_plugin(plugin)
        install_plugin(descriptor_file, request_id)


# Load plugin descriptor
def load_plugin(plugin):
    # Check if plugin is a URL or local path
    if plugin.startswith("https://") or plugin.startswith("file://"):
        # Check validity of plugin URL/path
        descriptor_file = "/megalinter-descriptors/" + plugin.rsplit("/", 1)[1]
        if "/mega-linter-plugin-" not in plugin:
            raise Exception(
                "[Plugins] Plugin descriptor file must be hosted in a directory containing /mega-linter-plugin-"
            )
        if not descriptor_file.endswith(".megalinter-descriptor.yml"):
            raise Exception(
                "[Plugins] Plugin descriptor file must end with .megalinter-descriptor.yml"
            )

        # Download plugin and write it in megalinter
        try:
            if plugin.startswith("https://"):
                r = requests.get(plugin, allow_redirects=True).content
            else:
                # From file://<path>, test both <path> and /tmp/lint/<path>
                plugin_path = plugin.split("file://")[1]
                if not os.access(plugin_path, os.R_OK):
                    plugin_path = "/tmp/lint/" + plugin_path
                    if not os.access(plugin_path, os.R_OK):
                        raise Exception(
                            f"[Plugins] Local plugin descriptor not found or not readable {plugin}"
                        )
                if os.stat(plugin_path).st_size == 0:
                    raise Exception(f"[Plugins] Plugin descriptor is empty: {plugin}")
                r = open(plugin_path, "r").read()
            plugin_descriptor = yaml.safe_load(r)
            plugin_descriptor["is_plugin"] = True
            with open(descriptor_file, "w") as outfile:
                yaml.dump(plugin_descriptor, outfile)
            logging.info(
                f"[Plugins] Loaded plugin descriptor {descriptor_file} from {plugin}"
            )
        except Exception as e:
            raise Exception(
                f"[Plugins] Unable to load remote plugin {plugin}:\n{str(e)}"
            )
        return descriptor_file
    else:
        raise Exception(
            "[Plugins] Plugin descriptors must follow the format"
            " https://**/mega-linter-plugin-**/**.mega-linter-descriptor.yml or"
            f" file://**/mega-linter-plugin-**/**.mega-linter-descriptor.yml (wrong value {plugin})"
        )


# Run plugin installation routines
def install_plugin(descriptor_file, request_id):
    descriptor = linter_factory.build_descriptor_info(descriptor_file)
    # Install descriptor level items
    if "install" in descriptor:
        process_install(descriptor["install"], request_id)
    # Install linter level items
    if "linters" in descriptor:
        for linter_description in descriptor["linters"]:
            if "install" in linter_description:
                process_install(linter_description["install"], request_id)
    logging.info(
        f"[Plugins] Successful initialization of {descriptor['descriptor_id']} plugins"
    )


# WARNING: works only with dockerfile and RUN instructions for now
def process_install(install, request_id):
    # Build commands from descriptor
    commands = []
    # Dockerfile commands
    if "dockerfile" in install:
        # Remove RUN and \ at the end of lines from commands
        commands += [
            command.replace("RUN ", "").replace(" \\\n", "\n").replace(" \\", " ")
            for command in install["dockerfile"]
        ]
    # Run install commands
    for command in commands:
        logging.debug("[Plugins] Install command: " + str(command))
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            executable=shutil.which("bash") if sys.platform == "win32" else "/bin/bash",
            env=config.build_env(request_id),
        )
        return_code = process.returncode
        stdout = utils.decode_utf8(process.stdout)
        logging.debug(f"[Plugins] Result ({str(return_code)}): {stdout}")
        if return_code != 0:
            raise Exception(
                f"[Plugins] Error while running install command {command}:\n{stdout}"
            )
