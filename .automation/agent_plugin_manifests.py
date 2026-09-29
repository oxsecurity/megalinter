#!/usr/bin/env python3
import json
import logging
import os
import sys
from pathlib import Path

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE_MANIFEST = "plugin.json"
NEWLINE = chr(10)
SEPARATOR = "---" + NEWLINE

# Per-vendor plugin manifests mirroring the identity declared in the Agent Plugins
# 1.0 manifest.
TARGET_PLUGIN_MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
]
# Marketplaces describe themselves, so only their plugin entries are mirrored. Those
# entries never carry a "version": when an entry and a plugin manifest both declare
# one, clients ignore the entry value.
TARGET_MARKETPLACE_MANIFESTS = [
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
]
SHARED_FIELDS = ["name", "version", "description", "license", "homepage", "repository"]
SHARED_ENTRY_FIELDS = ["name", "description", "license", "homepage", "repository"]

# Agent Plugins 1.0 standardizes skills, auto-discovered from skills/, but not
# sub-agents: Copilot clients load those from com.github.copilot/agents, named
# <name>.agent.md. Their bodies are identical to the Claude Code definitions, so
# they are generated from them to avoid drift. Only the frontmatter differs:
# Copilot tool aliases already accept the Claude tool names (Read -> read,
# Grep/Glob -> search, Bash -> execute, WebFetch/WebSearch -> web), but "haiku"
# is not a Copilot model id, so the model override is dropped.
AGENT_SOURCE_DIR = "skills/megalinter-setup/agents"
AGENT_NAMES = ["megalinter-watcher", "megalinter-runner", "megalinter-fixer"]
COPILOT_AGENTS_DIR = "com.github.copilot/agents"
COPILOT_DROPPED_FRONTMATTER_KEYS = ["model"]
COPILOT_GENERATED_NOTICE = (
    f"<!-- @generated from {AGENT_SOURCE_DIR}/<name>.md "
    "by .automation/agent_plugin_manifests.py, do not edit -->"
)


def read_manifest(relative_path: str) -> dict:
    return json.loads(Path(f"{REPO_HOME}/{relative_path}").read_text(encoding="utf-8"))


def write_manifest(relative_path: str, manifest: dict) -> None:
    Path(f"{REPO_HOME}/{relative_path}").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def sync() -> None:
    reference = read_manifest(REFERENCE_MANIFEST)
    for target in TARGET_PLUGIN_MANIFESTS:
        manifest = read_manifest(target)
        updated = False
        for field in SHARED_FIELDS:
            if field in manifest and manifest[field] != reference[field]:
                manifest[field] = reference[field]
                updated = True
        if updated is True:
            write_manifest(target, manifest)
            logging.info(f"Updated agent plugin manifest {target}")
    for target in TARGET_MARKETPLACE_MANIFESTS:
        manifest = read_manifest(target)
        updated = False
        for entry in manifest["plugins"]:
            for field in SHARED_ENTRY_FIELDS:
                if field in entry and entry[field] != reference[field]:
                    entry[field] = reference[field]
                    updated = True
        if updated is True:
            write_manifest(target, manifest)
            logging.info(f"Updated agent plugin marketplace {target}")
    sync_copilot_agents()


def build_copilot_agent(source_text: str) -> str:
    _, frontmatter, body = source_text.split(SEPARATOR, 2)
    kept = [
        line
        for line in frontmatter.splitlines()
        if line.split(":", 1)[0].strip() not in COPILOT_DROPPED_FRONTMATTER_KEYS
    ]
    return (
        SEPARATOR
        + NEWLINE.join(kept)
        + NEWLINE
        + SEPARATOR
        + NEWLINE
        + COPILOT_GENERATED_NOTICE
        + NEWLINE
        + body.rstrip(NEWLINE)
        + NEWLINE
    )


def sync_copilot_agents() -> None:
    target_dir = Path(f"{REPO_HOME}/{COPILOT_AGENTS_DIR}")
    target_dir.mkdir(parents=True, exist_ok=True)
    for name in AGENT_NAMES:
        source_path = Path(f"{REPO_HOME}/{AGENT_SOURCE_DIR}/{name}.md")
        content = build_copilot_agent(source_path.read_text(encoding="utf-8"))
        target = target_dir / f"{name}.agent.md"
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if current != content:
            with target.open("w", encoding="utf-8", newline=NEWLINE) as target_file:
                target_file.write(content)
            logging.info(f"Updated Copilot agent {COPILOT_AGENTS_DIR}/{name}.agent.md")


def bump_patch() -> str:
    reference = read_manifest(REFERENCE_MANIFEST)
    major, minor, patch = reference["version"].split(".")
    reference["version"] = f"{major}.{minor}.{int(patch) + 1}"
    write_manifest(REFERENCE_MANIFEST, reference)
    sync()
    return reference["version"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if "--bump" in sys.argv:
        logging.info(f"Agent plugin version bumped to {bump_patch()}")
    else:
        sync()
