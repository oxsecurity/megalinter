#!/usr/bin/env python3
import json
import logging
import os
import sys
from pathlib import Path

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE_MANIFEST = "plugin.json"

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
