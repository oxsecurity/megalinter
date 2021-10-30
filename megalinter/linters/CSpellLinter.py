#!/usr/bin/env python3
"""
Use cspell to check spell in files
https://github.com/streetsidesoftware/cspell
"""
import json
import logging
import os
import re

from megalinter import Linter, utils


class CSpellLinter(Linter):

    # Provide additional details in text reporter logs
    # noinspection PyMethodMayBeStatic
    def complete_text_reporter_report(self, reporter_self):
        # Collect detected words from logs
        if self.stdout is None:
            return []
        whitelisted_words = []
        for log_line in self.stdout.split("\n"):
            words = re.findall(r"(?<=Unknown word )\((.*)\)", log_line, re.MULTILINE)
            whitelisted_words += words
        if len(whitelisted_words) == 0:
            return []
        # Sort and make list unique
        whitelisted_words_clean = sorted(set(whitelisted_words))
        # Generate possible .cspell.json file
        cspell_example = {
            "version": "0.1",
            "language": "en",
            "ignorePaths": [
                "**/node_modules/**",
                "**/vscode-extension/**",
                "**/.git/**",
                ".vscode",
                "package-lock.json",
                "report",
            ],
            "words": whitelisted_words_clean,
        }
        cspell_example_json = json.dumps(cspell_example, indent=4)
        additional_report = f"""
You can skip this misspellings by defining the following .cspell.json file at the root of your repository
Of course, please correct real typos before :)

{cspell_example_json}

"""
        logging.debug(
            f"Generated additional TextReporter log for CSpellLinter:\n{additional_report}"
        )

        # Generate updated .cspell.json for manual update
        cspell_config_file = (
            reporter_self.master.github_workspace
            + os.path.sep
            + reporter_self.master.config_file_name
        )
        if os.path.isfile(cspell_config_file):
            try:
                with open(cspell_config_file, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
            except ValueError:
                logging.error(
                    f"[cspell] ERROR: Unable to parse {cspell_config_file} JSON data"
                    "please fix it manually before running Mega-Linter again"
                )
                return []
            prev_words = data.get("words", [])
            new_words = sorted(set(whitelisted_words_clean + prev_words))
            data["words"] = new_words
        else:
            data = cspell_example
        proposed_cspell_config_file = (
            reporter_self.report_folder
            + os.path.sep
            + reporter_self.master.config_file_name
        )
        with open(proposed_cspell_config_file, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
        proposed_cspell_config_file = utils.normalize_log_string(
            proposed_cspell_config_file
        )
        additional_report += "\n".join(
            [
                "",
                f"You can also copy-paste {proposed_cspell_config_file} at the root of your repository",
            ]
        )
        return additional_report.splitlines()
