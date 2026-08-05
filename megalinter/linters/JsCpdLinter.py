#!/usr/bin/env python3
"""
Use JSCPD to detect copy-pastes
https://github.com/kucherenko/jscpd
"""

import logging
import os
import shutil
import tempfile

from megalinter import Linter, flavor_factory, utils


class JsCpdLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        self.report_tmp_folder = None
        super().__init__(params, linter_config)
        self.remove_stale_copy_paste_report()

    # jscpd no longer deletes its report on a clean run, so one left by a previous
    # run would outlive the duplication it describes. Construction time is the only
    # safe moment to drop it: MegaLinter builds every linter before running any, and
    # deleting later would reintroduce the #3979 ENOENT race against linters still
    # walking the report folder. is_active does not suffice on its own, as
    # check_active_linters_match_flavor only clears it after construction.
    def remove_stale_copy_paste_report(self):
        if (
            self.is_active is not True
            or not self.is_present_in_image_flavor()
            or self.report_folder == ""
            or not utils.can_write_report_files(self)
        ):
            return
        stale_report_folder = os.path.join(self.report_folder, "copy-paste")
        if not os.path.isdir(stale_report_folder):
            return
        try:
            shutil.rmtree(stale_report_folder)
        except OSError as e:
            logging.warning(
                f"[jscpd] Unable to remove the copy-paste report of a previous run "
                f"in {stale_report_folder}: {str(e)}"
            )

    # "all" (every linter) and "none" (a single-linter image) have no entry in
    # all_flavors.json, so they must return before the lookup, as
    # check_active_linters_match_flavor also does.
    def is_present_in_image_flavor(self):
        flavor = flavor_factory.get_image_flavor()
        if flavor in ("all", "none"):
            return True
        return self.name in flavor_factory.list_flavor_linters(flavor)

    # Special cases for build lint command
    def build_lint_command(self, file=None):
        if utils.can_write_report_files(self.master):
            # jscpd runs while other linters are still scanning the workspace:
            # writing the report in place and deleting it again on success used to
            # make concurrent project mode linters fail with ENOENT (#3979)
            self.report_tmp_folder = tempfile.mkdtemp(prefix="megalinter-jscpd-")
            self.cli_lint_extra_args += [
                "--output",
                self.report_tmp_folder,
            ]
        cmd = super().build_lint_command(file)
        # Do not use Jscpd HTML reporter if deactivated
        if not utils.can_write_report_files(self.master):
            cmd = [item.replace("console,html", "console") for item in cmd]
        return cmd

    def process_linter(self, file=None):
        # return_code stays 0 if the base call raises, so a crashed run publishes no
        # report while its temp folder is still dropped
        return_code = 0
        try:
            return_code, stdout = super().process_linter(file)
            return return_code, stdout
        finally:
            self.materialize_copy_paste_report(return_code)

    # Nothing is ever removed from the report folder here, so linters still scanning
    # the workspace cannot observe a file disappear.
    def materialize_copy_paste_report(self, return_code):
        if self.report_tmp_folder is None:
            return
        try:
            if return_code != 0 and os.path.isdir(self.report_tmp_folder):
                published_folder = os.path.join(self.report_folder, "copy-paste")
                shutil.copytree(
                    self.report_tmp_folder,
                    published_folder,
                    dirs_exist_ok=True,
                )
                # copytree ends with copystat, copying mkdtemp's 0700 onto the
                # published folder whatever the umask and leaving it untraversable
                # to a non-root consumer such as a later artifact upload step
                os.chmod(published_folder, 0o755)
        except OSError as e:
            # shutil.Error (partial copy) is an OSError subclass but carries no
            # errno/strerror pair, so e.strerror would be None for that case
            logging.warning(
                f"[jscpd] Unable to copy the copy-paste report into "
                f"{self.report_folder}: {str(e)}"
            )
        finally:
            shutil.rmtree(self.report_tmp_folder, ignore_errors=True)
            self.report_tmp_folder = None

    # Perform additional actions and provide additional details in text reporter logs
    def complete_text_reporter_report(self, _reporter_self):
        # With report files disabled jscpd runs with the console reporter alone and
        # produces nothing whatever it finds, so the absence proves nothing
        if self.status == "success" and utils.can_write_report_files(self.master):
            return [
                "",
                "No excessive copy-paste has been detected, "
                "so no copy-paste report has been generated",
            ]
        return []
