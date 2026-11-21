#!/usr/bin/env python3
"""
Validation of SARIF logs against the SARIF 2.1.0 JSON schema (OASIS)
Test helpers: jsonschema is installed with the test requirements, not in the images
"""

import json
import os

import jsonschema
from megalinter import Linter, utils

SARIF_SCHEMA_FILE = os.path.join(
    utils.REPO_HOME_DEFAULT, ".automation", "test", "sarif", "sarif-schema-2.1.0.json"
)


# Violations of the SARIF 2.1.0 JSON schema by a SARIF log, as readable lines
def list_sarif_schema_errors(sarif_content):
    with open(SARIF_SCHEMA_FILE, "r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    errors = sorted(
        jsonschema.Draft4Validator(schema).iter_errors(sarif_content),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    return [
        "/".join(str(part) for part in error.absolute_path) + f": {error.message[:200]}"
        for error in errors
    ]


# True when the SARIF of the linter is built by MegaLinter, from the output of the linter
def is_sarif_built_by_megalinter(linter):
    return (
        linter.sarif_text_regex is not None
        or linter.sarif_whole_output is True
        or type(linter).convert_output_to_sarif is not Linter.convert_output_to_sarif
    )
