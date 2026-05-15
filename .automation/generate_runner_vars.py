#!/usr/bin/env python
"""Generate a slim JSON of MegaLinter configuration variables for mega-linter-runner.

Reads megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json and
writes mega-linter-runner/lib/megalinter-vars.json with just the fields the runner
CLI needs to surface variables to humans and agents via `mega-linter-runner --list-vars`.
"""

from __future__ import annotations

import json
import logging
import os

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(
    REPO_HOME,
    "megalinter",
    "descriptors",
    "schemas",
    "megalinter-configuration.jsonschema.json",
)
OUTPUT_PATH = os.path.join(
    REPO_HOME, "mega-linter-runner", "lib", "megalinter-vars.json"
)

KEEP_FIELDS = (
    "type",
    "title",
    "description",
    "default",
    "enum",
    "examples",
)


def slim_variable(name: str, raw: dict, enums: dict[str, list[str]]) -> dict:
    out: dict = {"name": name}
    for field in KEEP_FIELDS:
        if field in raw:
            out[field] = raw[field]
    if "x-category" in raw:
        out["category"] = raw["x-category"]
    if "x-section" in raw:
        out["section"] = raw["x-section"]
    # Resolve items.$ref to the referenced enum where it adds value
    items = raw.get("items")
    if isinstance(items, dict):
        ref = items.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/definitions/"):
            enum_key = ref.split("/")[-1]
            values = enums.get(enum_key)
            if values:
                out["items_enum"] = values
        elif "enum" in items:
            out["items_enum"] = items["enum"]
        elif "type" in items:
            out["items_type"] = items["type"]
    return out


def resolve_enums(definitions: dict) -> dict[str, list[str]]:
    resolved: dict[str, list[str]] = {}
    for key, value in definitions.items():
        if isinstance(value, dict) and isinstance(value.get("enum"), list):
            resolved[key] = value["enum"]
    return resolved


def generate(schema_path: str = SCHEMA_PATH, output_path: str = OUTPUT_PATH) -> str:
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)

    enums = resolve_enums(schema.get("definitions", {}))
    properties = schema.get("properties", {})
    variables = {
        name: slim_variable(name, raw, enums)
        for name, raw in sorted(properties.items())
    }

    categories: dict[str, int] = {}
    for var in variables.values():
        category = var.get("category", "GENERAL")
        categories[category] = categories.get(category, 0) + 1

    output = {
        "_meta": {
            "variable_count": len(variables),
            "categories": dict(sorted(categories.items())),
            "doc_url": "https://megalinter.io/latest/config-variables/",
        },
        "variables": variables,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    path = generate()
    logging.info(
        "Generated %s (%d variables)",
        os.path.relpath(path, REPO_HOME),
        sum(1 for _ in json.load(open(path, encoding="utf-8"))["variables"]),
    )
