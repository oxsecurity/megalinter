import configparser
import glob
import locale
import os
import re
import shlex
import shutil
import subprocess

from megalinter.native.context import find_git_bash

# Windows caps a command line at 32767 characters, and at 8191 when it goes through
# cmd.exe (.cmd and .bat launchers, like the ones npm creates). The margin covers
# what a launcher adds when it expands its own path and the path of the tool
WINDOWS_COMMAND_LINE_MAX_CHARS = 32000
WINDOWS_SCRIPT_COMMAND_LINE_MAX_CHARS = 7000
# Shortest command tried when a wrapped program can not start
WINDOWS_MIN_RETRY_CHARS = 2000

ROUTE_DIRECT = "direct"
ROUTE_NODE = "node"
ROUTE_PYTHON = "python"
ROUTE_PHP = "php"
ROUTE_JAVA = "java"
ROUTE_RUBY = "ruby"
ROUTE_GIT_BASH = "git_bash"
ROUTE_TOO_LONG = "too_long"

NODE_LAUNCHER_REGEX = re.compile(rb'exec\s+(?:"\$basedir/node"|node)\s')
# A tool started through a file can still start another program with all its
# arguments (ex: a npm package wrapping a native binary). These errors do not
# depend on the language of Windows
LAUNCH_FAILURE_REGEX = re.compile(
    r"spawn(?:Sync)?\b[^\n]*ENAMETOOLONG|\[WinError 206\]|CreateProcess error=206"
    r"|: Argument list too long|proc_open\(\): CreateProcess failed"
    r"|Errno::E(?:2BIG|NAMETOOLONG)"
    r"|The command line is too long|La ligne de commande est trop longue"
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

# Loaded by php before the tool (auto_prepend_file), and not by its child processes
PHP_PRELOAD = r"""<?php
$megalinterArgumentsFile = getenv('MEGALINTER_ARGUMENTS_FILE');
if ($megalinterArgumentsFile !== false) {
    $megalinterScanDir = getenv('MEGALINTER_PHP_INI_SCAN_DIR');
    putenv('MEGALINTER_ARGUMENTS_FILE');
    putenv('MEGALINTER_PHP_INI_SCAN_DIR');
    putenv($megalinterScanDir ? "PHP_INI_SCAN_DIR=$megalinterScanDir" : 'PHP_INI_SCAN_DIR');
    $megalinterArguments = explode("\0", file_get_contents($megalinterArgumentsFile));
    array_pop($megalinterArguments);
    $_SERVER['argv'] = array_merge($_SERVER['argv'], $megalinterArguments);
    $_SERVER['argc'] = count($_SERVER['argv']);
    $GLOBALS['argv'] = $_SERVER['argv'];
    $GLOBALS['argc'] = $_SERVER['argc'];
    unset($megalinterArgumentsFile, $megalinterScanDir, $megalinterArguments);
}
"""

# Loaded by ruby before the tool, and not by its child processes
RUBY_PRELOAD = r"""arguments_file = ENV.delete("MEGALINTER_ARGUMENTS_FILE")
if arguments_file
  { "RUBYOPT" => "MEGALINTER_RUBYOPT", "RUBYLIB" => "MEGALINTER_RUBYLIB" }.each do |name, saved|
    value = ENV.delete(saved)
    ENV[name] = value.nil? || value.empty? ? nil : value
  end
  ARGV.concat(File.read(arguments_file, encoding: "utf-8").split("\0"))
end
"""

# bundle exec relaunches a .bat file on Windows: the gem executable is loaded directly
RUBY_BUNDLE_LOAD = (
    'tool = ENV.delete("MEGALINTER_RUBY_TOOL"); '
    "spec = Gem.loaded_specs.values.find { |s| s.executables.include?(tool) }; "
    "$0 = spec.bin_file(tool); load $0"
)

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


# The command of a launcher written by MegaLinter: exec <program> <args> "$@"
def read_launcher_command(executable):
    if not is_windows_script(executable):
        return None
    _launcher, content = read_posix_launcher(executable)
    if content is None:
        return None
    for line in content.decode("utf-8", "replace").splitlines():
        if not line.startswith("exec "):
            continue
        try:
            parts = shlex.split(line)[1:]
        except ValueError:
            return None
        return parts[:-1] if len(parts) > 1 and parts[-1] == "$@" else None
    return None


def launcher_program(parts):
    name = os.path.basename(parts[0].replace("\\", "/")).lower()
    return os.path.splitext(name)[0]


def is_java_executable(executable):
    return os.path.basename(executable).lower() == "java.exe"


def find_runtime_route(command):
    if is_java_executable(command[0]):
        return ROUTE_JAVA if can_encode_for_java(command) else None
    parts = read_launcher_command(command[0])
    if not parts:
        return None
    program = launcher_program(parts)
    if program == "php":
        return ROUTE_PHP
    if program == "bundle" and parts[1:2] == ["exec"]:
        return ROUTE_RUBY
    if program == "java" and can_encode_for_java(command):
        return ROUTE_JAVA
    return None


# The java launcher reads its argument files in the encoding of the system
def can_encode_for_java(command):
    try:
        "".join(command[1:]).encode(locale.getencoding())
    except UnicodeEncodeError:
        return False
    return True


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


# Longest command that can really start this tool
def max_chars_for(executable):
    if (
        is_windows_script(executable)
        and not is_node_launcher(executable)
        and (find_git_bash() is None or read_posix_launcher(executable)[0] is None)
    ):
        return WINDOWS_SCRIPT_COMMAND_LINE_MAX_CHARS
    return WINDOWS_COMMAND_LINE_MAX_CHARS


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
    runtime_route = find_runtime_route(command)
    if runtime_route is not None:
        return runtime_route
    if (
        is_script
        and command_chars <= WINDOWS_COMMAND_LINE_MAX_CHARS
        and find_git_bash() is not None
        and read_posix_launcher(executable)[0] is not None
    ):
        return ROUTE_GIT_BASH
    return ROUTE_TOO_LONG


# Writes the arguments in the folder, and returns the short command reading them
# PHP getopt() only sees the real command line: options stay on it, and only the files
# at the end of the command go through the file
def split_trailing_files(command, files):
    first_file = len(command) - len(files or [])
    if files and first_file > 0 and command[first_file:] == list(files):
        return command[:first_file], list(files)
    return [command[0]], command[1:]


def build_launch(route, command, env, folder, files=None):
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
    if route == ROUTE_PHP:
        with open(
            os.path.join(folder, "arguments-preload.php"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as file:
            file.write(PHP_PRELOAD)
        preload = os.path.join(folder, "arguments-preload.php").replace("\\", "/")
        with open(
            os.path.join(folder, "megalinter-arguments.ini"), "w", encoding="utf-8"
        ) as file:
            file.write(f'auto_prepend_file="{preload}"\n')
        scan_dir = env.get("PHP_INI_SCAN_DIR", "")
        php_command, php_arguments = split_trailing_files(command, files)
        with open(arguments_file, "w", encoding="utf-8", newline="") as file:
            file.write("".join(f"{argument}\0" for argument in php_arguments))
        return php_command, {
            **env,
            "PHP_INI_SCAN_DIR": f"{scan_dir};{folder}" if scan_dir else folder,
            "MEGALINTER_PHP_INI_SCAN_DIR": scan_dir,
            "MEGALINTER_ARGUMENTS_FILE": arguments_file,
        }
    if route == ROUTE_RUBY:
        with open(
            os.path.join(folder, "megalinter_arguments.rb"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as file:
            file.write(RUBY_PRELOAD)
        ruby_lib = env.get("RUBYLIB", "")
        ruby_options = env.get("RUBYOPT", "")
        parts = read_launcher_command(executable)
        ruby = os.path.join(os.path.dirname(parts[0]), "ruby.exe")
        if not os.path.isfile(ruby):
            ruby = shutil.which("ruby", path=env.get("PATH")) or "ruby"
        return [ruby, "-rbundler/setup", "-e", RUBY_BUNDLE_LOAD], {
            **env,
            "MEGALINTER_RUBY_TOOL": parts[2],
            "RUBYLIB": f"{folder};{ruby_lib}" if ruby_lib else folder,
            "RUBYOPT": f"-rmegalinter_arguments {ruby_options}".strip(),
            "MEGALINTER_RUBYLIB": ruby_lib,
            "MEGALINTER_RUBYOPT": ruby_options,
            "MEGALINTER_ARGUMENTS_FILE": arguments_file,
        }
    if route == ROUTE_JAVA:
        parts = (
            [executable]
            if is_java_executable(executable)
            else read_launcher_command(executable)
        )
        java_file = os.path.join(folder, "java-arguments")
        with open(java_file, "w", encoding=locale.getencoding(), newline="\n") as file:
            for argument in [*parts[1:], *command[1:]]:
                escaped = argument.replace("\\", "\\\\").replace('"', '\\"')
                file.write(f'"{escaped}"\n')
        java = (
            executable
            if is_java_executable(executable)
            else shutil.which(parts[0], path=env.get("PATH")) or parts[0]
        )
        return [java, f"@{java_file}"], env
    launcher = read_posix_launcher(executable)[0]
    return [
        find_git_bash(),
        "-c",
        GIT_BASH_SCRIPT,
        "megalinter",
        arguments_file.replace("\\", "/"),
        launcher.replace("\\", "/"),
    ], {**env, "MSYS_NO_PATHCONV": "1"}
