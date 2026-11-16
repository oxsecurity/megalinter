import glob
import os
import platform
import shutil
import stat
import sys

from megalinter import config

DEFAULT_HOME = "~/.megalinter"
GIT_BASH_INSTALL_COMMAND = "winget install --id Git.Git -e"
SYSTEM_PLATFORMS = {"linux": "linux", "darwin": "darwin", "win32": "windows"}
MACHINE_ARCHITECTURES = {
    "x86_64": "amd64",
    "amd64": "amd64",
    "arm64": "arm64",
    "aarch64": "arm64",
}


class NativeError(Exception):
    pass


def is_native_mode(request_id=None):
    return config.get(request_id, "MEGALINTER_NATIVE", "false") == "true"


def current_platform():
    system = SYSTEM_PLATFORMS.get(sys.platform)
    architecture = MACHINE_ARCHITECTURES.get(platform.machine().lower())
    if system is None or architecture is None:
        raise NativeError(
            f"Unsupported platform for native mode: {sys.platform}/{platform.machine()}"
        )
    # Windows on ARM runs the amd64 binaries through emulation
    if system == "windows":
        architecture = "amd64"
    return f"{system}/{architecture}"


def current_os_family():
    return current_platform().split("/")[0]


def current_libc():
    if sys.platform != "linux":
        return "any"
    if glob.glob("/lib/ld-musl-*") or glob.glob("/usr/lib/ld-musl-*"):
        return "musl"
    return "glibc"


def is_posix():
    return os.name == "posix"


def megalinter_home(request_id=None):
    configured = config.get(request_id, "MEGALINTER_HOME", "")
    home = os.path.abspath(os.path.expanduser(configured or DEFAULT_HOME))
    os.makedirs(home, mode=0o700, exist_ok=True)
    check_home_permissions(home)
    return home


def check_home_permissions(home):
    if not is_posix():
        return
    info = os.stat(home)
    if info.st_uid != os.getuid():
        raise NativeError(
            f"{home} is owned by another user: refusing to run or install linters from it"
        )
    if info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        raise NativeError(
            f"{home} is writable by other users: refusing to run or install linters from it "
            f"(fix with: chmod go-w {home})"
        )


def is_root():
    return is_posix() and os.geteuid() == 0


def linters_dir(home):
    return os.path.join(home, "linters")


def runtimes_dir(home):
    return os.path.join(home, "runtimes")


def cache_dir(home):
    return os.path.join(home, "cache")


def core_dir(home):
    return os.path.join(home, "core")


def is_wsl_launcher(path):
    normalized = os.path.normcase(os.path.abspath(path))
    system_root = os.path.normcase(os.environ.get("SystemRoot", r"C:\Windows"))
    return normalized.startswith(system_root + os.sep)


def find_git_bash():
    if sys.platform != "win32":
        return shutil.which("bash") or "/bin/bash"
    git = shutil.which("git")
    candidates = []
    if git:
        git_root = os.path.dirname(os.path.dirname(os.path.abspath(git)))
        candidates += [
            os.path.join(git_root, "bin", "bash.exe"),
            os.path.join(git_root, "usr", "bin", "bash.exe"),
        ]
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        base = os.environ.get(variable)
        if base:
            candidates.append(os.path.join(base, "Git", "bin", "bash.exe"))
    for candidate in candidates:
        if os.path.isfile(candidate) and not is_wsl_launcher(candidate):
            return candidate
    return None


def require_git_bash():
    bash = find_git_bash()
    if bash is None:
        raise NativeError(
            "Git for Windows (Git Bash) is required to run MegaLinter natively on Windows.\n"
            f"Install it with: {GIT_BASH_INSTALL_COMMAND}"
        )
    return bash
