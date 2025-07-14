# !/usr/bin/env python3
"""
Build constants and global variables for MegaLinter build system
"""
import os
import re
import sys

from megalinter.constants import (
    DEFAULT_DOCKERFILE_APK_PACKAGES,
    DEFAULT_DOCKERFILE_ARGS,
    DEFAULT_DOCKERFILE_DOCKER_APK_PACKAGES,
    DEFAULT_DOCKERFILE_DOCKER_ARGS,
    DEFAULT_DOCKERFILE_FLAVOR_ARGS,
    DEFAULT_DOCKERFILE_FLAVOR_CARGO_PACKAGES,
    DEFAULT_DOCKERFILE_GEM_APK_PACKAGES,
    DEFAULT_DOCKERFILE_GEM_ARGS,
    DEFAULT_DOCKERFILE_NPM_APK_PACKAGES,
    DEFAULT_DOCKERFILE_NPM_ARGS,
    DEFAULT_DOCKERFILE_PIP_ARGS,
    DEFAULT_DOCKERFILE_PIPENV_ARGS,
    DEFAULT_DOCKERFILE_RUST_ARGS,
    DEFAULT_RELEASE,
    DEFAULT_REPORT_FOLDER_NAME,
    ML_DOC_URL_BASE,
    ML_DOCKER_IMAGE,
    ML_DOCKER_IMAGE_LEGACY,
    ML_DOCKER_IMAGE_LEGACY_V5,
    ML_REPO,
    ML_REPO_URL,
)

# Command line argument parsing
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

# Latest management
if IS_LATEST is True:
    VERSION_URL_SEGMENT = "latest"
else:
    VERSION_URL_SEGMENT = VERSION

# URL construction
MKDOCS_URL_ROOT = ML_DOC_URL_BASE + VERSION_URL_SEGMENT
BRANCH = "main"
URL_ROOT = ML_REPO_URL + "/tree/" + BRANCH
URL_RAW_ROOT = ML_REPO_URL + "/raw/" + BRANCH
TEMPLATES_URL_ROOT = URL_ROOT + "/TEMPLATES"
DOCS_URL_ROOT = URL_ROOT + "/docs"
DOCS_URL_DESCRIPTORS_ROOT = DOCS_URL_ROOT + "/descriptors"
DOCS_URL_FLAVORS_ROOT = DOCS_URL_ROOT + "/flavors"
DOCS_URL_RAW_ROOT = URL_RAW_ROOT + "/docs"

# Path construction
REPO_HOME = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
REPO_ICONS = REPO_HOME + "/docs/assets/icons"
REPO_IMAGES = REPO_HOME + "/docs/assets/images"

# File paths
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

# Shield/badge URLs
BASE_SHIELD_IMAGE_LINK = "https://img.shields.io/docker/image-size"
BASE_SHIELD_COUNT_LINK = "https://img.shields.io/docker/pulls"

# Schema files
DESCRIPTOR_JSON_SCHEMA = (
    f"{REPO_HOME}/megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json"
)
CONFIG_JSON_SCHEMA = f"{REPO_HOME}/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json"
OWN_MEGALINTER_CONFIG_FILE = f"{REPO_HOME}/.mega-linter.yml"

# IDE definitions
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

# Deprecated linters list
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
    "MARKDOWN_MARKDOWN_LINK_CHECK",  # Removed in v9
]

# Cache for descriptors
DESCRIPTORS_FOR_BUILD_CACHE = None

# Main Dockerfile path and Alpine version parsing
MAIN_DOCKERFILE = f"{REPO_HOME}/Dockerfile"
ALPINE_VERSION = ""
MAIN_DOCKERFILE_ARGS_MAP = {}

with open(MAIN_DOCKERFILE, "r", encoding="utf-8") as main_dockerfile_file:
    main_dockerfile_content = main_dockerfile_file.read()

    match = re.search(r"FROM python:.*-alpine(\d+.\d+.?\d+)", main_dockerfile_content)
    if match:
        ALPINE_VERSION = match.group(1)

    matches = re.finditer(r"ARG (.*)=(.*)", main_dockerfile_content)
    for match in matches:
        MAIN_DOCKERFILE_ARGS_MAP[match.group(1)] = match.group(2)

# Re-export constants from megalinter.constants for convenience
__all__ = [
    "DEFAULT_DOCKERFILE_APK_PACKAGES",
    "DEFAULT_DOCKERFILE_ARGS", 
    "DEFAULT_DOCKERFILE_DOCKER_APK_PACKAGES",
    "DEFAULT_DOCKERFILE_DOCKER_ARGS",
    "DEFAULT_DOCKERFILE_FLAVOR_ARGS",
    "DEFAULT_DOCKERFILE_FLAVOR_CARGO_PACKAGES",
    "DEFAULT_DOCKERFILE_GEM_APK_PACKAGES",
    "DEFAULT_DOCKERFILE_GEM_ARGS",
    "DEFAULT_DOCKERFILE_NPM_APK_PACKAGES",
    "DEFAULT_DOCKERFILE_NPM_ARGS", 
    "DEFAULT_DOCKERFILE_PIP_ARGS",
    "DEFAULT_DOCKERFILE_PIPENV_ARGS",
    "DEFAULT_DOCKERFILE_RUST_ARGS",
    "DEFAULT_RELEASE",
    "DEFAULT_REPORT_FOLDER_NAME",
    "ML_DOC_URL_BASE",
    "ML_DOCKER_IMAGE",
    "ML_DOCKER_IMAGE_LEGACY", 
    "ML_DOCKER_IMAGE_LEGACY_V5",
    "ML_REPO",
    "ML_REPO_URL",
    "RELEASE",
    "UPDATE_STATS",
    "UPDATE_DOC",
    "UPDATE_DEPENDENTS",
    "UPDATE_CHANGELOG",
    "IS_LATEST",
    "DELETE_DOCKERFILES",
    "DELETE_TEST_CLASSES",
    "VERSION",
    "VERSION_V",
    "VERSION_URL_SEGMENT",
    "MKDOCS_URL_ROOT",
    "BRANCH",
    "URL_ROOT",
    "URL_RAW_ROOT",
    "TEMPLATES_URL_ROOT",
    "DOCS_URL_ROOT",
    "DOCS_URL_DESCRIPTORS_ROOT",
    "DOCS_URL_FLAVORS_ROOT",
    "DOCS_URL_RAW_ROOT",
    "REPO_HOME",
    "REPO_ICONS",
    "REPO_IMAGES",
    "VERSIONS_FILE",
    "LICENSES_FILE",
    "USERS_FILE",
    "HELPS_FILE",
    "LINKS_PREVIEW_FILE",
    "DOCKER_STATS_FILE",
    "PLUGINS_FILE",
    "FLAVORS_DIR",
    "LINTERS_DIR",
    "GLOBAL_FLAVORS_FILE",
    "BASE_SHIELD_IMAGE_LINK",
    "BASE_SHIELD_COUNT_LINK",
    "DESCRIPTOR_JSON_SCHEMA",
    "CONFIG_JSON_SCHEMA",
    "OWN_MEGALINTER_CONFIG_FILE",
    "IDE_LIST",
    "DEPRECATED_LINTERS",
    "DESCRIPTORS_FOR_BUILD_CACHE",
    "MAIN_DOCKERFILE",
    "ALPINE_VERSION",
    "MAIN_DOCKERFILE_ARGS_MAP",
]
