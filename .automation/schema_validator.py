# !/usr/bin/env python3
"""
Schema validation and JSON schema generation functions for MegaLinter build system
"""
import json
import logging
import os

import jsonschema
import megalinter
import yaml

from build_constants import *
from test_generator import list_descriptors_for_build
from utils_build import replace_in_file, copy_md_file, move_to_file, replace_anchors_by_links, replace_full_url_links, get_linter_base_info


def validate_own_megalinter_config():
    """Apply configuration JSON Schema to MegaLinter's own config"""
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


def validate_descriptors():
    """Apply descriptor JSON Schema to every descriptor file"""
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


def generate_json_schema_enums():
    """Generate JSON schema enums for flavors, descriptors, and linters"""
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
    json_schema["definitions"]["enum_linter_keys"]["enum"] = sorted(
        set(json_schema["definitions"]["enum_linter_keys"]["enum"])
    )
    with open(CONFIG_JSON_SCHEMA, "w", encoding="utf-8") as outfile:
        json.dump(json_schema, outfile, indent=2, sort_keys=True)
        outfile.write("\n")


def finalize_doc_build():
    """Finalize documentation build by splitting sections and updating links"""
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
    """Generate dynamic mkdocs yml configuration"""
    logging.info("Generating mkdocs dynamic yml…")
    descriptors, linters_by_type = list_descriptors_for_build()
    process_type_mkdocs_yml(linters_by_type, "language")
    process_type_mkdocs_yml(linters_by_type, "format")
    process_type_mkdocs_yml(linters_by_type, "tooling_format")
    process_type_mkdocs_yml(linters_by_type, "other")


def process_type_mkdocs_yml(linters_by_type, type1):
    """Process a specific type of linters for mkdocs yml"""
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
