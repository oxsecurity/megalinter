# Class to manage MegaLinter plugins
import logging
import os
import re
import shutil
import subprocess
import sys

from megalinter import config, utils


# User defined commands to run before running linters
def run_pre_commands(mega_linter, tag="default"):
    return run_pre_post_commands("PRE_COMMANDS", "[Pre]", mega_linter, tag)


# User defined commands to run after running linters
def run_post_commands(mega_linter, tag="default"):
    return run_pre_post_commands("POST_COMMANDS", "[Post]", mega_linter, tag)


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
def run_linter_pre_commands(mega_linter, linter, run_before_linters=None):
    if linter.pre_commands is not None:
        filtered_commands: list = []

        if run_before_linters is None:
            filtered_commands = linter.pre_commands
        else:
            for command_info in linter.pre_commands:
                if command_info.get("run_before_linters", False) is run_before_linters:
                    filtered_commands.append(command_info)

        return run_commands(
            filtered_commands, "[Pre][" + linter.name + "]", mega_linter, linter
        )
    return []


# Commands to run before a linter (defined in descriptors)
def run_linter_post_commands(mega_linter, linter, run_after_linters=None):
    if linter.post_commands is not None:
        filtered_commands: list = []

        if run_after_linters is None:
            filtered_commands = linter.post_commands
        else:
            for command_info in linter.post_commands:
                if command_info.get("run_after_linters", False) is run_after_linters:
                    filtered_commands.append(command_info)

        return run_commands(
            filtered_commands, "[Post][" + linter.name + "]", mega_linter, linter
        )
    return []


# Get commands from configuration
def run_pre_post_commands(key, log_key, mega_linter, tag="default"):
    pre_or_post_commands = config.get_list(mega_linter.request_id, key, None)
    if pre_or_post_commands is None:
        logging.debug(f"{log_key} No commands declared in user configuration")
        return []
    # Filter commands according to tag
    applicable_pre_post_commands = []
    for command in pre_or_post_commands:
        if (
            tag == "default"
            and (("tag" not in command) or (command["tag"] == "default"))
        ) or (tag != "default" and "tag" in command and command["tag"] == tag):
            applicable_pre_post_commands += [command]
    # Run matching commands
    return run_commands(applicable_pre_post_commands, log_key, mega_linter)


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
    # Check if command_info is a string (should not happen but will allow to investigate)
    if isinstance(command_info, str):
        add_in_logs(
            linter,
            log_key,
            [f"{log_key} run: ERROR command_info type: {command_info}"],
        )
        return {
            "command_info": command_info,
            "status": 0,
            "stdout": f"Command info is a string ({command_info}), should be a dict",
        }
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
    # Complete with replacement variables if necessary
    if "replacement_env_vars" in command_info:
        for replacement in command_info["replacement_env_vars"]:
            if replacement["var_src"] in subprocess_env:
                var_src_name = replacement["var_src"]
                var_dest_name = replacement["var_dest"]
                subprocess_env[var_dest_name] = subprocess_env[var_src_name]
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
    # Get output variables if defined
    if command_info.get("output_variables", None) is not None:
        for output_variable in command_info["output_variables"]:
            regex_start = f"output of {output_variable}:"
            if regex_start in return_stdout:
                match = re.search(rf"{regex_start}(.+)", return_stdout)
                if match:
                    output_variable_value = match.group(1).strip()
                    if (
                        config.get(mega_linter.request_id, output_variable, None)
                        != output_variable_value
                    ):
                        config.set_value(
                            mega_linter.request_id,
                            output_variable,
                            output_variable_value,
                        )
                        add_in_logs(
                            linter,
                            log_key,
                            [
                                f"{log_key} updated ENV var {output_variable}] from command output"
                            ],
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
    # Handle output vars if present
    if command_info.get("output_variables", None) is not None:
        for output_variable in command_info["output_variables"]:
            command_info[
                "command"
            ] += f' && echo "output of {output_variable}:${output_variable}"'
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
