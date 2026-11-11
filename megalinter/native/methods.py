import json
import logging
import os
import shlex
import shutil
import subprocess
import sys

from megalinter.native import extract
from megalinter.native.context import (
    NativeError,
    cache_dir,
    current_os_family,
    is_posix,
)
from megalinter.native.download import fetch_verified
from megalinter.native.runtimes import satisfies

INSTALL_TIMEOUT_SECONDS = 1800
OUTPUT_TAIL_LINES = 30
PYTHON_RUNTIME = "python"


class InstallContext:
    def __init__(
        self,
        key,
        native,
        lock,
        platform_entry,
        destination,
        home,
        env,
        tool_names,
        offline,
    ):
        self.key = key
        self.native = native
        self.common = lock.get("common", {})
        self.platform_entry = platform_entry
        self.destination = destination
        self.home = home
        self.env = env
        self.tool_names = tool_names
        self.offline = offline


class InstallResult:
    def __init__(self, path_dirs=None, env=None):
        self.path_dirs = path_dirs or []
        self.env = env or {}


def run_command(command, env, cwd=None):
    logging.debug(f"[native] running {command}")
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=INSTALL_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        raise NativeError(f"Unable to run {' '.join(command)}: {e}") from e
    if process.returncode != 0:
        tail = "\n".join(
            process.stdout.decode("utf-8", errors="replace").splitlines()[
                -OUTPUT_TAIL_LINES:
            ]
        )
        raise NativeError(f"{' '.join(command)} failed ({process.returncode}):\n{tail}")


def find_tool(name, env):
    found = shutil.which(name, path=env.get("PATH"))
    if found is None:
        raise NativeError(f"{name} not found in PATH")
    return found


def executable_extensions():
    return (".exe", ".cmd", ".bat", ".ps1", "") if not is_posix() else ("",)


def venv_bin_dir(venv):
    return os.path.join(venv, "bin" if is_posix() else "Scripts")


def venv_python(venv):
    return os.path.join(venv_bin_dir(venv), "python" if is_posix() else "python.exe")


def python_constraint(native):
    for requirement in native.get("requires", []):
        if requirement["runtime"] == PYTHON_RUNTIME:
            return requirement.get("version")
    return None


def install_pip(ctx):
    venv = os.path.join(ctx.destination, "venv")
    requirements_file = os.path.join(ctx.destination, "requirements.lock")
    with open(requirements_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(ctx.common["requirements"])
    binary_only = (
        [] if ctx.native.get("allow_source_build") else ["--only-binary", ":all:"]
    )
    uv = shutil.which("uv")
    if uv:
        constraint = python_constraint(ctx.native)
        run_command(
            [
                uv,
                "venv",
                venv,
                "--no-config",
                *(["--python", constraint] if constraint else []),
            ],
            ctx.env,
        )
        run_command(
            [
                uv,
                "pip",
                "install",
                "--no-config",
                "--python",
                venv_python(venv),
                "--require-hashes",
                "--no-deps",
                *binary_only,
                "-r",
                requirements_file,
            ],
            ctx.env,
        )
    else:
        if not satisfies(
            ".".join(str(part) for part in sys.version_info[:3]),
            python_constraint(ctx.native),
        ):
            raise NativeError(
                f"{ctx.key} needs Python {python_constraint(ctx.native)} and uv is not installed "
                "(install uv: https://docs.astral.sh/uv/getting-started/installation/)"
            )
        run_command([sys.executable, "-m", "venv", venv], ctx.env)
        run_command(
            [
                venv_python(venv),
                "-m",
                "pip",
                "install",
                "--require-hashes",
                "--no-deps",
                "--disable-pip-version-check",
                *(["--only-binary=:all:"] if binary_only else []),
                "-r",
                requirements_file,
            ],
            ctx.env,
        )
    return InstallResult([venv_bin_dir(venv)], {"VIRTUAL_ENV": venv})


def install_npm(ctx):
    for file_name, key in (
        ("package.json", "package_json"),
        ("package-lock.json", "package_lock"),
    ):
        with open(
            os.path.join(ctx.destination, file_name),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(ctx.common[key], f, indent=2)
    npm = find_tool("npm", ctx.env)
    run_command(
        [npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
        ctx.env,
        cwd=ctx.destination,
    )
    for allowed in ctx.native.get("allow_install_scripts", []):
        run_command([npm, "rebuild", allowed["package"]], ctx.env, cwd=ctx.destination)
    return InstallResult(
        [os.path.join(ctx.destination, "node_modules", ".bin")],
        {"NODE_PATH": os.path.join(ctx.destination, "node_modules")},
    )


def shim_directory(destination):
    return os.path.join(destination, "shims")


def write_shim(destination, name, command_parts):
    folder = shim_directory(destination)
    os.makedirs(folder, exist_ok=True)
    script = os.path.join(folder, name)
    with open(script, "w", encoding="utf-8", newline="\n") as f:
        f.write(
            "#!/bin/sh\nexec "
            + " ".join(shlex.quote(part) for part in command_parts)
            + ' "$@"\n'
        )
    os.chmod(script, 0o755)
    if not is_posix():
        quoted = " ".join('"' + part.replace('"', '""') + '"' for part in command_parts)
        with open(script + ".cmd", "w", encoding="utf-8", newline="\r\n") as f:
            f.write(f"@echo off\r\n{quoted} %*\r\n")


def executable_basename(path):
    base = os.path.basename(path)
    for extension in (".exe", ".cmd", ".bat"):
        if base.lower().endswith(extension):
            return base[: -len(extension)]
    return base


def create_executables(ctx):
    path_dirs = []
    for name, target in (ctx.native.get("executables") or {}).items():
        if isinstance(target, str):
            absolute = os.path.join(ctx.destination, *target.split("/"))
            if executable_basename(target) == name:
                directory = os.path.dirname(absolute)
                if directory not in path_dirs:
                    path_dirs.append(directory)
            else:
                write_shim(ctx.destination, name, [absolute])
        else:
            args = [
                part.replace("{{NATIVE_INSTALL_DIR}}", ctx.destination)
                for part in target.get("args", [])
            ]
            write_shim(ctx.destination, name, [target["launcher"], *args])
    if os.path.isdir(shim_directory(ctx.destination)):
        path_dirs.append(shim_directory(ctx.destination))
    return path_dirs


def install_binary(ctx):
    for asset in ctx.platform_entry["assets"]:
        archive = fetch_verified(
            asset["url"],
            asset["sha256"],
            asset.get("size"),
            cache_dir(ctx.home),
            ctx.offline,
        )
        extract.extract_archive(
            archive,
            asset.get("archive", "none"),
            ctx.destination,
            asset.get("strip_components", 0),
            asset.get("name"),
        )
    path_dirs = create_executables(ctx)
    for relative in ctx.native.get("path", []):
        path_dirs.append(os.path.normpath(os.path.join(ctx.destination, relative)))
    if not path_dirs:
        path_dirs = [ctx.destination]
    env = {
        name: value.replace("{{NATIVE_INSTALL_DIR}}", ctx.destination)
        for name, value in (ctx.native.get("env") or {}).items()
    }
    return InstallResult(path_dirs, env)


def install_gem(ctx):
    with open(
        os.path.join(ctx.destination, "Gemfile"), "w", encoding="utf-8", newline="\n"
    ) as f:
        f.write(ctx.common["gemfile"])
    with open(
        os.path.join(ctx.destination, "Gemfile.lock"),
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(ctx.common["gemfile_lock"])
    env = {
        **ctx.env,
        "BUNDLE_GEMFILE": os.path.join(ctx.destination, "Gemfile"),
        "BUNDLE_APP_CONFIG": os.path.join(ctx.destination, ".bundle"),
        "BUNDLE_FROZEN": "true",
        "BUNDLE_PATH": os.path.join(ctx.destination, "vendor"),
    }
    run_command([find_tool("bundle", env), "install"], env, cwd=ctx.destination)
    for name in ctx.tool_names:
        write_shim(ctx.destination, name, ["bundle", "exec", name])
    return InstallResult(
        [shim_directory(ctx.destination)],
        {
            "BUNDLE_GEMFILE": env["BUNDLE_GEMFILE"],
            "BUNDLE_APP_CONFIG": env["BUNDLE_APP_CONFIG"],
            "BUNDLE_FROZEN": "true",
            "BUNDLE_PATH": env["BUNDLE_PATH"],
        },
    )


def install_dotnet_tool(ctx):
    source = os.path.join(ctx.destination, "packages")
    tools = os.path.join(ctx.destination, "tools")
    os.makedirs(source, exist_ok=True)
    for asset in ctx.platform_entry["assets"]:
        archive = fetch_verified(
            asset["url"],
            asset["sha256"],
            asset.get("size"),
            cache_dir(ctx.home),
            ctx.offline,
        )
        shutil.copyfile(archive, os.path.join(source, asset["name"]))
    env = {**ctx.env, "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"}
    run_command(
        [
            find_tool("dotnet", env),
            "tool",
            "install",
            ctx.platform_entry["package"],
            "--version",
            ctx.platform_entry["version"],
            "--tool-path",
            tools,
            "--add-source",
            source,
            "--ignore-failed-sources",
        ],
        env,
    )
    return InstallResult([tools], {"DOTNET_CLI_TELEMETRY_OPTOUT": "1"})


def install_powershell_module(ctx):
    modules = os.path.join(ctx.destination, "Modules")
    for asset in ctx.platform_entry["assets"]:
        archive = fetch_verified(
            asset["url"],
            asset["sha256"],
            asset.get("size"),
            cache_dir(ctx.home),
            ctx.offline,
        )
        target = os.path.join(modules, asset["module"], asset["module_version"])
        extract.extract_archive(archive, "zip", target)
    return InstallResult(
        [], {"PSModulePath": modules + os.pathsep + ctx.env.get("PSModulePath", "")}
    )


def install_go(ctx):
    binaries = os.path.join(ctx.destination, "bin")
    work = os.path.join(ctx.destination, "work")
    os.makedirs(work)
    env = {
        **ctx.env,
        "GOBIN": binaries,
        "GOPATH": os.path.join(ctx.destination, "gopath"),
        "GOFLAGS": "-mod=mod",
        "GOTOOLCHAIN": "local",
        "GOSUMDB": "sum.golang.org",
        "GONOSUMDB": "",
        "GOPRIVATE": "",
        "GOPROXY": "https://proxy.golang.org",
        "CGO_ENABLED": "0",
    }
    go = find_tool("go", env)
    for package in ctx.common["packages"]:
        process = subprocess.run(
            [go, "mod", "download", "-json", package],
            cwd=work,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=INSTALL_TIMEOUT_SECONDS,
            check=False,
        )
        if process.returncode != 0:
            raise NativeError(process.stdout.decode("utf-8", errors="replace"))
        if json.loads(process.stdout)["Sum"] != ctx.common["sums"][package]:
            raise NativeError(f"{package}: module checksum differs from the lock")
        run_command([go, "install", package], env, cwd=work)
    return InstallResult([binaries], {})


def install_runtime_provided(ctx):
    missing = [
        name
        for name in ctx.tool_names
        if shutil.which(name, path=ctx.env.get("PATH")) is None
    ]
    if missing:
        suggest = (ctx.native.get("suggest") or {}).get(current_os_family())
        message = f"{', '.join(missing)} not found in PATH."
        if suggest:
            message += f" Install it with: {suggest}"
        raise NativeError(message)
    return InstallResult()


INSTALLERS = {
    "pip": install_pip,
    "npm": install_npm,
    "binary": install_binary,
    "gem": install_gem,
    "go": install_go,
    "dotnet_tool": install_dotnet_tool,
    "powershell_module": install_powershell_module,
    "runtime_provided": install_runtime_provided,
}
