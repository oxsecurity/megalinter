---
title: Text Reporter for MegaLinter
description: Generate SAST results as text logs for each linter
---
# Text Reporter

Generate text logs for each linter

- General execution log `mega-linter.log` (same as [ConsoleReporter](ConsoleReporter.md) log)
- A separate log file for each processed linter

## Usage

### Get Artifacts on GitHub Actions

- Access GitHub action run

![Screenshot](../assets/images/AccessActionRun.jpg)

- Click on Artifacts then click on [**MegaLinter reports**](#report-folder-structure)

![Screenshot](../assets/images/TextReporter_1.jpg)

### Get Artifacts on GitLab CI

- Access GitLab CI job page

![Screenshot](../assets/images/TextReporter_gitlab_1.jpg)

- In **Job Artifacts** section, click on [**Download**](#report-folder-structure)

### Other CI tools

- You can export `mega-linter.log` and folder `<WORKSPACE>/report` as external artifacts

- You can also use [File.io Reporter](https://megalinter.io/reporters/FileIoReporter/) or [E-mail Reporter](https://megalinter.io/reporters/EmailReporter/)

## Report folder structure

- Open the downloaded zip file and browse **linters_logs** folder for reports

![Screenshot](../assets/images/TextReporter_2.jpg)

![Screenshot](../assets/images/TextReporter_3.jpg)

![Screenshot](../assets/images/TextReporter_4.jpg)

## Configuration

| Variable                 | Description                                       | Default value  |
|--------------------------|---------------------------------------------------|----------------|
| TEXT_REPORTER            | Activates/deactivates reporter                    | `true`         |
| TEXT_REPORTER_SUB_FOLDER | Sub-folder of reports folder containing text logs | `linters_logs` |
