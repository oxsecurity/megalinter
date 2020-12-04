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
        if config.get("EMAIL_REPORTER", "true") != "true":
            self.is_active = False
        elif config.get("EMAIL_REPORTER_EMAIL", "none") == "none":
            logging.warning(
                "To receive reports as email, please set variable EMAIL_REPORTER_EMAIL"
            )
            self.is_active = False

    def produce_report(self):
        # Create temporary zip file with content of report folder
        zf = tempfile.TemporaryFile(prefix="mail", suffix=".zip")
        zip_file = zipfile.ZipFile(zf, "w")
        for root, dirs, files in os.walk(self.report_folder):
            for file in files:
                zip_file.write(os.path.join(root, file))
        zip_file.close()
        zf.seek(0)

        # Create the message
        recipients = config.get_list("EMAIL_REPORTER_EMAIL", [])
        sender = config.get("EMAIL_REPORTER_SENDER", "mega-linter@gmail.com")
        the_msg = MIMEMultipart()
        the_msg["Subject"] = "Mega-Linter report"
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
        server = smtplib.SMTP_SSL(
            config.get("EMAIL_REPORTER_SMTP_HOST", "smtp.gmail.com"),
            config.get("EMAIL_REPORTER_SMTP_PORT", 465),
        )
        server.login(
            config.get("EMAIL_REPORTER_SMTP_USERNAME", sender),
            config.get("EMAIL_REPORTER_SMTP_PASSWORD"),
        )
        server.sendmail(sender, recipients, the_msg)
        server.quit()
        logging.info("Email Reporter: Sent mail to " + ", ".join(recipients))
