# !/usr/bin/env python3
"""
Utility functions for MegaLinter build system
"""
import json
import logging
import markdown
import os
import re
import subprocess
import sys
from shutil import copyfile, which
from typing import Any
from urllib import parse as parse_urllib

import jsonschema
import megalinter
import requests
import yaml
from bs4 import BeautifulSoup
from giturlparse import parse
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from build_constants import ALPINE_VERSION, IDE_LIST


def get_linter_base_info(linter):
    lang_lower = linter.descriptor_id.lower()
    linter_name_lower = linter.linter_name.lower().replace("-", "_")
    if hasattr(linter, "descriptor_label") and linter.descriptor_label is not None:
        descriptor_label = linter.descriptor_label
    else:
        descriptor_label = linter.descriptor_id
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
            f"https://pkgs.alpinelinux.org/packages?branch=v{ALPINE_VERSION}&arch=x86_64&name=",
        )
    if "cargo" in item["install"]:
        linter_doc_md += ["- Cargo packages (Rust):"]
        linter_doc_md += md_package_list(
            item["install"]["cargo"],
            "cargo",
            "  ",
            "https://crates.io/crates/",
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
    for package in package_list:
        package_name = package
        end_url = package

        if type == "cargo":  # cargo specific version
            match = re.search(r"(.*)@(.*)", package)

            if match:
                package_id = match.group(1)
                package_version = get_arg_variable_value(match.group(2))

                if package_version is not None:
                    package_name = f"{package_id}@{package_version}"
                    end_url = f"{package_id}/{package_version}"
                else:
                    package_name = package_id
                    end_url = package_id
        elif type == "npm":  # npm specific version
            match = re.search(r"(.*)@(.*)", package)

            if match:
                package_id = match.group(1)
                package_version = get_arg_variable_value(match.group(2))

                if package_version is not None:
                    package_name = f"{package_id}@{package_version}"
                    end_url = f"{package_id}/v/{package_version}"
                else:
                    package_name = package_id
                    end_url = package_id
        elif type == "pip":  # py specific version
            match = re.search(r"(.*)==(.*)", package)

            if match:
                package_id = match.group(1)
                package_version = get_arg_variable_value(match.group(2))

                if package_version is not None:
                    package_name = f"{package_id}=={package_version}"
                    end_url = f"{package_id}/{package_version}"
                else:
                    package_name = package_id
                    end_url = package_id
        elif type == "gem":  # gem specific version
            match = re.search(r"(.*):(.*)", package)

            if match:
                package_id = match.group(1)
                package_version = get_arg_variable_value(match.group(2))

                if package_version is not None:
                    package_name = f"{package_id}:{package_version}"
                    end_url = f"{package_id}/versions/{package_version}"
                else:
                    package_name = package_id
                    end_url = package_id

        res += [f"{indent}- [{package_name}]({start_url}{end_url})"]
    return res


def get_arg_variable_value(package_version):
    extracted_version = re.search(r"\$\{(.*)\}", package_version).group(1)

    if extracted_version in MAIN_DOCKERFILE_ARGS_MAP:
        return MAIN_DOCKERFILE_ARGS_MAP[extracted_version]
    else:
        return None


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


def dump_as_json(value: Any, empty_value: str) -> str:
    if not value:
        return empty_value
    # Convert any value to string with JSON
    # Don't indent since markdown table supports single line only
    result = json.dumps(value, indent=None, sort_keys=True)
    return f"`{result}`"


def number_human_format(num, round_to=1):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "G", "T", "P"][magnitude]
    )


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
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

    if (hasattr(linter, "get") and linter.get("disabled") is True) or (
        hasattr(linter, "disabled") and linter.disabled is True
    ):
        badges += ["![disabled](https://shields.io/badge/-disabled-orange)"]
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
    stdout = megalinter.utils.clean_string(process.stdout)
    logging.info(f"Format table results: ({process.returncode})\n" + stdout)


# Additional build utility functions from original build.py

def generate_version():
    """Generate new version for npm and python packages"""
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
        check=True,
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
    import git
    repo = git.Repo(os.getcwd())
    repo.git.add(update=True)
    repo.git.commit("-m", "Release MegaLinter " + RELEASE_TAG)
    repo.create_tag(RELEASE_TAG)


def update_dependents_info():
    """Update dependents information"""
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
    """Update workflow linters"""
    from test_generator import list_descriptors_for_build
    
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

    update_workflow_linters_file(".github/workflows/deploy-DEV-linters.yml", linters)
    update_workflow_linters_file(".github/workflows/deploy-BETA-linters.yml", linters)
    update_workflow_linters_file(".github/workflows/deploy-RELEASE-linters.yml", linters)


def update_workflow_linters_file(file_path, linters):
    """Update workflow linters file"""
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        file_content = re.sub(
            r"(linter:\s+\[\s*)([^\[\]]*?)(\s*\])",
            rf"\1{re.escape(linters).replace(chr(92), '').strip()}\3",
            file_content,
        )

    with open(file_path, "w") as f:
        f.write(file_content)
