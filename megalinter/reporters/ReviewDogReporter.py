#!/usr/bin/env python3
"""
ReviewDog reporter
When the linter allows it, call reviewdog to generate code reviews on related platform
https://github.com/reviewdog/reviewdog
"""
import logging
import shutil
import subprocess
import sys

from megalinter import Reporter, config, utils


class ReviewDogReporter(Reporter):
    name = "REVIEW_DOG"
    scope = "linter"

    github_api_url = "https://api.github.com"
    github_server_url = "https://github.com"

    def __init__(self, params=None):
        # Activate GitHub Status by default
        self.is_active = False
        super().__init__(params)

    def manage_activation(self):
        # Enable reviewdog if wanted by the user
        if config.get("REVIEW_DOG_REPORTER", "false") == "true":
            self.is_active = True

    def produce_report(self):
        if self.master.stdout is not None:

            # Call reviewdog
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                executable=shutil.which("bash")
                if sys.platform == "win32"
                else "/bin/bash",
            )
            return_code = process.returncode
            return_stdout = utils.decode_utf8(process.stdout)
            if return_code == 0:
                logging.info(
                    f"[ReviewDog Reporter] Successfully called ReviewDog for {self.master.descriptor_id} "
                    f"with {self.master.linter_name}")
            else:
                logging.warning(
                    f"[ReviewDog Reporter] Error while calling ReviewDog for {self.master.descriptor_id} "
                    f"with {self.master.linter_name}:\n{return_stdout}")
        else:
            logging.debug(
                f"[ReviewDog Reporter] Skipped ReviewDog reporter for {self.master.descriptor_id} "
                f"with {self.master.linter_name}: No single stdout"
            )
