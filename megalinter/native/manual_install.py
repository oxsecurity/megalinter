import posixpath
import re
from dataclasses import dataclass

from megalinter.native.lock import load_fresh_lock
from megalinter.native.methods import executable_basename
from megalinter.native.resolve import (
    NATIVE_PLATFORMS,
    platform_native_install,
    render_asset_template,
    resolve_native_install,
)

INSTALL_DIR_VARIABLE = "$INSTALL_DIR"
INSTALL_DIR_ASSIGNMENT = 'INSTALL_DIR="$HOME/.local/opt/{folder}"'
TAR_FLAGS = {"tar.gz": "z", "tar.xz": "J", "tar.bz2": "j"}
PROSE_REGEX = re.compile(r"^[A-Z]| \(")


@dataclass
class ManualInstallGroup:
    platforms: list
    lines: list


def os_family(platform):
    return platform.split("/")[0]


def is_windows(platform):
    return os_family(platform) == "windows"


def bin_dir(platform):
    return "Scripts" if is_windows(platform) else "bin"


def shell_block(lines):
    return ["```shell", *lines, "```"]


def export_path(directories):
    return 'export PATH="' + ":".join([*directories, "$PATH"]) + '"'


def quote(value):
    return '"' + value + '"'


def pip_commands(effective, platform):
    python_requirement = next(
        (r for r in effective.get("requires", []) if r["runtime"] == "python"), None
    )
    constraint = python_requirement.get("version") if python_requirement else None
    venv_python = f"{INSTALL_DIR_VARIABLE}/{bin_dir(platform)}/python" + (
        ".exe" if is_windows(platform) else ""
    )
    binary_only = [] if effective.get("allow_source_build") else ["--only-binary :all:"]
    install = " ".join(
        [
            "uv pip install",
            f'--python "{venv_python}"',
            *binary_only,
            *[quote(package) for package in effective["packages"]],
        ]
    )
    return [
        "uv venv "
        + quote(INSTALL_DIR_VARIABLE)
        + (f' --python "{constraint}"' if constraint else ""),
        install,
        export_path([f"{INSTALL_DIR_VARIABLE}/{bin_dir(platform)}"]),
    ]


def npm_commands(effective, platform):
    commands = [
        "npm install --prefix "
        + quote(INSTALL_DIR_VARIABLE)
        + " --ignore-scripts --no-audit --no-fund "
        + " ".join(quote(package) for package in effective["packages"])
    ]
    for allowed in effective.get("allow_install_scripts", []):
        commands.append(
            f'npm rebuild {quote(allowed["package"])} --prefix {quote(INSTALL_DIR_VARIABLE)}'
        )
    return [
        *commands,
        export_path([f"{INSTALL_DIR_VARIABLE}/node_modules/.bin"]),
        f'export NODE_PATH="{INSTALL_DIR_VARIABLE}/node_modules"',
    ]


def gem_commands(effective, platform):
    return [
        "gem install --no-document --install-dir "
        + quote(INSTALL_DIR_VARIABLE)
        + " "
        + " ".join(quote(package) for package in effective["packages"]),
        f'export GEM_HOME="{INSTALL_DIR_VARIABLE}"',
        export_path([f"{INSTALL_DIR_VARIABLE}/bin"]),
    ]


def go_commands(effective, platform):
    return [
        f'GOBIN="{INSTALL_DIR_VARIABLE}/bin" go install {package}'
        for package in effective["packages"]
    ] + [export_path([f"{INSTALL_DIR_VARIABLE}/bin"])]


def dotnet_tool_commands(effective, platform):
    return [
        f'dotnet tool install {package} --version {effective["version"]} --tool-path "{INSTALL_DIR_VARIABLE}"'
        for package in effective["packages"]
    ] + [export_path([INSTALL_DIR_VARIABLE])]


def powershell_module_commands(effective, platform):
    modules_path = (
        f'$(cygpath -w "{INSTALL_DIR_VARIABLE}")'
        if is_windows(platform)
        else INSTALL_DIR_VARIABLE
    )
    separator = ";" if is_windows(platform) else ":"
    return [
        f"pwsh -NoProfile -Command \"Save-Module -Name {package} -RequiredVersion {effective['version']} -Path '{modules_path}'\""
        for package in effective["packages"]
    ] + [
        f'export PSModulePath="{INSTALL_DIR_VARIABLE}{separator}$PSModulePath"',
    ]


def asset_checksums(spec, resolved):
    lock = load_fresh_lock(spec.key, resolved)
    checksums = {}
    for platform_entry in ((lock or {}).get("platforms") or {}).values():
        for asset in platform_entry.get("assets", []):
            checksums[asset["url"]] = asset["sha256"]
    return checksums


def binary_commands(effective, platform, checksums):
    assets = effective["assets"]
    asset = assets.get(platform) or assets["any"]
    url = render_asset_template(asset["url"], effective["version"])
    archive = asset.get("archive", "none")
    file_name = (
        asset.get("name") if archive == "none" else None
    ) or posixpath.basename(url.split("?")[0])
    file_path = f"{INSTALL_DIR_VARIABLE}/{file_name}"
    commands = [
        f"mkdir -p {quote(INSTALL_DIR_VARIABLE)}",
        f"curl -fsSL -o {quote(file_path)} {url}",
    ]
    if url in checksums:
        checker = (
            "shasum -a 256 -c -"
            if os_family(platform) == "darwin"
            else "sha256sum -c -"
        )
        commands.append(f'echo "{checksums[url]}  {file_path}" | {checker}')
    strip_components = asset.get("strip_components", 0)
    if archive in TAR_FLAGS or archive == "gz":
        if archive == "gz":
            commands.append(f"gunzip -f {quote(file_path)}")
        else:
            commands.append(
                f"tar -x{TAR_FLAGS[archive]}f {quote(file_path)} -C {quote(INSTALL_DIR_VARIABLE)}"
                + (
                    f" --strip-components={strip_components}"
                    if strip_components
                    else ""
                )
            )
            commands.append(f"rm {quote(file_path)}")
    elif archive == "zip":
        if strip_components:
            extract_folder = f"{INSTALL_DIR_VARIABLE}/extract"
            commands += [
                f"unzip -q {quote(file_path)} -d {quote(extract_folder)}",
                f'mv "{extract_folder}"/{"*/" * strip_components}* {quote(INSTALL_DIR_VARIABLE)}/',
                f"rm -r {quote(extract_folder)}",
            ]
        else:
            commands.append(
                f"unzip -q {quote(file_path)} -d {quote(INSTALL_DIR_VARIABLE)}"
            )
        commands.append(f"rm {quote(file_path)}")
    elif not is_windows(platform):
        commands.append(f"chmod +x {quote(file_path)}")
    return [*commands, *binary_path_commands(effective)]


def binary_path_commands(effective):
    directories = []
    launchers = []
    for name, target in (effective.get("executables") or {}).items():
        if isinstance(target, str):
            if executable_basename(target) == name:
                relative_dir = posixpath.dirname(target)
                directory = (
                    f"{INSTALL_DIR_VARIABLE}/{relative_dir}"
                    if relative_dir
                    else INSTALL_DIR_VARIABLE
                )
                if directory not in directories:
                    directories.append(directory)
            else:
                launchers.append(f'# {name}: run "{INSTALL_DIR_VARIABLE}/{target}"')
        else:
            arguments = " ".join(
                quote(part.replace("{{NATIVE_INSTALL_DIR}}", INSTALL_DIR_VARIABLE))
                for part in target.get("args", [])
            )
            launchers.append(f"# {name}: run {target['launcher']} {arguments}")
    for relative in effective.get("path", []):
        directories.append(
            posixpath.normpath(posixpath.join(INSTALL_DIR_VARIABLE, relative))
        )
    if not directories:
        directories = [INSTALL_DIR_VARIABLE]
    return [export_path(directories), *launchers]


def env_commands(effective):
    return [
        f'export {name}="{value.replace("{{NATIVE_INSTALL_DIR}}", INSTALL_DIR_VARIABLE)}"'
        for name, value in (effective.get("env") or {}).items()
    ]


def runtime_provided_lines(spec, effective, platform):
    family = os_family(platform)
    suggestion = (effective.get("suggest") or {}).get(family)
    if suggestion is None:
        requirements = [
            f"`{requirement['runtime']}`"
            + (f" {requirement['version']}" if requirement.get("version") else "")
            for requirement in effective.get("requires", [])
        ]
        provider = (
            "the " + " and ".join(requirements) + " runtime"
            if requirements
            else f"`{spec.linter_name}`"
        )
        return [f"Provided by {provider}: install it and add it to `PATH`."]
    if PROSE_REGEX.search(suggestion):
        return [suggestion]
    return shell_block([suggestion])


def platform_lines(spec, resolved, platform, checksums):
    effective = platform_native_install(resolved, platform)
    method = effective["method"]
    if method == "runtime_provided":
        return runtime_provided_lines(spec, effective, platform)
    if method == "binary":
        commands = binary_commands(effective, platform, checksums)
    else:
        commands = {
            "pip": pip_commands,
            "npm": npm_commands,
            "gem": gem_commands,
            "go": go_commands,
            "dotnet_tool": dotnet_tool_commands,
            "powershell_module": powershell_module_commands,
        }[method](effective, platform)
    return shell_block(
        [
            INSTALL_DIR_ASSIGNMENT.format(folder=spec.key.lower()),
            *commands,
            *env_commands(effective),
        ]
    )


def manual_install_groups(spec):
    resolved = resolve_native_install(spec)
    checksums = (
        asset_checksums(spec, resolved) if resolved["method"] == "binary" else {}
    )
    groups = []
    for platform in NATIVE_PLATFORMS:
        if platform not in resolved.get("platforms", []):
            continue
        lines = platform_lines(spec, resolved, platform, checksums)
        for group in groups:
            if group.lines == lines:
                group.platforms.append(platform)
                break
        else:
            groups.append(ManualInstallGroup([platform], lines))
    return groups
