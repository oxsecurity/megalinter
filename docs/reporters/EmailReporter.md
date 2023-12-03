---
title: Email Reporter for MegaLinter
description: If you don't use artifacts upload to read MegaLinter reports, you can receive them by e-mail
---
# E-mail Reporter

If you don't use artifacts upload to read MegaLinter reports, you can receive them by e-mail

## Usage

Define related variables below allowing to send e-mails.

To use with a gmail account, you have to previously follow [these steps](https://stackabuse.com/how-to-send-emails-with-gmail-using-python/#authenticating-with-gmail)

Reports are sent to the defined e-mail address at the end of each MegaLinter run

![Screenshot](../assets/images/EmailReporter_1.jpg)

## Configuration

| Variable                     | Description                                                                                             | Default value          |
|------------------------------|---------------------------------------------------------------------------------------------------------|------------------------|
| EMAIL_REPORTER               | Activates/deactivates reporter                                                                          | true                   |
| EMAIL_REPORTER_EMAIL         | Comma-separated list of recipient emails, that will receive reports                                     |                        |
| EMAIL_REPORTER_SEND_SUCCESS  | Define to `true` if you want to receive reports by mail even when there is no errors or updated sources | `false`                |
| EMAIL_REPORTER_SENDER        | Sender of emails                                                                                        | <megalinter@gmail.com> |
| EMAIL_REPORTER_SMTP_HOST     | SMTP server host                                                                                        | smtp.gmail.com         |
| EMAIL_REPORTER_SMTP_PORT     | SMTP server port                                                                                        | 465                    |
| EMAIL_REPORTER_SMTP_USERNAME | SMTP server username                                                                                    | <megalinter@gmail.com> |
| EMAIL_REPORTER_SMTP_PASSWORD | SMTP server password. Never hardcode it in a config variable, use secrets and context variables         |                        |
