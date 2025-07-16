# !/usr/bin/env python3
"""
Main orchestrator for MegaLinter build system
This replaces the original build.py and coordinates all build operations
"""
import logging
import os
import sys

from megalinter import config

from build_constants import *
from dockerfile_builder import generate_all_flavors, generate_linter_dockerfiles
from test_generator import generate_linter_test_classes
from schema_validator import generate_json_schema_enums, validate_descriptors, validate_own_megalinter_config, generate_mkdocs_yml
from documentation_generator import generate_documentation, generate_documentation_all_linters
from utils_build import reformat_markdown_tables, update_dependents_info, generate_version, update_workflows_linters
from stats_collector import collect_linter_previews, manage_output_variables


def main():
    """Main entry point for the build system"""
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


if __name__ == "__main__":
    main()
