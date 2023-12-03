#!/usr/bin/env python3
"""
Send reports artifacts by email
"""
import logging
import os
import smtplib
import tempfile
import zipfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from megalinter import Reporter, config


class EmailReporter(Reporter):
    name = "EMAIL"
    scope = "mega-linter"

    def __init__(self, params=None):
        # Activate email output by default
        self.is_active = True
        self.processing_order = 9
        super().__init__(params)

    def manage_activation(self):
        if config.get(self.master.request_id, "EMAIL_REPORTER", "true") != "true":
            self.is_active = False
        elif (
            config.get(self.master.request_id, "EMAIL_REPORTER_EMAIL", "none") == "none"
        ):
            logging.info(
                "To receive reports as email, please set variable EMAIL_REPORTER_EMAIL"
            )
            self.is_active = False

    def produce_report(self):
        # Skip report if no errors has been found
        if (
            self.master.status == "success"
            and config.get(
                self.master.request_id, "EMAIL_REPORTER_SEND_SUCCESS", "false"
            )
            == "true"
            and self.master.has_updated_sources is False
        ):
            logging.info(
                "[Email Reporter] No mail sent, "
                "as the MegaLinter status is success and there are no updated source"
            )
            return

        # get server and email config values
        smtp_host = config.get(
            self.master.request_id, "EMAIL_REPORTER_SMTP_HOST", "smtp.gmail.com"
        )
        smtp_port = config.get(self.master.request_id, "EMAIL_REPORTER_SMTP_PORT", 465)
        recipients = config.get_list(self.master.request_id, "EMAIL_REPORTER_EMAIL", [])
        sender = config.get(
            self.master.request_id, "EMAIL_REPORTER_SENDER", "megalinter@gmail.com"
        )
        smtp_username = config.get(
            self.master.request_id, "EMAIL_REPORTER_SMTP_USERNAME", sender
        )
        smtp_password = config.get(
            self.master.request_id, "EMAIL_REPORTER_SMTP_PASSWORD", ""
        )

        # Skip report if SMTP password is not set
        if smtp_password == "":
            logging.info(
                "[Email Reporter] No mail sent, as EMAIL_REPORTER_SMTP_PASSWORD configuration variable is missing"
            )
            return

        # Create temporary zip file with content of report folder
        zf = tempfile.TemporaryFile(prefix="mail", suffix=".zip")
        zip_file = zipfile.ZipFile(zf, "w")
        for root, dirs, files in os.walk(self.report_folder):
            for file in files:
                file_abs_path = os.path.join(root, file)
                if "copy-paste/html" not in file_abs_path:
                    zip_file.write(
                        file_abs_path,
                        arcname=file_abs_path.replace(self.report_folder, ""),
                    )
        zip_file.close()
        zf.seek(0)

        # Create the message
        the_msg = MIMEMultipart()
        the_msg["Subject"] = "MegaLinter report"
        the_msg["To"] = ", ".join(recipients)
        the_msg["From"] = "mega-linter@gmail.com"
        the_msg.preamble = "I am not using a MIME-aware mail reader.\n"
        msg = MIMEBase("application", "zip")
        msg.set_payload(zf.read())
        encoders.encode_base64(msg)
        msg.add_header(
            "Content-Disposition", "attachment", filename="mega-linter-reports" + ".zip"
        )
        the_msg.attach(msg)
        the_msg = the_msg.as_string()

        # send the message
        try:
            server = smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
            )
            server.ehlo()
            server.login(
                smtp_username,
                smtp_password,
            )
            server.sendmail(sender, recipients, the_msg)
            server.quit()
        except smtplib.SMTPAuthenticationError as e:
            logging.warning(
                "[Email Reporter] Unable to authenticate to SMTP server: \n"
                + str(e)
                + "\n - smtp server: "
                + smtp_host
                + ":"
                + str(smtp_port)
                + "\n - smtp username: "
                + smtp_username
                + "\n - smtp password:"
                + ("SET" if smtp_password != "" else "NOT SET")
            )
            return
        except Exception as e:
            logging.warning(
                "[Email Reporter] Unable to send e-mail: \n"
                + str(e.__class__)
                + " - "
                + str(e)
                + "\n - smtp server: "
                + smtp_host
                + ":"
                + str(smtp_port)
                + "\n - smtp username: "
                + smtp_username
                + "\n - smtp password:"
                + ("SET" if smtp_password != "" else "NOT SET")
            )
            return
        logging.info("[Email Reporter] Sent mail to " + ", ".join(recipients))
