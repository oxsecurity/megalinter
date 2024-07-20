#!/usr/bin/env python3
"""
Main MegaLinter class, encapsulating all linters process and reporting

"""

import argparse
import logging
import multiprocessing as mp
import os
import shutil
import sys
from shutil import copytree
from uuid import uuid1

import chalk as c
import git
from megalinter import (
    Linter,
    config,
    flavor_factory,
    linter_factory,
    plugin_factory,
    pre_post_factory,
    utils,
)
from megalinter.alpaca import alpaca
from megalinter.constants import (
    DEFAULT_DOCKER_WORKSPACE_DIR,
    DEFAULT_REPORT_FOLDER_NAME,
    ML_DOC_URL,
)
from megalinter.logger import display_header, initialize_logger, manage_upgrade_message
from megalinter.utils_reporter import log_section_end, log_section_start
from multiprocessing_logging import install_mp_handler, uninstall_mp_handler


# initialize worker processes
def init_worker(request_config_in):
    # declare scope of a new global variable
    global REQUEST_CONFIG
    # store argument in the global variable for this process
    REQUEST_CONFIG = request_config_in


# Function to run linters using multiprocessing pool
def run_linters(linters, request_id):
    global REQUEST_CONFIG
    config.set_config(request_id, REQUEST_CONFIG)
    for linter in linters:
        linter.run()
    return linters


# Main MegaLinter class, orchestrating files collection, linter processes and reporters
class Megalinter:
    # Constructor: Load global config, linters & compute file extensions
    def __init__(self, params=None):
        if params is None:
            params = {}

        # megalinter_exec cli variables
        self.cli = params["cli"] if "cli" in params else False
        self.arg_input = None
        self.arg_output = None
        self.linter_version_only = None
        self.load_cli_vars()

        if "request_id" in params:
            self.request_id = params["request_id"]
        else:
            self.request_id = str(uuid1())

        # Initialization for lint request cases
        self.workspace = self.get_workspace(params)
        # Do not send secrets to linter executables
        config.init_config(self.request_id, self.workspace, params)

        # Guess who's there ? :)
        if self.cli is True:
            alpaca(self.request_id)

        # Initialize runtime config
        self.github_workspace = config.get(
            self.request_id, "GITHUB_WORKSPACE", self.workspace
        )
        self.megalinter_flavor = flavor_factory.get_image_flavor()
        self.initialize_output()
        # Initialize logger + init logs
        if self.cli is True or os.environ.get("PYTEST_CURRENT_TEST", None) is not None:
            initialize_logger(self)
            manage_upgrade_message()
            display_header(self)
        # MegaLinter default rules location
        self.default_rules_location = (
            "/action/lib/.automation"
            if os.path.isdir("/action/lib/.automation")
            else os.path.relpath(
                os.path.relpath(
                    os.path.dirname(os.path.abspath(__file__)) + "/../TEMPLATES"
                )
            )
        )
        # User-defined rules location
        self.linter_rules_path = self.github_workspace + os.path.sep + ".github/linters"

        self.ignore_gitignore_files = True
        self.ignore_generated_files = False
        self.validate_all_code_base = True
        self.filter_regex_include = None
        self.filter_regex_exclude = None
        self.default_linter_activation = True
        self.output_sarif = False

        # Get enable / disable vars
        self.enable_descriptors = config.get_list(self.request_id, "ENABLE", [])
        self.enable_linters = config.get_list(self.request_id, "ENABLE_LINTERS", [])
        self.disable_descriptors = config.get_list(self.request_id, "DISABLE", [])
        self.disable_linters = config.get_list(self.request_id, "DISABLE_LINTERS", [])
        self.disable_errors_linters = config.get_list(
            self.request_id, "DISABLE_ERRORS_LINTERS", []
        )
        self.manage_default_linter_activation()
        self.apply_fixes = config.get_list(self.request_id, "APPLY_FIXES", "none")
        self.show_elapsed_time = (
            config.get(self.request_id, "SHOW_ELAPSED_TIME", "false") == "true"
            or config.get(self.request_id, "LOG_LEVEL", "DEBUG") == "DEBUG"
        )
        # In case SARIF is active, convert results into human readable text for logs
        self.sarif_to_human = (
            config.get(self.request_id, "SARIF_TO_HUMAN", "true") == "true"
        )
        # Load optional configuration
        self.load_config_vars()
        # Runtime properties
        self.reporters = []
        self.linters: list[Linter] = []
        self.file_extensions = []
        self.file_names_regex = []
        self.status = "success"
        self.return_code = 0
        self.has_git_extraheader = False
        self.has_updated_sources = 0
        self.fail_if_updated_sources = (
            config.get(self.request_id, "FAIL_IF_UPDATED_SOURCES", "false") == "true"
        )
        self.flavor_suggestions = None

        # Initialize plugins
        plugin_factory.initialize_plugins(self.request_id)

        # Copy node_modules in current folder if necessary
        internal_node_modules = "/node-deps/node_modules"
        if (
            os.path.isdir(internal_node_modules)
            and len(os.listdir(internal_node_modules)) > 0
            and pre_post_factory.has_npm_or_yarn_commands(self.request_id)
            and config.get(self.request_id, "COPY_NODE_MODULES_IN_WORKSPACE", "")
            == "true"
        ):
            workspace_node_modules = os.path.join(self.workspace, "node_modules")
            copytree(internal_node_modules, workspace_node_modules, dirs_exist_ok=True)
            # Update PATH & NODE_PATH so node_modules of the currently analyzed workspace is used
            # swapped_path = config.get(self.request_id, "PATH").replace(
            #     f"{internal_node_modules}/.bin", f"{workspace_node_modules}/.bin"
            # )
            # config.set(self.request_id, "PATH", swapped_path)
            # config.set(self.request_id, "NODE_PATH", workspace_node_modules)
            logging.info(
                "[pre] node.js related PRE_COMMANDS found: copy MegaLinter "
                f"internal node_modules ({internal_node_modules}) into "
                f"workspace node_modules ({workspace_node_modules})"
                # f"swap PATH to {swapped_path} and "
                # f"swap NODE_PATH to {workspace_node_modules}."
            )

        # Run user-defined commands
        self.pre_commands_results = pre_post_factory.run_pre_commands(self)
        self.post_commands_results = []
        # Initialize linters and gather criteria to browse files
        self.load_linters()
        self.compute_file_extensions()
        # Load MegaLinter reporters
        self.load_reporters()
        logging.info(log_section_end("megalinter-init"))

    # Collect files, run linters on them and write reports
    def run(self):
        # Manage case where we only want to return standalone linter version
        if self.linter_version_only is True:
            standalone_linter = self.linters[0]
            linter_version = standalone_linter.get_linter_version()
            logging.info(f"{standalone_linter.name}: {linter_version}")
            return

        # Collect files for each identified linter
        logging.info(
            log_section_start(
                "megalinter-file-listing",
                "MegaLinter now collects the files to analyse",
            )
        )
        self.collect_files()

        # Process linters serial or parallel according to configuration
        active_linters = []
        linters_do_fixes = False
        for linter in self.linters:
            if linter.is_active is True:
                active_linters += [linter]
                if linter.apply_fixes is True:
                    linters_do_fixes = True

        # Display warning if selected flavors doesn't match all linters
        if (
            flavor_factory.check_active_linters_match_flavor(
                active_linters, self.request_id
            )
            is False
        ):
            # Remove linters that are not existing in the flavor
            active_linters = [
                linter for linter in active_linters if linter.is_active is True
            ]

        # Initialize reports
        for reporter in self.reporters:
            reporter.initialize()

        active_descriptor_ids = []

        for active_linter in active_linters:
            if active_linter.descriptor_id not in active_descriptor_ids:
                active_descriptor_ids += [active_linter.descriptor_id]

        for active_descriptor_id in active_descriptor_ids:
            pre_post_factory.run_descriptor_pre_commands(self, active_descriptor_id)

        if (
            config.get(self.request_id, "PARALLEL", "true") == "true"
            and len(active_linters) > 1
        ):
            self.process_linters_parallel(active_linters, linters_do_fixes)
        else:
            self.process_linters_serial(active_linters)

        for active_descriptor_id in active_descriptor_ids:
            pre_post_factory.run_descriptor_post_commands(self, active_descriptor_id)

        # Update main MegaLinter status according to results of linters run
        for linter in self.linters:
            if linter.status != "success":
                # Not blocking linter error
                if linter.return_code == 0:
                    if self.status == "success":
                        self.status = "warning"
                # Blocking error
                else:
                    self.status = "error"
            # Blocking linter error
            if linter.return_code > 0:
                self.return_code = linter.return_code
            # Update number fixed
            if linter.number_fixed > 0:
                self.has_updated_sources = 1

        # Sort linters before reports production
        self.linters = sorted(
            self.linters, key=lambda lamb: (lamb.descriptor_id, lamb.name)
        )

        # Check if a MegaLinter flavor can be used for this repo, except if:
        # - FLAVOR_SUGGESTIONS: false is defined
        # - VALIDATE_ALL_CODE_BASE is false, or diff failed (we don't have all the files to calculate the suggestion)
        if (
            self.validate_all_code_base is True
            and config.get(self.request_id, "FLAVOR_SUGGESTIONS", "true") == "true"
        ):
            self.flavor_suggestions = flavor_factory.get_megalinter_flavor_suggestions(
                active_linters
            )

        # Run user-defined commands
        self.post_commands_results = pre_post_factory.run_post_commands(self)

        # Generate reports
        for reporter in self.reporters:
            reporter.produce_report()
        # Process commmands before closing MegaLinter
        self.before_exit()
        # Manage return code
        self.check_results()

    # noinspection PyMethodMayBeStatic
    def process_linters_serial(self, active_linters):
        for linter in active_linters:
            linter.run()

    def process_linters_parallel(self, active_linters, linters_do_fixes):
        linter_groups = []
        if linters_do_fixes is True:
            # Group linters by descriptor, to avoid different linters to update files at the same time
            linters_by_descriptor = {}
            linter_groups_without_fixes = []
            for linter in active_linters:
                if linter.apply_fixes is True:
                    # If the linter can update sources, it must be run in the same group than
                    # other linters that can update the same sources
                    descriptor_active_linters = linters_by_descriptor.get(
                        linter.descriptor_id, []
                    )
                    descriptor_active_linters += [linter]
                    linters_by_descriptor[linter.descriptor_id] = (
                        descriptor_active_linters
                    )
                else:
                    # If the linter can not updates sources, no need to run it in the same group
                    linter_groups_without_fixes += [[linter]]
            # Add groups of linters that can update sources
            for _descriptor_id, linters in linters_by_descriptor.items():
                linter_groups += [linters]
            linter_groups = linter_factory.sort_linters_groups_by_speed(linter_groups)
            # Add "groups" of 1 linter than can not update sources
            linter_groups += linter_factory.sort_linters_groups_by_speed(
                linter_groups_without_fixes
            )
        else:
            # If no fixes are applied, we don't care to run same languages linters at the same time
            for linter in active_linters:
                linter_groups += [[linter]]
            linter_groups = linter_factory.sort_linters_groups_by_speed(linter_groups)
        # Execute linters in asynchronous pool to improve overall performances
        if config.exists(self.request_id, "PARALLEL_PROCESS_NUMBER"):
            process_number = int(config.get(self.request_id, "PARALLEL_PROCESS_NUMBER"))
            logging.info(
                f"Processing linters on [{str(process_number)}] parallel cores… "
                "(according to variable PARALLEL_PROCESS_NUMBER"
            )
        else:
            process_number = mp.cpu_count()
            logging.info(
                f"Processing linters on [{str(process_number)}] parallel cores… "
                "(can be decreased with variable PARALLEL_PROCESS_NUMBER in case of performance issues)"
            )
        install_mp_handler()
        pool = mp.Pool(
            process_number,
            initializer=init_worker,
            initargs=(config.get(self.request_id),),
        )
        pool_results = []
        # Add linter groups to pool
        for linter_group in linter_groups:
            logging.debug(
                linter_group[0].descriptor_id
                + ": "
                + str([o.linter_name for o in linter_group])
            )
            result = pool.apply_async(run_linters, args=[linter_group, self.request_id])
            pool_results += [result]
        pool.close()
        pool.join()
        # Update self.linters objects with results from async processing
        for pool_result in pool_results:
            updated_linters = pool_result.get()
            for updated_linter in updated_linters:
                for i in range(0, len(self.linters)):
                    if self.linters[i].name == updated_linter.name:
                        self.linters[i] = updated_linter
                        break
        uninstall_mp_handler()

    # noinspection PyMethodMayBeStatic
    def get_workspace(self, params):
        if "workspace" in params:
            self.arg_input = params["workspace"]
        if config.is_initialized_for(self.request_id):
            # Use stored config vars
            default_workspace = config.get(self.request_id, "DEFAULT_WORKSPACE", "")
            github_workspace = config.get(self.request_id, "GITHUB_WORKSPACE", "")
        else:
            # Use ENV vars
            default_workspace = config.get(None, "DEFAULT_WORKSPACE", "")
            github_workspace = config.get(None, "GITHUB_WORKSPACE", "")
        # Use CLI input argument
        if self.arg_input is not None:
            if os.path.isdir(self.arg_input):
                # Absolute directory
                return self.arg_input
            else:
                # Relative directory
                logging.debug(
                    f"[Context] workspace sent as input argument: {self.arg_input}"
                )
                assert os.path.isdir(
                    DEFAULT_DOCKER_WORKSPACE_DIR + "/" + self.arg_input
                ), (
                    f"--input directory not found at {DEFAULT_DOCKER_WORKSPACE_DIR}/"
                    + self.arg_input
                )
                return DEFAULT_DOCKER_WORKSPACE_DIR + "/" + self.arg_input
        # Github action run without override of DEFAULT_WORKSPACE and using DEFAULT_DOCKER_WORKSPACE_DIR
        elif (
            default_workspace == ""
            and github_workspace != ""
            and os.path.isdir(github_workspace + DEFAULT_DOCKER_WORKSPACE_DIR)
        ):
            logging.debug(
                "[Context] Github action run without override of DEFAULT_WORKSPACE - "
                + DEFAULT_DOCKER_WORKSPACE_DIR
            )
            return github_workspace + DEFAULT_DOCKER_WORKSPACE_DIR
        # Docker run without override of DEFAULT_WORKSPACE
        elif default_workspace != "" and os.path.isdir(
            DEFAULT_DOCKER_WORKSPACE_DIR + os.path.sep + default_workspace
        ):
            logging.debug(
                "[Context] Docker run without override of DEFAULT_WORKSPACE"
                f" - {default_workspace}{DEFAULT_DOCKER_WORKSPACE_DIR}{os.path.sep + default_workspace}"
            )
            return (
                default_workspace
                + DEFAULT_DOCKER_WORKSPACE_DIR
                + os.path.sep
                + default_workspace
            )
        # Docker run with override of DEFAULT_WORKSPACE for test cases
        elif default_workspace != "" and os.path.isdir(default_workspace):
            logging.debug(
                f"[Context] Docker run test classes with override of DEFAULT_WORKSPACE - {default_workspace}"
            )
            return default_workspace
        # Docker run test classes without override of DEFAULT_WORKSPACE
        elif os.path.isdir(DEFAULT_DOCKER_WORKSPACE_DIR):
            logging.debug(
                "[Context] Docker run test classes without override of DEFAULT_WORKSPACE - "
                + DEFAULT_DOCKER_WORKSPACE_DIR
            )
            return DEFAULT_DOCKER_WORKSPACE_DIR
        # Github action with override of DEFAULT_WORKSPACE
        elif (
            default_workspace != ""
            and github_workspace != ""
            and os.path.isdir(github_workspace + os.path.sep + default_workspace)
        ):
            logging.debug(
                "[Context] Github action with override of DEFAULT_WORKSPACE"
                f" - {github_workspace + os.path.sep + default_workspace}"
            )
            return github_workspace + os.path.sep + default_workspace
        # Github action without override of DEFAULT_WORKSPACE and NOT using DEFAULT_DOCKER_WORKSPACE_DIR
        elif (
            default_workspace == ""
            and github_workspace != ""
            and github_workspace != "/"
            and os.path.isdir(github_workspace)
        ):
            logging.debug(
                "[Context] Github action without override of DEFAULT_WORKSPACE"
                f" and NOT using {DEFAULT_DOCKER_WORKSPACE_DIR}"
                f" - {github_workspace}"
            )
            return github_workspace
        # Unable to identify workspace
        else:
            raise FileNotFoundError(
                f"[Context] Unable to find a workspace to lint \n"
                f"DEFAULT_WORKSPACE: {default_workspace}\n"
                f"GITHUB_WORKSPACE: {github_workspace}"
            )

    # Manage CLI variables
    def load_cli_vars(self):
        if self.cli is False:
            return
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", type=str, help="Input folder to lint")
        parser.add_argument("--output", type=str, help="Output file or directory")
        parser.add_argument(
            "--linterversion",
            nargs="?",
            const="yes",
            default=None,
            help="Collect version of standalone linter",
        )
        args, _unknown = parser.parse_known_args()
        # Input folder to lint
        if args.input:
            self.arg_input = args.input
        # Report folder or file
        if args.output:
            self.arg_output = args.output
        # Linter version
        if args.linterversion == "yes":
            self.linter_version_only = True

    # Manage configuration variables
    def load_config_vars(self):
        # Linter rules root path
        if config.exists(self.request_id, "LINTER_RULES_PATH"):
            linter_rules_path_val = config.get(self.request_id, "LINTER_RULES_PATH")
            if linter_rules_path_val.startswith("http"):
                self.linter_rules_path = linter_rules_path_val
            elif os.path.isdir(
                self.github_workspace + os.path.sep + linter_rules_path_val
            ):
                self.linter_rules_path = (
                    self.github_workspace + os.path.sep + linter_rules_path_val
                )
            elif os.path.isdir(linter_rules_path_val):
                self.linter_rules_path = linter_rules_path_val
            else:
                raise ValueError(
                    f"LINTER_RULES_PATH should be a valid directory ({linter_rules_path_val})"
                )
        # Filtering regex (inclusion)
        if config.exists(self.request_id, "FILTER_REGEX_INCLUDE"):
            self.filter_regex_include = config.get(
                self.request_id, "FILTER_REGEX_INCLUDE"
            )
        # Filtering regex (exclusion)
        if config.exists(self.request_id, "FILTER_REGEX_EXCLUDE"):
            self.filter_regex_exclude = config.get(
                self.request_id, "FILTER_REGEX_EXCLUDE"
            )
        # Disable all fields validation if VALIDATE_ALL_CODEBASE is 'false'
        if (
            config.exists(self.request_id, "VALIDATE_ALL_CODEBASE")
            and config.get(self.request_id, "VALIDATE_ALL_CODEBASE") == "false"
        ):
            self.validate_all_code_base = False
        # Manage IGNORE_GITIGNORED_FILES
        if config.exists(self.request_id, "IGNORE_GITIGNORED_FILES"):
            self.ignore_gitignore_files = (
                config.get(self.request_id, "IGNORE_GITIGNORED_FILES", "true") == "true"
            )
        # Manage IGNORE_GENERATED_FILES
        if config.exists(self.request_id, "IGNORE_GENERATED_FILES"):
            self.ignore_generated_files = (
                config.get(self.request_id, "IGNORE_GENERATED_FILES", "false") == "true"
            )
        # Manage SARIF output
        if config.get(self.request_id, "SARIF_REPORTER", "") == "true":
            self.output_sarif = True

    # Calculate default linter activation according to env variables
    def manage_default_linter_activation(self):
        # If at least one language/linter is activated with VALIDATE_XXX , all others are deactivated by default
        if len(self.enable_descriptors) > 0 or len(self.enable_linters) > 0:
            self.default_linter_activation = False
        # V3 legacy variables
        for env_var in config.get(self.request_id):
            if env_var.startswith("VALIDATE_") and env_var != "VALIDATE_ALL_CODEBASE":
                if config.get(self.request_id, env_var) == "true":
                    self.default_linter_activation = False

    # Load and initialize all linters
    def load_linters(self):
        # Linters init params
        linter_init_params = {
            "master": self,
            "linter_rules_path": self.linter_rules_path,
            "default_rules_location": self.default_rules_location,
            "default_linter_activation": self.default_linter_activation,
            "enable_descriptors": self.enable_descriptors,
            "enable_linters": self.enable_linters,
            "disable_descriptors": self.disable_descriptors,
            "disable_linters": self.disable_linters,
            "disable_errors_linters": self.disable_errors_linters,
            "workspace": self.workspace,
            "github_workspace": self.github_workspace,
            "report_folder": self.report_folder,
            "apply_fixes": self.apply_fixes,
            "show_elapsed_time": self.show_elapsed_time,
            "output_sarif": self.output_sarif,
        }

        # Build linters from descriptor files
        # if flavor selected and no flavor suggestion, ignore linters that aren't in current flavor)
        if self.megalinter_flavor == "none":
            # Single linter docker image
            unique_linter = config.get(self.request_id, "SINGLE_LINTER")
            all_linters = linter_factory.list_linters_by_name(
                linter_init_params, [unique_linter]
            )
        elif (
            # Flavored MegaLinter
            self.megalinter_flavor != "all"
            and config.get(self.request_id, "FLAVOR_SUGGESTIONS", "true") != "true"
        ):
            all_linters = linter_factory.list_flavor_linters(
                linter_init_params, self.megalinter_flavor
            )
        else:
            # main flavor
            all_linters = linter_factory.list_all_linters(linter_init_params)

        skipped_linters = []
        # Remove inactive, disabled or skipped linters
        skip_cli_lint_modes = config.get_list(
            self.request_id, "SKIP_CLI_LINT_MODES", []
        )
        for linter in all_linters:
            linter.master = self
            if (
                linter.is_active is False
                or linter.disabled is True
                or linter.cli_lint_mode in skip_cli_lint_modes
            ):
                skipped_linters += [linter.name]
                if linter.disabled is True:
                    disabled_reason = (
                        linter.disabled_reason
                        if linter.disabled_reason is not None
                        else "Undefined"
                    )
                    logging.warning(
                        f"{linter.name} has been disabled in MegaLinter for the following reason: "
                        + disabled_reason
                    )
                if linter.cli_lint_mode in skip_cli_lint_modes:
                    logging.info(
                        f"{linter.name} has been skipped because its CLI lint mode"
                        " {linter.cli_lint_mode} is in SKIP_CLI_LINT_MODES variable."
                    )
                continue
            self.linters += [linter]
        # Display skipped linters in log
        show_skipped_linters = (
            config.get(self.request_id, "SHOW_SKIPPED_LINTERS", "true") == "true"
        )
        if len(skipped_linters) > 0 and show_skipped_linters:
            skipped_linters.sort()
            logging.info("Skipped linters: " + ", ".join(skipped_linters))
        # Sort linters by language and linter_name
        self.linters = sorted(
            self.linters, key=lambda lamb: (lamb.processing_order, lamb.descriptor_id)
        )

    # List all reporters, then instantiate each of them
    def load_reporters(self):
        reporter_init_params = {"master": self, "report_folder": self.report_folder}
        self.reporters = utils.list_active_reporters_for_scope(
            "mega-linter", reporter_init_params
        )

    # Define all file extensions to browse
    def compute_file_extensions(self):
        file_extensions = []
        file_names_regex = []
        for linter in self.linters:
            file_extensions += linter.file_extensions
            file_names_regex += linter.file_names_regex

        # Remove duplicates
        self.file_extensions = list(dict.fromkeys(file_extensions))
        self.file_names_regex = list(dict.fromkeys(file_names_regex))

    # Collect list of files matching extensions and regex
    def collect_files(self):
        # Collect not filtered list of files
        files_to_lint = config.get_list(self.request_id, "MEGALINTER_FILES_TO_LINT", [])
        if len(files_to_lint) > 0:
            # Files sent as input parameter
            all_files = list()
            for file_to_lint in files_to_lint:
                if os.path.isfile(self.workspace + os.path.sep + file_to_lint):
                    all_files += [file_to_lint]
                else:
                    logging.warning(
                        "[File listing] Input file "
                        + self.workspace
                        + os.path.sep
                        + file_to_lint
                        + " not found"
                    )
        elif self.validate_all_code_base is False:
            # List files using git diff
            try:
                all_files = self.list_files_git_diff()
            except git.InvalidGitRepositoryError as git_err:
                logging.warning(
                    "Unable to list updated files from git diff. Switch to VALIDATE_ALL_CODE_BASE=true"
                )
                logging.debug(f"git error: {str(git_err)}")
                all_files = self.list_files_all()
                self.validate_all_code_base = True
        else:
            # List all files
            all_files = self.list_files_all()
        all_files = sorted(set(all_files))

        logging.debug(
            "All found files before filtering:" + utils.format_bullet_list(all_files)
        )
        # Filter files according to file_extensions, file_names_regex,
        # filter_regex_include, and filter_regex_exclude
        if self.file_extensions:
            logging.info(
                "- File extensions: " + ", ".join(sorted(self.file_extensions))
            )
        if self.file_names_regex:
            logging.info(
                "- File names (regex): " + ", ".join(sorted(self.file_names_regex))
            )
        if self.filter_regex_include is not None:
            logging.info("- Including regex: " + self.filter_regex_include)
        if self.filter_regex_exclude is not None:
            logging.info("- Excluding regex: " + self.filter_regex_exclude)

        # List git ignored files if necessary
        ignored_files = []
        if self.ignore_gitignore_files is True:
            try:
                ignored_files = self.list_git_ignored_files()
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug(
                        "- Excluding .gitignored files ["
                        + str(len(ignored_files))
                        + "]: "
                        + ", ".join(ignored_files)
                    )
                else:
                    logging.info(
                        "- Excluding .gitignored files ["
                        + str(len(ignored_files))
                        + "]: "
                        + ", ".join(ignored_files[0:10])
                        + (",…(full list in DEBUG)" if len(ignored_files) > 10 else "")
                    )
            except git.InvalidGitRepositoryError as git_err:
                logging.warning(f"Unable to list git ignored files ({str(git_err)})")
                ignored_files = []
            except Exception as git_err:
                logging.warning(f"Unable to list git ignored files ({str(git_err)})")
                ignored_files = []

        # Apply all filters on file list
        filtered_files = utils.filter_files(
            all_files=all_files,
            filter_regex_include=self.filter_regex_include,
            filter_regex_exclude=[self.filter_regex_exclude],
            file_names_regex=self.file_names_regex,
            file_extensions=self.file_extensions,
            ignored_files=ignored_files,
            ignore_generated_files=self.ignore_generated_files,
            workspace=self.workspace,
        )

        logging.info(
            "Kept ["
            + str(len(filtered_files))
            + "] files on ["
            + str(len(all_files))
            + "] found files"
        )
        logging.debug(
            "Kept files before applying linter filters:\n- %s",
            "\n- ".join(filtered_files),
        )

        # Collect matching files for each linter
        for linter in self.linters:
            linter.collect_files(filtered_files)
            if len(linter.files) == 0 and linter.lint_all_files is False:
                linter.is_active = False

    def list_files_git_diff(self):
        # List all updated files from git
        logging.info(
            "Listing updated files in [" + self.github_workspace + "] using git diff."
        )
        repo = git.Repo(os.path.realpath(self.github_workspace))
        # Add auth header if necessary
        if config.get(self.request_id, "GIT_AUTHORIZATION_BEARER", "") != "":
            auth_bearer = "Authorization: Bearer " + config.get(
                self.request_id, "GIT_AUTHORIZATION_BEARER"
            )
            repo.config_writer().set_value("http", "extraheader", auth_bearer).release()
            self.has_git_extraheader = True
        # Fetch base branch content
        default_branch = config.get(self.request_id, "DEFAULT_BRANCH", "HEAD")
        default_branch_remote = f"origin/{default_branch}"
        if default_branch_remote not in [ref.name for ref in repo.refs]:
            remote_ref = (
                "HEAD" if default_branch == "HEAD" else f"refs/heads/{default_branch}"
            )
            local_ref = f"refs/remotes/{default_branch_remote}"
            # Try to fetch default_branch from origin, because it isn't cached locally.
            repo.git.fetch("origin", f"{remote_ref}:{local_ref}")
        # Make git diff to list files (and exclude symlinks)
        try:
            # Use optimized way from https://github.com/oxsecurity/megalinter/pull/3472
            diff = repo.git.diff(f"{default_branch_remote}...", name_only=True)
        except Exception as e7:
            # Use previous way as fallback
            logging.warning("Git diff error: " + str(e7))
            logging.warning(
                "You might need to add check-depth: 0 or equivalent to access merge-base"
            )
            logging.warning("See https://github.com/oxsecurity/megalinter/pull/3472")
            logging.warning("Using fallback without merge-base...")
            diff = repo.git.diff(default_branch_remote, name_only=True)
        logging.info(f"Modified files:\n{diff}")
        all_files = list()
        for diff_line in diff.splitlines():
            if os.path.isfile(
                self.workspace + os.path.sep + diff_line
            ) and not os.path.islink(self.workspace + os.path.sep + diff_line):
                all_files += [diff_line]
        return all_files

    def list_files_all(self):
        # List all files under workspace root directory
        logging.info(
            "Listing all files in directory [" + self.workspace + "], then filter with:"
        )
        all_files = [
            file
            for file in sorted(os.listdir(self.workspace))
            if os.path.isfile(os.path.join(self.workspace, file))
        ]
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("Root dir content:" + utils.format_bullet_list(all_files))
        excluded_directories = utils.get_excluded_directories(self.request_id)
        for dirpath, dirnames, filenames in os.walk(self.workspace, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in excluded_directories]
            all_files += [
                os.path.relpath(os.path.join(dirpath, file), self.workspace)
                for file in sorted(filenames)
            ]
        return list(dict.fromkeys(all_files))

    def list_git_ignored_files(self):
        dirpath = os.path.realpath(self.github_workspace)
        repo = git.Repo(dirpath)
        ignored_files = repo.git.execute(
            [
                "git",
                "ls-files",
                "--exclude-standard",
                "--ignored",
                "--others",
                "--cached",
            ]
        ).splitlines()
        ignored_files = map(lambda x: x + "**" if x.endswith("/") else x, ignored_files)
        ignored_files = sorted(list(ignored_files))
        return ignored_files

    def initialize_output(self):
        self.report_folder = config.get(
            self.request_id,
            "REPORT_OUTPUT_FOLDER",
            config.get(
                self.request_id,
                "OUTPUT_FOLDER",
                self.github_workspace + os.path.sep + DEFAULT_REPORT_FOLDER_NAME,
            ),
        )
        # Manage case when output is sent as argument.
        if self.arg_output is not None:
            if ".sarif" in self.arg_output:
                if "/" in self.arg_output:
                    # --output /logs/megalinter/myoutputfile.sarif
                    self.report_folder = os.path.dirname(self.arg_output)
                    config.set(
                        self.request_id,
                        "SARIF_REPORTER_FILE_NAME",
                        os.path.basename(self.arg_output),
                    )
                else:
                    # --output myoutputfile.sarif
                    config.set(
                        self.request_id, "SARIF_REPORTER_FILE_NAME", self.arg_output
                    )
            elif os.path.isdir(self.arg_output):
                # --output /logs/megalinter
                self.report_folder = self.arg_output
        # Don't initialize reports if report folder is none or false
        if not utils.can_write_report_files(self):
            return
        # Initialize output dir
        os.makedirs(self.report_folder, exist_ok=True)
        # Clear report folder if requested
        if config.get(self.request_id, "CLEAR_REPORT_FOLDER", "false") == "true":
            logging.info(
                f"CLEAR_REPORT_FOLDER found: empty folder {self.report_folder}"
            )
            shutil.rmtree(self.report_folder, ignore_errors=True)
            os.makedirs(self.report_folder, exist_ok=True)

    def check_results(self):
        if config.exists(self.request_id, "GITHUB_OUTPUT"):
            github_output_file = config.get(self.request_id, "GITHUB_OUTPUT")
            with open(github_output_file, "a", encoding="utf-8") as output_stream:
                output_stream.write(
                    f"has_updated_sources={str(self.has_updated_sources)}\n"
                )
        if self.status == "success":
            logging.info(c.green("✅ Successfully linted all files without errors"))
            config.delete(self.request_id)
            self.check_updated_sources_failure()
        elif self.status == "warning":
            logging.warning(
                c.yellow("⚠️ Successfully linted all files, but with ignored errors")
            )
            config.delete(self.request_id)
            self.check_updated_sources_failure()
        else:
            logging.error(c.red("❌ Error(s) have been found during linting"))
            logging.warning(
                "To disable linters or customize their checks, you can use a .mega-linter.yml file "
                "at the root of your repository"
            )
            logging.warning(f"More info at {ML_DOC_URL}/configuration/")
            if self.cli is True:
                if config.get(self.request_id, "DISABLE_ERRORS", "false") == "true":
                    config.delete(self.request_id)
                    sys.exit(0)
                else:
                    config.delete(self.request_id)
                    sys.exit(self.return_code)
            config.delete(self.request_id)

    def check_updated_sources_failure(self):
        if self.has_updated_sources > 0 and self.fail_if_updated_sources is True:
            logging.error(
                c.red(
                    "❌ Sources has been updated by linter autofixes, and FAIL_IF_UPDATED_SOURCES has been set to true"
                )
            )
            sys.exit(1)

    def before_exit(self):
        # Clean git repository
        self.manage_clean_git_repo()
        # Display upgrade recommendation if necessary
        manage_upgrade_message()

    def manage_clean_git_repo(self):
        # Add auth header if necessary
        if self.has_git_extraheader is True:
            repo = git.Repo(os.path.realpath(self.github_workspace))
            repo.config_writer().set_value("http", "extraheader", "").release()
