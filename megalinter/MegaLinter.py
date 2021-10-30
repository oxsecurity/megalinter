#!/usr/bin/env python3
"""
Main Mega-Linter class, encapsulating all linters process and reporting

"""

import logging
import multiprocessing as mp
import os
import sys

import chalk as c
import git
from megalinter import (
    config,
    flavor_factory,
    linter_factory,
    plugin_factory,
    pre_post_factory,
    utils,
)
from multiprocessing_logging import install_mp_handler

from megalinter.constants import ML_DOC_URL


# Function to run linters using multiprocessing pool
def run_linters(linters):
    for linter in linters:
        linter.run()
    return linters


# Main Mega-Linter class, orchestrating files collection, linter processes and reporters
class Megalinter:

    # Constructor: Load global config, linters & compute file extensions
    def __init__(self, params=None):
        if params is None:
            params = {}
        self.workspace = self.get_workspace()
        config.init_config(self.workspace)  # Initialize runtime config
        self.github_workspace = config.get("GITHUB_WORKSPACE", self.workspace)
        self.report_folder = config.get(
            "REPORT_OUTPUT_FOLDER",
            config.get("OUTPUT_FOLDER", self.github_workspace + os.path.sep + "report"),
        )
        self.initialize_logger()
        self.manage_upgrade_message()
        self.display_header()
        # Mega-Linter default rules location
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
        self.cli = params["cli"] if "cli" in params else False
        self.default_linter_activation = True

        # Get enable / disable vars
        self.enable_descriptors = config.get_list("ENABLE", [])
        self.enable_linters = config.get_list("ENABLE_LINTERS", [])
        self.disable_descriptors = config.get_list("DISABLE", [])
        self.disable_linters = config.get_list("DISABLE_LINTERS", [])
        self.manage_default_linter_activation()
        self.apply_fixes = config.get_list("APPLY_FIXES", "none")
        self.show_elapsed_time = (
            config.get("SHOW_ELAPSED_TIME", "false") == "true"
            or config.get("LOG_LEVEL", "DEBUG") == "DEBUG"
        )
        # Load optional configuration
        self.load_config_vars()
        # Runtime properties
        self.reporters = []
        self.linters = []
        self.file_extensions = []
        self.file_names_regex = []
        self.status = "success"
        self.return_code = 0
        self.has_updated_sources = 0
        self.flavor_suggestions = None
        # Initialize plugins
        plugin_factory.initialize_plugins()
        # Run user-defined commands
        self.pre_commands_results = pre_post_factory.run_pre_commands(self)
        self.post_commands_results = []
        # Initialize linters and gather criteria to browse files
        self.load_linters()
        self.compute_file_extensions()
        # Load Mega-Linter reporters
        self.load_reporters()

    # Collect files, run linters on them and write reports
    def run(self):

        # Collect files for each identified linter
        self.collect_files()

        # Process linters serial or parallel according to configuration
        active_linters = []
        linters_do_fixes = False
        for linter in self.linters:
            if linter.is_active is True:
                active_linters += [linter]
                if linter.apply_fixes is True:
                    linters_do_fixes = True

        # Initialize reports
        for reporter in self.reporters:
            reporter.initialize()

        # Display warning if selected flavors does not match all linters
        if flavor_factory.check_active_linters_match_flavor(active_linters) is False:
            active_linters = [
                linter for linter in active_linters if linter.is_active is True
            ]

        if config.get("PARALLEL", "true") == "true" and len(active_linters) > 1:
            self.process_linters_parallel(active_linters, linters_do_fixes)
        else:
            self.process_linters_serial(active_linters, linters_do_fixes)

        # Update main Mega-Linter status according to results of linters run
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
        self.linters = sorted(self.linters, key=lambda l: (l.descriptor_id, l.name))

        # Check if a Mega-Linter flavor can be used for this repo, except if:
        # - FLAVOR_SUGGESTIONS: false is defined
        # - VALIDATE_ALL_CODE_BASE is false, or diff failed (we don't have all the files to calculate the suggestion)
        if (
            self.validate_all_code_base is True
            and config.get("FLAVOR_SUGGESTIONS", "true") == "true"
        ):
            self.flavor_suggestions = flavor_factory.get_megalinter_flavor_suggestions(
                active_linters
            )

        # Run user-defined commands
        self.post_commands_results = pre_post_factory.run_post_commands(self)

        # Generate reports
        for reporter in self.reporters:
            reporter.produce_report()
        # Manage return code
        self.check_results()
        # Display upgrade recommendation if necessary
        self.manage_upgrade_message()

    # noinspection PyMethodMayBeStatic
    def process_linters_serial(self, active_linters, _linters_do_fixes):
        for linter in active_linters:
            linter.run()

    def process_linters_parallel(self, active_linters, linters_do_fixes):
        linter_groups = []
        if linters_do_fixes is True:
            # Group linters by descriptor, to avoid different linters to update files at the same time
            linters_by_descriptor = {}
            for linter in active_linters:
                descriptor_active_linters = linters_by_descriptor.get(
                    linter.descriptor_id, []
                )
                descriptor_active_linters += [linter]
                linters_by_descriptor[linter.descriptor_id] = descriptor_active_linters
            for _descriptor_id, linters in linters_by_descriptor.items():
                linter_groups += [linters]
        else:
            # If no fixes are applied, we don't care to run same languages linters at the same time
            for linter in active_linters:
                linter_groups += [[linter]]
        # Execute linters in asynchronous pool to improve overall performances
        install_mp_handler()
        pool = mp.Pool(mp.cpu_count())
        pool_results = []
        # Add linter groups to pool
        for linter_group in linter_groups:
            logging.debug(
                linter_group[0].descriptor_id
                + ": "
                + str([o.linter_name for o in linter_group])
            )
            result = pool.apply_async(run_linters, args=[linter_group])
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

    # noinspection PyMethodMayBeStatic
    def get_workspace(self):
        default_workspace = config.get("DEFAULT_WORKSPACE", "")
        github_workspace = config.get("GITHUB_WORKSPACE", "")
        # Github action run without override of DEFAULT_WORKSPACE and using /tmp/lint
        if (
            default_workspace == ""
            and github_workspace != ""
            and os.path.isdir(github_workspace + "/tmp/lint")
        ):
            logging.debug(
                "[Context] Github action run without override of DEFAULT_WORKSPACE - /tmp/lint"
            )
            return github_workspace + "/tmp/lint"
        # Docker run without override of DEFAULT_WORKSPACE
        elif default_workspace != "" and os.path.isdir(
            "/tmp/lint" + os.path.sep + default_workspace
        ):
            logging.debug(
                "[Context] Docker run without override of DEFAULT_WORKSPACE"
                f" - {default_workspace}/tmp/lint{os.path.sep + default_workspace}"
            )
            return default_workspace + "/tmp/lint" + os.path.sep + default_workspace
        # Docker run with override of DEFAULT_WORKSPACE for test cases
        elif default_workspace != "" and os.path.isdir(default_workspace):
            logging.debug(
                f"[Context] Docker run test classes with override of DEFAULT_WORKSPACE - {default_workspace}"
            )
            return default_workspace
        # Docker run test classes without override of DEFAULT_WORKSPACE
        elif os.path.isdir("/tmp/lint"):
            logging.debug(
                "[Context] Docker run test classes without override of DEFAULT_WORKSPACE - /tmp/lint"
            )
            return "/tmp/lint"
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
        # Github action without override of DEFAULT_WORKSPACE and NOT using /tmp/lint
        elif (
            default_workspace == ""
            and github_workspace != ""
            and github_workspace != "/"
            and os.path.isdir(github_workspace)
        ):
            logging.debug(
                "[Context] Github action without override of DEFAULT_WORKSPACE and NOT using /tmp/lint"
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

    # Manage configuration variables
    def load_config_vars(self):
        # Linter rules root path
        if config.exists("LINTER_RULES_PATH"):
            linter_rules_path_val = config.get("LINTER_RULES_PATH")
            if linter_rules_path_val.startswith("http"):
                self.linter_rules_path = linter_rules_path_val
            else:
                self.linter_rules_path = (
                    self.github_workspace + os.path.sep + linter_rules_path_val
                )
        # Filtering regex (inclusion)
        if config.exists("FILTER_REGEX_INCLUDE"):
            self.filter_regex_include = config.get("FILTER_REGEX_INCLUDE")
        # Filtering regex (exclusion)
        if config.exists("FILTER_REGEX_EXCLUDE"):
            self.filter_regex_exclude = config.get("FILTER_REGEX_EXCLUDE")
        # Disable all fields validation if VALIDATE_ALL_CODEBASE is 'false'
        if (
            config.exists("VALIDATE_ALL_CODEBASE")
            and config.get("VALIDATE_ALL_CODEBASE") == "false"
        ):
            self.validate_all_code_base = False
        # Manage IGNORE_GITIGNORED_FILES
        if config.exists("IGNORE_GITIGNORED_FILES"):
            self.ignore_gitignore_files = (
                config.get("IGNORE_GITIGNORED_FILES", "true")
            )
        # Manage IGNORE_GENERATED_FILES
        if config.exists("IGNORE_GENERATED_FILES"):
            self.ignore_generated_files = (
                config.get("IGNORE_GENERATED_FILES", "false") == "true"
            )

    # Calculate default linter activation according to env variables
    def manage_default_linter_activation(self):
        # If at least one language/linter is activated with VALIDATE_XXX , all others are deactivated by default
        if len(self.enable_descriptors) > 0 or len(self.enable_linters) > 0:
            self.default_linter_activation = False
        # V3 legacy variables
        for env_var in config.get():
            if env_var.startswith("VALIDATE_") and env_var != "VALIDATE_ALL_CODEBASE":
                if config.get(env_var) == "true":
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
            "workspace": self.workspace,
            "github_workspace": self.github_workspace,
            "report_folder": self.report_folder,
            "apply_fixes": self.apply_fixes,
            "show_elapsed_time": self.show_elapsed_time,
        }

        # Build linters from descriptor files
        all_linters = linter_factory.list_all_linters(linter_init_params)
        skipped_linters = []
        for linter in all_linters:
            linter.master = self
            if linter.is_active is False or linter.disabled is True:
                skipped_linters += [linter.name]
                continue
            self.linters += [linter]
        # Display skipped linters in log
        show_skipped_linters = config.get("SHOW_SKIPPED_LINTERS", "true") == "true"
        if len(skipped_linters) > 0 and show_skipped_linters:
            skipped_linters.sort()
            logging.info("Skipped linters: " + ", ".join(skipped_linters))
        # Sort linters by language and linter_name
        self.linters = sorted(
            self.linters, key=lambda l: (l.processing_order, l.descriptor_id)
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
        if self.validate_all_code_base is False:
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
            all_files = self.list_files_all()
        all_files = sorted(set(all_files))

        logging.debug(
            "All found files before filtering:" + utils.format_bullet_list(all_files)
        )
        # Filter files according to fileExtensions, fileNames , filterRegexInclude and filterRegexExclude
        if len(self.file_extensions) > 0:
            logging.info(
                "- File extensions: " + ", ".join(sorted(self.file_extensions))
            )
        if len(self.file_names_regex) > 0:
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
                        + (
                            ",...(full list in DEBUG)"
                            if len(ignored_files) > 10
                            else ""
                        )
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
            filter_regex_exclude=self.filter_regex_exclude,
            file_names_regex=self.file_names_regex,
            file_extensions=self.file_extensions,
            ignored_files=ignored_files,
            ignore_generated_files=self.ignore_generated_files,
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
        default_branch = config.get("DEFAULT_BRANCH", "master")
        default_branch_remote = f"origin/{default_branch}"
        if default_branch_remote not in [ref.name for ref in repo.refs]:
            # Try to fetch default_branch from origin, because it isn't cached locally.
            repo.git.fetch(
                "origin",
                f"refs/heads/{default_branch}:refs/remotes/{default_branch_remote}",
            )
        diff = repo.git.diff(default_branch_remote, name_only=True)
        logging.info(f"Modified files:\n{diff}")
        all_files = list()
        for diff_line in diff.splitlines():
            if os.path.isfile(self.workspace + os.path.sep + diff_line):
                all_files += [self.workspace + os.path.sep + diff_line]
        return all_files

    def list_files_all(self):
        # List all files under workspace root directory
        logging.info(
            "Listing all files in directory [" + self.workspace + "], then filter with:"
        )
        all_files = [
            os.path.join(self.workspace, file)
            for file in sorted(os.listdir(self.workspace))
            if os.path.isfile(os.path.join(self.workspace, file))
        ]
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("Root dir content:" + utils.format_bullet_list(all_files))
        excluded_directories = utils.get_excluded_directories()
        for (dirpath, dirnames, filenames) in os.walk(self.workspace, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in excluded_directories]
            all_files += [os.path.join(dirpath, file) for file in sorted(filenames)]
        return all_files

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
        # ignored_files will be match against absolute path (in all_files), so it should be absolute
        ignored_files = map(lambda x: os.path.join(dirpath, x), ignored_files)
        ignored_files = sorted(list(ignored_files))
        return ignored_files

    def initialize_logger(self):
        logging_level_key = config.get("LOG_LEVEL", "INFO").upper()
        logging_level_list = {
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            # Previous values for v3 ascending compatibility
            "TRACE": logging.WARNING,
            "VERBOSE": logging.INFO,
        }
        logging_level = (
            logging_level_list[logging_level_key]
            if logging_level_key in logging_level_list
            else logging.INFO
        )
        log_file = (
            self.report_folder + os.path.sep + config.get("LOG_FILE", "mega-linter.log")
        )
        if not os.path.isdir(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(
            force=True,
            level=logging_level,
            format="%(message)s",
            handlers=[
                logging.FileHandler(log_file, "w", "utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )

    @staticmethod
    def display_header():
        # Header prints
        logging.info(utils.format_hyphens(""))
        logging.info(utils.format_hyphens("Mega-Linter"))
        logging.info(utils.format_hyphens(""))
        logging.info(
            " - Image Creation Date: " + config.get("BUILD_DATE", "No docker image")
        )
        logging.info(
            " - Image Revision: " + config.get("BUILD_REVISION", "No docker image")
        )
        logging.info(
            " - Image Version: " + config.get("BUILD_VERSION", "No docker image")
        )
        logging.info(utils.format_hyphens(""))
        logging.info("The Mega-Linter documentation can be found at:")
        logging.info(" - "+ML_DOC_URL)
        logging.info(utils.format_hyphens(""))
        logging.info("GITHUB_REPOSITORY: " + os.environ.get("GITHUB_REPOSITORY", ""))
        # logging.info("GITHUB_SHA: " + os.environ.get("GITHUB_SHA", ""))
        logging.info("GITHUB_REF: " + os.environ.get("GITHUB_REF", ""))
        # logging.info("GITHUB_TOKEN: " + os.environ.get("GITHUB_TOKEN", ""))
        logging.info("GITHUB_RUN_ID: " + os.environ.get("GITHUB_RUN_ID", ""))
        logging.info("PAT: " + "set" if os.environ.get("PAT", "") != "" else "")
        # Display config variables for debug mode
        for name, value in sorted(config.get_config().items()):
            logging.debug("" + name + "=" + str(value))
        logging.debug(utils.format_hyphens(""))
        logging.info("")

    def check_results(self):
        print(f"::set-output name=has_updated_sources::{str(self.has_updated_sources)}")
        if self.status == "success":
            logging.info("✅ Successfully linted all files without errors")
            config.delete()
        elif self.status == "warning":
            logging.warning("◬ Successfully linted all files, but with ignored errors")
            config.delete()
        else:
            logging.error("❌ Error(s) have been found during linting")
            logging.warning(
                "To disable linters or customize their checks, you can use a .mega-linter.yml file "
                "at the root of your repository"
            )
            logging.warning(
                f"More info at {ML_DOC_URL}/configuration/"
            )
            if self.cli is True:
                if config.get("DISABLE_ERRORS", "false") == "true":
                    config.delete()
                    sys.exit(0)
                else:
                    config.delete()
                    sys.exit(self.return_code)
            config.delete()

    def manage_upgrade_message(self):
        mega_linter_version = config.get("BUILD_VERSION", "No docker image")
        if "insiders" in mega_linter_version or "v4" in mega_linter_version:
            logging.warning(
                c.yellow(
                    "#######################################################################"
                )
            )
            logging.warning(
                c.yellow(
                    "MEGA-LINTER HAS A NEW V5 VERSION at https://github.com/megalinter/megalinter."
                    " Please upgrade to it by:"
                )
            )
            logging.warning(
                c.yellow(
                    "- Running the command at the root of your repo (requires node.js):"
                    " npx mega-linter-runner --upgrade"
                )
            )
            logging.warning(
                c.yellow(
                    "- Replace versions used by latest (v5 latest stable version) "
                    "or beta (previously 'insiders', content of main branch of megalinter/megalinter)"
                )
            )
            logging.warning(
                c.yellow(
                    "#######################################################################"
                )
            )
