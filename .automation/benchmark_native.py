#!/usr/bin/env python3
# Benchmark of MegaLinter native mode against Docker (.github/workflows/benchmark-native.yml)
#
#   prepare  copies the demo repository (.automation/test/benchmark_native) in a new git repository
#   native   measures native mode with the published packages: install, first and warm runs, fixes,
#            single file run, npx overhead, disk usage of ~/.megalinter, peak memory
#   docker   measures Docker mode: image pulls (duration, sizes), first and warm runs
#   summary  merges the JSON results of every job into Markdown tables
#
# Lint runs exit with a non-zero code because of the problems planted in the demo repository:
# exit codes are recorded, they do not stop the benchmark.
import argparse
import glob
import json
import logging
import os
import platform
import re
import shutil
import signal
import statistics
import subprocess
import sys
import threading
import time
import urllib.request
from typing import Any, Callable

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(REPO_HOME, ".automation", "test", "benchmark_native")
LINTERS = [
    "PYTHON_RUFF",
    "PYTHON_BLACK",
    "YAML_YAMLLINT",
    "MARKDOWN_MARKDOWNLINT",
    "BASH_SHELLCHECK",
    "REPOSITORY_BETTERLEAKS",
]
RUNNER_PACKAGE = "mega-linter-runner@beta"
DOCKER_IMAGES = {
    "full": "ghcr.io/oxsecurity/megalinter:beta",
    "python": "ghcr.io/oxsecurity/megalinter-python:beta",
}
WARM_RUNS = 3
STEP_TIMEOUT_SECONDS = 1800
PLATFORMS_ORDER = [
    "linux/amd64",
    "linux/arm64",
    "darwin/amd64",
    "darwin/arm64",
    "windows/amd64",
]
# Exit code of a lint run that found the planted problems
LINT_ERRORS_FOUND = 1
SINGLE_FILE = "src/app.py"

Result = dict[str, Any]


def megalinter_home() -> str:
    return os.environ.get("MEGALINTER_HOME") or os.path.join(
        os.path.expanduser("~"), ".megalinter"
    )


# The job environment, without the GitHub Actions variables that the Docker runs do not
# receive either: GITHUB_WORKSPACE would point MegaLinter to the checkout of this repository,
# GITHUB_STEP_SUMMARY would publish its reports in the summary of the benchmark job
def benchmark_environment() -> dict[str, str]:
    return {
        key: value for key, value in os.environ.items() if not key.startswith("GITHUB_")
    }


def kill_process_tree(process: subprocess.Popen) -> None:
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(process.pid)],
            check=False,
            capture_output=True,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


# Runs a command, its output going to a log file. On Linux and macOS, os.wait4 returns the
# resource usage of the command: ru_maxrss is the peak resident memory of the LARGEST single
# process of its tree (not the sum of the processes running at the same time)
def run_measured(command: list[str], cwd: str, log_file: str) -> Result:
    executable = shutil.which(command[0]) or command[0]
    state = {"timed_out": False}

    def on_timeout() -> None:
        state["timed_out"] = True
        kill_process_tree(process)

    max_rss_mb = None
    with open(log_file, "w", encoding="utf-8", errors="replace") as log:
        log.write("$ " + " ".join(command) + "\n")
        log.flush()
        start = time.perf_counter()
        process = subprocess.Popen(
            [executable, *command[1:]],
            cwd=cwd,
            env=benchmark_environment(),
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=os.name != "nt",
        )
        timer = threading.Timer(STEP_TIMEOUT_SECONDS, on_timeout)
        timer.start()
        try:
            if hasattr(os, "wait4"):
                _pid, status, usage = os.wait4(process.pid, 0)
                return_code = os.waitstatus_to_exitcode(status)
                process.returncode = return_code
                divider = 1024 * 1024 if sys.platform == "darwin" else 1024
                max_rss_mb = round(usage.ru_maxrss / divider, 1)
            else:
                return_code = process.wait()
        finally:
            timer.cancel()
        seconds = time.perf_counter() - start
    return {
        "command": " ".join(command),
        "seconds": round(seconds, 3),
        "return_code": return_code,
        "timed_out": state["timed_out"],
        "max_rss_mb": max_rss_mb,
    }


def log_tail(log_file: str, lines: int = 15) -> list[str]:
    with open(log_file, encoding="utf-8", errors="replace") as file:
        return file.read().splitlines()[-lines:]


def read_json_report(report_dir: str) -> dict[str, Result]:
    with open(
        os.path.join(report_dir, "mega-linter-report.json"), encoding="utf-8"
    ) as file:
        report = json.load(file)
    results = {}
    for linter in report.get("linters", []):
        results[linter.get("name")] = {
            "errors": linter.get("total_number_errors"),
            "warnings": linter.get("total_number_warnings"),
            "fixed": linter.get("number_fixed"),
            "elapsed_s": linter.get("elapsed_time_s"),
            "status": linter.get("status"),
        }
    return results


# Fallback when there is no JSON report: the SUMMARY table of megalinter.log
# | âœ… PYTHON | ruff | list_of_files | 2 | | 1 | | 0 | 0.51s |
def read_log_summary(report_dir: str) -> dict[str, Result]:
    results: dict[str, Result] = {}
    with open(
        os.path.join(report_dir, "megalinter.log"), encoding="utf-8", errors="replace"
    ) as file:
        lines = file.read().splitlines()
    for line in lines:
        if "|" not in line:
            continue
        # Anything before the first "|" (log prefix) is dropped with the first element
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 9 or not cells[8].endswith("s"):
            continue
        try:
            elapsed = float(cells[8][:-1])
            errors = int(cells[5])
        except ValueError:
            continue
        descriptor = cells[0].split()[-1]
        key = f"{descriptor}_{cells[1]}".upper().replace("-", "_")
        results[key] = {
            "errors": errors,
            "warnings": int(cells[7]) if cells[7].isdigit() else None,
            "fixed": cells[4] or None,
            "elapsed_s": elapsed,
            "status": cells[0].split()[0],
        }
    return results


def read_linter_results(workspace: str) -> tuple[dict[str, Result], str | None]:
    report_dir = os.path.join(workspace, "megalinter-reports")
    readers: list[tuple[str, Callable[[str], dict[str, Result]]]] = [
        ("mega-linter-report.json", read_json_report),
        ("megalinter.log", read_log_summary),
    ]
    for file_name, reader in readers:
        if os.path.isfile(os.path.join(report_dir, file_name)):
            try:
                return reader(report_dir), file_name
            except (OSError, ValueError) as error:
                logging.warning(f"Unable to read {file_name}: {error}")
    return {}, None


def git(workspace: str, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


# Back to the committed demo repository: no fixes, no reports, no tool cache from a previous run.
# Files written by a Docker container belong to root: they are removed with sudo
def reset_workspace(workspace: str, use_sudo: bool = False) -> None:
    untracked = [
        path
        for path in git(workspace, "ls-files", "--others", "--directory").splitlines()
        if path
    ]
    if untracked and use_sudo:
        subprocess.run(["sudo", "rm", "-rf", *untracked], cwd=workspace, check=True)
    for path in untracked if not use_sudo else []:
        full_path = os.path.join(workspace, path)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        elif os.path.exists(full_path):
            os.remove(full_path)
    if not use_sudo:
        git(workspace, "checkout", "--", ".")


def folder_size_mb(path: str) -> float:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            if not os.path.islink(file_path):
                try:
                    total += os.lstat(file_path).st_size
                except OSError:
                    pass
    return round(total / (1024 * 1024), 1)


def disk_usage(path: str) -> Result:
    if not os.path.isdir(path):
        return {"total_mb": None, "folders": {}}
    folders = {}
    for name in sorted(os.listdir(path)):
        if os.path.isdir(os.path.join(path, name)):
            folders[name] = folder_size_mb(os.path.join(path, name))
    return {"total_mb": folder_size_mb(path), "folders": folders}


def command_output(command: list[str]) -> str:
    try:
        return subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=60
        ).stdout.strip()
    except OSError:
        return ""


def total_memory_gb() -> float | None:
    if sys.platform.startswith("linux"):
        with open("/proc/meminfo", encoding="utf-8") as file:
            for line in file:
                if line.startswith("MemTotal:"):
                    return round(int(line.split()[1]) / (1024 * 1024), 1)
    if sys.platform == "darwin":
        value = command_output(["sysctl", "-n", "hw.memsize"])
        return round(int(value) / (1024**3), 1) if value.isdigit() else None
    if os.name == "nt":
        value = command_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory",
            ]
        )
        return round(int(value) / (1024**3), 1) if value.isdigit() else None
    return None


def cpu_model() -> str:
    if sys.platform.startswith("linux"):
        # lscpu also names ARM cores, that /proc/cpuinfo only lists by part number
        for line in command_output(["lscpu"]).splitlines():
            if line.startswith("Model name:"):
                return line.split(":", 1)[1].strip()
        return platform.machine()
    if sys.platform == "darwin":
        return command_output(["sysctl", "-n", "machdep.cpu.brand_string"])
    return platform.processor()


def new_results(mode: str, arguments: argparse.Namespace) -> Result:
    return {
        "mode": mode,
        "platform": arguments.platform,
        "runner": arguments.runner,
        "machine": {
            "os": platform.platform(),
            "cpu_model": cpu_model(),
            "cpu_count": os.cpu_count(),
            "memory_gb": total_memory_gb(),
        },
        "versions": {},
        "steps": [],
    }


class Benchmark:
    def __init__(self, mode: str, arguments: argparse.Namespace):
        self.workspace = os.path.abspath(arguments.demo)
        self.logs_dir = os.path.abspath(arguments.logs)
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(arguments.output_dir, exist_ok=True)
        self.output_file = os.path.join(
            arguments.output_dir,
            f"{mode}-{arguments.platform.replace('/', '-')}.json",
        )
        self.results = new_results(mode, arguments)
        self.use_sudo = mode == "docker"
        self.save()

    def save(self) -> None:
        with open(self.output_file, "w", encoding="utf-8") as file:
            json.dump(self.results, file, indent=2)

    def step(
        self,
        step_id: str,
        command: list[str],
        lint: bool = False,
        cwd: str | None = None,
    ) -> Result:
        if lint:
            reset_workspace(self.workspace, self.use_sudo)
        log_file = os.path.join(self.logs_dir, f"{step_id}.log")
        logging.info(f"::group::{step_id}: {' '.join(command)}")
        try:
            result = run_measured(command, cwd or self.workspace, log_file)
        except OSError as error:
            result = {"command": " ".join(command), "error": str(error)}
        result["id"] = step_id
        result["lint"] = lint
        if lint:
            result["linters"], result["report"] = read_linter_results(self.workspace)
        if (lint and not result["linters"]) or (
            not lint and result.get("return_code") != 0
        ):
            result["error_excerpt"] = error_excerpt(log_file)
        for line in log_tail(log_file):
            logging.info(line)
        logging.info("::endgroup::")
        logging.info(
            f"{step_id}: {result.get('seconds')} s, exit code {result.get('return_code')}, "
            f"peak memory {result.get('max_rss_mb')} MB"
        )
        self.results["steps"].append(result)
        self.save()
        return result


# The error messages of a failed command, shown in the summary
def error_excerpt(log_file: str, max_lines: int = 3) -> list[str]:
    pattern = re.compile(r"\b(error|cause|fatal)\b\s*:", re.IGNORECASE)
    excerpt: list[str] = []
    for line in log_tail(log_file, 400):
        text = line.strip()[:300]
        if pattern.search(text) and text not in excerpt:
            excerpt.append(text)
    return excerpt[:max_lines]


def last_line(log_file: str) -> str:
    lines = [line for line in log_tail(log_file, 5) if line.strip()]
    return lines[-1].strip() if lines else ""


def core_executables() -> list[str]:
    pattern = os.path.join(megalinter_home(), "core", "*", "venv")
    executables = glob.glob(os.path.join(pattern, "bin", "megalinter")) + glob.glob(
        os.path.join(pattern, "Scripts", "megalinter.exe")
    )
    return sorted(executables, key=os.path.getmtime)


def command_native(arguments: argparse.Namespace) -> int:
    bench = Benchmark("native", arguments)
    npx = ["npx", "-y", RUNNER_PACKAGE]
    release = ["--release", "beta"]
    home = megalinter_home()
    bench.results["megalinter_home"] = home
    bench.results["disk_before"] = disk_usage(home)

    # npx downloads mega-linter-runner (empty npx cache)
    bench.step("npx_first_version", npx + ["--version"])
    bench.results["versions"]["runner"] = last_line(
        os.path.join(bench.logs_dir, "npx_first_version.log")
    )
    # Downloads and installs the MegaLinter core then the linters of NATIVE_LINTERS
    bench.step("install_linters", npx + ["--install-linters", *release])
    bench.results["disk_after_install"] = disk_usage(home)

    bench.step("native_npx_first_run", npx + ["--native", *release], lint=True)
    for index in range(1, WARM_RUNS + 1):
        bench.step(f"native_npx_warm_{index}", npx + ["--native", *release], lint=True)
    bench.step("native_fix", npx + ["--native", *release, "--fix"], lint=True)
    bench.step(
        "native_single_file",
        npx + ["--native", *release, "--fix", "--filesonly", SINGLE_FILE],
        lint=True,
    )
    reset_workspace(bench.workspace)

    executables = core_executables()
    bench.results["versions"]["core"] = [
        os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path))))
        for path in executables
    ]
    if executables:
        for index in range(1, WARM_RUNS + 1):
            bench.step(
                f"native_direct_warm_{index}",
                [executables[-1], "run", "--input", bench.workspace],
                lint=True,
            )
    else:
        logging.error(f"No megalinter executable found in {home}/core")

    # npx overhead: npx checks the registry for the beta tag at each call
    for index in range(1, WARM_RUNS + 1):
        bench.step(f"npx_version_{index}", npx + ["--version"])
    bench.step("npm_global_install", ["npm", "install", "-g", RUNNER_PACKAGE])
    for index in range(1, WARM_RUNS + 1):
        bench.step(f"global_version_{index}", ["mega-linter-runner", "--version"])
    for index in range(1, WARM_RUNS + 1):
        bench.step(
            f"native_global_warm_{index}",
            ["mega-linter-runner", "--native", *release],
            lint=True,
        )
    reset_workspace(bench.workspace)
    bench.results["disk_after_runs"] = disk_usage(home)
    bench.save()
    return 0


def registry_download_mb(image: str, image_platform: str) -> float | None:
    registry, _, rest = image.partition("/")
    repository, _, tag = rest.rpartition(":")
    accept = ", ".join(
        [
            "application/vnd.oci.image.index.v1+json",
            "application/vnd.docker.distribution.manifest.list.v2+json",
            "application/vnd.oci.image.manifest.v1+json",
            "application/vnd.docker.distribution.manifest.v2+json",
        ]
    )
    try:
        token_url = f"https://{registry}/token?scope=repository:{repository}:pull"
        with urllib.request.urlopen(token_url, timeout=60) as response:  # nosec B310
            token = json.load(response)["token"]

        def manifest(reference: str) -> Result:
            request = urllib.request.Request(
                f"https://{registry}/v2/{repository}/manifests/{reference}",
                headers={"Authorization": f"Bearer {token}", "Accept": accept},
            )
            with urllib.request.urlopen(request, timeout=60) as response:  # nosec B310
                return json.load(response)

        document = manifest(tag)
        if "manifests" in document:
            os_name, architecture = image_platform.split("/")[:2]
            digest = next(
                item["digest"]
                for item in document["manifests"]
                if item.get("platform", {}).get("os") == os_name
                and item.get("platform", {}).get("architecture") == architecture
            )
            document = manifest(digest)
        return round(
            sum(layer["size"] for layer in document["layers"]) / (1024 * 1024), 1
        )
    except (OSError, ValueError, KeyError, StopIteration) as error:
        logging.warning(f"Unable to read the manifest of {image}: {error}")
        return None


def docker_image_info(image: str) -> Result:
    output = command_output(
        [
            "docker",
            "image",
            "inspect",
            "--format",
            "{{.Size}}|{{index .RepoDigests 0}}|{{.Created}}",
            image,
        ]
    )
    parts = output.split("|")
    if len(parts) != 3 or not parts[0].isdigit():
        return {}
    return {
        "size_mb": round(int(parts[0]) / (1024 * 1024), 1),
        "digest": parts[1],
        "created": parts[2],
    }


def command_docker(arguments: argparse.Namespace) -> int:
    bench = Benchmark("docker", arguments)
    npx = ["npx", "-y", RUNNER_PACKAGE]
    image_platform = arguments.image_platform
    bench.results["image_platform"] = image_platform
    bench.results["versions"]["docker"] = command_output(
        ["docker", "version", "--format", "{{.Server.Version}}"]
    )
    bench.results["images"] = {}
    bench.step("npx_first_version", npx + ["--version"])
    bench.results["versions"]["runner"] = last_line(
        os.path.join(bench.logs_dir, "npx_first_version.log")
    )
    for flavor, image in DOCKER_IMAGES.items():
        # No layer shared with a previously pulled image: every pull starts empty
        subprocess.run(["docker", "image", "prune", "-af"], check=False)
        image_results = {
            "image": image,
            "download_mb": registry_download_mb(image, image_platform),
        }
        bench.step(
            f"pull_{flavor}", ["docker", "pull", "--platform", image_platform, image]
        )
        image_results.update(docker_image_info(image))
        bench.results["images"][flavor] = image_results
        bench.save()
        run_command = npx + [
            "--image",
            image,
            "--nodockerpull",
            "--platform",
            image_platform,
        ]
        bench.step(f"docker_{flavor}_first_run", run_command, lint=True)
        for index in range(1, WARM_RUNS + 1):
            bench.step(f"docker_{flavor}_warm_{index}", run_command, lint=True)
        reset_workspace(bench.workspace, use_sudo=True)
        subprocess.run(["docker", "image", "rm", image], check=False)
    bench.save()
    return 0


def command_prepare(arguments: argparse.Namespace) -> int:
    destination = os.path.abspath(arguments.dest)
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(FIXTURES_DIR, destination)
    git(destination, "-c", "init.defaultBranch=main", "init", "-q")
    git(destination, "config", "user.name", "MegaLinter benchmark")
    git(destination, "config", "user.email", "benchmark@example.com")
    git(destination, "config", "core.autocrlf", "false")
    git(destination, "add", ".")
    git(destination, "commit", "-q", "-m", "Demo repository")
    logging.info(f"Demo repository created in {destination}")
    return 0


# Summary


def load_results(input_dir: str) -> list[Result]:
    results = []
    for path in glob.glob(os.path.join(input_dir, "**", "*.json"), recursive=True):
        with open(path, encoding="utf-8") as file:
            results.append(json.load(file))

    def order(result: Result) -> tuple[int, int]:
        position = (
            PLATFORMS_ORDER.index(result["platform"])
            if result["platform"] in PLATFORMS_ORDER
            else len(PLATFORMS_ORDER)
        )
        return position, 0 if result["mode"] == "native" else 1

    return sorted(results, key=order)


def steps_by_id(result: Result) -> dict[str, Result]:
    return {step["id"]: step for step in result.get("steps", [])}


def seconds(step: Result | None) -> str:
    if step is None:
        return ""
    if step.get("error"):
        return "error"
    value = f"{step['seconds']:.2f}"
    if step.get("timed_out"):
        return value + " (timeout)"
    if step.get("lint") and not step.get("linters"):
        return value + " (failed)"
    if not step.get("lint") and step.get("return_code") != 0:
        return value + " (failed)"
    return value


# Median of the runs that worked: failed runs (no report) are left out
def median_seconds(steps: list[Result]) -> str:
    values = [
        step["seconds"]
        for step in steps
        if step.get("seconds") is not None
        and (step.get("linters") if step.get("lint") else step.get("return_code") == 0)
    ]
    return f"{statistics.median(values):.2f}" if values else ""


def number(value: Any) -> str:
    return "" if value is None else str(value)


# The first `text_columns` columns are left-aligned, the following ones (numbers) right-aligned
def table(header: list[str], rows: list[list[str]], text_columns: int = 2) -> list[str]:
    alignments = [":---"] * text_columns + ["---:"] * (len(header) - text_columns)
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(alignments) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines + [""]


def docker_label(result: Result) -> str:
    image_platform = result.get("image_platform", "linux/amd64")
    if image_platform != result["platform"]:
        return f"Docker ({image_platform} image, emulated)"
    return "Docker"


# Series of lint runs: (label, first run step id, warm runs step id prefix)
def lint_series(result: Result) -> list[tuple[str, str | None, str]]:
    if result["mode"] == "native":
        return [
            (
                "Native, `npx mega-linter-runner@beta`",
                "native_npx_first_run",
                "native_npx_warm_",
            ),
            ("Native, global `mega-linter-runner`", None, "native_global_warm_"),
            ("Native, `megalinter run`", None, "native_direct_warm_"),
        ]
    label = docker_label(result)
    return [
        (f"{label}, full image", "docker_full_first_run", "docker_full_warm_"),
        (f"{label}, python flavor", "docker_python_first_run", "docker_python_warm_"),
    ]


def warm_steps(steps: dict[str, Result], prefix: str) -> list[Result]:
    return [
        steps[f"{prefix}{index}"]
        for index in range(1, WARM_RUNS + 1)
        if f"{prefix}{index}" in steps
    ]


def section_machines(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        machine = result["machine"]
        versions = result.get("versions", {})
        runner_version = versions.get("runner", "").replace(
            "mega-linter-runner version ", ""
        )
        version_cells = [f"runner {runner_version}"]
        if versions.get("core"):
            version_cells.append("core " + ", ".join(versions["core"]))
        if versions.get("docker"):
            version_cells.append(f"Docker {versions['docker']}")
        rows.append(
            [
                result["platform"],
                result["mode"],
                f"`{result['runner']}`",
                machine.get("cpu_model") or "",
                number(machine.get("cpu_count")),
                number(machine.get("memory_gb")),
                "<br>".join(version_cells),
            ]
        )
    lines = ["## Runners", ""]
    lines += table(
        ["Platform", "Mode", "Runner", "CPU", "CPUs", "RAM (GB)", "Versions"], rows, 7
    )
    core_warnings = [
        result["platform"]
        for result in results
        if len(result.get("versions", {}).get("core", [])) > 1
    ]
    if core_warnings:
        lines += [
            "> A new MegaLinter beta was published during the native job of "
            + ", ".join(core_warnings)
            + ": some runs installed it, their durations include that install.",
            "",
        ]
    return lines


def section_install(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        steps = steps_by_id(result)
        if result["mode"] == "native":
            install = result.get("disk_after_install", {}).get("total_mb")
            rows.append(
                [
                    result["platform"],
                    "Native",
                    "npx first call (`--version`, empty npx cache)",
                    seconds(steps.get("npx_first_version")),
                    "",
                ]
            )
            rows.append(
                [
                    result["platform"],
                    "Native",
                    "`--install-linters` (empty `~/.megalinter`: core + 6 linters)",
                    seconds(steps.get("install_linters")),
                    f"{number(install)} MB on disk",
                ]
            )
            rows.append(
                [
                    result["platform"],
                    "Native",
                    "`npm install -g mega-linter-runner@beta`",
                    seconds(steps.get("npm_global_install")),
                    "",
                ]
            )
            continue
        rows.append(
            [
                result["platform"],
                docker_label(result),
                "npx first call (`--version`, empty npx cache)",
                seconds(steps.get("npx_first_version")),
                "",
            ]
        )
        for flavor, image in result.get("images", {}).items():
            rows.append(
                [
                    result["platform"],
                    docker_label(result),
                    f"`docker pull {image['image']}`",
                    seconds(steps.get(f"pull_{flavor}")),
                    f"{number(image.get('download_mb'))} MB download, "
                    f"{number(image.get('size_mb'))} MB on disk",
                ]
            )
    lines = ["## Install and download", ""]
    return lines + table(["Platform", "Mode", "Step", "Duration (s)", "Size"], rows, 3)


def section_runs(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        steps = steps_by_id(result)
        for label, first_id, prefix in lint_series(result):
            warm = warm_steps(steps, prefix)
            series = ([steps[first_id]] if first_id in steps else []) + warm
            if not series:
                continue
            warm_cells = [seconds(step) for step in warm]
            warm_cells += [""] * (WARM_RUNS - len(warm_cells))
            rows.append(
                [
                    result["platform"],
                    label,
                    seconds(steps.get(first_id)) if first_id else "",
                    *warm_cells,
                    median_seconds(warm),
                    ", ".join(number(step.get("return_code")) for step in series),
                ]
            )
    header = ["Platform", "Mode", "First run"]
    header += [f"Warm {index}" for index in range(1, WARM_RUNS + 1)]
    header += ["Warm median", "Exit codes"]
    lines = [
        "## Lint run duration (s)",
        "",
        "Wall-clock duration of the whole command, 6 linters on the demo repository. "
        "Exit code 1 is expected: the demo repository has planted problems.",
        "",
    ]
    return lines + table(header, rows)


def section_native_other_runs(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        if result["mode"] != "native":
            continue
        steps = steps_by_id(result)
        fix = steps.get("native_fix") or {}
        linters = fix.get("linters", {})
        fixed = [
            f"{key} {linters[key].get('fixed')}"
            for key in LINTERS
            if linters.get(key, {}).get("fixed")
        ]
        errors_left = [
            f"{key} {linters[key].get('errors')}" for key in LINTERS if key in linters
        ]
        rows.append(
            [
                result["platform"],
                seconds(steps.get("native_fix")),
                seconds(steps.get("native_single_file")),
                ", ".join(fixed),
                ", ".join(errors_left),
            ]
        )
    lines = [
        "## Native: fixes and single file",
        "",
        f"Through `npx mega-linter-runner@beta --native --release beta`. Single file: "
        f"`--fix --filesonly {SINGLE_FILE}` (project mode linters skipped).",
        "",
    ]
    return lines + table(
        [
            "Platform",
            "`--fix` run (s)",
            "Single file (s)",
            "Fixed (count of the report)",
            "Errors left after `--fix`",
        ],
        rows,
        1,
    )


def section_npx_overhead(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        if result["mode"] != "native":
            continue
        steps = steps_by_id(result)
        npx_versions = warm_steps(steps, "npx_version_")
        global_versions = warm_steps(steps, "global_version_")
        overhead = ""
        if npx_versions and global_versions:
            overhead = f"{float(median_seconds(npx_versions)) - float(median_seconds(global_versions)):.2f}"
        rows.append(
            [
                result["platform"],
                ", ".join(seconds(step) for step in npx_versions),
                median_seconds(npx_versions),
                ", ".join(seconds(step) for step in global_versions),
                median_seconds(global_versions),
                overhead,
                median_seconds(warm_steps(steps, "native_npx_warm_")),
                median_seconds(warm_steps(steps, "native_global_warm_")),
                median_seconds(warm_steps(steps, "native_direct_warm_")),
            ]
        )
    lines = [
        "## npx overhead (s)",
        "",
        "`npx mega-linter-runner@beta --version` (npx checks the registry for the beta tag) "
        "against a global install (`mega-linter-runner --version`), then the median of the "
        "warm native runs through each entry point.",
        "",
    ]
    return lines + table(
        [
            "Platform",
            "npx `--version`",
            "npx median",
            "global `--version`",
            "global median",
            "npx overhead",
            "Run via npx",
            "Run via global runner",
            "Run via `megalinter run`",
        ],
        rows,
        1,
    )


def section_disk(results: list[Result]) -> list[str]:
    native = [result for result in results if result["mode"] == "native"]
    folders = sorted(
        {
            name
            for result in native
            for name in result.get("disk_after_runs", {}).get("folders", {})
        }
    )
    rows = []
    for result in native:
        for moment in ["disk_after_install", "disk_after_runs"]:
            usage = result.get(moment, {})
            rows.append(
                [
                    result["platform"],
                    (
                        "after install"
                        if moment == "disk_after_install"
                        else "after all runs"
                    ),
                    number(usage.get("total_mb")),
                    *[number(usage.get("folders", {}).get(name)) for name in folders],
                ]
            )
    lines = [
        "## Disk usage (MB)",
        "",
        "Native: size of the files of `~/.megalinter` and of its folders. "
        "Docker: see the image sizes in [Install and download](#install-and-download).",
        "",
    ]
    return lines + table(
        ["Platform", "When", "Total", *[f"`{name}`" for name in folders]], rows
    )


def section_memory(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        if result["mode"] != "native":
            continue
        steps = steps_by_id(result)
        warm = [
            step["max_rss_mb"]
            for step in warm_steps(steps, "native_npx_warm_")
            if step.get("max_rss_mb") is not None
        ]
        direct = [
            step["max_rss_mb"]
            for step in warm_steps(steps, "native_direct_warm_")
            if step.get("max_rss_mb") is not None
        ]
        rows.append(
            [
                result["platform"],
                number((steps.get("install_linters") or {}).get("max_rss_mb")),
                number((steps.get("native_npx_first_run") or {}).get("max_rss_mb")),
                ", ".join(str(value) for value in warm),
                ", ".join(str(value) for value in direct),
                number((steps.get("native_fix") or {}).get("max_rss_mb")),
            ]
        )
    lines = [
        "## Native peak memory (MB)",
        "",
        "Peak resident memory of the largest single process of the command tree "
        "(`ru_maxrss` from `wait4`, the measure of `/usr/bin/time`), not the sum of the "
        "processes running at the same time. Not measured on Windows. "
        "Not measured for Docker runs: the processes run in the container, outside of the "
        "process tree of the `docker` client.",
        "",
    ]
    return lines + table(
        [
            "Platform",
            "`--install-linters`",
            "First run",
            "Warm runs (npx)",
            "Warm runs (`megalinter run`)",
            "`--fix` run",
        ],
        rows,
        1,
    )


def series_linter_values(steps: list[Result], key: str, field: str) -> list[Any]:
    return [
        step.get("linters", {}).get(key, {}).get(field)
        for step in steps
        if step.get("linters")
    ]


def section_linter_times(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        steps = steps_by_id(result)
        for label, _first_id, prefix in lint_series(result):
            warm = warm_steps(steps, prefix)
            if not warm:
                continue
            cells = []
            for key in LINTERS:
                values = [
                    value
                    for value in series_linter_values(warm, key, "elapsed_s")
                    if value is not None
                ]
                cells.append(f"{statistics.median(values):.2f}" if values else "")
            rows.append([result["platform"], label, *cells])
    lines = [
        "## Per-linter duration (s, median of the warm runs)",
        "",
        "Elapsed time of each linter as reported by MegaLinter (`elapsed_time_s` of "
        "`mega-linter-report.json`, the Elapsed time column of the console summary).",
        "",
    ]
    return lines + table(["Platform", "Mode", *[f"`{key}`" for key in LINTERS]], rows)


def section_errors(results: list[Result]) -> list[str]:
    rows = []
    reference: dict[str, Any] = {}
    differences = []
    for result in results:
        steps = steps_by_id(result)
        for label, first_id, prefix in lint_series(result):
            series = ([steps[first_id]] if first_id in steps else []) + warm_steps(
                steps, prefix
            )
            if not series:
                continue
            cells = []
            for key in LINTERS:
                values = series_linter_values(series, key, "errors")
                distinct = sorted({number(value) for value in values})
                cells.append("/".join(distinct) if distinct else "missing")
                if len(distinct) == 1:
                    reference.setdefault(key, distinct[0])
                    if reference[key] != distinct[0]:
                        differences.append(f"{result['platform']} {label} {key}")
                elif distinct:
                    differences.append(f"{result['platform']} {label} {key}")
            rows.append([result["platform"], label, *cells])
    lines = [
        "## Errors found per linter",
        "",
        "Over the first and warm runs of each mode (several values: they changed between runs).",
        "",
    ]
    lines += table(["Platform", "Mode", *[f"`{key}`" for key in LINTERS]], rows)
    if differences:
        lines += ["Different counts: " + "; ".join(differences), ""]
    elif rows:
        lines += [
            "Every platform and mode that produced a report finds the same number of errors.",
            "",
        ]
    return lines


def section_failures(results: list[Result]) -> list[str]:
    rows = []
    for result in results:
        for step in result.get("steps", []):
            expected = [0, LINT_ERRORS_FOUND] if step.get("lint") else [0]
            problem = ""
            if step.get("error"):
                problem = step["error"]
            elif step.get("timed_out"):
                problem = "timeout"
            elif step.get("return_code") not in expected:
                problem = f"exit code {step.get('return_code')}"
            elif step.get("lint") and not step.get("linters"):
                problem = "no report"
            if problem and step.get("error_excerpt"):
                excerpt = "<br>".join(
                    f"`{line.replace('`', '')}`" for line in step["error_excerpt"]
                )
                problem = f"{problem}: {excerpt.replace('|', '¦')}"
            if problem:
                rows.append(
                    [result["platform"], result["mode"], f"`{step['id']}`", problem]
                )
    lines = ["## Unexpected results", ""]
    if not rows:
        return lines + ["None.", ""]
    return lines + table(["Platform", "Mode", "Step", "Problem"], rows, 4)


def command_summary(arguments: argparse.Namespace) -> int:
    results = load_results(arguments.input)
    lines = [
        "# MegaLinter native mode benchmark",
        "",
        "Demo repository: `.automation/test/benchmark_native` (6 linters: "
        + ", ".join(f"`{key}`" for key in LINTERS)
        + "). Published packages: `mega-linter-runner@beta` (npm), `megalinter` beta (PyPI), "
        "`ghcr.io/oxsecurity/megalinter:beta` and `ghcr.io/oxsecurity/megalinter-python:beta`.",
        "",
    ]
    expected = {(platform_name, "native") for platform_name in PLATFORMS_ORDER}
    expected |= {("linux/amd64", "docker"), ("linux/arm64", "docker")}
    missing = sorted(expected - {(item["platform"], item["mode"]) for item in results})
    if missing:
        lines += [
            "> No results for: "
            + ", ".join(f"{mode} {platform_name}" for platform_name, mode in missing)
            + " (the job failed before writing them, see its log).",
            "",
        ]
    for section in [
        section_machines,
        section_install,
        section_runs,
        section_native_other_runs,
        section_npx_overhead,
        section_disk,
        section_memory,
        section_linter_times,
        section_errors,
        section_failures,
    ]:
        lines += section(results)
    with open(arguments.output, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))
    logging.info(f"Summary written in {arguments.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark of MegaLinter native mode against Docker"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Create the demo repository")
    prepare.add_argument("--dest", required=True)
    prepare.set_defaults(handler=command_prepare)
    for mode, handler in [("native", command_native), ("docker", command_docker)]:
        measure = commands.add_parser(mode, help=f"Measure {mode} mode")
        measure.add_argument("--demo", required=True, help="Demo repository")
        measure.add_argument("--platform", required=True, help="Example: linux/amd64")
        measure.add_argument("--runner", default="", help="Runner label")
        measure.add_argument("--output-dir", required=True)
        measure.add_argument("--logs", required=True, help="Folder of the step logs")
        if mode == "docker":
            measure.add_argument("--image-platform", default="linux/amd64")
        measure.set_defaults(handler=handler)
    summary = commands.add_parser("summary", help="Write the Markdown summary")
    summary.add_argument("--input", required=True, help="Folder of the JSON results")
    summary.add_argument("--output", required=True)
    summary.set_defaults(handler=command_summary)
    return parser


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    arguments = build_parser().parse_args()
    return arguments.handler(arguments)


if __name__ == "__main__":
    sys.exit(main())
