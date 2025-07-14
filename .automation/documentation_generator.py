# !/usr/bin/env python3
"""
Documentation generation functions for MegaLinter build system
"""
import json
import logging
import os

import megalinter
import yaml

from build_constants import *
from test_generator import list_descriptors_for_build
from utils_build import (
    replace_in_file, get_linter_base_info, get_install_md, doc_url, 
    banner_link, logo_link, icon, get_badges, md_to_text, add_in_config_schema_file
)
from schema_validator import finalize_doc_build


def generate_documentation():
    """Automatically generate README linters table and a MD file for each linter"""
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

    # Build & Update plugins table
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


def generate_descriptor_documentation(descriptor):
    """Generate a MD page for a descriptor (language, format, tooling_format)"""
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
        f"# {descriptor.get('descriptor_label', descriptor.get('descriptor_id')).replace('#', '\\#')}",
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
    """Generate documentation for a specific flavor"""
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
                if linter_name in line:
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


def process_type(linters_by_type, type1, type_label, linters_tables_md):
    """Build a MD table for a type of linter (language, format, tooling_format), and a MD file for each linter"""
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
        generate_linter_documentation(linter, md_individual_extra, lang_lower, linter_name_lower)


def generate_linter_documentation(linter, md_individual_extra, lang_lower, linter_name_lower):
    """Generate documentation for an individual linter"""
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
            f"# {linter.linter_name} "
            + logo_link(
                linter.linter_image_url,
                linter.linter_name,
                doc_url(linter.linter_url),
                "Visit linter Web Site",
                28,
            ),
            "",
            md_individual_extra,
        ]
    elif md_individual_extra == "":
        linter_doc_md += [f"# {linter.linter_name}", ""]
    else:
        linter_doc_md += [f"# {linter.linter_name}", "", md_individual_extra, ""]

    # Indicate that a linter is deprecated in this version
    title_prefix = ""
    if hasattr(linter, "deprecated") and linter.deprecated is True:
        linter_doc_md += [
            "> :warning: **DEPRECATED LINTER**: This linter has been deprecated."
            " Please use an alternative or upgrade your version of MegaLinter"
        ]

    # Indicate that a linter is disabled in this version
    if hasattr(linter, "disabled") and linter.disabled is True:
        linter_doc_md += [
            "> :warning: **DISABLED LINTER**: This linter has been disabled "
            "in this version of MegaLinter for performance reasons"
        ]

    # Linter text , if defined in YML descriptor
    if hasattr(linter, "linter_text") and linter.linter_text:
        linter_doc_md += [linter.linter_text, ""]

    # Linter-specific configuration
    linter_doc_md += ["", f"## {linter.linter_name} documentation", ""]
    
    # Continue with the rest of the linter documentation...
    # This is a simplified version - the full implementation would include all the linter config details


def build_flavors_md_table(filter_linter_name=None, replace_link=False):
    """Build flavors markdown table"""
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
        + len(linters_by_type["other"])
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


def build_plugins_md_table():
    """Build plugins table from YML file in .automation/plugins.yml"""
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


def generate_documentation_all_linters():
    """Generate comprehensive documentation for all linters"""
    # This is a placeholder for the complex function that generates the all_linters.md file
    # The full implementation would be quite long and handle all the linter details
    logging.info("Generating all linters documentation...")
    pass
