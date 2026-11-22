import configparser
import glob
import os
import re
import subprocess

from megalinter.native.context import find_git_bash

# Windows caps a command line at 32767 characters, and at 8191 when it goes through
# cmd.exe (.cmd and .bat launchers, like the ones npm creates). The margin covers
# what a launcher adds when it expands its own path and the path of the tool
WINDOWS_COMMAND_LINE_MAX_CHARS = 32000
WINDOWS_SCRIPT_COMMAND_LINE_MAX_CHARS = 7000

ROUTE_DIRECT = "direct"
ROUTE_NODE = "node"
ROUTE_PYTHON = "python"
ROUTE_GIT_BASH = "git_bash"
ROUTE_TOO_LONG = "too_long"

NODE_LAUNCHER_REGEX = re.compile(rb'exec\s+(?:"\$basedir/node"|node)\s')
# A tool started through a file can still start another program with all its
# arguments (ex: a npm package wrapping a native binary). These errors do not
# depend on the language of Windows
LAUNCH_FAILURE_REGEX = re.compile(
    r"ENAMETOOLONG|WinError 206|error=206|Argument list too long"
)

# Loaded by node before the tool: adds the arguments to process.argv, then removes
# itself from the environment so that the child processes of the tool are not affected
NODE_PRELOAD = r"""const { isMainThread } = require("worker_threads");
const argumentsFile = process.env.MEGALINTER_ARGUMENTS_FILE;
if (isMainThread && argumentsFile) {
  const nodeOptions = process.env.MEGALINTER_NODE_OPTIONS;
  delete process.env.MEGALINTER_ARGUMENTS_FILE;
  delete process.env.MEGALINTER_NODE_OPTIONS;
  if (nodeOptions) {
    process.env.NODE_OPTIONS = nodeOptions;
  } else {
    delete process.env.NODE_OPTIONS;
  }
  const content = require("fs").readFileSync(argumentsFile, "utf8");
  for (const argument of content.split("\0").slice(0, -1)) {
    process.argv.push(argument);
  }
}
"""

# Starts the console script of a Python tool with the arguments of the file
PYTHON_BOOTSTRAP = r"""import importlib.metadata, sys
name, program, arguments_file = sys.argv[1:4]
with open(arguments_file, encoding="utf-8", newline="") as file:
    arguments = file.read().split("\0")[:-1]
sys.argv = [program, *arguments]
entry_points = importlib.metadata.entry_points(group="console_scripts")
entry_point = next(entry for entry in entry_points if entry.name == name)
sys.exit(entry_point.load()())
"""

GIT_BASH_SCRIPT = 'mapfile -d "" -t arguments < "$1" && exec "$2" "${arguments[@]}"'


def is_windows_script(executable):
    return executable.lower().endswith((".cmd", ".bat"))


def read_posix_launcher(executable):
    launcher = os.path.splitext(executable)[0]
    try:
        with open(launcher, "rb") as launcher_file:
            content = launcher_file.read(4096)
    except OSError:
        return None, None
    return (launcher, content) if content.startswith(b"#!") else (None, None)


def is_node_launcher(executable):
    if not is_windows_script(executable):
        return False
    _launcher, content = read_posix_launcher(executable)
    return content is not None and NODE_LAUNCHER_REGEX.search(content) is not None


def find_python_entry_point(executable):
    if not executable.lower().endswith(".exe"):
        return None
    scripts_folder = os.path.dirname(executable)
    venv = os.path.dirname(scripts_folder)
    if os.path.basename(scripts_folder).lower() != "scripts" or not os.path.isfile(
        os.path.join(venv, "pyvenv.cfg")
    ):
        return None
    name = os.path.basename(executable)[: -len(".exe")]
    pattern = os.path.join(
        glob.escape(venv), "Lib", "site-packages", "*.dist-info", "entry_points.txt"
    )
    for entry_points_file in glob.glob(pattern):
        parser = configparser.ConfigParser(interpolation=None, delimiters=("=",))
        parser.optionxform = str
        try:
            parser.read(entry_points_file, encoding="utf-8")
        except (configparser.Error, OSError, UnicodeDecodeError):
            continue
        if parser.has_option("console_scripts", name):
            return name
    return None


def is_launch_failure(output):
    return LAUNCH_FAILURE_REGEX.search(output or "") is not None


# How to start this command on Windows, from the way the tool is launched
def find_route(command):
    executable = command[0]
    command_chars = len(subprocess.list2cmdline(command))
    is_script = is_windows_script(executable)
    max_chars = (
        WINDOWS_SCRIPT_COMMAND_LINE_MAX_CHARS
        if is_script
        else WINDOWS_COMMAND_LINE_MAX_CHARS
    )
    if command_chars <= max_chars:
        return ROUTE_DIRECT
    if is_node_launcher(executable):
        return ROUTE_NODE
    if find_python_entry_point(executable) is not None:
        return ROUTE_PYTHON
    if (
        is_script
        and command_chars <= WINDOWS_COMMAND_LINE_MAX_CHARS
        and find_git_bash() is not None
        and read_posix_launcher(executable)[0] is not None
    ):
        return ROUTE_GIT_BASH
    return ROUTE_TOO_LONG


# Writes the arguments in the folder, and returns the short command reading them
def build_launch(route, command, env, folder):
    arguments_file = os.path.join(folder, "arguments")
    with open(arguments_file, "w", encoding="utf-8", newline="") as file:
        file.write("".join(f"{argument}\0" for argument in command[1:]))
    executable = command[0]
    if route == ROUTE_NODE:
        preload = os.path.join(folder, "arguments-preload.cjs")
        with open(preload, "w", encoding="utf-8", newline="\n") as file:
            file.write(NODE_PRELOAD)
        node_options = env.get("NODE_OPTIONS", "")
        # Forward slashes: a backslash is an escape character in NODE_OPTIONS
        require = f'--require "{preload.replace(os.sep, "/")}"'
        return [executable], {
            **env,
            "NODE_OPTIONS": f"{require} {node_options}".strip(),
            "MEGALINTER_NODE_OPTIONS": node_options,
            "MEGALINTER_ARGUMENTS_FILE": arguments_file,
        }
    if route == ROUTE_PYTHON:
        python = os.path.join(os.path.dirname(executable), "python.exe")
        name = find_python_entry_point(executable)
        return [python, "-c", PYTHON_BOOTSTRAP, name, executable, arguments_file], env
    launcher = read_posix_launcher(executable)[0]
    return [
        find_git_bash(),
        "-c",
        GIT_BASH_SCRIPT,
        "megalinter",
        arguments_file.replace("\\", "/"),
        launcher.replace("\\", "/"),
    ], {**env, "MSYS_NO_PATHCONV": "1"}
