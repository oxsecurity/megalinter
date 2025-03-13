#!/usr/bin/env python3
"""
Send reports artifacts by email
"""
import logging
import os
import tempfile
import zipfile
from json.decoder import JSONDecodeError

import requests
from megalinter import Reporter, config


class FileIoReporter(Reporter):
    name = "FILEIO"
    scope = "mega-linter"

    def __init__(self, params=None):
        # Activate email output by default
        self.is_active = False
        self.processing_order = 9
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "FILEIO_REPORTER", "false") == "true":
            self.is_active = True

    def produce_report(self):
        # Skip report if no errors has been found
        if (
            self.master.status == "success"
            and config.get(
                self.master.request_id, "FILEIO_REPORTER_SEND_SUCCESS", "false"
            )
            == "true"
            and self.master.has_updated_sources is False
        ):
            logging.info(
                "[File.io Reporter] No file sent, "
                "as the MegaLinter status is success and there are no updated source"
            )
            return

        # Create temporary zip file with content of report folder
        zf = tempfile.TemporaryFile(prefix="mail", suffix=".zip")
        zip_file = zipfile.ZipFile(zf, "w")
        for root, dirs, files in os.walk(self.report_folder):
            for file in files:
                file_abs_path = os.path.join(root, file)
                if os.path.splitext(file_abs_path) not in [".js", ".map"]:
                    zip_file.write(
                        file_abs_path,
                        arcname=file_abs_path.replace(self.report_folder, ""),
                    )
        zip_file.close()
        zf.seek(0)

        # Post file on file.io API
        try:
            url = "https://file.io/?expires=1d"
            files = {"file": ("mega-linter-report.zip", zf.read())}
            response = requests.post(url, files=files)
            if 200 <= response.status_code < 299:
                json_data = response.json()
                file_io_url = json_data["link"]
                logging.info(
                    f"[File.io Reporter] Reports are available at {file_io_url}"
                )
            else:
                json_data = response.json()
                logging.warning(
                    f"[File.io Reporter] Error posting report on file.io: {response.status_code} \n {json_data}"
                )
                logging.warning(
                    f"[File.io Reporter] GitHub API response: {response.text}"
                )
        except JSONDecodeError as e:
            logging.warning(
                f"[File.io Reporter] Fatal error posting report on file.io: {str(e.msg)}"
            )
        except Exception as e:
            logging.warning(
                f"[File.io Reporter] Fatal error posting report on file.io: {str(e)}"
            )
