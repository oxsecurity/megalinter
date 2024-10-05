# !/usr/bin/env python3
"""
Automatically generate source code ,descriptive files Dockerfiles and documentation
"""
# pylint: disable=import-error
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from shutil import copyfile, which
from typing import Any
from urllib import parse as parse_urllib

import git
import jsonschema
import markdown
import megalinter
import requests
import terminaltables
import webpreview
import yaml
from bs4 import BeautifulSoup
from giturlparse import parse
from megalinter import config, utils
from megalinter.constants import (
    DEFAULT_DOCKERFILE_APK_PACKAGES,
    DEFAULT_RELEASE,
    DEFAULT_REPORT_FOLDER_NAME,
    ML_DOC_URL_BASE,
    ML_DOCKER_IMAGE,
    ML_DOCKER_IMAGE_LEGACY,
    ML_DOCKER_IMAGE_LEGACY_V5,
    ML_REPO,
    ML_REPO_URL,
)
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from webpreview import web_preview

RELEASE = "--release" in sys.argv
UPDATE_STATS = "--stats" in sys.argv or RELEASE is True
UPDATE_DOC = "--doc" in sys.argv or RELEASE is True
UPDATE_DEPENDENTS = "--dependents" in sys.argv
UPDATE_CHANGELOG = "--changelog" in sys.argv
IS_LATEST = "--latest" in sys.argv
DELETE_DOCKERFILES = "--delete-dockerfiles" in sys.argv
DELETE_TEST_CLASSES = "--delete-test-classes" in sys.argv

# Release args management
if RELEASE is True:
    RELEASE_TAG = sys.argv[sys.argv.index("--release") + 1]
    if "v" not in RELEASE_TAG:
        RELEASE_TAG = "v" + RELEASE_TAG
    VERSION = RELEASE_TAG.replace("v", "")
    VERSION_V = "v" + VERSION
elif "--version" in sys.argv:
    VERSION = sys.argv[sys.argv.index("--version") + 1].replace("v", "")
    VERSION_V = "v" + VERSION
else:
    VERSION = "beta"
    VERSION_V = VERSION
# latest management
if IS_LATEST is True:
    VERSION_URL_SEGMENT = "latest"
else:
    VERSION_URL_SEGMENT = VERSION


MKDOCS_URL_ROOT = ML_DOC_URL_BASE + VERSION_URL_SEGMENT

BRANCH = "main"
URL_ROOT = ML_REPO_URL + "/tree/" + BRANCH
URL_RAW_ROOT = ML_REPO_URL + "/raw/" + BRANCH
TEMPLATES_URL_ROOT = URL_ROOT + "/TEMPLATES"
DOCS_URL_ROOT = URL_ROOT + "/docs"
DOCS_URL_DESCRIPTORS_ROOT = DOCS_URL_ROOT + "/descriptors"
DOCS_URL_FLAVORS_ROOT = DOCS_URL_ROOT + "/flavors"
DOCS_URL_RAW_ROOT = URL_RAW_ROOT + "/docs"
REPO_HOME = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
REPO_ICONS = REPO_HOME + "/docs/assets/icons"
REPO_IMAGES = REPO_HOME + "/docs/assets/images"

VERSIONS_FILE = REPO_HOME + "/.automation/generated/linter-versions.json"
LICENSES_FILE = REPO_HOME + "/.automation/generated/linter-licenses.json"
USERS_FILE = REPO_HOME + "/.automation/generated/megalinter-users.json"
HELPS_FILE = REPO_HOME + "/.automation/generated/linter-helps.json"
LINKS_PREVIEW_FILE = REPO_HOME + "/.automation/generated/linter-links-previews.json"
DOCKER_STATS_FILE = REPO_HOME + "/.automation/generated/flavors-stats.json"
PLUGINS_FILE = REPO_HOME + "/.automation/plugins.yml"
FLAVORS_DIR = REPO_HOME + "/flavors"
LINTERS_DIR = REPO_HOME + "/linters"
GLOBAL_FLAVORS_FILE = REPO_HOME + "/megalinter/descriptors/all_flavors.json"

BASE_SHIELD_IMAGE_LINK = "https://img.shields.io/docker/image-size"
BASE_SHIELD_COUNT_LINK = "https://img.shields.io/docker/pulls"

DESCRIPTOR_JSON_SCHEMA = (
    f"{REPO_HOME}/megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json"
)
CONFIG_JSON_SCHEMA = f"{REPO_HOME}/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json"
OWN_MEGALINTER_CONFIG_FILE = f"{REPO_HOME}/.mega-linter.yml"

IDE_LIST = {
    "atom": {"label": "Atom", "url": "https://atom.io/"},
    "brackets": {"label": "Brackets", "url": "https://brackets.io/"},
    "eclipse": {"label": "Eclipse", "url": "https://www.eclipse.org/"},
    "emacs": {"label": "Emacs", "url": "https://www.gnu.org/software/emacs/"},
    "idea": {
        "label": "IDEA",
        "url": "https://www.jetbrains.com/products.html#type=ide",
    },
    "sublime": {"label": "Sublime Text", "url": "https://www.sublimetext.com/"},
    "vim": {"label": "vim", "url": "https://www.vim.org/"},
    "vscode": {"label": "Visual Studio Code", "url": "https://code.visualstudio.com/"},
}

DEPRECATED_LINTERS = [
    "CREDENTIALS_SECRETLINT",  # Removed in v6
    "DOCKERFILE_DOCKERFILELINT",  # Removed in v6
    "GIT_GIT_DIFF",  # Removed in v6
    "PHP_BUILTIN",  # Removed in v6
    "KUBERNETES_KUBEVAL",  # Removed in v7
    "REPOSITORY_GOODCHECK",  # Removed in v7
    "SPELL_MISSPELL",  # Removed in v7
    "TERRAFORM_CHECKOV",  # Removed in v7
    "TERRAFORM_KICS",  # Removed in v7
    "CSS_SCSSLINT",  # Removed in v8
    "OPENAPI_SPECTRAL",  # Removed in v8
    "SQL_SQL_LINT",  # Removed in v8
]

DESCRIPTORS_FOR_BUILD_CACHE = None


# Generate one Dockerfile by MegaLinter flavor
def generate_all_flavors():
    flavors = megalinter.flavor_factory.list_megalinter_flavors()

    for flavor, flavor_info in flavors.items():
        generate_flavor(flavor, flavor_info)
    update_mkdocs_and_workflow_yml_with_flavors()
    if UPDATE_STATS is True:
        try:
            update_docker_pulls_counter()
        except requests.exceptions.ConnectionError as e:
            logging.warning(
                "Connection error - Unable to update docker pull counters: " + str(e)
            )
        except Exception as e:
            logging.warning("Unable to update docker pull counters: " + str(e))


# Automatically generate Dockerfile , action.yml and upgrade all_flavors.json
def generate_flavor(flavor, flavor_info):
    descriptor_and_linters = []
    flavor_descriptors = []
    flavor_linters = []
    # Get install instructions at descriptor level
    descriptor_files = megalinter.linter_factory.list_descriptor_files()
    for descriptor_file in descriptor_files:
        with open(descriptor_file, "r", encoding="utf-8") as f:
            descriptor = yaml.safe_load(f)
            if (
                match_flavor(descriptor, flavor, flavor_info) is True
                and "install" in descriptor
            ):
                descriptor_and_linters += [descriptor]
                flavor_descriptors += [descriptor["descriptor_id"]]
    # Get install instructions at linter level
    linters = megalinter.linter_factory.list_all_linters(({"request_id": "build"}))
    requires_docker = False
    for linter in linters:
        if match_flavor(vars(linter), flavor, flavor_info) is True:
            descriptor_and_linters += [vars(linter)]
            flavor_linters += [linter.name]
            if linter.cli_docker_image is not None:
                requires_docker = True
    # Initialize Dockerfile
    if flavor == "all":
        dockerfile = f"{REPO_HOME}/Dockerfile"
        if RELEASE is True:
            image_release = RELEASE_TAG
            action_yml = f"""# Automatically {'@'}generated by build.py
name: "MegaLinter"
author: "Nicolas Vuillamy"
description: "Combine all available linters to automatically validate your sources without configuration !"
outputs:
  has_updated_sources:
    description: "0 if no source file has been updated, 1 if source files has been updated"
runs:
  using: "docker"
  image: "docker://{ML_DOCKER_IMAGE}:{image_release}"
  args:
    - "-v"
    - "/var/run/docker.sock:/var/run/docker.sock:rw"
branding:
  icon: "check"
  color: "green"
"""
            main_action_yml = "action.yml"
            with open(main_action_yml, "w", encoding="utf-8") as file:
                file.write(action_yml)
                logging.info(f"Updated {main_action_yml}")
    else:
        # Flavor json
        flavor_file = f"{FLAVORS_DIR}/{flavor}/flavor.json"
        if os.path.isfile(flavor_file):
            with open(flavor_file, "r", encoding="utf-8") as json_file:
                flavor_info = json.load(json_file)
        flavor_info["descriptors"] = flavor_descriptors
        flavor_info["linters"] = flavor_linters
        os.makedirs(os.path.dirname(flavor_file), exist_ok=True)
        with open(flavor_file, "w", encoding="utf-8") as outfile:
            json.dump(flavor_info, outfile, indent=4, sort_keys=True)
            outfile.write("\n")
        # Write in global flavors files
        with open(GLOBAL_FLAVORS_FILE, "r", encoding="utf-8") as json_file:
            global_flavors = json.load(json_file)
            global_flavors[flavor] = flavor_info
        with open(GLOBAL_FLAVORS_FILE, "w", encoding="utf-8") as outfile:
            json.dump(global_flavors, outfile, indent=4, sort_keys=True)
            outfile.write("\n")
        # Flavored dockerfile
        dockerfile = f"{FLAVORS_DIR}/{flavor}/Dockerfile"
        if not os.path.isdir(os.path.dirname(dockerfile)):
            os.makedirs(os.path.dirname(dockerfile), exist_ok=True)
        copyfile(f"{REPO_HOME}/Dockerfile", dockerfile)
        flavor_label = flavor_info["label"]
        comment = f"# MEGALINTER FLAVOR [{flavor}]: {flavor_label}"
        with open(dockerfile, "r+", encoding="utf-8") as f:
            first_line = f.readline().rstrip()
            if first_line.startswith("# syntax="):
                comment = f"{first_line}\n{comment}"
            else:
                f.seek(0)
            content = f.read()
            f.seek(0)
            f.truncate()
            f.write(f"{comment}\n{content}")
        # Generate action.yml
        if RELEASE is True:
            image_release = RELEASE_TAG
        else:
            image_release = DEFAULT_RELEASE
        flavor_x = f"[{flavor} flavor]"
        action_yml = f""" # Automatically {'@'}generated by build.py
name: "MegaLinter"
author: "Nicolas Vuillamy"
description: "{flavor_x} Combine all available linters to automatically validate your sources without configuration !"
outputs:
  has_updated_sources:
    description: "0 if no source file has been updated, 1 if source files has been updated"
runs:
  using: "docker"
  image: "docker://{ML_DOCKER_IMAGE}-{flavor}:{image_release}"
  args:
    - "-v"
    - "/var/run/docker.sock:/var/run/docker.sock:rw"
branding:
  icon: "check"
  color: "green"
"""
        flavor_action_yml = f"{FLAVORS_DIR}/{flavor}/action.yml"
        with open(flavor_action_yml, "w", encoding="utf-8") as file:
            file.write(action_yml)
            logging.info(f"Updated {flavor_action_yml}")
    extra_lines = [
        "COPY entrypoint.sh /entrypoint.sh",
        "RUN chmod +x entrypoint.sh",
        'ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]',
    ]
    build_dockerfile(
        dockerfile,
        descriptor_and_linters,
        requires_docker,
        flavor,
        extra_lines,
        {"cargo": ["sarif-fmt"]},
    )


def build_dockerfile(
    dockerfile,
    descriptor_and_linters,
    requires_docker,
    flavor,
    extra_lines,
    extra_packages=None,
):
    if extra_packages is None:
        extra_packages = {}
    # Gather all dockerfile commands
    docker_from = []
    docker_arg = []
    docker_copy = []
    docker_other = []
    all_dockerfile_items = []
    apk_packages = DEFAULT_DOCKERFILE_APK_PACKAGES.copy()
    npm_packages = []
    pip_packages = []
    pipvenv_packages = {}
    gem_packages = []
    cargo_packages = [] if "cargo" not in extra_packages else extra_packages["cargo"]
    is_docker_other_run = False
    # Manage docker
    if requires_docker is True:
        apk_packages += ["docker", "openrc"]
        docker_other += [
            "RUN rc-update add docker boot && rc-service docker start || true"
        ]
        is_docker_other_run = True
    for item in descriptor_and_linters:
        if "install" not in item:
            item["install"] = {}
        # Collect Dockerfile items
        if "dockerfile" in item["install"]:
            item_label = item.get("linter_name", item.get("descriptor_id", ""))
            docker_other += [f"# {item_label} installation"]
            for dockerfile_item in item["install"]["dockerfile"]:
                # FROM
                if dockerfile_item.startswith("FROM"):
                    if dockerfile_item in all_dockerfile_items:
                        dockerfile_item = (
                            "# Next FROM line commented because already managed by another linter\n"
                            "# " + "\n# ".join(dockerfile_item.splitlines())
                        )
                    docker_from += [dockerfile_item]
                # ARG
                elif dockerfile_item.startswith("ARG") or (
                    len(dockerfile_item.splitlines()) > 1
                    and dockerfile_item.splitlines()[0].startswith("# renovate: ")
                    and dockerfile_item.splitlines()[1].startswith("ARG")
                ):
                    docker_arg += [dockerfile_item]
                # COPY
                elif dockerfile_item.startswith("COPY"):
                    if dockerfile_item in all_dockerfile_items:
                        dockerfile_item = (
                            "# Next COPY line commented because already managed by another linter\n"
                            "# " + "\n# ".join(dockerfile_item.splitlines())
                        )
                    docker_copy += [dockerfile_item]
                    docker_other += [
                        "# Managed with "
                        + "\n#              ".join(dockerfile_item.splitlines())
                    ]
                # Already used item
                elif (
                    dockerfile_item in all_dockerfile_items
                    or dockerfile_item.replace(
                        "RUN ", "RUN --mount=type=secret,id=GITHUB_TOKEN "
                    )
                    in all_dockerfile_items
                ):
                    dockerfile_item = (
                        "# Next line commented because already managed by another linter\n"
                        "# " + "\n# ".join(dockerfile_item.splitlines())
                    )
                    docker_other += [dockerfile_item]
                # RUN (standalone with GITHUB_TOKEN)
                elif (
                    dockerfile_item.startswith("RUN")
                    and "GITHUB_TOKEN" in dockerfile_item
                ):
                    dockerfile_item_cmd = dockerfile_item.replace(
                        "RUN ", "RUN --mount=type=secret,id=GITHUB_TOKEN "
                    )
                    docker_other += [dockerfile_item_cmd]
                    is_docker_other_run = False
                # RUN (start)
                elif dockerfile_item.startswith("RUN") and is_docker_other_run is False:
                    docker_other += [dockerfile_item]
                    is_docker_other_run = True
                # RUN (append)
                elif dockerfile_item.startswith("RUN") and is_docker_other_run is True:
                    dockerfile_item_cmd = dockerfile_item.replace("RUN", "    &&")
                    # Add \ in previous instruction line
                    for index, prev_instruction_line in reversed(
                        list(enumerate(docker_other))
                    ):
                        if (
                            prev_instruction_line.strip() != ""
                            and not prev_instruction_line.startswith("#")
                        ):
                            # Remove last char if \n
                            prev_instruction_line = (
                                prev_instruction_line
                                if not prev_instruction_line.endswith("\n")
                                else prev_instruction_line[:-1]
                            )
                            docker_other[index] = prev_instruction_line + " \\"
                            break
                    docker_other += [dockerfile_item_cmd]
                # Other
                else:
                    is_docker_other_run = False
                    docker_other += [dockerfile_item]
                all_dockerfile_items += [dockerfile_item]
            docker_other += ["#"]
        # Collect python packages
        if "apk" in item["install"]:
            apk_packages += item["install"]["apk"]
        # Collect npm packages
        if "npm" in item["install"]:
            npm_packages += item["install"]["npm"]
        # Collect python for venvs
        if "linter_name" in item and "pip" in item["install"]:
            pipvenv_packages[item["linter_name"]] = item["install"]["pip"]
        # Collect python packages
        if "pip" in item["install"]:
            pip_packages += item["install"]["pip"]
        # Collect ruby packages
        if "gem" in item["install"]:
            gem_packages += item["install"]["gem"]
        # Collect cargo packages (rust)
        if "cargo" in item["install"]:
            cargo_packages += item["install"]["cargo"]
    # Add node install if node packages are here
    if len(npm_packages) > 0:
        apk_packages += ["npm", "nodejs-current", "yarn"]
    # Add ruby apk packages if gem packages are here
    if len(gem_packages) > 0:
        apk_packages += ["ruby", "ruby-dev", "ruby-bundler", "ruby-rdoc"]
    # Separate args used in FROM instructions from others
    all_from_instructions = "\n".join(list(dict.fromkeys(docker_from)))
    docker_arg_top = []
    docker_arg_main = []
    for docker_arg_item in docker_arg:
        match = re.match(
            r"(?:# renovate: .*\n)?ARG\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=?\s*",
            docker_arg_item,
        )
        arg_name = match.group(1)
        if arg_name in all_from_instructions:
            docker_arg_top += [docker_arg_item]
        else:
            docker_arg_main += [docker_arg_item]
    # Replace between tags in Dockerfile
    # Commands
    replace_in_file(
        dockerfile,
        "#FROM__START",
        "#FROM__END",
        "\n".join(list(dict.fromkeys(docker_from))),
    )
    replace_in_file(
        dockerfile,
        "#ARGTOP__START",
        "#ARGTOP__END",
        "\n".join(list(dict.fromkeys(docker_arg_top))),
    )
    replace_in_file(
        dockerfile,
        "#ARG__START",
        "#ARG__END",
        "\n".join(list(dict.fromkeys(docker_arg_main))),
    )
    replace_in_file(
        dockerfile,
        "#COPY__START",
        "#COPY__END",
        "\n".join(docker_copy),
    )
    replace_in_file(
        dockerfile,
        "#OTHER__START",
        "#OTHER__END",
        "\n".join(docker_other),
    )
    # apk packages
    apk_install_command = ""
    if len(apk_packages) > 0:
        apk_install_command = (
            "RUN apk add --no-cache \\\n                "
            + " \\\n                ".join(list(dict.fromkeys(apk_packages)))
            + " \\\n    && git config --global core.autocrlf true"
        )
    replace_in_file(dockerfile, "#APK__START", "#APK__END", apk_install_command)
    # cargo packages
    cargo_install_command = ""
    keep_rustup = False
    if len(cargo_packages) > 0:
        rust_commands = []
        if "clippy" in cargo_packages:
            cargo_packages.remove("clippy")
            rust_commands += ["rustup component add clippy"]
            keep_rustup = True
        # Only COMPILER_ONLY in descriptors just to have rust toolchain in the Dockerfile
        if all(p == "COMPILER_ONLY" for p in cargo_packages):
            rust_commands += [
                'echo "No cargo package to install, we just need rust for dependencies"'
            ]
            keep_rustup = True
        # Cargo packages to install minus empty package
        elif len(cargo_packages) > 0:
            cargo_packages = [
                p for p in cargo_packages if p != "COMPILER_ONLY"
            ]  # remove empty string packages
            cargo_cmd = "cargo install --force --locked " + "  ".join(
                list(dict.fromkeys(cargo_packages))
            )
            rust_commands += [cargo_cmd]
        rustup_cargo_cmd = " && ".join(rust_commands)
        cargo_install_command = (
            "RUN curl https://sh.rustup.rs -sSf |"
            + " sh -s -- -y --profile minimal --default-toolchain stable \\\n"
            + '    && export PATH="/root/.cargo/bin:${PATH}" \\\n'
            + f"    && {rustup_cargo_cmd} \\\n"
            + "    && rm -rf /root/.cargo/registry /root/.cargo/git "
            + "/root/.cache/sccache"
            + (" /root/.rustup" if keep_rustup is False else "")
            + "\n"
            + 'ENV PATH="/root/.cargo/bin:${PATH}"'
        )
    replace_in_file(dockerfile, "#CARGO__START", "#CARGO__END", cargo_install_command)
    # NPM packages
    npm_install_command = ""
    if len(npm_packages) > 0:
        npm_install_command = (
            "WORKDIR /node-deps\n"
            + "RUN npm --no-cache install --ignore-scripts --omit=dev \\\n                "
            + " \\\n                ".join(list(dict.fromkeys(npm_packages)))
            + "  && \\\n"
            #    + '       echo "Fixing audit issues with npm…" \\\n'
            #    + "    && npm audit fix --audit-level=critical || true \\\n" # Deactivated for now
            + '    echo "Cleaning npm cache…" \\\n'
            + "    && npm cache clean --force || true \\\n"
            + '    && echo "Changing owner of node_modules files…" \\\n'
            + '    && chown -R "$(id -u)":"$(id -g)" node_modules # fix for https://github.com/npm/cli/issues/5900 \\\n'
            + '    && echo "Removing extra node_module files…" \\\n'
            + '    && find . \\( -not -path "/proc" \\)'
            + " -and \\( -type f"
            + ' \\( -iname "*.d.ts"'
            + ' -o -iname "*.map"'
            + ' -o -iname "*.npmignore"'
            + ' -o -iname "*.travis.yml"'
            + ' -o -iname "CHANGELOG.md"'
            + ' -o -iname "README.md"'
            + ' -o -iname ".package-lock.json"'
            + ' -o -iname "package-lock.json"'
            + " \\) -o -type d -name /root/.npm/_cacache \\) -delete \n"
            + "WORKDIR /\n"
        )
    replace_in_file(dockerfile, "#NPM__START", "#NPM__END", npm_install_command)
    # Python pip packages
    pip_install_command = ""
    if len(pip_packages) > 0:
        pip_install_command = (
            "RUN PYTHONDONTWRITEBYTECODE=1 pip3 install --no-cache-dir --upgrade pip &&"
            + " PYTHONDONTWRITEBYTECODE=1 pip3 install --no-cache-dir --upgrade \\\n          '"
            + "' \\\n          '".join(list(dict.fromkeys(pip_packages)))
            + "' && \\\n"
            + r"find . \( -type f \( -iname \*.pyc -o -iname \*.pyo \) -o -type d -iname __pycache__ \) -delete"
            + " \\\n    && "
            + "rm -rf /root/.cache"
        )
    replace_in_file(dockerfile, "#PIP__START", "#PIP__END", pip_install_command)
    # Python packages in venv
    if len(pipvenv_packages.items()) > 0:
        pipenv_install_command = (
            "RUN PYTHONDONTWRITEBYTECODE=1 pip3 install"
            " --no-cache-dir --upgrade pip virtualenv \\\n"
        )
        env_path_command = 'ENV PATH="${PATH}"'
        for pip_linter, pip_linter_packages in pipvenv_packages.items():
            pipenv_install_command += (
                f'    && mkdir -p "/venvs/{pip_linter}" '
                + f'&& cd "/venvs/{pip_linter}" '
                + "&& virtualenv . "
                + "&& source bin/activate "
                + "&& PYTHONDONTWRITEBYTECODE=1 pip3 install --no-cache-dir "
                + (" ".join(pip_linter_packages))
                + " "
                + "&& deactivate "
                + "&& cd ./../.. \\\n"
            )
            env_path_command += f":/venvs/{pip_linter}/bin"
        pipenv_install_command = pipenv_install_command[:-2]  # remove last \
        pipenv_install_command += (
            " \\\n    && "
            + r"find /venvs \( -type f \( -iname \*.pyc -o -iname \*.pyo \) -o -type d -iname __pycache__ \) -delete"
            + " \\\n    && "
            + "rm -rf /root/.cache\n"
            + env_path_command
        )
    else:
        pipenv_install_command = ""
    replace_in_file(
        dockerfile, "#PIPVENV__START", "#PIPVENV__END", pipenv_install_command
    )

    # Ruby gem packages
    gem_install_command = ""
    if len(gem_packages) > 0:
        gem_install_command = (
            "RUN echo 'gem: --no-document' >> ~/.gemrc && \\\n"
            + "    gem install \\\n          "
            + " \\\n          ".join(list(dict.fromkeys(gem_packages)))
        )
    replace_in_file(dockerfile, "#GEM__START", "#GEM__END", gem_install_command)
    flavor_env = f"ENV MEGALINTER_FLAVOR={flavor}"
    replace_in_file(dockerfile, "#FLAVOR__START", "#FLAVOR__END", flavor_env)
    replace_in_file(
        dockerfile,
        "#EXTRA_DOCKERFILE_LINES__START",
        "#EXTRA_DOCKERFILE_LINES__END",
        "\n".join(extra_lines),
    )


def match_flavor(item, flavor, flavor_info):
    is_strict = "strict" in flavor_info and flavor_info["strict"] is True
    if "disabled" in item and item["disabled"] is True:
        return
    if (
        "descriptor_flavors_exclude" in item
        and flavor in item["descriptor_flavors_exclude"]
    ):
        return False
    # Flavor all
    elif flavor == "all":
        return True
    # Formatter flavor
    elif flavor == "formatters":
        if "is_formatter" in item and item["is_formatter"] is True:
            return True
        elif (
            "descriptor_flavors" in item
            and flavor in item["descriptor_flavors"]
            and "linter_name" not in item
        ):
            return True
        else:
            return False
    # Other flavors
    elif "descriptor_flavors" in item:
        if flavor in item["descriptor_flavors"] or (
            "all_flavors" in item["descriptor_flavors"]
            and not flavor.endswith("_light")
            and "cupcake" not in flavor
            and not is_strict
        ):
            return True
    return False


# Automatically generate Dockerfile for standalone linters
def generate_linter_dockerfiles():
    # Remove all the contents of LINTERS_DIR beforehand so that the result is deterministic
    if DELETE_DOCKERFILES is True:
        shutil.rmtree(os.path.realpath(LINTERS_DIR))
    # Browse descriptors
    linters_md = "# Standalone linter docker images\n\n"
    linters_md += "| Linter key | Docker image | Size |\n"
    linters_md += "| :----------| :----------- | :--: |\n"
    descriptor_files = megalinter.linter_factory.list_descriptor_files()
    gha_workflow_yml = ["        linter:", "          ["]
    for descriptor_file in descriptor_files:
        descriptor_items = []
        with open(descriptor_file, "r", encoding="utf-8") as f:
            descriptor = yaml.safe_load(f)
        if "install" in descriptor:
            descriptor_items += [descriptor]
        descriptor_linters = megalinter.linter_factory.build_descriptor_linters(
            descriptor_file, {"request_id": "build"}
        )
        # Browse descriptor linters
        for linter in descriptor_linters:
            # Unique linter dockerfile
            linter_lower_name = linter.name.lower()
            dockerfile = f"{LINTERS_DIR}/{linter_lower_name}/Dockerfile"
            if not os.path.isdir(os.path.dirname(dockerfile)):
                os.makedirs(os.path.dirname(dockerfile), exist_ok=True)
            requires_docker = False
            if linter.cli_docker_image is not None:
                requires_docker = True
            descriptor_and_linter = descriptor_items + [vars(linter)]
            copyfile(f"{REPO_HOME}/Dockerfile", dockerfile)
            extra_lines = [
                f"ENV ENABLE_LINTERS={linter.name} \\",
                "    FLAVOR_SUGGESTIONS=false \\",
                f"    SINGLE_LINTER={linter.name} \\",
                "    PRINT_ALPACA=false \\",
                "    LOG_FILE=none \\",
                "    SARIF_REPORTER=true \\",
                "    TEXT_REPORTER=false \\",
                "    UPDATED_SOURCES_REPORTER=false \\",
                "    GITHUB_STATUS_REPORTER=false \\",
                "    GITHUB_COMMENT_REPORTER=false \\",
                "    EMAIL_REPORTER=false \\",
                "    API_REPORTER=false \\",
                "    FILEIO_REPORTER=false \\",
                "    CONFIG_REPORTER=false \\",
                "    SARIF_TO_HUMAN=false" "",
                # "EXPOSE 80",
                "RUN mkdir /root/docker_ssh && mkdir /usr/bin/megalinter-sh",
                "EXPOSE 22",
                "COPY entrypoint.sh /entrypoint.sh",
                "COPY sh /usr/bin/megalinter-sh",
                "COPY sh/megalinter_exec /usr/bin/megalinter_exec",
                "COPY sh/motd /etc/motd",
                'RUN find /usr/bin/megalinter-sh/ -type f -iname "*.sh" -exec chmod +x {} \\; && \\',
                "    chmod +x entrypoint.sh && \\",
                "    chmod +x /usr/bin/megalinter_exec && \\",
                "    echo \"alias megalinter='python -m megalinter.run'\" >> ~/.bashrc && source ~/.bashrc && \\",
                "    echo \"alias megalinter_exec='/usr/bin/megalinter_exec'\" >> ~/.bashrc && source ~/.bashrc",
                'RUN export STANDALONE_LINTER_VERSION="$(python -m megalinter.run --input /tmp --linterversion)" && \\',
                "    echo $STANDALONE_LINTER_VERSION",
                # "    echo $STANDALONE_LINTER_VERSION >> ~/.bashrc && source ~/.bashrc",
                'ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]',
            ]
            build_dockerfile(
                dockerfile, descriptor_and_linter, requires_docker, "none", extra_lines
            )
            gha_workflow_yml += [f'            "{linter_lower_name}",']
            docker_image = f"{ML_DOCKER_IMAGE}-only-{linter_lower_name}:{VERSION_V}"
            docker_image_badge = (
                f"![Docker Image Size (tag)]({BASE_SHIELD_IMAGE_LINK}/"
                f"{ML_DOCKER_IMAGE}-only-{linter_lower_name}/{VERSION_V})"
            )
            linters_md += (
                f"| {linter.name} | {docker_image} | {docker_image_badge}  |\n"
            )

    # Update github action workflow
    gha_workflow_yml += ["          ]"]
    replace_in_file(
        f"{REPO_HOME}/.github/workflows/deploy-DEV-linters.yml",
        "# linters-start",
        "# linters-end",
        "\n".join(gha_workflow_yml),
    )
    replace_in_file(
        f"{REPO_HOME}/.github/workflows/deploy-BETA-linters.yml",
        "# linters-start",
        "# linters-end",
        "\n".join(gha_workflow_yml),
    )
    replace_in_file(
        f"{REPO_HOME}/.github/workflows/deploy-RELEASE-linters.yml",
        "# linters-start",
        "# linters-end",
        "\n".join(gha_workflow_yml),
    )
    # Write MD file
    file = open(f"{REPO_HOME}/docs/standalone-linters.md", "w", encoding="utf-8")
    file.write(linters_md + "\n")
    file.close()


# Automatically generate a test class for each linter class
# This could be done dynamically at runtime, but having a physical class is easier for developers in IDEs
def generate_linter_test_classes():
    test_linters_root = f"{REPO_HOME}/megalinter/tests/test_megalinter/linters"

    if DELETE_TEST_CLASSES is True:
        # Remove all the contents of test_linters_root beforehand so that the result is deterministic
        shutil.rmtree(os.path.realpath(test_linters_root))
        os.makedirs(os.path.realpath(test_linters_root))

    linters = megalinter.linter_factory.list_all_linters(({"request_id": "build"}))
    for linter in linters:
        if linter.name is not None:
            linter_name = linter.name
        else:
            lang_lower = linter.descriptor_id.lower()
            linter_name = f"{lang_lower}_{linter.linter_name}"

        linter_name_lower = linter_name.lower().replace("-", "_")
        test_class_code = f"""# !/usr/bin/env python3
\"\"\"
Unit tests for {linter.descriptor_id} linter {linter.linter_name}
This class has been automatically {'@'}generated by .automation/build.py, please don't update it manually
\"\"\"

from unittest import TestCase

from megalinter.tests.test_megalinter.LinterTestRoot import LinterTestRoot


class {linter_name_lower}_test(TestCase, LinterTestRoot):
    descriptor_id = "{linter.descriptor_id}"
    linter_name = "{linter.linter_name}"
"""
        test_class_file_name = f"{test_linters_root}/{linter_name_lower}_test.py"
        if not os.path.isfile(test_class_file_name):
            file = open(
                test_class_file_name,
                "w",
                encoding="utf-8",
            )
            file.write(test_class_code)
            file.close()
            logging.info("Updated " + file.name)


def list_descriptors_for_build():
    global DESCRIPTORS_FOR_BUILD_CACHE
    if DESCRIPTORS_FOR_BUILD_CACHE is not None:
        return DESCRIPTORS_FOR_BUILD_CACHE
    descriptor_files = megalinter.linter_factory.list_descriptor_files()
    linters_by_type = {"language": [], "format": [], "tooling_format": [], "other": []}
    descriptors = []
    for descriptor_file in descriptor_files:
        descriptor = megalinter.linter_factory.build_descriptor_info(descriptor_file)
        descriptors += [descriptor]
        descriptor_linters = megalinter.linter_factory.build_descriptor_linters(
            descriptor_file, {"request_id": "build"}
        )
        linters_by_type[descriptor_linters[0].descriptor_type] += descriptor_linters
    DESCRIPTORS_FOR_BUILD_CACHE = descriptors, linters_by_type
    return descriptors, linters_by_type


# Automatically generate README linters table and a MD file for each linter
def generate_documentation():
    descriptors, linters_by_type = list_descriptors_for_build()
    # Build descriptors documentation
    for descriptor in descriptors:
        generate_descriptor_documentation(descriptor)
    # Build README linters table and linters documentation
    linters_tables_md = []
    process_type(linters_by_type, "language", "Languages", linters_tables_md)
    process_type(linters_by_type, "format", "Formats", linters_tables_md)
    process_type(
        linters_by_type, "tooling_format", "Tooling formats", linters_tables_md
    )
    process_type(linters_by_type, "other", "Other", linters_tables_md)
    linters_tables_md_str = "\n".join(linters_tables_md)
    logging.info("Generated Linters table for README:\n" + linters_tables_md_str)
    replace_in_file(
        f"{REPO_HOME}/README.md",
        "<!-- linters-table-start -->",
        "<!-- linters-table-end -->",
        linters_tables_md_str,
    )
    replace_in_file(
        f"{REPO_HOME}/mega-linter-runner/README.md",
        "<!-- linters-table-start -->",
        "<!-- linters-table-end -->",
        linters_tables_md_str,
    )
    # Update welcome phrase
    welcome_phrase = (
        "MegaLinter is an **Open-Source** tool for **CI/CD workflows** "
        + "that analyzes the **consistency of your "
        + "code**, **IAC**, **configuration**, and **scripts** in your repository "
        + "sources, to **ensure all your projects "
        + "sources are clean and formatted** whatever IDE/toolbox is used by "
        + "their developers, powered by [**OX Security**](https://www.ox.security/?ref=megalinter).\n\n"
        + f"Supporting [**{len(linters_by_type['language'])}** languages]"
        + "(#languages), "
        + f"[**{len(linters_by_type['format'])}** formats](#formats), "
        + f"[**{len(linters_by_type['tooling_format'])}** tooling formats](#tooling-formats) "
        + "and **ready to use out of the box**, as a GitHub action or any CI system, "
        + "**highly configurable** and **free for all uses**.\n\n"
        + "MegaLinter has **native integrations** with many of the major CI/CD tools of the market.\n\n"
        + "[![GitHub](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/github.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/reporters/GitHubCommentReporter.md)\n"  # noqa: E501
        + "[![Gitlab](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/gitlab.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/reporters/GitlabCommentReporter.md)\n"  # noqa: E501
        + "[![Azure](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/azure.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/reporters/AzureCommentReporter.md)\n"  # noqa: E501
        + "[![Bitbucket](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/bitbucket.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/reporters/BitbucketCommentReporter.md)\n"  # noqa: E501
        + "[![Jenkins](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/jenkins.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/install-jenkins.md)\n"  # noqa: E501
        + "[![Drone](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/drone.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/install-drone.md)\n"  # noqa: E501
        + "[![Concourse](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/concourse.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/install-concourse.md)\n"  # noqa: E501
        + "[![Docker](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/docker.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/install-docker.md)\n"  # noqa: E501
        + "[![SARIF](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/sarif.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/reporters/SarifReporter.md)\n"  # noqa: E501
        + "[![Grafana](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/icons/integrations/grafana.png?raw=true>)](https://github.com/oxsecurity/megalinter/tree/main/docs/reporters/ApiReporter.md)\n\n"  # noqa: E501
    )
    # Update README.md file
    replace_in_file(
        f"{REPO_HOME}/README.md",
        "<!-- welcome-phrase-start -->",
        "<!-- welcome-phrase-end -->",
        welcome_phrase,
    )
    # Update mkdocs.yml file
    replace_in_file(
        f"{REPO_HOME}/mkdocs.yml",
        "# site_description-start",
        "# site_description-end",
        "site_description: " + md_to_text(welcome_phrase.replace("\n", "")),
    )
    # Build & Update flavors table
    flavors_table_md = build_flavors_md_table()
    flavors_table_md_str = "\n".join(flavors_table_md)
    logging.info("Generated Flavors table for README:\n" + flavors_table_md_str)
    replace_in_file(
        f"{REPO_HOME}/README.md",
        "<!-- flavors-table-start -->",
        "<!-- flavors-table-end -->",
        flavors_table_md_str,
    )

    # Build & Update flavors table
    plugins_table_md = build_plugins_md_table()
    plugins_table_md_str = "\n".join(plugins_table_md)
    logging.info("Generated Plugins table for README:\n" + plugins_table_md_str)
    replace_in_file(
        f"{REPO_HOME}/README.md",
        "<!-- plugins-table-start -->",
        "<!-- plugins-table-end -->",
        plugins_table_md_str,
    )

    # Generate flavors individual documentations
    flavors = megalinter.flavor_factory.get_all_flavors()
    for flavor, flavor_info in flavors.items():
        generate_flavor_documentation(flavor, flavor_info, linters_tables_md)
    # Automate generation of /docs items generated from README sections
    finalize_doc_build()


# Generate a MD page for a descriptor (language, format, tooling_format)
def generate_descriptor_documentation(descriptor):
    descriptor_file = f"{descriptor.get('descriptor_id').lower()}.yml"
    descriptor_url = f"{URL_ROOT}/megalinter/descriptors/{descriptor_file}"
    linter_names = [
        linter.get("linter_name") for linter in descriptor.get("linters", [])
    ]
    is_are = "is" if len(linter_names) == 1 else "are"
    descriptor_md = [
        "---",
        f"title: {descriptor.get('descriptor_id')} linters in MegaLinter",
        f"description: {', '.join(linter_names)} {is_are} available to analyze "
        f"{descriptor.get('descriptor_id')} files in MegaLinter",
        "---",
        "<!-- markdownlint-disable MD003 MD020 MD033 MD041 -->",
        f"<!-- {'@'}generated by .automation/build.py, please don't update manually -->",
        f"<!-- Instead, update descriptor file at {descriptor_url} -->",
    ]
    # Title
    descriptor_md += [
        f"# {descriptor.get('descriptor_label', descriptor.get('descriptor_id'))}",
        "",
    ]
    # List of linters
    lang_lower = descriptor.get("descriptor_id").lower()
    descriptor_md += [
        "## Linters",
        "",
        "| Linter | Additional |",
        "| ------ | ---------- |",
    ]
    for linter in descriptor.get("linters", []):
        linter_name_lower = linter.get("linter_name").lower().replace("-", "_")
        linter_doc_url = f"{lang_lower}_{linter_name_lower}.md"
        badges = get_badges(linter)
        md_extra = " ".join(badges)
        linter_key = linter.get("name", "")
        if linter_key == "":
            linter_key = (
                descriptor.get("descriptor_id")
                + "_"
                + linter.get("linter_name").upper().replace("-", "_")
            )
        descriptor_md += [
            f"| [**{linter.get('linter_name')}**]({doc_url(linter_doc_url)})<br/>"
            f"[_{linter_key}_]({doc_url(linter_doc_url)}) "
            f"| {md_extra} |"
        ]

    # Criteria used by the descriptor to identify files to lint
    descriptor_md += ["", "## Linted files", ""]
    if len(descriptor.get("active_only_if_file_found", [])) > 0:
        descriptor_md += [
            f"- Activated only if at least one of these files is found:"
            f" `{', '.join(descriptor.get('active_only_if_file_found'))}`"
        ]
    if len(descriptor.get("file_extensions", [])) > 0:
        descriptor_md += ["- File extensions:"]
        for file_extension in descriptor.get("file_extensions"):
            descriptor_md += [f"  - `{file_extension}`"]
        descriptor_md += [""]
    if len(descriptor.get("file_names_regex", [])) > 0:
        descriptor_md += ["- File names:"]
        for file_name in descriptor.get("file_names_regex"):
            descriptor_md += [f"  - `{file_name}`"]
        descriptor_md += [""]
    if len(descriptor.get("file_contains_regex", [])) > 0:
        descriptor_md += ["- Detected file content:"]
        for file_contains_expr in descriptor.get("file_contains_regex"):
            descriptor_md += [f"  - `{file_contains_expr}`"]
        descriptor_md += [""]
    # Mega-linter variables
    descriptor_md += [
        "## Configuration in MegaLinter",
        "",
        "| Variable | Description | Default value |",
        "| ----------------- | -------------- | -------------- |",
    ]
    descriptor_md += [
        f"| {descriptor.get('descriptor_id')}_PRE_COMMANDS | List of bash commands to run before the linters | None |",
        f"| {descriptor.get('descriptor_id')}_POST_COMMANDS | List of bash commands to run after the linters | None |",
        f"| {descriptor.get('descriptor_id')}_FILTER_REGEX_INCLUDE | Custom regex including filter |  |",
        f"| {descriptor.get('descriptor_id')}_FILTER_REGEX_EXCLUDE | Custom regex excluding filter |  |",
        "",
    ]
    add_in_config_schema_file(
        [
            [
                f"{descriptor.get('descriptor_id')}_PRE_COMMANDS",
                {
                    "$id": f"#/properties/{descriptor.get('descriptor_id')}_PRE_COMMANDS",
                    "type": "array",
                    "title": f"Pre commands for {descriptor.get('descriptor_id')} descriptor",
                    "examples": [
                        [
                            {
                                "command": "composer install",
                                "continue_if_failed": False,
                                "cwd": "workspace",
                            }
                        ]
                    ],
                    "items": {"$ref": "#/definitions/command_info"},
                },
            ],
            [
                f"{descriptor.get('descriptor_id')}_POST_COMMANDS",
                {
                    "$id": f"#/properties/{descriptor.get('descriptor_id')}_POST_COMMANDS",
                    "type": "array",
                    "title": f"Post commands for {descriptor.get('descriptor_id')} descriptor",
                    "examples": [
                        [
                            {
                                "command": "npm run test",
                                "continue_if_failed": False,
                                "cwd": "workspace",
                            }
                        ]
                    ],
                    "items": {"$ref": "#/definitions/command_info"},
                },
            ],
            [
                f"{descriptor.get('descriptor_id')}_FILTER_REGEX_INCLUDE",
                {
                    "$id": f"#/properties/{descriptor.get('descriptor_id')}_FILTER_REGEX_INCLUDE",
                    "type": "string",
                    "title": f"Including regex filter for {descriptor.get('descriptor_id')} descriptor",
                },
            ],
            [
                f"{descriptor.get('descriptor_id')}_FILTER_REGEX_EXCLUDE",
                {
                    "$id": f"#/properties/{descriptor.get('descriptor_id')}_FILTER_REGEX_EXCLUDE",
                    "type": "string",
                    "title": f"Excluding regex filter for {descriptor.get('descriptor_id')} descriptor",
                },
            ],
        ]
    )
    # Add install info
    if descriptor.get("install", None) is not None:
        descriptor_md += ["", "## Behind the scenes"]
        descriptor_md += ["", "### Installation", ""]
        descriptor_md += get_install_md(descriptor)
    # Write MD file
    file = open(f"{REPO_HOME}/docs/descriptors/{lang_lower}.md", "w", encoding="utf-8")
    file.write("\n".join(descriptor_md) + "\n")
    file.close()
    logging.info("Updated " + file.name)


def generate_flavor_documentation(flavor_id, flavor, linters_tables_md):
    flavor_github_action = f"{ML_REPO}/flavors/{flavor_id}@{VERSION_V}"
    flavor_docker_image = f"{ML_DOCKER_IMAGE}-{flavor_id}:{VERSION_V}"
    docker_image_badge = (
        f"![Docker Image Size (tag)]({BASE_SHIELD_IMAGE_LINK}/"
        f"{ML_DOCKER_IMAGE}-{flavor_id}/{VERSION_V})"
    )
    docker_pulls_badge = (
        f"![Docker Pulls]({BASE_SHIELD_COUNT_LINK}/" f"{ML_DOCKER_IMAGE}-{flavor_id})"
    )
    flavor_doc_md = [
        "---",
        f"title: {flavor_id} flavor in MegaLinter",
        f"description: {flavor_id} flavor is an optimized MegaLinter with "
        f"only linters related to {flavor_id} projects",
        "---",
        f"# {flavor_id} MegaLinter Flavor",
        "",
        docker_image_badge,
        docker_pulls_badge,
        "",
        "## Description",
        "",
        flavor["label"],
        "",
        "## Usage",
        "",
        f"- [GitHub Action]({MKDOCS_URL_ROOT}/installation/#github-action): **{flavor_github_action}**",
        f"- Docker image: **{flavor_docker_image}**",
        f"- [mega-linter-runner]({MKDOCS_URL_ROOT}/mega-linter-runner/): `mega-linter-runner --flavor {flavor_id}`",
        "",
        "## Embedded linters",
        "",
    ]
    filtered_table_md = []
    for line in linters_tables_md:
        if "<!-- linter-icon -->" in line:
            match = False
            for linter_name in flavor["linters"]:
                if f"{linter_name}" in line:
                    match = True
                    break
            if match is False:
                continue
        line = (
            line.replace(DOCS_URL_DESCRIPTORS_ROOT, MKDOCS_URL_ROOT + "/descriptors")
            .replace(".md#readme", "/")
            .replace(".md", "/")
        )
        filtered_table_md += [line]
    flavor_doc_md += filtered_table_md
    # Write MD file
    flavor_doc_file = f"{REPO_HOME}/docs/flavors/{flavor_id}.md"
    file = open(flavor_doc_file, "w", encoding="utf-8")
    file.write("\n".join(flavor_doc_md) + "\n")
    file.close()
    logging.info("Updated " + flavor_doc_file)


def dump_as_json(value: Any, empty_value: str) -> str:
    if not value:
        return empty_value
    # Convert any value to string with JSON
    # Don't indent since markdown table supports single line only
    result = json.dumps(value, indent=None, sort_keys=True)
    return f"`{result}`"


# Build a MD table for a type of linter (language, format, tooling_format), and a MD file for each linter
def process_type(linters_by_type, type1, type_label, linters_tables_md):
    col_header = (
        "Language"
        if type1 == "language"
        else (
            "Format"
            if type1 == "format"
            else (
                "Tooling format"
                if type1 == "tooling_format"
                else "Code quality checker"
            )
        )
    )
    linters_tables_md += [
        f"### {type_label}",
        "",
        f"| <!-- --> | {col_header} | Linter | Additional  |",
        "| :---: | ----------------- | -------------- | :-----:  |",
    ]
    descriptor_linters = linters_by_type[type1]
    for linter in descriptor_linters:
        lang_lower, linter_name_lower, descriptor_label = get_linter_base_info(linter)
        if os.path.isfile(REPO_ICONS + "/" + linter.descriptor_id.lower() + ".ico"):
            icon_html = icon(
                f"{DOCS_URL_RAW_ROOT}/assets/icons/{linter.descriptor_id.lower()}.ico",
                "",
                "",
                descriptor_label,
                32,
            )
        elif os.path.isfile(REPO_ICONS + "/default.ico"):
            icon_html = icon(
                f"{DOCS_URL_RAW_ROOT}/assets/icons/default.ico",
                "",
                "",
                descriptor_label,
                32,
            )
        else:
            icon_html = "<!-- -->"
        descriptor_url = doc_url(f"{DOCS_URL_DESCRIPTORS_ROOT}/{lang_lower}.md")
        descriptor_id_cell = f"[{descriptor_label}]({descriptor_url})"
        # Build extra badges
        badges = get_badges(linter)
        md_extra = " ".join(badges)
        # Build doc URL
        linter_doc_url = (
            f"{DOCS_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}.md"
        )
        # Build md table line
        linters_tables_md += [
            f"| {icon_html} <!-- linter-icon --> | "
            f"{descriptor_id_cell} | "
            f"[**{linter.linter_name}**]({doc_url(linter_doc_url)})<br/>"
            f"[_{linter.name}_]({doc_url(linter_doc_url)}) | "
            f"{md_extra} |"
        ]
        individual_badges = get_badges(
            linter,
            show_last_release=True,
            show_last_commit=True,
            show_commits_activity=True,
            show_contributors=True,
            show_downgraded_version=True,
        )
        md_individual_extra = " ".join(individual_badges)
        # Build individual linter doc
        linter_doc_md = [
            "---",
            f"title: {linter.linter_name} configuration in MegaLinter",
            f"description: How to use {linter.linter_name} (configure, "
            "ignore files, ignore errors, help & version documentations)"
            f" to analyze {linter.descriptor_id} files",
            "---",
            "<!-- markdownlint-disable MD033 MD041 -->",
            f"<!-- {'@'}generated by .automation/build.py, please don't update manually -->",
        ]
        # Header image as title
        if (
            hasattr(linter, "linter_banner_image_url")
            and linter.linter_banner_image_url is not None
        ):
            linter_doc_md += [
                banner_link(
                    linter.linter_banner_image_url,
                    linter.linter_name,
                    doc_url(linter.linter_url),
                    "Visit linter Web Site",
                    "center",
                    150,
                ),
                "\n" + md_individual_extra,
            ]
        # Text + image as title
        elif (
            hasattr(linter, "linter_image_url") and linter.linter_image_url is not None
        ):
            linter_doc_md += [
                "# "
                + logo_link(
                    linter.linter_image_url,
                    linter.linter_name,
                    linter.linter_url,
                    "Visit linter Web Site",
                    100,
                )
                + linter.linter_name
                + "\n"
                + md_individual_extra
            ]
        # Text as title
        elif md_individual_extra == "":
            linter_doc_md += [f"# {linter.linter_name}"]
        else:
            linter_doc_md += [f"# {linter.linter_name}\n{md_individual_extra}"]

        # Indicate that a linter is deprecated in this version
        title_prefix = ""
        if hasattr(linter, "deprecated") and linter.deprecated is True:
            title_prefix = "(deprecated) "
            linter_doc_md += [""]
            linter_doc_md += ["> This linter has been deprecated.", ">"]

            if (
                hasattr(linter, "deprecated_description")
                and linter.deprecated_description
            ):
                linter_doc_md += [
                    "> ".join(
                        ("> " + linter.deprecated_description.lstrip()).splitlines(True)
                    ),
                    ">",
                ]

            linter_doc_md += [
                f"> You should disable {linter.linter_name} by adding it in DISABLE_LINTERS property.",
                ">",
                "> It will be maintained at least until the next major release.",
            ]

        # Indicate that a linter is disabled in this version
        if hasattr(linter, "disabled") and linter.disabled is True:
            linter_doc_md += [""]
            linter_doc_md += ["_This linter has been disabled in this version_"]
            if hasattr(linter, "disabled_reason") and linter.disabled_reason is True:
                linter_doc_md += [""]
                linter_doc_md += [f"_Disabled reason: {linter.disabled_reason}_"]

        # Linter text , if defined in YML descriptor
        if hasattr(linter, "linter_text") and linter.linter_text:
            linter_doc_md += [""]
            linter_doc_md += linter.linter_text.splitlines()

        # Linter-specific configuration
        linter_doc_md += ["", f"## {linter.linter_name} documentation", ""]
        # Linter URL & version
        with open(VERSIONS_FILE, "r", encoding="utf-8") as json_file:
            linter_versions = json.load(json_file)
            if (
                linter.linter_name in linter_versions
                and linter_versions[linter.linter_name] != "0.0.0"
            ):
                linter_doc_md += [
                    f"- Version in MegaLinter: **{linter_versions[linter.linter_name]}**"
                ]
        linter_doc_md += [
            f"- Visit [Official Web Site]({doc_url(linter.linter_url)}){{target=_blank}}",
        ]
        # Docker image doc
        if linter.cli_docker_image is not None:
            linter_doc_md += [
                f"- Docker image: [{linter.cli_docker_image}:{linter.cli_docker_image_version}]"
                f"(https://hub.docker.com/r/{linter.cli_docker_image})"
                "{target=_blank}",
                f"  - arguments: `{' '.join(linter.cli_docker_args)}`",
            ]
        # Rules configuration URL
        if (
            hasattr(linter, "linter_rules_configuration_url")
            and linter.linter_rules_configuration_url is not None
        ):
            linter_doc_md += [
                f"- See [How to configure {linter.linter_name} rules]({linter.linter_rules_configuration_url})"
                "{target=_blank}"
            ]
        # Default rules
        if linter.config_file_name is not None:
            config_file = f"TEMPLATES{os.path.sep}{linter.config_file_name}"
            if os.path.isfile(f"{REPO_HOME}{os.path.sep}{config_file}"):
                linter_doc_md += [
                    f"  - If custom `{linter.config_file_name}` config file isn't found, "
                    f"[{linter.config_file_name}]({TEMPLATES_URL_ROOT}/{linter.config_file_name}){{target=_blank}}"
                    " will be used"
                ]
        # Inline disable rules
        if (
            hasattr(linter, "linter_rules_inline_disable_url")
            and linter.linter_rules_inline_disable_url is not None
        ):
            linter_doc_md += [
                f"- See [How to disable {linter.linter_name} rules in files]({linter.linter_rules_inline_disable_url})"
                "{target=_blank}"
            ]
        # Ignore configuration
        if (
            hasattr(linter, "linter_rules_ignore_config_url")
            and linter.linter_rules_ignore_config_url is not None
        ):
            linter_doc_md += [
                f"- See [How to ignore files and directories with {linter.linter_name}]"
                f"({linter.linter_rules_ignore_config_url})"
                "{target=_blank}"
            ]
            if linter.ignore_file_name is not None:
                ignore_file = f"TEMPLATES{os.path.sep}{linter.ignore_file_name}"
                if os.path.isfile(f"{REPO_HOME}{os.path.sep}{ignore_file}"):
                    linter_doc_md += [
                        f"  - If custom `{linter.ignore_file_name}` ignore file is not found, "
                        f"[{linter.ignore_file_name}]({TEMPLATES_URL_ROOT}/{linter.ignore_file_name}){{target=_blank}}"
                        " will be used"
                    ]
                else:
                    linter_doc_md += [
                        f"  - You can define a `{linter.ignore_file_name}` file to ignore files and folders"
                    ]
        # Rules configuration URL
        if hasattr(linter, "linter_rules_url") and linter.linter_rules_url is not None:
            linter_doc_md += [
                f"- See [Index of problems detected by {linter.linter_name}]({linter.linter_rules_url})"
                "{target=_blank}"
            ]
        linter_doc_md += [""]
        # Github repo svg preview
        repo = get_repo(linter)
        if repo is not None and repo.github is True:
            # pylint: disable=no-member
            linter_doc_md += [
                f"[![{repo.repo} - GitHub](https://gh-card.dev/repos/{repo.owner}/{repo.repo}.svg?fullname=)]"
                f"(https://github.com/{repo.owner}/{repo.repo}){{target=_blank}}",
                "",
                # pylint: enable=no-member
            ]
        else:
            logging.warning(
                f"Unable to find github repository for {linter.linter_name}"
            )
        # Mega-linter variables
        activation_url = MKDOCS_URL_ROOT + "/configuration/#activation-and-deactivation"
        apply_fixes_url = MKDOCS_URL_ROOT + "/configuration/#apply-fixes"
        linter_doc_md += [
            "## Configuration in MegaLinter",
            "",
            f"- Enable {linter.linter_name} by adding `{linter.name}` in [ENABLE_LINTERS variable]({activation_url})",
            f"- Disable {linter.linter_name} by adding `{linter.name}` in [DISABLE_LINTERS variable]({activation_url})",
        ]
        if linter.cli_lint_fix_arg_name is not None:
            linter_doc_md += [
                "",
                f"- Enable **autofixes** by adding `{linter.name}` in [APPLY_FIXES variable]({apply_fixes_url})",
            ]
        linter_doc_md += [
            "",
            "| Variable | Description | Default value |",
            "| ----------------- | -------------- | -------------- |",
        ]
        if hasattr(linter, "activation_rules"):
            for rule in linter.activation_rules:
                linter_doc_md += [
                    f"| {rule['variable']} | For {linter.linter_name} to be active, {rule['variable']} must be "
                    f"`{rule['expected_value']}` | `{rule['default_value']}` |"
                ]
        if hasattr(linter, "variables"):
            for variable in linter.variables:
                linter_doc_md += [
                    f"| {variable['name']} | {variable['description']} | `{variable['default_value']}` |"
                ]
        if linter.cli_docker_image is not None:
            linter_doc_md += [
                f"| {linter.name}_DOCKER_IMAGE_VERSION | Docker image version | `{linter.cli_docker_image_version}` |"
            ]
        linter_doc_md += [
            f"| {linter.name}_ARGUMENTS | User custom arguments to add in linter CLI call<br/>"
            f'Ex: `-s --foo "bar"` |  |'
        ]
        linter_doc_md += [
            f"| {linter.name}_COMMAND_REMOVE_ARGUMENTS | User custom arguments to remove "
            "from command line before calling the linter<br/>"
            f'Ex: `-s --foo "bar"` |  |'
        ]
        # Files can be filtered only in cli_lint_mode is file or list_of_files
        if linter.cli_lint_mode != "project":
            linter_doc_md += [
                f"| {linter.name}_FILTER_REGEX_INCLUDE | Custom regex including filter<br/>"
                f"Ex: `(src\\|lib)` | Include every file |",
                f"| {linter.name}_FILTER_REGEX_EXCLUDE | Custom regex excluding filter<br/>"
                f"Ex: `(test\\|examples)` | Exclude no file |",
            ]
            add_in_config_schema_file(
                [
                    [
                        f"{linter.name}_FILTER_REGEX_INCLUDE",
                        {
                            "$id": f"#/properties/{linter.name}_FILTER_REGEX_INCLUDE",
                            "type": "string",
                            "title": f"{title_prefix}{linter.name}: Including Regex",
                        },
                    ],
                    [
                        f"{linter.name}_FILTER_REGEX_EXCLUDE",
                        {
                            "$id": f"#/properties/{linter.name}_FILTER_REGEX_EXCLUDE",
                            "type": "string",
                            "title": f"{title_prefix}{linter.name}: Excluding Regex",
                        },
                    ],
                ]
            )
        else:
            remove_in_config_schema_file(
                [
                    f"{linter.name}_FILTER_REGEX_INCLUDE",
                    f"{linter.name}_FILTER_REGEX_EXCLUDE",
                ]
            )
        # cli_lint_mode can be overridden by user config
        # if the descriptor cli_lint_mode == "project", it's at the user's own risk :)
        cli_lint_mode_doc_md = (
            f"| {linter.name}_CLI_LINT_MODE | Override default CLI lint mode<br/>"
        )
        if linter.cli_lint_mode == "project":
            cli_lint_mode_doc_md += (
                "⚠️ As default value is **project**, overriding might not work<br/>"
            )
        cli_lint_mode_doc_md += "- `file`: Calls the linter for each file<br/>"
        if linter.cli_lint_mode == "file":
            enum = ["file", "project"]
        else:
            enum = ["file", "list_of_files", "project"]
            cli_lint_mode_doc_md += "- `list_of_files`: Call the linter with the list of files as argument<br/>"
        cli_lint_mode_doc_md += (
            "- `project`: Call the linter from the root of the project"
        )
        cli_lint_mode_doc_md += f" | `{linter.cli_lint_mode}` |"
        linter_doc_md += [cli_lint_mode_doc_md]
        add_in_config_schema_file(
            [
                [
                    f"{linter.name}_CLI_LINT_MODE",
                    {
                        "$id": f"#/properties/{linter.name}_CLI_LINT_MODE",
                        "type": "string",
                        "title": f"{title_prefix}{linter.name}: Override default cli lint mode",
                        "default": linter.cli_lint_mode,
                        "enum": enum,
                    },
                ]
            ]
        )

        # File extensions & file names override if not "lint_all_files"
        if linter.lint_all_files is False:
            linter_doc_md += [
                # FILE_EXTENSIONS
                f"| {linter.name}_FILE_EXTENSIONS | Allowed file extensions."
                f' `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>'
                f"Ex: `[\".py\", \"\"]` | {dump_as_json(linter.file_extensions, 'Exclude every file')} |",
                # FILE_NAMES_REGEX
                f"| {linter.name}_FILE_NAMES_REGEX | File name regex filters. Regular expression list for"
                f" filtering files by their base names using regex full match. Empty list includes all files<br/>"
                f'Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]` '
                f"| {dump_as_json(linter.file_names_regex, 'Include every file')} |",
            ]
            add_in_config_schema_file(
                [
                    [
                        f"{linter.name}_FILE_EXTENSIONS",
                        {
                            "$id": f"#/properties/{linter.name}_FILE_EXTENSIONS",
                            "type": "array",
                            "title": (
                                title_prefix
                                + f"{linter.name}: Override descriptor/linter matching files extensions"
                            ),
                            "examples:": [".py", ".myext"],
                            "items": {"type": "string"},
                        },
                    ],
                    [
                        f"{linter.name}_FILE_NAMES_REGEX",
                        {
                            "$id": f"#/properties/{linter.name}_FILE_NAMES_REGEX",
                            "type": "array",
                            "title": (
                                title_prefix
                                + f"{linter.name}: Override descriptor/linter matching file name regex"
                            ),
                            "examples": ["Dockerfile(-.+)?", "Jenkinsfile"],
                            "items": {"type": "string"},
                        },
                    ],
                ]
            )
        else:
            remove_in_config_schema_file(
                [f"{linter.name}_FILE_EXTENSIONS", f"{linter.name}_FILE_NAMES_REGEX"]
            )
        # Pre/post commands & unsecured variables
        linter_doc_md += [
            f"| {linter.name}_PRE_COMMANDS | List of bash commands to run before the linter"
            f"| {dump_as_json(linter.pre_commands, 'None')} |",
            f"| {linter.name}_POST_COMMANDS | List of bash commands to run after the linter"
            f"| {dump_as_json(linter.post_commands, 'None')} |",
            f"| {linter.name}_UNSECURED_ENV_VARIABLES  | List of env variables explicitly "
            + f"not filtered before calling {linter.name} and its pre/post commands"
            f"| {dump_as_json(linter.post_commands, 'None')} |",
        ]
        add_in_config_schema_file(
            [
                [
                    f"{linter.name}_COMMAND_REMOVE_ARGUMENTS",
                    {
                        "$id": f"#/properties/{linter.name}_COMMAND_REMOVE_ARGUMENTS",
                        "type": ["array", "string"],
                        "title": f"{title_prefix}{linter.name}: Custom remove arguments",
                        "description": f"{linter.name}: User custom arguments to remove before calling linter",
                        "examples:": ["--foo", "bar"],
                        "items": {"type": "string"},
                    },
                ],
                [
                    f"{linter.name}_ARGUMENTS",
                    {
                        "$id": f"#/properties/{linter.name}_ARGUMENTS",
                        "type": ["array", "string"],
                        "title": f"{title_prefix}{linter.name}: Custom arguments",
                        "description": f"{linter.name}: User custom arguments to add in linter CLI call",
                        "examples:": ["--foo", "bar"],
                        "items": {"type": "string"},
                    },
                ],
                [
                    f"{linter.name}_PRE_COMMANDS",
                    {
                        "$id": f"#/properties/{linter.name}_PRE_COMMANDS",
                        "type": "array",
                        "title": (
                            title_prefix
                            + f"{linter.name}: Define or override a list of bash commands to run before the linter"
                        ),
                        "examples": [
                            [
                                {
                                    "command": "tflint --init",
                                    "continue_if_failed": False,
                                    "cwd": "workspace",
                                }
                            ]
                        ],
                        "items": {"$ref": "#/definitions/command_info"},
                    },
                ],
                [
                    f"{linter.name}_POST_COMMANDS",
                    {
                        "$id": f"#/properties/{linter.name}_POST_COMMANDS",
                        "type": "array",
                        "title": (
                            title_prefix
                            + f"{linter.name}: Define or override a list of bash commands to run after the linter"
                        ),
                        "examples": [
                            [
                                {
                                    "command": "npm run test",
                                    "continue_if_failed": False,
                                    "cwd": "workspace",
                                }
                            ]
                        ],
                        "items": {"$ref": "#/definitions/command_info"},
                    },
                ],
                [
                    f"{linter.name}_DISABLE_ERRORS",
                    {
                        "$id": f"#/properties/{linter.name}_DISABLE_ERRORS",
                        "type": "boolean",
                        "default": False,
                        "title": (
                            title_prefix
                            + f"{linter.name}: Linter doesn't make MegaLinter fail even if errors are found"
                        ),
                    },
                ],
                [
                    f"{linter.name}_DISABLE_ERRORS_IF_LESS_THAN",
                    {
                        "$id": f"#/properties/{linter.name}_DISABLE_ERRORS_IF_LESS_THAN",
                        "type": "number",
                        "default": 0,
                        "title": f"{title_prefix}{linter.name}: Maximum number of errors allowed",
                    },
                ],
                [
                    f"{linter.name}_CLI_EXECUTABLE",
                    {
                        "$id": f"#/properties/{linter.name}_CLI_EXECUTABLE",
                        "type": "array",
                        "default": [linter.cli_executable],
                        "title": f"{title_prefix}{linter.name}: CLI Executable",
                        "items": {"type": "string"},
                    },
                ],
                [
                    f"{linter.name}_UNSECURED_ENV_VARIABLES",
                    {
                        "$id": f"#/properties/{linter.name}_UNSECURED_ENV_VARIABLES",
                        "type": "array",
                        "default": [],
                        "description": "List of env variables explicitly "
                        + f"not filtered before calling {linter.name} and its pre/post commands",
                        "title": f"{title_prefix}{linter.name}: Unsecured env variables",
                        "items": {"type": "string"},
                    },
                ],
            ]
        )

        if linter.config_file_name is not None:
            linter_doc_md += [
                f"| {linter.name}_CONFIG_FILE | {linter.linter_name} configuration file name</br>"
                f"Use `LINTER_DEFAULT` to let the linter find it | "
                f"`{linter.config_file_name}` |",
                f"| {linter.name}_RULES_PATH | Path where to find linter configuration file | "
                "Workspace folder, then MegaLinter default rules |",
            ]
            add_in_config_schema_file(
                [
                    [
                        f"{linter.name}_CONFIG_FILE",
                        {
                            "$id": f"#/properties/{linter.name}_CONFIG_FILE",
                            "type": "string",
                            "title": f"{title_prefix}{linter.name}: Custom config file name",
                            "default": linter.config_file_name,
                            "description": f"{linter.name}: User custom config file name if different from default",
                        },
                    ],
                    [
                        f"{linter.name}_RULES_PATH",
                        {
                            "$id": f"#/properties/{linter.name}_RULES_PATH",
                            "type": "string",
                            "title": f"{title_prefix}{linter.name}: Custom config file path",
                            "description": f"{linter.name}: Path where to find linter configuration file",
                        },
                    ],
                ]
            )
        default_disable_errors = "true" if linter.is_formatter is True else "false"
        linter_doc_md += [
            f"| {linter.name}_DISABLE_ERRORS | Run linter but consider errors as warnings |"
            f" `{default_disable_errors}` |",
            f"| {linter.name}_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed |"
            f" `0` |",
            f"| {linter.name}_CLI_EXECUTABLE | Override CLI executable |"
            f" `{str(linter.cli_executable)}` |",
        ]

        if linter.files_sub_directory is not None:
            linter_doc_md += [
                f"| {linter.descriptor_id}_DIRECTORY | Directory containing {linter.descriptor_id} files"
                " (use `any` to always activate the linter)"
                f"| `{linter.files_sub_directory}` |"
            ]
            add_in_config_schema_file(
                [
                    [
                        f"{linter.name}_DIRECTORY",
                        {
                            "$id": f"#/properties/{linter.name}_DIRECTORY",
                            "type": "string",
                            "description": (
                                'Directory that must be found to activate linter. Use value "any" to always activate'
                            ),
                            "title": f"{title_prefix}{linter.name}: Directory containing {linter.descriptor_id} files",
                            "default": linter.files_sub_directory,
                        },
                    ],
                ]
            )
        # IDE Integration
        if hasattr(linter, "ide"):
            linter_doc_md += ["", "## IDE Integration", ""]
            linter_doc_md += [
                f"Use {linter.linter_name} in your favorite IDE to catch errors before MegaLinter !",
                "",
            ]
            linter_doc_md += [
                "| <!-- --> | IDE | Extension Name | Install |",
                "| :--: | ----------------- | -------------- | :------: |",
            ]
            for ide, ide_extensions in linter.ide.items():
                for ide_extension in ide_extensions:
                    ide_icon = ide
                    if not os.path.isfile(f"{REPO_ICONS}/{ide}.ico"):
                        ide_icon = "default"
                    icon_html = icon(
                        f"{DOCS_URL_RAW_ROOT}/assets/icons/{ide_icon}.ico",
                        "",
                        "",
                        ide_extension["name"],
                        32,
                    )
                    install_link = md_ide_install_link(ide, ide_extension)
                    linter_doc_md += [
                        f"| {icon_html} | {md_ide(ide)} | [{ide_extension['name']}]({ide_extension['url']}) | "
                        f"{install_link} |"
                    ]
        # Mega-linter flavors
        linter_doc_md += [
            "",
            "## MegaLinter Flavors",
            "",
            "This linter is available in the following flavors",
            "",
        ]
        linter_doc_md += build_flavors_md_table(
            filter_linter_name=linter.name, replace_link=True
        )

        # Behind the scenes section
        linter_doc_md += ["", "## Behind the scenes", ""]
        # Criteria used by the linter to identify files to lint
        linter_doc_md += ["### How are identified applicable files", ""]
        if linter.files_sub_directory is not None:
            linter_doc_md += [
                f"- Activated only if sub-directory `{linter.files_sub_directory}` is found."
                f" (directory name can be overridden with `{linter.descriptor_id}_DIRECTORY`)"
            ]
        if len(linter.active_only_if_file_found) > 0:
            linter_doc_md += [
                f"- Activated only if one of these files is found:"
                f" `{', '.join(linter.active_only_if_file_found)}`"
            ]
        if linter.lint_all_files is True:
            linter_doc_md += [
                "- If this linter is active, all files will always be linted"
            ]
        if linter.lint_all_other_linters_files is True:
            linter_doc_md += [
                "- If this linter is active, all files linted by all other active linters will be linted"
            ]
        if len(linter.file_extensions) > 0:
            linter_doc_md += [
                f"- File extensions: `{'`, `'.join(linter.file_extensions)}`"
            ]
        if len(linter.file_names_regex) > 0:
            linter_doc_md += [
                f"- File names (regex): `{'`, `'.join(linter.file_names_regex)}`"
            ]
        if len(linter.file_contains_regex) > 0:
            linter_doc_md += [
                f"- Detected file content (regex): `{'`, `'.join(linter.file_contains_regex)}`"
            ]
        if len(linter.file_names_not_ends_with) > 0:
            linter_doc_md += [
                f"- File name don't ends with: `{'`, `'.join(linter.file_names_not_ends_with)}`"
            ]
        linter_doc_md += [
            "",
            "<!-- markdownlint-disable -->",
            "<!-- /* cSpell:disable */ -->",
        ]  # Don't check spelling of examples and logs

        # Lint mode
        linter_doc_md += ["### How the linting is performed", ""]
        if linter.cli_lint_mode == "project":
            linter_doc_md += [
                f"{linter.linter_name} is called once on the whole project directory (`project` CLI lint mode)",
                "",
                "- filtering can not be done using MegaLinter configuration variables,"
                f"it must be done using {linter.linter_name} configuration or ignore file (if existing)",
                f"- `VALIDATE_ALL_CODEBASE: false` doesn't make {linter.linter_name} analyze only updated files",
            ]
        elif linter.cli_lint_mode == "list_of_files":
            linter_doc_md += [
                f"- {linter.linter_name} is called once with the list "
                "of files as arguments (`list_of_files` CLI lint mode)"
            ]
        else:
            linter_doc_md += [
                f"- {linter.linter_name} is called one time by identified file (`file` CLI lint mode)"
            ]

        linter_doc_md += ["", "### Example calls", ""]
        for example in linter.examples:
            linter_doc_md += ["```shell", example, "```", ""]
        # Add help info
        with open(HELPS_FILE, "r", encoding="utf-8") as json_file:
            linter_helps = json.load(json_file)
            if linter.linter_name in linter_helps:
                linter_doc_md += ["", "### Help content", "", "```shell"]
                linter_doc_md += linter_helps[linter.linter_name]
                linter_doc_md += ["```"]
        # Installation doc
        linter_doc_md += ["", "### Installation on mega-linter Docker image", ""]
        item = vars(linter)
        merge_install_attr(item)
        linter_doc_md += get_install_md(item)
        # Example log files
        test_report_folder = (
            REPO_HOME
            + os.path.sep
            + ".automation"
            + os.path.sep
            + "test"
            + os.path.sep
            + linter.test_folder
            + os.path.sep
            + DEFAULT_REPORT_FOLDER_NAME
        )
        success_log_file_example = (
            test_report_folder + os.path.sep + f"SUCCESS-{linter.name}.txt"
        )
        if os.path.isfile(success_log_file_example):
            with open(success_log_file_example, "r", encoding="utf-8") as file:
                success_log_file_content = file.read()
            linter_doc_md += ["", "### Example success log", "", "```shell"]
            linter_doc_md += success_log_file_content.splitlines()
            linter_doc_md += ["```"]
        error_log_file_example = (
            test_report_folder + os.path.sep + f"ERROR-{linter.name}.txt"
        )
        if os.path.isfile(error_log_file_example):
            with open(error_log_file_example, "r", encoding="utf-8") as file:
                success_log_file_content = file.read()
            linter_doc_md += ["", "### Example error log", "", "```shell"]
            linter_doc_md += success_log_file_content.splitlines()
            linter_doc_md += ["```"]

        # Write md file
        file = open(
            f"{REPO_HOME}/docs/descriptors/{lang_lower}_{linter_name_lower}.md",
            "w",
            encoding="utf-8",
        )
        file.write("\n".join(linter_doc_md) + "\n")
        file.close()
        logging.info("Updated " + file.name)
    linters_tables_md += [""]
    return linters_tables_md


def build_flavors_md_table(filter_linter_name=None, replace_link=False):
    md_table = [
        "| <!-- --> | Flavor | Description | Embedded linters | Info |",
        "| :------: | :----- | :---------- | :--------------: | ---: |",
    ]
    icon_html = icon(
        f"{DOCS_URL_RAW_ROOT}/assets/images/mega-linter-square.png",
        "",
        "",
        "Default MegaLinter Flavor",
        32,
    )
    _descriptors, linters_by_type = list_descriptors_for_build()
    linters_number = (
        len(linters_by_type["language"])
        + len(linters_by_type["format"])
        + len(linters_by_type["tooling_format"])
        + +len(linters_by_type["other"])
    )
    docker_image_badge = f"![Docker Image Size (tag)]({BASE_SHIELD_IMAGE_LINK}/{ML_DOCKER_IMAGE}/{VERSION_V})"
    docker_pulls_badge = (
        f"![Docker Pulls]({BASE_SHIELD_COUNT_LINK}/" f"{ML_DOCKER_IMAGE})"
    )
    md_line_all = (
        f"| {icon_html} | [all]({MKDOCS_URL_ROOT}/supported-linters/) | "
        f"Default MegaLinter Flavor | {str(linters_number)} | {docker_image_badge} {docker_pulls_badge} |"
    )
    md_table += [md_line_all]
    all_flavors = megalinter.flavor_factory.get_all_flavors()
    for flavor_id, flavor in all_flavors.items():
        icon_html = icon(
            f"{DOCS_URL_RAW_ROOT}/assets/icons/{flavor_id}.ico",
            "",
            "",
            flavor_id,
            32,
        )
        linters_number = len(flavor["linters"])
        if (
            filter_linter_name is not None
            and filter_linter_name not in flavor["linters"]
        ):
            continue
        flavor_doc_url = f"{DOCS_URL_FLAVORS_ROOT}/{flavor_id}.md"
        docker_image_badge = (
            f"![Docker Image Size (tag)]({BASE_SHIELD_IMAGE_LINK}/"
            f"{ML_DOCKER_IMAGE}-{flavor_id}/{VERSION_V})"
        )
        docker_pulls_badge = (
            f"![Docker Pulls]({BASE_SHIELD_COUNT_LINK}/"
            f"{ML_DOCKER_IMAGE}-{flavor_id})"
        )
        md_line = (
            f"| {icon_html} | [{flavor_id}]({doc_url(flavor_doc_url)}) |"
            f" {flavor['label']} | {str(linters_number)} | {docker_image_badge} {docker_pulls_badge} |"
        )
        if replace_link is True:
            md_line = (
                md_line.replace(DOCS_URL_FLAVORS_ROOT, MKDOCS_URL_ROOT + "/flavors")
                .replace(".md#readme", "/")
                .replace(".md", "/")
            )
        md_table += [md_line]
    return md_table


# Build plugins table from YML file in .automation/plugins.yml
def build_plugins_md_table():
    with open(PLUGINS_FILE, "r", encoding="utf-8") as f:
        plugins_file_data = yaml.safe_load(f)
    plugins = plugins_file_data["plugins"]
    md_table = [
        "| Name | Description | Author | Raw URL |",
        "| :----- | :---------- | :--------------: | :--- |",
    ]
    for plugin in plugins:
        md_table += [
            f"| [**{plugin['name']}**]({plugin['docUrl']}) | "
            f"{plugin['description']} | {plugin['author']} | "
            f"[Descriptor]({plugin['pluginUrl']}) |",
        ]
    return md_table


def update_mkdocs_and_workflow_yml_with_flavors():
    mkdocs_yml = []
    gha_workflow_yml = ["        flavor:", "          ["]
    for flavor_id, _flavor_info in megalinter.flavor_factory.get_all_flavors().items():
        mkdocs_yml += [f'      - "{flavor_id}": "flavors/{flavor_id}.md"']
        gha_workflow_yml += [f'            "{flavor_id}",']
    gha_workflow_yml += ["          ]"]
    # Update mkdocs.yml file
    replace_in_file(
        f"{REPO_HOME}/mkdocs.yml",
        "# flavors-start",
        "# flavors-end",
        "\n".join(mkdocs_yml),
    )
    # Update Github actions workflow files
    replace_in_file(
        f"{REPO_HOME}/.github/workflows/deploy-BETA-flavors.yml",
        "# flavors-start",
        "# flavors-end",
        "\n".join(gha_workflow_yml),
    )
    replace_in_file(
        f"{REPO_HOME}/.github/workflows/deploy-RELEASE-flavors.yml",
        "# flavors-start",
        "# flavors-end",
        "\n".join(gha_workflow_yml),
    )


def update_docker_pulls_counter():
    logging.info("Fetching docker pull counters on flavors images")
    total_count = 0
    all_flavors_ids = list(megalinter.flavor_factory.get_all_flavors().keys())
    all_flavors_ids.insert(0, "all")
    with open(DOCKER_STATS_FILE, "r", encoding="utf-8") as json_stats:
        docker_stats = json.load(json_stats)
    now_str = datetime.now().replace(microsecond=0).isoformat()
    for flavor_id in all_flavors_ids:
        if flavor_id == "all":
            docker_image_url = (
                f"https://hub.docker.com/v2/repositories/{ML_DOCKER_IMAGE}"
            )
            legacy_docker_image_url = (
                f"https://hub.docker.com/v2/repositories/{ML_DOCKER_IMAGE_LEGACY}"
            )
            legacy_v5_docker_image_url = (
                f"https://hub.docker.com/v2/repositories/{ML_DOCKER_IMAGE_LEGACY_V5}"
            )
        else:
            docker_image_url = (
                f"https://hub.docker.com/v2/repositories/{ML_DOCKER_IMAGE}-{flavor_id}"
            )
            legacy_docker_image_url = f"https://hub.docker.com/v2/repositories/{ML_DOCKER_IMAGE_LEGACY}-{flavor_id}"
            legacy_v5_docker_image_url = (
                "https://hub.docker.com/v2/repositories/"
                + f"{ML_DOCKER_IMAGE_LEGACY_V5}-{flavor_id}"
            )

        flavor_count_1 = perform_count_request(docker_image_url)
        flavor_count_2 = perform_count_request(legacy_docker_image_url)
        flavor_count_3 = perform_count_request(legacy_v5_docker_image_url)
        flavor_count = flavor_count_1 + flavor_count_2 + flavor_count_3
        logging.info(f"- docker pulls for {flavor_id}: {flavor_count}")
        total_count = total_count + flavor_count
        flavor_stats = list(docker_stats.get(flavor_id, []))
        flavor_stats.append([now_str, flavor_count])
        flavor_stats = keep_one_stat_by_day(flavor_stats)
        docker_stats[flavor_id] = flavor_stats
    total_count_human = number_human_format(total_count)
    logging.info(f"Total docker pulls: {total_count_human} ({total_count})")
    # Update total badge counters
    replace_in_file(
        f"{REPO_HOME}/README.md", "pulls-", "-blue", total_count_human, False
    )
    replace_in_file(
        f"{REPO_HOME}/mega-linter-runner/README.md",
        "pulls-",
        "-blue",
        total_count_human,
        False,
    )
    # Write docker stats
    with open(DOCKER_STATS_FILE, "w", encoding="utf-8") as jsonstats:
        json.dump(docker_stats, jsonstats, indent=4, sort_keys=True)


def perform_count_request(docker_image_url):
    r = requests_retry_session().get(docker_image_url)
    resp = r.json()
    flavor_count = resp["pull_count"] if "pull_count" in resp else 0
    logging.info(f"{docker_image_url}: {flavor_count}")
    return flavor_count


def keep_one_stat_by_day(flavor_stats):
    filtered_flavor_stats = []
    prev_date = date.min
    for [count_date_iso, count_date_number] in flavor_stats:
        count_date = datetime.fromisoformat(count_date_iso).date()
        if count_date == prev_date:
            filtered_flavor_stats.pop()
        filtered_flavor_stats.append([count_date_iso, count_date_number])
        prev_date = count_date
    return filtered_flavor_stats


def requests_retry_session(
    retries=3,
    backoff_factor=0.5,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def number_human_format(num, round_to=1):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return "{:.{}f}{}".format(
        round(num, round_to), round_to, ["", "k", "M", "G", "T", "P"][magnitude]
    )


def get_linter_base_info(linter):
    lang_lower = linter.descriptor_id.lower()
    linter_name_lower = linter.linter_name.lower().replace("-", "_")
    descriptor_label = (
        f"**{linter.descriptor_label}** ({linter.descriptor_id})"
        if hasattr(linter, "descriptor_label")
        else f"**{linter.descriptor_id}**"
    )
    return lang_lower, linter_name_lower, descriptor_label


def get_install_md(item):
    linter_doc_md = []
    if "install" not in item:
        linter_doc_md += ["None"]
        return linter_doc_md
    if "dockerfile" in item["install"]:
        linter_doc_md += ["- Dockerfile commands :"]
        linter_doc_md += ["```dockerfile"]
        linter_doc_md += item["install"]["dockerfile"]
        linter_doc_md += ["```", ""]
    if "apk" in item["install"]:
        linter_doc_md += ["- APK packages (Linux):"]
        linter_doc_md += md_package_list(
            item["install"]["apk"],
            "apk",
            "  ",
            "https://pkgs.alpinelinux.org/packages?branch=edge&name=",
        )
    if "npm" in item["install"]:
        linter_doc_md += ["- NPM packages (node.js):"]
        linter_doc_md += md_package_list(
            item["install"]["npm"], "npm", "  ", "https://www.npmjs.com/package/"
        )
    if "pip" in item["install"]:
        linter_doc_md += ["- PIP packages (Python):"]
        linter_doc_md += md_package_list(
            item["install"]["pip"], "pip", "  ", "https://pypi.org/project/"
        )
    if "gem" in item["install"]:
        linter_doc_md += ["- GEM packages (Ruby) :"]
        linter_doc_md += md_package_list(
            item["install"]["gem"], "gem", "  ", "https://rubygems.org/gems/"
        )
    return linter_doc_md


def doc_url(href):
    if (
        "/descriptors/" in href
        or "/flavors/" in href
        or "/licenses/" in href
        or "/reporters/" in href
    ) and "#" not in href:
        return href
    elif href.startswith("https://github") and "#" not in href:
        return href + "#readme"
    return href


def banner_link(src, alt, link, title, align, maxheight):
    return f"""
<div align=\"{align}\">
  <a href=\"{link}\" target=\"blank\" title=\"{title}\">
    <img src=\"{src}\" alt=\"{alt}\" height=\"{maxheight}px\" class=\"megalinter-banner\">
  </a>
</div>"""


def logo_link(src, alt, link, title, maxheight):
    return (
        f'<a href="{link}" target="blank" title="{title}">'
        f'<img src="{src}" alt="{alt}" height="{maxheight}px" class="megalinter-logo"></a>'
    )


def icon(src, alt, _link, _title, height):
    return (
        f'<img src="{src}" alt="{alt}" height="{height}px" class="megalinter-icon"></a>'
    )


def md_ide(ide):
    if ide in IDE_LIST:
        return f"[{IDE_LIST[ide]['label']}]({IDE_LIST[ide]['url']})"
    return ide


def md_ide_install_link(ide, ide_extension):
    item_name = None
    # Visual studio code plugins
    if ide == "vscode":
        if ide_extension["url"].startswith(
            "https://marketplace.visualstudio.com/items?itemName="
        ):
            item_name = dict(
                parse_urllib.parse_qsl(
                    parse_urllib.urlsplit(ide_extension["url"]).query
                )
            )["itemName"]
        elif ide_extension["url"].startswith(
            "https://marketplace.visualstudio.com/items/"
        ):
            item_name = ide_extension["url"].split("/items/", 1)[1]
        if item_name is not None:
            install_link = f"vscode:extension/{item_name}"
            return f"[![Install in VSCode]({md_get_install_button(ide)})]({install_link}){{target=_blank}}"
    # JetBrains Idea family editors plugins
    if ide == "idea":
        if ide_extension["url"].startswith("https://plugins.jetbrains.com/plugin/"):
            item_name = ide_extension["url"].split("/")[-1].split("-")[0]
        if item_name is not None and item_name.isnumeric():
            iframe_content = (
                f"https://plugins.jetbrains.com/embeddable/install/{item_name}"
            )
            return f'<iframe frameborder="none" width="245px" height="48px" src="{iframe_content}"></iframe>'
    return f"[Visit Web Site]({ide_extension['url']}){{target=_blank}}"


def md_get_install_button(key):
    image_file = f"{REPO_IMAGES}{os.path.sep}btn_install_{key}.png"
    if os.path.isfile(image_file):
        return f"{DOCS_URL_RAW_ROOT}/assets/images/btn_install_{key}.png"
    return f"{DOCS_URL_RAW_ROOT}/assets/images/btn_install_default.png"


def md_to_text(md):
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()


def get_repo(linter, check_github=True):
    if linter.linter_url:
        parse_res = parse(linter.linter_url)
        if parse_res is not None and (
            (check_github is True and parse_res.github is True) or check_github is False
        ):
            return parse_res
    if hasattr(linter, "linter_repo"):
        parse_res = parse(linter.linter_repo)
        if parse_res is not None and (
            (check_github is True and parse_res.github is True) or check_github is False
        ):
            return parse_res
    return None


def merge_install_attr(item):
    if "descriptor_install" not in item:
        return
    for elt, elt_val in item["descriptor_install"].items():
        if "install" not in item:
            item["install"] = {}
        if elt in item["install"]:
            if elt == "dockerfile":
                item["install"][elt] = (
                    ["# Parent descriptor install"]
                    + elt_val
                    + ["# Linter install"]
                    + item["install"][elt]
                )
            else:
                item["install"][elt] = elt_val + item["install"][elt]


def md_package_list(package_list, type, indent, start_url):
    res = []
    for package_id_v in package_list:
        package_id = package_id_v
        package_version = ""

        if type == "npm" and package_id.count("@") == 2:  # npm specific version
            package_id_split = package_id.split("@")
            package_id = "@" + package_id_split[1]
            package_version = "/v/" + package_id_split[2]
        elif type == "pip" and "==" in package_id_v:  # py specific version
            package_id = package_id_v.split("==")[0]
            package_version = "/" + package_id_v.split("==")[1]
        elif type == "gem":
            gem_match = re.match(
                r"(.*)\s-v\s(.*)", package_id_v
            )  # gem specific version

            if gem_match:  # gem specific version
                package_id = gem_match.group(1)
                package_version = "/versions/" + gem_match.group(2)
        res += [f"{indent}- [{package_id_v}]({start_url}{package_id}{package_version})"]
    return res


def replace_in_file(file_path, start, end, content, add_new_line=True):
    # Read in the file
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    # Detect markdown headers if in replacement
    header_content = None
    header_matches = re.findall(
        r"<!-- markdown-headers\n(.*)\n-->", content, re.MULTILINE | re.DOTALL
    )
    if header_matches and len(header_matches) > 0:
        # Get text between markdown-headers tag
        header_content = header_matches[0]
        content = re.sub(
            r"<!-- markdown-headers\n.*?\n-->", "", content, 1, re.MULTILINE | re.DOTALL
        )[1:]
    # Replace the target string
    if add_new_line is True:
        replacement = f"{start}\n{content}\n{end}"
    else:
        replacement = f"{start}{content}{end}"
    regex = rf"{start}([\s\S]*?){end}"
    file_content = re.sub(regex, replacement, file_content, 1, re.DOTALL)
    # Add / replace header if necessary
    if header_content is not None:
        existing_header_matches = re.findall(
            r"---\n(.*)\n---", file_content, re.MULTILINE | re.DOTALL
        )
        if (
            existing_header_matches
            and len(existing_header_matches) > 0
            and file_content.startswith("---")
        ):
            file_content = re.sub(
                r"---\n.*?\n---",
                header_content,
                file_content,
                1,
                re.MULTILINE | re.DOTALL,
            )
        else:
            file_content = header_content + "\n" + file_content
    # Write the file out again
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(file_content)
    logging.info("Updated " + file.name + " between " + start + " and " + end)


def add_in_config_schema_file(variables):
    with open(CONFIG_JSON_SCHEMA, "r", encoding="utf-8") as json_file:
        json_schema = json.load(json_file)
    json_schema_props = json_schema["properties"]
    updated = False
    for key, variable in variables:
        prev_val = json_schema_props.get(key, "")
        json_schema_props[key] = variable
        if prev_val != variable:
            updated = True
    json_schema["properties"] = json_schema_props
    if updated is True:
        with open(CONFIG_JSON_SCHEMA, "w", encoding="utf-8") as outfile:
            json.dump(json_schema, outfile, indent=2, sort_keys=True)
            outfile.write("\n")


def remove_in_config_schema_file(variables):
    with open(CONFIG_JSON_SCHEMA, "r", encoding="utf-8") as json_file:
        json_schema = json.load(json_file)
    json_schema_props = json_schema["properties"]
    updated = False
    for variable in variables:
        prev_val = json_schema_props.get(variable, "")
        if prev_val != "":
            del json_schema_props[variable]
            updated = True
    json_schema["properties"] = json_schema_props
    if updated is True:
        with open(CONFIG_JSON_SCHEMA, "w", encoding="utf-8") as outfile:
            json.dump(json_schema, outfile, indent=2, sort_keys=True)
            outfile.write("\n")


def copy_md_file(source_file, target_file):
    copyfile(source_file, target_file)
    source_file_formatted = (
        os.path.relpath(source_file).replace("..\\", "").replace("\\", "/")
    )
    comment = (
        f"<!-- This file has been {'@'}generated by build.sh, please don't update it, but update its source "
        f"{source_file_formatted}, then build again -->"
    )
    with open(target_file, "r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(f"{comment}\n{content}")


def move_to_file(file_path, start, end, target_file, keep_in_source=False):
    # Read in the file
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    # Replace the target string
    replacement_content = ""
    replacement = f"{start}\n{replacement_content}\n{end}"
    regex = rf"{start}([\s\S]*?){end}"
    bracket_contents = re.findall(regex, file_content, re.DOTALL)
    if bracket_contents:
        bracket_content = bracket_contents[0]
    else:
        bracket_content = ""
    if keep_in_source is False:
        file_content = re.sub(regex, replacement, file_content, 1, re.DOTALL)
    # Write the file out again
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(file_content)
    logging.info("Updated " + file.name + " between " + start + " and " + end)
    if "<!-- install-" in start or "<!-- config-" in start:
        bracket_content = (
            bracket_content.replace("####", "#TWO#")
            .replace("###", "#ONE#")
            .replace("#TWO#", "##")
            .replace("#ONE#", "#")
        )
    else:
        bracket_content = (
            bracket_content.replace("####", "#THREE#")
            .replace("###", "#TWO#")
            .replace("##", "#ONE#")
            .replace("#THREE#", "###")
            .replace("#TWO#", "##")
            .replace("#ONE#", "#")
        )

    if not os.path.isfile(target_file):
        mdl_disable = "<!-- markdownlint-disable MD013 -->"
        comment = f"<!-- {'@'}generated by .automation/build.py, please don't update manually -->"
        with open(target_file, "w", encoding="utf-8") as file2:
            file2.write(
                f"{mdl_disable}\n{comment}\n{start}\n{bracket_content}\n{end}\n"
            )
    else:
        replace_in_file(target_file, start, end, bracket_content)


def replace_full_url_links(target_file, full_url__base, shorten_url=""):
    with open(target_file, "r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace(full_url__base, shorten_url))


def replace_anchors_by_links(file_path, moves):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    file_content_new = file_content
    for move in moves:
        file_content_new = file_content_new.replace(f"(#{move})", f"({move}.md)")
    for pair in [
        ["languages", "supported-linters.md#languages"],
        ["formats", "supported-linters.md#formats"],
        ["tooling-formats", "supported-linters.md#tooling-formats"],
        ["other", "supported-linters.md#other"],
        ["apply-fixes", "config-apply-fixes.md"],
        ["installation", "install-assisted.md"],
        ["configuration", "config-file.md"],
        ["activation-and-deactivation", "config-activation.md"],
        ["filter-linted-files", "config-filtering.md"],
        ["pre-commands", "config-precommands.md"],
        ["post-commands", "config-postcommands.md"],
        ["environment-variables-security", "config-variables-security.md"],
    ]:
        file_content_new = file_content_new.replace(f"(#{pair[0]})", f"({pair[1]})")
    if file_content_new != file_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(file_content_new)
        logging.info(f"Updated links in {file_path}")


# Apply descriptor JSON Schema to every descriptor file
def validate_own_megalinter_config():
    with open(CONFIG_JSON_SCHEMA, "r", encoding="utf-8") as schema_file:
        descriptor_schema = schema_file.read()
        with open(
            OWN_MEGALINTER_CONFIG_FILE, "r", encoding="utf-8"
        ) as descriptor_file1:
            logging.info("Validating " + os.path.basename(OWN_MEGALINTER_CONFIG_FILE))
            mega_linter_config = descriptor_file1.read()
            jsonschema.validate(
                instance=yaml.safe_load(mega_linter_config),
                schema=yaml.safe_load(descriptor_schema),
            )


# Apply descriptor JSON Schema to every descriptor file
def validate_descriptors():
    with open(DESCRIPTOR_JSON_SCHEMA, "r", encoding="utf-8") as schema_file:
        descriptor_schema = schema_file.read()
        descriptor_files = megalinter.linter_factory.list_descriptor_files()
        errors = 0
        for descriptor_file in descriptor_files:
            with open(descriptor_file, "r", encoding="utf-8") as descriptor_file1:
                logging.info("Validating " + os.path.basename(descriptor_file))
                descriptor = descriptor_file1.read()
                try:
                    jsonschema.validate(
                        instance=yaml.safe_load(descriptor),
                        schema=yaml.safe_load(descriptor_schema),
                    )
                except jsonschema.exceptions.ValidationError as validation_error:
                    logging.error(
                        f"{os.path.basename(descriptor_file)} is not compliant with JSON schema"
                    )
                    logging.error(f"reason: {str(validation_error)}")
                    errors = errors + 1
        if errors > 0:
            raise ValueError(
                "Errors have been found while validating descriptor YML files, please check logs"
            )


def finalize_doc_build():
    # Copy README.md into /docs/index.md
    target_file = f"{REPO_HOME}{os.path.sep}docs{os.path.sep}index.md"
    copy_md_file(
        f"{REPO_HOME}{os.path.sep}README.md",
        target_file,
    )
    # Split README sections into individual files
    moves = [
        "quick-start",
        "supported-linters",
        # 'languages',
        # 'format',
        # 'tooling-formats',
        # 'other',
        "install-assisted",
        "install-version",
        "install-github",
        "install-gitlab",
        "install-azure",
        "install-bitbucket",
        "install-jenkins",
        "install-concourse",
        "install-drone",
        "install-docker",
        "install-locally",
        "config-file",
        "config-variables",
        "config-activation",
        "config-filtering",
        "config-apply-fixes",
        "config-linters",
        "config-precommands",
        "config-postcommands",
        "config-variables-security",
        "config-cli-lint-mode",
        "reporters",
        "flavors",
        "badge",
        "plugins",
        "articles",
        "frequently-asked-questions",
        "how-to-contribute",
        "special-thanks",
        "license",
        "mega-linter-vs-super-linter",
    ]
    for move in moves:
        section_page_md_file = f"{REPO_HOME}{os.path.sep}docs{os.path.sep}{move}.md"
        move_to_file(
            target_file,
            f"<!-- {move}-section-start -->",
            f"<!-- {move}-section-end -->",
            section_page_md_file,
            move in ["supported-linters", "demo"],
        )
        replace_anchors_by_links(section_page_md_file, moves)
        replace_full_url_links(section_page_md_file, DOCS_URL_ROOT + "/", "")

    # Replace hardcoded links into relative links
    replace_full_url_links(target_file, DOCS_URL_ROOT + "/", "")
    logging.info(f"Copied and updated {target_file}")
    # Add header intro
    replace_in_file(
        target_file,
        "<!-- header-intro-start -->",
        "<!-- header-intro-end -->",
        "<h2>Verify your code consistency with an open-source tool.<br/>"
        + 'Powered by <a href="https://www.ox.security/?ref=megalinter" target="_blank">OX Security</a>.</h2>',
    )
    # Add header badges
    replace_in_file(
        target_file,
        "<!-- mega-linter-badges-start -->",
        "<!-- mega-linter-badges-end -->",
        """![GitHub release](https://img.shields.io/github/v/release/oxsecurity/megalinter?sort=semver&color=%23FD80CD)
[![Docker Pulls](https://img.shields.io/badge/docker%20pulls-5.5M-blue?color=%23FD80CD)](https://megalinter.io/flavors/)
[![Downloads/week](https://img.shields.io/npm/dw/mega-linter-runner.svg?color=%23FD80CD)](https://npmjs.org/package/mega-linter-runner)
[![GitHub stars](https://img.shields.io/github/stars/oxsecurity/megalinter?cacheSeconds=3600&color=%23FD80CD)](https://github.com/oxsecurity/megalinter/stargazers/)
[![Dependents](https://img.shields.io/static/v1?label=Used%20by&message=2180&color=%23FD80CD&logo=slickpic)](https://github.com/oxsecurity/megalinter/network/dependents)
[![GitHub contributors](https://img.shields.io/github/contributors/oxsecurity/megalinter.svg?color=%23FD80CD)](https://github.com/oxsecurity/megalinter/graphs/contributors/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square&color=%23FD80CD)](http://makeapullrequest.com)""",  # noqa: E501
    )

    # Remove TOC in target file
    replace_in_file(
        target_file,
        "<!-- mega-linter-title-start -->",
        "<!-- mega-linter-title-end -->",
        "",
    )
    replace_in_file(
        target_file,
        "<!-- table-of-contents-start -->",
        "<!-- table-of-contents-end -->",
        "",
    )
    replace_in_file(
        target_file,
        "<!-- configuration-section-start -->",
        "<!-- configuration-section-end -->",
        "",
    )
    replace_in_file(
        target_file,
        "<!-- installation-section-start -->",
        "<!-- installation-section-end -->",
        "",
    )
    # Remove link to online doc
    replace_in_file(
        target_file,
        "<!-- online-doc-start -->",
        "<!-- online-doc-end -->",
        "",
    )
    replace_anchors_by_links(target_file, moves)
    # Copy mega-linter-runner/README.md into /docs/mega-linter-runner.md
    target_file_readme_runner = (
        f"{REPO_HOME}{os.path.sep}docs{os.path.sep}mega-linter-runner.md"
    )
    copy_md_file(
        f"{REPO_HOME}{os.path.sep}mega-linter-runner{os.path.sep}README.md",
        target_file_readme_runner,
    )
    # Update mega-linter-runner.md for online doc
    replace_in_file(
        target_file_readme_runner,
        "<!-- header-logo-start -->",
        "<!-- header-logo-end -->",
        "",
    )
    replace_in_file(
        target_file_readme_runner,
        "<!-- readme-header-start -->",
        "<!-- readme-header-end -->",
        "",
    )
    replace_in_file(
        target_file_readme_runner,
        "<!-- linters-section-start -->",
        "<!-- linters-section-end -->",
        "",
    )
    # Replace hardcoded links into relative links
    with open(target_file_readme_runner, "r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace(DOCS_URL_ROOT + "/", ""))
    logging.info(f"Copied and updated {target_file_readme_runner}")


def generate_mkdocs_yml():
    logging.info("Generating mkdocs dynamic yml…")
    descriptors, linters_by_type = list_descriptors_for_build()
    process_type_mkdocs_yml(linters_by_type, "language")
    process_type_mkdocs_yml(linters_by_type, "format")
    process_type_mkdocs_yml(linters_by_type, "tooling_format")
    process_type_mkdocs_yml(linters_by_type, "other")


def process_type_mkdocs_yml(linters_by_type, type1):
    descriptor_linters = linters_by_type[type1]
    mkdocs_yml = []
    prev_lang = ""
    for linter in descriptor_linters:
        lang_lower, linter_name_lower, descriptor_label = get_linter_base_info(linter)
        # Language menu
        if prev_lang != lang_lower:
            descriptor_label = descriptor_label.replace("*", "").replace(r"\(.*\)", "")
            mkdocs_yml += [
                f'          - "{descriptor_label}":',
                f'              - "All {descriptor_label} linters": "descriptors/{lang_lower}.md"',
            ]

        prev_lang = lang_lower
        # Linters menus
        mkdocs_yml += [
            f'              - "{linter.linter_name}": "descriptors/{lang_lower}_{linter_name_lower}.md"'
        ]
    # Update mkdocs.yml file
    replace_in_file(
        f"{REPO_HOME}/mkdocs.yml",
        f"# {type1}-start",
        f"# {type1}-end",
        "\n".join(mkdocs_yml),
    )


def generate_json_schema_enums():
    # Update list of flavors in descriptor schema
    flavors = megalinter.flavor_factory.list_megalinter_flavors()
    with open(DESCRIPTOR_JSON_SCHEMA, "r", encoding="utf-8") as json_file:
        json_schema = json.load(json_file)
    json_schema["definitions"]["enum_flavors"]["enum"] = ["all_flavors"] + list(
        sorted(set(list(flavors.keys())))
    )
    with open(DESCRIPTOR_JSON_SCHEMA, "w", encoding="utf-8") as outfile:
        json.dump(json_schema, outfile, indent=2, sort_keys=True)
        outfile.write("\n")
    # Update list of descriptors and linters in configuration schema
    descriptors, _linters_by_type = list_descriptors_for_build()
    linters = megalinter.linter_factory.list_all_linters({"request_id": "build"})
    with open(CONFIG_JSON_SCHEMA, "r", encoding="utf-8") as json_file:
        json_schema = json.load(json_file)
    json_schema["definitions"]["enum_descriptor_keys"]["enum"] = [
        x["descriptor_id"] for x in descriptors
    ]
    json_schema["definitions"]["enum_descriptor_keys"]["enum"] += ["CREDENTIALS", "GIT"]
    json_schema["definitions"]["enum_linter_keys"]["enum"] = [x.name for x in linters]
    # Deprecated linters
    json_schema["definitions"]["enum_linter_keys"]["enum"] += DEPRECATED_LINTERS

    # Sort:
    json_schema["definitions"]["enum_descriptor_keys"]["enum"] = sorted(
        set(json_schema["definitions"]["enum_descriptor_keys"]["enum"])
    )
    json_schema["definitions"]["enum_linter_keys"]["enum"] = sorted(
        set(json_schema["definitions"]["enum_linter_keys"]["enum"])
    )
    with open(CONFIG_JSON_SCHEMA, "w", encoding="utf-8") as outfile:
        json.dump(json_schema, outfile, indent=2, sort_keys=True)
        outfile.write("\n")


# Collect linters info from linter url, later used to build link preview card within linter documentation
def collect_linter_previews():
    linters = megalinter.linter_factory.list_all_linters({"request_id": "build"})
    # Read file
    with open(LINKS_PREVIEW_FILE, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    updated = False
    # Collect info using web_preview
    for linter in linters:
        if (
            linter.linter_name not in data
            or megalinter.config.get(None, "REFRESH_LINTER_PREVIEWS", "false") == "true"
        ):
            logging.info(
                f"Collecting link preview info for {linter.linter_name} at {linter.linter_url}"
            )
            title = None
            try:
                title, description, image = web_preview(
                    linter.linter_url, parser="html.parser", timeout=1000
                )
            except webpreview.excepts.URLUnreachable as e:
                logging.error("URLUnreachable: " + str(e))
            except Exception as e:
                logging.error(str(e))
            if title is not None:
                item = {
                    "title": megalinter.utils.decode_utf8(title),
                    "description": megalinter.utils.decode_utf8(description),
                    "image": image,
                }
                data[linter.linter_name] = item
                updated = True
    # Update file
    if updated is True:
        with open(LINKS_PREVIEW_FILE, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=2, sort_keys=True)


def generate_documentation_all_linters():
    linters_raw = megalinter.linter_factory.list_all_linters(({"request_id": "build"}))
    linters = []
    with open(VERSIONS_FILE, "r", encoding="utf-8") as json_file:
        linter_versions = json.load(json_file)
    for linter in linters_raw:
        duplicates = [
            [index, dup_linter]
            for index, dup_linter in enumerate(linters)
            if dup_linter.linter_name == linter.linter_name
        ]
        if len(duplicates) == 0:
            setattr(linter, "descriptor_id_list", [linter.descriptor_id])
            linters += [linter]
        else:
            index, duplicate = duplicates[0]
            duplicate.descriptor_id_list += [linter.descriptor_id]
            duplicate.descriptor_id_list.sort()
            linters[index] = duplicate
    linters.sort(key=lambda x: x.linter_name)
    table_header = [
        "Linter",
        "Version",
        "License",
        "Popularity",
        "Descriptors",
        "Status",
        "URL",
    ]
    md_table_lines = []
    table_data = [table_header]
    hearth_linters_md = []
    leave = False
    for linter in linters:
        status = "Not submitted"
        md_status = ":white_circle:"
        # url
        url = (
            linter.linter_repo
            if hasattr(linter, "linter_repo") and linter.linter_repo is not None
            else linter.linter_url
        )
        md_url = (
            f"[Repository]({linter.linter_repo}){{target=_blank}}"
            if hasattr(linter, "linter_repo") and linter.linter_repo is not None
            else f"[Web Site]({linter.linter_url}){{target=_blank}}"
        )
        md_linter_name = f"[**{linter.linter_name}**]({url}){{target=_blank}}"
        # version
        linter_version = "N/A"
        if (
            linter.linter_name in linter_versions
            and linter_versions[linter.linter_name] != "0.0.0"
        ):
            linter_version = linter_versions[linter.linter_name]
        # reference on linter documentation
        if hasattr(
            linter, "linter_megalinter_ref_url"
        ) and linter.linter_megalinter_ref_url not in ["", None]:
            url = linter.linter_megalinter_ref_url
            if linter.linter_megalinter_ref_url not in ["no", "never"]:
                md_url = f"[MegaLinter reference]({linter.linter_megalinter_ref_url}){{target=_blank}}"
            if linter.linter_megalinter_ref_url == "no":
                status = "❌ Refused"
                md_status = ":no_entry_sign:"
            elif linter.linter_megalinter_ref_url == "never":
                status = "Θ Not applicable"
                md_status = "<!-- -->"
            elif "/pull/" in str(url):
                if url.endswith("#ok"):
                    status = "✅ Awaiting publication"
                    md_status = ":love_letter:"
                else:
                    status = "Ω Pending"
                    md_status = ":hammer_and_wrench:"
                md_url = f"[Pull Request]({url}){{target=_blank}}"
                url = "PR: " + url
            else:
                status = "✅ Published"
                md_status = ":heart:"
                hearth_linters_md += [
                    f"- [{linter.linter_name}]({linter.linter_megalinter_ref_url}){{target=_blank}}"
                ]
        # license
        with open(LICENSES_FILE, "r", encoding="utf-8") as json_file:
            linter_licenses = json.load(json_file)
            license = ""
            md_license = "<!-- -->"
            linter_license_md_file = None
            # get license from github api
            repo = get_github_repo(linter)
            if repo is not None:
                repo = linter.linter_repo.split("https://github.com/", 1)[1]
                api_github_url = f"https://api.github.com/repos/{repo}"
                api_github_headers = {"content-type": "application/json"}
                use_github_token = ""
                if "GITHUB_TOKEN" in os.environ:
                    github_token = os.environ["GITHUB_TOKEN"]
                    api_github_headers["authorization"] = f"Bearer {github_token}"
                    use_github_token = " (with GITHUB_TOKEN)"
                logging.info(
                    f"Getting license info for {api_github_url}" + use_github_token
                )
                try:
                    session = requests_retry_session()
                    r = session.get(api_github_url, headers=api_github_headers)
                except requests.exceptions.ConnectionError as e:
                    logging.warning(
                        "Connection error - Unable to get info from github api: "
                        + str(e)
                    )
                    leave = True
                    break
                except Exception as e:
                    logging.warning("Unable to update docker pull counters: " + str(e))
                    leave = True
                    break

                if r is not None:
                    # Update license key for licenses file
                    resp = r.json()
                    if resp is not None and not isinstance(resp, type(None)):
                        if (
                            "license" in resp
                            and resp["license"] is not None
                            and "spdx_id" in resp["license"]
                        ):
                            license = (
                                resp["license"]["spdx_id"]
                                if resp["license"]["spdx_id"] != "NOASSERTION"
                                else (
                                    resp["license"]["name"]
                                    if "name" in resp["license"]
                                    else (
                                        resp["license"]["key"]
                                        if "key" in resp["license"]
                                        else ""
                                    )
                                )
                            )
                            if license != "":
                                linter_licenses[linter.linter_name] = license
                    # Fetch and update license file if not in repo
                    linter_license_md_file = (
                        f"{REPO_HOME}/docs/licenses/{linter.linter_name}.md"
                    )
                    if not os.path.isfile(linter_license_md_file):
                        api_github_license_url = api_github_url + "/license"
                        r_license = session.get(
                            api_github_license_url, headers=api_github_headers
                        )
                        if r_license is not None:
                            resp_license = r_license.json()
                            if "download_url" in resp_license:
                                license_downloaded = session.get(
                                    resp_license["download_url"],
                                    headers=api_github_headers,
                                )
                                with open(
                                    linter_license_md_file, "w", encoding="utf-8"
                                ) as license_out_file:
                                    license_header = (
                                        "---\n"
                                        f"title: License info for {linter.linter_name} within MegaLinter\n"
                                        "search:\n"
                                        "  exclude: true\n"
                                        "---\n"
                                    )
                                    license_out_file.write(
                                        license_header + license_downloaded.text
                                    )
                                    logging.info(
                                        f"Copied license of {linter.linter_name} in {linter_license_md_file}"
                                    )
                            else:
                                logging.warning(
                                    f"WARNING: No download_url returned in {api_github_license_url}"
                                )

            # get license from descriptor
            if (
                (license is None or license == "" or license == "Other")
                and hasattr(linter, "linter_spdx_license")
                and linter.linter_spdx_license is not None
            ):
                license = linter.linter_spdx_license
            # get license from licenses file
            if license == "" and linter.linter_name in linter_licenses:
                license = linter_licenses[linter.linter_name]
            # build md_license
            if license != "":
                if linter_license_md_file is not None:
                    license_doc_url = f"licenses/{linter.linter_name}.md"
                    md_license = f"[{license}]({license_doc_url})"
                else:
                    md_license = license
        # Update licenses file
        with open(LICENSES_FILE, "w", encoding="utf-8") as outfile:
            json.dump(linter_licenses, outfile, indent=4, sort_keys=True)
        # popularity
        md_popularity = "<!-- -->"
        repo = get_github_repo(linter)
        if repo is not None:
            md_popularity = (
                f"[![GitHub stars](https://img.shields.io/github/stars/{repo}?cacheSeconds=3600)]"
                f"(https://github.com/{repo}){{target=_blank}}"
            )
        # line
        table_line = [
            linter.linter_name,
            linter_version,
            license,
            "N/A",
            ", ".join(linter.descriptor_id_list),
            status,
            url,
        ]
        table_data += [table_line]

        linter_doc_links = []
        for descriptor_id in linter.descriptor_id_list:
            linter_doc_url = f"descriptors/{descriptor_id.lower()}_{linter.linter_name.lower().replace('-', '_')}.md"
            link = f"[{descriptor_id}]({doc_url(linter_doc_url)})"
            linter_doc_links += [link]
        md_table_line = [
            md_linter_name,
            linter_version,
            md_license,
            md_popularity,
            "<br/> ".join(linter_doc_links),
            md_status,
            md_url,
        ]
        md_table_lines += [md_table_line]

    if leave is True:
        logging.warning("Error during process: Don't regenerate list of linters")
        return

    # Write referring linters to README
    hearth_linters_md_str = "\n".join(hearth_linters_md)
    replace_in_file(
        f"{REPO_HOME}/README.md",
        "<!-- referring-linters-start -->",
        "<!-- referring-linters-end -->",
        hearth_linters_md_str,
    )

    # Display results (disabled)
    table = terminaltables.AsciiTable(table_data)
    table.title = "----Reference to MegaLinter in linters documentation summary"
    # Output table in console
    logging.info("")
    # for table_line in table.table.splitlines():
    #    logging.info(table_line)
    logging.info("")

    # Write in file
    with open(REPO_HOME + "/docs/all_linters.md", "w", encoding="utf-8") as outfile:
        outfile.write(
            f"<!-- This file has been automatically {'@'}generated by build.py"
            " (generate_documentation_all_linters method) -->\n"
        )
        outfile.write("<!-- markdownlint-disable -->\n\n")
        outfile.write("# References\n\n")
        outfile.write(
            "| Linter | Version | License | Popularity | Descriptors | Ref | URL |\n"
        )
        outfile.write(
            "| :----  | :-----: | :-----: | :-----: | :---------  | :--------------: | :-: |\n"
        )
        for md_table_line in md_table_lines:
            outfile.write("| %s |\n" % " | ".join(md_table_line))


# Generate page of MegaLinter public repositories users
def generate_documentation_all_users():
    with open(USERS_FILE, "r", encoding="utf-8") as json_file:
        megalinter_users = json.load(json_file)
    repositories = megalinter_users["repositories"]
    linter_doc_md = [
        "# They use MegaLinter",
        "",
        "Here is a non-exhaustive list of open-source projects that use Megalinter",
        "",
        "According to posted issues, there are many more private and self-hosted "
        "repos using MegaLinter but as we don't track them I can't provide a list :)",
        "",
    ]
    for repo in repositories:
        if "info" in repo:
            repo_full = repo["info"]["full_name"]
        elif "repo_url" in repo and "https://github.com/" in repo["repo_url"]:
            repo_full = repo["repo_url"].replace("https://github.com/", "")
        else:
            continue
        # pylint: disable=no-member
        linter_doc_md += [
            f"[![{repo_full} - GitHub](https://gh-card.dev/repos/{repo_full}.svg?fullname=)]"
            f"(https://github.com/{repo_full}){{target=_blank}}",
        ]
        # pylint: enable=no-member
    with open(f"{REPO_HOME}/docs/all_users.md", "w", encoding="utf-8") as file:
        file.write("\n".join(linter_doc_md) + "\n")
    logging.info(f"Generated {REPO_HOME}/docs/all_users.md")


def get_badges(
    linter,
    show_last_release=False,
    show_last_commit=False,
    show_commits_activity=False,
    show_contributors=False,
    show_downgraded_version=False,
):
    badges = []
    repo = get_github_repo(linter)

    if (hasattr(linter, "get") and linter.get("deprecated") is True) or (
        hasattr(linter, "deprecated") and linter.deprecated is True
    ):
        badges += ["![deprecated](https://shields.io/badge/-deprecated-red)"]
    if (
        show_downgraded_version
        and (hasattr(linter, "get") and linter.get("downgraded_version") is True)
        or (hasattr(linter, "downgraded_version") and linter.downgraded_version is True)
    ):
        badges += [
            "![downgraded version](https://shields.io/badge/-downgraded%20version-orange)"
        ]
    if repo is not None:
        badges += [
            f"[![GitHub stars](https://img.shields.io/github/stars/{repo}?cacheSeconds=3600)]"
            f"(https://github.com/{repo})"
        ]
    if (hasattr(linter, "get") and linter.get("is_formatter") is True) or (
        hasattr(linter, "is_formatter") and linter.is_formatter is True
    ):
        badges += ["![formatter](https://shields.io/badge/-format-yellow)"]
    elif (
        hasattr(linter, "get") and linter.get("cli_lint_fix_arg_name") is not None
    ) or (
        hasattr(linter, "cli_lint_fix_arg_name")
        and linter.cli_lint_fix_arg_name is not None
    ):
        badges += ["![autofix](https://shields.io/badge/-autofix-green)"]
    if (hasattr(linter, "get") and linter.get("can_output_sarif") is True) or (
        hasattr(linter, "can_output_sarif") and linter.can_output_sarif is True
    ):
        badges += ["![sarif](https://shields.io/badge/-SARIF-orange)"]

    if show_last_release and repo is not None:
        badges += [
            f"[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/{repo}?sort=semver)]"
            f"(https://github.com/{repo}/releases)"
        ]
    if show_last_commit and repo is not None:
        badges += [
            f"[![GitHub last commit](https://img.shields.io/github/last-commit/{repo})]"
            f"(https://github.com/{repo}/commits)"
        ]
    if show_commits_activity and repo is not None:
        badges += [
            f"[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/{repo})]"
            f"(https://github.com/{repo}/graphs/commit-activity/)"
        ]
    if show_contributors and repo is not None:
        badges += [
            f"[![GitHub contributors](https://img.shields.io/github/contributors/{repo})]"
            f"(https://github.com/{repo}/graphs/contributors/)"
        ]
    return badges


# get github repo info using api
def get_github_repo_info(repo):
    api_github_url = f"https://api.github.com/repos/{repo}"
    api_github_headers = {"content-type": "application/json"}
    if "GITHUB_TOKEN" in os.environ:
        github_token = os.environ["GITHUB_TOKEN"]
        api_github_headers["authorization"] = f"Bearer {github_token}"
    logging.info(f"Getting repo info for {api_github_url}")
    session = requests_retry_session()
    r = session.get(api_github_url, headers=api_github_headers)
    if r is not None:
        # Update license key for licenses file
        resp = r.json()
        if resp is not None and not isinstance(resp, type(None)):
            return resp
    return {}


# Refresh github users info
def refresh_users_info():
    with open(USERS_FILE, "r", encoding="utf-8") as json_file:
        megalinter_users = json.load(json_file)
    repositories = megalinter_users["repositories"]
    updated_repositories = []
    for repo_item in repositories:
        # get stargazers from github api
        if repo_item["repo_url"] and repo_item["repo_url"].startswith(
            "https://github.com"
        ):
            repo = repo_item["repo_url"].split("https://github.com/", 1)[1]
            resp = get_github_repo_info(repo)
            if "stargazers_count" in resp:
                repo_item["stargazers"] = resp["stargazers_count"]
                repo_item["info"] = resp
        updated_repositories += [repo_item]
    updated_repositories.sort(
        key=lambda x: x["stargazers"] if "stargazers" in x else 0, reverse=True
    )
    megalinter_users["repositories"] = updated_repositories
    with open(USERS_FILE, "w", encoding="utf-8") as outfile:
        json.dump(megalinter_users, outfile, indent=4, sort_keys=True)
        outfile.write("\n")


def get_github_repo(linter):
    if (
        hasattr(linter, "get")
        and linter.get("linter_repo") is not None
        and linter.get("linter_repo").startswith("https://github.com")
    ):
        repo = linter.get("linter_repo").split("https://github.com/", 1)[1]
        return repo
    elif (
        hasattr(linter, "linter_repo")
        and linter.linter_repo is not None
        and linter.linter_repo.startswith("https://github.com")
    ):
        repo = linter.linter_repo.split("https://github.com/", 1)[1]
        return repo
    return None


def manage_output_variables():
    if os.environ.get("UPGRADE_LINTERS_VERSION", "") == "true":
        updated_files = megalinter.utils.list_updated_files("..")
        updated_versions = 0
        for updated_file in updated_files:
            updated_file_clean = megalinter.utils.normalize_log_string(updated_file)
            if os.path.basename(updated_file_clean) == "linter-versions.json":
                updated_versions = 1
                break
        if updated_versions == 1:
            if "GITHUB_OUTPUT" in os.environ:
                github_output_file = os.environ["GITHUB_OUTPUT"]
                if not os.path.isfile(github_output_file):
                    github_output_file = github_output_file.replace(
                        "/home/runner/work/_temp/_runner_file_commands",
                        "/github/file_commands",
                    )
                with open(github_output_file, "a", encoding="utf-8") as output_stream:
                    output_stream.write("has_updated_versions=1\n")


def reformat_markdown_tables():
    logging.info("Formatting markdown tables…")
    # Call markdown-table-formatter with the list of files
    if sys.platform == "win32":
        format_md_tables_command = ["bash", "format-tables.sh"]
    else:
        format_md_tables_command = ["./format-tables.sh"]
    cwd = os.getcwd() + "/.automation"
    logging.info("Running command: " + str(format_md_tables_command) + f" in cwd {cwd}")
    process = subprocess.run(
        format_md_tables_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=cwd,
        shell=True,
        executable=None if sys.platform == "win32" else which("bash"),
    )
    stdout = utils.decode_utf8(process.stdout)
    logging.info(f"Format table results: ({process.returncode})\n" + stdout)


def generate_version():
    # npm version
    logging.info("Updating npm package version…")
    cwd_to_use = os.getcwd() + "/mega-linter-runner"
    process = subprocess.run(
        [
            "npm",
            "version",
            "--newversion",
            RELEASE_TAG,
            "-no-git-tag-version",
            "--no-commit-hooks",
        ],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd_to_use,
        shell=True,
    )
    print(process.stdout)
    print(process.stderr)
    # Update python project version:
    process = subprocess.run(
        ["hatch", "version", RELEASE_TAG],
        stdout=subprocess.PIPE,
        text=True,
        shell=True,
        check=False,
    )
    # Update changelog
    if UPDATE_CHANGELOG is True:
        changelog_file = f"{REPO_HOME}/CHANGELOG.md"
        with open(changelog_file, "r", encoding="utf-8") as md_file:
            changelog_content = md_file.read()
        changelog_content = changelog_content.replace(
            "<!-- linter-versions-end -->", ""
        )
        new_release_lines = [
            "," "<!-- unreleased-content-marker -->",
            "",
            "- Linter versions upgrades",
            "<!-- linter-versions-end -->",
            "",
            f"## [{RELEASE_TAG}] - {datetime.today().strftime('%Y-%m-%d')}",
        ]
        changelog_content = changelog_content.replace(
            "<!-- unreleased-content-marker -->", "\n".join(new_release_lines)
        )
        with open(changelog_file, "w", encoding="utf-8") as file:
            file.write(changelog_content)

    # git add , commit & tag
    repo = git.Repo(os.getcwd())
    repo.git.add(update=True)
    repo.git.commit("-m", "Release MegaLinter " + RELEASE_TAG)
    repo.create_tag(RELEASE_TAG)


def update_dependents_info():
    logging.info("Updating dependents info…")
    command = [
        "github-dependents-info",
        "--repo",
        "oxsecurity/megalinter",
        "--markdownfile",
        "./docs/used-by-stats.md",
        "--badgemarkdownfile",
        "README.md",
        "--mergepackages",
        "--sort",
        "stars",
        "--verbose",
    ]
    logging.info("Running command: " + " ".join(command))
    os.system(" ".join(command))


def update_workflows_linters():
    descriptors, _ = list_descriptors_for_build()

    linters = ""

    for descriptor in descriptors:
        for linter in descriptor["linters"]:
            if "disabled" in linter and linter["disabled"] is True:
                continue
            if "name" in linter:
                name = linter["name"].lower()
            else:
                lang_lower = descriptor["descriptor_id"].lower()
                linter_name_lower = linter["linter_name"].lower().replace("-", "_")
                name = f"{lang_lower}_{linter_name_lower}"

            linters += f'            "{name}",\n'

    update_workflow_linters(".github/workflows/deploy-DEV-linters.yml", linters)
    update_workflow_linters(".github/workflows/deploy-BETA-linters.yml", linters)
    update_workflow_linters(".github/workflows/deploy-RELEASE-linters.yml", linters)


def update_workflow_linters(file_path, linters):
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        file_content = re.sub(
            r"(linter:\s+\[\s*)([^\[\]]*?)(\s*\])",
            rf"\1{re.escape(linters).replace(chr(92), '').strip()}\3",
            file_content,
        )

    with open(file_path, "w") as f:
        f.write(file_content)


if __name__ == "__main__":
    logging_format = (
        "[%(levelname)s] %(message)s"
        if "CI" in os.environ
        else "%(asctime)s [%(levelname)s] %(message)s"
    )
    try:
        logging.basicConfig(
            force=True,
            level=logging.INFO,
            format=logging_format,
            handlers=[logging.StreamHandler(sys.stdout)],
        )
    except ValueError:
        logging.basicConfig(
            level=logging.INFO,
            format=logging_format,
            handlers=[logging.StreamHandler(sys.stdout)],
        )
    config.init_config("build")
    # noinspection PyTypeChecker
    collect_linter_previews()
    generate_json_schema_enums()
    validate_descriptors()
    if UPDATE_DEPENDENTS is True:
        update_dependents_info()
    generate_all_flavors()
    generate_linter_dockerfiles()
    generate_linter_test_classes()
    update_workflows_linters()
    if UPDATE_DOC is True:
        logging.info("Running documentation generators…")
        # refresh_users_info() # deprecated since now we use github-dependents-info
        generate_documentation()
        generate_documentation_all_linters()
        # generate_documentation_all_users() # deprecated since now we use github-dependents-info
        generate_mkdocs_yml()
    validate_own_megalinter_config()
    manage_output_variables()
    reformat_markdown_tables()
    if RELEASE is True:
        generate_version()
