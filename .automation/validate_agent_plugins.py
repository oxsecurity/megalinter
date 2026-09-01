#!/usr/bin/env python3
import json
import logging
import os
import sys
import urllib.request

import jsonschema
from agent_plugin_manifests import (
    AGENT_NAMES,
    AGENT_SOURCE_DIR,
    COPILOT_AGENTS_DIR,
    REFERENCE_MANIFEST,
    REPO_HOME,
    SHARED_ENTRY_FIELDS,
    SHARED_FIELDS,
    TARGET_MARKETPLACE_MANIFESTS,
    TARGET_PLUGIN_MANIFESTS,
    build_copilot_agent,
    read_manifest,
)

AGENT_PLUGINS_SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_FILES = [
    "skills/megalinter-setup/agents/megalinter-watcher.md",
    "skills/megalinter-setup/agents/megalinter-runner.md",
    "skills/megalinter-setup/agents/megalinter-fixer.md",
]
MANIFESTS_DECLARING_AGENTS = [
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
]


def check_agent_plugins_schema(errors: list[str]) -> None:
    with urllib.request.urlopen(AGENT_PLUGINS_SCHEMA_URL, timeout=30) as response:
        schema = json.loads(response.read().decode("utf-8"))
    try:
        jsonschema.validate(read_manifest(REFERENCE_MANIFEST), schema)
    except jsonschema.ValidationError as error:
        errors.append(
            f"{REFERENCE_MANIFEST} does not match Agent Plugins 1.0: {error.message}"
        )


def check_shared_fields(errors: list[str]) -> None:
    reference = read_manifest(REFERENCE_MANIFEST)
    for relative_path in TARGET_PLUGIN_MANIFESTS:
        manifest = read_manifest(relative_path)
        for field in SHARED_FIELDS:
            if field in manifest and manifest[field] != reference[field]:
                errors.append(
                    f"{relative_path}: {field} is {manifest[field]!r}, expected "
                    f"{reference[field]!r} (from {REFERENCE_MANIFEST})"
                )
    for relative_path in TARGET_MARKETPLACE_MANIFESTS:
        entries = read_manifest(relative_path)["plugins"]
        if len(entries) != 1 or entries[0]["name"] != reference["name"]:
            errors.append(
                f"{relative_path}: expected a single plugin entry named "
                f"{reference['name']!r}"
            )
            continue
        if "version" in entries[0]:
            errors.append(
                f"{relative_path}: plugin entries must not declare a version, "
                "it is read from the plugin manifest"
            )
        for field in SHARED_ENTRY_FIELDS:
            if field in entries[0] and entries[0][field] != reference[field]:
                errors.append(
                    f"{relative_path}: plugin entry {field} differs from "
                    f"{REFERENCE_MANIFEST}"
                )


def check_referenced_paths(errors: list[str]) -> None:
    expected_agents = sorted(f"./{path}" for path in AGENT_FILES)
    for relative_path in MANIFESTS_DECLARING_AGENTS:
        declared_agents = read_manifest(relative_path)["agents"]
        for agent_file in declared_agents:
            if not os.path.isfile(os.path.join(REPO_HOME, agent_file)):
                errors.append(f"{relative_path}: agent file not found: {agent_file}")
        if sorted(declared_agents) != expected_agents:
            errors.append(
                f"{relative_path}: agents list is out of sync with {AGENT_FILES}"
            )
    for skill_dir in sorted(os.listdir(os.path.join(REPO_HOME, "skills"))):
        skill_path = os.path.join(REPO_HOME, "skills", skill_dir)
        if os.path.isdir(skill_path) and not os.path.isfile(
            os.path.join(skill_path, "SKILL.md")
        ):
            errors.append(
                f"skills/{skill_dir}: missing SKILL.md, it will not be loaded"
            )


# Copilot clients do not read the vendor manifests declaring the sub-agents: they
# load them from com.github.copilot/agents. Those files are generated, so a source
# definition edited without re-running the sync would silently ship a stale agent.
def check_copilot_agents(errors: list[str]) -> None:
    for name in AGENT_NAMES:
        source = os.path.join(REPO_HOME, AGENT_SOURCE_DIR, f"{name}.md")
        target = os.path.join(REPO_HOME, COPILOT_AGENTS_DIR, f"{name}.agent.md")
        if not os.path.isfile(target):
            errors.append(
                f"{COPILOT_AGENTS_DIR}/{name}.agent.md is missing: "
                "run python .automation/agent_plugin_manifests.py"
            )
            continue
        with open(source, encoding="utf-8") as source_file:
            expected = build_copilot_agent(source_file.read())
        with open(target, encoding="utf-8") as target_file:
            if target_file.read() != expected:
                errors.append(
                    f"{COPILOT_AGENTS_DIR}/{name}.agent.md is out of sync with "
                    f"{AGENT_SOURCE_DIR}/{name}.md: "
                    "run python .automation/agent_plugin_manifests.py"
                )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    errors: list[str] = []
    check_agent_plugins_schema(errors)
    check_shared_fields(errors)
    check_referenced_paths(errors)
    check_copilot_agents(errors)
    if len(errors) > 0:
        for error in errors:
            logging.error(f"  {error}")
        logging.error(f"Agent plugin manifests validation FAILED ({len(errors)})")
        return 1
    logging.info("Agent plugin manifests are valid and consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
