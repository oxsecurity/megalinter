#!/usr/bin/env python3
"""
Use cspell to check spell in files
https://github.com/nvuillam/npm-groovy-lint
"""
import os
import shutil

from megalinter import Linter


class JsCpdLinter(Linter):

    # Perform additional actions and provide additional details in text reporter logs
    # noinspection PyMethodMayBeStatic
    def complete_text_reporter_report(self, reporter_self):
        if reporter_self.master.return_code == 0:
            copy_paste_dir = reporter_self.master.report_folder + "copy-paste"
            if os.path.isdir(copy_paste_dir):
                try:
                    shutil.rmtree(copy_paste_dir)
                except OSError as e:
                    return [
                        "",
                        f"No copy-paste has been detected, but unable to remove {copy_paste_dir}: {e.strerror}"
                    ]
                return ["", "copy-paste folder has been removed, as no abusive copy-paste has been detected"]
        return []
