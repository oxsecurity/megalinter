import posixpath
from dataclasses import dataclass

from megalinter.native.methods import executable_basename
from megalinter.native.resolve import (
    NATIVE_PLATFORMS,
    platform_native_install,
    render_asset_template,
    resolve_native_install,
)
from megalinter.native.runtimes import load_runtime_catalog

INSTALL_DIR_VARIABLE = "$INSTALL_DIR"
INSTALL_DIR_ASSIGNMENT = 'INSTALL_DIR="$HOME/.megalinter/linters/{key}"'
TAR_FLAGS = {"tar.gz": "z", "tar.xz": "J", "tar.bz2": "j"}


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


def inline_code(value):
    fence = "``" if "`" in value else "`"
    return f"{fence}{value}{fence}"


def chain(commands):
    return [
        ("  " if index else "") + command + (" &&" if index < len(commands) - 1 else "")
        for index, command in enumerate(commands)
    ]


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
        f'pwsh -NoProfile -Command "Save-Module -Name {package} '
        f"-RequiredVersion {effective['version']} -Path '{modules_path}'\""
        for package in effective["packages"]
    ] + [
        f'export PSModulePath="{modules_path}{separator}$PSModulePath"',
    ]


def binary_commands(effective, platform):
    assets = effective["assets"]
    asset = assets.get(platform) or assets["any"]
    url = render_asset_template(asset["url"], effective["version"])
    archive = asset.get("archive", "none")
    url_file_name = posixpath.basename(url.split("?")[0])
    file_name = (asset.get("name") if archive == "none" else None) or url_file_name
    file_path = f"{INSTALL_DIR_VARIABLE}/{file_name}"
    steps = [f"curl -fsSL -o {quote(file_path)} {url}"]
    strip_components = asset.get("strip_components", 0)
    executable = None
    if archive in TAR_FLAGS:
        steps.append(
            f"tar -x{TAR_FLAGS[archive]}f {quote(file_path)} -C {quote(INSTALL_DIR_VARIABLE)}"
            + (f" --strip-components={strip_components}" if strip_components else "")
        )
    elif archive == "gz":
        executable = f"{INSTALL_DIR_VARIABLE}/" + (
            asset.get("name") or url_file_name.removesuffix(".gz")
        )
        steps.append(f"gunzip -c {quote(file_path)} > {quote(executable)}")
    elif archive == "zip":
        if strip_components:
            extract_folder = f"{INSTALL_DIR_VARIABLE}/extract"
            steps += [
                f"unzip -q {quote(file_path)} -d {quote(extract_folder)}",
                f'mv "{extract_folder}"/{"*/" * strip_components}* {quote(INSTALL_DIR_VARIABLE)}/',
                f"rm -r {quote(extract_folder)}",
            ]
        else:
            steps.append(
                f"unzip -q {quote(file_path)} -d {quote(INSTALL_DIR_VARIABLE)}"
            )
    else:
        executable = file_path
    if archive != "none":
        steps.append(f"rm {quote(file_path)}")
    if executable is not None and not is_windows(platform):
        steps.append(f"chmod +x {quote(executable)}")
    path_export, launchers = binary_path_commands(effective)
    return [
        f"mkdir -p {quote(INSTALL_DIR_VARIABLE)}",
        *chain([*steps, path_export]),
        *launchers,
    ]


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
    return export_path(directories), launchers


def env_commands(effective):
    return [
        f'export {name}="{value.replace("{{NATIVE_INSTALL_DIR}}", INSTALL_DIR_VARIABLE)}"'
        for name, value in (effective.get("env") or {}).items()
    ]


def runtime_provided_lines(spec, effective, platform):
    family = os_family(platform)
    suggestion = (effective.get("suggest") or {}).get(family)
    if suggestion is not None:
        return [inline_code(suggestion)]
    requirements = effective.get("requires", [])
    if not requirements:
        return [f"Install `{spec.linter_name}` and add it to `PATH`."]
    catalog = load_runtime_catalog()
    lines = []
    for requirement in requirements:
        runtime = requirement["runtime"]
        constraint = f" {requirement['version']}" if requirement.get("version") else ""
        runtime_suggestion = ((catalog.get(runtime) or {}).get("suggest") or {}).get(
            family
        )
        if lines:
            lines.append("")
        if runtime_suggestion is None:
            lines.append(
                f"Provided by the `{runtime}`{constraint} runtime: install it and add it to `PATH`."
            )
        else:
            lines += [
                f"Provided by the `{runtime}`{constraint} runtime, install it with:",
                "",
                inline_code(runtime_suggestion),
            ]
    return lines


def platform_lines(spec, resolved, platform):
    effective = platform_native_install(resolved, platform)
    method = effective["method"]
    if method == "runtime_provided":
        return runtime_provided_lines(spec, effective, platform)
    if method == "binary":
        commands = binary_commands(effective, platform)
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
            INSTALL_DIR_ASSIGNMENT.format(key=spec.key),
            *commands,
            *env_commands(effective),
        ]
    )


def manual_install_groups(spec):
    resolved = resolve_native_install(spec)
    groups = []
    for platform in NATIVE_PLATFORMS:
        if platform not in resolved.get("platforms", []):
            continue
        lines = platform_lines(spec, resolved, platform)
        for group in groups:
            if group.lines == lines:
                group.platforms.append(platform)
                break
        else:
            groups.append(ManualInstallGroup([platform], lines))
    return groups
