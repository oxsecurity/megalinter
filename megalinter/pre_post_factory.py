# Class to manage MegaLinter plugins
import logging
import os
import shutil
import subprocess
import sys

from megalinter import config, utils


# User defined commands to run before running linters
def run_pre_commands(mega_linter):
    return run_pre_post_commands("PRE_COMMANDS", "[Pre]", mega_linter)


# User defined commands to run after running linters
def run_post_commands(mega_linter):
    return run_pre_post_commands("POST_COMMANDS", "[Post]", mega_linter)


# Commands to run before running all linters in a descriptor
def run_descriptor_pre_commands(mega_linter, descriptor_id):
    return run_pre_post_commands(
        f"{descriptor_id}_PRE_COMMANDS", f"[Pre][{descriptor_id}]", mega_linter
    )


# Commands to run after running all linters in a descriptor
def run_descriptor_post_commands(mega_linter, descriptor_id):
    return run_pre_post_commands(
        f"{descriptor_id}_POST_COMMANDS", f"[Post][{descriptor_id}]", mega_linter
    )


# Commands to run before a linter (defined in descriptors)
def run_linter_pre_commands(mega_linter, linter):
    if linter.pre_commands is not None:
        return run_commands(
            linter.pre_commands, "[Pre][" + linter.name + "]", mega_linter, linter
        )
    return []


# Commands to run before a linter (defined in descriptors)
def run_linter_post_commands(mega_linter, linter):
    if linter.post_commands is not None:
        return run_commands(
            linter.post_commands, "[Post][" + linter.name + "]", mega_linter, linter
        )
    return []


# Get commands from configuration
def run_pre_post_commands(key, log_key, mega_linter):
    pre_or_post_commands = config.get_list(mega_linter.request_id, key, None)
    return run_commands(pre_or_post_commands, log_key, mega_linter)


# Perform run of commands
def run_commands(all_commands, log_key, mega_linter, linter=None):
    pre_commands_results: list = []
    if all_commands is None:
        logging.debug(f"{log_key} No commands declared in user configuration")
        return pre_commands_results
    for command_info in all_commands:
        pre_command_result = run_command(command_info, log_key, mega_linter, linter)
        pre_commands_results += [pre_command_result]
    return pre_commands_results


def run_command(command_info, log_key, mega_linter, linter=None):
    # Run a command in Docker image root or in workspace root
    cwd = os.getcwd()
    if command_info.get("cwd", "root") == "workspace":
        cwd = mega_linter.workspace
        # Secure env by default. Must be explicitly define to false in command definition to be disabled
    if "secured_env" not in command_info:
        command_info["secured_env"] = True
    command_info = complete_command(command_info)
    unsecured_env_variables = []
    if linter is not None:
        unsecured_env_variables = linter.unsecured_env_variables
    subprocess_env = {
        **config.build_env(
            mega_linter.request_id, command_info["secured_env"], unsecured_env_variables
        )
    }
    add_in_logs(
        linter,
        log_key,
        [f"{log_key} run: [{command_info['command']}] in cwd [{cwd}]"],
    )
    # Run command
    process = subprocess.run(
        command_info["command"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=os.path.realpath(cwd),
        executable=shutil.which("bash") if sys.platform == "win32" else "/bin/bash",
        env=subprocess_env,
    )
    return_code = process.returncode
    return_stdout = utils.decode_utf8(process.stdout)
    if return_code == 0:
        add_in_logs(linter, log_key, [f"{log_key} result:\n{return_stdout}"])
    else:
        add_in_logs(linter, log_key, [f"{log_key} error:\n{return_stdout}"])
    # If user defined command to fail in case of crash, stop running MegaLinter
    if return_code > 0 and command_info.get("continue_if_failed", True) is False:
        raise Exception(
            f"{log_key}: User command failed, stop running MegaLinter\n{return_stdout}"
        )
    return {
        "command_info": command_info,
        "status": return_code,
        "stdout": return_stdout,
    }


def complete_command(command_info: dict):
    # Force npm install in /node-deps ONLY if cwd is root
    command: str = command_info["command"]
    if command.startswith("npm i") and command_info.get("cwd", "root") == "root":
        command_info["command"] = "cd /node-deps && " + command_info["command"]
    # Pip dependencies case
    elif command_info.get("venv", None) is not None:
        venv = command_info.get("venv")
        command_info["command"] = (
            f"cd /venvs/{venv} && source bin/activate && {command} && deactivate"
        )
    return command_info


def add_in_logs(linter, log_key, lines):
    if linter is not None:
        if "[Pre]" in log_key:
            linter.log_lines_pre += lines
        elif "[Post]" in log_key:
            linter.log_lines_post += lines
    else:
        logging.info("\n".join(lines))


def has_npm_or_yarn_commands(request_id):
    config_dict = config.get(request_id)
    for key in config_dict.keys():
        if "PRE_COMMANDS" in key or "POST_COMMANDS" in key:
            for command_info in config.get_list(request_id, key, []):
                if (
                    "command" in command_info
                    and "npm" in command_info["command"]
                    or "yarn" in command_info["command"]
                ):
                    return True
    return False
