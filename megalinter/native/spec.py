import json
import logging
import os
import sys

import jsonschema
import yaml
from megalinter.native.catalog import load_native_specs
from megalinter.native.resolve import (
    METHODS_WITHOUT_VERSION,
    NATIVE_PLATFORMS,
    PACKAGE_METHODS,
    platform_native_install,
    resolve_native_install,
)
from megalinter.utils import get_descriptor_dir

SCHEMA_FILE = "megalinter-descriptor.jsonschema.json"


def load_runtime_names(descriptor_dir=None):
    descriptor_dir = descriptor_dir or get_descriptor_dir()
    with open(
        os.path.join(descriptor_dir, "native-runtimes.yml"), "r", encoding="utf-8"
    ) as f:
        return set(yaml.safe_load(f)["runtimes"].keys())


def validate_spec(spec, runtime_names, schema_validator):
    errors = []
    native = spec.native_install
    if native is None:
        return [f"{spec.key}: missing native_install"]
    for error in schema_validator.iter_errors(native):
        errors.append(f"{spec.key}: native_install schema: {error.message}")
    if errors:
        return errors
    method = native["method"]
    try:
        resolved = resolve_native_install(spec)
    except KeyError as e:
        return [f"{spec.key}: version reference: {e}"]
    declared = set(native.get("platforms", []))
    unsupported = set(native.get("unsupported", {}).keys())
    both = declared & unsupported
    if both:
        errors.append(
            f"{spec.key}: platforms listed as supported and unsupported: {sorted(both)}"
        )
    missing = set(NATIVE_PLATFORMS) - declared - unsupported
    if missing:
        errors.append(
            f"{spec.key}: platforms neither supported nor unsupported: {sorted(missing)}"
        )
    if method not in METHODS_WITHOUT_VERSION and not resolved.get("version"):
        errors.append(f"{spec.key}: method {method} requires version")
    if method in PACKAGE_METHODS and not resolved.get("packages"):
        errors.append(
            f"{spec.key}: method {method} has no packages (install.{method} is empty)"
        )
    if method == "binary":
        assets = native.get("assets") or {}
        for platform in declared:
            effective = platform_native_install(native, platform)
            effective_assets = effective.get("assets") or {}
            if platform not in effective_assets and "any" not in effective_assets:
                errors.append(f"{spec.key}: binary has no asset for {platform}")
            if not effective.get("provenance"):
                errors.append(
                    f"{spec.key}: binary needs provenance (or provenance.unverified)"
                )
                break
        if not assets and not any(
            (native.get("overrides") or {}).get(p, {}).get("assets") for p in declared
        ):
            errors.append(f"{spec.key}: binary has no assets")
    if (
        method == "runtime_provided"
        and not native.get("requires")
        and not native.get("suggest")
    ):
        errors.append(
            f"{spec.key}: runtime_provided needs requires (runtime) or suggest (host-provided tool)"
        )
    for requirement in native.get("requires", []):
        if requirement["runtime"] not in runtime_names:
            errors.append(f"{spec.key}: unknown runtime {requirement['runtime']}")
    return errors


def build_schema_validator(descriptor_dir=None):
    descriptor_dir = descriptor_dir or get_descriptor_dir()
    with open(
        os.path.join(descriptor_dir, "schemas", SCHEMA_FILE), "r", encoding="utf-8"
    ) as f:
        schema = json.load(f)
    native_schema = dict(schema["definitions"]["native_install"])
    native_schema["definitions"] = schema["definitions"]
    return jsonschema.Draft7Validator(native_schema)


def validate_all(only=None):
    runtime_names = load_runtime_names()
    validator = build_schema_validator()
    errors = []
    specs = load_native_specs(only=only)
    for spec in specs:
        errors.extend(validate_spec(spec, runtime_names, validator))
    return specs, errors


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    argv = sys.argv[1:] if argv is None else argv
    specs, errors = validate_all(only=set(argv) or None)
    for error in errors:
        logging.error(error)
    logging.info(f"{len(specs)} linters checked, {len(errors)} native_install error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
