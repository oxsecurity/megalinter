#!/usr/bin/env python3
"""
Use PHP to lint php files
https://www.php.net
"""
import logging
import subprocess

from megalinter import Linter, config, utils

class PhpLinter(Linter):

    # To execute before linting files
    def before_lint_files(self):
        php_version = config.get("PHP_VERSION", "7")
        if php_version == "7":
            return
        pre_command = f"update-alternatives --set php /usr/bin/php{php_version}"
        logging.debug("PHP before_lint_files: " + pre_command)
        process = subprocess.run(
            pre_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        return_code = process.returncode
        return_stdout = utils.decode_utf8(process.stdout)
        logging.debug(f"{return_code} : {return_stdout}")
