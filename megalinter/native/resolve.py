import os
import re

from megalinter.native.context import linters_dir
from megalinter.native.lock import compute_spec_hash

NATIVE_PLATFORMS = [
    "linux/amd64",
    "linux/arm64",
    "darwin/amd64",
    "darwin/arm64",
    "windows/amd64",
]
PACKAGE_METHODS = ["pip", "npm", "gem"]
METHODS_WITHOUT_VERSION = ["pip", "npm", "gem", "runtime_provided"]
ARG_REGEX = re.compile(r"^\s*ARG\s+([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$", re.MULTILINE)
FROM_REGEX = re.compile(
    r"^\s*FROM\s+(?:--\S+\s+)*(\S+?)(?::(\S+))?(?:\s+AS\s+\S+)?\s*$"
)
VERSION_REF_REGEX = re.compile(r"\$\{(FROM_TAG:[^}]+|[A-Za-z0-9_]+)\}")


class NativeLinterSpec:
    def __init__(self, descriptor_id, descriptor_install, linter, source_file):
        self.descriptor_id = descriptor_id
        self.descriptor_install = descriptor_install or {}
        self.linter = linter
        self.source_file = source_file
        self.linter_name = linter["linter_name"]
        self.key = linter.get("name") or (
            descriptor_id + "_" + self.linter_name.upper().replace("-", "_")
        )
        self.native_install = linter.get("native_install")

    def docker_install_blocks(self):
        return [self.descriptor_install, self.linter.get("install") or {}]

    def dockerfile_lines(self):
        lines = []
        for block in self.docker_install_blocks():
            for snippet in block.get("dockerfile", []) or []:
                lines.extend(snippet.splitlines())
        return lines


def resolve_version_reference(value, spec):
    if value is None or "${" not in str(value):
        return value
    lines = spec.dockerfile_lines()
    args = dict(ARG_REGEX.findall("\n".join(lines)))

    def replace(match):
        ref = match.group(1)
        if ref.startswith("FROM_TAG:"):
            image = ref[len("FROM_TAG:") :]
            for line in lines:
                from_match = FROM_REGEX.match(line)
                if (
                    from_match
                    and from_match.group(2)
                    and from_match.group(1) == image
                    and from_match.group(2) != "latest"
                ):
                    return from_match.group(2)
            raise KeyError(f"FROM {image}:<tag> not found in install.dockerfile")
        if ref not in args:
            raise KeyError(f"ARG {ref} not found in install.dockerfile")
        return args[ref].strip("\"'")

    return VERSION_REF_REGEX.sub(replace, str(value))


def resolve_native_install(spec):
    native = dict(spec.native_install or {})
    method = native.get("method")
    if "version" in native:
        native["version"] = resolve_version_reference(native["version"], spec)
    if method in PACKAGE_METHODS and "packages" not in native:
        packages = []
        for block in spec.docker_install_blocks():
            packages.extend(block.get(method, []) or [])
        native["packages"] = packages
    if "packages" in native:
        native["packages"] = [
            resolve_version_reference(package, spec) for package in native["packages"]
        ]
    return native


def platform_native_install(native, platform):
    if platform == "windows/arm64":
        platform = "windows/amd64"
    merged = {k: v for k, v in native.items() if k != "overrides"}
    merged.update((native.get("overrides") or {}).get(platform, {}))
    return merged


def native_linter_properties(spec, effective_native):
    return {**spec.linter, **(effective_native.get("linter_overrides") or {})}


def unsupported_reason(native, platform):
    return (native.get("unsupported") or {}).get(platform)


def spec_from_linter(linter):
    data = {
        "linter_name": linter.linter_name,
        "name": linter.name,
        "install": getattr(linter, "install", None) or {},
        "native_install": getattr(linter, "native_install", None),
    }
    return NativeLinterSpec(
        linter.descriptor_id, getattr(linter, "descriptor_install", None), data, None
    )


def linter_install_dir(home, key, resolved_native_install):
    return os.path.join(
        linters_dir(home), key, compute_spec_hash(resolved_native_install)[:12]
    )


def replace_install_dir(value, install_dir):
    if isinstance(value, str):
        return value.replace("{{NATIVE_INSTALL_DIR}}", install_dir)
    if isinstance(value, list):
        return [replace_install_dir(item, install_dir) for item in value]
    if isinstance(value, dict):
        return {
            key: replace_install_dir(item, install_dir) for key, item in value.items()
        }
    return value


def apply_native_overrides(
    linter_descriptor, platform, descriptor_id, descriptor_install, home
):
    native = linter_descriptor.get("native_install")
    if not native:
        return linter_descriptor
    overrides = platform_native_install(native, platform).get("linter_overrides")
    if not overrides:
        return linter_descriptor
    spec = NativeLinterSpec(descriptor_id, descriptor_install, linter_descriptor, None)
    install_dir = linter_install_dir(home, spec.key, resolve_native_install(spec))
    return {**linter_descriptor, **replace_install_dir(overrides, install_dir)}
