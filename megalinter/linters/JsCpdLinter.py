#!/usr/bin/env python3
"""
Use JSCPD to detect copy-pastes
https://github.com/kucherenko/jscpd
"""
import os
import shutil

from megalinter import Linter, utils


class JsCpdLinter(Linter):
    # Special cases for build lint command
    def build_lint_command(self, file=None):
        if utils.can_write_report_files(self.master):
            self.cli_lint_extra_args += [
                "--output",
                f"{self.report_folder}/copy-paste/",
            ]
        cmd = super().build_lint_command(file)
        # Do not use Jscpd HTML reporter if deactivated
        if not utils.can_write_report_files(self.master):
            cmd = [item.replace("console,html", "console") for item in cmd]
        return cmd

    # Perform additional actions and provide additional details in text reporter logs
    def complete_text_reporter_report(self, reporter_self):
        if self.status == "success":
            copy_paste_dir = (
                reporter_self.master.report_folder + os.path.sep + "copy-paste"
            )
            if os.path.isdir(copy_paste_dir):
                try:
                    shutil.rmtree(copy_paste_dir)
                except OSError as e:
                    return [
                        "",
                        f"No copy-paste has been detected, but unable to remove {copy_paste_dir}: {e.strerror}",
                    ]
                return [
                    "",
                    "copy-paste folder has been removed, as no excessive copy-paste has been detected",
                ]
        return []
