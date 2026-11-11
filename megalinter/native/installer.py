import logging
import os
import shutil

from megalinter import config
from megalinter.native.context import (
    NativeError,
    current_libc,
    current_os_family,
    current_platform,
    megalinter_home,
)
from megalinter.native.lock import (
    check_lock_fresh,
    compute_spec_hash,
    load_lock,
)
from megalinter.native.methods import INSTALLERS, InstallContext
from megalinter.native.resolve import (
    linter_install_dir,
    native_linter_properties,
    platform_native_install,
    resolve_native_install,
    unsupported_reason,
)
from megalinter.native.runtimes import POLICIES, resolve_requirements
from megalinter.native.state import read_state, update_state
from megalinter.native.toolchain import (
    Toolchain,
    build_subprocess_env,
    installed_toolchain,
)

DEFAULT_POLICY = "ask"


def runtime_policy(request_id):
    policy = config.get(request_id, "NATIVE_INSTALL_RUNTIMES", DEFAULT_POLICY)
    if policy not in POLICIES:
        raise NativeError(
            f"NATIVE_INSTALL_RUNTIMES must be one of {', '.join(POLICIES)} (got {policy})"
        )
    return policy


def is_offline(request_id):
    return config.get(request_id, "NATIVE_OFFLINE", "false") == "true"


def check_platform_support(spec, resolved, platform):
    reason = unsupported_reason(resolved, platform)
    if reason is None and platform not in resolved.get("platforms", []):
        reason = "no native install is declared for this platform. Use Docker."
    if reason is None and resolved.get("libc") == "glibc" and current_libc() == "musl":
        reason = "this tool needs glibc, and this system uses musl. Use Docker."
    if reason is not None:
        raise NativeError(
            f"{spec.key} is not supported natively on {platform}: {reason}"
        )


def tool_names(spec, effective):
    executables = effective.get("executables")
    if executables:
        return list(executables.keys())
    properties = native_linter_properties(spec, effective)
    executable = properties.get("cli_executable") or properties["linter_name"]
    if isinstance(executable, list):
        executable = executable[0]
    return [] if ("/" in executable or "\\" in executable) else [executable]


class NativeInstaller:
    def __init__(self, request_id=None):
        self.request_id = request_id
        self.home = megalinter_home(request_id)
        self.policy = runtime_policy(request_id)
        self.offline = is_offline(request_id)
        self.platform = current_platform()

    def prepare(self, spec):
        resolved = resolve_native_install(spec)
        check_platform_support(spec, resolved, self.platform)
        effective = platform_native_install(resolved, self.platform)
        return resolved, effective

    def is_host_provided(self, resolved):
        return resolved["method"] == "runtime_provided" and not resolved.get("requires")

    def status(self, spec):
        try:
            resolved, effective = self.prepare(spec)
        except NativeError as e:
            return "unsupported", str(e)
        if installed_toolchain(self.home, spec.key, resolved) is not None:
            return "installed", None
        if self.is_host_provided(effective):
            return "host-provided", None
        return "not installed", None

    def toolchain(self, spec):
        resolved, _ = self.prepare(spec)
        toolchain = installed_toolchain(self.home, spec.key, resolved)
        if toolchain is None and self.is_host_provided(resolved):
            return Toolchain()
        if toolchain is None:
            raise NativeError(
                f"{spec.key} is not installed: run `megalinter install-linters {spec.key}`"
            )
        return toolchain

    def install(self, spec, force=False):
        resolved, effective = self.prepare(spec)
        lock = load_lock(spec.key)
        check_lock_fresh(spec.key, resolved, lock)
        if not force and installed_toolchain(self.home, spec.key, resolved) is not None:
            logging.info(f"[native] {spec.key} is already installed")
            return
        requirements = [
            requirement
            for requirement in effective.get("requires", [])
            if not (requirement["runtime"] == "python" and shutil.which("uv"))
        ]
        runtimes = resolve_requirements(
            requirements, self.home, self.policy, self.offline
        )
        path_dirs = []
        runtime_env = {}
        for runtime in runtimes:
            if runtime.executable:
                path_dirs.append(os.path.dirname(runtime.executable))
            path_dirs.extend(runtime.path_dirs)
            runtime_env.update(runtime.env)
        install_env = build_subprocess_env(
            dict(os.environ), Toolchain(path_dirs, runtime_env), self.request_id
        )
        destination = linter_install_dir(self.home, spec.key, resolved)
        if os.path.isdir(destination):
            shutil.rmtree(destination)
        os.makedirs(destination)
        platform_entry = (lock.get("platforms") or {}).get(self.platform, {})
        if effective["method"] == "binary" and not platform_entry:
            raise NativeError(
                f"The native lock of {spec.key} has no {self.platform} entry"
            )
        names = tool_names(spec, effective)
        context = InstallContext(
            spec.key,
            effective,
            lock,
            platform_entry,
            destination,
            self.home,
            install_env,
            names,
            self.offline,
        )
        logging.info(f"[native] Installing {spec.key} ({effective['method']})")
        try:
            result = INSTALLERS[effective["method"]](context)
            for name, value in (effective.get("env") or {}).items():
                result.env[name] = value.replace("{{NATIVE_INSTALL_DIR}}", destination)
            search_path = os.pathsep.join([*result.path_dirs, install_env["PATH"]])
            missing = [
                name for name in names if shutil.which(name, path=search_path) is None
            ]
            if missing:
                raise NativeError(
                    f"{spec.key}: executable(s) not found after install: {', '.join(missing)}"
                )
        except Exception:
            shutil.rmtree(destination, ignore_errors=True)
            raise
        update_state(
            self.home,
            "linters",
            spec.key,
            {
                "dir": destination,
                "spec_hash": compute_spec_hash(resolved),
                "platform": self.platform,
                "path_dirs": result.path_dirs,
                "env": result.env,
                "os": current_os_family(),
            },
        )

    def uninstall(self, spec):
        entry = read_state(self.home)["linters"].get(spec.key)
        if entry is None:
            return False
        shutil.rmtree(os.path.dirname(entry["dir"]), ignore_errors=True)
        update_state(self.home, "linters", spec.key, None)
        return True
