#!/usr/bin/env python3
# Audits the community plugins listed in .automation/plugins.yml (schema, native install, SARIF,
# main descriptor properties) and writes .automation/generated/plugins-audit.json, used by build.py to
# generate the plugin pages of the documentation.
# --check-added <base ref>: checks only the plugins added or changed by a pull request.
import argparse
import logging
import os
import subprocess
import sys

import yaml

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_HOME)

from megalinter import plugin_audit  # noqa: E402

PLUGINS_FILE = os.path.join(REPO_HOME, ".automation", "plugins.yml")
AUDIT_FILE = os.path.join(REPO_HOME, ".automation", "generated", "plugins-audit.json")
PLUGINS_FILE_GIT_PATH = ".automation/plugins.yml"
REQUIRED_ENTRY_KEYS = ["name", "description", "docUrl", "pluginUrl", "author"]


def parse_plugins(text):
    return (yaml.safe_load(text) or {}).get("plugins") or []


def read_plugins():
    with open(PLUGINS_FILE, "r", encoding="utf-8") as f:
        return parse_plugins(f.read())


def catalog_errors(plugins):
    errors = []
    names = set()
    slugs = set()
    for index, plugin in enumerate(plugins):
        missing = [key for key in REQUIRED_ENTRY_KEYS if not plugin.get(key)]
        if missing:
            errors.append(f"plugins[{index}] has no {', '.join(missing)}")
        if plugin.get("name") in names:
            errors.append(f"plugins[{index}]: duplicate name {plugin.get('name')}")
        names.add(plugin.get("name"))
        # Each plugin gets the page docs/plugins/<slug>.md
        slug = plugin_audit.plugin_slug(str(plugin.get("name") or ""))
        if slug in ["", "index"] or slug in slugs:
            errors.append(
                f"plugins[{index}]: name {plugin.get('name')} gives the documentation page "
                f"name '{slug}', empty, reserved or already used"
            )
        slugs.add(slug)
    return errors


def changed_plugins(plugins, base_ref):
    process = subprocess.run(
        ["git", "show", f"{base_ref}:{PLUGINS_FILE_GIT_PATH}"],
        capture_output=True,
        text=True,
        cwd=REPO_HOME,
    )
    base_plugins = parse_plugins(process.stdout) if process.returncode == 0 else []
    base_by_name = {plugin.get("name"): plugin for plugin in base_plugins}
    return [plugin for plugin in plugins if base_by_name.get(plugin["name"]) != plugin]


# GitHub workflow commands: escaped data, else a multi-line message is cut at its first line
def escape_annotation_data(value):
    return str(value).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_annotation_property(value):
    return escape_annotation_data(value).replace(":", "%3A").replace(",", "%2C")


def annotation(level, title, message):
    return (
        f"::{level} title={escape_annotation_property(title)}::"
        f"{escape_annotation_data(message)}"
    )


def report_plugin(name, result):
    title = f"Plugin {name}"
    blocking = []
    if result["status"] == "unreachable":
        blocking.append(f"Descriptor unreachable: {result.get('fetch_error')}")
    if "url" in result["required_missing"]:
        blocking += result["errors"]
    for message in blocking:
        logging.info(annotation("error", title, message))
    for scope, item in plugin_audit.missing_requirements(result):
        if item == "url":
            continue
        prefix = f"{scope}: " if scope else ""
        logging.info(
            annotation(
                "warning",
                title,
                f"{prefix}{plugin_audit.requirement_label(item)} is missing "
                f"({plugin_audit.REQUIRED_CHECKS[item]['impact']})",
            )
        )
    if "url" not in result["required_missing"]:
        for error in result["errors"]:
            logging.info(annotation("warning", title, error))
    recommendations = plugin_audit.missing_recommendations(result)
    if recommendations:
        logging.info(
            annotation(
                "notice",
                title,
                "Recommended: "
                + ", ".join(
                    plugin_audit.requirement_label(item)
                    for _scope, item in recommendations
                ),
            )
        )
    logging.info(f"{name}: {result['status']}")
    return len(blocking)


def check_added(base_ref):
    plugins = read_plugins()
    errors = catalog_errors(plugins)
    for error in errors:
        logging.info(annotation("error", "plugins.yml", error))
    if errors:
        return 1
    changed = changed_plugins(plugins, base_ref)
    if not changed:
        logging.info("No plugin added or changed in .automation/plugins.yml")
        return 0
    audit = plugin_audit.audit_catalog(changed)
    blocking = sum(report_plugin(name, result) for name, result in audit.items())
    return 1 if blocking else 0


def audit_all(only, output):
    plugins = read_plugins()
    errors = catalog_errors(plugins)
    for error in errors:
        logging.error(error)
    if errors:
        return 1
    previous = plugin_audit.load_audit_file(output)
    selected = [plugin for plugin in plugins if not only or plugin["name"] in only]
    audit = plugin_audit.audit_catalog(selected, previous)
    for name, result in audit.items():
        logging.info(f"{name}: {result['status']}")
    names = {plugin["name"] for plugin in plugins}
    # Keep the previous results of the plugins not selected, drop the removed plugins
    merged = {
        name: result for name, result in previous.items() if name in names
    } | audit
    plugin_audit.write_audit_file(output, merged)
    logging.info(f"Wrote {output}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit the MegaLinter plugins catalog")
    parser.add_argument("--only", nargs="*", default=[], help="Plugin names to audit")
    parser.add_argument(
        "--check-added",
        metavar="BASE_REF",
        default=None,
        help="Check only the plugins added or changed since BASE_REF (pull requests)",
    )
    parser.add_argument("--output", default=AUDIT_FILE, help="Audit file to write")
    options = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    if options.check_added:
        return check_added(options.check_added)
    return audit_all(set(options.only), options.output)


if __name__ == "__main__":
    sys.exit(main())
