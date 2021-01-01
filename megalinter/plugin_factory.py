# Class to manage Mega-Linter plugins
import logging
import shutil
import subprocess
import sys

import requests
from megalinter import config, linter_factory, utils


def list_plugins():
    plugins = config.get_list("PLUGINS", [])
    return plugins


# Load & install plugins from external URLs
def initialize_plugins():
    plugins = list_plugins()
    for plugin in plugins:
        descriptor_file = load_plugin(plugin)
        install_plugin(descriptor_file)


# Load plugin descriptor
def load_plugin(plugin):
    if plugin.startswith("https://"):
        # Check validity of plugin URL
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
            r = requests.get(plugin, allow_redirects=True)
            open(descriptor_file, "wb").write(r.content)
            logging.info(
                f"[Plugins] Loaded plugin descriptor {descriptor_file} from {plugin}"
            )
        except Exception as e:
            raise Exception(f"[Plugins] Unable to load plugin {plugin}:\n{str(e)}")
        return descriptor_file
    else:
        raise Exception(
            "[Plugins] Plugin descriptors must follow the format"
            f" https://**/mega-linter-plugin-**/**.mega-linter-descriptor.yml (wrong value {plugin})"
        )


# Run plugin installation routines
def install_plugin(descriptor_file):
    descriptor = linter_factory.build_descriptor_info(descriptor_file)
    # Install descriptor level items
    if "install" in descriptor:
        process_install(descriptor["install"])
    # Install linter level items
    if "linters" in descriptor:
        for linter_description in descriptor["linters"]:
            if "install" in descriptor:
                process_install(linter_description["install"])
    logging.info(
        f"[Plugins] Successful initialization of {descriptor['descriptor_id']} plugins"
    )


# WARNING: works only with dockerfile and RUN instructions for now
def process_install(install):
    # Build commands from descriptor
    commands = []
    # Dockerfile commands
    if "dockerfile" in install:
        # Remove RUN and \ at the end of lines from commands
        commands += [
            command.replace("RUN ").replace(" \\\n", "\n")
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
        )
        return_code = process.returncode
        stdout = utils.decode_utf8(process.stdout)
        logging.debug(f"[Plugins] Result ({str(return_code)}): {stdout}")
        if return_code != 0:
            raise Exception(
                f"[Plugins] Error while running install command {command}:\n{stdout}"
            )
