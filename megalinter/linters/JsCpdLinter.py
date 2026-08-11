#!/usr/bin/env python3
"""
Use JSCPD to detect copy-pastes
https://github.com/kucherenko/jscpd
"""

import json
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
        # jscpd's sarif reporter is a value within the single comma-joined
        # --reporters string, not a standalone CLI flag: append it here
        # rather than through cli_sarif_args, which would need a second
        # --reporters occurrence that may not merge with the first.
        # jscpd (pinned v5.0.14) writes it to <output>/jscpd-report.sarif,
        # picked up afterwards via sarif_default_output_file.
        if self.can_output_sarif is True and self.output_sarif is True:
            self.cli_lint_extra_args = [
                item.replace("console,html", "console,html,sarif")
                for item in self.cli_lint_extra_args
            ]
            self.sarif_default_output_file = "copy-paste/jscpd-report.sarif"
        cmd = super().build_lint_command(file)
        # Do not use Jscpd HTML reporter if deactivated
        if not utils.can_write_report_files(self.master):
            cmd = [item.replace("console,html", "console") for item in cmd]
        return cmd

    # Forward excluded directories through a generated config: the jscpd
    # --ignore CLI argument would replace the resolved config's ignore list
    # wholesale, so the globs are merged into the config instead
    def manage_excluded_directories_config(self, cmd):
        if any(arg in ("-i", "--ignore") for arg in cmd):
            return cmd
        config_index = self.find_cli_argument_value_index(cmd, ("-c", "--config"))
        config_content = {}
        if config_index is not None:
            with open(cmd[config_index], encoding="utf-8") as config_file:
                config_content = json.load(config_file)
        ignore_globs = list(config_content.get("ignore", []))
        for excluded_dir in self.get_project_exclude_directories():
            glob = f"**/{excluded_dir}/**"
            if glob not in ignore_globs:
                ignore_globs += [glob]
        config_content["ignore"] = ignore_globs
        generated_config = self.write_report_generated_file(
            "jscpd-config.json", json.dumps(config_content, indent=2).splitlines()
        )
        cmd = self.replace_or_append_cli_argument(
            cmd, config_index, "-c", generated_config
        )
        self.log_project_exclude_forwarding(
            f"Generated {generated_config} merging EXCLUDED_DIRECTORIES into the "
            f"jscpd ignore list "
            f"(disable with {self.name}_FORWARD_EXCLUDED_DIRECTORIES: false)"
        )
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
