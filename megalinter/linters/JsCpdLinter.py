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
        # COPYPASTE_JSCPD_DISABLE_ERRORS_IF_LESS_THAN only has effect if jscpd
        # exits nonzero, and by default jscpd exits 0 when clones are found.
        # Only pass --exitCode 1 when
        # COPYPASTE_JSCPD_DISABLE_ERRORS_IF_LESS_THAN > 0, because the jscpd
        # threshold option becomes moot once jscpd exits nonzero whenever any
        # clones are found.
        if self.disable_errors_if_less_than:
            cmd += ["--exitCode", "1"]
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
