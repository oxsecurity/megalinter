#!/usr/bin/env python3
"""
Use Shellcheck to analyze shell / bash code
"""

import logging
import subprocess

from megalinter import Linter, config, utils


class ShellcheckLinter(Linter):
    # Call shellcheck-sarif to convert default output to sarif
    # https://crates.io/crates/shellcheck-sarif
    def manage_sarif_output(self, return_stdout):
        if self.can_output_sarif is True and self.output_sarif is True:
            shellcheck_sarif_cmd = "shellcheck-sarif"
            process = subprocess.run(
                shellcheck_sarif_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                input=return_stdout + "\n",
                env=config.build_env(self.request_id),
            )
            return_code = process.returncode
            shellcheck_res_sarif = utils.decode_utf8(process.stdout)
            logging.debug(
                "shellcheck-sarif output"
                + str(return_code)
                + "\n"
                + shellcheck_res_sarif
            )
            with open(self.sarif_output_file, "w", encoding="utf-8") as outfile:
                outfile.write(shellcheck_res_sarif)
        super().manage_sarif_output(return_stdout)
