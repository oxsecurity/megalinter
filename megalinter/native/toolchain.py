import os

from megalinter import config
from megalinter.native.context import NativeError, current_platform
from megalinter.native.lock import compute_spec_hash
from megalinter.native.runtimes import resolve_requirements
from megalinter.native.state import read_state

ALLOWED_ENV_NAMES = {
    "HOME",
    "USERPROFILE",
    "USER",
    "USERNAME",
    "LOGNAME",
    "TEMP",
    "TMP",
    "TMPDIR",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "APPDATA",
    "LOCALAPPDATA",
    "PROGRAMDATA",
    "PROGRAMFILES",
    "PROGRAMFILES(X86)",
    "PROGRAMW6432",
    "COMMONPROGRAMFILES",
    "OS",
    "PROCESSOR_ARCHITECTURE",
    "NUMBER_OF_PROCESSORS",
    "LANG",
    "LANGUAGE",
    "TERM",
    "TZ",
    "SHELL",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "ALL_PROXY",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
    "NODE_EXTRA_CA_CERTS",
    "GIT_SSL_CAINFO",
    "FORCE_COLOR",
    "NO_COLOR",
    "CI",
    # Toolchain locations (not secrets): linters launched by a runtime need them
    "JAVA_HOME",
    "DOTNET_ROOT",
    "DOTNET_ROOT_X64",
    "DOTNET_CLI_HOME",
    "NUGET_PACKAGES",
    "GOROOT",
    "GOPATH",
    "GOMODCACHE",
    "CARGO_HOME",
    "RUSTUP_HOME",
    "RUSTUP_TOOLCHAIN",
    "GEM_HOME",
    "GEM_PATH",
    "R_HOME",
    "R_LIBS_USER",
    "PERL5LIB",
    "PERL_LOCAL_LIB_ROOT",
    "COMPOSER_HOME",
    "PSMODULEPATH",
}
ALLOWED_ENV_PREFIXES = ("LC_", "XDG_", "MEGALINTER_", "MEGALINTER")
PATH_NAME = "PATH"


class Toolchain:
    def __init__(self, path_dirs=None, env=None, install_dir=None, version=None):
        self.path_dirs = path_dirs or []
        self.env = env or {}
        self.install_dir = install_dir
        self.version = version


def is_allowed_env_name(name, extra_allowed):
    upper = name.upper()
    return (
        upper in ALLOWED_ENV_NAMES
        or upper.startswith(ALLOWED_ENV_PREFIXES)
        or upper in extra_allowed
    )


def filter_environment(env, request_id, unsecured_variables=None):
    extra_allowed = {
        item.upper()
        for item in config.get_list(request_id, "NATIVE_ENV_ALLOWLIST", [])
        + list(unsecured_variables or [])
    }
    return {
        name: value
        for name, value in env.items()
        if is_allowed_env_name(name, extra_allowed) or name.upper() == PATH_NAME
    }


def installed_toolchain(home, key, resolved_native_install, policy="never"):
    entry = read_state(home)["linters"].get(key)
    if (
        not entry
        or entry.get("spec_hash") != compute_spec_hash(resolved_native_install)
        or entry.get("platform") != current_platform()
        or not os.path.isdir(entry["dir"])
    ):
        return None
    path_dirs = list(entry.get("path_dirs", []))
    env = dict(entry.get("env", {}))
    try:
        # An installed Python linter runs from its own virtual environment
        runtimes = resolve_requirements(
            [
                requirement
                for requirement in resolved_native_install.get("requires", [])
                if requirement["runtime"] != "python"
            ],
            home,
            policy,
        )
    except NativeError:
        return None
    for runtime in runtimes:
        if runtime.executable:
            path_dirs.append(os.path.dirname(runtime.executable))
        path_dirs.extend(runtime.path_dirs)
        env.update(runtime.env)
    return Toolchain(path_dirs, env, entry["dir"], entry.get("version"))


def build_subprocess_env(base_env, toolchain, request_id, unsecured_variables=None):
    env = filter_environment(base_env, request_id, unsecured_variables)
    host_path = next(
        (value for name, value in base_env.items() if name.upper() == PATH_NAME), ""
    )
    env = {name: value for name, value in env.items() if name.upper() != PATH_NAME}
    env[PATH_NAME] = os.pathsep.join(
        [*toolchain.path_dirs, *([host_path] if host_path else [])]
    )
    env.update(toolchain.env)
    return env
