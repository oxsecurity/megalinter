#!/usr/bin/env python3
"""
Template class for custom linters: any linter class in /linters folder must inherit from this class
The following list of items can/must be overridden on custom linter local class:
- field descriptor_id (required) ex: "JAVASCRIPT"
- field name (optional) ex: "JAVASCRIPT_ES". If not set, language value is used
- field linter_name (required) ex: "eslint"
- field linter_url (required) ex: "https://eslint.org/"
- field test_folder (optional) ex: "docker". If not set, language.lowercase() value is used
- field config_file_name (optional) ex: ".eslintrc.yml". If not set, no default config file will be searched
- field file_extensions (optional) ex: [".js"]. At least file_extension or file_names_regex must be set
- field file_names_regex (optional) ex: ["Dockerfile(-.+)?"]. At least file_extension or file_names_regex must be set
- method build_lint_command (optional) : Return CLI command to lint a file with the related linter
                                         Default: linter_name + (if config_file(-c + config_file)) + config_file
- method build_version_command (optional): Returns CLI command to get the related linter version.
                                           Default: linter_name --version
- method build_extract_version_regex (optional): Returns RegEx to extract version from version command output
                                                 Default: "\\d+(\\.\\d+)+"

"""
import errno
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from time import perf_counter

import yaml
from megalinter import config, pre_post_factory, utils, utils_reporter, utils_sarif
from megalinter.constants import DEFAULT_DOCKER_WORKSPACE_DIR


class Linter:
    TEMPLATES_DIR = "/action/lib/.automation/"

    # Constructor: Initialize Linter instance with name and config variables
    def __init__(self, params=None, linter_config=None):
        self.linter_version_cache = None
        self.linter_help_cache = None
        self.processing_order = 0
        self.master = None
        self.request_id = None
        # Definition fields & default values: can be overridden at custom linter class level or in YML descriptors
        # Ex: JAVASCRIPT
        self.descriptor_id = (
            "Field 'descriptor_id' must be overridden at custom linter class level"
        )
        # If you have several linters for the same language,override with a different name.Ex: JAVASCRIPT_ES
        self.name = None
        self.disabled = False
        self.disabled_reason = None
        self.is_formatter = False
        self.is_sbom = False
        self.linter_name = "Field 'linter_name' must be overridden at custom linter class level"  # Ex: eslint
        self.linter_speed = 3
        self.can_output_sarif = False
        self.output_sarif = False
        # ex: https://eslint.org/
        self.linter_url = (
            "Field 'linter_url' must be overridden at custom linter class level"
        )
        self.linter_icon_png_url = None
        self.test_folder = None  # Override only if different from language.lowercase()
        self.test_format_fix_file_extensions = []
        self.test_format_fix_regex_exclude = None
        self.activation_rules = []
        self.test_variables = {}
        # Array of strings defining file extensions. Ex: ['.js','.cjs', '']
        self.file_extensions = []
        # Array of file name regular expressions. Ex: [Dockerfile(-.+)?]
        self.file_names_regex = []
        # Default name of the configuration file to use with the linter. Ex: '.eslintrc.js'
        self.config_file_name = None
        self.final_config_file = None
        # Ignore file name and arg
        self.ignore_file_name = None
        self.cli_lint_ignore_arg_name = None
        self.final_ignore_file = None
        # Other
        self.files_sub_directory = None
        self.file_contains_regex = []
        self.file_contains_regex_extensions = []
        self.file_names_not_ends_with = []
        self.active_only_if_file_found = []
        self.lint_all_files = False
        self.lint_all_other_linters_files = False
        self.is_plugin = False
        self.pre_commands = None
        self.post_commands = None
        self.unsecured_env_variables = []
        self.ignore_for_flavor_suggestions = False

        self.cli_lint_mode = "file"
        self.cli_docker_image = None
        self.cli_docker_image_version = "latest"
        self.cli_docker_args = []
        self.cli_executable = []
        self.cli_executable_fix = []
        self.cli_executable_version = []
        self.cli_executable_help = []
        # Default arg name for configurations to use in linter CLI call
        self.cli_config_arg_name = "-c"
        self.cli_config_default_value = None
        self.cli_config_extra_args = (
            []
        )  # Extra arguments to send to cli when a config file is used
        self.cli_sarif_args = []
        self.sarif_output_file = None
        self.sarif_default_output_file = None
        self.no_config_if_fix = False
        self.cli_lint_extra_args = []  # Extra arguments to send to cli everytime
        self.cli_command_remove_args = (
            []
        )  # Arguments to remove in case fix argument is sent
        # Name of the cli argument to send in case of APPLY_FIXES required by user
        self.cli_lint_fix_arg_name = None
        self.cli_lint_fix_remove_args = (
            []
        )  # Arguments to remove in case fix argument is sent
        self.cli_lint_user_args = (
            []
        )  # Arguments from config, defined in <LINTER_KEY>_ARGUMENTS variable
        # Extra arguments to send to cli everytime, just before file argument
        self.cli_lint_extra_args_after = []
        self.cli_lint_errors_count = None
        self.cli_lint_errors_regex = None
        self.cli_lint_warnings_count = None
        self.cli_lint_warnings_regex = None
        # Default arg name for configurations to use in linter version call
        self.cli_version_arg_name = "--version"
        self.cli_version_extra_args = []  # Extra arguments to send to cli everytime
        self.cli_help_arg_name = "-h"
        self.cli_help_extra_args = []  # Extra arguments to send to cli everytime
        self.cli_help_extra_commands = []
        # If linter --help doesn't return 0 when it's in success, override. ex: 1
        self.help_command_return_code = 0
        self.version_extract_regex = r"\d+(\.\d+)+"
        # If linter --version doesn't return 0 when it's in success, override. ex: 1
        self.version_command_return_code = 0

        self.log_lines_pre: list(str) = []
        self.log_lines_post: list(str) = []

        self.report_folder = ""
        self.reporters = []
        self.lint_command_log: list(str) = []

        # Initialize parameters
        default_params = {
            "default_linter_activation": False,
            "enable_descriptors": [],
            "enable_linters": [],
            "disable_descriptors": [],
            "disable_linters": [],
            "enable_errors_linters": [],
            "disable_errors_linters": [],
            "post_linter_status": True,
        }
        if params is None:
            params = default_params
        else:
            params = {**default_params, **params}

        # Initialize with configuration data
        for key, value in linter_config.items():
            self.__setattr__(key, value)
        if "request_id" in params:
            self.request_id = params["request_id"]
        elif self.master is not None:
            self.request_id: str = self.master.request_id
        elif "master" in params:
            self.request_id: str = params["master"].request_id
        else:
            raise Exception("Missing megalinter request_id")

        self.is_active = (
            False
            if "default_linter_activation" not in params
            else params["default_linter_activation"]
        )
        # Disable errors
        self.disable_errors_if_less_than = None
        self.disable_errors = (
            True
            if self.is_formatter is True
            and not config.get(self.request_id, "FORMATTERS_DISABLE_ERRORS", "true")
            == "false"
            else (
                True
                if config.get(self.request_id, "DISABLE_ERRORS", "false") == "true"
                else False
            )
        )
        # Name
        if self.name is None:
            self.name = (
                self.descriptor_id + "_" + self.linter_name.upper().replace("-", "_")
            )
        # Sarif enablement
        self.output_sarif = (
            params["output_sarif"]
            if "output_sarif" in params and self.can_output_sarif is True
            else self.output_sarif
        )
        if self.output_sarif is True:
            # Disable SARIF if linter not in specified linter list
            sarif_enabled_linters = config.get_list(
                self.request_id, "SARIF_REPORTER_LINTERS", None
            )
            if (
                sarif_enabled_linters is not None
                and self.name not in sarif_enabled_linters
            ):
                self.output_sarif = False
        # Use linter_name if the descriptor does not force another executable
        if len(self.cli_executable) == 0:
            self.cli_executable = [self.linter_name]
        else:
            self.cli_executable = [self.cli_executable]
        # Override default executable
        if config.exists(self.request_id, self.name + "_CLI_EXECUTABLE"):
            self.cli_executable = config.get_list(
                self.request_id, self.name + "_CLI_EXECUTABLE"
            )
        if len(self.cli_executable_fix) == 0:
            self.cli_executable_fix = [*self.cli_executable]
        else:
            self.cli_executable_fix = [self.cli_executable_fix]
        if len(self.cli_executable_version) == 0:
            self.cli_executable_version = [*self.cli_executable]
        else:
            self.cli_executable_version = [self.cli_executable_version]
        if len(self.cli_executable_help) == 0:
            self.cli_executable_help = [*self.cli_executable]
        else:
            self.cli_executable_help = [self.cli_executable_help]
        if self.test_folder is None:
            self.test_folder = self.descriptor_id.lower()

        # Apply linter customization via config settings:
        self.file_extensions = config.get_list(
            self.request_id, self.name + "_FILE_EXTENSIONS", self.file_extensions
        )
        self.file_names_regex = config.get_list(
            self.request_id, self.name + "_FILE_NAMES_REGEX", self.file_names_regex
        )

        self.manage_activation(params)

        if self.is_active is True:
            self.show_elapsed_time = params.get("show_elapsed_time", False)

            self.manage_apply_fixes(params)

            # Disable lint_all_other_linters_files=true if we are in a standalone linter docker image,
            # because there are no other linters
            if (
                self.lint_all_other_linters_files is True
                and config.get(self.request_id, "SINGLE_LINTER", "") != ""
            ):
                self.lint_all_other_linters_files = False

            # Config items
            self.linter_rules_path = (
                params["linter_rules_path"] if "linter_rules_path" in params else "."
            )
            self.default_rules_location = (
                params["default_rules_location"]
                if "default_rules_location" in params
                else "."
            )
            self.workspace = params["workspace"] if "workspace" in params else "."
            self.github_workspace = (
                params["github_workspace"] if "github_workspace" in params else "."
            )
            self.config_file = None
            self.config_file_label = None
            self.config_file_error = None
            self.ignore_file = None
            self.ignore_file_label = None
            self.ignore_file_error = None
            self.filter_regex_include = None
            self.filter_regex_exclude_descriptor = None
            self.filter_regex_exclude_linter = None
            self.post_linter_status = (
                params["post_linter_status"]
                if "post_linter_status" in params
                else False
            )
            self.github_api_url = (
                params["github_api_url"] if "github_api_url" in params else None
            )

            self.report_types = (
                params["report_types"] if "report_types" in params else []
            )
            self.report_folder = (
                params["report_folder"] if "report_folder" in params else ""
            )

            self.load_config_vars(params)

            # Manage sub-directory filter if defined
            if self.files_sub_directory is not None:
                self.files_sub_directory = config.get(
                    self.request_id,
                    f"{self.descriptor_id}_DIRECTORY",
                    self.files_sub_directory,
                )
                if self.files_sub_directory == "any":
                    logging.info(
                        f'[Activation] {self.name} skip check of directory as value set to "any"'
                    )
                elif not os.path.isdir(
                    self.workspace + os.path.sep + self.files_sub_directory
                ):
                    self.is_active = False
                    logging.info(
                        f"[Activation] {self.name} has been set inactive, as subdirectory has not been found:"
                        f' {self.files_sub_directory} (set value "any" to always activate)'
                    )

            # Some linters require a file to be existing, else they're deactivated ( ex: .editorconfig )
            if len(self.active_only_if_file_found) > 0:
                is_found = False
                for file_to_check in self.active_only_if_file_found:
                    found_file = None
                    prop = None
                    if ":" in file_to_check:
                        file_to_check, prop = file_to_check.split(":")
                    if os.path.isfile(f"{self.workspace}{os.path.sep}{file_to_check}"):
                        found_file = f"{self.workspace}{os.path.sep}{file_to_check}"
                    elif os.path.isfile(
                        f"{self.workspace}{os.path.sep}{self.linter_rules_path}{os.path.sep}{file_to_check}"
                    ):
                        found_file = (
                            f"{self.workspace}{os.path.sep}{self.linter_rules_path}"
                            + f"{os.path.sep}{file_to_check}"
                        )
                    elif os.path.isfile(
                        f"{self.workspace}{os.path.sep}{self.files_sub_directory}{os.path.sep}{file_to_check}"
                    ):
                        found_file = (
                            f"{self.workspace}{os.path.sep}{self.files_sub_directory}"
                            + f"{os.path.sep}{file_to_check}"
                        )
                    # filename case
                    if found_file is not None and prop is None:
                        is_found = True
                        break
                    # filename + prop case
                    if found_file is not None and prop is not None:
                        with open(found_file, "r", encoding="utf-8") as json_file:
                            found_file_content = json.load(json_file)
                        if prop in found_file_content:
                            is_found = True
                            break
                if is_found is False:
                    self.is_active = False
                    logging.info(
                        f"[Activation] {self.name} has been set inactive, as none of these files has been found:"
                        f" {str(self.active_only_if_file_found)}"
                    )

            # Load MegaLinter reporters
            self.load_reporters()

            # Runtime items
            self.files = []
            self.try_fix = False
            self.status = "success"
            self.stdout = None
            self.stdout_human = None
            self.return_code = 0
            self.number_errors = 0
            self.total_number_errors = 0
            self.total_number_warnings = 0
            self.number_fixed = 0
            self.files_lint_results = []
            self.start_perf = None
            self.elapsed_time_s = 0
            self.remote_config_file_to_delete = None
            self.remote_ignore_file_to_delete = None

    # Enable or disable linter
    def manage_activation(self, params):
        strategies = {
            "ENABLE": False,
            "ENABLE_LINTERS": False,
            "DISABLE": False,
            "DISABLE_LINTERS": False,
            "VALIDATE": False,
            "VALIDATE_LINTERS": False,
        }

        # Default value is false in case ENABLE variables are used
        # See megalinter/MegaLinter.py, manage_default_linter_activation() function
        # for params["default_linter_activation"]
        self.is_active = params["default_linter_activation"]
        # Activate or not the linter
        if self.name in params["enable_linters"]:
            self.is_active = True
            strategies["ENABLE_LINTERS"] = True
        elif self.name in params["disable_linters"]:
            self.is_active = False
            strategies["DISABLE_LINTERS"] = True
        elif self.descriptor_id in params["disable_descriptors"]:
            self.is_active = False
            strategies["DISABLE"] = True
        elif self.name in params["disable_linters"]:
            self.is_active = False
            strategies["DISABLE_LINTERS"] = True
        elif self.descriptor_id in params["enable_descriptors"]:
            self.is_active = True
            strategies["ENABLE"] = True
        elif (
            config.exists(self.request_id, "VALIDATE_" + self.name)
            and config.get(self.request_id, "VALIDATE_" + self.name) == "false"
        ):
            self.is_active = False
            strategies["VALIDATE_LINTERS"] = True
        elif (
            config.exists(self.request_id, "VALIDATE_" + self.descriptor_id)
            and config.get(self.request_id, "VALIDATE_" + self.descriptor_id) == "false"
        ):
            self.is_active = False
            strategies["VALIDATE"] = True
        elif (
            config.exists(self.request_id, "VALIDATE_" + self.name)
            and config.get(self.request_id, "VALIDATE_" + self.name) == "true"
        ):
            self.is_active = True
            strategies["VALIDATE_LINTERS"] = True
        elif (
            config.exists(self.request_id, "VALIDATE_" + self.descriptor_id)
            and config.get(self.request_id, "VALIDATE_" + self.descriptor_id) == "true"
        ):
            self.is_active = True
            strategies["VALIDATE"] = True
        # check activation rules
        if self.is_active is True and len(self.activation_rules) > 0:
            self.is_active = utils.check_activation_rules(self.activation_rules, self)

        strategiesUsed = format(
            ", ".join("{0}".format(k) for k, v in strategies.items() if v)
        )

        if not strategiesUsed:
            strategiesUsed = "default"

        if self.is_active:
            logging.debug(
                f"[Activation] + {self.name} ({self.descriptor_id}) was activated by {strategiesUsed} strategies"
            )
        else:
            logging.debug(
                f"[Activation] - {self.name} ({self.descriptor_id}) was not activated by {strategiesUsed} strategies"
            )

    # Manage apply fixes flag on linter
    def manage_apply_fixes(self, params):
        self.apply_fixes = False

        param_apply_fixes = params.get("apply_fixes", "none")

        # APPLY_FIXES is "all"
        if param_apply_fixes == "all" or (
            isinstance(param_apply_fixes, bool) and param_apply_fixes is True
        ):
            self.apply_fixes = True
        # APPLY_FIXES is a comma-separated list in a single string
        elif (
            param_apply_fixes != "none"
            and isinstance(param_apply_fixes, str)
            and self.name in param_apply_fixes.split(",")
        ):
            self.apply_fixes = True
        # APPLY_FIXES is a list of strings
        elif (
            param_apply_fixes != "none"
            and isinstance(param_apply_fixes, list)
            and (self.name in param_apply_fixes or param_apply_fixes[0] == "all")
        ):
            self.apply_fixes = True
        else:
            self.apply_fixes = False

        if self.apply_fixes:
            logging.debug(
                f"[Apply Fixes] is enabled for + {self.name} ({self.descriptor_id})"
            )
        else:
            logging.debug(
                f"[Apply Fixes] is disabled for + {self.name} ({self.descriptor_id})"
            )

    # Manage configuration variables
    def load_config_vars(self, params):
        # Configuration file name: try first NAME + _FILE_NAME, then LANGUAGE + _FILE_NAME
        # _CONFIG_FILE = _FILE_NAME (config renaming but keeping config ascending compatibility)
        if config.exists(self.request_id, self.name + "_CONFIG_FILE"):
            self.config_file_name = config.get(
                self.request_id, self.name + "_CONFIG_FILE"
            )
            self.update_active_if_file_found()
        elif config.exists(self.request_id, self.descriptor_id + "_CONFIG_FILE"):
            self.config_file_name = config.get(
                self.request_id, self.descriptor_id + "_CONFIG_FILE"
            )
            self.update_active_if_file_found()
        elif config.exists(self.request_id, self.name + "_FILE_NAME"):
            self.config_file_name = config.get(
                self.request_id, self.name + "_FILE_NAME"
            )
            self.update_active_if_file_found()
        elif config.exists(self.request_id, self.descriptor_id + "_FILE_NAME"):
            self.config_file_name = config.get(
                self.request_id, self.descriptor_id + "_FILE_NAME"
            )
            self.update_active_if_file_found()
        # Ignore file name: try first NAME + _FILE_NAME, then LANGUAGE + _FILE_NAME
        if self.cli_lint_ignore_arg_name is not None:
            if config.exists(self.request_id, self.name + "_IGNORE_FILE"):
                self.ignore_file_name = config.get(
                    self.request_id, self.name + "_IGNORE_FILE"
                )
            elif config.exists(self.request_id, self.descriptor_id + "_IGNORE_FILE"):
                self.ignore_file_name = config.get(
                    self.request_id, self.descriptor_id + "_IGNORE_FILE"
                )
        # Linter rules path: try first NAME + _RULE_PATH, then LANGUAGE + _RULE_PATH
        if config.exists(self.request_id, self.name + "_RULES_PATH"):
            self.linter_rules_path = config.get(
                self.request_id, self.name + "_RULES_PATH"
            )
        elif config.exists(self.request_id, self.descriptor_id + "_RULES_PATH"):
            self.linter_rules_path = config.get(
                self.request_id, self.descriptor_id + "_RULES_PATH"
            )
        # Linter config file:
        # 0: LINTER_DEFAULT set in user config: let the linter find it, don't reference it in cli arguments
        # 1: http rules path: fetch remove file and copy it locally (then delete it after linting)
        # 2: repo + config_file_name
        # 3: linter_rules_path + config_file_name
        # 4: workspace root + linter_rules_path + config_file_name
        # 5: mega-linter default rules path + config_file_name
        if (
            self.config_file_name is not None
            and self.config_file_name != "LINTER_DEFAULT"
        ):
            if self.linter_rules_path.startswith("http"):
                if not self.linter_rules_path.endswith("/"):
                    self.linter_rules_path += "/"
                remote_config_file = self.linter_rules_path + self.config_file_name
                local_config_file = self.workspace + os.path.sep + self.config_file_name
                existing_before = os.path.isfile(local_config_file)
                try:
                    with (
                        urllib.request.urlopen(remote_config_file) as response,
                        open(local_config_file, "wb") as out_file,
                    ):
                        shutil.copyfileobj(response, out_file)
                        self.config_file_label = remote_config_file
                        if existing_before is False:
                            self.remote_config_file_to_delete = local_config_file
                except urllib.error.HTTPError as e:
                    self.config_file_error = (
                        f"Unable to fetch {remote_config_file}\n{str(e)}\n"
                        f" fallback to repository config or MegaLinter default config"
                    )
                except Exception as e:
                    self.config_file_error = (
                        f"Unable to fetch {remote_config_file}\n{str(e)}\n"
                        f" fallback to repository config or MegaLinter default config"
                    )
            # in repo root (already here or fetched by code above)
            if os.path.isfile(self.workspace + os.path.sep + self.config_file_name):
                self.config_file = self.workspace + os.path.sep + self.config_file_name
            # in user repo ./github/linters folder
            elif os.path.isfile(
                self.linter_rules_path + os.path.sep + self.config_file_name
            ):
                self.config_file = (
                    self.linter_rules_path + os.path.sep + self.config_file_name
                )
            # in workspace root
            elif os.path.isfile(
                self.workspace
                + os.path.sep
                + self.linter_rules_path
                + os.path.sep
                + self.config_file_name
            ):
                self.config_file = (
                    self.workspace
                    + os.path.sep
                    + self.linter_rules_path
                    + os.path.sep
                    + self.config_file_name
                )
            # in user repo directory provided in <Linter>RULES_PATH or LINTER_RULES_PATH
            elif os.path.isfile(
                self.default_rules_location + os.path.sep + self.config_file_name
            ):
                self.config_file = (
                    self.default_rules_location + os.path.sep + self.config_file_name
                )
            # Make config file path absolute if not located in workspace
            if self.config_file is not None and not os.path.isfile(
                self.workspace + os.path.sep + self.config_file
            ):
                self.config_file = os.path.abspath(self.config_file)
            # Set config file label if not set by remote rule
            if self.config_file is not None and self.config_file_label is None:
                self.config_file_label = self.config_file.replace(
                    DEFAULT_DOCKER_WORKSPACE_DIR, ""
                ).replace(self.TEMPLATES_DIR, "")

        # Linter ignore file:
        # 0: LINTER_DEFAULT set in user config: let the linter find it, don't reference it in cli arguments
        # 1: http rules path: fetch remove file and copy it locally (then delete it after linting)
        # 2: repo + ignore_file_name
        # 3: linter_rules_path + ignore_file_name
        # 4: workspace root + linter_rules_path + ignore_file_name
        # 5: mega-linter default rules path + ignore_file_name
        if (
            self.ignore_file_name is not None
            and self.ignore_file_name != "LINTER_DEFAULT"
        ):
            if self.linter_rules_path.startswith("http"):
                if not self.linter_rules_path.endswith("/"):
                    self.linter_rules_path += "/"
                remote_ignore_file = self.linter_rules_path + self.ignore_file_name
                local_ignore_file = self.workspace + os.path.sep + self.ignore_file_name
                existing_before = os.path.isfile(local_ignore_file)
                try:
                    with (
                        urllib.request.urlopen(remote_ignore_file) as response,
                        open(local_ignore_file, "wb") as out_file,
                    ):
                        shutil.copyfileobj(response, out_file)
                        self.ignore_file_label = remote_ignore_file
                        if existing_before is False:
                            self.remote_ignore_file_to_delete = local_ignore_file
                except urllib.error.HTTPError as e:
                    self.ignore_file_error = (
                        f"Unable to fetch {remote_ignore_file}\n{str(e)}\n"
                        f" fallback to repository config or MegaLinter default ignore file"
                    )
                except Exception as e:
                    self.ignore_file_error = (
                        f"Unable to fetch {remote_ignore_file}\n{str(e)}\n"
                        f" fallback to repository config or MegaLinter default ignore file"
                    )
            # in repo root (already here or fetched by code above)
            if os.path.isfile(self.workspace + os.path.sep + self.ignore_file_name):
                self.ignore_file = self.workspace + os.path.sep + self.ignore_file_name
            # in user repo ./github/linters folder
            elif os.path.isfile(
                self.linter_rules_path + os.path.sep + self.ignore_file_name
            ):
                self.ignore_file = (
                    self.linter_rules_path + os.path.sep + self.ignore_file_name
                )
            # in workspace root
            elif os.path.isfile(
                self.workspace
                + os.path.sep
                + self.linter_rules_path
                + os.path.sep
                + self.ignore_file_name
            ):
                self.ignore_file = (
                    self.workspace
                    + os.path.sep
                    + self.linter_rules_path
                    + os.path.sep
                    + self.ignore_file_name
                )
            # in user repo directory provided in <Linter>RULES_PATH or LINTER_RULES_PATH
            elif os.path.isfile(
                self.default_rules_location + os.path.sep + self.ignore_file_name
            ):
                self.ignore_file = (
                    self.default_rules_location + os.path.sep + self.ignore_file_name
                )
            # Set ignore file label if not set by remote rule
            if self.ignore_file is not None and self.ignore_file_label is None:
                self.ignore_file_label = self.ignore_file.replace(
                    DEFAULT_DOCKER_WORKSPACE_DIR, ""
                ).replace(self.TEMPLATES_DIR, "")

        # User override of cli_lint_mode
        if config.exists(self.request_id, self.name + "_CLI_LINT_MODE"):
            cli_lint_mode_descriptor = self.cli_lint_mode
            cli_lint_mode_config = config.get(
                self.request_id, self.name + "_CLI_LINT_MODE"
            )
            if cli_lint_mode_descriptor == "project":
                logging.warning(
                    f"Override {self.name} cli_lint_mode with {cli_lint_mode_config} at your own risk, "
                    "as command line arguments are built for project mode"
                )
            elif (
                cli_lint_mode_descriptor == "file"
                and cli_lint_mode_config == "list_of_files"
            ):
                logging.warning(
                    f"Override {self.name} cli_lint_mode with {cli_lint_mode_config} at your own risk, "
                    f"as command line arguments are built for {cli_lint_mode_descriptor} mode"
                )
            self.cli_lint_mode = cli_lint_mode_config

        # Include regex :try first NAME + _FILTER_REGEX_INCLUDE, then LANGUAGE + _FILTER_REGEX_INCLUDE
        if config.exists(self.request_id, self.name + "_FILTER_REGEX_INCLUDE"):
            self.filter_regex_include = config.get(
                self.request_id, self.name + "_FILTER_REGEX_INCLUDE"
            )
        elif config.exists(
            self.request_id, self.descriptor_id + "_FILTER_REGEX_INCLUDE"
        ):
            self.filter_regex_include = config.get(
                self.request_id, self.descriptor_id + "_FILTER_REGEX_INCLUDE"
            )

        # User arguments from config
        if (
            config.get(self.request_id, self.name + "_COMMAND_REMOVE_ARGUMENTS", "")
            != ""
        ):
            self.cli_command_remove_args = config.get_list_args(
                self.request_id, self.name + "_COMMAND_REMOVE_ARGUMENTS"
            )

        # User remove arguments from config
        if config.get(self.request_id, self.name + "_ARGUMENTS", "") != "":
            self.cli_lint_user_args = config.get_list_args(
                self.request_id, self.name + "_ARGUMENTS"
            )
        # Get PRE_COMMANDS overridden by user
        if config.get(self.request_id, self.name + "_PRE_COMMANDS", "") != "":
            self.pre_commands = config.get_list(
                self.request_id, self.name + "_PRE_COMMANDS"
            )

        # Get POST_COMMANDS overridden by user
        if config.get(self.request_id, self.name + "_POST_COMMANDS", "") != "":
            self.post_commands = config.get_list(
                self.request_id, self.name + "_POST_COMMANDS"
            )

        # Get secured variables allow list
        if config.exists(self.request_id, self.name + "_UNSECURED_ENV_VARIABLES"):
            self.unsecured_env_variables = config.get_list(
                self.request_id, self.name + "_UNSECURED_ENV_VARIABLES"
            )

        # Disable errors for this linter NAME + _DISABLE_ERRORS, then LANGUAGE + _DISABLE_ERRORS
        if config.get(self.request_id, self.name + "_DISABLE_ERRORS_IF_LESS_THAN"):
            self.disable_errors_if_less_than = int(
                config.get(self.request_id, self.name + "_DISABLE_ERRORS_IF_LESS_THAN")
            )
        if self.disable_errors_if_less_than is not None:
            self.disable_errors = False
        elif self.name in params["disable_errors_linters"]:
            self.disable_errors = True
        elif (
            "enable_errors_linters" in params
            and len(params["enable_errors_linters"]) > 0
            and self.name in params["enable_errors_linters"]
        ):
            self.disable_errors = False
        elif (
            "enable_errors_linters" in params
            and len(params["enable_errors_linters"]) > 0
            and self.name not in params["enable_errors_linters"]
        ):
            self.disable_errors = True
        elif config.get(self.request_id, self.name + "_DISABLE_ERRORS", "") == "false":
            self.disable_errors = False
        elif config.get(self.request_id, self.name + "_DISABLE_ERRORS", "") == "true":
            self.disable_errors = True
        elif (
            config.get(self.request_id, self.descriptor_id + "_DISABLE_ERRORS", "")
            == "false"
        ):
            self.disable_errors = False
        elif (
            config.get(self.request_id, self.descriptor_id + "_DISABLE_ERRORS", "")
            == "true"
        ):
            self.disable_errors = True
        # Exclude regex: descriptor level
        if config.exists(self.request_id, self.descriptor_id + "_FILTER_REGEX_EXCLUDE"):
            self.filter_regex_exclude_descriptor = config.get(
                self.request_id, self.descriptor_id + "_FILTER_REGEX_EXCLUDE"
            )
        # Exclude regex: linter level
        if config.exists(self.request_id, self.name + "_FILTER_REGEX_EXCLUDE"):
            self.filter_regex_exclude_linter = config.get(
                self.request_id, self.name + "_FILTER_REGEX_EXCLUDE"
            )
        # Override default docker image version
        if config.exists(self.request_id, self.name + "_DOCKER_IMAGE_VERSION"):
            self.cli_docker_image_version = config.get(
                self.request_id, self.name + "_DOCKER_IMAGE_VERSION"
            )

    # If linter is activated only if some file is found, and config file has been overridden
    # ->  add it to the files to check
    def update_active_if_file_found(self):
        if (
            len(self.active_only_if_file_found) > 0
            and self.config_file_name not in self.active_only_if_file_found
        ):
            self.active_only_if_file_found.append(self.config_file_name)

    # Processes the linter
    def run(self, run_commands_before_linters=None, run_commands_after_linters=None):
        self.start_perf = perf_counter()

        # Initialize linter reports
        for reporter in self.reporters:
            reporter.initialize()

        # Apply actions defined on Linter class if defined
        self.before_lint_files()

        # Run commands defined in descriptor, or overridden by user in configuration
        pre_post_factory.run_linter_pre_commands(
            self.master, self, run_commands_before_linters
        )

        # Lint each file one by one
        if self.cli_lint_mode == "file":
            index = 0
            for file in self.files:
                file_status = "success"
                index = index + 1
                return_code, stdout = self.process_linter(file)
                file_errors_number = 0
                file_warnings_number = 0
                file_warnings_number = self.get_total_number_warnings(stdout)
                self.total_number_warnings += file_warnings_number
                if return_code > 0:
                    file_status = "error"
                    self.status = "warning" if self.disable_errors is True else "error"
                    self.return_code = (
                        self.return_code if self.disable_errors is True else 1
                    )
                    self.number_errors += 1
                    # Calls external functions to count the number of warnings and errors
                    file_errors_number = self.get_total_number_errors(stdout)

                    self.total_number_errors += file_errors_number
                self.update_files_lint_results(
                    [file],
                    return_code,
                    file_status,
                    stdout,
                    file_errors_number,
                    file_warnings_number,
                )
        else:
            # Lint all workspace in one command
            return_code, stdout = self.process_linter()
            self.stdout = stdout
            # Count warnings regardless of return code
            self.total_number_warnings += self.get_total_number_warnings(stdout)
            if return_code != 0:
                self.status = "warning" if self.disable_errors is True else "error"
                self.return_code = 0 if self.disable_errors is True else 1
                self.number_errors += 1
                self.total_number_errors += self.get_total_number_errors(stdout)
            elif self.total_number_warnings > 0:
                self.status = "warning"
            # Build result for list of files
            if self.cli_lint_mode == "list_of_files":
                self.update_files_lint_results(self.files, None, None, None, None, None)

        # Set return code to 0 if failures in this linter must not make the MegaLinter run fail
        if self.return_code != 0:
            # Disable errors: no failure, just warning
            if self.disable_errors is True:
                self.return_code = 0
            elif (
                self.disable_errors_if_less_than is not None
                and self.total_number_errors < self.disable_errors_if_less_than
            ):
                self.return_code = 0

        # Delete locally copied remote config file if necessary
        if self.remote_config_file_to_delete is not None:
            os.remove(self.remote_config_file_to_delete)

        # Delete locally copied remote ignore file if necessary
        if self.remote_ignore_file_to_delete is not None:
            os.remove(self.remote_ignore_file_to_delete)

        # Run commands defined in descriptor, or overridden by user in configuration
        pre_post_factory.run_linter_post_commands(
            self.master, self, run_commands_after_linters
        )

        # Generate linter reports
        self.elapsed_time_s = perf_counter() - self.start_perf
        for reporter in self.reporters:
            try:
                reporter.produce_report()
            except Exception as e:
                logging.error("Unable to process reporter " + reporter.name + str(e))

        return self

    def replace_vars(self, variables):
        variables_with_replacements = []
        for txt in variables:
            if "{{SARIF_OUTPUT_FILE}}" in txt:
                txt = txt.replace("{{SARIF_OUTPUT_FILE}}", self.sarif_output_file)
            elif "{{REPORT_FOLDER}}" in txt:
                txt = txt.replace("{{REPORT_FOLDER}}", self.report_folder)
            elif "{{WORKSPACE}}" in txt:
                txt = txt.replace("{{WORKSPACE}}", self.workspace)
            variables_with_replacements += [txt]

        return variables_with_replacements

    def update_files_lint_results(
        self,
        linted_files,
        return_code,
        file_status,
        stdout,
        file_errors_number,
        file_warnings_number,
    ):
        if self.try_fix is True:
            updated_files = utils.list_updated_files(self.github_workspace)
        else:
            updated_files = []
        for file in linted_files:
            if self.try_fix is True:
                fixed = utils.check_updated_file(
                    file, self.github_workspace, updated_files
                )
            else:
                fixed = False
            if fixed is True:
                self.number_fixed = self.number_fixed + 1
            # store result
            self.files_lint_results += [
                {
                    "file": file,
                    "status_code": return_code,
                    "status": file_status,
                    "stdout": stdout,
                    "fixed": fixed,
                    "errors_number": file_errors_number,
                    "warnings_number": file_warnings_number,
                }
            ]

    # List all reporters, then instantiate each of them
    def load_reporters(self):
        reporter_init_params = {"master": self, "report_folder": self.report_folder}
        self.reporters = utils.list_active_reporters_for_scope(
            "linter", reporter_init_params
        )

    def log_file_filters(self):
        log_object = {
            "name": self.name,
            "filter_regex_include": self.filter_regex_include,
            "filter_regex_exclude_descriptor": self.filter_regex_exclude_descriptor,
            "filter_regex_exclude_linter": self.filter_regex_exclude_linter,
            "files_sub_directory": self.files_sub_directory,
            "lint_all_files": self.lint_all_files,
            "lint_all_other_linters_files": self.lint_all_other_linters_files,
            "file_extensions": self.file_extensions,
            "file_names_regex": self.file_names_regex,
            "file_names_not_ends_with": self.file_names_not_ends_with,
            "file_contains_regex": self.file_contains_regex,
            "file_contains_regex_extensions": self.file_contains_regex_extensions,
        }
        logging.debug("[Filters] " + str(log_object))

    # Collect all files that will be analyzed by the current linter
    def collect_files(self, all_files):
        self.log_file_filters()
        # Filter all files to keep only the ones matching with the current linter
        self.files = utils.filter_files(
            all_files=all_files,
            filter_regex_include=self.filter_regex_include,
            filter_regex_exclude=[
                self.filter_regex_exclude_descriptor,
                self.filter_regex_exclude_linter,
            ],
            file_names_regex=self.file_names_regex,
            file_extensions=self.file_extensions,
            ignored_files=[],
            ignore_generated_files=False,  # This filter is applied at MegaLinter level
            file_names_not_ends_with=self.file_names_not_ends_with,
            file_contains_regex=self.file_contains_regex,
            file_contains_regex_extensions=self.file_contains_regex_extensions,
            files_sub_directory=self.files_sub_directory,
            lint_all_other_linters_files=self.lint_all_other_linters_files,
            workspace=self.workspace,
        )
        self.files_number = len(self.files)
        logging.debug(
            f"{self.name} linter kept {self.files_number} files after applying linter filters:"
            + utils.format_bullet_list(self.files)
        )

    # lint a single file or whole project
    def process_linter(self, file=None):
        # Remove previous run SARIF file if necessary
        if self.sarif_output_file is not None and os.path.isfile(
            self.sarif_output_file
        ):
            os.remove(self.sarif_output_file)
        # Build command using method locally defined on Linter class
        command = self.build_lint_command(file)
        # Output command if debug mode
        logging.debug(f"[{self.linter_name}] command: {str(command)}")
        # Run command via CLI
        return_code, return_output = self.execute_lint_command(command)
        logging.debug(
            f"[{self.linter_name}] result: {str(return_code)} {return_output}"
        )
        return return_code, return_output

    # Execute a linting command . Can be overridden for special cases, like use of PowerShell script
    # noinspection PyMethodMayBeStatic
    def execute_lint_command(self, command):
        cwd = os.path.abspath(self.workspace)
        logging.debug(f"[{self.linter_name}] CWD: {cwd}")
        subprocess_env = {
            **config.build_env(self.request_id, True, self.unsecured_env_variables),
            "FORCE_COLOR": "0",
        }
        if isinstance(command, str):
            self.lint_command_log.append(command)
            # Call linter with a sub-process
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                cwd=cwd,
                env=subprocess_env,
                executable=(
                    shutil.which("bash") if sys.platform == "win32" else "/bin/bash"
                ),
            )
            return_code = process.returncode
            return_stdout = utils.decode_utf8(process.stdout)
        else:
            # Use full executable path if we are on Windows
            if sys.platform == "win32":
                cli_absolute = shutil.which(command[0])
                if cli_absolute is not None:
                    command[0] = cli_absolute
                else:
                    msg = "Unable to find command: " + command[0]
                    logging.error(msg)
                    return errno.ESRCH, msg
            self.lint_command_log.append(" ".join(command))
            # Call linter with a sub-process (RECOMMENDED: with a list of strings corresponding to the command)
            try:
                process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=subprocess_env,
                    cwd=cwd,
                )
                return_code = process.returncode
                return_stdout = utils.decode_utf8(process.stdout)
            except FileNotFoundError as err:
                return_code = 999
                return_stdout = (
                    f"Fatal error while calling {self.linter_name}: {str(err)}"
                )
            except Exception as err:
                return_code = 99
                return_stdout = (
                    f"Fatal error while calling {self.linter_name}: {str(err)}"
                )
        self.manage_sarif_output(return_stdout)
        # Return linter result
        return return_code, return_stdout

    def manage_sarif_output(self, return_stdout):
        sarif_confirmed = False
        # Move SARIF file if necessary if generated in a fixed place by the linter
        if (
            self.can_output_sarif is True
            and self.output_sarif is True
            and self.sarif_output_file is not None
            and self.sarif_default_output_file is not None
            and not os.path.isfile(self.sarif_output_file)
        ):
            linter_sarif_report = (
                self.sarif_default_output_file
                if os.path.isfile(self.sarif_default_output_file)
                else os.path.join(self.workspace, self.sarif_default_output_file)
            )
            if not os.path.isfile(linter_sarif_report):
                linter_sarif_report = os.path.join(
                    self.report_folder, self.sarif_default_output_file
                )

            # Check that a sarif report really exists before moving it etc)
            if os.path.isfile(linter_sarif_report):
                shutil.move(linter_sarif_report, self.sarif_output_file)
                sarif_confirmed = True
                logging.debug(
                    f"Moved {linter_sarif_report} to {self.sarif_output_file}"
                )
            else:
                logging.debug(
                    f"Could not find {linter_sarif_report} (linter sarif output error?)"
                )
                sarif_confirmed = False
        # Manage case when SARIF output is in stdout (and not generated by the linter)
        elif (
            self.can_output_sarif is True
            and self.output_sarif is True
            and not os.path.isfile(self.sarif_output_file)
        ):
            sarif_stdout = utils.find_json_in_stdout(return_stdout)
            if sarif_stdout != "":
                with open(self.sarif_output_file, "w", encoding="utf-8") as file:
                    file.write(sarif_stdout)
                sarif_confirmed = True
            else:
                logging.error(
                    "[Sarif] ERROR: there is no SARIF output file found, and stdout doesn't contain SARIF"
                )
                logging.error("[Sarif] stdout: " + return_stdout)
        elif (
            self.can_output_sarif is True
            and self.output_sarif is True
            and os.path.isfile(self.sarif_output_file)
        ):
            sarif_confirmed = True

        if sarif_confirmed is True:
            utils_sarif.normalize_sarif_files(self)

        # Convert SARIF into human readable text for Console & Text reporters
        if sarif_confirmed is True and self.master.sarif_to_human is True:
            with open(self.sarif_output_file, "r", encoding="utf-8") as file:
                self.stdout_human = utils_reporter.convert_sarif_to_human(
                    file.read(), self.request_id
                )

    # Returns linter version (can be overridden in special cases, like version has special format)
    def get_linter_version(self):
        if self.linter_version_cache is not None:
            return self.linter_version_cache
        version_output = self.get_linter_version_output()
        reg = self.version_extract_regex
        if isinstance(reg, str):
            reg = re.compile(reg)
        m = reg.search(version_output)
        if m:
            self.linter_version_cache = ".".join(m.group().split())
        else:
            logging.error(
                f"Unable to extract version with regex {str(reg)} from {version_output}"
            )
            self.linter_version_cache = "ERROR"
        return self.linter_version_cache

    # Returns the version of the associated linter (can be overridden in special cases, like version has special format)
    def get_linter_version_output(self):
        command = self.build_version_command()
        logging.debug("Linter version command: " + str(command))
        cwd = os.getcwd() if command[0] != "npm" else "~/"
        subprocess_env = {
            **config.build_env(self.request_id, True, self.unsecured_env_variables),
            "FORCE_COLOR": "0",
            "NO_COLOR": "true",
        }
        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=subprocess_env,
            )
            return_code = process.returncode
            output = utils.decode_utf8(process.stdout)
            logging.debug("Linter version result: " + str(return_code) + " " + output)
        except FileNotFoundError:
            logging.warning("Unable to call command [" + " ".join(command) + "]")
            return_code = 666
            output = "ERROR"

        if return_code != self.version_command_return_code:
            logging.warning(
                "Unable to get version for linter [" + self.linter_name + "]"
            )
            logging.warning(
                " ".join(command) + f" returned output: ({str(return_code)}) " + output
            )
            return "ERROR"
        else:
            return output

    # Returns linter help (can be overridden in special cases, like version has special format)
    def get_linter_help(self):
        if self.linter_help_cache is not None:
            return self.linter_help_cache
        help_command = self.build_help_command()
        return_code = 666
        output = ""
        command = ""
        for command in [help_command] + self.cli_help_extra_commands:
            try:
                if isinstance(command, str):
                    command = command.split(" ")
                if sys.platform == "win32":
                    cli_absolute = shutil.which(command[0])
                    if cli_absolute is not None:
                        command[0] = cli_absolute
                logging.debug("Linter help command: " + str(command))
                subprocess_env = {
                    **config.build_env(
                        self.request_id, True, self.unsecured_env_variables
                    ),
                    "FORCE_COLOR": "0",
                }
                process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=subprocess_env,
                )
                return_code = process.returncode
                output += utils.decode_utf8(process.stdout)
                logging.debug("Linter help result: " + str(return_code) + " " + output)
            except FileNotFoundError:
                logging.warning("Unable to call command [" + " ".join(command) + "]")
                return_code = 666
                output += "ERROR"
                break

        if return_code != self.help_command_return_code or output.strip() == "":
            logging.warning("Unable to get help for linter [" + self.linter_name + "]")
            logging.warning(f"{str(command)} returned output: ({return_code}) {output}")
            return "ERROR"
        else:
            return output

    # noinspection PyMethodMayBeStatic
    def get_regex(self, reg):
        if reg is None:
            raise Exception("You must define a regex !")
        if isinstance(reg, str):
            reg = re.compile(reg)
        return reg

    def manage_docker_command(self, command):
        if self.cli_docker_image is None:
            return command
        docker_command = ["docker", "run", "--rm"]
        if hasattr(self, "workspace"):
            volume_root = config.get(self.request_id, "MEGALINTER_VOLUME_ROOT", "")
            if volume_root != "":
                workspace_value = (
                    volume_root
                    + "/"
                    + self.workspace.replace(DEFAULT_DOCKER_WORKSPACE_DIR, "")
                )
            else:
                workspace_value = self.workspace
        else:
            workspace_value = DEFAULT_DOCKER_WORKSPACE_DIR
        docker_command += map(
            lambda arg, w=workspace_value: arg.replace("{{WORKSPACE}}", w),
            self.cli_docker_args,
        )
        docker_command += [
            f"{self.cli_docker_image}:"
            + f"{os.environ.get(self.cli_docker_image_version, self.cli_docker_image_version)}"
        ]
        if isinstance(command, str):
            command = " ".join(docker_command) + " " + command
        else:
            command = (
                docker_command + command
            )  # ["ls", "-A", DEFAULT_DOCKER_WORKSPACE_DIR]
        return command

    ########################################
    # Methods that can be overridden below #
    ########################################

    def before_lint_files(self):
        pass

    # Build the CLI command to call to lint a file (can be overridden)
    def build_lint_command(self, file=None) -> list:
        cmd = [*self.cli_executable]

        # Add other lint cli arguments if defined
        self.cli_lint_extra_args = self.replace_vars(self.cli_lint_extra_args)
        cmd += self.cli_lint_extra_args

        # Add fix argument if defined
        if self.apply_fixes is True and (
            self.cli_lint_fix_arg_name is not None
            or len(self.cli_lint_fix_remove_args) > 0
            or str(self.cli_executable_fix) != str(self.cli_executable)
        ):
            args_pos = len(self.cli_executable)
            cmd = cmd[args_pos:]  # Remove executable elements
            cmd = self.cli_executable_fix + cmd
            if self.cli_lint_fix_arg_name is not None:
                cmd += [self.cli_lint_fix_arg_name]
            self.try_fix = True

        # Add user-defined extra arguments if defined
        self.cli_lint_user_args = self.replace_vars(self.cli_lint_user_args)
        cmd += self.cli_lint_user_args

        # Add config arguments if defined (except for case when no_config_if_fix is True)
        if (
            self.cli_config_arg_name in cmd
            or self.cli_config_arg_name in self.cli_config_extra_args
        ):
            # User overridden config within LINTER_NAME_ARGUMENTS
            cmd += self.cli_config_extra_args
        elif self.config_file is not None:
            # Config file
            self.final_config_file = self.config_file
            if self.cli_docker_image is not None:
                self.final_config_file = self.final_config_file.replace(
                    self.workspace, DEFAULT_DOCKER_WORKSPACE_DIR
                )
            if self.cli_config_arg_name.endswith(
                "="
            ) or self.cli_config_arg_name.endswith(":"):
                cmd += [self.cli_config_arg_name + self.final_config_file]
            elif self.cli_config_arg_name != "":
                cmd += [self.cli_config_arg_name, self.final_config_file]
            cmd += self.cli_config_extra_args
        elif self.cli_config_default_value is not None:
            # Default config value
            cmd += [self.cli_config_arg_name, self.cli_config_default_value]
            cmd += self.cli_config_extra_args

        # Manage ignore arguments if necessary
        cmd += self.get_ignore_arguments(cmd)

        # Manage SARIF arguments if necessary
        cmd += self.get_sarif_arguments()

        # Add other lint cli arguments after other arguments if defined
        self.cli_lint_extra_args_after = self.replace_vars(
            self.cli_lint_extra_args_after
        )
        cmd += self.cli_lint_extra_args_after

        # Some linters/formatters update files by default.
        # To avoid that, declare -megalinter-fix-flag as cli_lint_fix_arg_name
        if self.try_fix is True:
            for arg in self.cli_lint_fix_remove_args:
                cmd.remove(arg)
            if "--megalinter-fix-flag" in cmd:
                cmd.remove("--megalinter-fix-flag")

        # Remove arguments at user request
        for arg in self.cli_command_remove_args:
            cmd.remove(arg)

        # Append file in command arguments
        if file is not None:
            cmd += [file]

        # If mode is "list of files", append all files as cli arguments
        elif self.cli_lint_mode == "list_of_files":
            cmd += self.files
        return self.manage_docker_command(cmd)

    # Manage ignore arguments
    def get_ignore_arguments(self, cmd):
        ignore_args = []
        if (
            self.ignore_file is not None
            and self.cli_lint_ignore_arg_name is not None
            and self.cli_lint_ignore_arg_name not in cmd
            and self.cli_lint_ignore_arg_name not in self.cli_lint_extra_args_after
        ):
            self.final_ignore_file = self.ignore_file
            if self.cli_docker_image is not None:
                self.final_ignore_file = self.final_ignore_file.replace(
                    self.workspace, DEFAULT_DOCKER_WORKSPACE_DIR
                )
            if self.cli_lint_ignore_arg_name.endswith("="):
                ignore_args += [self.cli_lint_ignore_arg_name + self.final_ignore_file]
            elif self.cli_lint_ignore_arg_name != "":
                ignore_args += [self.cli_lint_ignore_arg_name, self.final_ignore_file]
        return ignore_args

    # Manage SARIF arguments
    def get_sarif_arguments(self):
        if self.can_output_sarif is True and self.output_sarif is True:
            self.sarif_output_file = (
                self.report_folder + os.sep + "sarif" + os.sep + self.name + ".sarif"
            )
            os.makedirs(os.path.dirname(self.sarif_output_file), exist_ok=True)
            self.cli_sarif_args = self.replace_vars(self.cli_sarif_args)
            return self.cli_sarif_args
        return []

    # Find number of errors in linter stdout log
    def get_total_number_errors(self, stdout: str):
        total_errors = 0

        # Count using SARIF output file
        if self.output_sarif is True:
            try:
                # SARIF is in MegaLinter named file
                if self.sarif_output_file is not None and os.path.isfile(
                    self.sarif_output_file
                ):
                    with open(
                        self.sarif_output_file, "r", encoding="utf-8"
                    ) as sarif_file:
                        sarif_output = yaml.safe_load(sarif_file)
                        # SARIF is in default output file
                elif self.sarif_default_output_file is not None and os.path.isfile(
                    self.sarif_default_output_file
                ):
                    with open(
                        self.sarif_default_output_file, "r", encoding="utf-8"
                    ) as sarif_file:
                        sarif_output = yaml.safe_load(sarif_file)
                        # SARIF is in stdout
                else:
                    # SARIF is in stdout
                    sarif_output = yaml.safe_load(stdout)
                if "results" in sarif_output["runs"][0]:
                    # Get number of results
                    total_errors = len(sarif_output["runs"][0]["results"])
                    # Append number of invocation config notifications (other type of errors, not in result)
                    if "invocations" in sarif_output["runs"][0]:
                        for invocation in sarif_output["runs"][0]["invocations"]:
                            if "toolConfigurationNotifications" in invocation:
                                total_errors += len(
                                    invocation["toolConfigurationNotifications"]
                                )
                # If we got here, we should have found a number of errors from SARIF output
                if total_errors == 0:
                    logging.warning(
                        "Unable to get total errors from SARIF output.\nSARIF:"
                        + str(sarif_output)
                    )
                return total_errors
            except Exception as e:
                total_errors = 1
                logging.error(
                    "Error while getting total errors from SARIF output.\nError:"
                    + str(e)
                    + "\nstdout: "
                    + stdout
                )
                return total_errors
        # Get number with a single regex. Used when linter prints out Found _ errors
        elif self.cli_lint_errors_count == "regex_number":
            reg = self.get_regex(self.cli_lint_errors_regex)
            m = re.search(reg, utils.normalize_log_string(stdout))
            if m:
                total_errors = int(m.group(1))
        # Count the number of occurrences of a regex corresponding to an error in linter log (parses linter log)
        elif self.cli_lint_errors_count == "regex_count":
            reg = self.get_regex(self.cli_lint_errors_regex)
            total_errors = len(re.findall(reg, utils.normalize_log_string(stdout)))
        # Sum of all numbers found in linter logs with a regex. Found when each file prints out total number of errors
        elif self.cli_lint_errors_count == "regex_sum":
            reg = self.get_regex(self.cli_lint_errors_regex)
            matches = re.findall(reg, utils.normalize_log_string(stdout))
            total_errors = sum(int(m) for m in matches)
        # Count all lines of the linter log
        elif self.cli_lint_errors_count == "total_lines":
            total_errors = sum(
                not line.isspace() and line != "" for line in stdout.splitlines()
            )
        # Count number of results in sarif format
        elif self.cli_lint_errors_count == "sarif":
            sarif = None
            sarif_stdout = utils.find_json_in_stdout(stdout)
            try:
                sarif = json.loads(sarif_stdout)
            except ValueError as e:
                logging.warning(f"Unable to parse sarif ({str(e)}):" + stdout)
            if sarif and sarif["runs"] and sarif["runs"][0]["results"]:
                total_errors = len(sarif["runs"][0]["results"])
            else:
                logging.warning("Unable to find results in :" + stdout)
        # Return result if found, else default value according to status
        if total_errors > 0:
            return total_errors
        if self.cli_lint_errors_count is not None and self.output_sarif is False:
            logging.warning(
                f"Unable to get number of errors with {self.cli_lint_errors_count} "
                f"and {str(self.cli_lint_errors_regex)}"
            )

        # If no regex is defined, return 0 errors if there is a success or 1 error if there are any
        if self.status == "success":
            return 0
        else:
            return 1

    # Find number of warnings in linter stdout log
    def get_total_number_warnings(self, stdout: str):
        total_warnings = None

        # Get number with a single regex.
        if self.cli_lint_warnings_count == "regex_number":
            reg = self.get_regex(self.cli_lint_warnings_regex)
            m = re.search(reg, utils.normalize_log_string(stdout))
            if m:
                total_warnings = int(m.group(1))
        # Count the number of occurrences of a regex corresponding to an error in linter log (parses linter log)
        elif self.cli_lint_warnings_count == "regex_count":
            reg = self.get_regex(self.cli_lint_warnings_regex)
            total_warnings = len(re.findall(reg, utils.normalize_log_string(stdout)))
        # Sum of all numbers found in linter logs with a regex. Found when each file prints out total number of errors
        elif self.cli_lint_warnings_count == "regex_sum":
            reg = self.get_regex(self.cli_lint_warnings_regex)
            matches = re.findall(reg, utils.normalize_log_string(stdout))
            total_warnings = sum(int(m) for m in matches)
        # Count all lines of the linter log
        elif self.cli_lint_warnings_count == "total_lines":
            total_warnings = sum(
                not line.isspace() and line != "" for line in stdout.splitlines()
            )
        if self.cli_lint_warnings_count is not None and total_warnings is None:
            logging.warning(
                f"Unable to get number of warnings with {self.cli_lint_warnings_count} "
                f"and {str(self.cli_lint_warnings_regex)}"
            )

        if total_warnings is None:
            total_warnings = 0

        return total_warnings

    # Build the CLI command to get linter version (can be overridden if --version is not the way to get the version)
    def build_version_command(self):
        cmd = [*self.cli_executable_version]
        cli_absolute = shutil.which(cmd[0])
        if cli_absolute is not None:
            cmd[0] = cli_absolute
        cmd += self.cli_version_extra_args
        if self.cli_version_arg_name != "":
            cmd += [self.cli_version_arg_name]
        return self.manage_docker_command(cmd)

    # Build the CLI command to get linter version (can be overridden if --version is not the way to get the version)
    def build_help_command(self):
        cmd = [*self.cli_executable_help]
        cmd += self.cli_help_extra_args
        cmd += [self.cli_help_arg_name]
        return self.manage_docker_command(cmd)

    # Provide additional details in text reporter logs
    # noinspection PyMethodMayBeStatic
    def complete_text_reporter_report(self, _reporter_self):
        return []

    def pre_test(self, test_name):
        pass

    def post_test(self, test_name):
        pass
