import argparse
import json
import logging
import os
import shutil
import sys
import uuid

import megalinter
from megalinter import config
from megalinter.native import config_writer
from megalinter.native import selection as native_selection
from megalinter.native import suggest as native_suggest
from megalinter.native.catalog import load_native_specs
from megalinter.native.context import (
    NativeError,
    cache_dir,
    current_libc,
    current_platform,
    find_git_bash,
    is_root,
    megalinter_home,
    require_git_bash,
)
from megalinter.native.installer import NativeInstaller
from megalinter.native.lock import check_lock_fresh, lock_path
from megalinter.native.resolve import resolve_native_install
from megalinter.native.runtimes import (
    POLICIES,
    detect_on_host,
    load_runtime_catalog,
    provisioned_info,
)
from megalinter.run import enable_crash_diagnostics

EXIT_ERROR = 2


def build_parser():
    parser = argparse.ArgumentParser(
        prog="megalinter",
        description="Run MegaLinter natively (without Docker), install and manage native linters",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser(
        "run", help="Lint a folder with the linters listed in NATIVE_LINTERS"
    )
    run.add_argument(
        "--input", default=None, help="Folder to lint (default: current folder)"
    )
    run.add_argument(
        "--trust-repo-commands",
        action="store_true",
        help=(
            "Run PRE_COMMANDS / POST_COMMANDS, load PLUGINS and fetch remote EXTENDS declared by the "
            "analyzed repository. Only for repositories you fully trust"
        ),
    )
    run.add_argument(
        "--runtimes",
        choices=POLICIES,
        default=None,
        help="Policy to install missing language runtimes (default: ask)",
    )
    add_report_arguments(run)

    prerun = commands.add_parser(
        "prerun",
        help=(
            "Analyze the repository without running any linter: suggest the linters "
            "to run natively and the configuration improvements"
        ),
    )
    prerun.add_argument(
        "--input", default=None, help="Folder to analyze (default: current folder)"
    )
    prerun.add_argument(
        "--runtimes",
        choices=POLICIES,
        default=None,
        help="Policy to install missing language runtimes (default: ask)",
    )

    setup = commands.add_parser(
        "setup",
        help=(
            "Choose the linters to run natively, write them in NATIVE_LINTERS, "
            "install them and run a first lint"
        ),
    )
    setup.add_argument(
        "--linters",
        default=None,
        help=(
            "Comma separated linter keys to use (example: PYTHON_BLACK,JAVASCRIPT_ES). "
            "Without it, the suggestion is shown and asked in a terminal"
        ),
    )
    setup.add_argument(
        "--input",
        default=None,
        help="Folder holding the configuration (default: current folder)",
    )
    setup.add_argument(
        "--runtimes",
        choices=POLICIES,
        default=None,
        help="Policy to install missing language runtimes (default: ask)",
    )
    setup.add_argument(
        "--no-run",
        action="store_true",
        help="Only write the configuration and install the linters",
    )
    add_report_arguments(setup)

    install = commands.add_parser(
        "install-linters",
        help="Install the linters listed in NATIVE_LINTERS (or the ones given as arguments)",
    )
    install.add_argument(
        "linters", nargs="*", help="Linter keys, example: PYTHON_BLACK"
    )
    install.add_argument(
        "--all",
        action="store_true",
        help=(
            "Install every linter matching the configuration. Discouraged: slower, and you must "
            "fully trust the security of all of them"
        ),
    )
    install.add_argument(
        "--input",
        default=None,
        help="Folder holding the configuration (default: current folder)",
    )
    install.add_argument(
        "--runtimes",
        choices=POLICIES,
        default=None,
        help="Policy to install missing language runtimes (default: ask)",
    )
    install.add_argument(
        "--force", action="store_true", help="Reinstall even when already installed"
    )

    uninstall = commands.add_parser(
        "uninstall-linters", help="Remove installed linters"
    )
    uninstall.add_argument("linters", nargs="+")

    listing = commands.add_parser(
        "list-linters", help="Show the native status of every linter"
    )
    listing.add_argument("--json", action="store_true")

    commands.add_parser("doctor", help="Check the native mode prerequisites")

    cache = commands.add_parser("cache", help="Manage the download and linter caches")
    cache.add_argument("action", choices=["prune"])
    return parser


def add_report_arguments(parser):
    parser.add_argument(
        "--json",
        action="store_true",
        help="Generate the JSON report (JSON_REPORTER=true)",
    )
    parser.add_argument(
        "--sarif",
        action="store_true",
        help="Generate the SARIF report (SARIF_REPORTER=true)",
    )


def prepare_environment(arguments):
    os.environ["MEGALINTER_NATIVE"] = "true"
    if getattr(arguments, "json", False):
        os.environ["JSON_REPORTER"] = "true"
    if getattr(arguments, "sarif", False):
        os.environ["SARIF_REPORTER"] = "true"
    workspace = os.path.abspath(getattr(arguments, "input", None) or os.getcwd())
    if not os.path.isdir(workspace):
        raise NativeError(f"Folder not found: {workspace}")
    os.environ["DEFAULT_WORKSPACE"] = workspace
    if getattr(arguments, "trust_repo_commands", False):
        os.environ["NATIVE_TRUST_REPO_COMMANDS"] = "true"
    if getattr(arguments, "runtimes", None):
        os.environ["NATIVE_INSTALL_RUNTIMES"] = arguments.runtimes
    config.refresh_env_snapshot()
    return workspace


def command_run(arguments):
    prepare_environment(arguments)
    logging.info(
        "MegaLinter native mode is in beta: please report problems at "
        "https://github.com/oxsecurity/megalinter/issues"
    )
    enable_crash_diagnostics()
    linter = megalinter.Megalinter({"cli": True, "request_id": str(uuid.uuid1())})
    linter.run()
    return 0


def run_native_prerun():
    os.environ["MEGALINTER_PRERUN"] = "true"
    config.refresh_env_snapshot()
    try:
        mega_linter = megalinter.Megalinter(
            {"cli": True, "request_id": str(uuid.uuid1())}
        )
        mega_linter.run()
    finally:
        del os.environ["MEGALINTER_PRERUN"]
        config.refresh_env_snapshot()
    return mega_linter


def command_prerun(arguments):
    prepare_environment(arguments)
    run_native_prerun()
    return 0


def parse_linter_keys(value):
    keys = [key.strip().upper() for key in value.split(",") if key.strip() != ""]
    if len(keys) == 0:
        raise NativeError("No linter chosen")
    known = {spec.key for spec in load_native_specs()}
    unknown = sorted(set(keys) - known)
    if len(unknown) > 0:
        raise NativeError(native_selection.unknown_linters_message(unknown))
    return keys


def read_answer(question):
    try:
        return input(question).strip().lower()
    except EOFError:
        # Windows reports the NUL device (no input at all) as a terminal
        raise NativeError("Setup cancelled: no answer was given") from None


def ask_native_linters(suggestion):
    recommended = suggestion["values"]
    logging.info(
        "Linters proposed for native mode (CI keeps running every active linter):"
    )
    logging.info("\n".join(native_suggest.format_native_rows(suggestion["details"])))
    if not sys.stdin.isatty():
        raise NativeError(
            "Choose the linters to run natively, for example: megalinter setup --linters "
            + ",".join(recommended)
        )
    answer = read_answer(
        f"Run these {len(recommended)} linters natively? [Y/n/e (edit the list)] "
    )
    if answer in ("", "y", "yes"):
        return recommended
    if answer in ("e", "edit"):
        return parse_linter_keys(
            read_answer("Linters to run natively (comma separated keys): ")
        )
    raise NativeError("Setup cancelled")


def choose_native_linters(arguments, prerun_report, configured):
    if arguments.linters:
        return parse_linter_keys(arguments.linters)
    suggestion = next(
        (
            item
            for item in prerun_report["suggestions"]
            if native_suggest.is_native_suggestion(item)
        ),
        None,
    )
    if suggestion is not None:
        return ask_native_linters(suggestion)
    if len(configured) > 0:
        return configured
    raise NativeError(
        "No linter of this repository can run without Docker: use Docker "
        "(npx mega-linter-runner without --native)"
    )


def command_setup(arguments):
    workspace = prepare_environment(arguments)
    mega_linter = run_native_prerun()
    config_file = config_writer.find_config_file(workspace)
    configured = config_writer.read_configured_linters(config_file)
    keys = choose_native_linters(arguments, mega_linter.prerun_report, configured)
    if keys != configured:
        config_writer.write_native_linters(config_file, keys)
        logging.info(f"NATIVE_LINTERS written in {config_file}: {', '.join(keys)}")
    install_explicit_linters(argparse.Namespace(linters=keys, force=False))
    if arguments.no_run:
        return 0
    return command_run(arguments)


def command_install_linters(arguments):
    prepare_environment(arguments)
    if arguments.linters:
        return install_explicit_linters(arguments)
    if arguments.all:
        os.environ["NATIVE_LINTERS"] = native_selection.ALL_KEYWORD
    os.environ["NATIVE_MISSING_LINTERS"] = "install"
    megalinter.Megalinter({"cli": True, "request_id": str(uuid.uuid1())})
    return 0


def install_explicit_linters(arguments):
    specs = load_native_specs()
    by_key = {spec.key: spec for spec in specs}
    unknown = [key for key in arguments.linters if key not in by_key]
    if unknown:
        raise NativeError("Unknown linter(s): " + ", ".join(unknown))
    installer = NativeInstaller()
    errors = []
    for key in arguments.linters:
        try:
            installer.install(by_key[key], force=arguments.force)
            logging.info(f"{key}: installed")
        except NativeError as e:
            logging.error(f"{key}: {e}")
            errors.append(key)
    if errors:
        raise NativeError("Not installed: " + ", ".join(errors))
    return 0


def command_uninstall_linters(arguments):
    by_key = {spec.key: spec for spec in load_native_specs()}
    installer = NativeInstaller()
    for key in arguments.linters:
        if key not in by_key:
            raise NativeError(f"Unknown linter: {key}")
        removed = installer.uninstall(by_key[key])
        logging.info(f"{key}: {'removed' if removed else 'was not installed'}")
    return 0


def command_list_linters(arguments):
    installer = NativeInstaller()
    rows = []
    for spec in load_native_specs():
        if spec.linter.get("disabled") is True:
            reason = spec.linter.get("disabled_reason", "disabled in MegaLinter")
            rows.append({"linter": spec.key, "status": "disabled", "reason": reason})
            continue
        status, reason = installer.status(spec)
        row = {"linter": spec.key, "status": status, "reason": reason}
        if resolve_native_install(spec)["method"] == "runtime_provided":
            # The tool comes from the host: MegaLinter only knows the version of its Docker image
            row["host_tool"] = True
            row["docker_version"] = installer.pinned_host_version(spec)
        rows.append(row)
    if arguments.json:
        logging.info(json.dumps(rows, indent=2))
        return 0
    for row in rows:
        suffix = f" - {row['reason']}" if row["reason"] else ""
        if row.get("host_tool") and row["status"] != "unsupported":
            suffix += " - uses the version installed on this machine"
            if row["docker_version"]:
                suffix += f" (Docker image: {row['docker_version']})"
        logging.info(f"{row['linter']:<40} {row['status']}{suffix}")
    return 0


def command_doctor(arguments):
    problems = 0
    home = megalinter_home()
    logging.info(f"Platform: {current_platform()} ({current_libc()})")
    logging.info(f"MEGALINTER_HOME: {home}")
    if is_root():
        logging.warning("Running as root: native mode is meant to run as a normal user")
    if sys.platform == "win32":
        try:
            logging.info(f"Git Bash: {require_git_bash()}")
        except NativeError as e:
            logging.error(str(e))
            problems += 1
    elif find_git_bash() is None:
        logging.error("bash not found")
        problems += 1
    uv = shutil.which("uv")
    logging.info(
        f"uv: {uv or 'not found (python linters then need a matching host python)'}"
    )
    catalog = load_runtime_catalog()
    for name, definition in catalog.items():
        host = detect_on_host(name, definition)
        provisioned = provisioned_info(home, name, definition)
        found = provisioned or host
        logging.info(
            f"runtime {name}: {found.version + ' (' + found.source + ')' if found else 'not found'}"
        )
    stale = 0
    for spec in load_native_specs():
        # Disabled linters have no lock: they can not be installed at all
        if spec.linter.get("disabled") is True:
            continue
        try:
            from_lock = os.path.isfile(lock_path(spec.key))
            if not from_lock:
                stale += 1
                continue
            with open(lock_path(spec.key), "r", encoding="utf-8") as f:
                check_lock_fresh(spec.key, resolve_native_install(spec), json.load(f))
        except NativeError:
            stale += 1
    if stale > 0:
        logging.warning(
            f"{stale} linter lock(s) missing or stale: those linters are temporarily unavailable natively"
        )
    return 1 if problems else 0


def command_cache(arguments):
    folder = cache_dir(megalinter_home())
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    logging.info(f"Cache cleared: {folder}")
    return 0


COMMANDS = {
    "run": command_run,
    "prerun": command_prerun,
    "setup": command_setup,
    "install-linters": command_install_linters,
    "uninstall-linters": command_uninstall_linters,
    "list-linters": command_list_linters,
    "doctor": command_doctor,
    "cache": command_cache,
}


def main(argv=None):
    # Redirected output (pre-commit, CI logs) uses the legacy code page on Windows: messages of
    # tools with other characters (uv errors...) made logging fail instead of showing them
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and not stream.isatty():
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    arguments = build_parser().parse_args(argv)
    try:
        return COMMANDS[arguments.command](arguments)
    except NativeError as e:
        logging.error(str(e))
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
