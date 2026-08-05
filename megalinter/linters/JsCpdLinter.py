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
        cmd = super().build_lint_command(file)
        # Do not use Jscpd HTML reporter if deactivated
        if not utils.can_write_report_files(self.master):
            cmd = [item.replace("console,html", "console") for item in cmd]
        if (
            self.cli_lint_mode == "project"
            and self.is_project_exclude_forwarding_active()
            and not any(arg in ("-i", "--ignore") for arg in cmd)
        ):
            cmd = self.manage_excluded_directories_config(cmd)
        return cmd

    # Forward excluded directories through a generated config: the jscpd
    # --ignore CLI argument would replace the resolved config's ignore list
    # wholesale, so the globs are merged into the config instead
    def manage_excluded_directories_config(self, cmd):
        existing_config_index = None
        for index, arg in enumerate(cmd):
            if arg in ("-c", "--config") and index + 1 < len(cmd):
                existing_config_index = index + 1
                break
        config_content = {}
        if existing_config_index is not None:
            with open(cmd[existing_config_index], encoding="utf-8") as config_file:
                config_content = json.load(config_file)
        ignore_globs = list(config_content.get("ignore", []))
        for excluded_dir in self.get_project_exclude_directories():
            glob = f"**/{excluded_dir}/**"
            if glob not in ignore_globs:
                ignore_globs += [glob]
        config_content["ignore"] = ignore_globs
        generated_config = os.path.join(self.report_folder, "jscpd-config.json")
        os.makedirs(self.report_folder, exist_ok=True)
        with open(generated_config, "w", encoding="utf-8") as config_file:
            json.dump(config_content, config_file, indent=2)
        if existing_config_index is not None:
            cmd[existing_config_index] = generated_config
        else:
            cmd += ["-c", generated_config]
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
