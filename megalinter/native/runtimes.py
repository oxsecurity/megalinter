import logging
import os
import re
import shutil
import subprocess
import sys

import yaml

from megalinter import config
from megalinter.native import extract
from megalinter.native.context import (
    NativeError,
    cache_dir,
    current_libc,
    current_os_family,
    current_platform,
    runtimes_dir,
)
from megalinter.native.download import fetch_verified
from megalinter.native.lock import load_runtime_lock, platform_lock
from megalinter.native.state import read_state, update_state
from megalinter.utils import get_descriptor_dir

VERSION_TIMEOUT_SECONDS = 30
CONSTRAINT_REGEX = re.compile(r"^\s*(>=|<=|==|>|<)?\s*(\d+(?:\.\d+)*)\s*$")
POLICIES = ["ask", "auto", "never"]


class RuntimeInfo:
    def __init__(
        self, name, version, source, executable=None, path_dirs=None, env=None
    ):
        self.name = name
        self.version = version
        self.source = source
        self.executable = executable
        self.path_dirs = path_dirs or []
        self.env = env or {}


def load_runtime_catalog():
    with open(
        os.path.join(get_descriptor_dir(), "native-runtimes.yml"), "r", encoding="utf-8"
    ) as f:
        return yaml.safe_load(f)["runtimes"]


def version_tuple(version):
    numbers = re.findall(r"\d+", version.split("+")[0])
    return tuple(int(number) for number in numbers)


def satisfies(version, constraint):
    if not constraint:
        return True
    current = version_tuple(version)
    for clause in constraint.split(","):
        match = CONSTRAINT_REGEX.match(clause)
        if match is None:
            raise NativeError(f"Unsupported version constraint: {constraint}")
        operator = match.group(1) or "=="
        wanted = version_tuple(match.group(2))
        length = max(len(current), len(wanted))
        padded_current = current + (0,) * (length - len(current))
        padded_wanted = wanted + (0,) * (length - len(wanted))
        if operator == ">=" and not padded_current >= padded_wanted:
            return False
        if operator == ">" and not padded_current > padded_wanted:
            return False
        if operator == "<=" and not padded_current <= padded_wanted:
            return False
        if operator == "<" and not padded_current < padded_wanted:
            return False
        if operator == "==" and not padded_current == padded_wanted:
            return False
    return True


def detect_on_host(name, definition, search_path=None):
    detect = definition["detect"]
    for executable in detect["executables"]:
        found = shutil.which(executable, path=search_path)
        if found is None:
            continue
        command = [
            found if part == "{{EXECUTABLE}}" else part
            for part in detect["version_command"]
        ]
        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=VERSION_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        output = process.stdout.decode("utf-8", errors="replace")
        match = re.search(detect["version_regex"], output)
        if match:
            version = match.group(1)
            # Java 8 and older report 1.x
            if name == "java" and version.startswith("1."):
                version = version[2:]
            executable_dir = os.path.dirname(os.path.realpath(found))
            env = {
                key: value.replace("{{EXECUTABLE_DIR}}", executable_dir)
                for key, value in (detect.get("env") or {}).items()
            }
            return RuntimeInfo(name, version, "host", executable=found, env=env)
    return None


def provisioned_runtime_dir(home, name, version):
    return os.path.join(runtimes_dir(home), name, version)


def platform_provision(definition):
    provision = definition.get("provision") or {}
    overrides = (provision.get("overrides") or {}).get(current_platform(), {})
    return {
        key: value for key, value in provision.items() if key != "overrides"
    } | overrides


def provisioned_info(home, name, definition):
    provision = platform_provision(definition)
    state_entry = read_state(home)["runtimes"].get(name)
    if not state_entry or state_entry.get("platform") != current_platform():
        return None
    install_dir = state_entry["dir"]
    if not os.path.isdir(install_dir):
        return None
    path_dirs = [os.path.join(install_dir, p) for p in provision.get("path", ["."])]
    env = {
        key: value.replace("{{NATIVE_INSTALL_DIR}}", install_dir)
        for key, value in (provision.get("env") or {}).items()
    }
    return RuntimeInfo(
        name, state_entry["version"], "provisioned", path_dirs=path_dirs, env=env
    )


def can_provision(definition):
    provision = platform_provision(definition)
    if not provision:
        return False
    if provision.get("via") == "uv":
        return shutil.which("uv") is not None
    if provision.get("libc") == "glibc" and current_libc() == "musl":
        return False
    return current_platform() in (provision.get("assets") or {}) or "any" in (
        provision.get("assets") or {}
    )


def suggest_command(definition):
    return (definition.get("suggest") or {}).get(current_os_family())


def provision_runtime(name, definition, home, offline=False):
    lock = load_runtime_lock(name)
    entry = platform_lock(lock, current_platform())
    version = entry["version"]
    install_dir = provisioned_runtime_dir(home, name, version)
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir)
    temp_dir = install_dir + ".tmp"
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    for asset in entry["assets"]:
        archive = fetch_verified(
            asset["url"], asset["sha256"], asset.get("size"), cache_dir(home), offline
        )
        extract.extract_archive(
            archive,
            asset.get("archive", "none"),
            temp_dir,
            asset.get("strip_components", 0),
            asset.get("name"),
        )
    os.makedirs(os.path.dirname(install_dir), exist_ok=True)
    os.replace(temp_dir, install_dir)
    update_state(
        home,
        "runtimes",
        name,
        {"version": version, "dir": install_dir, "platform": current_platform()},
    )
    logging.info(f"[native] Installed runtime {name} {version} in {install_dir}")
    return provisioned_info(home, name, definition)


def ask_user(question):
    if not sys.stdin.isatty():
        return False
    answer = input(f"{question} [y/N] ")
    return answer.strip().lower() in ("y", "yes")


def find_runtime(name, constraint, home, policy="ask", offline=False, catalog=None):
    catalog = catalog or load_runtime_catalog()
    definition = catalog[name]
    provisioned = provisioned_info(home, name, definition)
    if provisioned and satisfies(provisioned.version, constraint):
        return provisioned
    ignore_host = config.get(None, "NATIVE_IGNORE_HOST_RUNTIMES", "false") == "true"
    host = None if ignore_host else detect_on_host(name, definition)
    if host and satisfies(host.version, constraint):
        return host
    if (
        ignore_host is False
        and name == "python"
        and satisfies(".".join(str(part) for part in sys.version_info[:3]), constraint)
    ):
        return RuntimeInfo(
            name,
            ".".join(str(part) for part in sys.version_info[:3]),
            "host",
            executable=sys.executable,
        )
    if can_provision(definition) and platform_provision(definition).get("via") != "uv":
        wanted = f"{name} {constraint or ''}".strip()
        if policy == "auto" or (
            policy == "ask"
            and ask_user(f"{wanted} is required. Install it in {runtimes_dir(home)}?")
        ):
            return provision_runtime(name, definition, home, offline)
    return None


def missing_runtime_message(name, constraint, definition):
    message = f"Runtime {name}{(' ' + constraint) if constraint else ''} not found."
    command = suggest_command(definition)
    if command:
        message += f" Install it with: {command}"
    if can_provision(definition):
        message += (
            " Or allow MegaLinter to install it with NATIVE_INSTALL_RUNTIMES=auto."
        )
    return message


def resolve_requirements(requirements, home, policy="ask", offline=False):
    catalog = load_runtime_catalog()
    infos = []
    for requirement in requirements or []:
        name = requirement["runtime"]
        info = find_runtime(
            name, requirement.get("version"), home, policy, offline, catalog
        )
        if info is None:
            raise NativeError(
                missing_runtime_message(name, requirement.get("version"), catalog[name])
            )
        infos.append(info)
    return infos
