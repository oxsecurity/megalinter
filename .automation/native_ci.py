#!/usr/bin/env python3
# Helpers of the native mode CI workflows (.github/workflows/test-native.yml)
#
#   matrix   prints the GitHub Actions matrix: every linter supported natively on each runner
#            platform, split in shards, with the pytest expression of its test classes
#   prepare  installs on the current runner the host-provided tools of some linters
#            (the ones MegaLinter does not download itself, declared with `suggest`)
import argparse
import glob
import json
import logging
import os
import re
import subprocess
import sys

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_HOME)

from megalinter.native.catalog import load_native_specs  # noqa: E402
from megalinter.native.context import (  # noqa: E402
    current_os_family,
    current_platform,
)
from megalinter.native.resolve import (  # noqa: E402
    platform_native_install,
    resolve_native_install,
)
from megalinter.native.runtimes import (  # noqa: E402
    can_provision,
    detect_on_host,
    load_runtime_catalog,
)

RUNNERS = [
    {"os": "ubuntu-latest", "platform": "linux/amd64"},
    {"os": "ubuntu-24.04-arm", "platform": "linux/arm64"},
    {"os": "macos-15-intel", "platform": "darwin/amd64"},
    {"os": "macos-latest", "platform": "darwin/arm64"},
    {"os": "windows-latest", "platform": "windows/amd64"},
]
# Runtimes without a verifiable portable download, installed on the runner by a setup action
SETUP_ACTION_RUNTIMES = ["ruby", "r", "rust"]
SAFE_SUGGEST_PREFIXES = (
    "sudo apt-get install",
    "sudo apt install",
    "brew install",
    "choco install",
    "winget install",
    "cpan -T",
    "Rscript -e",
    "gem install",
)
TESTS_DIR = os.path.join(REPO_HOME, "megalinter", "tests", "test_megalinter", "linters")
DESCRIPTOR_REGEX = re.compile(r'descriptor_id = "([^"]+)"')
LINTER_REGEX = re.compile(r'linter_name = "([^"]+)"')


def test_modules():
    modules = {}
    for path in glob.glob(os.path.join(TESTS_DIR, "*_test.py")):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        descriptor = DESCRIPTOR_REGEX.search(content)
        linter = LINTER_REGEX.search(content)
        if descriptor and linter:
            modules[(descriptor.group(1), linter.group(1))] = os.path.basename(path)[
                :-3
            ]
    return modules


def is_host_provided(spec):
    return resolve_native_install(spec)["method"] == "runtime_provided"


def supported_on(spec, platform):
    resolved = resolve_native_install(spec)
    return platform in resolved.get("platforms", []), resolved


def build_matrix(shard_size):
    catalog = load_runtime_catalog()
    modules = test_modules()
    specs = load_native_specs()
    include = []
    for runner in RUNNERS:
        entries = []
        for spec in specs:
            if spec.linter.get("disabled") is True:
                continue
            supported, resolved = supported_on(spec, runner["platform"])
            if not supported:
                continue
            effective = platform_native_install(resolved, runner["platform"])
            runtimes = {
                requirement["runtime"]
                for requirement in effective.get("requires", [])
                if requirement["runtime"] in SETUP_ACTION_RUNTIMES
                and not catalog[requirement["runtime"]].get("provision")
            }
            entries.append((spec, runtimes))
        entries.sort(key=lambda entry: entry[0].key)
        for index in range(0, len(entries), shard_size):
            shard = entries[index : index + shard_size]
            tests = [
                modules[(spec.descriptor_id, spec.linter_name)]
                for spec, _ in shard
                if (spec.descriptor_id, spec.linter_name) in modules
            ]
            include.append(
                {
                    **runner,
                    "name": f"{runner['platform']} #{index // shard_size + 1}",
                    "linters": ",".join(
                        spec.key for spec, _ in shard if not is_host_provided(spec)
                    ),
                    "host_linters": ",".join(
                        spec.key for spec, _ in shard if is_host_provided(spec)
                    ),
                    "tests": " or ".join(tests),
                    "host_runtimes": ",".join(
                        sorted(set().union(*[r for _, r in shard]))
                    ),
                }
            )
    return {"include": include}


def run_suggestion(command):
    # "Install X from your distribution (example: sudo apt install x)" -> the example command
    example = re.search(r"\(example: ([^)]+)\)", command)
    command = example.group(1) if example else command.split(" (")[0]
    command = command.strip()
    if not command.startswith(SAFE_SUGGEST_PREFIXES):
        logging.info(f"not automated: {command}")
        return
    if (
        command.startswith(("sudo apt-get install", "sudo apt install"))
        and " -y" not in command
    ):
        command += " -y"
    logging.info(f"running: {command}")
    result = subprocess.run(command, shell=True, check=False)
    if result.returncode != 0:
        logging.warning(f"failed ({result.returncode}): {command}")


# Install what MegaLinter does not download itself: host-provided tools, and runtimes that
# have no verified portable build on this platform (php on Linux and macOS...)
def prepare(keys):
    family = current_os_family()
    catalog = load_runtime_catalog()
    for spec in load_native_specs(only=set(keys)):
        native = platform_native_install(
            resolve_native_install(spec), current_platform()
        )
        for requirement in native.get("requires", []):
            definition = catalog[requirement["runtime"]]
            if can_provision(definition) or detect_on_host(
                requirement["runtime"], definition
            ):
                continue
            suggestion = (definition.get("suggest") or {}).get(family)
            if suggestion:
                run_suggestion(suggestion)
        if native["method"] != "runtime_provided":
            continue
        suggestion = (native.get("suggest") or {}).get(family)
        if suggestion:
            run_suggestion(suggestion)


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    matrix = commands.add_parser("matrix")
    matrix.add_argument("--shard-size", type=int, default=10)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--linters", required=True)
    arguments = parser.parse_args(argv)
    if arguments.command == "matrix":
        sys.stdout.write(json.dumps(build_matrix(arguments.shard_size)) + "\n")
    else:
        prepare([key for key in arguments.linters.split(",") if key])
    return 0


if __name__ == "__main__":
    sys.exit(main())
