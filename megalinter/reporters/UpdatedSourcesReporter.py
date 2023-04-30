#!/usr/bin/env python3
"""
Updated Repository reporter
Creates a folder containing only files updated by the linters
"""
import logging
import os
import shutil

from megalinter import Reporter, config, utils


class UpdatedSourcesReporter(Reporter):
    name = "UPDATED_SOURCES"
    scope = "mega-linter"

    def __init__(self, params=None):
        # Activate update repository reporter by default
        self.is_active = True
        super().__init__(params)

    def manage_activation(self):
        if not utils.can_write_report_files(self.master):
            self.is_active = False
        elif (
            config.get(self.master.request_id, "UPDATED_SOURCES_REPORTER", "true")
            != "true"
        ):
            self.is_active = False

    def produce_report(self):
        logging.debug("Start updated Sources Reporter")
        # Copy updated files in report folder
        updated_files = utils.list_updated_files(self.master.github_workspace)
        logging.debug("Updated files :\n" + "\n -".join(updated_files))
        updated_dir = config.get(
            self.master.request_id, "UPDATED_SOURCES_REPORTER_DIR", "updated_sources"
        )
        updated_sources_dir = f"{self.report_folder}{os.path.sep}{updated_dir}"
        for updated_file in updated_files:
            updated_file_clean = utils.normalize_log_string(updated_file)
            if os.path.basename(updated_file_clean) in [
                "linter-helps.json",
                "linter-versions.json",
            ]:
                continue
            source_file = utils.REPO_HOME_DEFAULT + os.path.sep + updated_file
            if not os.path.isfile(source_file):
                source_file = updated_file
            target_file = f"{updated_sources_dir}{os.path.sep}{updated_file_clean}"
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            try:
                shutil.copy(source_file, target_file)
                logging.debug(f"Copied {source_file} to {target_file}")
            except FileNotFoundError as copy_err:
                logging.warning(
                    f"[Updated Sources Reporter] Unable to copy {source_file} to {target_file} ({str(copy_err)})"
                )
        # Log
        if len(updated_files) > 0:
            logging.info(
                f"[Updated Sources Reporter] copied {str(len(updated_files))} fixed source files"
                f" in folder {updated_sources_dir}.\n"
                "Download it from artifacts then copy-paste it in your local repo to apply linters updates"
            )
        else:
            logging.info(
                "[Updated Sources Reporter] No source file has been formatted or fixed"
            )
