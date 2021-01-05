# Class to manage Mega-Linter plugins
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


def run_pre_post_commands(key, log_key, mega_linter):
    pre_commands = config.get_list(key, None)
    pre_commands_results = []
    if pre_commands is None:
        logging.debug(f"{log_key} No commands declared in user configuration")
        return pre_commands_results
    for command_info in pre_commands:
        pre_command_result = run_command(command_info, log_key, mega_linter)
        pre_commands_results += [pre_command_result]
    return pre_commands_results


def run_command(command_info, log_key, mega_linter):
    # Run a command in Docker image root or in workspace root
    cwd = os.getcwd()
    if command_info.get("cwd", "root") == "workspace":
        cwd = mega_linter.workspace
    logging.info(f"{log_key} run: [{command_info['command']}] in cwd [{cwd}]")
    # Run command
    process = subprocess.run(
        command_info["command"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=os.path.realpath(cwd),
        executable=shutil.which("bash") if sys.platform == "win32" else "/bin/bash",
    )
    return_code = process.returncode
    return_stdout = utils.decode_utf8(process.stdout)
    if return_code == 0:
        logging.info(f"{log_key} [{return_stdout}] {return_stdout}")
    else:
        logging.error(f"{log_key} [{return_stdout}] {return_stdout}")
    # If user defined command to fail in case of crash, stop running Mega-Linter
    if return_code > 0 and command_info.get("continue_if_failed", True) is False:
        raise Exception(f"{log_key}: User command failed, stop running Mega-Linter")
    return {
        "command_info": command_info,
        "status": return_code,
        "stdout": return_stdout,
    }
