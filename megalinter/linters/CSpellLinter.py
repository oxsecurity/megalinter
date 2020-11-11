#!/usr/bin/env python3
"""
Use cspell to check spell in files
https://github.com/nvuillam/npm-groovy-lint
"""
import json
import logging
import os.path
import re

from megalinter import Linter


class CSpellLinter(Linter):

    # Provide additional details in text reporter logs
    # noinspection PyMethodMayBeStatic
    def complete_text_reporter_report(self, reporter_self):
        # Collect detected words from logs
        whitelisted_words = []
        for log_line in reporter_self.report_items:
            word = re.match(r"Unknown word \((.*)\)", log_line)
            if word:
                whitelisted_words += [word.group(0)]
        if len(whitelisted_words) == 0:
            return []
        # Sort and make list unique
        whitelisted_words_clean = sorted(set(whitelisted_words))
        # Generate possible .cspell.json file
        cspell_example = {
            "version": 0.1,
            "language": "en",
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
        return additional_report.split(os.linesep)
